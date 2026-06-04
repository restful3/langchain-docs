## §4. 사람 개입과 내구성 (Step 4\~5)

<div class="section-summary">
  <div class="section-summary__kicker">한 줄 요약</div>
  <div class="section-summary__body"><code>interrupt()</code> 가 워크플로우를 멈춰 모든 State 를 저장하고, <code>Command(resume=...)</code> 가 멈춘 지점부터 재개한다. 이를 가능케 하는 것이 <strong>checkpointer</strong> 이고, 노드를 작게 쪼갤수록 재개 비용이 줄어든다.</div>
</div>

### 4.1. Step 4(2부) — `interrupt()` 로 사람을 1급으로

> **핵심 메시지**: LangGraph 에서 **사람의 입력은 1급 시민(first-class)** 이다.

`approve_order` 노드는 주문 후보를 사람에게 보여 주고 승인/수정을 받는다. 핵심은 `interrupt()` 를 가능한 한 노드 앞쪽에, **특히 비멱등(non-idempotent) side effect — 외부 API 호출·DB 쓰기·브로커 주문 전송 — 보다 먼저** 두는 것이다. 재개 시 `interrupt()` 이전의 순수 계산·State 읽기는 다시 실행되므로(아래에서 `order`·`signal` 을 읽는 것처럼 부작용 없는 코드는 무방하다), 부작용이 있는 호출을 그 앞에 두면 중복 실행된다.

```python
def approve_order(state: TradingAgentState) -> Command[Literal["place_order", END]]:
    """interrupt 로 일시정지하고, 사람의 결정에 따라 라우팅"""

    order = state.get('order')          # 리스크 차단 에스컬레이션이면 None 일 수 있다
    signal = state.get('signal') or {}

    # 재개 시 이 앞의 코드는 다시 실행된다 → 부작용(브로커 호출) 있는 코드를 앞에 두지 말 것
    human_decision = interrupt({
        "instrument": state.get('instrument', ''),
        "order": order,
        "conviction": signal.get('conviction'),
        "approval_required": state.get('approval_required', False),
        "action": "이 주문을 승인/거부/수정해 주세요"
    })

    # 사람의 결정을 처리
    if human_decision.get("approved") and order is not None:
        return Command(
            update={"order": {**order, "qty": human_decision.get("edited_qty", order["qty"])}},
            goto="place_order"
        )
    else:
        # 거부 = 사람이 직접 처리
        return Command(update={}, goto=END)
```

### 4.2. Step 5 — 노드를 그래프로 연결하고 컴파일

노드들이 스스로 라우팅을 결정하므로(`Command(goto=...)`), 필요한 엣지는 몇 개뿐이다. `interrupt()` 로 사람 개입을 쓰려면 상태를 저장할 **checkpointer** 와 함께 컴파일해야 한다.

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy

workflow = StateGraph(TradingAgentState)

# 노드 등록 — 일시적 실패가 잦은 시세 호출에 재시도 정책
workflow.add_node(
    "fetch_market_data",
    fetch_market_data,
    retry_policy=RetryPolicy(max_attempts=3)
)
workflow.add_node("generate_signal", generate_signal)
workflow.add_node("check_risk", check_risk)
workflow.add_node("size_position", size_position)
workflow.add_node("approve_order", approve_order)
workflow.add_node("place_order", place_order)
workflow.add_node("flag_anomaly", flag_anomaly)

# 꼭 필요한 엣지만
workflow.add_edge(START, "fetch_market_data")
workflow.add_edge("fetch_market_data", "generate_signal")
workflow.add_edge("place_order", END)

# 영속성을 위해 checkpointer 와 함께 컴파일
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
```

> **유의 — `MemorySaver` 는 인메모리(개발·데모)용이다.** 위 코드는 한 프로세스 안에서 interrupt/resume 흐름을 보여 주기 위한 것이다. 프로세스를 재시작해도 살아남는 "며칠 뒤 재개" 를 보장하려면 Postgres 같은 durable checkpointer(또는 LangSmith Deployment 계열의 영속 저장소)가 필요하다.

그래프 구조가 이토록 작은 이유는 라우팅이 노드 안의 `Command` 로 일어나기 때문이다. 각 노드는 `Command[Literal["node1", "node2"]]` 타입 힌트로 자기가 갈 수 있는 곳을 선언하므로, 흐름이 명시적이고 추적 가능하다. (LangGraph 에는 이 방식 외에 `add_conditional_edges` 같은 조건부 엣지 라우팅도 있으나, 이 교안의 트레이딩 예제는 `Command(goto=...)` 를 택했다 — 조건부 엣지는 이번 범위 밖이다.)

### 4.3. 멈췄다가 며칠 뒤에 이어서 — 실행과 재개

```python
# 사람 검토가 필요한 급등 과열(critical) 신호로 테스트
initial_state = {
    "instrument": "TSLA",
    "price_window": [200, 201, 199, ..., 218, 225],   # 최근 종가 윈도우
    "market_data_timestamp": "2026-06-04T09:30:00Z",
    "headline": "단기 급등, 과열 우려"
}

# 영속성을 위해 thread_id 와 함께 실행
config = {"configurable": {"thread_id": "TSLA-2026-06-04"}}
result = app.invoke(initial_state, config)
# 그래프는 approve_order 에서 (주문 전송 직전) 멈춘다
print(f"order approval interrupt:{result['__interrupt__']}")

# 준비되면 사람의 입력으로 재개
from langgraph.types import Command

human_response = Command(
    resume={"approved": True, "edited_qty": 5}   # 큰 베팅이라 수량을 줄여 승인
)

# 재개
final_result = app.invoke(human_response, config)
print("주문 전송 완료!")
```

그래프는 `interrupt()` 를 만나면 모든 것을 checkpointer 에 저장하고 **기다린다.** 같은 checkpointer 백엔드에 체크포인트가 남아 있고 같은 `thread_id` 로 다시 호출하면, 멈췄던 지점부터 이어진다. 여기서 `thread_id` 는 저장소 자체가 아니라 **체크포인트를 식별·조회하는 키** 이고, State 가 실제로 보존되는 곳은 checkpointer 다(이 예제에선 인메모리 `MemorySaver`).

![interrupt → checkpointer → resume](figs/fig07_interrupt_resume.svg)
<small>Figure — `interrupt()` 가 checkpointer 에 State 를 저장하고 멈춘다. 며칠 뒤라도 외부 호출자가 같은 `thread_id` 로 `Command(resume=...)` 를 호출하면, 런타임이 저장된 체크포인트를 조회해 멈춘 지점부터 재개한다.</small>

### 4.4. 노드를 얼마나 잘게 쪼갤까 — granularity 트레이드오프

"`fetch_market_data` 와 `generate_signal` 을 한 노드로 합치면 안 되나?" 라는 질문에 대한 답은 **회복력 vs 관찰가능성** 의 트레이드오프다.[^1]

![노드 granularity 와 재실행 범위](figs/fig08_node_granularity.svg)
<small>Figure — 노드를 작게 쪼갤수록 실패 시 재실행 범위가 줄어든다. 큰 노드는 끝에서 실패해도 처음부터 전부 다시 한다.</small>

- **회복력**: LangGraph 의 **내구성 있는 실행(durable execution)** 은 노드/슈퍼스텝 경계에서 체크포인트를 만든다. 중단 후 재개하면 멈춘 노드의 **처음부터** 다시 실행된다. 노드가 작을수록 재실행 비용이 작다. 여러 작업을 한 큰 노드에 몰면, 끝부분에서 실패해도 노드 처음부터 전부 다시 한다.
- **관찰가능성**: `generate_signal` 을 독립 노드로 두면, 주문 전에 무엇으로 판단했는지(z-score·방향·확신) 들여다볼 수 있다.
- **서로 다른 실패 양상**: 시세 조회·지표 계산·브로커 주문 전송은 재시도 전략이 제각각이다. 노드를 나누면 정책을 독립적으로 줄 수 있다.

> **성능 오해 주의**: 노드가 많다고 느려지지 않는다. LangGraph 는 기본적으로 체크포인트를 **백그라운드(async durability 모드)** 로 쓰므로, 그래프는 체크포인트 완료를 기다리지 않고 계속 실행된다. 필요하면 `"exit"` 모드(완료 시에만 체크포인트)나 `"sync"` 모드(매 체크포인트마다 블록)로 바꿀 수 있다.

### 4.5. 정리 — LangGraph 식 사고 6가지

<div class="feature-cards">
  <div class="feature-card">
    <div class="feature-card__icon">📦</div>
    <div class="feature-card__title">개별 스텝으로 분해</div>
    <div class="feature-card__body">노드 하나가 한 가지를 잘함. 스트리밍·재개·디버깅이 여기서 나온다.</div>
  </div>
  <div class="feature-card">
    <div class="feature-card__icon">💾</div>
    <div class="feature-card__title">State 는 공유 메모리</div>
    <div class="feature-card__body">포맷된 문자열이 아닌 raw 데이터를 저장한다.</div>
  </div>
  <div class="feature-card">
    <div class="feature-card__icon">⚙️</div>
    <div class="feature-card__title">노드는 함수</div>
    <div class="feature-card__body">State 를 받아 업데이트를 돌려준다. 라우팅이 필요하면 다음 행선지까지 함께 지정한다.</div>
  </div>
  <div class="feature-card">
    <div class="feature-card__icon">⚠️</div>
    <div class="feature-card__title">에러는 흐름의 일부</div>
    <div class="feature-card__body">재시도·되돌아오기·일시정지·띄워보내기로 나눈다.</div>
  </div>
  <div class="feature-card">
    <div class="feature-card__icon">👤</div>
    <div class="feature-card__title">사람 입력은 1급</div>
    <div class="feature-card__body"><code>interrupt()</code> 가 무한정 멈추고 State 를 저장, 입력이 오면 정확히 그 자리에서 재개한다.</div>
  </div>
  <div class="feature-card">
    <div class="feature-card__icon">🔗</div>
    <div class="feature-card__title">그래프 구조는 자연히 생긴다</div>
    <div class="feature-card__body">꼭 필요한 연결만 정의하고 라우팅은 노드가 한다.</div>
  </div>
</div>
