"""2주차 §5 — 도구 인자 edit 후 재개 데모."""
from __future__ import annotations

import uuid

from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from deepagents import create_deep_agent

from common import build_model


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"DEMO ONLY: sent email to {to} / {subject}"


agent = create_deep_agent(
    model=build_model(),
    tools=[send_email],
    system_prompt="사용자가 메일 발송을 요청하면 send_email 도구를 호출하라.",
    interrupt_on={"send_email": {"allowed_decisions": ["approve", "edit", "reject"]}},
    checkpointer=MemorySaver(),
)


def main() -> None:
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "everyone@company.com 에게 배포 공지를 보내줘."}]},
        config=config,
    )

    if result.get("__interrupt__"):
        action = result["__interrupt__"][0].value["action_requests"][0]
        print("원래 요청:", action)
        decisions = [
            {
                "type": "edit",
                "edited_action": {
                    "name": action["name"],
                    "args": {
                        "to": "team@company.com",
                        "subject": "2주차 발표 자료 공유",
                        "body": "서브에이전트와 HITL 데모 자료를 공유합니다.",
                    },
                },
            }
        ]
        result = agent.invoke(Command(resume={"decisions": decisions}), config=config)

    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
