# Research 자료 색인 — 2주차 Backends

> Phase 2 (RESEARCH) 산출물 · 2주차 발표 보강 자료
> 수집일: 2026-05-15 · 자료 수: **5건** (DESIGN.md §9 5건 목표 충족)
> **검증 완료**: 4건 verbatim (curl + Mintlify `.md` 또는 GitHub raw), 1건은 로컬 패키지 스냅샷 등재

---

## 0. 원본 보존 정책

발표·교안에서 정확한 인용을 위해, 모든 research 파일은 다음 원칙으로 저장된다 (week1 컨벤션 그대로):

- 본문은 paraphrase·요약·재구성 **금지** — 원문 그대로
- 자체 합성한 다이어그램·요약 헤딩 **금지**
- 비공식·2차 출처는 frontmatter `source_type` 에 명시
- 수집 방법(`curl + Mintlify .md` / `curl + GitHub raw` / WebFetch / 로컬 스냅샷)을 frontmatter 에 명시

> **주의**: WebFetch 는 AI 가 처리한 결과를 반환하므로 verbatim 보장이 안 됨. 본 INDEX 에 등재된 5건은
> 모두 `curl` 기반 원문 다운로드 또는 로컬 파일 등재로 처리되었다. WebFetch 결과는 단 1건도 사용하지 않음.

---

## 1. 자료 일람

| # | 제목 | 출처 | 1차/2차 | 수집 방법 | 교안 매핑 | 파일 |
|---:|---|---|:---:|---|---|---|
| 01 | LangGraph Persistence — Checkpoints, State, Storage | docs.langchain.com | **1차** | curl + Mintlify `.md` | §5 (StoreBackend), §3 (StateBackend 컨텍스트) | [01_langgraph_persistence_concepts-docs-langchain.md](01_langgraph_persistence_concepts-docs-langchain.md) (665L) |
| 02 | `BackendProtocol` 시그니처 (deepagents 패키지 소스) | github.com/langchain-ai/deepagents | **1차** | 로컬 verbatim 스냅샷 (SHA `4421bec`) | §2 (Backend Protocol 한 장) | [`../original_docs/deepagents_backends/protocol.py`](../original_docs/deepagents_backends/protocol.py) (852L) |
| 03 | `deepagents-backends` — S3 + Postgres 구현체 (README) | github.com/DiTo97/deepagents-backends | **1차** (커뮤니티 구현) | curl + GitHub raw | §7 (가상 FS — S3 스타일 production 레퍼런스) | [03_deepagents-backends_dito97-github-readme.md](03_deepagents-backends_dito97-github-readme.md) (511L) |
| 04 | LangChain Middleware — Overview | docs.langchain.com | **1차** | curl + Mintlify `.md` | §8 (Policy hooks — 미들웨어 레이어) | [04_langchain_middleware-docs-langchain.md](04_langchain_middleware-docs-langchain.md) (120L) |
| 05 | Ollama — Tool calling capabilities | docs.ollama.com | **1차** | curl + Mintlify `.md` | walkthrough.ipynb 사전 검증 (gemma4:31b tool-use) | [05_ollama_tool_calling-docs-ollama.md](05_ollama_tool_calling-docs-ollama.md) (798L) |

**1차 출처**: 5건 (100%) — 공식 LangChain 문서 2건 + 공식 Ollama 문서 1건 + 공식 deepagents 패키지 1건 + 커뮤니티 production 구현 1건
**2차 출처**: 0건

---

## 2. 교안 섹션별 보강 매핑

| 교안 § | 항목 | 출처 자료 |
|---|---|---|
| §2 Backend Protocol | 6개 메서드 시그니처 풀버전 | 02 (`protocol.py` L?-?) |
| §3 StateBackend | thread / checkpoint 작동 원리 | 01 (Threads and Checkpoints) |
| §5 StoreBackend | BaseStore namespace, search, semantic search | 01 (Memory Store: Cross-Thread State) |
| §7 가상 FS — S3 스타일 | production-ready 구현 (다중 클라이언트, retry, pooling) | 03 (deepagents-backends README) |
| §8 Policy hooks | 백엔드 정책(GuardedBackend) ↔ 미들웨어 정책(PIIRedaction 등) 두 레이어 | 04 (LangChain Middleware Overview) + 05-backends.md L219-end (이미 보유) |
| walkthrough 실행 사전 | `ollama show gemma4:31b` 도구 호출 지원 확인 | 05 (Ollama tool-calling 컨벤션) |

---

## 3. 다음 단계 (Phase 3 진입 전 검증)

- [x] 5건 등재 완료
- [x] 모든 자료 verbatim (WebFetch 결과 사용 0건)
- [x] 교안 §섹션 매핑 표 완성
- [ ] (Phase 3 작업) 텍스트북 본문에서 본 자료 인용 시 정확한 라인/단락 픽업
- [ ] (사용자 확인) gemma4:31b 가 로컬 `ollama list` 에 존재하고 tool-use 지원하는지 — 미지원 시 변경 필요

---

## 4. 사용자 확인 요청 (Phase 3 시작 전)

- gemma4:31b 모델 가용성 — 본 시점(2026-05-15) Ollama 라이브러리에 31b 변종 미확인.
  로컬에서 `ollama list | grep gemma` 결과 공유해 주시면 walkthrough 의 모델명 확정 가능.
  대안 후보: `gemma4:27b`, `gemma3:27b` (tool-use 신뢰도 가장 높은 변종)
