# 실습 — 평균회귀 트레이딩 에이전트

리포트 **"노드·엣지·State 편"** §3.4 가 약속한 _"실행 가능한 전체본"_ 입니다.
본문 코드는 핵심 패턴만 보인 축약본이었고, 여기서는 7개 노드 전부와
checkpointer·interrupt/resume 까지 채워 **그대로 돌아가게** 했습니다.

> ⚠️ **교육용 예제입니다.** 실제 매매·브로커 연동이 아니라 dry-run 으로 LangGraph
> 흐름(노드·엣지·State·interrupt)만 보여 줍니다.

## 무엇을 보여 주나

리포트의 5단계 설계가 한 그래프에서 어떻게 도는지를 세 시나리오로 보여 줍니다.

- **시나리오 A** — 저평가 되돌림(long): `check_risk`(한도 OK) → `size_position` → `approve_order`(승인) → `place_order`
- **시나리오 B** — 급등 과열(short, conviction critical): `approval_required` 플래그 → 리스크·사이징 후 `approve_order` 에서 사람이 수량을 줄여 승인
- **시나리오 C** — 평탄: 진입 임계값 미만 → 무거래로 종료(interrupt 없음)

A·B 는 `interrupt()` 로 **주문 전송 직전** 멈췄다가 `Command(resume=...)` 로 멈춘 지점부터 재개됩니다.

## 실행

API 키 없이 바로 됩니다 (키가 없으면 신호 근거를 규칙 문구로 대체). 방향(롱/숏)은 키 유무와 무관하게 **언제나 결정론적 z-score** 가 정합니다.

```bash
cd scripts

# 저장소에 이미 있는 venv (langgraph 설치됨) 사용
../../../deep-agents/.venv/bin/python trading_agent.py        # 데모 3종
../../../deep-agents/.venv/bin/python trading_agent.py viz    # 그래프 구조(Mermaid)
```

실제 LLM 으로 돌리려면:

```bash
cp .env.example .env        # OPENAI_API_KEY 채우기
```

## 주피터 노트북 — `trading_agent_workshop.ipynb`

리포트 서사 + 스크립트 코드를 합쳐 **위에서 아래로 실행**하며 트레이딩 에이전트를 완성하는 핸즈온 노트북입니다(19셀). 분해 → State → 노드+에러4전략 → 그래프 연결 → 그래프 그림(Mermaid PNG) → interrupt/resume 데모 → 정리 → `langgraph dev` 안내 순.

```bash
# JupyterLab 에서 열고 커널은 'LangGraph (deep-agents venv)' 선택
# (CLI 로 한 번에 실행·검증하려면)
nb execute trading_agent_workshop.ipynb --start 3 --end 16 -k langgraph-venv --allow-errors
```

> 셀이 langgraph 를 쓰므로 **`langgraph-venv` 커널**(= `deep-agents/.venv`)이 필요합니다. 등록돼 있지 않으면:
> `deep-agents/.venv/bin/python -m ipykernel install --user --name langgraph-venv --display-name "LangGraph (deep-agents venv)"`
> 맨 위 `%pip install` 셀을 한 번 돌리면 다른 커널에서도 됩니다.

## 단계별 실습 — `steps/`

리포트의 5단계 흐름을 하나씩 쌓아가는 progressive 버전입니다. 각 파일은 **독립 실행 가능**하며, 개념을 하나씩만 추가합니다. 순서대로 읽으며 돌려 보세요.

| 파일 | 리포트 | 무엇을 배우나 |
|---|---|---|
| `01_decompose.py` | §2 | 노드=함수, 그래프 컴파일·실행, 고정 엣지 |
| `02_state.py` | §3.1-3.2 | State 는 raw 신호 dict, 포맷은 노드에서 온디맨드 |
| `03_routing.py` | §3.4·§4.2 | 라우팅은 노드 안 `Command(goto)`, 엣지는 최소 (리스크 차단 분기 포함) |
| `04_errors.py` | §3.3 | 에러 4전략 (재시도·되돌아오기·일시정지·띄워보내기) — 전부 실제로 동작 |
| `05_hitl.py` | §4 | `interrupt` + checkpointer + resume = 완성본(부모 `trading_agent.py` 그래프 재사용) |

```bash
cd scripts/steps
../../../../deep-agents/.venv/bin/python 01_decompose.py   # 01 → 05 순서로
```

> `trading_agent.py` = 완성 전체본(한 파일에 7노드 전부),  `steps/` = 그 완성본에 이르는 학습용 점진 빌드.
> `04_errors.py` 만 §3.3 ②(loop-back)를 포함합니다 — 트레이딩 주 경로엔 없는 도구 루프 패턴이라 여기서 따로 보입니다.

## §5 — `langgraph dev` 로 Studio 에서 보기

`langgraph.json` 이 이 폴더의 `graph` 변수를 가리킵니다(assistant 이름 `trading_agent`).

```bash
pip install -U "langgraph-cli[inmem]"
langgraph dev               # http://127.0.0.1:2024 · Studio URL 출력
```

Studio 에서 `approve_order` 의 interrupt 를 눈으로 보고, 주문을 승인/수정해 재개해 볼 수 있습니다.
(`langgraph dev` 는 인메모리 개발 모드 — 운영은 영속 저장소를 갖춘 배포가 필요합니다.)

## 리포트 절 → 코드 매핑

| 리포트 | 코드 위치 |
|---|---|
| §3.1 State 스키마 | `TradingAgentState` · `SignalDecision` |
| §2.2 네 가지 스텝 유형 | 각 노드 docstring 의 `[유형]` 태그 |
| §3.3 ① 일시적 오류 → 재시도 | `fetch_market_data` 의 `RetryPolicy` |
| §3.3 ③ 사용자 수정 → 일시정지 | `approve_order` 의 `interrupt()` |
| §3.3 ④ 예상치 못한 오류 → 띄워보내기 | `place_order` 의 `raise` |
| §4.2 노드 연결 + checkpointer | `build_graph()` |
| §4.3 interrupt → resume | `run_demo()` |
| §5 `langgraph dev` | `langgraph.json` + 모듈 레벨 `graph` |

> §3.3 ② (LLM 복구 가능 — State 에 에러 저장 후 되돌아오기) 는 도구 실행 에이전트의
> `agent ↔ run_indicator` 루프 패턴이라 이 트레이딩 그래프의 주 경로에는 없습니다.
> `steps/04_errors.py` 의 별도 데모를 참고하세요.
