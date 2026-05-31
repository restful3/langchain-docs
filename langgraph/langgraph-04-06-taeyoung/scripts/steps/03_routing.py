"""
[Step 4·5] 노드가 스스로 라우팅한다 — Command(goto=...), 엣지는 최소 (리포트 §3.4·§4.2)

🎯 이 단계에서 배우는 것:
    - 라우팅을 엣지가 아니라 '노드 안에서' Command(goto=...) 로 결정한다
    - 노드는 Command[Literal["a","b"]] 타입 힌트로 '갈 수 있는 곳' 을 선언한다
      → 흐름이 명시적이고, 그래프 그림에서 분기가 점선으로 보인다
    - 그래서 add_edge 로 박는 고정 엣지는 몇 개뿐이다

아직 사람 개입(interrupt)은 없다 — 분기 후 끝까지 자동으로 흐른다.

💻 실행:
    ../../../../deep-agents/.venv/bin/python 03_routing.py
"""

from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command


class State(TypedDict, total=False):
    email_content: str
    classification: dict | None
    search_results: list[str] | None
    draft: str


def classify_intent(
    state: State,
) -> Command[Literal["search_documentation", "bug_tracking", "draft_response"]]:
    """[LLM 스텝] 분류하고, 그 결과에 따라 다음 노드를 '스스로' 고른다."""
    text = state["email_content"]
    if any(k in text for k in ("버그", "오류")):
        cls, goto = {"intent": "bug", "topic": "버그"}, "bug_tracking"
    elif any(k in text for k in ("어떻게", "방법", "?")):
        cls, goto = {"intent": "question", "topic": "사용 문의"}, "search_documentation"
    else:
        cls, goto = {"intent": "complex", "topic": "기타"}, "draft_response"
    print(f"  🧠 classify_intent → {goto}")
    return Command(update={"classification": cls}, goto=goto)


def search_documentation(state: State) -> Command[Literal["draft_response"]]:
    """[데이터 스텝] 문서 검색 후 초안 작성으로."""
    topic = state["classification"]["topic"]
    print("  🗄️ search_documentation")
    return Command(update={"search_results": [f"[문서] {topic} 도움말"]}, goto="draft_response")


def bug_tracking(state: State) -> Command[Literal["draft_response"]]:
    """[액션 스텝] 이슈 생성 후 초안 작성으로."""
    print("  ⚡ bug_tracking: 이슈 생성")
    return Command(update={"search_results": ["이슈 BUG-001 생성"]}, goto="draft_response")


def draft_response(state: State) -> dict:
    """[LLM 스텝] 초안 작성. 여기선 끝(END)으로."""
    ctx = ", ".join(state.get("search_results") or [])
    print("  ✍️ draft_response")
    return {"draft": f"문의 확인했습니다. 참고: {ctx}"}


def build():
    g = StateGraph(State)
    g.add_node("classify_intent", classify_intent)
    g.add_node("search_documentation", search_documentation)
    g.add_node("bug_tracking", bug_tracking)
    g.add_node("draft_response", draft_response)
    # 고정 엣지는 단 둘 — 나머지 분기는 노드 안 Command 가 한다
    g.add_edge(START, "classify_intent")
    g.add_edge("draft_response", END)
    return g.compile()


if __name__ == "__main__":
    app = build()
    print("=" * 56)
    print("[Step 4·5] 노드 안 Command(goto) 라우팅")
    print("=" * 56)
    for email in ["비밀번호를 어떻게 변경하나요?", "로그인이 안 돼요 오류가 떠요"]:
        print(f"\n📨 '{email}'")
        result = app.invoke({"email_content": email})
        print(f"  → 초안: {result['draft']}")
