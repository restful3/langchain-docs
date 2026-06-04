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

트레이딩 에이전트라면 다음을 추적해야 한다.[^1]

- 원본 가격 윈도우와 종목·시점 정보 (나중에 재구성 불가)
- 신호 결과 (이후 여러 노드가 사용)
- 리스크 점검 결과 (다시 계산하기 비쌈)
- 주문 후보 (승인을 거치는 동안 보존)
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

# 평균회귀 신호 결과의 구조
class SignalDecision(TypedDict):
    direction: Literal["long", "short", "flat", "uncertain"]
    conviction: Literal["low", "medium", "high", "critical"]  # critical = '사람 검토 필요'
    instrument: str
    rationale: str

class TradingAgentState(TypedDict):
    # 원본 시장 데이터
    instrument: str
    price_window: list[float]           # 원시 종가(또는 스프레드) 윈도우
    market_data_timestamp: str
    headline: str | None                # LLM 의 동적 맥락 (옵션)

    # 신호 결과
    signal: SignalDecision | None

    # 원본 리스크/계좌 조회 결과
    risk_report: dict | None            # 변동성·노출·허용 한도

    # 생성된 주문
    order: dict | None
    approval_required: bool             # 큰 신호/리스크 초과 → 사람 검토 표시
```

State 안에는 프롬프트 템플릿도, 포맷된 문자열도, 지시문도 없다. 신호 결과는 **하나의 딕셔너리** 로 저장된다 — 방향은 결정론적 z-score 가, 근거(rationale)는 LLM 이 채운다.

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
    "fetch_market_data",
    fetch_market_data,
    retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0)
)
```

**② LLM 복구 가능 — State 에 에러 저장 후 되돌아오기**

```python
from langgraph.types import Command

def run_indicator(state: State) -> Command[Literal["agent", "run_indicator"]]:
    try:
        result = compute_indicator(state['indicator_call'])
        return Command(update={"indicator_result": result}, goto="agent")
    except IndicatorError as e:
        # LLM 이 무엇이 잘못됐는지 보고 파라미터를 바꾸도록
        return Command(
            update={"indicator_result": f"Indicator error: {str(e)}"},
            goto="agent"
        )
```

여기서 핵심 전제는, 되돌아간 `agent` 노드가 이 에러 문자열을 **실제 프롬프트·메시지 맥락으로 읽어** 다시 계획한다는 것이다 — State 에 저장만 한다고 자동으로 회복되지는 않는다. 필드명을 `indicator_result` 대신 `indicator_error` 처럼 에러임이 드러나게 두면 더 명확하다. (이 도구 루프 패턴은 트레이딩 주 경로엔 없고 `scripts/steps/04_errors.py` 에서 따로 시연한다.)

**③ 사용자 수정 가능 — `interrupt()` 로 멈추고 입력 받기**

```python
from langgraph.types import Command, interrupt

def lookup_account(state: State) -> Command[Literal["size_position"]]:
    if not state.get('account_id'):
        user_input = interrupt({
            "message": "계좌 ID 필요",
            "request": "주문에 쓸 계좌(매수여력 조회용) ID 를 입력해 주세요"
        })
        return Command(
            update={"account_id": user_input['account_id']},
            goto="lookup_account"
        )
    account_data = fetch_account(state['account_id'])
    return Command(update={"account_data": account_data}, goto="size_position")
```

**④ 예상치 못한 오류 — 그대로 띄워보내기**

```python
def place_order(state: TradingAgentState):
    try:
        broker.place(state["order"])
    except Exception:
        raise  # 다룰 수 없는 건 표면화시켜 디버깅
```

핵심은 "모든 에러를 try/except 로 삼키지 않는다" 는 것이다. 어떤 에러는 자동 재시도가, 어떤 에러는 LLM 에게 되먹임이, 어떤 에러는 사람의 입력이, 어떤 에러는 그냥 터지게 두는 것이 맞다.

### 3.4. 노드 구현 예 — 시세 수신·신호 생성

스텝 유형(§2.2)과 에러 전략(§3.3)을 적용한 노드들이다. 라우팅이 노드 **안에서** `Command(goto=...)` 로 결정되는 점에 주목하라.

> **이 절 이하의 코드는 핵심 패턴만 보이는 축약본이다.** `check_risk`·`size_position`·`flag_anomaly`·`place_order` 의 본문과 일부 타입 처리(rationale 생성·데이터 이상 분기 등)는 생략했다 — 그대로 복사하면 바로 돌지 않는다(예: 기본 `TypedDict` 는 모든 키가 required 라, `initial_state` 에 전부 채우거나 `total=False`/`NotRequired` 가 필요하다). 실행 가능한 전체본은 후속 `scripts/` 에 둔다.

```python
import statistics
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command, RetryPolicy
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-5-nano")

def fetch_market_data(state: TradingAgentState) -> dict:
    """최근 종가 윈도우 수신 (RetryPolicy 대상 — §3.3①)"""
    return {"log": [f"fetched {state['instrument']}: {len(state['price_window'])} bars"]}

def generate_signal(
    state: TradingAgentState
) -> Command[Literal["check_risk", "flag_anomaly", END]]:
    """z-score 로 방향·확신을 정하고 그에 맞게 라우팅"""

    # 방향은 결정론적 z-score 가 정한다 — LLM 은 근거(rationale)만 맡는다
    w = state["price_window"]
    z = (w[-1] - statistics.fmean(w)) / statistics.pstdev(w)
    direction = "long" if z <= -1.0 else "short" if z >= 1.0 else "flat"
    conviction = "critical" if abs(z) >= 2.5 else "high" if abs(z) >= 1.5 else "medium"

    # 신호에 따라 다음 노드 결정
    if direction == "flat":
        goto = END                      # 진입 신호 없음 → 무거래
    else:
        goto = "check_risk"

    signal = {"direction": direction, "conviction": conviction,
              "instrument": state["instrument"], "rationale": f"z={z:.2f}"}

    # critical(비정상적으로 강한 신호)이면 '사람 검토 필요' 플래그만 — 직행하지 않는다
    return Command(
        update={"signal": signal, "approval_required": conviction == "critical"},
        goto=goto,
    )
```
