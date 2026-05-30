
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
