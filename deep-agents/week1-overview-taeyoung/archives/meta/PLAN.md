# 구현 계획서 — 1주차 발표 자료 (v2)

> 흐름: **안 A (문제 주도형)** · 청중: LangChain 경험자 · 톤: 격식·캐주얼 중간
> 산출물: **상세 교안(textbook)** + 슬라이드(HTML→PDF) + 실행 스크립트
> **워크플로우**: 디자인 → 보강자료 수집 → 교안 작성 → 슬라이드 추출

---

## 0. 산출물 (최종)

| # | 산출물 | 경로 | 단계 |
|---:|---|---|:---:|
| 1 | 자료·콘텐츠 구조 설계서 | `DESIGN.md` | Phase 1 |
| 2 | 보강 자료 (검색·요약) | `research/*.md` | Phase 2 |
| 3 | 보강 자료 색인 | `research/INDEX.md` | Phase 2 |
| 4 | 상세 교안 / 리포트 | `TEXTBOOK.md` | Phase 3 |
| 5 | 실행 스크립트 + 가이드 | `scripts/*.py`, `scripts/README.md` | Phase 3 |
| 6 | 슬라이드 마크다운 | `content/slides.md` | Phase 4 |
| 7 | 슬라이드 HTML/PDF | `content/slides.{html,pdf}` | Phase 4 |

---

## 1. 폴더 구조 (최종)

```text
week1-overview-taeyoung/
├── README.md             (이미 있음)
├── BRAINSTORM.md         (이미 있음)
├── PLAN.md               (← 이 문서)
├── STATUS.md             (NEW — 진행 추적)
├── DESIGN.md             (Phase 1)
├── 01-overview*.md       (이미 있음 — 한/영)
├── 02-quickstart*.md     (이미 있음 — 한/영)
├── 03-customization*.md  (이미 있음 — 한/영)
├── research/             (Phase 2)
│   ├── INDEX.md
│   ├── 01_<주제>_<출처>.md
│   ├── 02_<주제>_<출처>.md
│   └── ...
├── TEXTBOOK.md           (Phase 3)
├── scripts/              (Phase 3)
│   ├── README.md
│   ├── requirements.txt
│   ├── 01_quickstart_research_agent.py
│   ├── 02_model_string_swap.py
│   ├── 03_model_object_ollama.py
│   └── 04_custom_system_prompt.py
└── content/              (Phase 4)
    ├── slides.md
    ├── slides.html
    └── slides.pdf
```

---

## 2. 워크플로우 (4단계)

각 단계는 다음 단계 시작 전에 **사용자 승인** 을 받는다.
진행 상태는 `STATUS.md` 에 기록한다.

```text
┌──────────────────────────────────────────────────────────┐
│ Phase 1. DESIGN  (디자인)                                │
│   주어진 3개 문서 분석 → 청중·범위·구조 정의             │
│   → DESIGN.md 산출                                       │
└──────────────────────────────────────────────────────────┘
              ↓ 사용자 승인
┌──────────────────────────────────────────────────────────┐
│ Phase 2. RESEARCH  (보강자료 수집)                       │
│   디자인의 빈 칸 식별 → 검색 → research/*.md 다운로드    │
│   → research/INDEX.md 산출                               │
└──────────────────────────────────────────────────────────┘
              ↓ 사용자 승인
┌──────────────────────────────────────────────────────────┐
│ Phase 3. TEXTBOOK  (상세 교안 + 스크립트)                │
│   원문 + 보강자료 → 교안 본문 작성                       │
│   → TEXTBOOK.md + scripts/ 산출                          │
└──────────────────────────────────────────────────────────┘
              ↓ 사용자 승인
┌──────────────────────────────────────────────────────────┐
│ Phase 4. SLIDES  (슬라이드 추출)                         │
│   교안에서 핵심 메시지 추출 → 슬라이드 17장              │
│   → slides.{md,html,pdf} 산출                            │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Phase 1 — DESIGN

### 3-1. 목적

발표·교안의 **구조와 범위** 를 먼저 못박는다. 글을 쓰기 전에 "무엇을 / 어떤 순서로 / 누구에게 / 어디까지" 를 결정.

### 3-2. 산출 — `DESIGN.md` 구성

1. **청중 프로파일** (전제 지식 / 기대 / 시간 제약)
2. **학습 목표** (발표 후 청중이 할 수 있어야 할 것 3~5개)
3. **교안 목차 안** (장·절 단위 — Phase 3 의 뼈대)
4. **슬라이드 ↔ 교안 매핑** (어느 슬라이드가 어느 절에서 나오나)
5. **핵심 메시지** (한 문장 답)
6. **포함/제외 정책** (이 발표에서 다루지 않는 주제 명시)
7. **시각자료 명세** (다이어그램·표·코드 블록 일람)
8. **용어·표기 가이드** (deepagents / Deep Agent / `create_deep_agent()` 일관성)

### 3-3. Verify

- 목차에 BRAINSTORM.md §6 8개 포인트가 모두 매핑되는가
- 학습 목표 ↔ 슬라이드 ↔ 코드 스크립트가 1:N 으로 연결되는가

---

## 4. Phase 2 — RESEARCH

### 4-1. 목적

원문 3개 문서가 짧다 (각 3~4KB). 발표를 위한 **두께·근거·맥락** 을 인터넷에서 보강.

### 4-2. 후보 검색 주제 (DESIGN 단계에서 확정)

| 주제 | 왜 필요한가 | 우선순위 |
|---|---|:---:|
| Deep Agent 라이브러리 공식 블로그/릴리즈 노트 | 출시 배경·디자인 의도 1차 자료 | ⭐⭐⭐ |
| Claude Code · Deep Research · Manus 의 작동 원리 | "영감을 받았다" 의 실체 | ⭐⭐⭐ |
| `create_deep_agent` 코드 레벨 설명 | 시그니처 / 옵션 / 내부 구조 | ⭐⭐⭐ |
| LangGraph 위에 어떻게 얹혔나 (StateGraph/노드) | 청중이 LangChain 경험자 → 자연 다리 | ⭐⭐ |
| `write_todos` 의 실제 출력 예시 | "어떻게 보이는지" 시각화 | ⭐⭐ |
| 기본 시스템 프롬프트 전문 | "Claude Code에서 영감" 의 증거 | ⭐⭐ |
| 실제 사용 사례 (블로그·튜토리얼) | 청중이 머릿속에 그림 그릴 수 있게 | ⭐⭐ |
| `create_agent` vs `create_deep_agent` 비교 | 결정 표 근거 | ⭐⭐ |

### 4-3. 다운로드 컨벤션

각 파일은 다음 포맷:

```text
---
title: <원문 제목>
url: <원문 URL>
fetched: 2026-05-04
note: <한 줄 — 왜 가져왔는가>
---

# <원문 제목>

(전문 — 가능한 한 원문 그대로. 광고·내비게이션은 제거)

---
출처: <URL>
```

파일명: `NN_<짧은 주제>_<도메인>.md` (예: `01_deepagents_announcement_langchain-blog.md`)

### 4-4. 산출 — `research/INDEX.md`

색인 표:
| # | 제목 | 출처 | 보강 대상(교안 절) | 우선순위 |

### 4-5. Verify

- 각 자료가 교안 어느 절에 쓰일지 명시되어 있는가 (orphan 금지)
- URL 이 살아있는가 (재방문 가능)
- 인용 시 저작권 (paraphrase vs quote) 정책 일관

### 4-6. 검색 도구

- WebSearch · WebFetch (최우선)
- 공식 문서 사이트 · GitHub README · LangChain 블로그 우선
- 신뢰성 낮은 미디엄 글은 보조용으로만

---

## 5. Phase 3 — TEXTBOOK + SCRIPTS

### 5-1. 목적

스터디 멤버가 발표 전후로 **혼자 읽어도 이해할 수 있는** 교안. 슬라이드의 부족한 맥락을 채움.

### 5-2. `TEXTBOOK.md` 목차 안 (DESIGN 후 확정)

```text
0. 들머리 — 이 글이 무엇을 다루나
1. 왜 Deep Agent 인가
   1.1. Vanilla LLM 에이전트의 한계
   1.2. 문제를 해결한 3가지 사례 (Claude Code / Deep Research / Manus)
   1.3. 패턴의 일반화 — 라이브러리화
2. 4가지 내장 능력
   2.1. Planning — `write_todos`
   2.2. Filesystem — `ls/read_file/write_file/edit_file`
   2.3. Subagents — `task`
   2.4. Long-term Memory — LangGraph Store
3. 5줄로 시작하기 — Quickstart
   3.1. 환경 준비
   3.2. 검색 도구 정의
   3.3. `create_deep_agent` 호출
   3.4. invoke 시 백그라운드에서 일어나는 일
4. 청사진 — `create_deep_agent` 의 다이얼
   4.1. Core Config — Model / System Prompt / Tools
   4.2. Features — Backend / Subagents / Interrupts (개요만)
   4.3. Model 바꾸기 — 문자열 vs 객체
   4.4. System Prompt 패턴
5. 언제 쓰나
   5.1. `create_agent` vs LangGraph vs `create_deep_agent`
   5.2. 의사결정 표
6. 다음 주차로 가는 다리
   6.1. 컨텍스트·메모리·스킬 (정훈)
   6.2. 백엔드·샌드박스·권한 (종훈L)
부록 A. 용어집
부록 B. 실행 스크립트 안내
부록 C. 참고문헌 (research/INDEX.md 와 매핑)
```

### 5-3. 작성 원칙

- 각 절은 **한 줄 요약** 으로 시작
- 코드 블록은 모두 `scripts/` 의 실제 파일에서 직접 가져옴 (불일치 방지)
- 외부 인용은 footnote `[^N]` 으로 → 부록 C 의 참고문헌 매핑
- 분량 가이드: 각 1차 절 1~2 페이지 (총 15~20페이지)

### 5-4. 스크립트 4종 (변경 없음)

| 파일 | 출처 | 무엇을 보여주나 | 필수 키 |
|---|---|---|---|
| `01_quickstart_research_agent.py` | 02-quickstart Step 3~5 | 리서치 에이전트 풀 예제 | `ANTHROPIC_API_KEY`, `TAVILY_API_KEY` |
| `02_model_string_swap.py` | 03-customization | `"openai:gpt-5"` 문자열 교체 | `OPENAI_API_KEY` |
| `03_model_object_ollama.py` | 03-customization | Ollama 모델 객체 | (Ollama 로컬) |
| `04_custom_system_prompt.py` | 03-customization | 커스텀 system_prompt 최소 | `ANTHROPIC_API_KEY` |

### 5-5. Verify

- 교안 본문에서 인용된 코드 ≡ `scripts/*.py` 의 실제 코드
- 교안 footnote 가 모두 `research/INDEX.md` 에 존재
- 교안의 모든 한국어 BOLD 가 CJK 렌더링 규칙 준수 (글로벌 CLAUDE.md)

---

## 6. Phase 4 — SLIDES

### 6-1. 목적

교안의 **시각·축약 버전**. 발표장에서 보조용. 텍스트 의존하지 않게.

### 6-2. 17슬라이드 구성 (v1 PLAN 과 동일 — 안 A 흐름)

| # | variant | 제목 | 시간 | 교안 매핑 |
|---:|---|---|---:|---|
| 1 | cover | Deep Agents 첫 발걸음 | 0:30 | — |
| 2 | section/01 | 왜 Deep Agent 인가 | 0:30 | §1 |
| 3 | default | Vanilla 에이전트의 한계 | 1:30 | §1.1 |
| 4 | section/02 | 4가지 내장 능력 | 0:30 | §2 |
| 5 | default | 비유 — 비서의 4가지 도구 | 1:30 | §2 도입 |
| 6 | default | Planning + Filesystem | 1:30 | §2.1, §2.2 |
| 7 | default | Subagents + Long-term Memory | 1:30 | §2.3, §2.4 |
| 8 | section/03 | 5줄로 시작하기 | 0:30 | §3 |
| 9 | default | Quickstart 4단계 | 1:00 | §3.1, §3.2 |
| 10 | default | 코드 한 페이지 | 1:30 | §3.3 |
| 11 | default | invoke() 백그라운드 5단계 | 1:30 | §3.4 |
| 12 | section/04 | 청사진 | 0:30 | §4 |
| 13 | default | Core Config + Features | 1:30 | §4.1, §4.2 |
| 14 | default | Model 바꿔 끼우기 | 1:30 | §4.3 |
| 15 | section/05 | 언제 쓰나 | 0:30 | §5 |
| 16 | default | 결정 표 | 1:30 | §5.2 |
| 17 | closing | 다음 주제로 | 0:30 | §6 |

### 6-3. 빌드 명령

```bash
cd /home/restful3/workspace/langchain-docs
# HTML 만
python -m template.build_slides \
    deep-agents/week1-overview-taeyoung/content/slides.md \
    --html-only

# PDF 까지 (Chrome + chromedriver 필요)
python -m template.build_slides \
    deep-agents/week1-overview-taeyoung/content/slides.md
```

### 6-4. Verify

- 17개 슬라이드 분할 확인 (브라우저 또는 PDF 페이지 수)
- 각 슬라이드가 1280×720 영역 안에서 오버플로우 없음
- 슬라이드 코드 블록 ≡ `scripts/*.py` 와 동일

---

## 7. 결정/확인 필요 (구현 전)

> Phase 1 시작 전에 답이 있어야 흔들림 없이 진행됨.

- [ ] **시간 배분** — 발표 17분 + Q&A 3분 = 20분 적정?
- [ ] **template 모듈명** — 폴더가 `template/` 인데 README는 `ai_odyssey_publisher`. `python -m template.build_slides` 로 호출 OK?
- [ ] **워드마크/푸터** — 기본 "AI Odyssey · External Publishing" 그대로 둘지?
- [ ] **research 분량 한도** — 자료 몇 개까지? (제안: 5~8개)
- [ ] **교안 분량 한도** — 페이지 수? (제안: 15~20p A4)
- [ ] **스크립트 4 → 3** 으로 줄일지? (04 와 03 일부 중복)
- [ ] **PDF 빌드 환경** — Chrome/chromedriver 사용 가능?
- [ ] **Phase 간 승인 방식** — Phase 끝날 때마다 사용자에게 보여주고 진행? 아니면 모아서?

---

## 8. 작업 순서 (Phase 별 verify)

```text
Phase 1. DESIGN
  1.1 BRAINSTORM.md + 3개 원문 재독
  1.2 DESIGN.md 작성
       → verify: 학습목표 ↔ 교안 절 ↔ 슬라이드 매핑 표 완성
  1.3 STATUS.md 업데이트 → Phase 1 완료
  ✋ 사용자 승인 대기

Phase 2. RESEARCH
  2.1 검색 주제 우선순위 확정
  2.2 각 주제별 WebSearch + WebFetch
       → verify: research/<NN>_*.md 5~8개
  2.3 research/INDEX.md 작성
       → verify: 모든 자료가 교안 절에 매핑됨
  2.4 STATUS.md 업데이트 → Phase 2 완료
  ✋ 사용자 승인 대기

Phase 3. TEXTBOOK + SCRIPTS
  3.1 scripts/*.py 4종 작성 + py_compile
       → verify: 각 스크립트 syntax 통과
  3.2 scripts/01 만 실제 실행 (Anthropic+Tavily 키 필요)
       → verify: 응답 출력
  3.3 scripts/README.md + requirements.txt
  3.4 TEXTBOOK.md 본문 작성 (§0 ~ §6 + 부록)
       → verify: 모든 footnote 가 research/INDEX.md 와 일치
       → verify: 코드 블록 ≡ scripts/*.py
  3.5 STATUS.md 업데이트 → Phase 3 완료
  ✋ 사용자 승인 대기

Phase 4. SLIDES
  4.1 slides.md 작성 (교안 §↔슬라이드 매핑 따라)
  4.2 build_slides --html-only
       → verify: 17 슬라이드 분할 + 오버플로우 없음
  4.3 build_slides (PDF)
       → verify: PDF 17p / 1280×720
  4.4 STATUS.md 업데이트 → Phase 4 완료
```

---

## 9. 비고

- BRAINSTORM.md 의 페르소나 분석은 Phase 1 DESIGN.md 의 "핵심 메시지" 와 "학습 목표" 도출 시 직접 활용
- v1 PLAN.md 의 슬라이드 17장 구성은 v2 §6 으로 이전 (변경 없음)
- 교안·슬라이드의 코드 블록은 모두 `scripts/` 의 실제 파일과 sync — 한 곳을 고치면 다른 곳도 함께 갱신해야 함을 STATUS.md 에서 추적
