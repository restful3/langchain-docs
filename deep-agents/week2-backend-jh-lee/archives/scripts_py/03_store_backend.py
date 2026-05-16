"""2주차 §5 — StoreBackend (LangGraph Store 영속).

원문: 05-backends.md §"Built-in backends" → StoreBackend
교안: archives/source/01_textbook.md §5

StoreBackend 는 LangGraph 의 `BaseStore` 위에서 동작하며, **thread 를 가로질러
파일이 살아남는다**. 본 데모는 `InMemoryStore` 를 공유해 두 번의 invoke 에서
다른 thread_id 로도 동일 파일이 읽히는지 확인한다.

실행:
    cd .../week2-backend-jh-lee
    cp .env_sample .env  # 없으면
    python archives/scripts_py/03_store_backend.py
"""
from __future__ import annotations

# 시연 출력의 가독성을 위해 deepagents/langchain 내부의 deprecation 경고를 가립니다.
# (런타임 동작에는 영향 없음 — 경고만 숨길 뿐)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os

from dotenv import find_dotenv, load_dotenv
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from deepagents import create_deep_agent
from deepagents.backends import StoreBackend

load_dotenv(find_dotenv())

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:31b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL")

extra = {"base_url": OLLAMA_BASE_URL} if OLLAMA_BASE_URL else {}
model = ChatOllama(model=OLLAMA_MODEL, **extra)


system_prompt = """You are a long-term memory assistant.
When asked to remember, write_file to /memories/<topic>.md.
When asked to recall, read_file from /memories/<topic>.md.
"""

store = InMemoryStore()
checkpointer = InMemorySaver()

agent = create_deep_agent(
    model=model,
    system_prompt=system_prompt,
    backend=(lambda rt: StoreBackend(rt)),
    store=store,
    checkpointer=checkpointer,
)


def main() -> None:
    print("▶ StoreBackend 데모 — LangGraph BaseStore 위에 파일 저장. thread 를 가로질러 살아남음.")
    print("  · 본 데모는 InMemoryStore 라 스크립트 종료 시 휘발.")
    print("  · PostgresStore 로 바꾸면 진짜 영속.\n")

    cfg_a = {"configurable": {"thread_id": "session-A"}}
    cfg_b = {"configurable": {"thread_id": "session-B"}}

    print("=== session-A: 기록 ===")
    print("  ↳ thread_id=session-A 로 /memories/release.md 작성 → 파일은 store 의 namespace 키에 들어감.")
    r1 = agent.invoke(
        {"messages": [{"role": "user", "content": "remember about 'release': 2주차 PDF 빌드는 build.py 로 한다."}]},
        config=cfg_a,
    )
    print(r1["messages"][-1].content)

    print("\n=== session-B (다른 thread): 회상 ===")
    print("  ↳ thread_id=session-B (다른 thread) 로 같은 파일 read → Store 는 thread-cross 영속이므로 보여야 함.")
    r2 = agent.invoke(
        {"messages": [{"role": "user", "content": "recall about 'release'."}]},
        config=cfg_b,
    )
    print(r2["messages"][-1].content)
    print("\n→ Store 는 thread 간 공유되므로 session-B 에서도 동일 파일이 읽혀야 한다.")

    # store 의 내부 상태 직접 살펴보기 (디버그용)
    print("\n=== Store 내부 (디버그) ===")
    for namespace, items in store.search(("memories",)) if hasattr(store, "search") else []:
        print(f"  {namespace}: {items}")


if __name__ == "__main__":
    main()
