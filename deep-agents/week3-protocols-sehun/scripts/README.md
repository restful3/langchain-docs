# scripts — 서버/클라이언트 실행 파일

노트북은 개념 학습용이고, 실제로 **서버를 띄우고 통신**하는 부분은 stdio·포트
특성상 별도 프로세스로 실행해야 한다. 노트북이 인라인으로 생성하던 파일들을
여기에 바로 실행 가능한 형태로 분리해 두었다.

```
scripts/
├── requirements.txt
├── mcp/
│   ├── math_server.py      # stdio MCP 서버 (add, multiply)
│   ├── weather_server.py   # http MCP 서버 (get_weather)
│   └── client_demo.py      # MultiServerMCPClient + create_agent
├── acp/
│   └── acp_server.py       # deep agent 를 ACP(stdio) 로 노출
└── a2a/
    ├── graph.py            # A2A 호환 LangGraph 에이전트
    ├── langgraph.json      # langgraph dev 등록 파일
    ├── pingpong_client.py  # 두 에이전트 핑퐁 대화
    └── traced_client.py    # thread_id 로 트레이스 통합
```

## 준비

```bash
uv pip install -r scripts/requirements.txt
cp .env_sample .env   # 상위 폴더에서. 키 채우기
```

## 실행 방법

### MCP (`scripts/mcp`)
```bash
# 터미널 1 — http weather 서버 (먼저 띄움)
python scripts/mcp/weather_server.py        # -> http://localhost:8000/mcp

# 터미널 2 — 클라이언트 (math 서버는 자동으로 서브프로세스 실행)
python scripts/mcp/client_demo.py
```
> weather 서버를 생략하려면 `client_demo.py` 의 `"weather"` 항목을 주석 처리.

### ACP (`scripts/acp`)
stdio 서버라 직접 실행하면 입력 대기 상태가 된다. 보통 에디터가 실행한다.
```bash
# 단독 확인
python scripts/acp/acp_server.py
```
에디터 등록 예시는 `acp_server.py` 상단 docstring 또는 노트북 §4 참고.

### A2A (`scripts/a2a`)
```bash
cd scripts/a2a
langgraph dev                 # agent A — 포트 2024
langgraph dev --port 2025     # agent B — 다른 터미널

# .env 에 AGENT_A_ID, AGENT_B_ID 채운 뒤
python pingpong_client.py     # 핑퐁 대화
python traced_client.py       # thread_id 트레이스 통합 (URL 의 assistant_id 교체)
```

## 필요한 환경변수 (`.env`)

| 스크립트 | 키 |
|----------|-----|
| mcp/client_demo.py | `ANTHROPIC_API_KEY` (또는 `MCP_MODEL`) |
| acp/acp_server.py | `GOOGLE_API_KEY` (gemini) 또는 모델에 맞는 키 |
| a2a/graph.py | `OPENAI_API_KEY` |
| a2a/*_client.py | `AGENT_A_ID`, `AGENT_B_ID`, (선택) `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` |
