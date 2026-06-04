# LangGraph 로 사고하기 — 노드·엣지·State, 그리고 실행

> **핵심 메시지**: LangGraph 는 에이전트를 **노드·엣지·State 의 그래프** 로 모델링하는 런타임이다. 설계는 "업무를 노드로 분해 → State 설계 → 노드 구현 → 연결" 의 사고법으로 하고, `interrupt()`·checkpointer 로 사람 개입과 장애 재개를 1급으로 다룬다.

이 교안은 LangGraph 공식 문서 세 편 — **Thinking in LangGraph**, **Run a local server**, **Changelog** — 을 하나로 합쳐 핵심 주제 다섯 가지로 다시 짠 것이다. 발표 전후로 혼자 읽어도 이해되도록, 슬라이드가 생략하는 맥락을 채우는 데 목적이 있다.

---

## §0. 들머리 — "LangGraph 위에 얹혀 있다" 의 그 LangGraph

> 한 줄 요약: 지난 스터디 내내 "깔개" 로만 불리던 LangGraph 를, 오늘 처음으로 직접 연다.

DeepAgent 4주를 거치며 우리는 같은 문장을 반복해서 들었다 — *"Deep Agent 는 LangGraph 위에 얹혀 있다."* 계획 수립·파일시스템·서브에이전트·장기 메모리라는 4대 능력이 모두 LangGraph 라는 런타임 위에서 돈다는 뜻이었다. 그런데 정작 그 LangGraph 가 무엇인지는 블랙박스로 남겨 두었다.

이 발제는 그 블랙박스를 연다. LangGraph 는 LLM 으로 **상태를 유지하고(stateful) 여러 액터가 참여하는(multi-actor)** 복잡한 애플리케이션을 그래프 구조로 짜는 라이브러리다. 에이전트의 워크플로우를 **노드(node)** 와 **엣지(edge)**, 그리고 공유 **상태(state)** 로 모델링한다. (그 아래에서는 Pregel 계열의 런타임이 돌지만, 내부 실행 모델은 이 발제의 범위 밖이다.)

이 글이 다루는 다섯 주제는 다음과 같다.

**표 1.** 이 교안이 다루는 다섯 핵심 주제

| # | 주제 | 출처 문서 |
|:---:|---|---|
| 1 | 왜 그래프인가 — 사고 모델 | Thinking in LangGraph |
| 2 | 에이전트를 설계하는 5단계 | Thinking in LangGraph |
| 3 | State 설계 & 에러를 흐름의 일부로 | Thinking in LangGraph |
| 4 | 사람 개입과 내구성 | Thinking in LangGraph |
| 5 | 로컬에서 돌려보고, 생태계 근황 | Run a local server · Changelog |

§1\~§4 는 공식 문서가 끝까지 끌고 가는 하나의 예제 — **고객지원 이메일 에이전트** — 를 함께 따라간다. 추상적인 "노드와 엣지" 가 실제로 어떻게 살이 붙는지 한 사례로 관통해 보는 것이다.

---

## §1. 왜 그래프인가 — 노드·엣지·State

> 한 줄 요약: **노드는 작업을 수행하고, 엣지는 다음에 무엇을 할지 알려주며, State 는 모든 노드가 읽고 쓰는 공유 메모리다.**

### 1.1. 한 번의 LLM 호출로는 부족한 순간

간단한 질문 하나라면 LLM 을 한 번 부르면 끝이다. 그러나 현실의 에이전트 업무는 그렇지 않다. 예컨대 "들어온 고객 이메일을 읽고, 긴급도와 주제로 분류하고, 필요하면 문서를 검색해 답을 만들고, 복잡하면 사람에게 넘기고, 후속 일정을 잡아라" 같은 업무는 **여러 단계 · 분기 · 외부 호출 · 사람 개입** 이 얽힌다.

이런 업무를 함수 하나에 if/for 로 몰아넣으면, 중간에 무슨 일이 일어났는지 들여다볼 수 없고, 한 단계가 실패하면 처음부터 다시 해야 하며, "사람의 승인을 기다리는 동안 멈춰 있기" 같은 동작을 표현하기 어렵다.

### 1.2. 세 가지 부품

LangGraph 는 이 복잡함을 세 가지 부품으로 분해한다.

**표 2.** LangGraph 의 세 부품

| 부품 | 역할 | 비유 |
|---|---|---|
| **노드(Node)** | 한 가지 일을 하는 함수. State 를 받아 업데이트를 돌려준다 | 작업대 위의 한 공정 |
| **엣지(Edge)** | 한 노드 다음에 어느 노드로 갈지 | 공정 사이의 컨베이어 |
| **상태(State)** | 모든 노드가 공유하는 메모리. 노드는 여기서 읽고 여기에 쓴다 | 작업 노트 |

**그림 1.** 노드는 작업(state→update)을 하고, 엣지는 다음 노드를 가리키며, State 는 모든 노드가 읽고 쓰는 공유 메모리다.

![노드·엣지·State 세 부품](figs/fig01_three_parts.svg)

> 공식 문서의 표현을 빌리면, **"노드는 작업을 수행하고, 엣지는 다음에 무엇을 할지 알려줍니다."**[^1] 로직(노드)과 제어 흐름(엣지)을 분리하는 것이 LangGraph 의 기본 철학이다.

### 1.3. 그래프로 쪼개면 무엇을 얻나

업무를 여러 노드로 잘게 쪼개는 데는 비용이 따른다 — 코드가 함수 하나보다 길어진다. 그럼에도 그렇게 하는 이유는 세 가지 이득 때문이다.[^1]

- **스트리밍 진행상황**: 노드 경계마다 "지금 어디까지 했다" 를 사용자에게 흘려보낼 수 있다.
- **내구성 있는 일시정지·재개**: 노드 경계에서 상태를 저장해 두므로, 멈췄다가 며칠 뒤에 이어서 실행할 수 있다.
- **단계별 디버깅**: 노드 사이에서 State 를 들여다보며 "분류기가 무엇으로 판단했는지" 를 실행 전에 확인할 수 있다.

### 1.4. 따라갈 예제 — 고객지원 이메일 에이전트

앞으로 §4 까지 함께 따라갈 예제다. 제품팀이 요구한 동작은 이렇다.[^1]

```text
에이전트는 다음을 해야 한다:
- 들어온 고객 이메일을 읽는다
- 긴급도와 주제로 분류한다
- 답을 위해 관련 문서를 검색한다
- 적절한 답변 초안을 작성한다
- 복잡한 이슈는 사람 상담원에게 에스컬레이션한다
- 필요하면 후속 일정을 잡는다

처리해야 할 시나리오:
1. 단순 질문:   "비밀번호를 어떻게 재설정하나요?"
2. 버그 리포트: "PDF 형식으로 내보내기를 선택하면 충돌합니다"
3. 긴급 청구:   "구독료가 두 번 청구됐어요!"
4. 기능 요청:   "모바일 앱에 다크 모드 추가해 주세요"
5. 복잡한 기술 이슈: "API 연동이 간헐적으로 504 오류로 실패합니다"
```

이 업무를 LangGraph 로 옮기는 일은 보통 **다섯 단계** 를 거친다. §2 부터가 그 다섯 단계다.

---

## §2. 에이전트를 설계하는 5단계 (Step 1\~2)

> 한 줄 요약: LangGraph 설계는 **① 분해 → ② 스텝 유형 식별 → ③ State 설계 → ④ 노드 구현 → ⑤ 연결** 의 다섯 단계다. 이 절은 ①·② 를, §3 이 ③·④(에러)를, §4 가 ④(개입)·⑤ 를 다룬다.

다섯 단계를 한눈에:

**표 3.** 에이전트 설계 5단계 개요

| 단계 | 이름 | 하는 일 | 다루는 절 |
|:---:|---|---|:---:|
| 1 | 분해 | 업무를 개별 스텝(노드 후보)으로 쪼갠다 | §2 |
| 2 | 스텝 유형 식별 | 각 노드가 어떤 종류의 작업인지 분류한다 | §2 |
| 3 | State 설계 | 노드 간 공유 메모리의 스키마를 정의한다 | §3 |
| 4 | 노드 구현 | 각 스텝을 함수로 구현(에러·개입 포함) | §3·§4 |
| 5 | 연결 | 노드를 그래프로 잇고 컴파일한다 | §4 |

**그림 2.** 설계 5단계 파이프라인. ①② 는 §2, ③ 은 §3, ④ 는 §3·§4, ⑤ 는 §4 에서 다룬다.

![설계 5단계 파이프라인](figs/fig02_design_5steps.svg)

### 2.1. Step 1 — 워크플로우를 개별 스텝으로 분해

먼저 업무 안의 서로 다른 단계를 식별한다. 각 단계가 하나의 **노드**(한 가지 일만 하는 함수)가 된다. 그런 다음 이 단계들이 어떻게 이어지는지 스케치한다.

**그림 3.** 고객지원 이메일 에이전트 그래프. **실선** 은 늘 같은 다음 노드로 가는 고정 엣지, **보라 점선** 은 노드 내부에서 `Command(goto=...)` 로 결정하는 분기다. (`human_review` 가 두 번 보이는 것은 같은 노드를 두 진입 경로 — 분류 직후 에스컬레이션, 초안 후 검토 — 로 나눠 그린 레이아웃 단순화다.)

![이메일 에이전트 그래프](figs/fig03_email_agent_graph.svg)

화살표는 **가능한 경로** 를 보여줄 뿐, 실제로 어느 길로 갈지의 결정은 각 노드 **안에서** 일어난다(점선이 분기 가능 경로다).

각 노드가 할 일:

**표 4.** 이메일 에이전트의 노드별 역할

| 노드 | 하는 일 |
|---|---|
| `read_email` | 이메일 내용을 추출·파싱 |
| `classify_intent` | LLM 으로 긴급도·주제를 분류하고 다음 행동으로 라우팅 |
| `search_documentation` | 지식 베이스에서 관련 정보 검색 |
| `bug_tracking` | 트래킹 시스템에 이슈 생성/갱신 |
| `draft_response` | 적절한 답변 생성 |
| `human_review` | 사람 상담원에게 승인/처리 에스컬레이션 |
| `send_reply` | 이메일 답변 발송 |

> **유의**: 어떤 노드는 다음 행선지를 **스스로 결정** 하고(`classify_intent`, `draft_response`, `human_review`), 어떤 노드는 늘 같은 다음 노드로 간다(`read_email` → 항상 `classify_intent`). 이 차이가 §4 에서 "엣지는 최소, 라우팅은 노드 안" 으로 이어진다.

### 2.2. Step 2 — 각 스텝이 무엇을 하는지(유형) 식별

분해한 각 노드가 어떤 **종류** 의 작업이고, 제대로 동작하려면 어떤 맥락이 필요한지 정한다. 작업은 대체로 네 유형으로 나뉜다.

**표 5.** 네 가지 스텝 유형

| 유형 | 언제 쓰나 | 예 |
|---|---|---|
| 🧠 **LLM 스텝** | 이해·분석·생성·추론 판단이 필요할 때 | `classify_intent`, `draft_response` |
| 🗄️ **데이터 스텝** | 외부 소스에서 정보를 가져올 때 | `search_documentation`, 고객 이력 조회 |
| ⚡ **액션 스텝** | 외부에 실제 행동을 가할 때 | `send_reply`, `bug_tracking` |
| 👤 **사용자 입력 스텝** | 사람의 개입이 필요할 때 | `human_review` |

**그림 4.** 네 가지 스텝 유형과 이메일 에이전트에서의 예시 노드.

![네 가지 스텝 유형](figs/fig04_step_types.svg)

각 유형마다 고려할 점이 다르다.[^1]

- **LLM 스텝**은 *정적 맥락(프롬프트)* 과 *동적 맥락(State 에서 오는 데이터)*, 그리고 *원하는 출력 형태* 를 구분해 둔다. 예컨대 `classify_intent` 의 정적 맥락은 "분류 카테고리·긴급도 정의·출력 포맷", 동적 맥락은 "이메일 내용·발신자", 출력은 "라우팅을 결정하는 구조화된 분류 결과" 다.
- **데이터 스텝**은 *파라미터·재시도 전략·캐싱* 을 따진다. 문서 검색은 일시적 실패에 지수 백오프 재시도를 걸 만하고, 자주 쓰는 질의는 캐시할 수 있다.
- **액션 스텝**은 *언제 실행할지·재시도 전략* 을 정하되 **캐시하지 않는다** — 매 전송은 고유한 행동이다.
- **사용자 입력 스텝**은 *판단에 필요한 맥락·기대 입력 형식·언제 트리거되는지* 를 정한다.

이렇게 스텝 유형을 먼저 분류해 두면, 같은 "노드" 라도 재시도·캐싱·에러 처리 정책을 유형별로 다르게 가져갈 근거가 생긴다(§3 의 에러 표로 이어진다).

---

## §3. State 설계 & 에러를 흐름의 일부로 (Step 3\~4)

> 한 줄 요약: State 는 **원시 데이터** 만 담고 프롬프트는 노드에서 그때그때 포맷한다. 에러는 종류에 따라 **재시도 / 되돌아오기 / 일시정지 / 띄워보내기** 네 전략으로 나눠 흐름 안에서 다룬다.

### 3.1. Step 3 — State 설계: 무엇을 담을 것인가

State 는 에이전트의 모든 노드가 접근하는 공유 **메모리** 다. 에이전트가 일하며 알게 되고 결정한 것들을 적어 두는 노트라고 보면 된다.

무엇을 담을지는 한 가지 질문으로 판단한다 — **"단계를 넘어 보존되어야 하는가?"**

- ✅ **담는다**: 단계를 넘어 살아남아야 하는 데이터 (나중에 재구성 불가능하거나, 다시 가져오기 비싼 것)
- ⛔ **담지 않는다**: 다른 데이터로부터 **파생** 할 수 있는 것 → 저장하지 말고 필요할 때 계산

이메일 에이전트라면 다음을 추적해야 한다.[^1]

- 원본 이메일과 발신자 정보 (나중에 재구성 불가)
- 분류 결과 (이후 여러 노드가 사용)
- 검색 결과·고객 데이터 (다시 가져오기 비쌈)
- 답변 초안 (검토를 거치는 동안 보존)
- 실행 메타데이터 (디버깅·복구용)

### 3.2. 원칙 — State 는 raw 로, 프롬프트는 온디맨드로

> **핵심 메시지**: State 에는 **포맷된 문자열이 아니라 원시 데이터** 를 저장하라. 프롬프트는 그것이 필요한 노드 안에서 그때 만든다.

이 분리가 주는 이점:[^1]

- 서로 다른 노드가 같은 데이터를 **각자 다르게** 포맷해 쓸 수 있다.
- State 스키마를 건드리지 않고 **프롬프트 템플릿만** 바꿀 수 있다.
- 디버깅이 명확해진다 — 각 노드가 정확히 어떤 데이터를 받았는지 보인다.
- State 가 기존 데이터를 깨뜨리지 않고 진화할 수 있다.

**그림 5.** State 에는 raw 데이터만 두고, 각 노드가 같은 데이터를 자기 프롬프트로 그때그때 다르게 포맷한다.

![State 는 raw, 포맷은 노드에서](figs/fig05_state_raw.svg)

State 스키마는 `TypedDict` 로 정의한다.

```python
from typing import TypedDict, Literal

# 이메일 분류 결과의 구조
class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str

class EmailAgentState(TypedDict):
    # 원본 이메일 데이터
    email_content: str
    sender_email: str
    email_id: str

    # 분류 결과
    classification: EmailClassification | None

    # 원본 검색/API 결과
    search_results: list[str] | None   # 원시 문서 청크 목록
    customer_history: dict | None       # CRM 의 원시 고객 데이터

    # 생성된 콘텐츠
    draft_response: str | None
    messages: list[str] | None
```

State 안에는 프롬프트 템플릿도, 포맷된 문자열도, 지시문도 없다. 분류 출력은 LLM 이 준 그대로 **하나의 딕셔너리** 로 저장된다.

### 3.3. Step 4(1부) — 노드는 함수다, 그리고 에러는 흐름의 일부다

노드는 **State 를 받아 업데이트를 돌려주는 파이썬 함수** 일 뿐이다. 구현에서 가장 중요한 설계 판단은 "에러를 어떻게 다룰 것인가" 다. LangGraph 는 에러를 예외적 사건이 아니라 **흐름의 일부** 로 본다. 에러 종류마다 처리 전략이 다르다.[^1]

**표 6.** 에러 유형별 처리 전략

| 에러 유형 | 누가 고치나 | 전략 | 언제 |
|---|---|---|---|
| 일시적 오류 (네트워크·레이트리밋) | 시스템(자동) | 재시도 정책 | 재시도하면 대개 해결되는 실패 |
| LLM 복구 가능 (도구 실패·파싱 오류) | LLM | State 에 에러 저장 후 되돌아오기 | LLM 이 에러를 보고 접근을 바꿀 수 있을 때 |
| 사용자 수정 가능 (정보 부족) | 사람 | `interrupt()` 로 일시정지 | 진행에 사용자 입력이 필요할 때 |
| 예상치 못한 오류 | 개발자 | 그대로 띄워보내기(bubble up) | 디버깅이 필요한 미지의 문제 |

**그림 6.** 에러 유형별 네 가지 처리 전략 — "누가 고치느냐" 로 갈린다.

![네 가지 에러 처리 전략](figs/fig06_error_strategies.svg)

**① 일시적 오류 — 재시도 정책**

```python
from langgraph.types import RetryPolicy

workflow.add_node(
    "search_documentation",
    search_documentation,
    retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0)
)
```

**② LLM 복구 가능 — State 에 에러 저장 후 되돌아오기**

```python
from langgraph.types import Command

def execute_tool(state: State) -> Command[Literal["agent", "execute_tool"]]:
    try:
        result = run_tool(state['tool_call'])
        return Command(update={"tool_result": result}, goto="agent")
    except ToolError as e:
        # LLM 이 무엇이 잘못됐는지 보고 다시 시도하도록
        return Command(
            update={"tool_result": f"Tool error: {str(e)}"},
            goto="agent"
        )
```

여기서 핵심 전제는, 되돌아간 `agent` 노드가 이 에러 문자열을 **실제 프롬프트·메시지 맥락으로 읽어** 다시 계획한다는 것이다 — State 에 저장만 한다고 자동으로 회복되지는 않는다. 필드명을 `tool_result` 대신 `tool_error` 처럼 에러임이 드러나게 두면 더 명확하다.

**③ 사용자 수정 가능 — `interrupt()` 로 멈추고 입력 받기**

```python
from langgraph.types import Command, interrupt

def lookup_customer_history(state: State) -> Command[Literal["draft_response"]]:
    if not state.get('customer_id'):
        user_input = interrupt({
            "message": "고객 ID 필요",
            "request": "구독 이력을 조회할 고객 계정 ID 를 입력해 주세요"
        })
        return Command(
            update={"customer_id": user_input['customer_id']},
            goto="lookup_customer_history"
        )
    customer_data = fetch_customer_history(state['customer_id'])
    return Command(update={"customer_history": customer_data}, goto="draft_response")
```

**④ 예상치 못한 오류 — 그대로 띄워보내기**

```python
def send_reply(state: EmailAgentState):
    try:
        email_service.send(state["draft_response"])
    except Exception:
        raise  # 다룰 수 없는 건 표면화시켜 디버깅
```

핵심은 "모든 에러를 try/except 로 삼키지 않는다" 는 것이다. 어떤 에러는 자동 재시도가, 어떤 에러는 LLM 에게 되먹임이, 어떤 에러는 사람의 입력이, 어떤 에러는 그냥 터지게 두는 것이 맞다.

### 3.4. 노드 구현 예 — 읽기·분류·검색

스텝 유형(§2.2)과 에러 전략(§3.3)을 적용한 노드들이다. 라우팅이 노드 **안에서** `Command(goto=...)` 로 결정되는 점에 주목하라.

> **이 절 이하의 코드는 핵심 패턴만 보이는 축약본이다.** `search_documentation`·`bug_tracking`·`draft_response`·`send_reply` 의 본문과 일부 타입 처리는 생략했다 — 그대로 복사하면 바로 돌지 않는다(예: 기본 `TypedDict` 는 모든 키가 required 라, `initial_state` 에 전부 채우거나 `total=False`/`NotRequired` 가 필요하다). 실행 가능한 전체본은 후속 `scripts/` 에 둔다.

```python
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command, RetryPolicy
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage

llm = ChatOpenAI(model="gpt-5-nano")

def read_email(state: EmailAgentState) -> dict:
    """이메일 내용 추출·파싱"""
    return {
        "messages": [HumanMessage(content=f"Processing email: {state['email_content']}")]
    }

def classify_intent(
    state: EmailAgentState
) -> Command[Literal["search_documentation", "human_review", "draft_response", "bug_tracking"]]:
    """LLM 으로 의도·긴급도를 분류하고 그에 맞게 라우팅"""

    # EmailClassification 딕셔너리를 돌려주는 구조화 LLM
    structured_llm = llm.with_structured_output(EmailClassification)

    # 프롬프트는 State 에 저장하지 않고 여기서 그때 포맷
    classification_prompt = f"""
    이 고객 이메일을 분석해 분류하라:

    Email: {state['email_content']}
    From: {state['sender_email']}

    intent, urgency, topic, summary 를 포함해 분류하라.
    """

    classification = structured_llm.invoke(classification_prompt)

    # 분류에 따라 다음 노드 결정
    if classification['intent'] == 'billing' or classification['urgency'] == 'critical':
        goto = "human_review"
    elif classification['intent'] in ['question', 'feature']:
        goto = "search_documentation"
    elif classification['intent'] == 'bug':
        goto = "bug_tracking"
    else:
        goto = "draft_response"

    # 분류 결과를 단일 딕셔너리로 State 에 저장
    return Command(update={"classification": classification}, goto=goto)
```

---

## §4. 사람 개입과 내구성 (Step 4\~5)

> 한 줄 요약: `interrupt()` 가 워크플로우를 멈춰 모든 State 를 저장하고, `Command(resume=...)` 가 멈춘 지점부터 재개한다. 이를 가능케 하는 것이 **checkpointer** 이고, 노드를 작게 쪼갤수록 재개 비용이 줄어든다.

### 4.1. Step 4(2부) — `interrupt()` 로 사람을 1급으로

> **핵심 메시지**: LangGraph 에서 **사람의 입력은 1급 시민(first-class)** 이다.

`human_review` 노드는 답변 초안을 사람에게 보여 주고 승인/수정을 받는다. 핵심은 `interrupt()` 를 가능한 한 노드 앞쪽에, **특히 비멱등(non-idempotent) side effect — 외부 API 호출·DB 쓰기·이메일 발송 — 보다 먼저** 두는 것이다. 재개 시 `interrupt()` 이전의 순수 계산·State 읽기는 다시 실행되므로(아래에서 `classification` 을 읽는 것처럼 부작용 없는 코드는 무방하다), 부작용이 있는 호출을 그 앞에 두면 중복 실행된다.

```python
def human_review(state: EmailAgentState) -> Command[Literal["send_reply", END]]:
    """interrupt 로 일시정지하고, 사람의 결정에 따라 라우팅"""

    classification = state.get('classification') or {}  # None 일 수 있으므로 or {}

    # 재개 시 이 앞의 코드는 다시 실행된다 → 부작용 있는 호출을 앞에 두지 말 것
    human_decision = interrupt({
        "email_id": state.get('email_id', ''),
        "original_email": state.get('email_content', ''),
        "draft_response": state.get('draft_response', ''),
        "urgency": classification.get('urgency'),
        "intent": classification.get('intent'),
        "action": "이 답변을 검토하고 승인/수정해 주세요"
    })

    # 사람의 결정을 처리
    if human_decision.get("approved"):
        return Command(
            update={"draft_response": human_decision.get("edited_response", state.get('draft_response', ''))},
            goto="send_reply"
        )
    else:
        # 거절 = 사람이 직접 처리
        return Command(update={}, goto=END)
```

### 4.2. Step 5 — 노드를 그래프로 연결하고 컴파일

노드들이 스스로 라우팅을 결정하므로(`Command(goto=...)`), 필요한 엣지는 몇 개뿐이다. `interrupt()` 로 사람 개입을 쓰려면 상태를 저장할 **checkpointer** 와 함께 컴파일해야 한다.

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy

workflow = StateGraph(EmailAgentState)

# 노드 등록
workflow.add_node("read_email", read_email)
workflow.add_node("classify_intent", classify_intent)

# 일시적 실패가 잦은 노드에는 재시도 정책
workflow.add_node(
    "search_documentation",
    search_documentation,
    retry_policy=RetryPolicy(max_attempts=3)
)
workflow.add_node("bug_tracking", bug_tracking)
workflow.add_node("draft_response", draft_response)
workflow.add_node("human_review", human_review)
workflow.add_node("send_reply", send_reply)

# 꼭 필요한 엣지만
workflow.add_edge(START, "read_email")
workflow.add_edge("read_email", "classify_intent")
workflow.add_edge("send_reply", END)

# 영속성을 위해 checkpointer 와 함께 컴파일
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
```

> **유의 — `MemorySaver` 는 인메모리(개발·데모)용이다.** 위 코드는 한 프로세스 안에서 interrupt/resume 흐름을 보여 주기 위한 것이다. 프로세스를 재시작해도 살아남는 "며칠 뒤 재개" 를 보장하려면 Postgres 같은 durable checkpointer(또는 LangSmith Deployment 계열의 영속 저장소)가 필요하다.

그래프 구조가 이토록 작은 이유는 라우팅이 노드 안의 `Command` 로 일어나기 때문이다. 각 노드는 `Command[Literal["node1", "node2"]]` 타입 힌트로 자기가 갈 수 있는 곳을 선언하므로, 흐름이 명시적이고 추적 가능하다. (LangGraph 에는 이 방식 외에 `add_conditional_edges` 같은 조건부 엣지 라우팅도 있으나, 이 교안의 이메일 예제는 `Command(goto=...)` 를 택했다 — 조건부 엣지는 이번 범위 밖이다.)

### 4.3. 멈췄다가 며칠 뒤에 이어서 — 실행과 재개

```python
# 사람 검토가 필요한 긴급 청구 이슈로 테스트
initial_state = {
    "email_content": "구독료가 두 번 청구됐어요! 급해요!",
    "sender_email": "customer@example.com",
    "email_id": "email_123",
    "messages": []
}

# 영속성을 위해 thread_id 와 함께 실행
config = {"configurable": {"thread_id": "customer_123"}}
result = app.invoke(initial_state, config)
# 그래프는 human_review 에서 멈춘다
print(f"human review interrupt:{result['__interrupt__']}")

# 준비되면 사람의 입력으로 재개
from langgraph.types import Command

human_response = Command(
    resume={
        "approved": True,
        "edited_response": "이중 청구 건 진심으로 사과드립니다. 즉시 환불을 진행했습니다..."
    }
)

# 재개
final_result = app.invoke(human_response, config)
print("이메일 전송 완료!")
```

그래프는 `interrupt()` 를 만나면 모든 것을 checkpointer 에 저장하고 **기다린다.** 같은 checkpointer 백엔드에 체크포인트가 남아 있고 같은 `thread_id` 로 다시 호출하면, 멈췄던 지점부터 이어진다. 여기서 `thread_id` 는 저장소 자체가 아니라 **체크포인트를 식별·조회하는 키** 이고, State 가 실제로 보존되는 곳은 checkpointer 다(이 예제에선 인메모리 `MemorySaver`).

**그림 7.** `interrupt()` 가 checkpointer 에 State 를 저장하고 멈춘다. 며칠 뒤라도 외부 호출자가 같은 `thread_id` 로 `Command(resume=...)` 를 호출하면, 런타임이 저장된 체크포인트를 조회해 멈춘 지점부터 재개한다.

![interrupt → checkpointer → resume](figs/fig07_interrupt_resume.svg)

### 4.4. 노드를 얼마나 잘게 쪼갤까 — granularity 트레이드오프

"`read_email` 과 `classify_intent` 를 한 노드로 합치면 안 되나?" 라는 질문에 대한 답은 **회복력 vs 관찰가능성** 의 트레이드오프다.[^1]

**그림 8.** 노드를 작게 쪼갤수록 실패 시 재실행 범위가 줄어든다. 큰 노드는 끝에서 실패해도 처음부터 전부 다시 한다.

![노드 granularity 와 재실행 범위](figs/fig08_node_granularity.svg)

- **회복력**: LangGraph 의 **내구성 있는 실행(durable execution)** 은 노드/슈퍼스텝 경계에서 체크포인트를 만든다. 중단 후 재개하면 멈춘 노드의 **처음부터** 다시 실행된다. 노드가 작을수록 재실행 비용이 작다. 여러 작업을 한 큰 노드에 몰면, 끝부분에서 실패해도 노드 처음부터 전부 다시 한다.
- **관찰가능성**: `classify_intent` 를 독립 노드로 두면, 행동 전에 LLM 이 무엇으로 판단했는지 들여다볼 수 있다.
- **서로 다른 실패 양상**: LLM 호출·DB 조회·이메일 발송은 재시도 전략이 제각각이다. 노드를 나누면 정책을 독립적으로 줄 수 있다.

> **성능 오해 주의**: 노드가 많다고 느려지지 않는다. LangGraph 는 기본적으로 체크포인트를 **백그라운드(async durability 모드)** 로 쓰므로, 그래프는 체크포인트 완료를 기다리지 않고 계속 실행된다. 필요하면 `"exit"` 모드(완료 시에만 체크포인트)나 `"sync"` 모드(매 체크포인트마다 블록)로 바꿀 수 있다.

### 4.5. 정리 — LangGraph 식 사고 6가지

| | |
|:---|:---|
| 📦 **개별 스텝으로 분해** — 노드 하나가 한 가지를 잘함. 스트리밍·재개·디버깅이 여기서 나온다 | 💾 **State 는 공유 메모리** — 포맷된 문자열이 아닌 raw 데이터를 저장 |
| ⚙️ **노드는 함수** — State 를 받아 업데이트를 돌려준다. 라우팅이 필요하면 다음 행선지까지 함께 지정 | ⚠️ **에러는 흐름의 일부** — 재시도·되돌아오기·일시정지·띄워보내기 |
| 👤 **사람 입력은 1급** — `interrupt()` 가 무한정 멈추고 State 를 저장, 입력이 오면 정확히 그 자리에서 재개 | 🔗 **그래프 구조는 자연히 생긴다** — 꼭 필요한 연결만 정의하고 라우팅은 노드가 한다 |

---

## §5. 로컬에서 돌려보고, 생태계 근황

> 한 줄 요약: `langgraph dev` 한 줄로 인메모리 서버를 띄워 Studio·SDK·REST 로 테스트한다(개발용). 그리고 LangChain/LangGraph 생태계는 v1 정식 이후 빠르게 움직인다 — 발표 시점의 changelog 를 한 번 확인하라.

### 5.1. §1\~§4 에서 만든 그래프를, 이제 실제로 띄운다

`app = workflow.compile(...)` 까지 했다면, 이걸 로컬 서버로 올려 Studio 로 디버깅할 수 있다. 공식 **Run a local server** 가이드의 흐름은 일곱 단계다.[^2]

> 한 가지 연결고리: `langgraph dev` 는 코드 안의 `app` 변수를 자동으로 찾아 띄우는 게 아니라, 프로젝트의 `langgraph.json` 에 등록된 **그래프 경로와 assistant 이름** 을 보고 서버를 올린다(템플릿이 이 파일을 만들어 준다). 아래 SDK/REST 예의 `"agent"` 가 바로 그 assistant 이름이다. §1\~§4 의 그래프를 직접 서빙하려면 `app` 이 있는 모듈 경로를 `langgraph.json` 에 등록하면 된다.

**그림 9.** `langgraph dev` 는 `langgraph.json` 에 등록된 그래프를 인메모리 서버(:2024)로 띄우고, Studio·SDK·REST 가 거기에 붙는다.

![langgraph dev 로컬 토폴로지](figs/fig09_local_topology.svg)

**① LangGraph CLI 설치** (Python ≥ 3.11)

```bash
pip install -U "langgraph-cli[inmem]"
```

**② 앱 생성** — 템플릿에서 단일 노드 앱을 만들어 확장한다

```bash
langgraph new path/to/your/app --template new-langgraph-project-python
```

> 템플릿을 지정하지 않고 `langgraph new` 만 치면 사용 가능한 템플릿 메뉴가 뜬다.

**③ 의존성 설치** (edit 모드 — 로컬 변경이 서버에 바로 반영)

```bash
pip install -e .
```

**④ `.env` 작성** — `.env.example` 을 복사해 키를 채운다

```text
LANGSMITH_API_KEY=lsv2...
```

**⑤ 서버 실행**

```bash
langgraph dev
```

출력 예:

```text
   Welcome to
   ╦  ┌─┐┌┐┌┌─┐╔═╗┬─┐┌─┐┌─┐┬ ┬
   ║  ├─┤││││ ┬║ ╦├┬┘├─┤├─┘├─┤
   ╩═╝┴ ┴┘└┘└─┘╚═╝┴└─┴ ┴┴  ┴ ┴

 - 🚀 API:       http://127.0.0.1:2024
 - 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
 - 📚 API Docs:  http://127.0.0.1:2024/docs
```

> **중요**: `langgraph dev` 는 **인메모리 모드** 다. 개발·테스트용이며, 운영에서는 영속 저장소를 갖춘 **LangSmith Deployment** 로 배포해야 한다.

**⑥ Studio 로 디버깅** — 출력의 Studio URL 로 접속해 그래프를 시각화하고, 단계별로 실행하며, 특정 단계의 입력을 수정해 즉시 반응을 본다. (Safari 는 완전 호환되지 않음 → Chrome·Brave 등 Chromium 계열 권장)

**⑦ API 테스트** — Python SDK(async/sync) 또는 REST 로 호출

```python
# async SDK
from langgraph_sdk import get_client
import asyncio

client = get_client(url="http://localhost:2024")

async def main():
    async for chunk in client.runs.stream(
        None,            # 스레드 없는 실행
        "agent",         # langgraph.json 에 정의된 assistant 이름
        input={"messages": [{"role": "human", "content": "What is LangGraph?"}]},
    ):
        print(f"Receiving new event of type: {chunk.event}...")
        print(chunk.data)

asyncio.run(main())
```

```bash
# REST
curl -s --request POST \
    --url "http://localhost:2024/runs/stream" \
    --header 'Content-Type: application/json' \
    --data '{
        "assistant_id": "agent",
        "input": {"messages": [{"role": "human", "content": "What is LangGraph?"}]},
        "stream_mode": "messages-tuple"
    }'
```

여기서 우리가 §1\~§4 에 만든 노드·엣지·State·checkpointer 가, `langgraph dev` 라는 한 줄과 Studio 라는 눈으로 실제 손에 잡힌다.

### 5.2. 생태계 근황 — Changelog 가 말해 주는 것

LangChain/LangGraph 의 changelog 는 **얼마나 빠르게 움직이는지** 를 보여 준다. 이론 발제에서 중요한 건 개별 릴리스 암기가 아니라 "이 생태계는 분기마다 바뀐다" 는 감각이다. 아래 표는 **원문 05 (2025-12-15 시점) 기준 발췌** 이고, 발표 시점에는 그 이후 추가된 릴리스가 더 있으니 [공식 changelog](https://docs.langchain.com/oss/python/releases/changelog) 를 한 번 확인하라. 주요 흐름은 다음과 같다.[^3]

**표 7.** 원문 05 기준 주요 릴리스

| 시점 | 릴리스 | 핵심 |
|---|---|---|
| 2025-10-20 | **`langchain` · `langgraph` v1.0.0** | 두 패키지의 **1.0 정식**. 릴리스 노트·마이그레이션 가이드 제공 |
| 2025-11-25 | `langchain` v1.1.0 | **Model profiles**(`.profile` 로 모델 능력 노출), summarization·model retry·content moderation **미들웨어**, structured output `ProviderStrategy` |
| 2025-12-08 | `langchain-google-genai` v4.0.0 | Google 통합 GenAI SDK 로 재작성 (Gemini API + Vertex AI 동일 인터페이스) |
| 2025-12-15 | `langchain` v1.2.0 | `create_agent` 의 도구 `extras` 속성(provider별 설정·클라이언트 실행 도구), `response_format` strict 스키마 |

> changelog 에는 **RSS 피드** 가 있어 Slack·이메일·Discord 봇 등에 연동할 수 있다. 빠르게 바뀌는 생태계를 따라가는 가장 싼 방법이다.

특히 **미들웨어** 흐름(요약·재시도·콘텐츠 검열)은 우리가 DeepAgent 에서 본 "내장 능력을 미들웨어로 얹는다" 는 패턴과 같은 줄기다. 큰 방향으로는 — LangGraph 의 노드·State 모델 위에 LangChain 이 이런 미들웨어를 쌓고, 그 위에 deepagents 가 4대 능력을 얹었다고 — 이해할 수 있다(이는 changelog 가 명시하는 사실이라기보다 계층 구조에 대한 해석이다).

---

## §6. 다음으로 가는 다리, 그리고 한 문장

> 한 줄 요약: 오늘은 LangGraph 의 **사고법**(노드·엣지·State)과 **실행**(`langgraph dev`)을 봤다. 다음은 이 사고법을 떠받치는 메커니즘의 깊이다.

오늘 그린 것은 **지도** 다. 여기서 더 들어갈 길들:

- **Graph API 깊이** — `add_conditional_edges`, 리듀서(`add_messages`), 병렬 분기 등 노드/엣지의 본격 문법
- **Persistence · Memory** — checkpointer 의 실제 백엔드(Postgres·Redis), 스레드 간 장기 메모리(Store)와 시맨틱 검색
- **Streaming** — `values`/`updates`/`messages`/`custom` 스트림 모드로 실시간 진행 노출
- **Subgraphs** — 복잡한 다단계 작업을 하위 그래프로 캡슐화
- **Time Travel** — 과거 체크포인트로 돌아가 분기(fork) 실행

마지막으로, 발표가 끝났을 때 청중이 한 문장으로 답할 수 있어야 할 것:

> **LangGraph 는 에이전트를 노드·엣지·State 의 그래프로 모델링하는 런타임이다. 업무를 노드로 분해하고, raw State 로 잇고, 에러와 사람 개입을 흐름 안에서 다루며, `langgraph dev` 로 띄워 Studio 로 디버깅한다.**

---

## 부록 A. 용어집

**표 8.** 용어집

| 용어 | 뜻 |
|---|---|
| **노드(Node)** | State 를 받아 업데이트를 돌려주는 함수. 한 가지 일을 한다 |
| **엣지(Edge)** | 한 노드 다음에 어느 노드로 갈지. `add_edge` 또는 노드 안의 `Command(goto=...)` |
| **상태(State)** | 모든 노드가 공유하는 메모리. 보통 `TypedDict` 로 스키마 정의 |
| **`StateGraph`** | 노드·엣지·State 로 그래프를 조립하는 빌더 |
| **`Command`** | 노드의 반환값. State 업데이트(`update`)와 다음 행선지(`goto`), 재개(`resume`)를 함께 표현 |
| **`interrupt()`** | 노드를 일시정지하고 State 를 저장한 뒤 외부 입력을 기다림. 재개 시 앞 코드가 재실행되므로 비멱등 side effect 보다 앞에 둠 |
| **checkpointer** | 노드/슈퍼스텝 경계의 State 스냅샷을 저장하는 레이어. `MemorySaver` 는 인메모리(개발·데모)용, 프로세스 재시작 후 장기 재개는 Postgres 등 durable 백엔드 필요 |
| **`thread_id`** | 한 실행 세션의 식별자. 체크포인트가 State 를 묶는 기준 |
| **`RetryPolicy`** | 노드 단위 재시도 정책 (일시적 오류용) |
| **내구성 있는 실행(Durable Execution)** | 노드/슈퍼스텝 경계 체크포인트로 중단 후 그 자리에서 재개 (장기 재개는 durable checkpointer 전제) |
| **`langgraph dev`** | 로컬 인메모리 API 서버(포트 2024). 개발·테스트용 |
| **Studio** | 로컬 서버에 붙어 그래프를 시각화·디버깅하는 UI |

## 부록 B. 참고 — 원문 04\~06 매핑

**표 9.** 원문 04\~06 매핑

| 절 | 원문 |
|---|---|
| §1\~§4 | 06 Thinking in LangGraph |
| §5.1 | 04 Run a local server |
| §5.2 | 05 Changelog |

[^1]: LangGraph Docs — *Thinking in LangGraph* (노드·엣지·State 모델, 설계 5단계, State raw 원칙, 4가지 에러 전략, `interrupt()`/checkpointer, 노드 granularity). 본 교안 §1\~§4 의 1차 출처.
[^2]: LangGraph Docs — *Run a local server* (`langgraph-cli` 설치, `langgraph new`, `langgraph dev` 인메모리 서버, Studio, Python SDK/REST 테스트). 본 교안 §5.1 의 1차 출처.
[^3]: LangChain Docs — *Changelog* (`langchain`/`langgraph` v1.0.0 정식, v1.1.0 미들웨어·model profiles, `langchain-google-genai` v4.0.0, v1.2.0 `create_agent` extras, RSS 피드). 본 교안 §5.2 의 1차 출처.
