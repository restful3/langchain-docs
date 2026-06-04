"""
[Step 4·5] 노드가 스스로 라우팅한다 — Command(goto=...), 엣지는 최소 (리포트 §3.4·§4.2)

🎯 이 단계에서 배우는 것:
    - 라우팅을 엣지가 아니라 '노드 안에서' Command(goto=...) 로 결정한다
    - 노드는 Command[Literal["a","b"]] 타입 힌트로 '갈 수 있는 곳' 을 선언한다
      → 흐름이 명시적이고, 그래프 그림에서 분기가 점선으로 보인다
    - 그래서 add_edge 로 박는 고정 엣지는 몇 개뿐이다

아직 사람 개입(interrupt)은 없다 — 분기 후 끝까지 자동으로 흐른다.
check_risk 가 '한도 OK → 사이징' / '변동성 초과 → 차단' 두 갈래로 가는 것까지 보여 준다.

💻 실행:
    ../../../../deep-agents/.venv/bin/python 03_routing.py
"""

import statistics
from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command


class State(TypedDict, total=False):
    instrument: str
    price_window: list[float]
    signal: dict | None
    risk_report: dict | None
    order: dict | None


def generate_signal(
    state: State,
) -> Command[Literal["check_risk", "flag_anomaly", END]]:
    """[계산 스텝] z-score 로 방향을 정하고, 그 결과에 따라 다음 노드를 '스스로' 고른다."""
    w = state["price_window"]
    if len(w) < 10 or statistics.pstdev(w) == 0:        # 데이터 품질 이상
        print("  🧮 generate_signal: 데이터 이상 → flag_anomaly")
        return Command(update={"signal": {"direction": "uncertain"}}, goto="flag_anomaly")
    z = (w[-1] - statistics.fmean(w)) / statistics.pstdev(w)
    direction = "long" if z <= -1 else "short" if z >= 1 else "flat"
    sig = {"direction": direction, "zscore": round(z, 2)}
    if direction == "flat":
        print(f"  🧮 generate_signal: z={z:+.2f} flat → 무거래(END)")
        return Command(update={"signal": sig}, goto=END)
    print(f"  🧮 generate_signal: z={z:+.2f} {direction} → check_risk")
    return Command(update={"signal": sig}, goto="check_risk")


def check_risk(state: State) -> Command[Literal["size_position", END]]:
    """[데이터+계산 스텝] 변동성 한도 점검. OK 면 사이징, 초과면 차단(데모는 END)."""
    w = state["price_window"]
    vol = statistics.pstdev(w) / statistics.fmean(w)
    if vol > 0.06:
        print(f"  🛡️ check_risk: 변동성 {vol:.1%} 초과 → 차단(END)")
        return Command(update={"risk_report": {"blocked": True, "volatility": round(vol, 4)}}, goto=END)
    print(f"  🛡️ check_risk: 변동성 {vol:.1%} OK → size_position")
    return Command(update={"risk_report": {"blocked": False, "volatility": round(vol, 4)}},
                   goto="size_position")


def size_position(state: State) -> dict:
    """[계산 스텝] 고정비중 주문을 만든다. 여기선 끝(END)으로."""
    last = state["price_window"][-1]
    side = "buy" if state["signal"]["direction"] == "long" else "sell"
    qty = int((100_000 * 0.02) // last)
    print(f"  📐 size_position: {side} {qty}주 @ ${last:,.2f}")
    return {"order": {"side": side, "qty": qty, "limit_price": last}}


def flag_anomaly(state: State) -> dict:
    """[액션 스텝] 데이터 이상을 기록한다."""
    print(f"  ⚠️ flag_anomaly: {state['instrument']} 데이터 이상 기록")
    return {}


def build():
    g = StateGraph(State)
    g.add_node("generate_signal", generate_signal)
    g.add_node("check_risk", check_risk)
    g.add_node("size_position", size_position)
    g.add_node("flag_anomaly", flag_anomaly)
    # 고정 엣지는 둘뿐 — 나머지 분기는 노드 안 Command 가 한다
    g.add_edge(START, "generate_signal")
    g.add_edge("size_position", END)
    return g.compile()


if __name__ == "__main__":
    app = build()
    print("=" * 56)
    print("[Step 4·5] 노드 안 Command(goto) 라우팅")
    print("=" * 56)
    cases = {
        "저평가 되돌림(long)": [150, 153, 148, 151, 147, 152, 149, 151, 148, 145],
        "평탄(무거래)":      [430, 431, 429, 430, 431, 429, 430, 431, 430, 430],
    }
    for title, window in cases.items():
        print(f"\n📨 {title}")
        result = app.invoke({"instrument": "X", "price_window": window})
        print(f"  → order: {result.get('order')}")
