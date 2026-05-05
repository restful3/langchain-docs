"""1주차 §4.3 Model — 문자열로 갈아 끼우기.

원문: 03-customization_ko.md (모델 문자열 절)
교안: content/01_textbook.md §4.3

init_chat_model 의 'provider:model' 한 줄로 모델을 교체한다.
deepagents 의 기본은 Anthropic 의 claude-sonnet-4-6 이지만, 여기서는
'openai:<model>' 으로 갈아 끼운다. OPENAI_BASE_URL 이 설정돼 있으면
clipproxyapi 같은 OpenAI 호환 프록시로 라우팅된다.

실행:
    python scripts/02_model_string_swap.py
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

agent = create_deep_agent(model=model)


def main() -> None:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "한 줄로 자기소개 해줘."}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
