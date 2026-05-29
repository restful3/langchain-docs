"""MCP 실습 — Weather 서버 (streamable-http 전송).

노트북: 01_mcp_langchain.ipynb §2
원문: https://docs.langchain.com/oss/python/langchain/mcp

HTTP 전송 MCP 서버. stdio 서버와 달리 별도 포트에서 떠 있으므로
클라이언트보다 먼저 실행해 두어야 한다.

실행:
    python scripts/mcp/weather_server.py
    # -> http://localhost:8000/mcp 에서 대기
"""
from fastmcp import FastMCP

mcp = FastMCP("Weather")


@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "It's always sunny in New York"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
