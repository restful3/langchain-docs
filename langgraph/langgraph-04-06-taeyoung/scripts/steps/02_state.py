"""
[Step 3] State 설계 — raw 데이터만 담고, 프롬프트는 노드에서 그때 포맷한다 (리포트 §3.1-3.2)

🎯 이 단계에서 배우는 것:
    - State 에 담는 기준 한 가지: "단계를 넘어 보존돼야 하는가?"
    - 핵심 원칙: 포맷된 문자열이 아니라 raw 데이터(가격 윈도우·신호 dict)를 저장한다
    - 같은 raw 데이터를 노드마다 '다르게' 포맷해 쓴다 (아래 두 노드가 같은
      signal 을 각각 사람용 알림 / 주문 메모로 다르게 포맷)

(Step 2 '스텝 유형 식별' 은 개념 단계라 코드가 없다 — 각 노드 docstring 의 [유형] 태그로 표시.)

💻 실행:
    ../../../../deep-agents/.venv/bin/python 02_state.py
"""

import statistics
from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END


class SignalDecision(TypedDict):
    """신호 결과 — z-score 가 준 그대로 '하나의 딕셔너리' 로 저장한다."""
    direction: Literal["long", "short", "flat"]
    conviction: Literal["low", "high", "critical"]
    zscore: float


class TradingAgentState(TypedDict, total=False):
    # 원본 (다시 가져오기 비쌈 → 담는다)
    instrument: str
    price_window: list[float]
    # 신호 결과 (이후 여러 노드가 사용 → 담는다)
    signal: SignalDecision | None
    # 사람에게 보여줄 알림 (파생 가능하지만 데모로 보존)
    alert: str
    # ⛔ 프롬프트 문자열·포맷된 텍스트는 State 에 담지 않는다


def generate_signal(state: TradingAgentState) -> dict:
    """[계산 스텝] raw 신호 dict 그대로 저장. 포맷은 하지 않는다."""
    w = state["price_window"]
    z = (w[-1] - statistics.fmean(w)) / statistics.pstdev(w)
    direction = "long" if z <= -1 else "short" if z >= 1 else "flat"
    conviction = "critical" if abs(z) >= 2.5 else "high" if abs(z) >= 1.5 else "low"
    return {"signal": {"direction": direction, "conviction": conviction, "zscore": round(z, 2)}}


def make_alert(state: TradingAgentState) -> dict:
    """[데이터 스텝] 같은 raw 신호를 '사람용 알림' 으로 포맷 — State 의 raw 는 건드리지 않는다."""
    s = state["signal"]
    return {"alert": f"[{s['conviction'].upper()}] {state['instrument']} {s['direction'].upper()} "
                     f"신호 (z={s['zscore']})"}


def build():
    g = StateGraph(TradingAgentState)
    g.add_node("generate_signal", generate_signal)
    g.add_node("make_alert", make_alert)
    g.add_edge(START, "generate_signal")
    g.add_edge("generate_signal", "make_alert")
    g.add_edge("make_alert", END)
    return g.compile()


if __name__ == "__main__":
    app = build()
    print("=" * 56)
    print("[Step 3] State 는 raw, 포맷은 노드에서 온디맨드")
    print("=" * 56)
    result = app.invoke({"instrument": "TSLA",
                         "price_window": [200, 201, 199, 200, 202, 198, 200, 201, 218, 225]})

    print(f"\n  State 의 signal (raw dict): {result['signal']}")
    print(f"  같은 데이터를 '사람용' 으로 포맷한 alert: {result['alert']}")
    print("\n  → 같은 raw 신호를 알림용·주문메모용·LLM프롬프트용으로 '각자 다르게' 포맷할 수 있다.")
    print("     프롬프트 템플릿이 바뀌어도 State 스키마는 그대로다.")
