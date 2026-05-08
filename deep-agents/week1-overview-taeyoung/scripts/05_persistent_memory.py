"""1주차 §2.4 Long-term Memory — cross-thread 영속 메모리.

원문: 04-deep_dive_ko.md (Backend / Store 절)
교안: content/01_textbook.md §2.4 (코드.4)

핵심 아이디어 — `CompositeBackend` 가 가상 파일시스템의 `/memories/` prefix
만 `StoreBackend` 로 라우팅한다. 같은 도구 (`write_file`, `read_file`) 로
단기·장기 메모리를 다루며, 차이는 경로뿐이다.

검증 — 두 `agent.invoke()` 가 다른 thread_id 인데도 두 번째 호출이 첫
번째에서 `/memories/user.txt` 에 저장한 사용자 이름 'Alice' 를 읽어 회신한다.

실행:
    python scripts/05_persistent_memory.py
"""
from __future__ import annotations

import os

from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

load_dotenv(find_dotenv())

MODEL_NAME = os.environ.get("DEEPAGENT_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")

extra = {"base_url": OPENAI_BASE_URL} if OPENAI_BASE_URL else {}
model = init_chat_model(f"openai:{MODEL_NAME}", **extra)

agent = create_deep_agent(
    model=model,
    store=InMemoryStore(),
    checkpointer=MemorySaver(),
    backend=CompositeBackend(
        default=StateBackend(),
        routes={"/memories/": StoreBackend()},
    ),
)


def main() -> None:
    # Thread 1 — 영속 메모에 사용자 이름 저장
    config_1 = {"configurable": {"thread_id": "thread-1"}}
    print("=" * 60)
    print("[Thread 1] /memories/user.txt 에 'Alice' 저장 요청")
    print("=" * 60)
    result_1 = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Save my name 'Alice' to /memories/user.txt",
                }
            ]
        },
        config_1,
    )
    print(result_1["messages"][-1].content)

    # Thread 2 — 다른 thread 에서 같은 파일 읽기
    config_2 = {"configurable": {"thread_id": "thread-2"}}
    print()
    print("=" * 60)
    print("[Thread 2] (다른 thread) 사용자 이름 질의 — Store 에서 회수")
    print("=" * 60)
    result_2 = agent.invoke(
        {"messages": [{"role": "user", "content": "What is my name?"}]},
        config_2,
    )
    print(result_2["messages"][-1].content)


if __name__ == "__main__":
    main()
