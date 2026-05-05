"""1주차 §4.4 System Prompt — 커스텀 프롬프트 한 장.

원문: 03-customization_ko.md (시스템 프롬프트 절)
교안: content/01_textbook.md §4.4

deepagents 는 BASE_AGENT_PROMPT (Claude Code 영감, ~42 라인) 를 기본으로
싣고 그 위에 사용자가 넘긴 system_prompt 를 합성한다. 도메인 한 줄을 더
얹는 가장 작은 형태를 보인다 — Quickstart 와 달리 도구는 비워둔다.

실행:
    python scripts/04_custom_system_prompt.py
"""
from __future__ import annotations

import os

from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import init_chat_model

from deepagents import create_deep_agent

load_dotenv(find_dotenv())

MODEL_NAME = os.environ.get("DEEPAGENT_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")

extra = {"base_url": OPENAI_BASE_URL} if OPENAI_BASE_URL else {}
model = init_chat_model(f"openai:{MODEL_NAME}", **extra)

research_instructions = """\
You are an expert researcher. Your job is to conduct \
thorough research, and then write a polished report. \
"""

agent = create_deep_agent(
    model=model,
    system_prompt=research_instructions,
)


def main() -> None:
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "RAG 와 fine-tuning 의 차이를 한 단락으로.",
                }
            ]
        }
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
