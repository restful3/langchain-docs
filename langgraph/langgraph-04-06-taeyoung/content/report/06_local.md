## §5. 로컬에서 돌려보고, 생태계 근황

<div class="section-summary">
  <div class="section-summary__kicker">한 줄 요약</div>
  <div class="section-summary__body"><code>langgraph dev</code> 한 줄로 인메모리 서버를 띄워 Studio·SDK·REST 로 테스트한다(개발용). 그리고 LangChain/LangGraph 생태계는 v1 정식 이후 빠르게 움직인다 — 발표 시점의 changelog 를 한 번 확인하라.</div>
</div>

### 5.1. §1\~§4 에서 만든 그래프를, 이제 실제로 띄운다

`app = workflow.compile(...)` 까지 했다면, 이걸 로컬 서버로 올려 Studio 로 디버깅할 수 있다. 공식 **Run a local server** 가이드의 흐름은 일곱 단계다.[^2]

> 한 가지 연결고리: `langgraph dev` 는 코드 안의 `app` 변수를 자동으로 찾아 띄우는 게 아니라, 프로젝트의 `langgraph.json` 에 등록된 **그래프 경로와 assistant 이름** 을 보고 서버를 올린다(템플릿이 이 파일을 만들어 준다). 아래 SDK/REST 예의 `"agent"` 가 바로 그 assistant 이름이다. §1\~§4 의 그래프를 직접 서빙하려면 `app` 이 있는 모듈 경로를 `langgraph.json` 에 등록하면 된다.

![langgraph dev 로컬 토폴로지](figs/fig09_local_topology.svg)
<small>Figure — `langgraph dev` 는 `langgraph.json` 에 등록된 그래프를 인메모리 서버(:2024)로 띄우고, Studio·SDK·REST 가 거기에 붙는다.</small>

**① LangGraph CLI 설치** (Python ≥ 3.11)

```bash
pip install -U "langgraph-cli[inmem]"
```

**② 앱 생성** — 템플릿에서 단일 노드 앱을 만들어 확장한다

```bash
langgraph new path/to/your/app --template new-langgraph-project-python
```

> 템플릿을 지정하지 않고 `langgraph new` 만 치면 사용 가능한 템플릿 메뉴가 뜬다.

**③ 의존성 설치** (edit 모드 — 로컬 변경이 서버에 바로 반영)

```bash
pip install -e .
```

**④ `.env` 작성** — `.env.example` 을 복사해 키를 채운다

```text
LANGSMITH_API_KEY=lsv2...
```

**⑤ 서버 실행**

```bash
langgraph dev
```

출력 예:

```text
   Welcome to
   ╦  ┌─┐┌┐┌┌─┐╔═╗┬─┐┌─┐┌─┐┬ ┬
   ║  ├─┤││││ ┬║ ╦├┬┘├─┤├─┘├─┤
   ╩═╝┴ ┴┘└┘└─┘╚═╝┴└─┴ ┴┴  ┴ ┴

 - 🚀 API:       http://127.0.0.1:2024
 - 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
 - 📚 API Docs:  http://127.0.0.1:2024/docs
```

> **중요**: `langgraph dev` 는 **인메모리 모드** 다. 개발·테스트용이며, 운영에서는 영속 저장소를 갖춘 **LangSmith Deployment** 로 배포해야 한다.

**⑥ Studio 로 디버깅** — 출력의 Studio URL 로 접속해 그래프를 시각화하고, 단계별로 실행하며, 특정 단계의 입력을 수정해 즉시 반응을 본다. (Safari 는 완전 호환되지 않음 → Chrome·Brave 등 Chromium 계열 권장)

**⑦ API 테스트** — Python SDK(async/sync) 또는 REST 로 호출

```python
# async SDK
from langgraph_sdk import get_client
import asyncio

client = get_client(url="http://localhost:2024")

async def main():
    async for chunk in client.runs.stream(
        None,            # 스레드 없는 실행
        "agent",         # langgraph.json 에 정의된 assistant 이름
        input={"messages": [{"role": "human", "content": "What is LangGraph?"}]},
    ):
        print(f"Receiving new event of type: {chunk.event}...")
        print(chunk.data)

asyncio.run(main())
```

```bash
# REST
curl -s --request POST \
    --url "http://localhost:2024/runs/stream" \
    --header 'Content-Type: application/json' \
    --data '{
        "assistant_id": "agent",
        "input": {"messages": [{"role": "human", "content": "What is LangGraph?"}]},
        "stream_mode": "messages-tuple"
    }'
```

여기서 우리가 §1\~§4 에 만든 노드·엣지·State·checkpointer 가, `langgraph dev` 라는 한 줄과 Studio 라는 눈으로 실제 손에 잡힌다.

### 5.2. 생태계 근황 — Changelog 가 말해 주는 것

LangChain/LangGraph 의 changelog 는 **얼마나 빠르게 움직이는지** 를 보여 준다. 이론 발제에서 중요한 건 개별 릴리스 암기가 아니라 "이 생태계는 분기마다 바뀐다" 는 감각이다. 아래 표는 [공식 changelog](https://docs.langchain.com/oss/python/releases/changelog) 를 **2026년 5월 기준** 으로 추린 것이다 — v1 정식 이후에도 분기마다 굵직한 변화가 이어진다.[^3]

**표 7. 주요 릴리스 — LangChain Changelog (2026-05 기준)**

| 시점 | 릴리스 | 핵심 |
|---|---|---|
| 2025-10-20 | **`langchain` · `langgraph` v1.0.0** | 두 패키지의 **1.0 정식**. 릴리스 노트·마이그레이션 가이드 제공 |
| 2025-11-25 | `langchain` v1.1.0 | **Model profiles**(`.profile`), 요약·재시도·콘텐츠 검열 **미들웨어**, structured output `ProviderStrategy` |
| 2025-12-08 | `langchain-google-genai` v4.0.0 | Google 통합 GenAI SDK 로 재작성 (Gemini API + Vertex AI 동일 인터페이스) |
| 2025-12-15 | `langchain` v1.2.0 | `create_agent` 의 도구 `extras` 속성, `response_format` strict 스키마 |
| 2026-03-10 | `langgraph` v1.1.0 | **타입 세이프 스트리밍·invoke** (`version="v2"`), Pydantic·dataclass 강제변환, time-travel 버그 수정 |
| 2026-05-12 | `langgraph` v1.2.0 | **노드별 에러 핸들러**(`error_handler=`)·**per-node 타임아웃**, graceful shutdown, v3 이벤트 스트리밍 |

> changelog 에는 **RSS 피드** 가 있어 Slack·이메일·Discord 봇 등에 연동할 수 있다. 빠르게 바뀌는 생태계를 따라가는 가장 싼 방법이다.

특히 **미들웨어** 흐름(요약·재시도·콘텐츠 검열)은 우리가 DeepAgent 에서 본 "내장 능력을 미들웨어로 얹는다" 는 패턴과 같은 줄기다. 큰 방향으로는 — LangGraph 의 노드·State 모델 위에 LangChain 이 이런 미들웨어를 쌓고, 그 위에 deepagents 가 4대 능력을 얹었다고 — 이해할 수 있다(이는 changelog 가 명시하는 사실이라기보다 계층 구조에 대한 해석이다).

또 하나 눈여겨볼 흐름은 `langgraph` 코어 자체의 진화다. 2026-05 의 **`langgraph` v1.2.0** 은 노드에 `error_handler=` 와 `timeout=` 을 직접 지정하는 **노드별 에러 핸들러·타임아웃** 을 정식 도입했다 — §3\~§4 에서 "에러를 흐름의 일부로" 다루던 패턴이 이제 프레임워크 1급 기능으로 들어온 셈이다. 즉 이 교안의 사고법(노드 단위로 실패를 가두고 정책을 건다)은 최신 릴리스가 가는 방향과 같은 줄기다.
