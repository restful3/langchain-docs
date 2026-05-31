"""
[Step 1] 워크플로우를 노드로 분해한다 — 리포트 §2

🎯 이 단계에서 배우는 것:
    - 노드는 'State 를 받아 업데이트를 돌려주는 파이썬 함수' 일 뿐이다
    - 그래프 = 노드 + 엣지. compile() 하면 실행 가능해진다
    - 아직 라우팅(분기) 없음 — 늘 같은 다음 노드로 가는 고정 엣지만

업무(고객 이메일 처리)를 두 스텝으로 분해한다: read_email → classify_intent.

💻 실행:
    ../../../../deep-agents/.venv/bin/python 01_decompose.py
"""

from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END


# State — 일단 최소한만. (다음 단계에서 제대로 설계한다)
class State(TypedDict, total=False):
    email_content: str
    intent: str


def read_email(state: State) -> dict:
    """[데이터 스텝] 이메일을 읽는다. 늘 classify_intent 로 간다(고정 엣지)."""
    print(f"  📥 read_email: '{state['email_content']}'")
    return {}  # State 변경 없음


def classify_intent(state: State) -> dict:
    """[LLM 스텝] 의도를 분류한다. 지금은 규칙 기반(LLM 자리만 잡아둠)."""
    text = state["email_content"]
    if any(k in text for k in ("청구", "환불", "결제")):
        intent = "billing"
    elif any(k in text for k in ("버그", "오류", "안 돼")):
        intent = "bug"
    else:
        intent = "question"
    print(f"  🧠 classify_intent: intent={intent}")
    return {"intent": intent}


def build():
    g = StateGraph(State)
    g.add_node("read_email", read_email)
    g.add_node("classify_intent", classify_intent)
    # 고정 엣지만 — START → read_email → classify_intent → END
    g.add_edge(START, "read_email")
    g.add_edge("read_email", "classify_intent")
    g.add_edge("classify_intent", END)
    return g.compile()


if __name__ == "__main__":
    app = build()
    print("=" * 56)
    print("[Step 1] 분해 — read_email → classify_intent")
    print("=" * 56)
    result = app.invoke({"email_content": "구독료가 두 번 청구됐어요!"})
    print(f"\n최종 State: {result}")
