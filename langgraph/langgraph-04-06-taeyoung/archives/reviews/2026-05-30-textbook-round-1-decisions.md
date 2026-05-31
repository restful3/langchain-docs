# Round 1 — 결정 및 변경 (Claude)

대상: `content/01_textbook.md` · Codex 리뷰: `2026-05-30-textbook-round-1-codex.md`

## ACCEPT (반영 완료, 11건)

| # | 항목 | 변경 |
|---|---|---|
| M1 | MemorySaver/thread_id/영속성 혼동 | §4.2 코드 뒤 "MemorySaver=인메모리 데모, 장기 재개는 durable backend" 콜아웃 추가. §4.3 thread_id 를 "체크포인트 식별 키", State 보존처는 checkpointer 로 정정. 부록 checkpointer·durable execution 정의 정정 |
| M2 | "interrupt() 맨 먼저" 과도 | §4.1 본문을 "비멱등 side effect 보다 앞에. 순수 계산/State 읽기는 재실행돼도 무방" 으로 정정. 코드 주석·부록 정의도 동일 |
| M3 | 코드가 실행 가능처럼 보임 | §3.4 앞에 "이하 코드는 축약본, 일부 노드 본문·타입 생략, 전체본은 scripts/" 콜아웃 |
| M4 | langgraph dev ↔ langgraph.json 단절 | §5.1 에 "app 변수 자동 탐색 아님 — langgraph.json 의 그래프 경로·assistant 이름 기준" 콜아웃 |
| M5 | changelog 최신성 | 표를 "원문 05(2025-12-15 시점) 발췌" 로 라벨, 공식 changelog 링크로 최신 확인 유도 (구체적 미검증 2026 항목은 미추가 → DEFER) |
| m6 | Command vs 조건부 엣지 범위 | §4.2 에 "add_conditional_edges 도 있으나 이 예제는 Command(goto), 조건부 엣지는 범위 밖" 명시 |
| m7 | Pregel 언급이 범위와 충돌 | §0 에서 Pregel 을 괄호 주석으로 경량화 |
| m8 | LLM 에러 회복 전제 | §3.3 ②코드 뒤 "되돌아간 노드가 에러 필드를 프롬프트로 읽어야 회복, 자동 아님; tool_error 명명 권장" 추가 |
| m9 | `state.get('classification', {})` None 버그 | `state.get('classification') or {}` 로 수정 |
| m10 | "노드 경계" vs "슈퍼스텝" 용어 불일치 | 본문·부록 모두 "노드/슈퍼스텝 경계" 로 통일 |
| m11 | §5.2 아키텍처 단정 | "해석임" 을 명시하는 표현으로 완화 |

## REJECT (미반영, 2건)

| # | 항목 | 사유 |
|---|---|---|
| n12 | §2.2 이모지 제거 | 본문 빠른 스캔에 유효하고 원문 06 과 일치. 전역 no-emoji 규칙은 SVG/슬라이드 시각자료 대상이지 교안 본문이 아님. §4.5 와의 일관성도 유지 |
| n13 | REST 예시 스타일 | 이미 단일따옴표 `--data '{...}'` 형태로 복사 안전. 원문의 escaped heredoc 보다 오히려 견고 |

## DEFER (보류, 1건)

| 항목 | 사유 · 처리 |
|---|---|
| M5 의 구체적 2026 릴리스 항목 (langgraph v1.1/v1.2, langchain v1.3, deepagents v0.6 등) | Codex 주장이나 원문 05·작성자 지식으로 검증 불가(지식 컷오프 2026-01). 잘못된 버전·날짜를 본문에 단정하면 정확성 훼손. → 표는 원문 기준으로 두고, 발표자가 발표 시점에 공식 changelog 에서 직접 확인하도록 링크로 안내. (사용자가 원하면 WebFetch 로 실값 확인 후 추가 가능) |

## 검증

- HTML 재빌드 성공 (49KB), 코드펜스 언어식별자 유지, 본문 미이스케이프 `~` 0건
