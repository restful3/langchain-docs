# 디자인 — LangGraph 04~06 발표 자료

> 흐름 채택: **세 문서 통합 → 핵심 주제 5개 추출** · 청중: DeepAgent 스터디 수료자 · 톤: 격식·캐주얼 중간
> 우선 산출물: **상세 교과서(textbook.md)** · 슬라이드·스크립트·PDF 는 후속

---

## 1. 청중 프로파일

| 항목 | 내용 |
|---|---|
| 인원 | ~11명 (스터디 멤버) |
| 전제 지식 — 강함 | LangChain `ChatModel` / 도구 호출 / `create_agent` 사용 경험. DeepAgent 4주 수료 |
| 전제 지식 — 보통 | "Deep Agent 는 LangGraph 위에 얹혀 있다" 를 반복해 들음 — 이름은 익숙하나 내부는 미경험 |
| 전제 지식 — 약함 | LangGraph 의 노드/엣지/State 모델, `interrupt()`/checkpointer, 로컬 실행 |
| 기대 | DeepAgent 의 엔진이던 LangGraph 자체를 처음으로 직접 여는 청사진 |
| 시간 제약 | 발표 17분 + Q&A 3분 = 20분 (이론 발제) |
| 톤 | 전문 용어 정확히, 비유로 풀어줌 |

**훅**: "지난 스터디 내내 깔개로만 불리던 LangGraph 를, 오늘 직접 엽니다."

---

## 2. 학습 목표

| # | 학습 목표 | 검증 가능한 행동 |
|:---:|---|---|
| L1 | "왜 그래프인가" 로 LangGraph 를 설명하고 **노드·엣지·State** 세 요소를 매칭 | 세 단어와 각 역할("작업 / 다음 결정 / 공유 메모리")을 말할 수 있음 |
| L2 | 업무를 노드로 분해하고 **설계 5단계** 를 적용 | 임의 업무를 받아 노드 후보로 쪼개고 스텝 유형(LLM/Data/Action/User)을 분류 |
| L3 | State 에 무엇을 넣을지(**raw 원칙**) 판단 + **4가지 에러** 를 전략에 매칭 | "파생 가능하면 저장 안 함" 기준과 retry/loop-back/interrupt/bubble-up 구분 |
| L4 | `interrupt()`·checkpointer 로 **HITL·내구성 재개** 를 설명 | 일시정지→`Command(resume=...)` 흐름과 thread_id 의 역할을 풀 수 있음 |
| L5 | `langgraph dev` 로 **로컬 서버를 띄우고 Studio 로 디버깅** | 포트 2024 인메모리 서버·Studio·SDK/REST 테스트 경로를 안내 |

---

## 3. 교과서 목차 (핵심 주제 5개 — 04~06 통합)

worked example = **06 의 고객지원 이메일 에이전트** 를 §1~§4 에 관통.

```text
§0  들머리 — "LangGraph 위에 얹혀 있다" 의 그 LangGraph        (0.5p)
§1  왜 그래프인가 — 사고 모델               [핵심주제1]  (2.0p)  ← 06
§2  에이전트를 설계하는 5단계               [핵심주제2]  (4.0p)  ← 06
§3  State 설계 & 에러를 흐름의 일부로        [핵심주제3]  (3.0p)  ← 06
§4  사람 개입과 내구성                       [핵심주제4]  (2.5p)  ← 06
§5  로컬에서 돌려보고, 생태계 근황            [핵심주제5]  (2.5p)  ← 04+05
§6  다음으로 가는 다리 + 한 문장 정리         (0.5p)
부록 A 용어집 · B 참고(원문 04~06 매핑)
합계: 약 15~17p
```

**핵심 주제 ↔ 5단계 매핑** (5단계가 §2~§4 에 걸침)

| 주제 | 절 | 06 의 5단계 |
|---|---|---|
| 1 사고 모델 | §1 | (도입) 노드·엣지·State |
| 2 설계 5단계 | §2 | Step 1 분해 · Step 2 스텝 유형 |
| 3 State·에러 | §3 | Step 3 State 설계 · Step 4(에러 전략) |
| 4 사람 개입·내구성 | §4 | Step 4(interrupt) · Step 5 연결·compile |
| 5 실행·근황 | §5 | (04 local server + 05 changelog) |

---

## 4. 핵심 메시지 (한 문장)

> **LangGraph 는 에이전트를 노드·엣지·State 의 그래프로 모델링하는 런타임이다. 설계는 "업무를 노드로 분해 → State 설계 → 노드 구현 → 연결" 의 사고법으로 하고, `interrupt()`·checkpointer 로 사람 개입과 장애 재개를 1급으로 다룬다.**

- §0 마지막 줄에 박고, §6 정리에서 한 번 더 (수미상관).

---

## 5. 포함 / 제외 정책

### 포함

- 노드·엣지·State 모델 + "왜 그래프인가"
- 설계 5단계 (이메일 에이전트 예제 관통)
- State raw 저장 원칙 + 4가지 에러 전략
- `interrupt()`·`Command(resume)`·checkpointer·HITL·내구성·노드 granularity
- `langgraph dev`·Studio·SDK/REST 로컬 실행
- changelog — v1 정식 + 미들웨어 흐름 (생태계 근황)

### 제외 (langgraph 다른 문서로 미룸)

| 주제 | 비고 |
|---|---|
| Graph API 전체 레퍼런스 (22·23 문서) | "노드/엣지 정의" 까지만 |
| Functional API (24·25) | 이름만 언급 |
| Persistence/Memory 깊이 (08·13) | checkpointer 개념까지만 |
| Subgraphs (14) | "다음으로" 에서 언급 |
| Pregel 런타임 내부 (26) | "슈퍼스텝" 한 줄 |
| 운영 배포 (LangSmith Deployment) | "인메모리는 개발용" 경고까지만 |

**원칙**: 04~06 의 범위를 지킨다. 깊이 들어갈 주제는 langgraph 다른 문서 발제자에게 양보.

---

## 6. 작성 원칙 (글로벌 CLAUDE.md 준수)

- 각 절은 **한 줄 요약** 으로 시작
- 코드 블록은 모두 언어 식별자 (` ```python `, ` ```bash `, ` ```text `, ` ```mermaid `)
- 코드는 06 원문과 sync (후속 `scripts/*.py` 작성 시 본문과 일치 유지)
- `**용어(English)**` 뒤 한글 오면 공백 1칸
- 본문 `~` 는 `\~` 이스케이프 (HTML/코드 블록 안은 raw)
- 외부 인용은 footnote `[^N]` → 부록 B

---

## 7. 산출물 단계

- **지금**: `archives/meta/{BRAINSTORM,DESIGN,STATUS}.md` + `content/textbook.md` + `content/sections.yaml` + `README.md`
- **후속(별도 지시)**: `content/figs/*.svg`, `scripts/*.py`, `slides.md`, PDF 빌드(chromedriver 설치 후)
