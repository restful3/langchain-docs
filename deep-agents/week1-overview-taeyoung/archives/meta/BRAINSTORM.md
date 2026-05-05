# 발표 브레인스토밍 — 1주차 / 태영

> 20분 / 첫 발제 / Overview · Quickstart · Customization · Models

---

## 1. 청중과 역할 재정의

- **청중**: 11명 스터디 멤버. LangChain/LangGraph 기초는 어느 정도 알지만 Deep Agent는 처음.
- **포지션**: 스터디 전체의 첫 발표 → "Deep Agent란 무엇인가"의 **공통 출발점**을 만들어야 함.
- **이후 9개 발제가 모두 이 발표 위에 쌓임** → 내가 깔지 않으면 다음 발제자가 매번 다시 깔아야 함.

핵심 질문: *"내 발표가 끝났을 때 청중이 한 문장으로 뭐라고 답할 수 있어야 하나?"*
**제안 답변**: "Deep Agent = LangGraph 위에 **계획 / 파일시스템 / 서브에이전트 / 장기메모리** 4대 기능을 내장해 둔 라이브러리. `create_deep_agent()` 한 줄로 시작한다."

---

## 2. 다섯 페르소나 관점

### (a) 교육자 — "어떻게 click 시킬까"
- 비유: Deep Agent = **"노트와 인턴을 가진 비서"**
  - 노트(Filesystem) + 할 일 목록(Planning) + 인턴(Subagents) + 일기장(Long-term Memory)
- Before/After: 같은 과제를 vanilla LLM 에이전트 vs Deep Agent로 보여주기

### (b) 아키텍트 — "시스템 위치"
- 스택 다이어그램: **LangGraph(엔진) → LangChain(도구·모델) → deepagents(이 발표) → LangSmith(관측·배포)**
- 03-customization의 Mermaid 다이어그램(`CoreConfig` + `Features`)을 **발표의 시각적 앵커**로 반복 사용

### (c) 실무자 — "내가 뭘 할 수 있나"
- "5줄짜리 마법" 코드 분해 (02-quickstart의 Step 4)
- `agent.invoke()` 한 번 호출에 백그라운드에서 일어나는 **5단계** (계획 → 검색 → 컨텍스트 관리 → 위임 → 종합) 시각화

### (d) 회의론자 — "왜 그냥 create_agent 안 쓰나"
- **이게 발표의 결정적 질문**. 명확히 답해야 함.
- 의사결정표:

  | 상황 | 권장 |
  |---|---|
  | 단일/짧은 작업, 컨텍스트 작음 | `create_agent` |
  | 커스텀 그래프 구조 필요 | LangGraph workflow |
  | **다단계 + 컨텍스트 큼 + 위임/메모리 필요** | **`create_deep_agent`** |

### (e) 스토리텔러 — "왜 이게 지금 나왔나"
- 기원: Claude Code · Deep Research · Manus → 같은 패턴이 반복됨 → **패키지화한 게 deepagents**
- 즉, "특정 회사의 비밀 공식이 오픈소스로 내려온" 느낌으로 포지셔닝

---

## 3. 발표 구성 — 3개 안

### 안 A: **문제 주도형 (추천)** — Socratic 흐름

| 분 | 단계 | 내용 |
|---:|---|---|
| 0:00–2:30 | Hook | "복잡한 리서치를 시키면 vanilla 에이전트는 왜 무너지는가" 한 장면 |
| 2:30–6:30 | 4대 초능력 | Planning · Filesystem · Subagents · Long-term Memory (도구 이름까지) |
| 6:30–11:30 | Quickstart | 5줄 코드 + invoke 시 백그라운드 5단계 |
| 11:30–16:30 | Customization | Mermaid 다이어그램 + Model/Prompt/Tools 다이얼 |
| 16:30–19:00 | When to use | 결정 표 + 다음 발제(컨텍스트/메모리/스킬) 다리 놓기 |
| 19:00–20:00 | Q&A | — |

**장점**: 시작에 "왜"가 있어서 몰입. 끝에 다음 발제와 연결.

### 안 B: 도큐먼트 순서형

Overview → Quickstart → Customization 순서대로. 안전하지만 평면적.

### 안 C: 데모 우선형

라이브로 1줄 실행 → 결과 보고 → 거꾸로 분해. 임팩트 크지만 라이브 데모 리스크.

---

## 4. 슬라이드/시각 아이디어 풀

| 시각 자료 | 용도 | 우선순위 |
|---|---|:---:|
| **스택 위치 다이어그램** (LangGraph→LangChain→deepagents→LangSmith) | 오프닝, 다음 발제 다리 | ⭐⭐⭐ |
| **Mermaid CoreConfig + Features 그림** (03 문서 그대로) | 커스터마이즈 섹션 앵커 | ⭐⭐⭐ |
| **invoke() 백그라운드 5단계 플로우** | "무슨 일이 일어났나" 슬라이드 | ⭐⭐⭐ |
| **결정 표** (create_agent vs LangGraph vs create_deep_agent) | 마무리 직전 | ⭐⭐⭐ |
| **비유 그림** (노트 + 할 일 + 인턴 + 일기장) | 4대 기능 도입부 | ⭐⭐ |
| **기원 타임라인** (Claude Code/Deep Research/Manus → deepagents) | Hook 또는 도입 | ⭐⭐ |
| **Before/After 코드** (vanilla agent vs deep agent) | 한 장면 비교 | ⭐ |

---

## 5. 데모/코드 아이디어

- **권장**: 라이브 데모 대신 **사전 캡처 스크린샷/녹화**
  - 이론 주차라 시간 변동 리스크를 피해야 함
  - 실습은 2주차 종훈S 담당 (10번 미정 시 그쪽이 커버)
- 핵심 데모 1컷: `agent.invoke()` 호출 시 `write_todos`로 todo가 생성되고, `internet_search`가 호출되고, `write_file`로 큰 결과가 오프로드되는 **로그 출력 캡처**
- 코드 분해 슬라이드 1장은 02-quickstart Step 4 그대로 사용 (이미 잘 쓰여 있음)

---

## 6. 빠뜨리면 안 되는 포인트

- [ ] Deep Agent는 **LangGraph 기반** (즉 그래프로 풀어 헤칠 수 있음 — 9주차 세훈/수경 발제로 이어짐)
- [ ] 4대 내장 기능과 **각 기능을 만드는 도구 이름** (`write_todos`, `read_file`/`write_file`/`edit_file`/`ls`, `task`, Store)
- [ ] **기본 시스템 프롬프트가 Claude Code에서 영감받음** — 청중이 흥미로워할 trivia
- [ ] **도구 호출(tool calling) 지원 모델 필수** — 잘못 고르면 안 됨
- [ ] **모델 지정 방법 2가지**: `"provider:model"` 문자열 vs LangChain 모델 객체
- [ ] **기본 모델은 `claude-sonnet-4-5-20250929`**
- [ ] `create_deep_agent` 시그니처에서 자주 쓰는 인자: `model`, `system_prompt`, `tools`, `subagents`, `backend`
- [ ] 4주 스터디 전체 흐름 미리 한 줄로 언급 (다음 발제자 주제 = 컨텍스트/메모리/스킬, 백엔드/샌드박스, …)

---

## 7. 표기/용어 일관성

- `deepagents` (라이브러리 이름, 소문자 + 코드 폰트)
- `Deep Agent` / `Deep Agents` (개념, 본문에선 통일)
- `create_deep_agent()` (함수, 코드 폰트)
- 한국어로 풀 때: "딥 에이전트" 보다는 **원어 그대로 "Deep Agent"** 권장 (자료 일관성)

---

## 8. 다음 발제와의 다리 (마지막 30초)

> "오늘은 Deep Agent의 **뼈대(어떻게 조립되는가)**를 봤습니다.
> 다음 발제부터는 살을 붙입니다 —
> **정훈**님이 컨텍스트와 메모리·스킬을,
> **종훈L**님이 실행 환경(백엔드·샌드박스·권한)을 다룹니다.
> 그리고 2주차에는 같은 코드를 직접 돌려봅니다."

---

## 9. 결정 필요 사항 (사용자 답변 요청)

- [ ] **슬라이드 도구**: PowerPoint / Keynote / Marp / Slidev / 라이브 마크다운?
- [ ] **데모 포함 여부**: 사전 녹화만? 라이브 시도? 코드 슬라이드만?
- [ ] **청중 가정**: LangChain/LangGraph를 어디까지 안다고 가정할 것인가? (모름 / 들어봄 / 써봄)
- [ ] **본인이 직접 deepagents를 돌려본 경험**: 있음 / 없음 → 자기 사례 인용 가능 여부
- [ ] **톤**: 격식 / 캐주얼 / 발표자 본인 스타일
- [ ] **3개 안 중 어떤 흐름**: A(문제 주도) / B(문서 순서) / C(데모 우선)?

---

## 10. 다음 액션 후보

1. 9번 답변 후 → 슬라이드 초안(키노트별 글머리·시각자료 매칭) 작성
2. invoke() 백그라운드 5단계 플로우를 Mermaid로 그려 두기
3. "결정 표 (create_agent vs LangGraph vs create_deep_agent)" 한 장 디자인
4. Quickstart 코드를 직접 1회 실행 → 로그 캡처 (데모 자료용)
5. 기원 타임라인(Claude Code → Deep Research → Manus → deepagents) 시각화
