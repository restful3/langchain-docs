# 3주차 발표 — Protocols (MCP · A2A · ACP) & Coding Agent

**발표자**: 세훈
**주제**: Protocols & Coding Agent (20분)
**한 줄 요약**: MCP는 도구를, A2A는 에이전트를, ACP는 에디터를 표준 인터페이스로 묶는다. Deep Agents Code는 그 위에서 동작하는 LangChain의 코딩 에이전트다.

---

## 최종 산출물

| 산출물 | 파일 | 용도 |
| --- | --- | --- |
| 교과서 (PDF) | [content/textbook.pdf](content/textbook.pdf) | 발표 전후 단독 학습용 |
| 교과서 (HTML) | [content/textbook.html](content/textbook.html) | 빠른 브라우저 확인 |
| 슬라이드 (PDF) | [content/slides.pdf](content/slides.pdf) | 발표장 보조 자료 |
| 슬라이드 (HTML) | [content/slides.html](content/slides.html) | 브라우저 발표/검수 |
| 단독 실행 스크립트 5종 | [scripts/](scripts/) | MCP·A2A·ACP·Coding 패턴별 CLI 데모 |

시각자료는 [content/figs/](content/figs/) 의 SVG 5개를 사용한다.

---

## 다루는 4개 원문

| # | URL | 발제 섹션 |
| --- | --- | --- |
| 1 | [docs.langchain.com/oss/python/langchain/mcp](https://docs.langchain.com/oss/python/langchain/mcp) | §1. MCP |
| 2 | [docs.langchain.com/langsmith/server-a2a](https://docs.langchain.com/langsmith/server-a2a) | §2. A2A |
| 3 | [docs.langchain.com/oss/python/deepagents/acp](https://docs.langchain.com/oss/python/deepagents/acp) | §3. ACP |
| 4 | [docs.langchain.com/oss/python/deepagents/code/overview](https://docs.langchain.com/oss/python/deepagents/code/overview) | §5. Deep Agents Code |

§4 (Zed + ACP) 는 [zed.dev/blog/bring-your-own-agent-to-zed](https://zed.dev/blog/bring-your-own-agent-to-zed)
와 [agentclientprotocol.com](https://agentclientprotocol.com) 의 공개 문서를 보완해 작성했다.

---

## 셋업

```bash
cd langchain-docs/deep-agents/week3-protocols-sehun
cp .env_sample .env
pip install -r scripts/requirements.txt
```

필수 환경변수는 `.env_sample` 을 참고한다.

| 변수 | 비고 |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI 또는 OpenAI 호환 프록시 키 |
| `OPENAI_BASE_URL` | 비우면 OpenAI 직접, 채우면 호환 프록시 |
| `DEEPAGENT_MODEL` | 기본값 `gpt-4o-mini` |
| `MCP_MATH_SERVER_PATH` | (01·02 용) FastMCP math 서버 절대경로 |
| `LANGGRAPH_BASE_URL` | (03 용) LangGraph 서버 URL — 기본 `http://localhost:2024` |
| `LANGGRAPH_ASSISTANT_ID` | (03 용) 그래프 이름 — 기본 `agent` |

---

## 폴더 구조

```text
week3-protocols-sehun/
├── README.md
├── .env_sample
├── content/
│   ├── textbook.html
│   ├── textbook.pdf
│   ├── slides.html
│   ├── slides.pdf
│   └── figs/
├── scripts/
│   ├── 01_mcp_basic.py
│   ├── 02_mcp_interceptor.py
│   ├── 03_a2a_discovery.py
│   ├── 04_acp_server.py
│   ├── 05_coding_agent_demo.py
│   ├── common.py
│   ├── requirements.txt
│   └── README.md
└── archives/
    ├── meta/
    └── source/
```

PDF 재빌드는 다음 명령으로 수행한다.

```bash
python archives/source/build.py
```

`--html-only` 를 붙이면 chromedriver 없이도 HTML 만 출력된다.
