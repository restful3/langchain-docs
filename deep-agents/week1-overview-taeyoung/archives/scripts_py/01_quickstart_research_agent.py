"""1주차 §3 Quickstart — 리서치 에이전트.

원문: 02-quickstart_ko.md (3~5단계)
교안: content/01_textbook.md §3.2~§3.4

기본 deepagents Quickstart 는 ANTHROPIC_API_KEY 를 쓰지만, 이 스크립트는
OpenAI 호환 API (또는 clipproxyapi 같은 프록시) 위에서 동작하도록 한 번 더
얇게 감싼 변형이다. 모델만 갈아 끼웠을 뿐, create_deep_agent 호출 형태는
원문과 동일하다.

실행:
    cd .../week1-overview-taeyoung
    cp .env_sample .env  # 없으면. 그리고 키 채워넣기
    python scripts/01_quickstart_research_agent.py
"""
from __future__ import annotations

import os
from typing import Literal

from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import init_chat_model
from tavily import TavilyClient

from deepagents import create_deep_agent

load_dotenv(find_dotenv())

MODEL_NAME = os.environ.get("DEEPAGENT_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")  # None 이면 OpenAI 직접

# init_chat_model 은 추가 kwargs 를 ChatOpenAI 에 그대로 forward 한다.
# OPENAI_BASE_URL 이 비어 있으면 OpenAI 공식 엔드포인트, 채워져 있으면
# clipproxyapi 같은 OpenAI 호환 프록시로 라우팅된다.
extra = {"base_url": OPENAI_BASE_URL} if OPENAI_BASE_URL else {}
model = init_chat_model(f"openai:{MODEL_NAME}", **extra)


tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.
You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=research_instructions,
)


def main() -> None:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What is langgraph?"}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
