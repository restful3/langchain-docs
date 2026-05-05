# 디자인 — 1주차 발표 자료

> Phase 1 산출물 · PLAN.md §3 의 8개 섹션 구조
> 흐름 채택: **안 A (문제 주도형)** · 청중: LangChain 경험자 · 톤: 격식·캐주얼 중간

---

## 1. 청중 프로파일

| 항목 | 내용 |
|---|---|
| 인원 | 11명 (스터디 멤버) |
| 전제 지식 — 강함 | LangChain `ChatModel` / `Runnable` / 도구 호출 / `create_agent` 사용 경험 |
| 전제 지식 — 보통 | LangGraph 의 `StateGraph` 개념을 들어봄 (직접 짠 적은 없을 수 있음) |
| 전제 지식 — 약함 | Deep Agent 라이브러리 자체 / Claude Code · Deep Research · Manus 의 내부 구조 |
| 기대 | 다음 9개 발제의 **공통 출발점** 을 잡는 청사진 |
| 시간 제약 | 발표 17분 + Q&A 3분 = 20분 (이론 주차 첫 발제) |
| 톤 | 격식·캐주얼 중간 — 전문 용어는 정확히 쓰되 비유로 풀어줌 |

**파생 결정**

- LangChain 비유는 **공짜로 사용** 한다 (예: "`create_agent` 가 작은 칼이라면, `create_deep_agent` 는 스위스 아미").
- LangGraph 의 그래프 내부는 **블랙박스로 둔다** — 9주차 세훈/수경 발제에 양보.
- `create_agent` 와의 비교를 **필수 슬라이드** 로 둔다 (회의론자 페르소나 대응).

---

## 2. 학습 목표

발표가 끝났을 때 청중이 다음 다섯 가지를 할 수 있어야 한다.

| # | 학습 목표 | 검증 가능한 행동 |
|:---:|---|---|
| L1 | Deep Agent 를 **한 문장으로 정의** 하고 4대 내장 능력을 매칭한다 | "계획 / 파일시스템 / 서브에이전트 / 장기메모리" 4개 단어 + 각각의 도구 이름 (`write_todos`, `ls`/`read_file`/`write_file`/`edit_file`, `task`, Store) 을 말할 수 있음 |
| L2 | `create_deep_agent()` 로 **첫 에이전트를 5줄에 만들 수 있다** | Quickstart 코드를 빈 줄에서 보고 빠진 인자(`tools`, `system_prompt`)를 채울 수 있음 |
| L3 | `agent.invoke()` 호출 시 **백그라운드에서 일어나는 5단계** 를 설명한다 | 계획 → 검색 → 컨텍스트 관리 → 위임 → 종합의 흐름을 자기 말로 풀 수 있음 |
| L4 | Model / System Prompt / Tools **세 다이얼** 의 사용법을 안다 | `"provider:model"` 문자열 vs LangChain 모델 객체 차이를 구분, 기본값(claude-sonnet-4-5-20250929) 을 인지 |
| L5 | `create_agent` / LangGraph workflow / `create_deep_agent` **결정표** 를 자기 문제에 적용한다 | "다단계 + 컨텍스트 큼 + 위임/메모리 필요" 일 때만 Deep Agent 를 고른다는 기준을 말할 수 있음 |

> **L1\~L5 ↔ 슬라이드 ↔ 교안 절** 의 1:N 매핑은 §4 표로.

---

## 3. 교안 목차 (TEXTBOOK.md 뼈대)

PLAN.md §5.2 의 안을 **확정** 으로 옮긴다.

```text
§0  들머리 — 이 글이 무엇을 다루나                          (0.5p)
§1  왜 Deep Agent 인가
    §1.1 Vanilla LLM 에이전트의 한계                         (1.0p)
    §1.2 문제를 해결한 3가지 사례 (Claude Code/Deep Research/Manus) (1.5p)
    §1.3 패턴의 일반화 — 라이브러리화                        (0.5p)
§2  4가지 내장 능력
    §2.1 Planning — write_todos                               (1.0p)
    §2.2 Filesystem — ls/read_file/write_file/edit_file       (1.0p)
    §2.3 Subagents — task                                     (1.0p)
    §2.4 Long-term Memory — LangGraph Store                   (1.0p)
§3  5줄로 시작하기 — Quickstart
    §3.1 환경 준비 (의존성·API 키)                            (0.5p)
    §3.2 검색 도구 정의                                       (0.5p)
    §3.3 create_deep_agent 호출                               (1.0p)
    §3.4 invoke 시 백그라운드 5단계                           (1.5p)
§4  청사진 — create_deep_agent 의 다이얼
    §4.1 Core Config (Model / System Prompt / Tools)          (1.0p)
    §4.2 Features (Backend / Subagents / Interrupts) — 개요만  (0.5p)
    §4.3 Model 바꾸기 — 문자열 vs 객체                        (1.0p)
    §4.4 System Prompt 패턴                                   (0.5p)
§5  언제 쓰나
    §5.1 create_agent vs LangGraph vs create_deep_agent       (1.0p)
    §5.2 의사결정 표                                          (0.5p)
§6  다음 주차로 가는 다리
    §6.1 컨텍스트·메모리·스킬 (정훈)                          (0.3p)
    §6.2 백엔드·샌드박스·권한 (종훈L)                          (0.3p)
부록 A. 용어집                                                 (0.5p)
부록 B. 실행 스크립트 안내                                     (0.5p)
부록 C. 참고문헌 (research/INDEX.md 와 매핑)                    (0.5p)

합계: 약 18.6p (목표 15~20p 범위 안)
```

**BRAINSTORM.md §6 8개 포인트 매핑 검증**

| BRAINSTORM §6 포인트 | 매핑 |
|---|---|
| Deep Agent 는 LangGraph 기반 | §1.3, §0 (스택 그림) |
| 4대 내장 기능 + 각 도구 이름 | §2.1\~§2.4 |
| 기본 시스템 프롬프트 = Claude Code 영감 | §4.4 |
| 도구 호출 지원 모델 필수 | §3.1, §4.3 (경고 박스) |
| 모델 지정 2가지 — 문자열 vs 객체 | §4.3 |
| 기본 모델 = `claude-sonnet-4-5-20250929` | §4.1 |
| `create_deep_agent` 자주 쓰는 인자 | §3.3, §4.1 |
| 4주 스터디 전체 흐름 한 줄 | §6.1, §6.2 |

✅ 8/8 모두 매핑됨.

---

## 4. 슬라이드 ↔ 교안 ↔ 학습목표 매핑

PLAN.md §6.2 의 17슬라이드 구성을 **확정** 으로 옮기고 학습목표 컬럼을 추가한다.

| # | variant | 제목 | 시간 | 교안 | 학습목표 |
|---:|---|---|---:|---|:---:|
| 1 | cover | Deep Agents 첫 발걸음 | 0:30 | — | — |
| 2 | section/01 | 왜 Deep Agent 인가 | 0:30 | §1 | L1 |
| 3 | default | Vanilla 에이전트의 한계 | 1:30 | §1.1 | L1 |
| 4 | section/02 | 4가지 내장 능력 | 0:30 | §2 | L1 |
| 5 | default | 비유 — 비서의 4가지 도구 | 1:30 | §2 도입 | L1 |
| 6 | default | Planning + Filesystem | 1:30 | §2.1, §2.2 | L1 |
| 7 | default | Subagents + Long-term Memory | 1:30 | §2.3, §2.4 | L1 |
| 8 | section/03 | 5줄로 시작하기 | 0:30 | §3 | L2 |
| 9 | default | Quickstart 4단계 | 1:00 | §3.1, §3.2 | L2 |
| 10 | default | 코드 한 페이지 | 1:30 | §3.3 | L2 |
| 11 | default | invoke() 백그라운드 5단계 | 1:30 | §3.4 | L3 |
| 12 | section/04 | 청사진 | 0:30 | §4 | L4 |
| 13 | default | Core Config + Features | 1:30 | §4.1, §4.2 | L4 |
| 14 | default | Model 바꿔 끼우기 | 1:30 | §4.3 | L4 |
| 15 | section/05 | 언제 쓰나 | 0:30 | §5 | L5 |
| 16 | default | 결정 표 | 1:30 | §5.2 | L5 |
| 17 | closing | 다음 주제로 | 0:30 | §6 | — |

**합계 시간**: 17:00 (목표 17분 + Q&A 3분 = 20분)

**검증**

- 학습목표 L1\~L5 모두 최소 2개 슬라이드에 등장: ✅
- 슬라이드 → 교안 → 코드 스크립트 (`scripts/*.py`) 의 3중 매핑은 Phase 3 작성 시 코드 블록 기준으로 한 번 더 검증.

---

## 5. 핵심 메시지 (한 문장)

> **Deep Agent 는 LangGraph 위에 *계획·파일시스템·서브에이전트·장기메모리* 4대 능력을 내장한 라이브러리다. `create_deep_agent()` 한 줄로 시작하고, *Model · System Prompt · Tools* 세 다이얼로 자기 도메인에 맞춘다.**

이 문장은:

- **슬라이드 1 (cover)** 의 부제목 또는 첫 마디로 한 번
- **슬라이드 17 (closing)** 의 정리로 한 번 더 등장 (수미상관)
- 교안 §0 의 마지막 줄에 그대로 박힘

---

## 6. 포함 / 제외 정책

### 포함 (이 발표에서 다룬다)

- 4대 내장 능력 + 각 도구 이름 (BRAINSTORM §6 포인트 1\~2)
- `create_deep_agent()` 5줄 Quickstart 예제 + invoke 백그라운드 5단계
- Core Config 다이얼 — Model / System Prompt / Tools
- 모델 지정 2가지 방식 — 문자열 / LangChain 모델 객체
- 기본 모델 식별자 (`claude-sonnet-4-5-20250929`) + 도구 호출 모델 필수 경고
- 기본 시스템 프롬프트가 Claude Code 에서 영감받음 (trivia)
- `create_agent` vs LangGraph vs `create_deep_agent` 결정표
- 다음 발제 (컨텍스트/메모리/스킬, 백엔드/샌드박스) 다리

### 제외 (다음 발제로 미룬다)

| 주제 | 누구에게 | 비고 |
|---|---|---|
| 컨텍스트·메모리·스킬 깊이 | 정훈 | 우리 발표는 §6.1 한 줄로만 언급 |
| 백엔드 / 샌드박스 / 권한 | 종훈L | §6.2 한 줄로만 |
| Interrupts / HITL 패턴 | 후속 발제 | §4.2 에 이름만 띄움 |
| 미들웨어 아키텍처 깊이 | 후속 발제 | "기본 시스템 프롬프트의 자리" 정도만 |
| LangGraph 내부 구조 (StateGraph 노드) | 9주차 세훈/수경 | "LangGraph 기반" 으로만 |
| 실습 / 라이브 데모 | 2주차 종훈S | 사전 캡처 로그만 사용 |
| 평가 / LangSmith 관측성 | 별도 주차 | 스택 그림에 로고만 |
| Subagents 구현 디테일 (`SubAgent` 정의) | Customization 깊이 | "위임이 가능하다" 까지만 |

**원칙**: 1주차는 **지도** 만 그린다. 1주차에서 깊이 들어가면 다음 발제자가 할 게 없어진다.

---

## 7. 시각자료 명세

| ID | 슬라이드 | 자료 형태 | 출처 / 만드는 방법 | 우선순위 |
|---|---|---|---|:---:|
| V1 | S2 (또는 S1) | **스택 위치 다이어그램** (LangGraph → LangChain → deepagents → LangSmith) | Mermaid 또는 SVG 직접 작성 | ⭐⭐⭐ |
| V2 | S3 | Vanilla 에이전트 무너지는 한 장면 — Before/After 코드 톤 비교 | 텍스트 박스 2단 (코드 의사 표현) | ⭐⭐ |
| V3 | S5 | **비유 그림** — 노트(Filesystem) + 할 일(Planning) + 인턴(Subagents) + 일기장(Memory) | 4-grid 아이콘 + 라벨 (이모지 금지 → 도형) | ⭐⭐⭐ |
| V4 | S6, S7 | 4대 능력 ↔ 도구 이름 매핑 표 | 표 (한국어 라벨 + 코드폰트 도구명) | ⭐⭐⭐ |
| V5 | S10 | Quickstart 5줄 코드 (`scripts/01_quickstart_research_agent.py` 발췌) | 코드 블록 (구문 강조) | ⭐⭐⭐ |
| V6 | S11 | **invoke() 백그라운드 5단계 플로우** | Mermaid 가로 플로우 (계획 → 검색 → 오프로드 → 위임 → 종합) | ⭐⭐⭐ |
| V7 | S13 | **Mermaid CoreConfig + Features 그림** (03-customization 에 있는 다이어그램 그대로) | 03-customization_ko.md 5\~24행 | ⭐⭐⭐ |
| V8 | S14 | Model 문자열 vs 객체 — 좌우 코드 비교 | 코드 블록 2단 (`scripts/02`, `scripts/03` 발췌) | ⭐⭐ |
| V9 | S16 | **결정 표** (`create_agent` / LangGraph / `create_deep_agent`) | 표 — 행: 상황, 열: 도구 | ⭐⭐⭐ |
| V10 | S1, S17 | 핵심 메시지 한 줄 (수미상관) | 큰 텍스트 / 강조 박스 | ⭐⭐ |

**제작 정책**

- 이모지(emoji)는 **시각자료에 사용하지 않는다**. 한국어 본문/말머리에서만 제한적으로 (글로벌 CLAUDE.md 의 quantconnect 항목 영향 X — 이것은 슬라이드 정책).
- 모든 코드 블록은 **`scripts/*.py` 의 실제 코드와 sync** 되어야 한다 (PLAN §5.5 verify).
- Mermaid 노드 텍스트 줄바꿈은 `<br/>` 사용 (글로벌 CLAUDE.md 의 Mermaid 규칙).

---

## 8. 용어 · 표기 가이드

### 용어

| 형태 | 사용처 | 비고 |
|---|---|---|
| `deepagents` | 라이브러리/패키지 이름 | 코드폰트, 소문자 그대로 (PyPI 표기) |
| **Deep Agent** / **Deep Agents** | 개념 (단수/복수) | 본문에서 통일 — 한국어로도 그대로 표기 |
| `create_deep_agent()` | 함수 | 코드폰트, 괄호 포함 |
| Claude Code / Deep Research / Manus | 영감 출처 3개 | 고유명사 그대로 |
| LangGraph / LangChain / LangSmith | 생태계 | 한국어로 풀지 않음 |

### 한국어 번역 룰

| 영문 | 한국어 | 비고 |
|---|---|---|
| Planning | **계획 수립** | "플래닝" 보다 |
| Filesystem | **파일시스템** | 띄어쓰기 없이 |
| Subagent / Subagents | **서브에이전트** | "하위 에이전트" 사용 안 함 |
| Long-term Memory | **장기 메모리** | "롱텀" 사용 안 함 |
| Tool calling | **도구 호출** | LangChain 한국어 문서 일관성 |
| System prompt | **시스템 프롬프트** | "시스템 메시지" 사용 안 함 |

### 마크다운 표기 규칙 (글로벌 CLAUDE.md 준수)

- `**용어(English)**` 패턴: 닫는 `**` 뒤에 한글이 바로 오면 **공백 1칸 삽입**
  - ✅ `**계획 수립(Planning)** 은`
  - ❌ `**계획 수립(Planning)**은`
- 코드 블록은 반드시 언어 식별자 (` ```python `, ` ```bash `, ` ```text `, ` ```mermaid `)
- 페이지 범위 등에서 `~` 는 본문에서 `\~` 로 이스케이프 (HTML 블록 안에서는 그대로)
- 메타데이터 페어 줄들은 줄 끝 **공백 2칸** (hard break)

### 도구 이름 (코드폰트 고정)

`write_todos`, `ls`, `read_file`, `write_file`, `edit_file`, `task`, `internet_search`,
`init_chat_model`, `ChatOllama`

---

## 9. Phase 2 검색 주제 우선순위 확정

PLAN.md §4.2 후보 8개 → **5\~8개** 한도 안에서 우선순위 재확정.

| # | 주제 | 우선순위 | 보강 대상 절 | 필수/선택 |
|---:|---|:---:|---|:---:|
| R1 | `deepagents` 공식 블로그·릴리즈 노트 (LangChain) | ⭐⭐⭐ | §1.3, §0 | 필수 |
| R2 | Claude Code · Deep Research · Manus 작동 원리 (각 1건) | ⭐⭐⭐ | §1.2 | 필수 (3개 통합 1\~2건) |
| R3 | `create_deep_agent` 코드 레벨 — API 레퍼런스 | ⭐⭐⭐ | §3.3, §4.1 | 필수 |
| R4 | LangGraph 위에 어떻게 얹혔나 — 미들웨어 아키텍처 글 | ⭐⭐ | §1.3 footnote, §6 | 필수 |
| R5 | `write_todos` 실제 출력 예시 (블로그/트레이스 캡처) | ⭐⭐ | §2.1, §3.4 | 선택 |
| R6 | 기본 시스템 프롬프트 전문 (GitHub) | ⭐⭐ | §4.4 | 필수 |
| R7 | 실제 사용 사례 — 블로그/튜토리얼 1건 | ⭐⭐ | §1.2 보강 | 선택 |
| R8 | `create_agent` vs `create_deep_agent` 비교 | ⭐⭐ | §5.1, §5.2 | 선택 |

**Phase 2 목표**: 필수 5건 + 선택 1\~3건 → **총 5\~8건** (사용자 합의 한도).

---

## 10. Verify 체크리스트 (Phase 1 종료 기준)

- [x] 청중 프로파일 / 학습목표 3\~5개 / 교안 목차 / 슬라이드↔교안 매핑 / 핵심메시지 / 포함·제외 / 시각자료 / 용어 — 8개 섹션 모두 채워짐
- [x] BRAINSTORM.md §6 의 8개 빠뜨리면 안 되는 포인트가 교안 목차에 모두 매핑됨 (§3 표 참조)
- [x] 학습 목표 L1\~L5 가 슬라이드와 1:N 으로 연결됨 (§4 표 참조)
- [x] Phase 2 검색 주제 우선순위 5\~8개로 확정 (§9)
- [ ] ✋ **사용자 승인** — 다음 액션
