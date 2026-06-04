# LangGraph 워크드 예제 퀀트 트레이딩 재테마 설계 리뷰

## 결론

조건부 승인. 이메일 에이전트를 퀀트 트레이딩 에이전트로 바꾸는 방향은 LangGraph 교육 포인트를 거의 1:1로 보존한다. 특히 데이터 수집, 신호 생성, 리스크 점검, 사이징, 사람 승인, 주문 전송으로 쪼개는 구조는 노드 granularity, `Command(goto=...)`, `interrupt()/resume`, 노드 단위 에러 전략을 설명하기에 이메일 예제보다 퀀트 스터디 맥락에 더 잘 맞는다.

다만 한 가지는 설계상 고쳐야 한다. `generate_signal -> conviction=="critical" -> approve_order` 직행은 "주문 승인"이라는 노드명과 맞지 않는다. 이 시점에는 리스크 점검과 포지션 사이징이 끝나지 않았으므로 승인할 `order`가 없다. `critical`은 사람 검토를 요구하는 플래그로 들고 가되, 기본 경로는 `check_risk -> size_position -> approve_order -> place_order`가 되어야 한다. 직접 사람에게 보내고 싶다면 노드명을 `review_signal`로 바꾸거나, 승인 후 다시 `check_risk`로 돌아오는 별도 흐름이어야 한다.

검토 기준은 현재 리포트의 이메일 예제 구조, LangGraph `Thinking in LangGraph`, `Interrupts` 공식 문서에 둔다.

- https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph
- https://docs.langchain.com/oss/python/langgraph/interrupts

## 1. LangGraph 교육 포인트 보존 여부

대체로 보존된다.

| 교육 포인트 | 제안 설계 판정 | 코멘트 |
|---|---|---|
| 5단계 설계 | 보존 | `fetch_market_data -> generate_signal -> check_risk -> size_position -> approve_order -> place_order`는 분해, 스텝 유형 식별, State, 노드 구현, 연결의 설명 흐름을 유지한다. |
| 네 가지 스텝 유형 | 보존 | 데이터(`fetch_market_data`, `check_risk`), LLM/계산(`generate_signal`, `size_position`), 액션(`flag_anomaly`, `place_order`), 사용자 입력(`approve_order`)이 모두 남는다. |
| `Command(goto=...)` 라우팅 | 보존 | `generate_signal`, `check_risk`, `approve_order`가 라우팅 노드 역할을 한다. 기존 `classify_intent`, `human_review`의 교육 효과와 대응된다. |
| 에러 4전략 | 보존 가능 | ① `fetch_market_data` RetryPolicy, ② `steps/04` 전용 loop-back, ③ `approve_order` interrupt, ④ `place_order` bubble-up으로 유지된다. 단, 본 그래프에 ②가 없다는 점을 본문에서 명확히 해야 한다. |
| interrupt/resume | 보존 | `approve_order`가 주문 전송 직전의 사람 입력 노드가 되므로 기존 `human_review`보다 side effect 경계가 더 선명하다. |
| granularity | 보존, 오히려 강화 | 데이터 수집, 신호, 리스크, 사이징, 승인, 주문을 분리하면 실패 양상과 재실행 범위가 잘 보인다. |

어긋날 수 있는 부분은 세 가지다.

첫째, `check_risk`를 데이터 스텝으로만 설명하면 리스크 엔진이 단순 조회처럼 보일 수 있다. 교육상으로는 괜찮지만, "계정/포지션/한도 같은 외부 상태를 읽고, 변동성/노출 제한을 계산하는 데이터+계산 스텝"이라고 설명하는 편이 정확하다.

둘째, `flag_anomaly`는 `bug_tracking`의 액션 스텝 대응으로 좋지만, `uncertain`을 전부 데이터 이상으로 취급하면 의미가 흔들린다. `uncertain`은 보통 무거래 또는 사람 검토 사유이지 항상 anomaly가 아니다. `flag_anomaly`는 결측, 비정상 가격 점프, API 불일치, z-score 계산 불능 같은 데이터 품질 문제에만 쓰는 편이 낫다. 단순 신호 불확실성은 `END`로 보내며 `log`에 "no trade"를 남기는 것이 자연스럽다.

셋째, State의 `log: list[str]`는 구현 방식 주의가 필요하다. 노드가 `{"log": ["..."]}`처럼 부분 리스트를 반환할 계획이면 `Annotated[list[str], operator.add]` 같은 reducer가 필요하다. 기존 이메일 스크립트처럼 `_log(state, line)`으로 전체 누적 리스트를 반환한다면 reducer 없이도 동작하지만, State 교육 포인트에는 reducer를 보여 주는 쪽이 더 깔끔하다.

## 2. 퀀트 관점 검토

평균회귀 z-score는 Chan 스타일 워크드 예제로 자연스럽다. 다만 학습자가 오해하지 않도록 다음을 좁혀 쓰는 것이 좋다.

- 단일 종목 가격의 z-score보다는 "가격 또는 스프레드의 rolling z-score"라고 표현한다. Chan 맥락에서는 페어/스프레드, ETF, 선물 등 평균회귀가 가능한 시계열이라는 전제가 더 자연스럽다.
- 방향 규칙을 본문에 못 박는다. 예: `z <= -entry_threshold`면 long, `z >= entry_threshold`면 short, `abs(z) < exit_threshold`면 flat.
- `headline`은 LLM 입력으로 넣을 수 있지만, LLM이 거래 방향을 임의로 뒤집는 것처럼 보이면 위험하다. 교육 예제에서는 deterministic z-score가 1차 신호이고, LLM은 구조화 출력/설명/리스크 메모를 만드는 보조 역할이라고 선을 긋는 편이 안전하다.
- `conviction=critical`은 "큰 베팅"이라는 표현보다 "수동 검토 필요" 또는 "risk escalation"에 가깝게 쓰는 것이 낫다. 트레이딩에서 `critical`은 확신이라기보다 위험 이벤트처럼 읽힌다.
- Kelly sizing은 학습 예제로 과격하게 보일 수 있다. 기본값은 fixed fraction 또는 fractional Kelly로 두고, 항상 `max_notional`, `max_position_pct`, `volatility cap`을 걸어야 한다.
- `place_order` 실패를 전부 bubble-up으로 처리하면 실제 브로커 흐름과는 다르다. 미지의 시스템 오류는 bubble-up이 맞지만, 주문 거절, 장 마감, 부분 체결, 잔고 부족처럼 예상 가능한 실행 이벤트는 `execution_report`나 `order_status`로 State에 저장하는 편이 현실적이다. 다만 에러 ④를 보여 주는 데모 목적이라면 "예상치 못한 브로커 SDK 오류만 bubble-up"이라고 제한하면 충분하다.

가장 큰 도메인 문제는 리스크 게이트 위치다. `check_risk`가 `size_position`보다 앞에 있으면 "계좌/시장/변동성/거래 가능 여부" 같은 사전 점검은 할 수 있지만, 최종 주문 수량에 대한 한도 검사는 아직 불가능하다. 단순화를 유지하려면 `check_risk`가 `risk_report`와 `max_allowed_notional`을 만들고, `size_position`이 그 한도 안에서 `order`를 생성하도록 하라. 더 정확히 하려면 `size_position` 뒤에 `validate_order_risk`를 두지만, 학습 예제로는 노드가 늘어 과설계가 될 수 있다.

권장 라우팅은 다음이다.

```text
fetch_market_data
  -> generate_signal
      flat      -> END
      uncertain + data_quality_issue -> flag_anomaly -> END
      uncertain without anomaly      -> END
      long/short/critical            -> check_risk
  -> check_risk
      blocked    -> approve_order 또는 END
      ok         -> size_position
      escalated  -> size_position, 단 approval_required=True
  -> size_position
      order 생성
  -> approve_order
      approved -> place_order
      rejected -> END
  -> place_order -> END
```

이렇게 하면 `critical`의 교육적 역할도 살아난다. 즉 "강한 신호라서 바로 주문"이 아니라 "강한 신호 또는 큰 주문이라서 사람 승인 필요"가 된다.

## 3. interrupt 위치 검토

`size_position` 이후, `place_order` 이전의 `approve_order`에 `interrupt()`를 두는 것이 맞다. 이 위치가 가장 좋은 이유는 세 가지다.

- 사람이 승인할 payload에 실제 주문 후보(`instrument`, `side`, `qty`, `notional`, `limit/market`, `risk_report`, `rationale`)가 들어간다.
- 브로커 전송이라는 비멱등 side effect가 아직 발생하지 않았다.
- resume 이후에는 `approve_order` 노드의 앞부분만 재실행되고, 승인 결과에 따라 `place_order`로 넘어가므로 기존 `human_review -> send_reply` 구조와 정확히 대응된다.

구현 시 지켜야 할 점은 다음이다.

- `approve_order`에서 `interrupt()` 앞에는 순수 State 읽기와 JSON payload 조립만 둔다. DB write, audit insert, broker quote refresh, order id 발급 같은 부작용을 두지 않는다.
- interrupt payload와 resume payload는 JSON 직렬화 가능한 값으로 제한한다.
- 같은 `thread_id`로 resume해야 한다.
- `place_order`에는 idempotency key를 둔다. 예: `client_order_id = f"{thread_id}:{signal_id}:{order_hash}"`. 네트워크 재시도나 사용자 측 중복 resume에 대비한 브로커 중복 방지 장치다.
- 승인이 지연될 수 있으므로 `order["created_at"]` 또는 `market_data_timestamp`를 두고, `place_order` 진입 시 quote stale 여부를 검사한다. 오래된 주문이면 bubble-up보다 `END` 또는 재계산 경로가 더 적절하다.

## 4. 빠진 위험과 단순화 권고

추가하면 좋은 최소 State 필드는 다음이다.

```python
class TradingAgentState(TypedDict, total=False):
    instrument: str
    price_window: list[float]
    market_data_timestamp: str
    headline: str | None
    signal: SignalDecision | None
    risk_report: dict | None
    order: dict | None
    execution_report: dict | None
    client_order_id: str
    approval_required: bool
    log: Annotated[list[str], operator.add]
```

`risk_report`와 `order`는 가능하면 `TypedDict`를 추가로 정의하는 편이 좋다. 다만 발제 코드가 너무 길어지면 `dict` 유지가 낫다. 이 리포트의 목적은 트레이딩 시스템 설계가 아니라 LangGraph의 노드, 엣지, State를 가르치는 것이므로 타입 정밀도보다 흐름 가독성이 우선이다.

과설계를 피하려면 다음은 넣지 않는 편이 좋다.

- 포트폴리오 최적화, 백테스트, 멀티 자산 리밸런싱
- 뉴스 감성 모델과 z-score 모델의 복잡한 앙상블
- 실브로커 연동
- 부분 체결/정정/취소의 전체 주문관리시스템
- VaR, stress test, margin waterfall

대신 학습 예제의 기본 시나리오는 두세 개면 충분하다.

1. 정상 평균회귀 신호: 합성 시세 -> z-score -> fixed fraction sizing -> approval interrupt -> dry-run order.
2. flat/no-trade: 임계값 미만 -> `END`.
3. 데이터 이상 또는 API 실패: RetryPolicy 후 anomaly 기록, 또는 `steps/04`에서 loop-back 에러 전략 별도 시연.

## 리테마 작업 시 구체 수정 지침

- `fig03`은 topology를 유지하되 `critical` 직행선을 `approve_order`로 바로 보내지 말고, 사람 승인 필요 플래그가 리스크/사이징 이후 승인으로 이어지는 흐름을 보여 준다.
- `fig04`의 네 가지 스텝 유형은 `generate_signal`을 "LLM/계산", `size_position`을 "계산", `approve_order`를 "사용자 입력", `place_order`를 "액션"으로 라벨링한다.
- `fig05`가 State 그림이라면 formatted prompt가 아니라 raw `price_window`, `signal`, `risk_report`, `order`를 담는다는 점을 강조한다.
- `fig06/07`은 interrupt/checkpointer/resume 라벨만 트레이딩 용어로 바꾸면 된다. 이론 구조는 건드릴 필요가 없다.
- `fig08`은 `fetch_market_data + generate_signal + size_position + place_order`를 한 노드로 합쳤을 때 주문 실패 시 앞 계산까지 재실행되는 문제를 보여 주면 granularity 설명이 더 직관적이다.
- `scripts/langgraph.json`의 그래프 이름은 `email_agent`에서 `trading_agent`로 바꾸는 것이 좋다. 파일명도 가능하면 `trading_agent.py`로 바꾼다.
- `steps/04_errors.py`의 loop-back 예시는 본 그래프와 분리된 작은 그래프로 유지한다. 이론의 에러 ②를 억지로 주 경로에 넣으면 재테마가 과해진다.

## 최종 권고

재테마는 진행해도 된다. 단, `conviction=="critical" -> approve_order` 직행만은 그대로 두지 말라. 주문 승인 노드는 주문 후보가 만들어진 뒤에 와야 한다. `critical`은 `approval_required=True` 또는 `risk_escalation=True`로 State에 남기고, 리스크 점검과 사이징을 거친 뒤 `approve_order`에서 사람이 최종 주문을 승인하게 만드는 구성이 LangGraph 교육 포인트와 퀀트 도메인 양쪽에 가장 잘 맞는다.
