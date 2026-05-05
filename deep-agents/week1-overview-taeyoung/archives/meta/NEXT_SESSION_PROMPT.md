# 세션 재시작 프롬프트 — 1주차 발표 자료 (태영)

> 새 세션에서 작업을 이어가려면, 아래 **프롬프트 블록 전체** 를 복사해 첫 메시지로 붙여 넣는다.
> 작성일: 2026-05-04 (Phase 3 종료 시점)

---

## 복사용 프롬프트

```text
1주차 Deep Agent 스터디 발표 자료를 이어서 작업한다.

## 작업 폴더 (절대경로)
/home/restful3/workspace/langchain-docs/deep-agents/week1-overview-taeyoung/

## 핵심 컨텍스트
- 담당자: 태영 (1주차 첫 발제)
- 주제: Overview, Quickstart, Customization, Models / 20분 (17분 + Q&A 3분)
- 청중: LangChain 경험자
- 흐름: 안 A (문제 주도형 — Hook → 4대 능력 → Quickstart → Customize → When-to-use)
- 산출물: HTML→PDF 슬라이드 (template/) + 실행 스크립트 + 상세 교안
- 워크플로우: DESIGN → RESEARCH → TEXTBOOK → SLIDES (4단계, 매 Phase 끝마다 사용자 승인)
- 템플릿 폴더: /home/restful3/workspace/langchain-docs/template/

## 결정된 사항 (변경 금지)
- research 자료 한도: 5~8개 (현재 7건 + RAG 합성 1건 = 8)
- 교안 분량: 15~20p A4 → 실제 18p
- Phase 간 승인: 매 Phase 끝마다 (a)
- 스크립트 4종: OpenAI 호환 베이스 (clipproxyapi 환경변수로 라우팅)
- 흐름: 안 A 확정 (변경 X)
- 그림: SVG 9개, 표: 9개 (등장 순서로 그림.N / 표.N 캡션)
- SVG 정책: <title> 미삽입, viewBox = 콘텐츠 bbox+padding
- 리포트 빌드: 섹션 커버만 (프론트커버·TOC·백커버 X), A4 자연 흐름

## 현재 상태 — Phase 3 완료, Phase 4 시작 대기
[████████████████████████░░░░░░░░░] 75% (Phase 0~3 ✅ · Phase 4 ⏸ 시작 대기)

완료된 산출물:
- PLAN.md / BRAINSTORM.md / STATUS.md / README.md / DESIGN.md
- research/ 7건 (01~07, verbatim) + INDEX.md + RAG_textbook_synthesis.md
- notebooklm_artifacts/ 9건
- 영문 원문 3개 + 한국어 번역 3개
- TEXTBOOK.md (§0~§6 + 부록 A·B·C, 18p, 그림 9 + 표 9, footnote 8건)
- scripts/ (requirements.txt + 01~04_*.py + README.md, py_compile 4/4 통과)
- .env_sample (OPENAI_API_KEY/OPENAI_BASE_URL/DEEPAGENT_MODEL/TAVILY_API_KEY/OLLAMA_MODEL)
- figs/fig01~09_*.svg (외부 캡션 제거, viewBox 축소 완료)
- report/build_local.py + content/ + figs 심볼릭 + detailed_report_external.{html,pdf}
  - PDF: 16p A4 (210×297mm), 2.3MB, 시각 전수 검증 통과

## 새 세션 시작 시 읽는 순서 (1순위 → 5순위)
1. STATUS.md — 현재까지 완료된 작업과 다음 액션 (1순위)
2. NEXT_SESSION_PROMPT.md — 이 프롬프트 자체 (메타 정보)
3. PLAN.md — 워크플로우 4단계 전체 계획 (§6 슬라이드 17장 매핑)
4. DESIGN.md — Phase 1 산출물 (§4 슬라이드↔교안↔학습목표 매핑 / §5 핵심 메시지 / §7 시각자료 명세 V1~V10)
5. TEXTBOOK.md — 교안 본문 (그림 9 + 표 9 + footnote 매핑)

필요 시 추가:
- research/RAG_textbook_synthesis.md (인용 보강)
- research/0N_*.md (구체적 인용 시 원본 확인)
- figs/fig01~09_*.svg (슬라이드에 그대로 임베딩 가능)

## 다음 액션 — Phase 4 (SLIDES) 시작

PLAN.md §6 + DESIGN.md §4 슬라이드 매핑 따른다. 17 슬라이드 구성:

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

### 4-A. content/slides.md 작성

frontmatter (title/subtitle/author/version/org/kicker/date) + H1 분할 17 장.

각 슬라이드 사용 가능 자원:
- figs/fig01~09_*.svg — 그대로 인라인 임베딩 또는 <img> (slides.md 의 figs/ 경로는 빌드 후 content/figs/ 로 가는 심볼릭이 필요할 수 있음 — 확인)
- TEXTBOOK.md 의 표 (cmp-table 컴포넌트로 변환됨)
- scripts/01~04 의 코드 발췌 (slides.md 코드 블록 ≡ scripts/*.py sync 유지)

### 4-B. HTML/PDF 빌드

```bash
cd /home/restful3/workspace/langchain-docs
# HTML 만 (분할 검증)
python -m template.build_slides \
    deep-agents/week1-overview-taeyoung/content/slides.md \
    --html-only

# PDF 까지 (Chrome + chromedriver 필요)
python -m template.build_slides \
    deep-agents/week1-overview-taeyoung/content/slides.md
```

### 4-C. Verify

- 17 슬라이드 분할 확인 (HTML 또는 PDF 페이지 수)
- 1280×720 영역 안에서 오버플로우 없음
- 슬라이드 코드 블록 ≡ scripts/*.py sync
- 슬라이드 SVG ≡ figs/*.svg
- 한국어 BOLD CJK 규칙 준수

### 4-D. ✋ 사용자 최종 검수

## 작업 컨벤션 (글로벌 CLAUDE.md 준수)
- 한국어 마크다운 BOLD: `**용어(English)**` 패턴 닫는 `**` 뒤 한글 오면 공백 1칸
- 코드 펜스 언어 식별자 필수 (```python / ```bash / ```text / ```mermaid)
- 본문에서 `~` 는 `\~` 로 이스케이프 (HTML 블록 안에서는 그대로)
- Mermaid 노드 라벨 줄바꿈은 `<br/>` (`\n` 안 됨)
- 코딩 행동: 코딩 전 생각 → 단순함 우선 → 수술적 변경 → 목표 주도 실행
- 테스트 먼저 작성 후 구현

## 미결정 / 보류 항목 (Phase 4 진입 시 결정)
- template/build_slides.py 의 frontmatter 메타 필드 (title/subtitle/author/version/org/kicker/date) 값 확정 — DESIGN.md §1, §5 참조
- 슬라이드 워드마크/푸터 — 기본 "AI Odyssey" 유지 권장
- PDF 빌드 환경 — 이전 Phase 3 빌드에서 Selenium Manager 가 chromedriver 자동 다운로드 확인됨 (별도 설치 불필요)
- 슬라이드 SVG 경로 — content/slides.md 와 figs/ 의 상대 위치 검증 필요 (필요 시 content/figs 심볼릭)

## 시작 명령
"지금 상태 확인하고 Phase 4 (SLIDES) 시작해."
```

---

## 사용 방법

1. 새 Claude Code 세션을 연다 (또는 `/clear`).
2. 위 프롬프트 블록(```text ... ```)의 **내부 텍스트만** 복사해 첫 메시지로 붙여 넣는다.
3. Claude 가 STATUS.md → PLAN.md → DESIGN.md → TEXTBOOK.md 순서로 읽고 Phase 4 를 시작할 준비를 한다.
4. 사용자 확인 후 `content/slides.md` 작성부터 진입.

## 변경 시 갱신 포인트

- Phase 4 진입 후에는 이 파일을 **삭제** 하거나, 발표 직전 최종 점검용 메모로 갱신.
- 결정 사항 변경 시 (예: 슬라이드 17장 → 다른 수) 위 프롬프트의 "결정된 사항" 섹션도 같이 수정.
