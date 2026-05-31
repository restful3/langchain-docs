"""
[Step 4] 에러를 흐름의 일부로 — 네 가지 전략 (리포트 §3.3)

🎯 이 단계에서 배우는 것: 에러는 종류마다 다르게 다룬다. "누가 고치느냐" 로 갈린다.
    ① 일시적 오류      → 시스템이 RetryPolicy 로 자동 재시도
    ② LLM 복구 가능    → State 에 에러 저장 후 agent 로 '되돌아오기'(loop-back)
    ③ 사용자 수정 가능 → interrupt() 로 멈추고 입력 받기
    ④ 예상치 못한 오류 → 삼키지 말고 그대로 띄워보내기(bubble up)

각 전략을 작은 독립 그래프로 하나씩 보여 준다.

💻 실행:
    ../../../../deep-agents/.venv/bin/python 04_errors.py
"""

from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, RetryPolicy, interrupt


# ① 일시적 오류 — RetryPolicy 로 자동 재시도 (두 번 실패 후 세 번째 성공) ----------
_attempts = []

def flaky_search(state: dict) -> dict:
    _attempts.append(1)
    n = len(_attempts)
    if n < 3:
        print(f"  🗄️ search 시도 {n}: 일시적 실패(네트워크) → 재시도")
        raise ValueError("transient network error")
    print(f"  🗄️ search 시도 {n}: 성공 ✅")
    return {"result": "문서 검색 결과"}

def demo_retry():
    g = StateGraph(dict)
    g.add_node("search", flaky_search,
               retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.01,
                                        retry_on=(ValueError,)))
    g.add_edge(START, "search"); g.add_edge("search", END)
    app = g.compile()
    print("① 일시적 오류 — 재시도 정책")
    print(f"  최종: {app.invoke({})}\n")


# ② LLM 복구 가능 — 에러를 State 에 저장하고 agent 로 되돌아오기 -------------------
class LoopState(TypedDict, total=False):
    tries: int
    tool_error: str
    done: bool

def agent(state: LoopState) -> Command[Literal["execute_tool", "__end__"]]:
    if state.get("done"):
        return Command(goto=END)
    if state.get("tool_error"):
        # 되돌아온 agent 가 에러 문자열을 '읽고' 접근을 바꾼다 (저장만으론 회복 안 됨)
        print(f"  🧠 agent: 직전 에러 '{state['tool_error']}' 보고 다른 인자로 재계획")
    return Command(goto="execute_tool")

def execute_tool(state: LoopState) -> Command[Literal["agent"]]:
    tries = state.get("tries", 0) + 1
    if tries == 1:
        print("  ⚡ execute_tool: 실패 → 에러를 State 에 담아 agent 로 되돌아감")
        return Command(update={"tries": tries, "tool_error": "bad argument"}, goto="agent")
    print("  ⚡ execute_tool: 성공 ✅")
    return Command(update={"tries": tries, "tool_error": "", "done": True}, goto="agent")

def demo_loopback():
    g = StateGraph(LoopState)
    g.add_node("agent", agent); g.add_node("execute_tool", execute_tool)
    g.add_edge(START, "agent")
    app = g.compile()
    print("② LLM 복구 가능 — 에러 저장 후 되돌아오기(loop-back)")
    app.invoke({})
    print()


# ③ 사용자 수정 가능 — interrupt() 로 멈추고 입력 받기 ----------------------------
class LookupState(TypedDict, total=False):
    customer_id: str
    customer_data: str

def lookup_customer(state: LookupState) -> Command[Literal["__end__", "lookup_customer"]]:
    if not state.get("customer_id"):
        user_input = interrupt({"request": "조회할 고객 계정 ID 를 입력해 주세요"})
        return Command(update={"customer_id": user_input["customer_id"]}, goto="lookup_customer")
    return Command(update={"customer_data": f"{state['customer_id']} 의 구독 이력"}, goto=END)

def demo_interrupt():
    g = StateGraph(LookupState)
    g.add_node("lookup_customer", lookup_customer)
    g.add_edge(START, "lookup_customer")
    app = g.compile(checkpointer=MemorySaver())   # interrupt 에는 checkpointer 가 필수
    cfg = {"configurable": {"thread_id": "t1"}}
    print("③ 사용자 수정 가능 — interrupt 로 정보 요청")
    r = app.invoke({}, cfg)
    print(f"  ⏸️  멈춤: {r['__interrupt__'][0].value['request']}")
    r = app.invoke(Command(resume={"customer_id": "CUST-42"}), cfg)
    print(f"  ▶️  재개 → {r['customer_data']}\n")


# ④ 예상치 못한 오류 — 그대로 띄워보내기(bubble up) ------------------------------
def send_reply(state: dict) -> dict:
    try:
        raise RuntimeError("메일 서버 다운")  # 다룰 수 없는 미지의 실패
    except Exception:
        raise  # 삼키지 않는다 — 표면화시켜 디버깅

def demo_bubble():
    g = StateGraph(dict)
    g.add_node("send", send_reply)
    g.add_edge(START, "send"); g.add_edge("send", END)
    app = g.compile()
    print("④ 예상치 못한 오류 — 띄워보내기")
    try:
        app.invoke({})
    except RuntimeError as e:
        print(f"  💥 예외가 그대로 표면화됨: {e}")
        print("     → try/except 로 모든 에러를 삼키지 않는다.")


if __name__ == "__main__":
    print("=" * 56)
    print("[Step 4] 에러 처리 네 가지 전략")
    print("=" * 56)
    demo_retry()
    demo_loopback()
    demo_interrupt()
    demo_bubble()
