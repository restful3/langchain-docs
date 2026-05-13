"""2주차 §4 — delete_file 승인/거부 HITL 데모."""
from __future__ import annotations

import uuid

from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from deepagents import create_deep_agent

from common import build_model


@tool
def delete_file(path: str) -> str:
    """Delete a file from the filesystem."""
    return f"DEMO ONLY: deleted {path}"


checkpointer = MemorySaver()
agent = create_deep_agent(
    model=build_model(),
    tools=[delete_file],
    system_prompt="사용자가 삭제를 요청하면 delete_file 도구를 호출하라.",
    interrupt_on={"delete_file": True},
    checkpointer=checkpointer,
)


def main() -> None:
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "temp.txt 파일을 삭제해줘."}]},
        config=config,
    )

    if result.get("__interrupt__"):
        interrupts = result["__interrupt__"][0].value
        print("승인 대기:", interrupts["action_requests"])
        decisions = [{"type": "approve"}]
        result = agent.invoke(Command(resume={"decisions": decisions}), config=config)

    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
