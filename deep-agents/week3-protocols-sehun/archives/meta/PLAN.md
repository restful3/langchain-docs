# 3주차 발표 작성 계획 — Protocols & Coding Agent

## 목표

세 프로토콜(MCP·A2A·ACP)과 그 위의 코딩 에이전트(Deep Agents Code)를
20분 발표 + 단독 학습용 교안 한 권으로 묶는다.

## 다루는 원문

1. https://docs.langchain.com/oss/python/langchain/mcp
2. https://docs.langchain.com/langsmith/server-a2a
3. https://docs.langchain.com/oss/python/deepagents/acp
4. https://docs.langchain.com/oss/python/deepagents/code/overview

§4 (Zed + ACP) 는 다음을 보완 사용:

- https://zed.dev/blog/bring-your-own-agent-to-zed
- https://agentclientprotocol.com/overview/introduction
- https://agentclientprotocol.com/protocol/overview
- https://github.com/zed-industries/agent-client-protocol

## 텍스트북 섹션

- §0 큰 그림 (세 프로토콜 자리 매핑)
- §1 MCP — 도구·리소스·프롬프트 표준
- §2 A2A — 에이전트 간 통신
- §3 ACP — 에디터-에이전트 표준
- §4 Zed + ACP — 클라이언트 사례와 다대다 생태계
- §5 Deep Agents Code — LangChain 코딩 에이전트
- 부록 A 비교 표 · 부록 B 트러블슈팅 · 부록 C 스크립트 안내

## 시각 자료

| 그림 | 용도 |
|---|---|
| fig01 | 세 프로토콜의 자리 (Agent ↔ Tool/Agent/Editor) |
| fig02 | MCP 클라이언트–서버 흐름 |
| fig03 | A2A 호출 흐름 |
| fig04 | ACP 라이프사이클 (Zed ↔ Deep Agent) |
| fig05 | Deep Agents Code 스택 |

## 실행 스크립트

| # | 파일 | 무엇을 보이나 |
|---|---|---|
| 01 | mcp_basic | MultiServerMCPClient + stdio |
| 02 | mcp_interceptor | 양파 인터셉터 + 런타임 컨텍스트 주입 |
| 03 | a2a_discovery | Agent Card + message/send |
| 04 | acp_server | Deep Agent 를 ACP 서버로 띄움 (Zed 등록용) |
| 05 | coding_agent_demo | dcode 스타일 빌트인 도구 + HITL |
