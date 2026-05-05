# Research 자료 색인

> Phase 2 산출물 · 1주차 발표 보강 자료
> 수집일: 2026-05-04 · 자료 수: **7건** (한도 5\~8건 안)
> **검증 완료**: 모든 자료 원본 그대로(verbatim) 보관 — paraphrase·자체 합성 0건

---

## 0. 원본 보존 정책

발표·교안에서 정확한 인용을 위해, 모든 research 파일은 다음 원칙으로 저장된다:

- **광고·네비게이션·푸터·구독 박스만 제거**
- 본문은 paraphrase·요약·재구성 **금지** — 원문 그대로
- 자체 합성한 다이어그램·요약 헤딩 **금지**
- 비공식·2차 출처는 frontmatter `note` 에 명시
- 수집 방법(WebFetch / `gh gist view` / Mintlify `.md` endpoint / curl) 도 frontmatter 또는 INDEX 에 명시

---

## 1. 자료 일람

| # | 제목 | 출처 | 1차/2차 | 수집 방법 | 파일 |
|---:|---|---|:---:|---|---|
| 01 | Deep Agents (출시 발표, Harrison Chase) | LangChain Blog | **1차** | WebFetch | [01_deepagents_announcement_langchain-blog.md](01_deepagents_announcement_langchain-blog.md) |
| 02 | Building agents with the Claude Agent SDK | claude.com/blog (Anthropic) | **1차** | WebFetch (308 redirect 후) | [02_claude_code_anthropic.md](02_claude_code_anthropic.md) |
| 03 | How OpenAI's Deep Research Works | blog.promptlayer.com | 2차 | WebFetch | [03_deep_research_promptlayer.md](03_deep_research_promptlayer.md) |
| 04 | In-depth technical investigation into the Manus AI agent | gist.github.com (Renschni) | 2차 | `gh gist view` (raw) | [04_manus_github_gist.md](04_manus_github_gist.md) |
| 05 | `create_deep_agent` API Reference | reference.langchain.com | **1차** | WebFetch | [05_create_deep_agent_api_reference-langchain-com.md](05_create_deep_agent_api_reference-langchain-com.md) |
| 06 | Prebuilt middleware (LangChain & Deep Agents) | docs.langchain.com (OSS) | **1차** | curl + Mintlify `.md` endpoint | [06_middleware_architecture_docs-langchain-com.md](06_middleware_architecture_docs-langchain-com.md) |
| 07 | Default System Prompt (`BASE_AGENT_PROMPT`) | GitHub raw (langchain-ai/deepagents) | **1차** | WebFetch (raw URL) | [07_default_system_prompt_github.md](07_default_system_prompt_github.md) |
| RAG | NotebookLM 합성 보고서 (Q1\~Q6, 교안 §0\~§6 매핑) | NotebookLM (research/ 7건 + 영문 원문 3건 + INDEX 합성) | 파생 | NotebookLM RAG (chat=learning_guide, longer) | [RAG_textbook_synthesis.md](RAG_textbook_synthesis.md) |

**1차 출처**: 5건 (01, 02, 05, 06, 07)
**2차 출처**: 2건 (03, 04 — Deep Research / Manus 는 폐쇄 시스템이라 1차 자료 부재)

> **06 의 실제 페이지 제목**: docs.langchain.com 의 `/deepagents/middleware` URL 에 진짜로 게시된 페이지 제목은 "Prebuilt middleware" 다. LangChain core 미들웨어 카탈로그(provider-agnostic 16종) + Deep Agents 전용 미들웨어(Filesystem, Subagent) 가 한 페이지에 정리되어 있다.

---

## 2. 교안 절 ↔ 자료 매핑 (orphan 검사)

| 교안 절 | 보강 자료 | 우선순위 |
|---|---|:---:|
| §0 들머리 | 01 (스택 위치) | ⭐⭐⭐ |
| §1.1 Vanilla 에이전트 한계 | 02 (Claude Code 의 컨텍스트·툴 사용 패턴) | ⭐⭐ |
| §1.2 Claude Code / Deep Research / Manus 사례 | **02, 03, 04** (3개 시스템 각각 1건) | ⭐⭐⭐ |
| §1.3 패턴의 일반화 — 라이브러리화 | **01** (Harrison Chase 의 디자인 의도 1차 자료) | ⭐⭐⭐ |
| §2.1 Planning — `write_todos` | 06 (To-do list / TodoListMiddleware), 07 (프롬프트의 계획 지침) | ⭐⭐ |
| §2.2 Filesystem | **06** (Filesystem middleware 섹션 + StateBackend / StoreBackend 라우팅 예제) | ⭐⭐⭐ |
| §2.3 Subagents | **06** (Subagent 섹션 + `task` 툴, CompiledSubAgent 예제) | ⭐⭐⭐ |
| §2.4 Long-term Memory | 06 (Filesystem middleware 의 `/memories/` prefix 라우팅) | ⭐⭐⭐ |
| §3.1 환경 준비 | (원문 02-quickstart 로 충분) | — |
| §3.2 검색 도구 정의 | (원문 02-quickstart 로 충분) | — |
| §3.3 `create_deep_agent` 호출 | **05** (시그니처 + 17개 파라미터) | ⭐⭐⭐ |
| §3.4 invoke 백그라운드 5단계 | 06 (미들웨어 체인 — Summarization, To-do list, Filesystem, Subagent 가 어떻게 5단계를 만드는가) | ⭐⭐ |
| §4.1 Core Config | **05** (model / system_prompt / tools 등 17개 인자) | ⭐⭐⭐ |
| §4.2 Features (Backend / Subagents / Interrupts) | 05 (`backend`, `subagents`, `interrupt_on`), 06 (Subagent / Filesystem) | ⭐⭐⭐ |
| §4.3 Model 바꾸기 — 문자열 vs 객체 | (원문 03-customization 으로 충분) | — |
| §4.4 System Prompt 패턴 | **07** (BASE_AGENT_PROMPT 본체 + Claude Code 영감 증거) | ⭐⭐⭐ |
| §5.1 `create_agent` vs LangGraph vs `create_deep_agent` | 01 (Why deepagents) | ⭐⭐ |
| §5.2 의사결정 표 | 01 (라이브러리화 의도) | ⭐⭐ |
| §6.1 컨텍스트·메모리·스킬 다리 | 06 (Subagent 격리 + Filesystem `/memories/`) | ⭐⭐ |
| §6.2 백엔드·샌드박스 다리 | 06 (Shell tool / Context editing), 05 (`backend` 파라미터) | ⭐⭐ |

**Orphan 검사**: ✅ 모든 자료가 최소 1개 이상의 교안 절에 매핑됨 (orphan 0건).

**가장 많이 인용될 자료**: 06 (prebuilt middleware) — 7개 절에 등장, §2 의 4가지 내장 능력 보강의 핵심.

---

## 3. 자료별 핵심 인용 포인트

### 01. Deep Agents 출시 발표 (LangChain Blog)

- "Deep agents are agents that perform **planning**, use **sub agents**, have access to a **file system**, and have a **detailed prompt**."
- "Acknowledgements: this exploration was primarily inspired by Claude Code..."
- 4가지 디자인 축의 1차 출처 → 발표 §1.3 의 핵심 인용.

### 02. Building agents with the Claude Agent SDK (Anthropic 공식)

- 핵심 원리: *"The key design principle behind the Claude Agent SDK is to give your agents a computer, allowing them to work like humans do."*
- 에이전트 피드백 루프 4단계: **gather context → take action → verify work → repeat**
- 핵심 도구 카테고리: file system / agentic search / semantic search / **subagents** / compaction / tools / bash & scripts / code generation / MCPs
- §1.2 Claude Code 사례 + §1.1 Vanilla 한계 보강.
- 작성자: Thariq Shihipar.

### 03. How OpenAI's Deep Research Works (PromptLayer, 비공식 2차)

- Deep Research = OpenAI o3 기반 자율 리서치 에이전트.
- **Five-Phase Process**: Clarification → Decomposition → Iterative Search → Multi-format Reading → Synthesis with Citations.
- ReAct 루프 (Plan → Act → Observe).
- Stopping mechanism: coverage-based vs budget-driven (시간 20\~30분 / 검색 30\~60회 / 페이지 120\~150 / 추론 150\~200 iter).
- §1.2 Deep Research 사례 보강. **비공식 — footnote 표기 필수**.

### 04. Manus AI agent (GitHub Gist 리버스 분석, 비공식 2차)

- Foundation: Claude 3.5/3.7 + fine-tuned Qwen.
- **CodeAct paradigm** — 도구 호출 대신 짧은 Python 스크립트 생성.
- Iterative loop: **Analyze → Plan/Select → Execute → Observe** (event stream).
- Persistent scratchpad: 가상 파일시스템 + `todo.md` 파일로 진행 추적.
- Multi-agent: web browsing / coding / data analysis 각자 isolated sandbox.
- §1.2 Manus 사례 보강. **비공식 GitHub Gist — footnote 표기 필수**.

### 05. `create_deep_agent` API Reference (1차)

- 17개 파라미터: `model`, `tools`, `system_prompt`, `middleware`, `subagents`, `skills`, `memory`, `permissions`, `backend`, `interrupt_on`, `response_format`, `context_schema`, `checkpointer`, `store`, `debug`, `name`, `cache`
- 반환 타입: `CompiledStateGraph[AgentState[ResponseT], ContextT, _InputAgentState, _OutputAgentState[ResponseT]]` — **LangGraph 객체임을 보여주는 결정적 증거**.
- 기본 모델: `claude-sonnet-4-6` (DESIGN.md 의 `claude-sonnet-4-5-20250929` 보다 한 단계 위 — 발표 시 갱신 필요).
- 빌트인 도구: `write_todos`, `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `execute`, `task`.
- §3.3, §4.1, §4.2 모두 이 자료 기반.

### 06. Prebuilt middleware (docs.langchain.com OSS, 1차)

> **이 페이지는 LangChain core 미들웨어 카탈로그 + Deep Agents 전용 미들웨어를 한 곳에 정리한 페이지** 이다. Deep Agents 전용 아키텍처 페이지가 따로 있는 게 아니다.

- **Provider-agnostic middleware (16종)**: Summarization, Human-in-the-loop, Model call limit, Tool call limit, Model fallback, PII detection, **To-do list**, LLM tool selector, Tool retry, Model retry, LLM tool emulator, Context editing, Shell tool, File search, **Filesystem**, **Subagent**.
- **Filesystem middleware**: 가상 파일시스템 + Backend 추상화 (`StateBackend` / `StoreBackend` / `CompositeBackend` with `/memories/` prefix routing).
- **Subagent middleware**: 메인 에이전트가 항상 "general-purpose" subagent 에 접근. 커스텀 subagent 가능.
- **Provider-specific middleware**: Anthropic / AWS / OpenAI 별 prompt caching · content moderation 등.
- §2.1\~§2.4 모든 4대 능력의 미들웨어 출처.

### 07. Default System Prompt (`BASE_AGENT_PROMPT`, 1차)

- GitHub: `libs/deepagents/deepagents/graph.py` line 56\~97 (~42라인, ~2,100자).
- README 명시: *"This project was primarily inspired by Claude Code"* (Acknowledgements).
- 본문 키워드: "NEVER add unnecessary preamble", **Understand → Act → Verify** 3단계 워크플로.
- Sonnet 4.6 SUFFIX: `<use_parallel_tool_calls>`, `<investigate_before_answering>`, `<tool_result_reflection>` XML 태그.
- 4단 합성 구조: `USER → (BASE 또는 CUSTOM) → SUFFIX`.
- §4.4 System Prompt 패턴 + trivia 슬라이드의 결정적 증거.

---

## 4. 추가 수집 후보 (Phase 3 진입 전 결정)

DESIGN.md §9 의 R5, R7, R8 중 미수집 자료:

| # | 주제 | 보강 대상 | 추천도 |
|:---:|---|---|:---:|
| R5 | `write_todos` 실제 출력 예시 (트레이스 캡처) | §2.1, §3.4 | ⚪ 보류 — 실행 스크립트로 직접 캡처 가능 |
| R7 | 실제 사용 사례 — 블로그/튜토리얼 1건 | §1.2 보강 | ⚪ 보류 — 01 의 use case 절로 충분 |
| R8 | `create_agent` vs `create_deep_agent` 비교 | §5.1, §5.2 | 🟡 추가 검토 — 결정표 강화에 도움 |

**제안**: 현재 7건으로 충분. R8 추가 시 8건 (한도 끝). Phase 3 작성 중 부족하다고 판단되면 그때 추가.

---

## 5. Verify 체크리스트

- [x] 모든 자료가 교안 어느 절에 쓰일지 명시됨 (orphan 0건) — §2 매핑 표
- [x] URL 모두 살아있음 (수집 시점 2026-05-04 기준)
- [x] 자료 수: **7건** — 5\~8개 범위 안
- [x] 1차 출처 비율: 5/7 ≈ 71% (높음)
- [x] 비공식 2차 출처 (03, 04) 는 frontmatter `note` 에 명시됨
- [x] **모든 자료 원본 그대로(verbatim) 보관** — paraphrase·자체 합성 0건
  - 02: WebFetch (claude.com redirect 추적)
  - 03: WebFetch (저자 메타데이터 + 직접 인용 보존)
  - 04: `gh gist view` raw (460 라인, ~84KB 그대로)
  - 06: Mintlify `.md` endpoint 로 raw markdown 받음 (1485 라인, ~57KB)
  - 01, 05, 07: 초기 수집 시 이미 raw 발췌 (재검증 완료)

---

## 6. 인용 정책

- 발표/교안에서 인용 시 **footnote `[^N]`** 사용 → 부록 C (참고문헌) 에서 이 INDEX.md 와 매핑.
- 직접 인용은 큰따옴표 + 출처 URL 명시.
- paraphrase 시에도 출처 footnote 필수.
- 비공식 출처 (03, 04) 인용 시 본문에 "(비공식 분석)" 표시.
- 06 인용 시 "Deep Agents 전용 페이지가 아닌 LangChain prebuilt middleware 카탈로그" 라는 출처 성격을 footnote 에 한 번 명시 (혼동 방지).
