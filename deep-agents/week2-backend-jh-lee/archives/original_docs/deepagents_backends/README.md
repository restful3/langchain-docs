# deepagents.backends — Upstream Source Snapshot

이 디렉토리는 `langchain-ai/deepagents` 레포의 백엔드 패키지 소스를 **verbatim**으로 보존합니다. 교안 작성 시 코드 인용·구조 참조용이며 **수정 금지**입니다.

## 출처

| 항목 | 값 |
|------|-----|
| Repo | https://github.com/langchain-ai/deepagents |
| 경로 | `libs/deepagents/deepagents/backends/` |
| Commit SHA | `4421bec94ffbe1f3a3bf44088ebcf8ab8c24a736` (`.SHA` 파일 참조) |
| 브랜치 | `main` (수집 시점 기준) |
| 수집일 | 2026-05-15 |
| 라이선스 | LICENSE는 상위 레포 참조 (MIT 추정 — 사용 전 확인) |

## 파일 목록 (11개)

| 파일 | 줄 수 | 역할 |
|------|------|------|
| `__init__.py` | 28 | 패키지 진입 / 공개 심볼 |
| `protocol.py` | 852 | `Backend` 프로토콜 / 추상 인터페이스 정의 |
| `state.py` | 381 | **StateBackend** — 휘발성 in-memory |
| `filesystem.py` | 892 | **FilesystemBackend** — 로컬 디스크 |
| `store.py` | 800 | **StoreBackend** — LangGraph Store 영속 |
| `composite.py` | 738 | **Composite** — 라우팅 규칙 기반 합성 |
| `sandbox.py` | 874 | Sandbox 백엔드 (격리 환경) |
| `local_shell.py` | 368 | 로컬 셸 백엔드 |
| `langsmith.py` | 274 | LangSmith 통합 백엔드 |
| `context_hub.py` | 337 | Context hub 헬퍼 |
| `utils.py` | 743 | 공용 유틸 (경로 정규화, 정책 검사 등) |

## 교안 매핑 후보

- `01_state_backend.py` ← `state.py` + `protocol.py`
- `02_filesystem_backend.py` ← `filesystem.py` + `utils.py`
- `03_store_backend.py` ← `store.py`
- `04_composite_backend.py` ← `composite.py`

## 갱신 절차

업스트림이 업데이트되면:

```bash
SHA=$(curl -sL https://api.github.com/repos/langchain-ai/deepagents/commits/main | python3 -c "import json,sys; print(json.load(sys.stdin)['sha'])")
for f in __init__.py composite.py context_hub.py filesystem.py langsmith.py local_shell.py protocol.py sandbox.py state.py store.py utils.py; do
  curl -sL "https://raw.githubusercontent.com/langchain-ai/deepagents/${SHA}/libs/deepagents/deepagents/backends/${f}" -o "${f}"
done
echo "SHA=${SHA}" > .SHA
```

`.SHA` 파일과 본 README의 SHA·수집일을 함께 갱신할 것.
