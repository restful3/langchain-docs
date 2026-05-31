## §3. State 설계 & 에러를 흐름의 일부로 (Step 3\~4)

<div class="section-summary">
  <div class="section-summary__kicker">한 줄 요약</div>
  <div class="section-summary__body">State 는 <strong>원시 데이터</strong> 만 담고 프롬프트는 노드에서 그때그때 포맷한다. 에러는 종류에 따라 <strong>재시도 / 되돌아오기 / 일시정지 / 띄워보내기</strong> 네 전략으로 나눠 흐름 안에서 다룬다.</div>
</div>

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

![State 는 raw, 포맷은 노드에서](figs/fig05_state_raw.svg)
<small>Figure — State 에는 raw 데이터만 두고, 각 노드가 같은 데이터를 자기 프롬프트로 그때그때 다르게 포맷한다.</small>

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

**표 6. 에러 유형별 처리 전략**

| 에러 유형 | 누가 고치나 | 전략 | 언제 |
|---|---|---|---|
| 일시적 오류 (네트워크·레이트리밋) | 시스템(자동) | 재시도 정책 | 재시도하면 대개 해결되는 실패 |
| LLM 복구 가능 (도구 실패·파싱 오류) | LLM | State 에 에러 저장 후 되돌아오기 | LLM 이 에러를 보고 접근을 바꿀 수 있을 때 |
| 사용자 수정 가능 (정보 부족) | 사람 | `interrupt()` 로 일시정지 | 진행에 사용자 입력이 필요할 때 |
| 예상치 못한 오류 | 개발자 | 그대로 띄워보내기(bubble up) | 디버깅이 필요한 미지의 문제 |

![네 가지 에러 처리 전략](figs/fig06_error_strategies.svg)
<small>Figure — 에러 유형별 네 가지 처리 전략 — "누가 고치느냐" 로 갈린다.</small>

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
