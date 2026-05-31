## 부록 A. 용어집

**표 8. 용어집**

| 용어 | 뜻 |
|---|---|
| **노드(Node)** | State 를 받아 업데이트를 돌려주는 함수. 한 가지 일을 한다 |
| **엣지(Edge)** | 한 노드 다음에 어느 노드로 갈지. `add_edge` 또는 노드 안의 `Command(goto=...)` |
| **상태(State)** | 모든 노드가 공유하는 메모리. 보통 `TypedDict` 로 스키마 정의 |
| **`StateGraph`** | 노드·엣지·State 로 그래프를 조립하는 빌더 |
| **`Command`** | 노드의 반환값. State 업데이트(`update`)와 다음 행선지(`goto`), 재개(`resume`)를 함께 표현 |
| **`interrupt()`** | 노드를 일시정지하고 State 를 저장한 뒤 외부 입력을 기다림. 재개 시 앞 코드가 재실행되므로 비멱등 side effect 보다 앞에 둠 |
| **checkpointer** | 노드/슈퍼스텝 경계의 State 스냅샷을 저장하는 레이어. `MemorySaver` 는 인메모리(개발·데모)용, 프로세스 재시작 후 장기 재개는 Postgres 등 durable 백엔드 필요 |
| **`thread_id`** | 한 실행 세션의 식별자. 체크포인트가 State 를 묶는 기준 |
| **`RetryPolicy`** | 노드 단위 재시도 정책 (일시적 오류용) |
| **내구성 있는 실행(Durable Execution)** | 노드/슈퍼스텝 경계 체크포인트로 중단 후 그 자리에서 재개 (장기 재개는 durable checkpointer 전제) |
| **`langgraph dev`** | 로컬 인메모리 API 서버(포트 2024). 개발·테스트용 |
| **Studio** | 로컬 서버에 붙어 그래프를 시각화·디버깅하는 UI |

## 부록 B. 원문 출처 매핑

**표 9. 절별 1차 출처 — LangChain 공식 문서**

| 절 | 공식 문서 | URL |
|---|---|---|
| §1\~§4 | Thinking in LangGraph | https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph |
| §5.1 | Run a local server | https://docs.langchain.com/oss/python/langgraph/local-server |
| §5.2 | Changelog | https://docs.langchain.com/oss/python/releases/changelog |
