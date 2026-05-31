"""
[Step 3] State 설계 — raw 데이터만 담고, 프롬프트는 노드에서 그때 포맷한다 (리포트 §3.1-3.2)

🎯 이 단계에서 배우는 것:
    - State 에 담는 기준 한 가지: "단계를 넘어 보존돼야 하는가?"
    - 핵심 원칙: 포맷된 문자열이 아니라 raw 데이터를 저장한다
    - 같은 raw 데이터를 노드마다 '다르게' 포맷해 쓴다 (아래 두 노드가 같은
      classification 을 각각 사람용 / 로그용으로 다르게 포맷)

(Step 2 '스텝 유형 식별' 은 개념 단계라 코드가 없다 — 각 노드 docstring 의 [유형] 태그로 표시.)

💻 실행:
    ../../../../deep-agents/.venv/bin/python 02_state.py
"""

from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END


class EmailClassification(TypedDict):
    """분류 결과 — LLM 이 준 그대로 '하나의 딕셔너리' 로 저장한다."""
    intent: Literal["question", "bug", "billing"]
    urgency: Literal["low", "high", "critical"]
    topic: str


class EmailAgentState(TypedDict, total=False):
    # 원본 (나중에 재구성 불가 → 담는다)
    email_content: str
    sender_email: str
    # 분류 결과 (이후 여러 노드가 사용 → 담는다)
    classification: EmailClassification | None
    # 사람에게 보여줄 요약 (파생 가능하지만 데모로 보존)
    display: str
    # ⛔ 프롬프트 문자열·포맷된 텍스트는 State 에 담지 않는다


def classify_intent(state: EmailAgentState) -> dict:
    """[LLM 스텝] raw 분류 결과를 dict 그대로 저장. 포맷은 하지 않는다."""
    text = state["email_content"]
    if any(k in text for k in ("청구", "환불")):
        cls = {"intent": "billing", "urgency": "critical", "topic": "청구/결제"}
    elif any(k in text for k in ("버그", "오류")):
        cls = {"intent": "bug", "urgency": "high", "topic": "버그"}
    else:
        cls = {"intent": "question", "urgency": "low", "topic": "사용 문의"}
    return {"classification": cls}  # raw dict 그대로


def make_display(state: EmailAgentState) -> dict:
    """[데이터 스텝] 같은 raw 를 '사람용' 으로 포맷 — State 의 raw 는 건드리지 않는다."""
    c = state["classification"]
    return {"display": f"[{c['urgency'].upper()}] {c['topic']} 관련 {c['intent']} 문의"}


def build():
    g = StateGraph(EmailAgentState)
    g.add_node("classify_intent", classify_intent)
    g.add_node("make_display", make_display)
    g.add_edge(START, "classify_intent")
    g.add_edge("classify_intent", "make_display")
    g.add_edge("make_display", END)
    return g.compile()


if __name__ == "__main__":
    app = build()
    print("=" * 56)
    print("[Step 3] State 는 raw, 포맷은 노드에서 온디맨드")
    print("=" * 56)
    result = app.invoke({"email_content": "구독료가 두 번 청구됐어요!",
                         "sender_email": "customer@example.com"})

    print(f"\n  State 의 classification (raw dict): {result['classification']}")
    print(f"  같은 데이터를 '사람용' 으로 포맷한 display: {result['display']}")
    print("\n  → 같은 raw 를 로그용·프롬프트용으로 '각자 다르게' 포맷할 수 있다.")
    print("     프롬프트 템플릿이 바뀌어도 State 스키마는 그대로다.")
