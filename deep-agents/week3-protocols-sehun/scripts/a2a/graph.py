"""A2A 실습 — A2A 호환 LangGraph 에이전트.

노트북: 03_a2a_langsmith.ipynb §3
원문: https://docs.langchain.com/langsmith/server-a2a

핵심 조건: state 에 `messages` 키가 있어야 A2A text part 를 처리할 수 있다.
langgraph.json 에 등록한 뒤 `langgraph dev` 로 서버를 띄우면
Agent Server 가 /a2a/{assistant_id} 엔드포인트를 자동 노출한다.

실행:
    cd scripts/a2a
    langgraph dev          # agent A (포트 2024)
    langgraph dev --port 2025   # agent B (다른 터미널)

OPENAI_API_KEY 필요 (.env 참고).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from openai import AsyncOpenAI


class Context(TypedDict):
    my_configurable_param: str


@dataclass
class State:
    messages: List[Dict[str, Any]]  # A2A text part 처리를 위해 필수


async def call_model(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    latest_message = state.messages[-1] if state.messages else {}
    user_content = latest_message.get("content", "No message content")

    openai_messages = [
        {
            "role": "system",
            "content": "You are a helpful conversational agent. Keep responses brief and engaging.",
        },
        {"role": "user", "content": user_content},
    ]

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=openai_messages,
            max_tokens=100,
            temperature=0.7,
        )
        ai_response = response.choices[0].message.content
    except Exception as e:
        ai_response = f"I received your message but had trouble processing it. Error: {str(e)[:50]}..."

    response_message = {"role": "assistant", "content": ai_response}
    return {"messages": state.messages + [response_message]}


graph = (
    StateGraph(State, context_schema=Context)
    .add_node(call_model)
    .add_edge("__start__", "call_model")
    .compile()
)
