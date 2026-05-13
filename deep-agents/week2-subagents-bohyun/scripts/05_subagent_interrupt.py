"""2주차 §6 — 서브에이전트 내부 interrupt_on 재정의."""
from __future__ import annotations

import uuid

from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from deepagents import create_deep_agent

from common import build_model


@tool
def read_file(path: str) -> str:
    """Read a file."""
    return f"DEMO ONLY: contents of {path}"


@tool
def delete_file(path: str) -> str:
    """Delete a file."""
    return f"DEMO ONLY: deleted {path}"


file_manager = {
    "name": "file-manager",
    "description": "파일 읽기와 삭제를 처리한다. 읽기도 민감한 작업으로 간주한다.",
    "system_prompt": "파일 작업 요청은 적절한 도구를 호출하라.",
    "tools": [read_file, delete_file],
    "interrupt_on": {
        "read_file": True,
        "delete_file": {"allowed_decisions": ["approve", "reject"]},
    },
}

agent = create_deep_agent(
    model=build_model(),
    tools=[read_file, delete_file],
    system_prompt="파일 작업은 file-manager에게 위임하라.",
    interrupt_on={"delete_file": True, "read_file": False},
    subagents=[file_manager],
    checkpointer=MemorySaver(),
)


def main() -> None:
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "secrets.txt 내용을 확인해줘."}]},
        config=config,
    )

    if result.get("__interrupt__"):
        interrupts = result["__interrupt__"][0].value
        print("서브에이전트 승인 대기:", interrupts["action_requests"])
        decisions = [{"type": "approve"} for _ in interrupts["action_requests"]]
        result = agent.invoke(Command(resume={"decisions": decisions}), config=config)

    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
