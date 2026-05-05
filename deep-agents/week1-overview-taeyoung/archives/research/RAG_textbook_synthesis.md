---
title: NotebookLM RAG 합성 보고서 — 1주차 발표 교안 (TEXTBOOK) 작성용 참조
source_type: NotebookLM RAG synthesis (파생 자료)
notebook_id: 12fdc455-bcd2-4579-8722-8b72392b23b7
notebook_url: https://notebooklm.google.com/notebook/12fdc455-bcd2-4579-8722-8b72392b23b7
queried: 2026-05-04
queries: 6 (Q1\~Q6)
note: |
  research/ 의 7개 1차/2차 자료 + 영문 원문 3개 + INDEX.md 를 NotebookLM 노트북에
  올린 뒤, 교안 §0\~§6 매핑 질문 6개를 RAG 로 던져 받은 한국어 답변을 합성한 자료.
  NotebookLM 답변에는 inline [소스명] 인용이 포함되어 있어 원본과 즉시 매칭된다.
  파생 자료이므로 발표/교안 인용 시 항상 원본(research/0N_*.md)을 교차 확인한다.
---

# NotebookLM RAG 합성 보고서 — 1주차 발표 교안 작성용 참조

> 이 문서는 NotebookLM 노트북 ["Deep Agent — 1주차 발표 보강자료 (태영)"](https://notebooklm.google.com/notebook/12fdc455-bcd2-4579-8722-8b72392b23b7) 에 11개 소스(research/ 7건 + 영문 원문 3건 + INDEX)를 올린 뒤, 6개 질문을 RAG 로 던져 받은 한국어 답변을 정리한 합성(synthesis) 보고서다.
>
> 각 답변의 inline `[소스명]` 인용은 NotebookLM 이 자동으로 단 것이며, 우리가 보유한 research/ 파일명·영문 원문 파일명과 일치한다. 부록 A의 원본 링크 매핑 표로 즉시 추적 가능하다.

---

## 목차

1. [Q1. 왜 Deep Agent 인가 — Vanilla 한계 / 3대 사례 / Harrison Chase 4축 / 생태계 위치](#q1-왜-deep-agent-인가)  *(교안 §1)*
2. [Q2. 4가지 내장 능력 — 도구 / 미들웨어 / 동작 / 시나리오 + Backend 추상화](#q2-4가지-내장-능력)  *(교안 §2)*
3. [Q3. `create_deep_agent` 청사진 — 17개 파라미터 / 반환 타입 / 빌트인 도구 / Core Config & Features](#q3-create_deep_agent-청사진)  *(교안 §3.3, §4.1, §4.2)*
4. [Q4. System Prompt 패턴 — BASE_AGENT_PROMPT / 4단 합성 / Sonnet 4.6 SUFFIX / Trivia](#q4-system-prompt-패턴)  *(교안 §4.4)*
5. [Q5. 언제 쓰나 — `create_agent` vs LangGraph vs `create_deep_agent` 의사결정](#q5-언제-쓰나)  *(교안 §5)*
6. [Q6. Model 바꾸기 — 문자열 / 객체 / tool calling 필수 / 기본 모델](#q6-model-바꾸기)  *(교안 §4.3)*
7. [부록 A. 인용 ↔ 원본 링크 매핑](#부록-a-인용--원본-링크-매핑)
8. [부록 B. 사용 정책](#부록-b-사용-정책)

---

## Q1. 왜 Deep Agent 인가

> **교안 매핑**: §1.1 (Vanilla 한계), §1.2 (3대 사례), §1.3 (라이브러리화), §0 (생태계 위치)

Deep Agent 라이브러리(`deepagents`)는 단일 루프 기반의 기존 에이전트가 가진 한계를 극복하고, 복잡하고 장기적인 작업을 수행할 수 있는 범용적인 아키텍처를 제공하기 위해 등장했다 [01_deepagents_announcement_langchain-blog.md].

### 1.1 Vanilla LLM 에이전트의 구체적 한계 ('Shallow' 현상)

단순히 루프를 돌며 도구를 호출하는 전통적인(Vanilla) 에이전트 아키텍처는 긴 시간과 복잡한 절차가 필요한 작업에서 깊이를 가지지 못하고 '얕은(shallow)' 수준에 머무는 한계가 있다 [01_deepagents_announcement_langchain-blog.md].

- **계획 부재 (Lack of Planning)**: 기존 에이전트는 장기적인 목표를 위해 복잡한 작업을 세부 단계로 분해하고 전략을 세우는 능력이 부족하다 [01_deepagents_announcement_langchain-blog.md].
- **컨텍스트 윈도우 오버플로우**: 웹 검색이나 RAG 처럼 결과값의 길이가 가변적인 도구를 사용할 경우, 반환된 텍스트가 에이전트의 컨텍스트 윈도우를 순식간에 채워버리는 문제가 발생한다 [06_middleware_architecture_docs-langchain-com.md].
- **컨텍스트 격리 부재**: 여러 도구와 하위 작업의 결과가 하나의 메인 컨텍스트에 뒤섞이면 에이전트가 혼란을 겪게 되므로, 컨텍스트를 깔끔하게 유지하면서도 특정 작업에 깊이 파고들 수 있도록 돕는 격리(Isolation) 메커니즘이 필요하다 [01-overview.md].

### 1.2 영감을 받은 3대 사례

#### Claude Code

개발자처럼 파일 시스템에 접근하고 터미널의 bash 명령어를 실행할 수 있는 가상 컴퓨터 환경을 모델에게 제공한다 [02_claude_code_anthropic.md]. 이 시스템은 **'컨텍스트 수집 → 행동 취하기 → 작업 검증 → 반복'(gather context → take action → verify work → repeat)** 이라는 강력한 피드백 루프를 통해 코딩뿐만 아니라 다양한 디지털 워크플로우를 처리한다 [02_claude_code_anthropic.md].

#### OpenAI Deep Research

사람의 개입 없이 최장 30분 동안 웹을 탐색하며 데이터를 수집하고 분석하는 자율 리서치 에이전트 [03_deep_research_promptlayer.md]. 작업을 명확히 한 후 하위 질문으로 분해(Decomposition)하고, 검색 결과를 읽으며 지속적으로 다음 쿼리를 수정하는 **ReAct(Plan-Act-Observe)** 루프를 돈다 [03_deep_research_promptlayer.md]. 5단계 프로세스: Clarification → Decomposition → Iterative Search → Multi-format Reading → Synthesis with Citations.

#### Manus

**'CodeAct' 패러다임**을 차용하여 단순한 고정 도구 API 대신 실행 가능한 Python 코드를 생성해 웹 브라우저나 시스템 명령을 자율적으로 제어한다 [04_manus_github_gist.md]. 분석 → 계획 → 실행 → 관찰(Analyze → Plan → Execute → Observe) 루프를 반복하며, 가상 환경의 파일 시스템(예: `todo.md`)을 활용해 중간 과정을 메모하고 추적한다 [04_manus_github_gist.md].

### 1.3 Harrison Chase 의 4가지 디자인 의도 (패턴 일반화)

LangChain 의 창립자 Harrison Chase 는 위 세 시스템(특히 Claude Code)이 범용적인 능력을 갖출 수 있었던 원리를 추상화·일반화하여 `deepagents` 를 개발했다 [01_deepagents_announcement_langchain-blog.md]. 다음 4가지 핵심 요소를 내장 컴포넌트로 제공한다.

| # | 디자인 축 | 핵심 도구 / 컴포넌트 | 설명 |
|:---:|---|---|---|
| 1 | **Detailed Prompt** | 길고 상세한 시스템 프롬프트 | 상황별 예시(few-shot)와 도구 사용 규칙을 꼼꼼하게 정의 [01_deepagents_announcement_langchain-blog.md] |
| 2 | **Planning Tool** | `write_todos` | 복잡한 작업 추적용 To-do 리스트. 흥미롭게도 시스템에 물리적 변화를 주지 않는 'no-op(무동작)' 도구지만, 에이전트가 궤도를 벗어나지 않도록 강제하는 컨텍스트 엔지니어링 전략 [01_deepagents_announcement_langchain-blog.md] |
| 3 | **Sub Agents** | `task` | 작업 분할 + 컨텍스트 격리. 메인 에이전트는 컨텍스트 윈도우를 깨끗하게 유지하면서 각 하위 에이전트가 세부 주제에 깊이 집중하도록 위임 [01_deepagents_announcement_langchain-blog.md, 01-overview.md] |
| 4 | **File System** | `ls`, `read_file`, `write_file`, `edit_file` | 컨텍스트 오프로딩 + 공유 작업 공간 + 메모장. Manus 도 파일시스템을 메모리로 적극 활용 [01_deepagents_announcement_langchain-blog.md, 01-overview.md] |

### 1.4 LangChain 생태계에서의 위치

`deepagents` 는 LangChain 생태계의 기존 컴포넌트들을 유기적으로 결합하는 상위 레벨 라이브러리로 작동한다 [01-overview.md].

- **LangGraph** — 그래프 기반의 실행 흐름·상태 관리·영구 메모리(Store) 담당 [01-overview.md]
- **LangChain** — 모델 통합 인터페이스 + 다양한 커스텀 도구를 매끄럽게 연결 [01-overview.md]
- **LangSmith** — 모니터링(Observability) + 평가 + 프로덕션 배포 [01-overview.md]

```text
┌──────────────────────────────────────┐
│  deepagents (이 발표)                 │
│   = create_deep_agent()              │
│   = create_agent(middleware=[...])   │
└──────────────────────────────────────┘
            ↓ 얹힘
┌──────────────────────────────────────┐
│  LangChain (Tools / Models)          │
└──────────────────────────────────────┘
            ↓ 얹힘
┌──────────────────────────────────────┐
│  LangGraph (StateGraph / Store)      │
└──────────────────────────────────────┘
            ↓ 관측
┌──────────────────────────────────────┐
│  LangSmith (Observe / Eval / Deploy) │
└──────────────────────────────────────┘
```

---

## Q2. 4가지 내장 능력

> **교안 매핑**: §2.1 Planning, §2.2 Filesystem, §2.3 Subagents, §2.4 Long-term Memory

### 2.1 계획 수립 (Planning)

| 항목 | 내용 |
|---|---|
| 제공 도구 | `write_todos` [05_create_deep_agent_api_reference-langchain-com.md] |
| 담당 미들웨어 | `TodoListMiddleware` [06_middleware_architecture_docs-langchain-com.md] |
| 동작 원리 | 에이전트가 복잡한 작업을 개별 단계로 쪼개어 계획을 세우고, 진행 상황을 추적하며 새로운 정보에 맞춰 계획을 수정 [01-overview.md]. **이 도구는 시스템에 물리적 변화를 주지 않는 'no-op' 도구**지만, 에이전트가 궤도를 벗어나지 않도록 강제하는 강력한 컨텍스트 엔지니어링 전략으로 작용 [01_deepagents_announcement_langchain-blog.md] |
| 사용 시나리오 | (1) 여러 도구의 조율이 필요한 복잡한 다단계 작업 [06_middleware_architecture_docs-langchain-com.md]. (2) 장시간 실행되어 진행 상황의 가시성이 중요한 작업 [06_middleware_architecture_docs-langchain-com.md] |

### 2.2 파일 시스템 (Filesystem)

| 항목 | 내용 |
|---|---|
| 제공 도구 | `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` [05_create_deep_agent_api_reference-langchain-com.md] |
| 담당 미들웨어 | `FilesystemMiddleware` [06_middleware_architecture_docs-langchain-com.md] |
| 동작 원리 | 가변 길이 결과를 반환하는 도구(예: 웹검색·RAG)에서 발생하는 컨텍스트 윈도우 오버플로우 방지 [01-overview.md, 06_middleware_architecture_docs-langchain-com.md]. 결과물을 메인 컨텍스트에 모두 올리는 대신, 에이전트 상태(Graph State)에 구축된 로컬 파일 시스템에 쓰고 읽음으로써 단기 메모리를 관리 [06_middleware_architecture_docs-langchain-com.md] |
| 사용 시나리오 | (1) 방대한 웹 검색 결과나 문서 텍스트를 파일로 오프로드(offload)하여 컨텍스트 창을 확보 [01-overview.md]. (2) `glob`이나 `grep`으로 대규모 코드베이스를 탐색하고 특정 패턴을 찾을 때 [06_middleware_architecture_docs-langchain-com.md] |

### 2.3 하위 에이전트 (Subagents)

| 항목 | 내용 |
|---|---|
| 제공 도구 | `task` [01-overview.md, 05_create_deep_agent_api_reference-langchain-com.md] |
| 담당 미들웨어 | `SubAgentMiddleware` [06_middleware_architecture_docs-langchain-com.md] |
| 동작 원리 | 복잡한 하위 작업을 전문화된 서브 에이전트에게 위임 [01-overview.md]. 메인(감독) 에이전트는 중간 도구 호출로 인한 컨텍스트 비대화 없이 깔끔한 요약 답변만 받아 **완벽한 '컨텍스트 격리'** 달성 [06_middleware_architecture_docs-langchain-com.md]. 기본적으로 메인 에이전트와 동일한 도구를 가진 'general-purpose' 서브 에이전트가 내장 [06_middleware_architecture_docs-langchain-com.md] |
| 사용 시나리오 | (1) 메인 에이전트는 전체 글쓰기 계획을 관리하고, 특정 주제 깊은 리서치를 하위 에이전트에게 위임 [01-overview.md]. (2) 각기 다른 시스템 프롬프트와 도구를 가진 전문가 에이전트(코딩 전용, 검색 전용)를 병렬 활용 [06_middleware_architecture_docs-langchain-com.md, 02_claude_code_anthropic.md] |

### 2.4 장기 메모리 (Long-term Memory) + Backend 추상화

| 항목 | 내용 |
|---|---|
| 제공 도구 | 기본 파일 시스템 도구를 동일하게 사용 (`/memories/` prefix 라우팅) |
| 담당 미들웨어/컴포넌트 | `FilesystemMiddleware` + `StoreBackend` 결합 [06_middleware_architecture_docs-langchain-com.md] |
| 동작 원리 | LangGraph 의 Store 기능을 이용해 대화·스레드를 넘나드는 영구 메모리 유지 [01-overview.md]. 파일 시스템은 **Backend 추상화**를 통해 저장 위치를 결정 [06_middleware_architecture_docs-langchain-com.md] |

#### Backend 라우팅 3종

| Backend | 저장 위치 | 수명 |
|---|---|---|
| **`StateBackend`** (기본값) | 현재 그래프의 단기/휘발성 상태에 파일 저장 [05_create_deep_agent_api_reference-langchain-com.md, 06_middleware_architecture_docs-langchain-com.md] | 스레드 종료 시 사라짐 |
| **`StoreBackend`** | LangGraph 의 Store 사용 — 스레드 간에도 유지되는 영구 저장소 [06_middleware_architecture_docs-langchain-com.md] | 영속 (cross-thread) |
| **`CompositeBackend`** | 특정 파일 경로(prefix)에 따라 백엔드 분기 — 예: `/memories/` 경로를 `StoreBackend` 로 라우팅 [06_middleware_architecture_docs-langchain-com.md] | prefix 별 |

**시나리오**: 사용자의 과거 대화 기록·취향(예: 코드 작성 스타일, 템플릿)을 `/memories/user_pref.txt` 에 저장하면 다음 스레드에서도 영구적으로 살아남음 [01-overview.md, 06_middleware_architecture_docs-langchain-com.md].

---

## Q3. `create_deep_agent` 청사진

> **교안 매핑**: §3.3 호출, §4.1 Core Config, §4.2 Features

`create_deep_agent()` 는 복잡한 작업을 수행할 수 있는 Deep Agent 를 생성하는 핵심 API [05_create_deep_agent_api_reference-langchain-com.md].

### 3.1 17개 파라미터 (전체 표)

| 파라미터명 | 타입 | 기본값 | 역할 |
|---|---|---|---|
| **`model`** | `str \| BaseChatModel \| None` | `None` | 에이전트가 사용할 LLM. 문자열(예: `openai:gpt-5`)이나 초기화된 LangChain 모델 객체 |
| **`tools`** | `Sequence[BaseTool...] \| None` | `None` | 추가 커스텀 도구. 빌트인 도구와 자동 병합 |
| **`system_prompt`** | `str \| SystemMessage \| None` | `None` | 기본 시스템 프롬프트의 맨 앞에 추가될 커스텀 지시사항 |
| **`middleware`** | `Sequence[AgentMiddleware]` | `()` | 기본 미들웨어와 tail 미들웨어 사이에 삽입될 추가 미들웨어 |
| **`subagents`** | `Sequence[SubAgent...] \| None` | `None` | `task` 도구를 통해 호출할 하위 에이전트 명세 |
| **`skills`** | `list[str] \| None` | `None` | 스킬 파일(코드/지침) 경로 목록 |
| **`memory`** | `list[str] \| None` | `None` | 시작 시 시스템 프롬프트에 로드할 메모리 파일 (`AGENTS.md`) |
| **`permissions`** | `list[FilesystemPermission] \| None` | `None` | 파일시스템 도구 접근 권한 규칙 |
| **`backend`** | `BackendProtocol \| BackendFactory \| None` | `None` | 파일 저장 + 셸 실행 백엔드 |
| **`interrupt_on`** | `dict[str, bool \| InterruptOnConfig] \| None` | `None` | 인간 승인 인터럽트(HITL) — 도구 호출 전 중지 |
| **`response_format`** | `ResponseFormat... \| None` | `None` | 구조화된 출력 형식 |
| **`context_schema`** | `type[ContextT] \| None` | `None` | 실행 주기 불변 컨텍스트 스키마 |
| **`checkpointer`** | `Checkpointer \| None` | `None` | 실행 간 상태 저장/로드 |
| **`store`** | `BaseStore \| None` | `None` | `StoreBackend` 사용 시 영구 저장소 객체 |
| **`debug`** | `bool` | `False` | 디버그 모드 |
| **`name`** | `str \| None` | `None` | 에이전트 이름 |
| **`cache`** | `BaseCache \| None` | `None` | 캐시 객체 |

> 출처: [05_create_deep_agent_api_reference-langchain-com.md] (전체 17개 파라미터)

### 3.2 반환 타입: `CompiledStateGraph` 의 의미

`create_deep_agent()` 는 `CompiledStateGraph[AgentState[ResponseT], ContextT, _InputAgentState, _OutputAgentState[ResponseT]]` 를 반환한다 [05_create_deep_agent_api_reference-langchain-com.md].

이는 Deep Agent 가 완전히 새로운 프레임워크가 아니라, **LangGraph 의 상태 그래프(State Graph) 객체로 컴파일된다는 결정적 증거**다. LangGraph 의 노드와 엣지로 구성된 실행 흐름을 그대로 따르며, 기존 LangGraph 생태계(LangSmith 등)와 완벽 호환 [01-overview.md, 05_create_deep_agent_api_reference-langchain-com.md].

### 3.3 빌트인 도구 (4개 그룹)

| 그룹 | 도구 |
|---|---|
| 계획 수립 | `write_todos` |
| 파일 시스템 | `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` |
| 코드 실행 | `execute` (백엔드가 `SandboxBackendProtocol` 구현 시에만 동작 — 그 외 에러 메시지) |
| 하위 에이전트 | `task` |

> 출처: [05_create_deep_agent_api_reference-langchain-com.md]

### 3.4 ⚠ "Deep agents require a LLM that supports tool calling" 경고

API 문서 상단 경고 [05_create_deep_agent_api_reference-langchain-com.md].

이유: Deep Agent 의 핵심 동작 원리(파일시스템 조작, 서브에이전트 생성, 계획 수립 등)가 **모두 LLM 의 자율적인 함수 호출(Function Calling) 기능을 통해 이루어지기 때문**. 도구 호출 기능이 없거나 약한 모델은 에이전트 루프 자체가 성립하지 않는다.

### 3.5 Core Config 와 Features 의 분리

파라미터들은 논리적으로 두 그룹 [05_create_deep_agent_api_reference-langchain-com.md]:

- **Core Config (핵심 설정)**: 두뇌·목적 설정 — `model`, `system_prompt`, `tools`
- **Features (고급 확장)**: 환경 상호작용 제어 — `backend` (파일/실행), `subagents` (멀티 위임), `interrupt_on` (HITL)

### 3.6 기본 모델 식별자

`model` 파라미터 미지정 시 기본값 = **`claude-sonnet-4-6`** [05_create_deep_agent_api_reference-langchain-com.md]
(원문 03-customization.md 에는 한 단계 이전 식별자 `claude-sonnet-4-5-20250929` 가 표기되어 있어 — 발표 시 최신 reference.langchain.com 의 `claude-sonnet-4-6` 으로 갱신 필요 [03-customization.md])

---

## Q4. System Prompt 패턴

> **교안 매핑**: §4.4 System Prompt 패턴 + 발표 trivia

### 4.1 BASE_AGENT_PROMPT 의 핵심 섹션

`deepagents` 의 기본 시스템 프롬프트는 에이전트가 일관되고 자율적으로 행동하도록 엄격한 지침을 제공 [07_default_system_prompt_github.md].

| 섹션 | 핵심 지시 |
|---|---|
| **Core Behavior** | "불필요한 서문을 절대 추가하지 마라(NEVER add unnecessary preamble)" — 인사말·메타 설명을 생략하고 즉시 도구 사용으로 작업 돌입 [07_default_system_prompt_github.md] |
| **Professional Objectivity** | 객관성 유지, 사용자 의견에 맹목적 동의 금지 |
| **Doing Tasks (3단계)** | **Understand → Act → Verify** 워크플로 — 모든 작업을 이 3단계로 처리해 복잡한 작업 성공률을 높임 [07_default_system_prompt_github.md] |
| **Clarifying Requests** | 명확한 목표 설정을 위해 필요시 사용자에게 질문 |
| **Progress Updates** | 긴 작업 동안 진행 상황 알림 |

### 4.2 "Claude Code 영감" 의 증거

`deepagents` 의 README.md 에는 **"이 프로젝트는 주로 Claude Code 에서 영감을 받았으며, Claude Code 를 범용적으로 만든 요소를 파악하고 이를 일반화하려는 시도"** 라는 Acknowledgements 가 분명하게 명시 [07_default_system_prompt_github.md].

증거:
- Anthropic 공식 prompting guide 의 XML 태그 구조 (`<use_parallel_tool_calls>` 등) 를 그대로 차용 [07_default_system_prompt_github.md]
- Understand → Act → Verify 3단계 = Claude Code 의 *"gather context → take action → verify work → repeat"* 피드백 루프 [02_claude_code_anthropic.md] 와 동일 계보

### 4.3 4단 합성 구조 — `USER → (BASE 또는 CUSTOM) → SUFFIX`

최종적으로 에이전트에게 전달되는 프롬프트는 **4단 합성** 으로 조립된다 [07_default_system_prompt_github.md, 05_create_deep_agent_api_reference-langchain-com.md]:

```text
┌────────────────────────────────────────┐
│ USER  ← system_prompt= 인자로 넘긴 커스텀  │
├────────────────────────────────────────┤
│ BASE  ← BASE_AGENT_PROMPT (기본)         │
│  또는 CUSTOM ← HarnessProfile 매칭 시 대체  │
├────────────────────────────────────────┤
│ SUFFIX ← HarnessProfile.system_prompt_  │
│         suffix (모델별 자동 추가)          │
└────────────────────────────────────────┘
       (블랙라인 \n\n 으로 결합)
```

### 4.4 Anthropic Sonnet 4.6 Harness 의 SUFFIX

사용자가 `claude-sonnet-4-6` 같은 모델을 선택하면, 해당 모델에 등록된 `HarnessProfile` 이 작동하여 BASE 끝에 전용 SUFFIX 를 자동 추가 [05_create_deep_agent_api_reference-langchain-com.md, 07_default_system_prompt_github.md].

이 SUFFIX 는 Claude 모델 성능 극대화를 위한 특수 XML 태그 지시어를 포함 [07_default_system_prompt_github.md]:

| XML 태그 | 의미 |
|---|---|
| `<use_parallel_tool_calls>` | 의존성 없는 도구 호출은 모두 병렬로 |
| `<investigate_before_answering>` | 답변 전 관련 파일 읽기·조사 |
| `<tool_result_reflection>` | 도구 결과 받은 뒤 반성·다음 단계 계획 |

### 4.5 발표용 Trivia — `write_todos` 의 비밀

> **발표 hook 으로 강력 추천**: LangChain 창립자 Harrison Chase 에 따르면, 에이전트가 작업 계획을 세우고 추적할 때 쓰는 **`write_todos` 도구는 사실 시스템에 어떤 물리적 동작이나 변화도 일으키지 않는 'no-op(무동작)' 도구**다 [01_deepagents_announcement_langchain-blog.md].
>
> 이 도구는 단지 에이전트가 긴 시간 동안 궤도를 이탈하지 않도록 스스로 할 일을 텍스트로 적고 기억하게 만드는 순수한 **'컨텍스트 엔지니어링 전략'** 에 불과하다 [01_deepagents_announcement_langchain-blog.md].

> 원문(Harrison Chase): *"Claude Code uses a Todo list tool. Funnily enough — this doesn't do anything! It's basically a no-op."*

---

## Q5. 언제 쓰나

> **교안 매핑**: §5.1 (3가지 도구 비교), §5.2 (의사결정 표)

### 5.1 의사결정 표

| 구축 방식 | 권장 시나리오 | 주요 특징 |
|---|---|---|
| **`create_agent`** (LangChain) | 단순한 도구 호출 위주의 얕고(shallow) 짧은 작업 [01-overview.md, 01_deepagents_announcement_langchain-blog.md] | 단순히 루프를 돌며 도구를 호출하는 가장 기본적인 형태의 에이전트를 빠르게 만들 때 [01_deepagents_announcement_langchain-blog.md] |
| **Custom LangGraph** | `deepagents` 의 복잡한 내장 기능(파일시스템 등)까진 필요 없지만, **실행 흐름(라우팅) 이나 상태를 세밀하게 제어** 해야 하는 작업 [01-overview.md] | 개발자가 노드와 엣지를 직접 정의하여 커스텀 워크플로 구축 [01-overview.md] |
| **`create_deep_agent`** | 계획 수립, 방대한 컨텍스트 관리, 전문화된 하위 에이전트 위임, 영구 메모리 등이 요구되는 **복잡한 다단계 작업** [01-overview.md] | 장기간 실행되며 파일 시스템과 To-do 리스트를 활용해 목표를 달성하는 범용적인 에이전트 [01_deepagents_announcement_langchain-blog.md, 01-overview.md] |

### 5.2 `deepagents` 사용이 권장되지 않는 케이스

1. **단순한 단일 목적의 작업**: 파일 시스템 오프로딩이나 작업 분할이 필요 없는 간단한 질문 답변·단일 도구 사용 시 → 오버헤드 큼. `create_agent` 또는 커스텀 LangGraph 권장 [01-overview.md].
2. **도구 호출(Tool Calling) 미지원 LLM 사용 시**: `deepagents` 의 모든 아키텍처가 모델의 자율적 도구 호출에 의존하므로 미지원 모델로는 구동 불가 [05_create_deep_agent_api_reference-langchain-com.md].

---

## Q6. Model 바꾸기

> **교안 매핑**: §4.3 Model 바꾸기 — 문자열 vs 객체

### 6.1 기본 모델 + 도구 호출 필수

- **기본 모델**: `claude-sonnet-4-6` [05_create_deep_agent_api_reference-langchain-com.md] (또는 한 단계 이전 식별자 `claude-sonnet-4-5-20250929` [03-customization.md] — 발표 시 최신으로 갱신).
- **도구 호출(Tool Calling) 지원 모델 필수** [02-quickstart.md, 05_create_deep_agent_api_reference-langchain-com.md] — Deep Agent 의 핵심 능력(write_todos, 파일시스템, 하위 에이전트 위임)이 모두 LLM 의 자율적 함수 호출을 통해 작동하기 때문 [05_create_deep_agent_api_reference-langchain-com.md].

### 6.2 방식 1 — `provider:model` 문자열

가장 간편한 방법. `model` 파라미터에 `"openai:gpt-5"` 처럼 **제공자(provider)와 모델명을 결합한 문자열** 을 직접 넘김 [03-customization.md, 05_create_deep_agent_api_reference-langchain-com.md]. 내부적으로 LangChain 의 `init_chat_model` 함수를 사용 [05_create_deep_agent_api_reference-langchain-com.md].

**장점**: 패키지 import·코드 수정 없이 문자열 한 줄 바꾸기로 모델·제공자 간 매우 빠른 전환 [03-customization.md].

```python
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

model = init_chat_model(model="openai:gpt-5")
agent = create_deep_agent(model=model)
```

> 출처: [03-customization.md] 원문

### 6.3 방식 2 — LangChain 모델 객체

이미 구성된 LangChain `BaseChatModel` 인스턴스를 직접 전달 [03-customization.md, 05_create_deep_agent_api_reference-langchain-com.md]. **로컬 환경에서 구동하는 모델** 이나 **OpenAI API 의 데이터 보존(Data Retention) 옵션 등 세밀한 설정** 이 필요할 때 유용 [05_create_deep_agent_api_reference-langchain-com.md].

```python
# ollama pull llama3.1
from langchain_ollama import ChatOllama
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

model = init_chat_model(
    model="llama3.1",
    model_provider="ollama",
    temperature=0,
    # other params...
)

agent = create_deep_agent(model=model)
```

> 출처: [03-customization.md] 원문

### 6.4 두 방식 비교 (결정 가이드)

| 기준 | 문자열 (`provider:model`) | 객체 (`BaseChatModel` 인스턴스) |
|---|---|---|
| 사용 난이도 | 매우 쉬움 (한 줄) | 보통 (객체 구성 단계 필요) |
| 모델 전환 속도 | 매우 빠름 (문자열만 교체) | 객체 재구성 필요 |
| 세밀한 파라미터 (temperature, store, OpenAI Responses API 옵션 등) | 제한적 | **풍부** |
| 로컬 모델 (Ollama 등) | 가능하지만 객체 방식이 자연스러움 | **권장** |
| 권장 시나리오 | 빠른 prototyping, 모델 비교 실험 | 프로덕션, 로컬, 세밀한 제어 |

---

## 부록 A. 인용 ↔ 원본 링크 매핑

본문의 inline `[소스명]` 인용은 모두 다음 표로 추적할 수 있다.

| 인용 표기 | 파일 | 원본 URL |
|---|---|---|
| `[01_deepagents_announcement_langchain-blog.md]` | [research/01_deepagents_announcement_langchain-blog.md](01_deepagents_announcement_langchain-blog.md) | https://blog.langchain.com/deep-agents/ |
| `[02_claude_code_anthropic.md]` | [research/02_claude_code_anthropic.md](02_claude_code_anthropic.md) | https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk → https://claude.com/blog/building-agents-with-the-claude-agent-sdk |
| `[03_deep_research_promptlayer.md]` | [research/03_deep_research_promptlayer.md](03_deep_research_promptlayer.md) | https://blog.promptlayer.com/how-deep-research-works/ |
| `[04_manus_github_gist.md]` | [research/04_manus_github_gist.md](04_manus_github_gist.md) | https://gist.github.com/renschni/4fbc70b31bad8dd57f3370239dccd58f |
| `[05_create_deep_agent_api_reference-langchain-com.md]` | [research/05_create_deep_agent_api_reference-langchain-com.md](05_create_deep_agent_api_reference-langchain-com.md) | https://reference.langchain.com/python/deepagents/graph/create_deep_agent |
| `[06_middleware_architecture_docs-langchain-com.md]` | [research/06_middleware_architecture_docs-langchain-com.md](06_middleware_architecture_docs-langchain-com.md) | https://docs.langchain.com/oss/python/deepagents/middleware (Mintlify `.md` endpoint 로 raw 수집) |
| `[07_default_system_prompt_github.md]` | [research/07_default_system_prompt_github.md](07_default_system_prompt_github.md) | https://raw.githubusercontent.com/langchain-ai/deepagents/main/libs/deepagents/deepagents/graph.py |
| `[01-overview.md]` | [../01-overview.md](../01-overview.md) | https://docs.langchain.com/oss/python/deepagents/overview |
| `[02-quickstart.md]` | [../02-quickstart.md](../02-quickstart.md) | https://docs.langchain.com/oss/python/deepagents/quickstart |
| `[03-customization.md]` | [../03-customization.md](../03-customization.md) | https://docs.langchain.com/oss/python/deepagents/customization |

---

## 부록 B. 사용 정책

- 이 문서는 **NotebookLM 이 자동 합성한 파생 자료** 다. 발표·교안의 1차 근거는 항상 `research/` 의 원본 자료 (또는 영문 원문) 다.
- NotebookLM 출력에 hallucination 가능성이 있으므로 인용 전 항상 원본을 교차 확인한다.
- 한국어 번역·요약 문장을 그대로 복사하지 않고, 원본의 핵심 인용은 **큰따옴표 + footnote** 로 명시한다 (`research/INDEX.md` §6 인용 정책 준수).
- 발표 슬라이드의 코드 블록은 이 문서가 아닌 `scripts/*.py` 의 실제 코드와 sync (Phase 3 verify).

---

> **NotebookLM 노트북**: https://notebooklm.google.com/notebook/12fdc455-bcd2-4579-8722-8b72392b23b7
> **생성일**: 2026-05-04
> **합성 모델**: NotebookLM (chat goal=`learning_guide`, response_length=`longer`)
