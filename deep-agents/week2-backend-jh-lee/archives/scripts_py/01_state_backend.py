"""2주차 §3 — StateBackend (thread-scoped 휘발성).

원문: 05-backends.md §"Built-in backends" → StateBackend
교안: archives/source/01_textbook.md §3

기본값(`create_deep_agent()`만 호출)이 곧 StateBackend 다. 이 데모는
파일이 LangGraph state 에 적재된다는 사실을 명시적으로 드러내기 위해
`StateBackend` 를 직접 주입하고, 같은 thread 내 두 번의 invoke 에서
잔존하는지 확인한다.

실행:
    cd .../week2-backend-jh-lee
    cp .env_sample .env  # 없으면
    python archives/scripts_py/01_state_backend.py
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

from deepagents import create_deep_agent
from deepagents.backends import StateBackend

load_dotenv(find_dotenv())

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:31b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL")  # None → 로컬 127.0.0.1:11434

extra = {"base_url": OLLAMA_BASE_URL} if OLLAMA_BASE_URL else {}
model = ChatOllama(model=OLLAMA_MODEL, **extra)


system_prompt = """You are a note-taking assistant.
When asked to remember something, write it to /notes/note.md.
When asked to recall, read /notes/note.md and answer with its contents.
"""

# StateBackend 는 runtime 의존 — factory 형태(lambda)로 전달.
agent = create_deep_agent(
    model=model,
    system_prompt=system_prompt,
    backend=(lambda rt: StateBackend(rt)),
    checkpointer=InMemorySaver(),
)


def main() -> None:
    print("▶ StateBackend 데모 — LangGraph state 채널에 파일 저장.")
    print("  · 같은 thread 안에서만 파일이 보이며, thread 가 끝나면 휘발.")
    print("  · checkpointer 가 영속이면 (예: PostgresSaver) 프로세스가 죽어도 thread 가 살아남아 다음 실행에서 이어 쓸 수 있음.")
    print("  · 본 데모는 InMemorySaver 라 스크립트 종료 시 thread state 도 함께 사라짐.\n")

    config = {"configurable": {"thread_id": "demo-thread-1"}}

    print("=== Turn 1: 기록 ===")
    print("  ↳ thread_id=demo-thread-1 으로 invoke → 파일은 이 thread 의 state 채널에 적재됨.")
    r1 = agent.invoke(
        {"messages": [{"role": "user", "content": "remember: 2주차 발표일은 2026-05-16 입니다."}]},
        config=config,
    )
    print(r1["messages"][-1].content)

    print("\n=== Turn 2: 같은 thread 회상 ===")
    print("  ↳ 같은 thread_id 로 read → Turn 1 에서 쓴 파일이 그대로 보여야 함 (state 채널 잔존).")
    r2 = agent.invoke(
        {"messages": [{"role": "user", "content": "recall the note."}]},
        config=config,
    )
    print(r2["messages"][-1].content)

    print("\n=== Turn 3: 다른 thread → 휘발성 확인 ===")
    print("  ↳ thread_id=demo-thread-2 (새 thread) 로 read → 새 state 채널이라 파일이 없어야 함 (휘발 증명).")
    config2 = {"configurable": {"thread_id": "demo-thread-2"}}
    r3 = agent.invoke(
        {"messages": [{"role": "user", "content": "recall the note."}]},
        config=config2,
    )
    print(r3["messages"][-1].content)
    print("\n→ thread-2 에서는 /notes/note.md 가 존재하지 않아야 한다 (StateBackend 는 thread-scoped).")


if __name__ == "__main__":
    main()
