"""MCP 실습 — Math 서버 (stdio 전송).

노트북: 01_mcp_langchain.ipynb §2
원문: https://docs.langchain.com/oss/python/langchain/mcp

FastMCP 로 만든 최소 MCP 서버. @mcp.tool() 로 데코레이트된 함수가 그대로
도구가 되고, docstring 이 도구 설명으로 LLM 에 전달된다.

이 서버는 stdio 모드라 직접 실행하기보다, 클라이언트
(client_demo.py)가 서브프로세스로 띄운다. 단독 확인은:
    python scripts/mcp/math_server.py   # Ctrl-C 로 종료
"""
from fastmcp import FastMCP

mcp = FastMCP("Math")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


if __name__ == "__main__":
    mcp.run(transport="stdio")
