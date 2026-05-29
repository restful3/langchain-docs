"""MCP 실습 — MultiServerMCPClient 로 두 서버의 도구를 모아 에이전트 실행.

노트북: 01_mcp_langchain.ipynb §3
원문: https://docs.langchain.com/oss/python/langchain/mcp

math 서버(stdio)는 이 클라이언트가 서브프로세스로 직접 띄우고,
weather 서버(http)는 미리 실행돼 있어야 한다:
    터미널 1:  python scripts/mcp/weather_server.py
    터미널 2:  python scripts/mcp/client_demo.py

ANTHROPIC_API_KEY 필요 (.env 참고). weather 서버를 안 띄웠다면
WEATHER 부분은 주석 처리하고 math 만으로 실행해도 된다.
"""
from __future__ import annotations

import asyncio
import os

from dotenv import find_dotenv, load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(find_dotenv())

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.environ.get("MCP_MODEL", "claude-sonnet-4-6")


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": [os.path.join(HERE, "math_server.py")],
            },
            "weather": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            },
        }
    )

    tools = await client.get_tools()
    print("로드된 도구:", [t.name for t in tools])

    agent = create_agent(MODEL, tools)
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
