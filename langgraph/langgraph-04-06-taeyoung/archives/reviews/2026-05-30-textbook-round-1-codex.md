# LangGraph 상세 교과서 리뷰 — round 1

검토 대상: `content/01_textbook.md`  
대조 자료: `06-thinking-in-langgraph.md`, `04-local-server.md`, `05-changelog.md`, 현재 LangChain Python changelog

## Critical

없음.

## Major

### 1. 위치: §4.2~§4.3, §4.4, 부록 A 근처 (416~417, 454, 460, 613~617)

**문제**  
`MemorySaver()` 를 사용한 예제 직후에 "며칠 뒤에 재개", "영속성", "내구성 있는 실행"을 거의 같은 의미로 설명하고 있어, 독자가 `MemorySaver` 만으로 프로세스 재시작 이후의 장기 재개가 된다고 오해할 수 있습니다. `thread_id` 는 체크포인트를 식별·조회하는 키이지 저장소 자체가 아니며, `MemorySaver` 는 데모/개발용 인메모리 checkpointer 입니다. 실제로 "며칠 뒤" 재개를 보장하려면 Postgres 같은 durable checkpointer 또는 LangGraph Platform/LangSmith Deployment 계열의 영속 저장소가 필요합니다.

**권장 수정**  
`MemorySaver` 예제 주변에 "이 코드는 한 프로세스 안에서 interrupt/resume 흐름을 보여 주기 위한 데모"라고 명시하세요. 454줄은 "같은 checkpointer backend 에 checkpoint 가 남아 있고 같은 `thread_id` 로 호출하면 재개된다"로 바꾸는 편이 정확합니다. 부록의 `checkpointer` 정의도 "`MemorySaver` 는 인메모리 예시, 운영/장기 재개는 durable backend 필요"로 분리하세요.

### 2. 위치: §4.1 및 부록 A 근처 (350, 356, 362~365, 612)

**문제**  
"`interrupt()` 가 노드에서 맨 먼저 호출되어야 한다"는 설명과 코드가 서로 충돌합니다. 코드에서는 `classification = state.get(...)` 로 state 를 읽은 뒤 `interrupt()` 를 호출합니다. 더 중요한 기술 포인트는 "재개 시 interrupt 이전 코드는 다시 실행된다"는 점이며, 따라서 금지해야 할 것은 모든 코드가 아니라 외부 API 호출, DB write, 이메일 발송 같은 비멱등 side effect 입니다. 현재 표현은 너무 절대적이라 교육적으로 잘못된 규칙을 남길 수 있습니다.

**권장 수정**  
"`interrupt()` 는 가능하면 노드 앞쪽에 두고, 특히 비멱등 side effect 앞에 둔다. 재개 시 interrupt 이전의 순수 계산/State 읽기는 다시 실행된다"로 수정하세요. 350줄도 "`Command(resume=...)` 는 멈춘 노드를 다시 실행하고, 해당 `interrupt()` 호출이 resume 값을 반환하게 한다"처럼 설명하면 내부 동작과 더 잘 맞습니다.

### 3. 위치: §3.2~§4.3 코드 스니펫 전반 (202~218, 304~310, 390~451)

**문제**  
코드가 "실제 노드들"처럼 제시되지만 그대로 따라 치면 타입/정의 누락 문제가 생깁니다. `EmailAgentState` 는 기본 `TypedDict` 라 모든 키가 required 인데, 426~431줄의 `initial_state` 에는 `classification`, `search_results`, `customer_history`, `draft_response` 등이 없습니다. `messages: list[str] | None` 으로 선언해 놓고 `read_email` 은 `HumanMessage` 객체 리스트를 반환합니다. 또한 §4.2 의 그래프 조립 코드는 `search_documentation`, `bug_tracking`, `draft_response`, `send_reply` 를 등록하지만, 본문에는 이 함수들의 구현이 빠져 있습니다.

**권장 수정**  
스니펫의 목적을 하나로 정하세요. 실행 가능한 교안이라면 누락된 노드를 최소 구현으로 넣고, `TypedDict` 는 `NotRequired[...]` 또는 `total=False`/초기값 `None` 중 하나로 정리하세요. `messages` 는 범위를 줄이려면 아예 제거하거나, 메시지를 유지하려면 `list[HumanMessage]` 또는 LangGraph 메시지 reducer 를 소개하지 않는 선에서 `list[object]` 정도로 타입을 완화하세요. 실행용이 아니라면 "아래 코드는 핵심 패턴만 보이는 축약 코드"라고 명시해야 합니다.

### 4. 위치: §5.1 로컬 서버 설명 (482~545)

**문제**  
"`app = workflow.compile(...)` 까지 했다면, 이걸 로컬 서버로 올려"라고 설명하지만, `langgraph dev` 는 임의의 Python 변수 `app` 을 자동으로 찾아 올리는 것이 아니라 프로젝트의 `langgraph.json` 에 등록된 assistant/graph 경로를 기준으로 서버를 띄웁니다. 545줄에는 `"agent"` 가 `langgraph.json` 에 정의된 assistant 이름이라고 나오지만, 앞 단계에서는 `langgraph.json` 작성/확인 절차가 빠져 있어 §1~§4 코드와 §5.1 실행 사이가 끊깁니다.

**권장 수정**  
템플릿 사용 시 `langgraph.json` 이 생성되며, 여기의 graph 경로와 assistant 이름이 SDK/REST 의 `"agent"` 와 연결된다고 한 단락 추가하세요. §1~§4 의 그래프를 직접 서빙하려면 `app` 이 위치한 모듈 경로를 `langgraph.json` 에 등록해야 한다는 점도 짧게 넣으면 실습 실패를 줄일 수 있습니다.

### 5. 위치: §5.2 changelog 표와 설명 (570~578)

**문제**  
제공된 `05-changelog.md` 기준으로 2025-10-20, 2025-11-25, 2025-12-08, 2025-12-15 항목은 대체로 정확합니다. 다만 현재 발표일이 2026-05-30 이라면 "발표 시점의 최신을 확인하라"는 메시지와 표가 어긋납니다. 현재 LangChain Python changelog 에는 2026-03-10 `langgraph` v1.1.0, 2026-05-12 `langgraph` v1.2.0 및 `langchain` v1.3.0, `deepagents` v0.6.0 항목이 추가되어 있습니다. 참고: https://docs.langchain.com/oss/python/releases/changelog

**권장 수정**  
둘 중 하나로 정리하세요. 원문 05만 통합하는 문서라면 표 제목을 "원문 05 기준 changelog 발췌"로 바꾸고 최신성 주장을 낮추세요. 실제 발표용 최신 동향까지 담을 목적이라면 2026-03-10 `langgraph` v1.1.0(type-safe streaming/invoke), 2026-05-12 `langgraph` v1.2.0(node timeout/error handler/graceful shutdown/DeltaChannel/streaming v3) 정도를 추가하는 것이 맞습니다.

## Minor

### 6. 위치: §1.2, §2.1, §4.2 근처 (51, 120, 387~420)

**문제**  
"결정은 각 노드 안에서 일어난다", "라우팅은 노드 안"이라는 표현이 이 예제의 선택인지 LangGraph 전체의 원칙인지 구분되지 않습니다. LangGraph 에는 `Command(goto=...)` 외에도 conditional edges 등 다른 라우팅 방식이 있습니다. 원문 06의 예제는 노드 내부 라우팅을 강조하지만, 교안 작성 방침상 Graph API 전체를 제외하기로 했기 때문에 더더욱 범위 한정이 필요합니다.

**권장 수정**  
"이 교안의 고객지원 예제에서는 `Command(goto=...)` 로 라우팅한다" 또는 "conditional edges 는 이번 범위 밖"이라고 한 번 못박으세요. 이렇게 하면 범위를 지키면서도 LangGraph 자체를 과도하게 단순화하지 않습니다.

### 7. 위치: §0 및 작성 방침과의 정합성 (15)

**문제**  
"Google 의 Pregel 알고리즘에 기반한 런타임"이라는 설명은 넓게는 맞는 배경지식이지만, 원문 04~06 의 핵심 범위에는 없고 사용자가 의도적으로 Pregel 내부를 제외했다고 밝힌 범위와도 살짝 어긋납니다. 초반에 이 문장이 나오면 청중이 내부 실행 모델로 관심을 돌릴 수 있습니다.

**권장 수정**  
발표용 교안에서는 삭제하거나 각주 수준으로 낮추세요. 본문은 "상태를 가진 multi-step agent workflow 를 그래프로 실행하는 런타임" 정도로 충분합니다.

### 8. 위치: §3.3 LLM 복구 가능 에러 예시 (245~260)

**문제**  
예시는 `ToolError` 를 state 에 저장하고 `agent` 로 되돌리는 패턴을 보여 주지만, 이 방식이 유효하려면 `agent` 노드가 `tool_result` 의 에러 문자열을 실제 프롬프트/메시지 컨텍스트로 읽어 재계획해야 합니다. 현재 설명만으로는 "state 에 에러를 저장하면 LangGraph/LLM 이 자동으로 알아서 회복한다"는 인상을 줄 수 있습니다.

**권장 수정**  
"되돌아간 LLM 노드가 이 필드를 읽도록 프롬프트/메시지 구성이 되어 있어야 한다"는 한 문장을 추가하세요. 가능하면 `tool_result` 보다는 `tool_error` 또는 `last_error` 처럼 에러임이 드러나는 필드명을 쓰는 편이 교육적으로 명확합니다.

### 9. 위치: §3.4, §4.1 코드 (330~343, 362, 375~377)

**문제**  
`state.get('classification', {})` 는 키가 없을 때만 `{}` 를 반환합니다. State 에 `classification=None` 이 들어 있는 경우에는 이후 `classification.get(...)` 호출에서 오류가 납니다. 타입 선언이 `EmailClassification | None` 이므로 코드와 타입이 맞지 않습니다.

**권장 수정**  
`classification = state.get("classification") or {}` 로 바꾸세요. `draft_response` 등 다른 nullable 필드도 같은 패턴을 쓰면 스니펫의 타입 일관성이 좋아집니다.

### 10. 위치: §4.4 async durability 설명 (460~464)

**문제**  
"노드 경계마다 체크포인트"라는 표현은 단일 선형 그래프를 설명할 때는 이해하기 쉽지만, LangGraph 실행 모델에서는 보통 superstep/checkpoint 단위로 설명하는 편이 더 정확합니다. 부록 A 에는 "매 슈퍼스텝"이라고 되어 있어 본문과 용어가 흔들립니다.

**권장 수정**  
본문의 설명도 "대체로 노드 실행 경계/슈퍼스텝 경계에서 checkpoint 가 생긴다" 정도로 맞추세요. 발표에서는 "재개 시 실패한 노드의 처음부터 다시 실행될 수 있다"는 실무적 결론을 강조하면 충분합니다.

### 11. 위치: §5.2 마지막 해석 문단 (581)

**문제**  
"LangGraph 의 노드·State 모델 위에 LangChain 이 이런 미들웨어를 쌓고, 그 위에 deepagents 가 4대 능력을 얹은 셈"이라는 문장은 교육적 연결로는 좋지만, `05-changelog.md` 에서 직접 말하는 사실은 아닙니다. 또한 LangChain middleware 와 Deep Agents 의 내부 구성을 한 문장으로 단정하면 구현 계층을 지나치게 단순화할 수 있습니다.

**권장 수정**  
"큰 방향으로는 ... 라고 이해할 수 있다"처럼 해석임을 드러내세요. changelog 사실과 발표자의 아키텍처 해석을 분리하면 정확성과 설득력이 모두 올라갑니다.

## Nit

### 12. 위치: §2.2 유형 표 (142~145)

**문제**  
이모지가 표의 빠른 인지에는 도움이 되지만, "상세 교과서" 톤에서는 시각적 강조가 약간 많습니다. 특히 PDF/프린트나 발표 보조자료로 쓰면 정렬이 깨질 수 있습니다.

**권장 수정**  
슬라이드에는 유지해도 좋지만 교안 본문에서는 이모지를 제거하거나 절 제목 수준에서만 쓰는 편이 더 차분합니다.

### 13. 위치: §5.1 REST 예시 (554~563)

**문제**  
REST 예시는 원문과 다르게 single quote JSON heredoc 없이 직접 문자열을 넣어 가독성은 좋아졌지만, 실제 shell 복사 실행 시 줄바꿈/따옴표 편집에 민감할 수 있습니다.

**권장 수정**  
실습용이면 `--data-raw '{ ... }'` 형태로 유지하거나, `jq`/heredoc 없이도 복사 가능한 한 가지 스타일로 통일하세요.

## 전반 평가

큰 흐름은 좋습니다. 원문 06의 "고객지원 이메일 에이전트"를 끝까지 끌고 가며 노드·엣지·State, 5단계 설계법, 4가지 에러 전략, `interrupt()`/checkpointer, local server, changelog 를 20분 발표용 보조 교안으로 재구성한 의도는 잘 살아 있습니다. 다만 현재 원고는 코드가 "실행 가능한 예제"처럼 보이는 부분과 "개념 축약"인 부분이 섞여 있어, LangGraph 를 처음 깊게 보는 청중에게 checkpointer 영속성, interrupt 재개 semantics, `langgraph dev` 설정, State 타입 설계에서 잘못된 기억을 남길 위험이 있습니다. 위 Major 항목을 먼저 고치고, "이 예제에서 택한 방식"과 "LangGraph 전체 기능"의 경계를 명확히 하면 기술 정확성과 교육적 완성도가 모두 크게 올라갑니다.
