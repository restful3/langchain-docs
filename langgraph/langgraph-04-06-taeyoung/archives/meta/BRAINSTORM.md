# 발표 브레인스토밍 — LangGraph 04~06 / 태영

> 20분 / 이론 발제 / Run a local server · Changelog · Thinking in LangGraph

---

## 1. 청중과 포지션

- **청중**: 스터디 멤버. DeepAgent 4주를 거치며 **"Deep Agent 는 LangGraph 위에 얹혀 있다"** 를 반복해 들음.
- **포지션**: 그 "깔개" 였던 LangGraph 를 처음으로 직접 여는 발제. 이후 langgraph 다른 문서(Graph API, Persistence, Subgraphs…) 발제의 공통 출발점.
- 핵심 질문: *"내 발표가 끝났을 때 청중이 한 문장으로 뭐라고 답할 수 있어야 하나?"*
  - 답: "LangGraph = 에이전트를 **노드·엣지·State 의 그래프** 로 모델링하는 런타임. 업무를 노드로 분해하고 State 로 잇는다."

---

## 2. 문서 3개의 성격 차이 (설계상 핵심 문제)

| 문서 | 성격 | 분량 | 발표 무게 |
|---|---|---|---|
| 04 Run a local server | 실행 How-to | 5.5K | 보조 (실습 다리) |
| 05 Changelog | 릴리스 로그 | 4.4K | 가벼움 (맥락 한 장) |
| 06 Thinking in LangGraph | 설계 사고법 | 24.7K | **핵심** |

→ 문서 순서(04→05→06)대로 가면 changelog 가 가운데 끼어 흐름이 끊긴다.
→ **채택**: 세 문서를 합쳐 **핵심 주제 5개** 를 뽑고, 06 을 개념 축으로, 04+05 를 §5(실행·근황)로 묶는다.

---

## 3. 다섯 페르소나 관점

- **(a) 교육자**: 추상 그래프를 **이메일 고객지원 에이전트** 라는 하나의 worked example 로 관통. 06 이 이미 이 예제를 끝까지 끌고 가므로 그대로 활용.
- **(b) 아키텍트**: "노드는 작업, 엣지는 다음 결정, State 는 공유 메모리" 3분할을 발표의 시각적 앵커로 반복.
- **(c) 실무자**: §5 의 `langgraph dev` → Studio → SDK/REST 로 "내가 만든 그래프를 어떻게 띄우나" 를 손에 쥐어 줌.
- **(d) 회의론자**: "왜 그냥 함수로 안 짜고 그래프로 쪼개나?" → 답: 스트리밍 진행상황·내구성 재개·단계별 디버깅 (06 의 node granularity 절).
- **(e) 스토리텔러**: "DeepAgent 가 얹혀 있던 그 엔진을 오늘 직접 분해한다" 는 수미상관.

---

## 4. 빠뜨리면 안 되는 포인트

- [ ] 노드·엣지·State 세 요소 + 각 역할
- [ ] 설계 5단계 (분해 → 스텝 유형 → State → 노드 → 연결)
- [ ] State 는 **raw 데이터** 저장, 프롬프트는 노드에서 온디맨드 포맷
- [ ] 4가지 에러 전략: retry / loop-back / `interrupt()` / bubble-up
- [ ] `interrupt()` 는 노드에서 **맨 먼저** 호출 (재개 시 앞 코드 재실행)
- [ ] `Command(goto=...)` 로 라우팅을 노드 안에 두니 엣지는 최소
- [ ] checkpointer + `thread_id` 로 일시정지·재개·타임트래블
- [ ] async durability — 체크포인트는 백그라운드, 노드 많아도 느려지지 않음
- [ ] `langgraph dev` = 인메모리(개발용), 운영은 LangSmith Deployment
- [ ] changelog: v1.0 정식(2025-10) + 미들웨어 흐름

---

## 5. 데모/코드

- 라이브 데모 대신 **06 의 이메일 에이전트 코드** 를 본문 코드 블록으로 분해.
- 후속으로 `scripts/` 에 실행 가능한 이메일 에이전트 예제 분리 예정 (이번 단계 제외).

---

## 6. 표기/용어

- LangGraph / LangChain / LangSmith — 한국어로 풀지 않음
- 노드(Node) / 엣지(Edge) / 상태(State) — 한국어 + 영문 병기
- `interrupt()` / `Command` / checkpointer / `StateGraph` — 코드폰트 고정
- 사람 개입(Human-in-the-loop, HITL) / 내구성 있는 실행(Durable Execution)
