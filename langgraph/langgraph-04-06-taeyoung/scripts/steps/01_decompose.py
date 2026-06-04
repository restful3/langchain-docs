"""
[Step 1] 워크플로우를 노드로 분해한다 — 리포트 §2

🎯 이 단계에서 배우는 것:
    - 노드는 'State 를 받아 업데이트를 돌려주는 파이썬 함수' 일 뿐이다
    - 그래프 = 노드 + 엣지. compile() 하면 실행 가능해진다
    - 아직 라우팅(분기) 없음 — 늘 같은 다음 노드로 가는 고정 엣지만

업무(평균회귀 매매)를 두 스텝으로 분해한다: fetch_market_data → generate_signal.

💻 실행:
    ../../../../deep-agents/.venv/bin/python 01_decompose.py
"""

import statistics
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# State — 일단 최소한만. (다음 단계에서 제대로 설계한다)
class State(TypedDict, total=False):
    instrument: str
    price_window: list[float]
    direction: str


def fetch_market_data(state: State) -> dict:
    """[데이터 스텝] 시세를 가져온다. 늘 generate_signal 로 간다(고정 엣지)."""
    print(f"  📈 fetch_market_data: {state['instrument']} 종가 {len(state['price_window'])}개")
    return {}  # State 변경 없음 (데모는 price_window 를 이미 들고 옴)


def generate_signal(state: State) -> dict:
    """[계산 스텝] z-score 로 방향을 정한다. 지금은 규칙만(LLM 자리만 잡아둠)."""
    w = state["price_window"]
    z = (w[-1] - statistics.fmean(w)) / statistics.pstdev(w)
    direction = "long" if z <= -1 else "short" if z >= 1 else "flat"
    print(f"  🧮 generate_signal: z={z:+.2f} → {direction}")
    return {"direction": direction}


def build():
    g = StateGraph(State)
    g.add_node("fetch_market_data", fetch_market_data)
    g.add_node("generate_signal", generate_signal)
    # 고정 엣지만 — START → fetch_market_data → generate_signal → END
    g.add_edge(START, "fetch_market_data")
    g.add_edge("fetch_market_data", "generate_signal")
    g.add_edge("generate_signal", END)
    return g.compile()


if __name__ == "__main__":
    app = build()
    print("=" * 56)
    print("[Step 1] 분해 — fetch_market_data → generate_signal")
    print("=" * 56)
    result = app.invoke({"instrument": "AAPL",
                         "price_window": [150, 151, 149, 150, 152, 148, 150, 151, 149, 145]})
    print(f"\n최종 State: {result}")
