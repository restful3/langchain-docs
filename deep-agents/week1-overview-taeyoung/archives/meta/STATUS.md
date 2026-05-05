# 진행 상황 — 1주차 발표 자료

> **현재 단계**: ✅ Phase 3 (TEXTBOOK + SCRIPTS + REPORT 빌드) 완료 · Phase 4 (SLIDES) 시작 대기
> **마지막 업데이트**: 2026-05-04 (세션 종료 시점, Phase 3 완료)
> **다음 액션**: 새 세션에서 Phase 4 (SLIDES) 시작 — `content/slides.md` 작성 → HTML/PDF 빌드
> **세션 재시작 가이드**: [NEXT_SESSION_PROMPT.md](NEXT_SESSION_PROMPT.md)

---

## 🔄 세션 재시작 시 읽는 순서

새 세션으로 작업을 이어갈 때:

1. **이 파일 (STATUS.md)** — 현재까지 완료된 작업과 다음 액션
2. **PLAN.md** — 워크플로우 4단계 전체 계획
3. **BRAINSTORM.md** — 발표 콘텐츠 아이디어 정리
4. **README.md** — 폴더 구조와 담당 범위
5. 원문 3개 (`01-overview_ko.md`, `02-quickstart_ko.md`, `03-customization_ko.md`)

작업 컨텍스트:

- **담당자**: 태영 (1주차 첫 발제)
- **주제**: Overview, Quickstart, Customization, Models
- **시간**: 20분 (이론 발표)
- **흐름 채택**: 안 A (문제 주도형 — Hook → 4대 능력 → Quickstart → Customize → When-to-use)
- **청중**: LangChain 경험자
- **톤**: 격식·캐주얼 중간
- **산출물 형식**: HTML→PDF 슬라이드 (template/ 사용) + 실행 가능 스크립트
- **워크플로우**: DESIGN → RESEARCH → TEXTBOOK → SLIDES (4단계, Phase별 승인)

---

## 진행 게이지

```text
[████████████████████████░░░░░░░░░] 75% (Phase 0~3 완료 · Phase 4 시작 대기)
```

| Phase | 상태 | 시작 | 완료 | 산출물 |
|---|:---:|:---:|:---:|---|
| Phase 0. 계획 수립 | ✅ | 2026-05-04 | 2026-05-04 | PLAN.md, STATUS.md, BRAINSTORM.md |
| Phase 1. DESIGN | ✅ | 2026-05-04 | 2026-05-04 | DESIGN.md (사용자 승인 완료) |
| Phase 2. RESEARCH | ✅ | 2026-05-04 | 2026-05-04 | research/ 7건 (verbatim) + INDEX + RAG_textbook_synthesis + notebooklm_artifacts/ 9건 |
| Phase 3. TEXTBOOK + SCRIPTS + REPORT | ✅ | 2026-05-04 | 2026-05-04 | TEXTBOOK.md (18p · 그림 9 · 표 9) + scripts/ 4종 + figs/ SVG 9 + report/ HTML·PDF (16p A4) |
| Phase 4. SLIDES | ⏸ 대기 | — | — | content/slides.{md,html,pdf} |

**범례**: ✅ 완료 / 🟡 진행 중 / ⏸ 대기 / ❌ 차단 / ⏭ 스킵

---

## Phase 0. 계획 수립 ✅

- [x] 폴더 생성 + 원문 복사 (`week1-overview-taeyoung/`)
- [x] 페르소나 브레인스토밍 → `BRAINSTORM.md`
- [x] 워크플로우 4단계 정의 → `PLAN.md` v2
- [x] 진행 추적 체계 → `STATUS.md` (이 파일)

**산출물**

- [README.md](README.md)
- [BRAINSTORM.md](BRAINSTORM.md)
- [PLAN.md](PLAN.md)
- [STATUS.md](STATUS.md)

---

## Phase 1. DESIGN ✅

> 발표·교안의 구조·범위·청중·학습목표를 못박는다.

### 작업 항목

- [x] 1-1. 원문 3개 + BRAINSTORM 재독
- [x] 1-2. `DESIGN.md` 작성 (8개 섹션)
- [x] 1-3. Phase 2 검색 주제 우선순위 확정 (R1\~R8)
- [x] 1-4. ✋ 사용자 승인 완료 (2026-05-04)

### Verify 체크리스트

- [x] BRAINSTORM.md §6 8개 포인트가 교안 목차에 모두 매핑되었는가
- [x] 학습 목표 ↔ 슬라이드 ↔ 코드 스크립트 1:N 연결 완성

---

## Phase 2. RESEARCH ✅

> 인터넷에서 보강 자료를 검색해 `research/*.md` 로 다운로드. 7건 확보 (한도 5\~8 안) + RAG 합성 보고서 1건 + NotebookLM 9개 아티팩트 사이드 작업.

### 작업 항목

- [x] 2-1. 검색 주제별 WebSearch + WebFetch (병렬 5개 Agent)
  - [x] R1. Deep Agent 공식 발표 블로그 → 01
  - [x] R2. Claude Code · Deep Research · Manus 작동 원리 → 02, 03, 04 (3건)
  - [x] R3. `create_deep_agent` API 레퍼런스 → 05
  - [x] R4. LangGraph 위 미들웨어 아키텍처 → 06
  - [x] R6. 기본 시스템 프롬프트 전문 (GitHub) → 07
  - [ ] R5. `write_todos` 실제 출력 예시 — **보류** (실행 스크립트로 직접 캡처)
  - [ ] R7. 실제 사용 사례 — **보류** (01 의 use case 절로 충분)
  - [ ] R8. `create_agent` vs `create_deep_agent` 비교 — **추가 검토** (Phase 3 시 부족하면 추가)
- [x] 2-2. 각 자료를 `research/NN_<주제>_<도메인>.md` 컨벤션으로 저장 (frontmatter / 본문 / 출처 푸터)
- [x] 2-3. `research/INDEX.md` 작성 (자료 ↔ 교안 절 매핑, orphan 0건)
- [x] 2-4. 자료 verbatim 검증 — 02·03·04·06 paraphrase 발견 → 원본 그대로 재수집 (WebFetch redirect / Mintlify `.md` endpoint / `gh gist view`)
- [x] 2-5. (사이드) NotebookLM 노트북 + 11소스 + 9아티팩트 → `notebooklm_artifacts/`
- [x] 2-6. (사이드) RAG 합성 보고서 → `research/RAG_textbook_synthesis.md` (Q1\~Q6, 교안 §1\~§5 매핑, 부록 A 인용↔원본 표)

### Verify 체크리스트

- [x] 모든 자료가 교안 어느 절에 쓰일지 명시됨 (orphan 0건)
- [x] URL 모두 살아있음 (수집 시점 2026-05-04 확인)
- [x] 자료 수: **7건** — 5\~8개 범위 안
- [x] 1차 출처 5건 (01, 02, 05, 06, 07) / 2차 출처 2건 (03, 04 — 비공식 명시)
- [x] **원본 그대로(verbatim) 검증 완료** — 02·03·04·06 재수집으로 paraphrase·자체 합성 제거

### 수집 로그

| # | 제목 | 출처 | 1차/2차 | 보강 대상 |
|---:|---|---|:---:|---|
| 01 | Deep Agents (출시 발표) | LangChain Blog | 1차 | §0, §1.3, §5.1, §5.2 |
| 02 | Building Agents with Claude Agent SDK | Anthropic Engineering | 1차 | §1.1, §1.2 |
| 03 | How OpenAI's Deep Research Works | PromptLayer | 2차 | §1.2 |
| 04 | Manus AI agent 기술 분석 | GitHub Gist | 2차 | §1.2 |
| 05 | `create_deep_agent` API Reference | reference.langchain.com | 1차 | §3.3, §4.1, §4.2 |
| 06 | Middleware Architecture | docs.langchain.com (OSS) | 1차 | §2.1\~§2.4, §3.4, §4.2, §6 |
| 07 | Default System Prompt | GitHub raw | 1차 | §4.4 |

### 차단·이슈

(없음)

---

## Phase 3. TEXTBOOK + SCRIPTS + REPORT ✅

> 원문 + 보강자료로 교안 본문 + 실행 스크립트 작성, 그림(SVG) 시각화, HTML/PDF 빌드까지.

### 작업 항목 — 스크립트

- [x] 3-1. `scripts/requirements.txt`
- [x] 3-2. `scripts/01_quickstart_research_agent.py` (Tavily + create_deep_agent, OpenAI 호환 베이스)
- [x] 3-3. `scripts/02_model_string_swap.py` (init_chat_model "openai:<model>")
- [x] 3-4. `scripts/03_model_object_ollama.py` (ChatOllama 객체)
- [x] 3-5. `scripts/04_custom_system_prompt.py` (커스텀 system_prompt)
- [x] 3-6. 각 스크립트 `python -m py_compile` 통과 (4/4)
- [x] 3-7. `.env_sample` 작성 (OPENAI_API_KEY / OPENAI_BASE_URL / DEEPAGENT_MODEL / TAVILY_API_KEY / OLLAMA_MODEL)
- [x] 3-8. `scripts/README.md` (셋업·실행·트러블슈팅)

### 작업 항목 — 교안

- [x] 3-9. `TEXTBOOK.md` §0 들머리
- [x] 3-10. `TEXTBOOK.md` §1 왜 Deep Agent 인가 (§1.1\~§1.3)
- [x] 3-11. `TEXTBOOK.md` §2 4가지 내장 능력 (§2.1\~§2.4)
- [x] 3-12. `TEXTBOOK.md` §3 5줄로 시작하기 (§3.1\~§3.4)
- [x] 3-13. `TEXTBOOK.md` §4 청사진 — 다이얼 (§4.1\~§4.4)
- [x] 3-14. `TEXTBOOK.md` §5 언제 쓰나 (§5.1\~§5.2)
- [x] 3-15. `TEXTBOOK.md` §6 다음 주차로 (§6.1\~§6.2)
- [x] 3-16. `TEXTBOOK.md` 부록 A·B·C

### 작업 항목 — 시각화 (사용자 추가 요청)

- [x] 3-18. `figs/fig01\~09_*.svg` 9개 SVG 작성 (각 능력·구조·플로우)
- [x] 3-19. 본문에 SVG 임베딩 + `**그림.N**:` 캡션 (등장 순서)
- [x] 3-20. 표 9개에 `**표.N**:` 캡션 부여
- [x] 3-21. SVG 외부 캡션/제목/주석 텍스트 제거 (본문에 충실 반영)
- [x] 3-22. SVG `viewBox` / `width` / `height` 콘텐츠 bbox + padding 으로 축소 (슬라이드 삽입 대비)

### 작업 항목 — REPORT 빌드 (사용자 추가 요청)

- [x] 3-23. `report/content/` 분할 (00_front_matter, 01_textbook, 99_references, sections.yaml)
- [x] 3-24. `report/figs` 심볼릭 링크 (`../figs`) — SVG 경로 해결
- [x] 3-25. `report/build_local.py` 작성 (template/build_report.py 의 함수만 import, 자체 빌드)
- [x] 3-26. CSS override — 프론트커버/TOC/Executive Summary 페이지 제외 + named @page 풀기 + 강제 page-break 풀기 + SVG width 100%
- [x] 3-27. PDF 빌드 → 16 페이지 A4 (210×297mm), 2.3MB
- [x] 3-28. PDF 시각 전수 검증 (16 페이지 PNG 변환 → 그림 9개 + 표 9개 + 코드 + 한글 폰트 + footnote 점프 모두 정상)

### Verify 체크리스트

- [x] 교안 본문 코드 블록 ≡ `scripts/*.py` 실제 코드 (sync 확인)
- [x] 교안 footnote `[^N]` 모두 `research/INDEX.md` 와 매칭 (1차 5건 + 2차 2건 + 본문 메모 1건)
- [x] 한국어 BOLD 가 글로벌 CLAUDE.md CJK 규칙 준수
- [x] 분량: 18p A4 (목표 15\~20p 안)
- [x] 그림 9 / 표 9 / SVG 임베딩 9 모두 카운트 일치
- [x] PDF 페이지 분할: 강제 break 없음, 자연 흐름 (16p)

### 차단·이슈

(없음)

---

## Phase 4. SLIDES ⏸

> 교안에서 핵심 메시지 추출해 17슬라이드로 압축.

### 작업 항목

- [ ] 4-1. `content/slides.md` 작성 (frontmatter + 17 슬라이드)
- [ ] 4-2. `python -m template.build_slides … --html-only`
  - [ ] 17 슬라이드 분할 확인
  - [ ] 1280×720 영역 오버플로우 없음
- [ ] 4-3. PDF 빌드 (`python -m template.build_slides …`)
  - [ ] 17 페이지 / 1280×720 확인
- [ ] 4-4. 슬라이드 코드 블록 ≡ `scripts/*.py` 재확인
- [ ] 4-5. ✋ 최종 검수

### Verify 체크리스트

- [ ] 슬라이드 ↔ 교안 절 매핑 PLAN.md §6.2 와 일치
- [ ] 한국어 BOLD CJK 규칙 준수
- [ ] PDF 페이지 수 = 17

### 차단·이슈

(없음)

---

## 결정 항목 (PLAN.md §7)

| 항목 | 결정 | 결정일 |
|---|---|:---:|
| 시간 배분 | 17분 + Q&A 3분 = 20분 | 2026-05-04 |
| 흐름 | 안 A (문제 주도형) | 2026-05-04 (BRAINSTORM) |
| 청중·톤 | LangChain 경험자 / 격식·캐주얼 중간 | 2026-05-04 |
| **research 자료 수 한도** | **5\~8개 (필수 5 + 선택 1\~3)** | **2026-05-04** |
| **교안 분량 한도** | **15\~20p A4** | **2026-05-04** |
| **Phase 간 승인 방식** | **매 Phase 끝마다 (a)** | **2026-05-04** |
| 스크립트 4 → 3개 축소 | 4개 유지 (PLAN §5.4) | 2026-05-04 |
| template 모듈명 | `python -m template.build_slides` 로 호출 | (Phase 4 검증 시) |
| 워드마크/푸터 | 기본값 유지 | (Phase 4 검증 시) |
| PDF 빌드 환경 | Chrome/chromedriver — Phase 4 시 확인 | (Phase 4 검증 시) |

---

## 변경 로그

| 날짜 | 변경 | 비고 |
|---|---|---|
| 2026-05-04 | Phase 0 완료. PLAN v2 + STATUS 신설 | 워크플로우 4단계 확정 |
| 2026-05-04 | Phase 1 DESIGN.md 작성 완료 — 승인 대기 | 결정 3건(자료 5\~8 / 교안 15\~20p / 매 Phase 승인) 확정 |
| 2026-05-04 | Phase 1 사용자 승인 → Phase 2 시작 | — |
| 2026-05-04 | Phase 2 RESEARCH 완료 — 7건 수집, INDEX.md 작성 | 5개 Agent 병렬, R1\~R4·R6 처리. R5/R7/R8 은 보류 |
| 2026-05-04 | Phase 2 자료 검증 — 02·03·04·06 paraphrase 발견 → 원본 그대로 재수집 | 02 WebFetch redirect / 03 WebFetch 풀텍스트 / 04 `gh gist view` raw / 06 Mintlify `.md` endpoint. 06 의 진짜 페이지 제목은 "Prebuilt middleware". INDEX.md 갱신. |
| 2026-05-04 | NotebookLM 노트북 생성 + 11개 소스 업로드 | research/ 7 + INDEX + 영문 원문 3. URL: https://notebooklm.google.com/notebook/12fdc455-... |
| 2026-05-04 | NotebookLM 9종 아티팩트 생성 + 다운로드 (`notebooklm_artifacts/`) | mind_map · report · flashcards · data_table · quiz · infographic · slide_deck · video (41.5MB) · audio (32MB) |
| 2026-05-04 | NotebookLM RAG 합성 보고서 추가 (`research/RAG_textbook_synthesis.md`) | Q1\~Q6 (교안 §1\~§5 매핑) + 부록 A 인용↔원본 매핑 + 부록 B 사용 정책. INDEX.md 에 RAG 행 추가. |
| 2026-05-04 | 세션 종료 — 재시작 프롬프트 저장 (`NEXT_SESSION_PROMPT.md`) | Phase 2 사실상 완료, 다음 세션에서 Phase 3 (TEXTBOOK + SCRIPTS) 시작 |
| 2026-05-04 | Phase 3 시작 — scripts/ 4종 작성 (clipproxyapi/OpenAI 호환 베이스) | `.env_sample` + `requirements.txt` + `scripts/01\~04_*.py` + py_compile 4/4 통과 |
| 2026-05-04 | Phase 3 — TEXTBOOK.md 본문 작성 (§0\~§6 + 부록 A·B·C, 약 18p 분량) | research/INDEX.md footnote 매핑 7+1건 |
| 2026-05-04 | Phase 3 — figs/ SVG 9개 작성 + 본문 임베딩 + 표 9개 캡션 부여 | 그림.1\~9 / 표.1\~9 등장 순서 매김. ASCII/Mermaid 모두 SVG 로 대체 |
| 2026-05-04 | Phase 3 — SVG `viewBox` 콘텐츠 bbox+padding 으로 축소, 외부 캡션 제거 (본문 충실 반영) | 슬라이드 삽입 시 여백 이슈 해결용. 사용자 의도 반영 |
| 2026-05-04 | Phase 3 — `report/` HTML/PDF 빌드 시스템 구축 (`build_local.py`) | template/build_report.py 의 함수 import. 프론트커버/TOC/백커버 없이 섹션 커버만. A4 자연 흐름 (강제 페이지 break 풀림) |
| 2026-05-04 | Phase 3 — `report/figs` 심볼릭 링크 추가 (회귀 버그 수정) | SVG 경로 깨짐 → 모든 그림 alt 텍스트만 떴던 문제 해결. PDF 1959→2326KB |
| 2026-05-04 | Phase 3 — 16 페이지 PDF 시각 전수 검증 통과 | 그림 9 + 표 9 + 코드 + 한글 폰트 + footnote 점프 모두 정상. Phase 4 진입 준비 완료 |
