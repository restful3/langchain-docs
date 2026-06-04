"""
평균회귀 트레이딩 에이전트 — 리포트 "노드·엣지·State 편" 실행 가능 전체본

리포트 §3.4 의 약속("실행 가능한 전체본은 후속 scripts/ 에 둔다")을 이행하는 스크립트.
리포트의 축약본 코드(fetch_market_data·generate_signal 만 보였던)를 7개 노드 전부와
checkpointer·interrupt/resume 까지 채운 실행 가능본이다.

리포트 절 매핑:
    §3.1  TradingAgentState / SignalDecision      → State 스키마
    §2.2  네 가지 스텝 유형                        → 각 노드 docstring 의 [유형] 태그
    §3.3  에러 처리 4전략                          → ① RetryPolicy ③ interrupt ④ bubble up
    §4.1  interrupt() 로 사람 개입                  → approve_order
    §4.2  노드 연결 + checkpointer 컴파일           → build_graph()
    §4.3  멈췄다 재개 (interrupt→resume)           → run_demo()

🎯 학습 목표:
    - State 는 raw 데이터(가격 윈도우·신호·리스크)만 담고, 프롬프트는 노드에서 그때 포맷한다 (§3.2)
    - 라우팅은 엣지가 아니라 노드 안의 Command(goto=...) 가 결정한다 (§4.2)
    - interrupt() 가 '주문 전송 직전' 멈추고 State 를 저장, Command(resume=...) 가 그 자리에서 재개한다 (§4.3)

💻 실행 방법:
    # deep-agents/.venv 사용 (langgraph 설치돼 있음)
    ../../../deep-agents/.venv/bin/python trading_agent.py            # 데모 3종 실행
    ../../../deep-agents/.venv/bin/python trading_agent.py viz        # 그래프 ASCII 시각화

📦 필요한 패키지:
    - langgraph >= 1.0
    - (선택) langchain-openai + OPENAI_API_KEY — 없으면 z-score 규칙만으로 동작
    - ⚠️ 교육용 예제다. 실제 매매·브로커 연동이 아니라 dry-run 으로 흐름만 보여 준다.
"""

import os
import statistics
from typing import Literal, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, RetryPolicy, interrupt


# =============================================================================
# §3.1 — State 스키마 (raw 데이터만 담는다)
# =============================================================================

class SignalDecision(TypedDict):
    """평균회귀 신호 결과 — 하나의 딕셔너리로 State 에 저장.

    direction  : 결정론적 z-score 가 정하는 방향 (LLM 이 임의로 뒤집지 않는다)
    conviction : |z| 크기 버킷. 'critical' 은 '큰 확신' 이 아니라
                 '비정상적으로 강한 신호 → 사람 검토 필요(risk escalation)' 의 의미다.
    """
    direction: Literal["long", "short", "flat", "uncertain"]
    conviction: Literal["low", "medium", "high", "critical"]
    instrument: str
    rationale: str


class TradingAgentState(TypedDict, total=False):
    """
    모든 노드가 공유하는 메모리.

    total=False 인 이유: 리포트 §3.4 의 주의 — 기본 TypedDict 는 모든 키가 required 라
    initial_state 에 전부 채우거나 total=False 가 필요하다. 여기선 후자를 택했다.
    """
    # 원본 시장 데이터 (다시 가져오기 비쌈/재구성 불가 → State 에 담는다)
    instrument: str
    price_window: list[float]          # 최근 종가(또는 스프레드) 윈도우 — raw
    market_data_timestamp: str         # 신호가 어느 시점 데이터인지 (stale 판정용)
    headline: str | None               # 뉴스 헤드라인 (LLM 의 동적 맥락, 옵션)
    # 신호 (이후 여러 노드가 사용)
    signal: SignalDecision | None
    # 리스크 점검 결과 (다시 계산 비쌈 → 담는다)
    risk_report: dict | None           # {"volatility":.., "max_allowed_notional":.., "blocked":..}
    # 주문 후보
    order: dict | None                 # {"side","qty","notional","limit_price","type"}
    # 큰 신호/리스크 초과로 '사람 승인 필요' 플래그 (라우팅이 아니라 표시)
    approval_required: bool
    # 실행 로그 (디버깅·관찰용)
    log: list[str]


# 신호 임계값 (본문에 못 박는 규칙) — z 단위
ENTRY_Z = 1.0      # |z| >= ENTRY 면 진입(롱/숏)
EXIT_Z = 0.5       # |z| <  EXIT  면 평탄(무거래)
HIGH_Z = 1.5       # |z| >= HIGH  면 conviction high
CRITICAL_Z = 2.5   # |z| >= CRIT  면 conviction critical(사람 검토 필요)

VOL_CAP = 0.06         # 변동성(σ/μ) 한도. 초과 시 리스크 차단
EQUITY = 100_000.0     # 가상 계좌 자본
TARGET_FRACTION = 0.02  # 고정비중: 자본의 2% (풀 켈리 회피; fractional Kelly 로 바꿀 수 있다)


def _log(state: TradingAgentState, line: str) -> list[str]:
    """누적 로그 헬퍼 — State 의 log 에 한 줄 덧붙인 새 리스트를 돌려준다.

    전체 리스트를 통째로 반환하므로 reducer 가 필요 없다. 부분 리스트만 반환하려면
    State 에 `log: Annotated[list[str], operator.add]` 처럼 reducer 를 다는 방법도 있다.
    """
    return [*state.get("log", []), line]


def _zscore(window: list[float]) -> float:
    """가격(또는 스프레드) 윈도우의 마지막 값에 대한 rolling z-score."""
    mu = statistics.fmean(window)
    sigma = statistics.pstdev(window)
    return (window[-1] - mu) / sigma  # sigma==0 이면 ZeroDivisionError → 호출부에서 anomaly 처리


# =============================================================================
# LLM 옵셔널 — 키가 있으면 rationale 을 LLM 으로, 없으면 규칙 문구.
# ※ 방향(direction)은 '언제나' z-score 가 결정한다. LLM 은 설명/구조화 보조일 뿐.
# =============================================================================

def _get_llm():
    """OPENAI_API_KEY 가 있고 패키지가 깔려 있으면 ChatOpenAI, 아니면 None."""
    if not os.getenv("OPENAI_API_KEY"):
        return None
    try:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-5-nano")  # 리포트가 쓴 모델
    except ImportError:
        return None


def _make_rationale(state: TradingAgentState, direction: str, z: float) -> str:
    """신호 근거 한 줄. LLM 이 있으면 헤드라인까지 엮어 설명, 없으면 규칙 문구."""
    llm = _get_llm()
    if llm is not None:
        prompt = f"""아래 평균회귀 신호를 한국어 한 문장으로 설명하라. 방향은 바꾸지 말고 근거만 적어라.

종목: {state['instrument']}
방향: {direction}  z-score: {z:.2f}
헤드라인: {state.get('headline') or '(없음)'}"""
        return llm.invoke(prompt).content.strip()
    return f"z={z:.2f} → 평균에서 {'아래' if z < 0 else '위'}로 벗어나 {direction} 되돌림 기대"


# =============================================================================
# §2.2 / §3.3 — 노드 구현 (스텝 유형 + 에러 전략)
# 라우팅은 노드 안의 Command(goto=...) 가 결정한다.
# =============================================================================

def fetch_market_data(state: TradingAgentState) -> dict:
    """[데이터 스텝] 시세 윈도우를 가져온다. 늘 generate_signal 로 간다(고정 엣지).

    일시적 실패(레이트리밋·타임아웃)가 잦은 외부 호출이라 그래프 등록 시 RetryPolicy 를 건다(§3.3①).
    데모는 initial_state 가 price_window 를 이미 담아 오므로 여기선 수신만 기록한다.
    """
    n = len(state.get("price_window") or [])
    return {"log": _log(state, f"📈 fetch_market_data: {state['instrument']} 종가 {n}개 수신")}


def generate_signal(
    state: TradingAgentState,
) -> Command[Literal["check_risk", "flag_anomaly", END]]:
    """[LLM/계산 스텝] z-score 로 방향·확신을 정하고 그에 맞게 라우팅 (§3.4).

    방향은 결정론적 z-score 가 정한다(LLM 은 rationale 만). 데이터 품질 이상이면
    flag_anomaly, 평탄이면 무거래로 END, 진입 신호면 check_risk 로 보낸다.
    """
    window = state.get("price_window") or []

    # 데이터 품질 점검 → 이상이면 anomaly 로 (단순 '약한 신호' 와는 구분한다)
    bad = (len(window) < 10) or any((x != x) or x <= 0 for x in window)  # x!=x → NaN
    try:
        sigma_zero = statistics.pstdev(window) == 0 if window else True
    except statistics.StatisticsError:
        sigma_zero = True
    if bad or sigma_zero:
        sig: SignalDecision = {"direction": "uncertain", "conviction": "low",
                               "instrument": state["instrument"],
                               "rationale": "가격 데이터 품질 이상(결측·비정상·표준편차 0)"}
        line = f"🧮 generate_signal: 데이터 이상 → flag_anomaly"
        return Command(update={"signal": sig, "log": _log(state, line)}, goto="flag_anomaly")

    z = _zscore(window)
    if z <= -ENTRY_Z:
        direction = "long"
    elif z >= ENTRY_Z:
        direction = "short"
    else:
        direction = "flat"

    az = abs(z)
    conviction = ("critical" if az >= CRITICAL_Z else
                  "high" if az >= HIGH_Z else
                  "medium" if az >= ENTRY_Z else "low")

    sig = {"direction": direction, "conviction": conviction,
           "instrument": state["instrument"],
           "rationale": _make_rationale(state, direction, z)}

    # 평탄(되돌릴 게 없음) → 무거래로 종료
    if direction == "flat":
        line = f"🧮 generate_signal: z={z:.2f} flat → 무거래(END)"
        return Command(update={"signal": sig, "log": _log(state, line + " · no trade")}, goto=END)

    # 진입 신호 → 리스크 점검으로. critical 은 '사람 승인 필요' 플래그만 세운다(직행 금지).
    approval = conviction == "critical"
    line = (f"🧮 generate_signal: z={z:.2f} {direction} "
            f"conviction={conviction}{' (escalation)' if approval else ''} → check_risk")
    return Command(
        update={"signal": sig, "approval_required": approval, "log": _log(state, line)},
        goto="check_risk",
    )


def check_risk(state: TradingAgentState) -> Command[Literal["size_position", "approve_order"]]:
    """[데이터+계산 스텝] 변동성·노출을 읽고 한도를 계산한다.

    risk_report 와 max_allowed_notional 을 만들어 둔다 — size_position 이 그 한도 안에서 주문한다.
    변동성이 캡을 넘으면 차단하고 approve_order 로 에스컬레이션(사람이 거부/예외승인).
    """
    window = state["price_window"]
    vol = statistics.pstdev(window) / statistics.fmean(window)   # σ/μ
    blocked = vol > VOL_CAP
    # 변동성이 낮을수록 더 큰 노출 허용 (단순화: 자본의 5% 를 변동성으로 스케일)
    max_notional = round(min(EQUITY * 0.05, EQUITY * 0.05 * (VOL_CAP / max(vol, 1e-9))), 2)
    report = {"volatility": round(vol, 4), "max_allowed_notional": max_notional, "blocked": blocked}

    if blocked:
        line = f"🛡️ check_risk: 변동성 {vol:.1%} > 캡 {VOL_CAP:.0%} → 차단, approve_order 에스컬레이션"
        return Command(
            update={"risk_report": report, "approval_required": True, "log": _log(state, line)},
            goto="approve_order",
        )
    line = f"🛡️ check_risk: 변동성 {vol:.1%} OK · 한도 ${max_notional:,.0f} → size_position"
    return Command(update={"risk_report": report, "log": _log(state, line)}, goto="size_position")


def size_position(state: TradingAgentState) -> Command[Literal["approve_order"]]:
    """[계산 스텝] 한도 안에서 고정비중 주문을 만든다. 작성 후 approve_order 로.

    고정비중(자본의 TARGET_FRACTION)을 쓰되 risk_report 의 max_allowed_notional 로 캡한다.
    (풀 켈리는 학습 예제에 과격 — fractional Kelly 로 바꾸려면 여기만 손대면 된다.)
    """
    sig = state["signal"]
    report = state.get("risk_report") or {}
    last = state["price_window"][-1]
    notional = min(EQUITY * TARGET_FRACTION, report.get("max_allowed_notional", EQUITY))
    qty = int(notional // last)
    side = "buy" if sig["direction"] == "long" else "sell"
    order = {"side": side, "qty": qty, "notional": round(qty * last, 2),
             "limit_price": last, "type": "limit"}
    line = f"📐 size_position: {side} {qty}주 @ ${last:,.2f} (≈${order['notional']:,.0f})"
    return Command(update={"order": order, "log": _log(state, line)}, goto="approve_order")


def approve_order(state: TradingAgentState) -> Command[Literal["place_order", END]]:
    """
    [사용자 입력 스텝] interrupt 로 멈추고 사람의 주문 승인을 받는다 (§4.1).

    interrupt() 앞에는 순수 State 읽기와 payload 조립만 둔다 — 재개 시 이 앞은 다시 실행된다.
    브로커 호출(비멱등 side effect)은 절대 이 앞에 두지 않는다.
    정상(사이징 후)과 차단 에스컬레이션(주문 없음) 두 진입 경로를 모두 처리한다.
    """
    order = state.get("order")  # 차단 에스컬레이션이면 None 일 수 있다
    report = state.get("risk_report") or {}
    sig = state.get("signal") or {}

    human_decision = interrupt({
        "instrument": state.get("instrument", ""),
        "order": order,                                   # 차단이면 None
        "risk_report": report,
        "conviction": sig.get("conviction"),
        "rationale": sig.get("rationale"),
        "approval_required": state.get("approval_required", False),
        "action": "이 주문을 승인/거부/수정하세요 (차단 건이면 예외 승인 여부 결정)",
    })

    if human_decision.get("approved") and order is not None:
        # 사람이 수량을 줄여 보냈으면 반영
        edited_qty = human_decision.get("edited_qty")
        if edited_qty is not None:
            order = {**order, "qty": edited_qty,
                     "notional": round(edited_qty * order["limit_price"], 2)}
        return Command(
            update={"order": order, "log": _log(state, "👤 approve_order: 승인 → 발주")},
            goto="place_order",
        )
    # 거부 또는 승인할 주문 없음(차단) = 사람이 다른 방식으로 처리
    return Command(update={"log": _log(state, "👤 approve_order: 거부/보류 → 미발주")}, goto=END)


def place_order(state: TradingAgentState) -> dict:
    """[액션 스텝] 브로커로 주문 전송. 예상 못한 오류는 그대로 띄워보낸다(§3.3④).

    실무라면 client_order_id(idempotency key, 예: f"{thread_id}:{signal_ts}:{hash}") 로
    중복 발주를 막고, market_data_timestamp 로 호가가 stale 한지 검사한다 — 여기선 주석으로만.
    주문 거절·부분 체결 같은 '예상 가능한' 실행 이벤트는 execution_report 로 State 에 담는 게
    현실적이지만, 이 예제는 에러 ④(예상 못한 SDK 오류 표면화)만 보이려 단순화했다.
    """
    order = state["order"]
    try:
        # broker.place(order) 자리. 데모에서는 dry-run 으로 콘솔 출력만.
        return {"log": _log(state, f"📤 place_order: dry-run 발주 완료 {order['side']} "
                                   f"{order['qty']}주 @ ${order['limit_price']:,.2f}")}
    except Exception:
        raise  # 미지의 실패는 삼키지 않고 표면화시켜 디버깅


def flag_anomaly(state: TradingAgentState) -> Command[Literal[END]]:
    """[액션 스텝] 데이터 품질 이상을 기록한다. 캐시하지 않는다 — 매 호출이 고유 기록."""
    return Command(
        update={"log": _log(state, f"⚠️ flag_anomaly: {state['instrument']} 데이터 이상 기록 → 무거래")},
        goto=END,
    )


# =============================================================================
# §4.2 — 노드를 그래프로 연결하고 컴파일
# 라우팅이 노드 안 Command 로 일어나므로 필요한 엣지는 몇 개뿐이다.
# =============================================================================

def build_graph(checkpointer=None):
    """트레이딩 에이전트 그래프를 만들어 컴파일한다.

    checkpointer 를 넘기지 않으면 interrupt/resume 가 불가능하다(데모는 MemorySaver 사용).
    langgraph dev 로 띄울 때는 플랫폼이 checkpointer 를 주입하므로 None 으로 둔다.
    """
    workflow = StateGraph(TradingAgentState)

    # 일시적 실패가 잦은 시세 호출에는 재시도 정책 (§3.3①)
    workflow.add_node("fetch_market_data", fetch_market_data,
                      retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0))
    workflow.add_node("generate_signal", generate_signal)
    workflow.add_node("check_risk", check_risk)
    workflow.add_node("size_position", size_position)
    workflow.add_node("approve_order", approve_order)
    workflow.add_node("place_order", place_order)
    workflow.add_node("flag_anomaly", flag_anomaly)

    # 꼭 필요한 엣지만 — 나머지 라우팅은 노드 안 Command(goto=...) 가 한다
    workflow.add_edge(START, "fetch_market_data")
    workflow.add_edge("fetch_market_data", "generate_signal")
    workflow.add_edge("place_order", END)

    return workflow.compile(checkpointer=checkpointer)


# langgraph dev 용 (§5) — 모듈 레벨 그래프. langgraph.json 이 이 변수를 가리킨다.
graph = build_graph()


# =============================================================================
# §4.3 — 데모: 멈췄다가 재개 (interrupt → resume)
# =============================================================================

# 결정론적 합성 시세 (키 없이도 재현되게 하드코딩). z-score 가 의도한 방향을 내도록 구성.
_MARKET = {
    # 평균 아래로 벗어남 → long, 변동성 보통 (정상 경로)
    "AAPL": [150, 153, 148, 151, 147, 152, 149, 153, 147, 150,
             151, 148, 152, 149, 151, 148, 150, 152, 149, 145],
    # 급등으로 평균 위 크게 벗어남 → short, conviction critical (에스컬레이션)
    "TSLA": [200, 201, 199, 200, 202, 198, 200, 201, 199, 200,
             200, 201, 199, 200, 201, 200, 199, 201, 218, 225],
    # 평균 근처 → flat (무거래)
    "SPY":  [430, 431, 429, 430, 431, 429, 430, 431, 430, 429,
             430, 431, 429, 430, 431, 430, 429, 431, 430, 430],
}


def _run_one(app, title: str, initial_state: dict, human_resume: dict | None):
    """한 종목을 흘려보내고 → approve_order 에서 멈추면 → 사람 입력으로 재개."""
    print("\n" + "=" * 64)
    print(f"💹 {title}")
    print("=" * 64)
    print(f"   종목: {initial_state['instrument']}  마지막 종가: ${initial_state['price_window'][-1]:,.2f}")

    config = {"configurable": {"thread_id": initial_state["instrument"]}}
    result = app.invoke(initial_state, config)

    # interrupt 로 멈췄는지 확인
    if "__interrupt__" in result:
        payload = result["__interrupt__"][0].value
        order = payload.get("order")
        flag = " ⚠️사람검토필요" if payload.get("approval_required") else ""
        print(f"\n   ⏸️  approve_order 에서 일시정지{flag} (conviction={payload.get('conviction')})")
        print(f"      주문 후보: {order or '(없음 — 리스크 차단 에스컬레이션)'}")
        print(f"      → 사람 결정으로 재개: {human_resume}")
        result = app.invoke(Command(resume=human_resume), config)

    print("\n   📜 실행 로그:")
    for line in result.get("log", []):
        print(f"      {line}")


def run_demo():
    """리포트 §4.3 시나리오 — interrupt/resume 를 여러 경로로 보여 준다."""
    llm = _get_llm()
    mode = "실제 LLM(rationale 생성)" if llm is not None else "z-score 규칙만 (OPENAI_API_KEY 없음)"
    print("=" * 64)
    print("🤖 평균회귀 트레이딩 에이전트 데모 (dry-run · 교육용)")
    print(f"   신호 모드: {mode}")
    print("=" * 64)

    app = build_graph(checkpointer=MemorySaver())

    # 시나리오 A: 저평가 되돌림(long) → 리스크 OK → 사이징 → 승인 → 발주
    _run_one(
        app,
        "시나리오 A — 저평가 되돌림 신호 (정상 발주)",
        {"instrument": "AAPL", "price_window": _MARKET["AAPL"],
         "market_data_timestamp": "2026-06-04T09:30:00Z",
         "headline": "특별한 악재 없음"},
        {"approved": True},   # 초안 그대로 승인
    )

    # 시나리오 B: 급등 과열(short) → conviction critical → 사람 승인(수량 축소)
    _run_one(
        app,
        "시나리오 B — 급등 과열 신호 (critical 에스컬레이션)",
        {"instrument": "TSLA", "price_window": _MARKET["TSLA"],
         "market_data_timestamp": "2026-06-04T09:30:00Z",
         "headline": "단기 급등, 과열 우려"},
        {"approved": True, "edited_qty": 5},   # 큰 베팅이라 사람이 수량을 줄여 승인
    )

    # 시나리오 C: 평균 근처 → flat → 무거래로 종료(interrupt 없음)
    _run_one(
        app,
        "시나리오 C — 평탄 (무거래)",
        {"instrument": "SPY", "price_window": _MARKET["SPY"],
         "market_data_timestamp": "2026-06-04T09:30:00Z", "headline": None},
        None,
    )

    print("\n" + "=" * 64)
    print("✅ 데모 완료 — 주문 전송 '직전' 에서 멈췄다가 사람 승인으로 그 자리에서 재개됐다.")
    print("=" * 64)


def visualize():
    """그래프 구조를 ASCII / Mermaid 로 출력 (기존 예제 패턴)."""
    try:
        print("\n[ASCII 시각화]")
        print(graph.get_graph().draw_ascii())
    except ImportError:
        print("   (ASCII 생략 — `pip install grandalf` 필요)")
    print("\n[Mermaid]")
    print(graph.get_graph().draw_mermaid())


def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "viz":
        visualize()
    else:
        run_demo()


if __name__ == "__main__":
    main()
