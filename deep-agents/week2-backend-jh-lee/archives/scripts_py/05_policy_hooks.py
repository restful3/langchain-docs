"""2주차 §8 — Policy hooks (권한 제어).

원문: 05-backends.md §"Add policy hooks" L219-275
교안: archives/source/01_textbook.md §8

권한 제어를 거는 두 가지 패턴을 한 자리에서 시연한다:
  1) GuardedBackend  — FilesystemBackend 서브클래싱 (가장 단순, 한 백엔드 한정)
  2) PolicyWrapper   — BackendProtocol 제네릭 래퍼 (State/Store/Filesystem 어디든 적용)

두 패턴 모두 deny 매칭 시 `WriteResult(error=...)` / `EditResult(error=...)` 를
반환해 정책 위반을 표현한다 (예외를 던지지 않는다 — 에이전트가 에러를 메시지로 받음).

실행:
    cd .../week2-backend-jh-lee
    cp .env_sample .env  # 없으면
    python archives/scripts_py/05_policy_hooks.py
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
from deepagents.backends import FilesystemBackend, StateBackend
from deepagents.backends.protocol import BackendProtocol, EditResult, WriteResult
from deepagents.backends.utils import FileInfo, GrepMatch

load_dotenv(find_dotenv())

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:31b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL")

extra = {"base_url": OLLAMA_BASE_URL} if OLLAMA_BASE_URL else {}
model = ChatOllama(model=OLLAMA_MODEL, **extra)


# ---- Pattern A: GuardedBackend (FilesystemBackend 서브클래싱) ----
# 원문 L226-244 그대로. 단순하지만 Filesystem 한 백엔드에만 적용 가능.
class GuardedBackend(FilesystemBackend):
    def __init__(self, *, deny_prefixes: list[str], **kwargs):
        super().__init__(**kwargs)
        # deny_prefixes 끝을 '/' 로 정규화 → "/etc" 와 "/etcetc/" 혼동 방지
        self.deny_prefixes = [p if p.endswith("/") else p + "/" for p in deny_prefixes]

    def write(self, file_path: str, content: str) -> WriteResult:
        if any(file_path.startswith(p) for p in self.deny_prefixes):
            return WriteResult(error=f"Writes are not allowed under {file_path}")
        return super().write(file_path, content)

    def edit(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> EditResult:
        if any(file_path.startswith(p) for p in self.deny_prefixes):
            return EditResult(error=f"Edits are not allowed under {file_path}")
        return super().edit(file_path, old_string, new_string, replace_all)


# ---- Pattern B: PolicyWrapper (제네릭 — 어떤 백엔드든 감쌀 수 있음) ----
# 원문 L247-275 그대로. State/Store/Filesystem/Composite 어디에도 같은 정책 적용 가능.
class PolicyWrapper(BackendProtocol):
    def __init__(self, inner: BackendProtocol, deny_prefixes: list[str] | None = None):
        self.inner = inner
        self.deny_prefixes = [p if p.endswith("/") else p + "/" for p in (deny_prefixes or [])]

    def _deny(self, path: str) -> bool:
        return any(path.startswith(p) for p in self.deny_prefixes)

    # 읽기 계열은 그대로 통과 (정책 외 동작은 inner 에 위임)
    def ls_info(self, path: str) -> list[FileInfo]:
        return self.inner.ls_info(path)

    def read(self, file_path: str, offset: int = 0, limit: int = 2000) -> str:
        return self.inner.read(file_path, offset=offset, limit=limit)

    def grep_raw(self, pattern: str, path: str | None = None, glob: str | None = None) -> list[GrepMatch] | str:
        return self.inner.grep_raw(pattern, path, glob)

    def glob_info(self, pattern: str, path: str = "/") -> list[FileInfo]:
        return self.inner.glob_info(pattern, path)

    # 쓰기 계열에만 정책 검사
    def write(self, file_path: str, content: str) -> WriteResult:
        if self._deny(file_path):
            return WriteResult(error=f"Writes are not allowed under {file_path}")
        return self.inner.write(file_path, content)

    def edit(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> EditResult:
        if self._deny(file_path):
            return EditResult(error=f"Edits are not allowed under {file_path}")
        return self.inner.edit(file_path, old_string, new_string, replace_all)


system_prompt = """You are a file-system assistant.
You have ls/read_file/write_file/edit_file tools backed by a real filesystem.
Use absolute paths. Report the result honestly — if a write fails, say so explicitly.
"""


def main() -> None:
    print("▶ Policy hooks 데모 — 백엔드 위에 권한(deny) 규칙을 걸어 일부 경로의 write/edit 을 차단.")
    print("  · Pattern A: GuardedBackend  — FilesystemBackend 서브클래싱 (가장 단순)")
    print("  · Pattern B: PolicyWrapper   — BackendProtocol 제네릭 래퍼 (어떤 백엔드든 감쌀 수 있음)")
    print("  · 두 패턴 모두 deny 매칭 시 WriteResult(error=...) 반환 → 에이전트가 에러를 메시지로 받음.\n")

    deny = ["/etc/", "/private/"]
    print(f"deny_prefixes = {deny}\n")

    with tempfile.TemporaryDirectory() as tmp:
        root = str(Path(tmp).resolve())
        print(f"sandbox root: {root}\n")

        # ===== Pattern A: GuardedBackend =====
        agent_a = create_deep_agent(
            model=model,
            system_prompt=system_prompt,
            backend=GuardedBackend(deny_prefixes=deny, root_dir=root, virtual_mode=True),
        )

        print("=== A-1) GuardedBackend: 허용 경로 /notes/ok.md write ===")
        print("  ↳ /notes/* 는 deny 목록에 없음 → 정상 write 되어야 함.")
        r = agent_a.invoke({"messages": [{"role": "user", "content":
            "write_file '/notes/ok.md' with content 'allowed write'"
        }]})
        print(r["messages"][-1].content)
        ok_path = Path(root) / "notes" / "ok.md"
        print(f"  → 호스트 디스크: {ok_path} exists={ok_path.exists()}  (True 여야 함)")

        print("\n=== A-2) GuardedBackend: 거부 경로 /etc/passwd write ===")
        print("  ↳ /etc/* 는 deny 매칭 → WriteResult(error=...) 반환 → 에이전트 답변에 'Writes are not allowed' 류 메시지가 보여야 함.")
        r = agent_a.invoke({"messages": [{"role": "user", "content":
            "write_file '/etc/passwd' with content 'sneaky'"
        }]})
        print(r["messages"][-1].content)
        bad_path = Path(root) / "etc" / "passwd"
        print(f"  → 호스트 디스크: {bad_path} exists={bad_path.exists()}  (False 여야 함 — 정책이 실제로 막았다는 증거)")

        # ===== Pattern B: PolicyWrapper =====
        agent_b = create_deep_agent(
            model=model,
            system_prompt=system_prompt,
            backend=(lambda rt: PolicyWrapper(StateBackend(rt), deny_prefixes=deny)),
        )
        cfg = {"configurable": {"thread_id": "policy-demo"}}

        print("\n=== B-1) PolicyWrapper(StateBackend): 허용 경로 /notes/scratch.md write ===")
        print("  ↳ 같은 deny 규칙을 StateBackend 위에 적용 — Filesystem 이 아닌 백엔드에도 동일 정책.")
        r = agent_b.invoke({"messages": [{"role": "user", "content":
            "write_file '/notes/scratch.md' with content 'state ok'"
        }]}, config=cfg)
        print(r["messages"][-1].content)

        print("\n=== B-2) PolicyWrapper(StateBackend): 거부 경로 /private/secret.md write ===")
        print("  ↳ /private/* 는 deny 매칭 → 에이전트가 거부 메시지를 받음.")
        r = agent_b.invoke({"messages": [{"role": "user", "content":
            "write_file '/private/secret.md' with content 'leak'"
        }]}, config=cfg)
        print(r["messages"][-1].content)

        print("\n→ 두 패턴 모두 BackendProtocol 의 write/edit 반환 자리에 'error' 를 채우는 식으로 정책을 표현 (예외 X).")
        print("→ 같은 패턴으로 감사 로깅·redaction·우선순위(create-only) 정책도 표현 가능 (교안 §8 참조).")


if __name__ == "__main__":
    main()
