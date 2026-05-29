"""ACP 실습 — deep agent 를 ACP 서버로 노출 (stdio).

노트북: 02_acp_deepagents.ipynb §2
원문: https://docs.langchain.com/oss/python/deepagents/acp

create_deep_agent -> AgentServerACP -> run_agent 3단계로 ACP 서버를 만든다.
stdio 모드라 직접 실행하면 표준입력을 기다린다. 보통은 에디터(Zed/VS Code 등)
가 이 파일을 서브프로세스로 실행하도록 settings 에 등록한다.

에디터 등록 예 (Zed ~/.config/zed/settings.json):
    "agent_servers": {
      "My Deep Agent": {
        "command": "python",
        "args": ["/absolute/path/to/scripts/acp/acp_server.py"],
        "env": {"ANTHROPIC_API_KEY": "sk-ant-..."}
      }
    }
"""
from __future__ import annotations

import asyncio

from acp import run_agent
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

from deepagents_acp.server import AgentServerACP


async def main() -> None:
    agent = create_deep_agent(
        model="google_genai:gemini-3.5-flash",
        system_prompt="You are a helpful coding assistant",
        checkpointer=MemorySaver(),  # 멀티턴 대화 상태 유지
    )

    server = AgentServerACP(agent)
    await run_agent(server)


if __name__ == "__main__":
    asyncio.run(main())
