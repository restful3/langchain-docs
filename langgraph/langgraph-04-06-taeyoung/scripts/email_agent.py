"""
고객지원 이메일 에이전트 — 리포트 "노드·엣지·State 편" 실행 가능 전체본

리포트 §3.4 의 약속("실행 가능한 전체본은 후속 scripts/ 에 둔다")을 이행하는 스크립트.
리포트의 축약본 코드(read_email·classify_intent 만 보였던)를 7개 노드 전부와
checkpointer·interrupt/resume 까지 채운 실행 가능본이다.

리포트 절 매핑:
    §3.1  EmailAgentState / EmailClassification  → State 스키마
    §2.2  네 가지 스텝 유형                        → 각 노드 docstring 의 [유형] 태그
    §3.3  에러 처리 4전략                          → ① RetryPolicy ③ interrupt ④ bubble up
    §4.1  interrupt() 로 사람 개입                  → human_review
    §4.2  노드 연결 + checkpointer 컴파일           → build_graph()
    §4.3  멈췄다 재개 (interrupt→resume)           → run_demo()

🎯 학습 목표:
    - State 는 raw 데이터만 담고, 프롬프트는 노드에서 그때 포맷한다 (§3.2)
    - 라우팅은 엣지가 아니라 노드 안의 Command(goto=...) 가 결정한다 (§4.2)
    - interrupt() 가 멈추고 State 를 저장, Command(resume=...) 가 그 자리에서 재개한다 (§4.3)

💻 실행 방법:
    # deep-agents/.venv 사용 (langgraph 1.1.10 설치돼 있음)
    ../../../deep-agents/.venv/bin/python email_agent.py            # 데모 2종 실행
    ../../../deep-agents/.venv/bin/python email_agent.py viz        # 그래프 ASCII 시각화

📦 필요한 패키지:
    - langgraph >= 1.0
    - (선택) langchain-openai + OPENAI_API_KEY — 없으면 규칙 기반 시뮬레이션으로 동작
"""

import os
from typing import Literal, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, RetryPolicy, interrupt


# =============================================================================
# §3.1 — State 스키마 (raw 데이터만 담는다)
# =============================================================================

class EmailClassification(TypedDict):
    """이메일 분류 결과 — LLM 이 돌려주는 그대로 하나의 딕셔너리로 State 에 저장."""
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str


class EmailAgentState(TypedDict, total=False):
    """
    모든 노드가 공유하는 메모리.

    total=False 인 이유: 리포트 §3.4 의 주의 — 기본 TypedDict 는 모든 키가 required 라
    initial_state 에 전부 채우거나 total=False 가 필요하다. 여기선 후자를 택했다.
    """
    # 원본 이메일 데이터 (나중에 재구성 불가 → State 에 담는다)
    email_content: str
    sender_email: str
    email_id: str
    # 분류 결과 (이후 여러 노드가 사용)
    classification: EmailClassification | None
    # 원본 검색/조회 결과 (다시 가져오기 비쌈 → 담는다)
    search_results: list[str] | None
    # 생성된 콘텐츠
    draft_response: str | None
    # 실행 로그 (디버깅·관찰용)
    log: list[str]


def _log(state: EmailAgentState, line: str) -> list[str]:
    """누적 로그 헬퍼 — State 의 log 에 한 줄 덧붙인 새 리스트를 돌려준다."""
    return [*state.get("log", []), line]


# =============================================================================
# LLM 옵셔널 — 키가 있으면 실제 LLM, 없으면 규칙 기반 시뮬레이션 (기존 예제 패턴)
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


def _simulate_classification(email_content: str) -> EmailClassification:
    """LLM 이 없을 때 쓰는 규칙 기반 분류 — 데모가 키 없이도 돌게 한다."""
    text = email_content.lower()
    if any(k in email_content for k in ("청구", "환불", "결제", "요금")) or "billing" in text:
        return {"intent": "billing", "urgency": "critical",
                "topic": "청구/결제", "summary": "청구 관련 긴급 문의"}
    if any(k in email_content for k in ("버그", "오류", "안 돼", "안돼", "에러")) or "bug" in text:
        return {"intent": "bug", "urgency": "high",
                "topic": "버그 리포트", "summary": "제품 오류 신고"}
    if any(k in email_content for k in ("어떻게", "방법", "?", "？", "문의")):
        return {"intent": "question", "urgency": "low",
                "topic": "사용 문의", "summary": "기능 사용법 질문"}
    return {"intent": "complex", "urgency": "medium",
            "topic": "기타", "summary": "분류 모호 — 기본 처리"}


# =============================================================================
# §2.2 / §3.3 — 노드 구현 (스텝 유형 + 에러 전략)
# 라우팅은 노드 안의 Command(goto=...) 가 결정한다.
# =============================================================================

def read_email(state: EmailAgentState) -> dict:
    """[데이터 스텝] 이메일 내용을 추출·파싱. 늘 classify_intent 로 간다(고정 엣지)."""
    return {"log": _log(state, f"📥 read_email: {state['email_id']} 수신")}


def classify_intent(
    state: EmailAgentState,
) -> Command[Literal["search_documentation", "human_review", "bug_tracking", "draft_response"]]:
    """[LLM 스텝] 의도·긴급도를 분류하고 그에 맞게 라우팅 (§3.4)."""
    llm = _get_llm()
    if llm is not None:
        structured_llm = llm.with_structured_output(EmailClassification)
        # 프롬프트는 State 에 저장하지 않고 여기서 그때 포맷 (§3.2)
        prompt = f"""이 고객 이메일을 분석해 분류하라:

Email: {state['email_content']}
From: {state.get('sender_email', '')}

intent(question/bug/billing/feature/complex), urgency(low/medium/high/critical),
topic, summary 를 포함해 분류하라."""
        classification = structured_llm.invoke(prompt)
    else:
        classification = _simulate_classification(state["email_content"])

    # 분류에 따라 다음 노드 결정
    if classification["intent"] == "billing" or classification["urgency"] == "critical":
        goto = "human_review"          # 긴급/청구 → 사람에게 바로 에스컬레이션
    elif classification["intent"] in ("question", "feature"):
        goto = "search_documentation"
    elif classification["intent"] == "bug":
        goto = "bug_tracking"
    else:
        goto = "draft_response"

    line = f"🧠 classify_intent: intent={classification['intent']} " \
           f"urgency={classification['urgency']} → {goto}"
    return Command(update={"classification": classification, "log": _log(state, line)}, goto=goto)


def search_documentation(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """[데이터 스텝] 지식 베이스 검색. 일시적 실패가 잦아 RetryPolicy 를 건다(§3.3 ①)."""
    topic = (state.get("classification") or {}).get("topic", "일반")
    results = [f"[문서] '{topic}' 관련 도움말 #1", f"[문서] '{topic}' 관련 FAQ #2"]
    return Command(
        update={"search_results": results, "log": _log(state, f"🗄️ search_documentation: {len(results)}건")},
        goto="draft_response",
    )


def bug_tracking(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """[액션 스텝] 트래킹 시스템에 이슈 생성. 캐시하지 않는다 — 매 호출이 고유 행동."""
    issue_id = f"BUG-{state['email_id'][-3:]}"
    return Command(
        update={"search_results": [f"이슈 {issue_id} 생성됨"],
                "log": _log(state, f"⚡ bug_tracking: {issue_id} 생성")},
        goto="draft_response",
    )


def draft_response(state: EmailAgentState) -> Command[Literal["human_review"]]:
    """[LLM 스텝] 답변 초안 생성. 작성 후 항상 human_review 로 보낸다."""
    cls = state.get("classification") or {}
    context = "\n".join(state.get("search_results") or [])
    llm = _get_llm()
    if llm is not None:
        prompt = f"""고객 이메일에 대한 정중한 한국어 답변 초안을 작성하라.

원문: {state['email_content']}
분류: {cls}
참고 자료:
{context}"""
        draft = llm.invoke(prompt).content
    else:
        draft = (f"안녕하세요, 문의 주신 '{cls.get('topic', '내용')}' 건 확인했습니다. "
                 f"아래 자료를 참고해 처리해 드리겠습니다.\n{context}".strip())
    return Command(
        update={"draft_response": draft, "log": _log(state, "✍️ draft_response: 초안 작성")},
        goto="human_review",
    )


def human_review(state: EmailAgentState) -> Command[Literal["send_reply", END]]:
    """
    [사용자 입력 스텝] interrupt 로 멈추고 사람의 결정을 받는다 (§4.1).

    interrupt() 이전에는 부작용 있는 호출을 두지 않는다 — 재개 시 이 앞은 다시 실행된다.
    분류 직후 에스컬레이션(초안 없음)과 초안 후 검토, 두 진입 경로를 모두 처리한다.
    """
    cls = state.get("classification") or {}  # None 일 수 있으므로 or {}

    human_decision = interrupt({
        "email_id": state.get("email_id", ""),
        "original_email": state.get("email_content", ""),
        "draft_response": state.get("draft_response", ""),   # 에스컬레이션이면 빈 문자열
        "urgency": cls.get("urgency"),
        "intent": cls.get("intent"),
        "action": "이 답변을 검토하고 승인/수정해 주세요 (초안이 비었으면 직접 작성)",
    })

    if human_decision.get("approved"):
        final = human_decision.get("edited_response", state.get("draft_response", ""))
        return Command(
            update={"draft_response": final, "log": _log(state, "👤 human_review: 승인 → 발송")},
            goto="send_reply",
        )
    # 거절 = 사람이 다른 채널로 직접 처리
    return Command(update={"log": _log(state, "👤 human_review: 거절 → 수동 처리")}, goto=END)


def send_reply(state: EmailAgentState) -> dict:
    """[액션 스텝] 이메일 발송. 다룰 수 없는 에러는 그대로 띄워보낸다(§3.3 ④)."""
    try:
        # email_service.send(...) 자리. 데모에서는 콘솔 출력으로 대체.
        return {"log": _log(state, f"📤 send_reply: {state.get('sender_email', '')} 로 발송 완료")}
    except Exception:
        raise  # 미지의 실패는 삼키지 않고 표면화시켜 디버깅


# =============================================================================
# §4.2 — 노드를 그래프로 연결하고 컴파일
# 라우팅이 노드 안 Command 로 일어나므로 필요한 엣지는 몇 개뿐이다.
# =============================================================================

def build_graph(checkpointer=None):
    """이메일 에이전트 그래프를 만들어 컴파일한다.

    checkpointer 를 넘기지 않으면 interrupt/resume 가 불가능하다(데모는 MemorySaver 사용).
    langgraph dev 로 띄울 때는 플랫폼이 checkpointer 를 주입하므로 None 으로 둔다.
    """
    workflow = StateGraph(EmailAgentState)

    workflow.add_node("read_email", read_email)
    workflow.add_node("classify_intent", classify_intent)
    # 일시적 실패가 잦은 노드에는 재시도 정책 (§3.3 ①)
    workflow.add_node("search_documentation", search_documentation,
                      retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0))
    workflow.add_node("bug_tracking", bug_tracking)
    workflow.add_node("draft_response", draft_response)
    workflow.add_node("human_review", human_review)
    workflow.add_node("send_reply", send_reply)

    # 꼭 필요한 엣지만 — 나머지 라우팅은 노드 안 Command(goto=...) 가 한다
    workflow.add_edge(START, "read_email")
    workflow.add_edge("read_email", "classify_intent")
    workflow.add_edge("send_reply", END)

    return workflow.compile(checkpointer=checkpointer)


# langgraph dev 용 (§5) — 모듈 레벨 그래프. langgraph.json 이 이 변수를 가리킨다.
graph = build_graph()


# =============================================================================
# §4.3 — 데모: 멈췄다가 재개 (interrupt → resume)
# =============================================================================

def _run_one(app, title: str, initial_state: dict, human_resume: dict):
    """한 이메일을 흘려보내고 → human_review 에서 멈추면 → 사람 입력으로 재개."""
    print("\n" + "=" * 64)
    print(f"📨 {title}")
    print("=" * 64)
    print(f"   원문: {initial_state['email_content']}")

    config = {"configurable": {"thread_id": initial_state["email_id"]}}
    result = app.invoke(initial_state, config)

    # interrupt 로 멈췄는지 확인
    if "__interrupt__" in result:
        payload = result["__interrupt__"][0].value
        print(f"\n   ⏸️  human_review 에서 일시정지 (urgency={payload.get('urgency')})")
        print(f"      초안: {payload.get('draft_response') or '(없음 — 에스컬레이션)'}")
        print(f"      → 사람 결정으로 재개: approved={human_resume.get('approved')}")
        result = app.invoke(Command(resume=human_resume), config)

    print("\n   📜 실행 로그:")
    for line in result.get("log", []):
        print(f"      {line}")


def run_demo():
    """리포트 §4.3 시나리오 — interrupt/resume 를 두 진입 경로로 보여 준다."""
    llm = _get_llm()
    mode = "실제 LLM(ChatOpenAI)" if llm is not None else "규칙 기반 시뮬레이션 (OPENAI_API_KEY 없음)"
    print("=" * 64)
    print("🤖 고객지원 이메일 에이전트 데모")
    print(f"   분류 모드: {mode}")
    print("=" * 64)

    app = build_graph(checkpointer=MemorySaver())

    # 시나리오 A: 긴급 청구 → classify 가 human_review 로 직행(초안 없음, 사람이 작성)
    _run_one(
        app,
        "시나리오 A — 긴급 청구 (분류 직후 에스컬레이션)",
        {"email_content": "구독료가 두 번 청구됐어요! 급해요!",
         "sender_email": "customer@example.com", "email_id": "email_A01"},
        {"approved": True,
         "edited_response": "이중 청구 건 진심으로 사과드립니다. 즉시 환불을 진행했습니다."},
    )

    # 시나리오 B: 사용 문의 → search → draft → human_review(초안 검토) → 승인
    _run_one(
        app,
        "시나리오 B — 사용 문의 (검색 → 초안 → 검토)",
        {"email_content": "비밀번호를 어떻게 변경하나요?",
         "sender_email": "user@example.com", "email_id": "email_B02"},
        {"approved": True},   # edited_response 없음 → 초안 그대로 발송
    )

    print("\n" + "=" * 64)
    print("✅ 데모 완료 — 같은 thread_id 로 재호출하니 멈춘 지점부터 재개됐다.")
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
