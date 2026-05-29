"""A2A 실습 — 두 에이전트 핑퐁 대화.

노트북: 03_a2a_langsmith.ipynb §5
원문: https://docs.langchain.com/langsmith/server-a2a

agent A(포트 2024)와 agent B(포트 2025)를 번갈아 호출해, 한쪽의 응답을
다른 쪽의 입력으로 넘긴다. contextId/taskId 로 대화 스레드를 이어간다.

사전 준비:
    1) graph.py 를 두 포트로 실행 (langgraph dev / --port 2025)
    2) .env 에 AGENT_A_ID, AGENT_B_ID (assistant id) 채우기
실행:
    python scripts/a2a/pingpong_client.py
"""
import asyncio
import os
import uuid

import aiohttp
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


def extract_text(result: dict) -> str:
    for art in result.get("result", {}).get("artifacts", []) or []:
        for part in art.get("parts", []) or []:
            if part.get("kind") == "text" and part.get("text"):
                return part["text"]

    msg = (result.get("result", {}).get("status", {}) or {}).get("message", {}) or {}
    for part in msg.get("parts", []) or []:
        if part.get("kind") == "text" and part.get("text"):
            return part["text"]

    return "(no text found)"


async def send_message(session, port, assistant_id, text, context_id=None, task_id=None):
    url = f"http://127.0.0.1:{port}/a2a/{assistant_id}"

    message = {
        "role": "user",
        "parts": [{"kind": "text", "text": text}],
        "messageId": str(uuid.uuid4()),
    }
    if context_id:
        message["contextId"] = context_id
    if task_id:
        message["taskId"] = task_id

    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {"message": message},
    }

    headers = {"Accept": "application/json"}
    async with session.post(url, json=payload, headers=headers) as response:
        result = await response.json()

    returned_context_id = result.get("result", {}).get("contextId") or context_id
    returned_task_id = result.get("result", {}).get("id")
    return extract_text(result), returned_context_id, returned_task_id


async def simulate_conversation():
    agent_a_id = os.getenv("AGENT_A_ID")
    agent_b_id = os.getenv("AGENT_B_ID")

    if not agent_a_id or not agent_b_id:
        print("Set AGENT_A_ID and AGENT_B_ID environment variables")
        return

    message = "Hello! Let's have a conversation."
    context_id = None
    task_id = None

    async with aiohttp.ClientSession() as session:
        for i in range(3):
            print(f"--- Round {i + 1} ---")

            message, context_id, task_id = await send_message(
                session, 2024, agent_a_id, message,
                context_id=context_id, task_id=task_id,
            )
            print(f"\U0001F535 Agent A: {message}")

            message, context_id, task_id = await send_message(
                session, 2025, agent_b_id, message,
                context_id=context_id, task_id=task_id,
            )
            print(f"\U0001F534 Agent B: {message}\n")


if __name__ == "__main__":
    asyncio.run(simulate_conversation())
