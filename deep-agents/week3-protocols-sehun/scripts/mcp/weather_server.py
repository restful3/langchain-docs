"""MCP 실습 — Weather 서버 (streamable-http 전송) + Bearer 토큰 인증.

노트북: 01_mcp_langchain.ipynb §2, §4
원문: https://docs.langchain.com/oss/python/langchain/mcp

HTTP 전송 MCP 서버. stdio 서버와 달리 별도 포트에서 떠 있으므로
클라이언트보다 먼저 실행해 두어야 한다.

이 서버는 §4 "실제 인증 테스트"를 위해 Bearer 토큰을 검증한다.
- 헤더가 없거나 토큰이 틀리면  -> 401 Unauthorized
- 토큰이 일치하면            -> 정상 응답

기대 토큰과 포트는 환경변수로 바꿀 수 있다(.env 또는 셸):
    MCP_SERVER_TOKEN   기대 토큰 (기본: demo-secret-token)
    MCP_WEATHER_PORT   리스닝 포트 (기본: 8000)

실행:
    python scripts/mcp/weather_server.py
    # -> http://localhost:8765/mcp 에서 대기 (Bearer 인증 필요)

클라이언트는 headers={"Authorization": f"Bearer {토큰}"} 로 호출한다.
"""
from __future__ import annotations

import os

from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, TokenVerifier

EXPECTED_TOKEN = os.environ.get("MCP_SERVER_TOKEN", "demo-secret-token")
PORT = int(os.environ.get("MCP_WEATHER_PORT", "8765"))


class StaticTokenVerifier(TokenVerifier):
    """가장 단순한 토큰 검증기 — 사전 공유된 정적 토큰 하나와 비교한다.

    실전에서는 JWT 서명 검증(fastmcp.server.auth.providers.jwt)이나
    OAuth introspection 을 쓴다. 여기서는 인증 흐름을 눈으로 보기 위한
    학습용 구현이다.
    """

    def __init__(self, valid_token: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._valid_token = valid_token

    async def verify_token(self, token: str) -> AccessToken | None:
        if token == self._valid_token:
            # 유효 -> 이 토큰의 권한 정보를 반환하면 요청이 통과한다.
            return AccessToken(token=token, client_id="weather-demo-client", scopes=[])
        # None -> 401 Unauthorized 로 거부된다.
        return None


mcp = FastMCP("Weather", auth=StaticTokenVerifier(EXPECTED_TOKEN))


@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "It's always sunny in New York"


if __name__ == "__main__":
    print(f"Weather MCP 서버 시작 — http://127.0.0.1:{PORT}/mcp")
    print(f"기대 토큰: {EXPECTED_TOKEN!r}  (헤더: 'Authorization: Bearer {EXPECTED_TOKEN}')")
    mcp.run(transport="streamable-http", host="127.0.0.1", port=PORT)
