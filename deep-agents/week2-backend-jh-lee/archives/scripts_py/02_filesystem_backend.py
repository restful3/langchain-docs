"""2주차 §4 — FilesystemBackend (로컬 디스크 + virtual_mode).

원문: 05-backends.md §"Built-in backends" → FilesystemBackend
교안: archives/source/01_textbook.md §4

FilesystemBackend 는 `root_dir` 아래 실제 파일을 읽고 쓴다. `virtual_mode=True`
를 켜면 에이전트가 보는 절대경로(`/foo/bar.md`)가 호스트의 `<root_dir>/foo/bar.md`
로 정규화되어 샌드박싱된다. 본 데모는 임시 디렉토리를 root 로 잡고
두 모드의 동작 차이를 비교한다.

실행:
    cd .../week2-backend-jh-lee
    cp .env_sample .env  # 없으면
    python archives/scripts_py/02_filesystem_backend.py
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

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

load_dotenv(find_dotenv())

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:31b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL")

extra = {"base_url": OLLAMA_BASE_URL} if OLLAMA_BASE_URL else {}
model = ChatOllama(model=OLLAMA_MODEL, **extra)


system_prompt = """You are a file-system assistant.
You have ls/read_file/write_file/edit_file/glob/grep tools backed by a real filesystem.
Use absolute paths starting with /. Report what you did concisely.
"""


def build_agent(root_dir: str, virtual_mode: bool):
    return create_deep_agent(
        model=model,
        system_prompt=system_prompt,
        backend=FilesystemBackend(root_dir=root_dir, virtual_mode=virtual_mode),
    )


def main() -> None:
    print("▶ FilesystemBackend 데모 — 호스트 디스크의 root_dir 아래에 실제 파일 생성.")
    print("  · 본 데모는 tempfile.TemporaryDirectory() 를 root 로 쓰므로 스크립트 종료 시 자동 삭제.")
    print("  · 운영에서 영속 디렉토리를 root 로 쓰면 파일이 살아남음.\n")

    with tempfile.TemporaryDirectory() as tmp:
        root = str(Path(tmp).resolve())
        print(f"sandbox root: {root}\n")

        # ---- 1) virtual_mode=True : /report.md → <root>/report.md ----
        print("=== virtual_mode=True (경로 정규화) ===")
        print("  ↳ 에이전트는 '/report.md' 로 절대경로를 보지만, 실제로는 <root>/report.md 로 정규화되어 sandbox 안에 떨어짐.")
        agent_v = build_agent(root, virtual_mode=True)
        agent_v.invoke({
            "messages": [{"role": "user", "content": "write_file '/report.md' with content '# hello virtual'"}]
        })
        path_v = Path(root) / "report.md"
        print(f"호스트 디스크: {path_v} exists={path_v.exists()} content={path_v.read_text() if path_v.exists() else 'N/A'}")

        # ---- 2) virtual_mode=False : 에이전트가 절대경로 그대로 사용 ----
        print("\n=== virtual_mode=False (호스트 절대경로 그대로) ===")
        print("  ↳ 에이전트가 호스트 절대경로를 그대로 받아 그 자리에 파일 생성 — 격리는 약하지만 직관적.")
        agent_r = build_agent(root, virtual_mode=False)
        target = Path(root) / "raw.md"
        agent_r.invoke({
            "messages": [{"role": "user", "content": f"write_file '{target}' with content '# hello raw'"}]
        })
        print(f"호스트 디스크: {target} exists={target.exists()} content={target.read_text() if target.exists() else 'N/A'}")

        # ---- 3) ls 로 sandbox 안 결과 보기 ----
        print("\n=== ls / (virtual_mode=True 측에서) ===")
        print("  ↳ ls 결과의 경로(/raw.md, /report.md) 는 sandbox 시점. 실제 위치는 위 'sandbox root:' 아래.")
        r = agent_v.invoke({"messages": [{"role": "user", "content": "ls /"}]})
        print(r["messages"][-1].content)


if __name__ == "__main__":
    main()
