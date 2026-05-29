# Week3 — 에이전트 프로토콜 (MCP / ACP / A2A)

세 가지 에이전트 통신 프로토콜을 **코드 실습 중심**으로 배우는 자료입니다.
각 주제는 개념 설명과 실행 코드를 번갈아 담은 `.ipynb` 노트북으로 구성했습니다.

## 한 줄 비교

| 프로토콜 | 연결 대상 | 비유 | 노트북 |
|----------|-----------|------|--------|
| **MCP** (Model Context Protocol) | 에이전트 ↔ **외부 도구/데이터** | AI용 USB-C | [`01_mcp_langchain.ipynb`](01_mcp_langchain.ipynb) |
| **ACP** (Agent Client Protocol) | 에이전트 ↔ **에디터/IDE** | 에이전트-에디터 통합 | [`02_acp_deepagents.ipynb`](02_acp_deepagents.ipynb) |
| **A2A** (Agent2Agent) | 에이전트 ↔ **에이전트** | 에이전트 간 메시징 | [`03_a2a_langsmith.ipynb`](03_a2a_langsmith.ipynb) |

```
[에디터]  --ACP-->  [에이전트]  --MCP-->  [외부 도구]
                       |  A2A
                       v
                  [다른 에이전트]
```

## 학습 순서 (권장)

1. **MCP** — 가장 널리 쓰이고 다른 두 프로토콜의 토대가 되는 도구 연결 표준
2. **ACP** — 만든 에이전트를 에디터(Zed/VS Code 등)에 붙이기
3. **A2A** — 분산된 에이전트끼리 협업시키고 LangSmith 로 추적하기

## 시작하기

```bash
# 가상환경 후
cp .env_sample .env   # 키 채우기
jupyter lab           # 또는 VS Code 에서 .ipynb 열기
```

각 노트북 상단의 설치 셀(`!uv pip install ...`)을 먼저 실행하세요.

## 서버 실행이 필요한 실습 — [`scripts/`](scripts/)

stdio·포트 통신처럼 별도 프로세스로 띄워야 하는 부분은 바로 실행 가능한
파일로 [`scripts/`](scripts/) 에 분리해 두었습니다 (MCP 서버/클라이언트,
ACP 서버, A2A 그래프 + 핑퐁/트레이싱 클라이언트). 실행 방법은
[`scripts/README.md`](scripts/README.md) 참고.

## 원문 문서

- MCP: https://docs.langchain.com/oss/python/langchain/mcp
- ACP: https://docs.langchain.com/oss/python/deepagents/acp
- A2A: https://docs.langchain.com/langsmith/server-a2a
