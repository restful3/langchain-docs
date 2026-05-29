"""A2A 실습 — 멀티 에이전트 트레이스를 하나의 thread 로 통합.

노트북: 03_a2a_langsmith.ipynb §6
원문: https://docs.langchain.com/langsmith/server-a2a

pingpong_client 와 거의 같지만, JSON-RPC 최상위 metadata 에 thread_id 를
실어 보낸다. 모든 에이전트에서 같은 thread_id 를 재사용하면 LangSmith 에서
대화 전체가 하나의 thread 로 묶인다. (contextId -> thread_id 자동 매핑)

사전 준비:
    1) graph.py 를 두 포트로 실행
    2) .env 에 LANGSMITH_API_KEY, LANGSMITH_PROJECT 설정 (트레이싱용)
    3) 아래 URL 의 <assistant_id> 를 실제 값으로 교체
실행:
    python scripts/a2a/traced_client.py
"""
import asyncio
import uuid

import aiohttp
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


async def send_message(session, url, text, context_id=None, task_id=None, thread_id=None):
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
        "metadata": {"thread_id": thread_id},  # 트레이스 통합 키
    }

    async with session.post(url, json=payload, headers={"Accept": "application/json"}) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {await response.text()}")
        result = await response.json()

    if "error" in result:
        raise RuntimeError(result["error"].get("message", "Unknown error"))

    result_obj = result.get("result", {})
    returned_context_id = result_obj.get("contextId") or context_id
    returned_task_id = result_obj.get("id")
    text_out = next(
        (
            part.get("text", "")
            for art in result_obj.get("artifacts", []) or []
            for part in art.get("parts", []) or []
            if part.get("kind") == "text"
        ),
        "(no text)",
    )
    return text_out, returned_context_id, returned_task_id


async def run_conversation(agent_a_url, agent_b_url):
    thread_id = str(uuid.uuid4())
    context_id = None
    task_id = None
    message = "Hello! Let's collaborate."

    async with aiohttp.ClientSession() as session:
        for _ in range(3):
            message, context_id, task_id = await send_message(
                session, agent_a_url, message,
                context_id=context_id, task_id=task_id,
                thread_id=context_id or thread_id,
            )
            message, context_id, task_id = await send_message(
                session, agent_b_url, message,
                context_id=context_id, task_id=task_id,
                thread_id=context_id or thread_id,
            )


if __name__ == "__main__":
    asyncio.run(
        run_conversation(
            "http://localhost:2024/a2a/<agent_a_assistant_id>",
            "http://localhost:2025/a2a/<agent_b_assistant_id>",
        )
    )
