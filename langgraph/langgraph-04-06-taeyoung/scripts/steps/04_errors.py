"""
[Step 4] 에러를 흐름의 일부로 — 네 가지 전략 (리포트 §3.3)

🎯 이 단계에서 배우는 것: 에러는 종류마다 다르게 다룬다. "누가 고치느냐" 로 갈린다.
    ① 일시적 오류      → 시스템이 RetryPolicy 로 자동 재시도 (시세 API 레이트리밋/타임아웃)
    ② LLM 복구 가능    → State 에 에러 저장 후 agent 로 '되돌아오기'(loop-back)
    ③ 사용자 수정 가능 → interrupt() 로 멈추고 입력 받기 (계좌 ID 누락 등)
    ④ 예상치 못한 오류 → 삼키지 말고 그대로 띄워보내기(bubble up) (브로커 SDK 장애)

각 전략을 작은 독립 그래프로 하나씩 보여 준다.
(② loop-back 은 본 트레이딩 주 경로엔 없는 '도구 실행 에이전트' 패턴이라 여기서만 시연한다.)

💻 실행:
    ../../../../deep-agents/.venv/bin/python 04_errors.py
"""

from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, RetryPolicy, interrupt


# ① 일시적 오류 — RetryPolicy 로 자동 재시도 (두 번 실패 후 세 번째 성공) ----------
_attempts = []

def flaky_fetch(state: dict) -> dict:
    _attempts.append(1)
    n = len(_attempts)
    if n < 3:
        print(f"  📈 시세 호출 시도 {n}: 일시적 실패(레이트리밋) → 재시도")
        raise ConnectionError("rate limited")
    print(f"  📈 시세 호출 시도 {n}: 성공 ✅")
    return {"price_window": [150, 151, 149, 145]}

def demo_retry():
    g = StateGraph(dict)
    g.add_node("fetch", flaky_fetch,
               retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.01,
                                        retry_on=(ConnectionError,)))
    g.add_edge(START, "fetch"); g.add_edge("fetch", END)
    app = g.compile()
    print("① 일시적 오류 — 재시도 정책")
    print(f"  최종: {app.invoke({})}\n")


# ② LLM 복구 가능 — 에러를 State 에 저장하고 agent 로 되돌아오기 -------------------
class LoopState(TypedDict, total=False):
    tries: int
    tool_error: str
    done: bool

def agent(state: LoopState) -> Command[Literal["run_indicator", "__end__"]]:
    if state.get("done"):
        return Command(goto=END)
    if state.get("tool_error"):
        # 되돌아온 agent 가 에러 문자열을 '읽고' 접근을 바꾼다 (저장만으론 회복 안 됨)
        print(f"  🧠 agent: 직전 에러 '{state['tool_error']}' 보고 다른 파라미터로 재계획")
    return Command(goto="run_indicator")

def run_indicator(state: LoopState) -> Command[Literal["agent"]]:
    """지표 계산 도구 실행 — 처음엔 잘못된 룩백으로 실패, 재계획 후 성공."""
    tries = state.get("tries", 0) + 1
    if tries == 1:
        print("  ⚙️ run_indicator: 룩백 윈도우 부족으로 실패 → 에러를 State 에 담아 agent 로")
        return Command(update={"tries": tries, "tool_error": "lookback too short"}, goto="agent")
    print("  ⚙️ run_indicator: 성공 ✅")
    return Command(update={"tries": tries, "tool_error": "", "done": True}, goto="agent")

def demo_loopback():
    g = StateGraph(LoopState)
    g.add_node("agent", agent); g.add_node("run_indicator", run_indicator)
    g.add_edge(START, "agent")
    app = g.compile()
    print("② LLM 복구 가능 — 에러 저장 후 되돌아오기(loop-back)")
    app.invoke({})
    print()


# ③ 사용자 수정 가능 — interrupt() 로 멈추고 입력 받기 ----------------------------
class AccountState(TypedDict, total=False):
    account_id: str
    buying_power: float

def lookup_account(state: AccountState) -> Command[Literal["__end__", "lookup_account"]]:
    if not state.get("account_id"):
        user_input = interrupt({"request": "주문에 쓸 계좌 ID 를 입력해 주세요"})
        return Command(update={"account_id": user_input["account_id"]}, goto="lookup_account")
    return Command(update={"buying_power": 100_000.0}, goto=END)

def demo_interrupt():
    g = StateGraph(AccountState)
    g.add_node("lookup_account", lookup_account)
    g.add_edge(START, "lookup_account")
    app = g.compile(checkpointer=MemorySaver())   # interrupt 에는 checkpointer 가 필수
    cfg = {"configurable": {"thread_id": "t1"}}
    print("③ 사용자 수정 가능 — interrupt 로 정보 요청")
    r = app.invoke({}, cfg)
    print(f"  ⏸️  멈춤: {r['__interrupt__'][0].value['request']}")
    r = app.invoke(Command(resume={"account_id": "ACC-42"}), cfg)
    print(f"  ▶️  재개 → 매수여력 ${r['buying_power']:,.0f}\n")


# ④ 예상치 못한 오류 — 그대로 띄워보내기(bubble up) ------------------------------
def place_order(state: dict) -> dict:
    try:
        raise RuntimeError("브로커 SDK 인증 만료")  # 다룰 수 없는 미지의 실패
    except Exception:
        raise  # 삼키지 않는다 — 표면화시켜 디버깅

def demo_bubble():
    g = StateGraph(dict)
    g.add_node("place_order", place_order)
    g.add_edge(START, "place_order"); g.add_edge("place_order", END)
    app = g.compile()
    print("④ 예상치 못한 오류 — 띄워보내기")
    try:
        app.invoke({})
    except RuntimeError as e:
        print(f"  💥 예외가 그대로 표면화됨: {e}")
        print("     → 주문거절·부분체결 같은 '예상 가능' 이벤트는 execution_report 로 담고,")
        print("        미지의 SDK 오류만 이렇게 띄워보낸다.")


if __name__ == "__main__":
    print("=" * 56)
    print("[Step 4] 에러 처리 네 가지 전략")
    print("=" * 56)
    demo_retry()
    demo_loopback()
    demo_interrupt()
    demo_bubble()
