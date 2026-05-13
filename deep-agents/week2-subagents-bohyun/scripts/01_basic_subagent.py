"""2주차 §2 — 딕셔너리 기반 SubAgent 기본 구성."""
from __future__ import annotations

from langchain.tools import tool
from deepagents import create_deep_agent

from common import build_model


@tool
def summarize_notes(topic: str) -> str:
    """Return compact study notes for a topic."""
    return f"핵심 요약: {topic}은 서브에이전트에 위임해 메인 컨텍스트를 작게 유지한다."


research_subagent = {
    "name": "research-agent",
    "description": "Deep Agents 개념을 짧게 조사하고 핵심만 요약한다.",
    "system_prompt": """당신은 발표 준비를 돕는 리서처다.
도구 결과를 길게 복사하지 말고, 발표자가 바로 쓸 수 있는 5문장 이하 요약만 반환한다.""",
    "tools": [summarize_notes],
}

agent = create_deep_agent(
    model=build_model(),
    tools=[summarize_notes],
    system_prompt="필요하면 research-agent에게 하위 조사를 위임하라.",
    subagents=[research_subagent],
)


def main() -> None:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "서브에이전트를 왜 쓰는지 발표용으로 정리해줘."}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
