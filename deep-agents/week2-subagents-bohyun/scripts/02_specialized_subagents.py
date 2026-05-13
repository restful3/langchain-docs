"""2주차 §3 — 여러 전문 서브에이전트 구성."""
from __future__ import annotations

from langchain.tools import tool
from deepagents import create_deep_agent

from common import build_model


@tool
def inspect_api(name: str) -> str:
    """Explain an API field."""
    return f"{name}: 발표에서는 필수 여부, 선택 기준, 실패 모드를 함께 설명한다."


@tool
def draft_slide(title: str) -> str:
    """Draft a short slide message."""
    return f"슬라이드 초안 - {title}: 한 화면에는 개념 하나와 코드 한 조각만 둔다."


api_reviewer = {
    "name": "api-reviewer",
    "description": "SubAgent와 interrupt_on 같은 API 필드를 정확히 설명한다.",
    "system_prompt": "API 필드의 타입, 필수 여부, 사용 시점을 짧은 표로 정리하라.",
    "tools": [inspect_api],
}

slide_writer = {
    "name": "slide-writer",
    "description": "발표 슬라이드 메시지를 짧고 선명하게 다듬는다.",
    "system_prompt": "슬라이드 한 장에 들어갈 제목, 한 줄 메시지, 말할 포인트 3개만 반환하라.",
    "tools": [draft_slide],
}

agent = create_deep_agent(
    model=build_model(),
    tools=[inspect_api, draft_slide],
    system_prompt="API 정확성이 필요하면 api-reviewer, 발표 문구가 필요하면 slide-writer에게 위임하라.",
    subagents=[api_reviewer, slide_writer],
)


def main() -> None:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "interrupt_on 설명 슬라이드를 만들고 API 필드도 검토해줘."}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
