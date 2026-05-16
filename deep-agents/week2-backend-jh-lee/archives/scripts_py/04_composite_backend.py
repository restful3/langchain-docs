"""2주차 §6 — CompositeBackend (라우팅 규칙).

원문: 05-backends.md §"Built-in backends" → CompositeBackend, §"Route to different backends"
교안: archives/source/01_textbook.md §6

CompositeBackend 는 경로 prefix 기반으로 호출을 백엔드별로 라우팅한다.
본 데모는 다음 3개 규칙을 동시에 운영한다:

  /memories/*  → StoreBackend   (thread-cross 영속)
  /shared/*    → FilesystemBackend (로컬 디스크, sandboxed)
  그 외(default) → StateBackend  (thread-scoped 휘발성)

같은 에이전트에서 세 종류의 영속성/스코프가 한 가상 파일시스템 안에 공존한다.

실행:
    cd .../week2-backend-jh-lee
    cp .env_sample .env  # 없으면
    python archives/scripts_py/04_composite_backend.py
"""
from __future__ import annotations

# 시연 출력의 가독성을 위해 deepagents/langchain 내부의 deprecation 경고를 가립니다.
# (런타임 동작에는 영향 없음 — 경고만 숨길 뿐)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import tempfile
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from deepagents import create_deep_agent
from deepagents.backends import (
    CompositeBackend,
    FilesystemBackend,
    StateBackend,
    StoreBackend,
)

load_dotenv(find_dotenv())

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:31b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL")

extra = {"base_url": OLLAMA_BASE_URL} if OLLAMA_BASE_URL else {}
model = ChatOllama(model=OLLAMA_MODEL, **extra)


system_prompt = """You are a file-routing assistant.
Use:
  /memories/*  for long-term memory (persisted across sessions)
  /shared/*    for local-disk artifacts
  any other path for ephemeral scratch.
Use ls / write_file / read_file with absolute paths.
"""


def main() -> None:
    print("▶ CompositeBackend 데모 — 경로 prefix 기반 라우팅.")
    print("  · 같은 에이전트 안에서 세 매체(Store / Filesystem / State) 가 공존.")
    print("  · 매체별로 파일 수명이 다름 — 아래 step 별 설명 참조.\n")

    with tempfile.TemporaryDirectory() as tmp:
        root = str(Path(tmp).resolve())

        store = InMemoryStore()
        composite = lambda rt: CompositeBackend(
            default=StateBackend(rt),
            routes={
                "/memories/": StoreBackend(rt),
                "/shared/": FilesystemBackend(root_dir=root, virtual_mode=True),
            },
        )

        agent = create_deep_agent(
            model=model,
            system_prompt=system_prompt,
            backend=composite,
            store=store,
            checkpointer=InMemorySaver(),
        )

        cfg = {"configurable": {"thread_id": "composite-demo"}}

        print("=== 1) /memories/note.md (Store 경로) write ===")
        print("  ↳ /memories/* → StoreBackend.")
        print("     저장 위치: LangGraph Store (본 데모는 InMemoryStore).")
        print("     수명: thread-cross 영속 — 다른 thread 에서도 보임. 프로세스 종료 시 휘발 (PostgresStore 로 바꾸면 영속).")
        agent.invoke({"messages": [{"role": "user", "content":
            "write_file '/memories/note.md' with content 'long-term: 2주차 발표일은 5/22'"
        }]}, config=cfg)

        print("\n=== 2) /shared/draft.md (Filesystem 경로) write ===")
        print(f"  ↳ /shared/* → FilesystemBackend(root_dir={root}, virtual_mode=True).")
        print(f"     저장 위치: 호스트 디스크 {root}/shared/draft.md.")
        print("     수명: tempfile.TemporaryDirectory 가 정리되는 main 종료 시 사라짐. 운영에서 영속 디렉토리를 root 로 쓰면 살아남음.")
        agent.invoke({"messages": [{"role": "user", "content":
            "write_file '/shared/draft.md' with content 'shared: 슬라이드 초안'"
        }]}, config=cfg)

        print("\n=== 3) /tmp/scratch.md (default=State) write ===")
        print("  ↳ /tmp/* → default = StateBackend.")
        print("     저장 위치: LangGraph state 채널.")
        print("     수명: 같은 thread (composite-demo) 안에서만 보임. thread 끝나면 휘발.")
        agent.invoke({"messages": [{"role": "user", "content":
            "write_file '/tmp/scratch.md' with content 'scratch: 휘발성 메모'"
        }]}, config=cfg)

        # 호스트 디스크에는 /shared/* 만 떨어져 있어야 한다.
        print(f"\n호스트 디스크 ({root}):")
        print("  ↳ /shared/* 만 보여야 함. /memories/* 는 Store, /tmp/* 는 state 에 있으므로 디스크에서는 보이지 않음.")
        for p in Path(root).rglob("*"):
            if p.is_file():
                print(f"  {p.relative_to(root)} :: {p.read_text()[:60]}...")

        print("\n=== 4) ls / (composite 가 세 백엔드 결과 합치는지) ===")
        print("  ↳ Composite 가 세 백엔드의 ls 결과를 합쳐 보여줌 — /memories, /shared, /tmp 가 한 자리에서 한 가상 파일시스템처럼 보임.")
        r = agent.invoke({"messages": [{"role": "user", "content": "ls /"}]}, config=cfg)
        print(r["messages"][-1].content)


if __name__ == "__main__":
    main()
