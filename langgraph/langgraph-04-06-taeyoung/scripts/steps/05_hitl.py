"""
[Step 4·5 완성] 사람 개입과 내구성 — interrupt + checkpointer + resume (리포트 §4)

🎯 이 단계에서 배우는 것:
    - interrupt() 가 워크플로우를 멈춰 모든 State 를 checkpointer 에 저장한다
    - Command(resume=...) 가 멈춘 지점부터 정확히 재개한다
    - 이를 가능케 하는 것이 checkpointer (여기선 인메모리 MemorySaver)
    - thread_id 는 저장소가 아니라 '체크포인트를 식별·조회하는 키' 다

Step 1~4 를 합친 완성본 그래프(부모 폴더 trading_agent.py)를 그대로 가져와 쓴다.
즉 이 파일은 '완성 그래프에 사람 승인을 붙여 돌리는' 마지막 단계다.

💻 실행:
    ../../../../deep-agents/.venv/bin/python 05_hitl.py
"""

import os
import sys

# 부모 폴더(scripts/)의 trading_agent.py 를 import 할 수 있게 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from trading_agent import build_graph, _MARKET


if __name__ == "__main__":
    print("=" * 56)
    print("[Step 4·5] interrupt → checkpointer → resume")
    print("=" * 56)

    # checkpointer 와 함께 컴파일해야 interrupt/resume 가 가능하다
    app = build_graph(checkpointer=MemorySaver())

    # 급등 과열(critical) → approve_order(주문 전송 직전)에서 멈춘다
    initial = {"instrument": "TSLA", "price_window": _MARKET["TSLA"],
               "market_data_timestamp": "2026-06-04T09:30:00Z", "headline": "단기 급등"}
    config = {"configurable": {"thread_id": "TSLA-demo"}}

    result = app.invoke(initial, config)
    print("\n  1) 첫 호출 → approve_order 에서 일시정지")
    payload = result["__interrupt__"][0].value
    print(f"     interrupt payload: conviction={payload['conviction']} 주문={payload['order']}")

    # 멈춘 사이, checkpointer 에 State 가 저장돼 있음을 확인 (며칠 뒤라도 살아 있다)
    snapshot = app.get_state(config)
    print(f"\n  2) checkpointer 에 저장된 State 의 다음 실행 노드: {snapshot.next}")
    print(f"     (이 thread_id 로 다시 호출하면 바로 이 지점부터 재개된다)")

    # 사람의 결정으로 재개 (큰 베팅이라 수량을 줄여 승인)
    resume = Command(resume={"approved": True, "edited_qty": 5})
    final = app.invoke(resume, config)
    print("\n  3) 사람 승인으로 재개 → 멈춘 지점부터 이어짐")
    for line in final.get("log", []):
        print(f"     {line}")

    print("\n  ⚠️ MemorySaver 는 인메모리(개발·데모)용 — 프로세스 재시작에도 살아남는")
    print("     '며칠 뒤 재개' 는 Postgres 같은 durable checkpointer 가 필요하다.")
