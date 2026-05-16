# 진행 상황 — 2주차 발표 자료 (Backends)

## 🔄 세션 재시작 시 읽는 순서

1. `archives/meta/NEXT_SESSION_PROMPT.md` — 다음 액션
2. 본 파일 — 현재 게이지
3. `archives/meta/PLAN.md` — 전체 계획
4. `archives/meta/DESIGN.md` — 결정된 사항
5. `archives/original_docs/05-backends.md` — 원문

## 진행 게이지

```text
Phase 0. 스캐폴딩       ✅ 폴더·README·원문 복사·deepagents 소스 스냅샷 완료
Phase 1. DESIGN         ✅ 슬라이드 22장 매핑·S3 가상 FS·Ollama gemma4:31b 확정
Phase 2. RESEARCH       ✅ 5건 verbatim 수집 (1차 100%) — WebFetch 0건 사용
Phase 3. TEXTBOOK+SCRIPTS ✅ 본문 619줄 저작 — 10개 §섹션 + 3개 부록 / 코드 인용 라인 정합성 검증
Phase 4. SLIDES         ✅ 22장 작성 — DESIGN §4 표와 1:1 일치 / 빌드는 template 환경 dep 설치 필요
Phase 5. 다이어그램     ✅ fig01~05 SVG 5종 작성 — XML 유효성 통과, content/figs 동기화 완료
```

## Phase 0. 스캐폴딩 ✅

- [x] 폴더 트리 생성 (week1 미러)
- [x] `.env_sample` 복사
- [x] `05-backends.md` / `05-backends_ko.md` → `original_docs/`
- [x] `deepagents/backends/*.py` 11개 → `original_docs/deepagents_backends/` (SHA 고정)
- [x] `build.py`, `sections.yaml`, `99_references.md` 복사 + 타이틀 갱신
- [x] `README.md` 작성
- [x] meta/ 5개 스켈레톤 작성

## Phase 1. DESIGN ✅ (2026-05-15)

### 작업 항목

- [x] BRAINSTORM 의 결정 필요 사항 3개 해결
- [x] DESIGN.md §4 (슬라이드 매핑표) 22장 완성
- [x] 가상 FS 예시 선택 — S3 스타일
- [x] LLM 채널 결정 — Ollama gemma4:31b (4개 스크립트 + walkthrough 노트북 + requirements 일괄 반영)

### 결과물

- `DESIGN.md` v1 (Verify 체크리스트 §10 모두 ✅)
- 4개 demo 스크립트 Ollama 전환 (syntax OK)
- `requirements.txt` 갱신 (`langchain-ollama` 추가, `langchain-openai` 제거)
- `README.md` 환경변수 표 갱신
- `walkthrough.ipynb` 공통 셀 (#1) 갱신

## Phase 2. RESEARCH ✅ (2026-05-15)

### 수집 결과 (5건)

1. ✅ LangGraph Persistence 공식 (`docs.langchain.com`, 665L) — §3, §5 보강
2. ✅ `BackendProtocol` 로컬 스냅샷 (`protocol.py` 852L) — §2
3. ✅ DiTo97/deepagents-backends README (S3+Postgres 구현체, 511L) — §7
4. ✅ LangChain Middleware Overview (120L) — §8
5. ✅ Ollama Tool calling docs (798L) — walkthrough 사전 검증

### 검증

- 1차 출처 100% (5/5)
- 모두 curl 기반 verbatim — WebFetch 사용 0건
- INDEX §2 교안 매핑표 완성

### 미해결 (사용자 확인 요청)

- gemma4:31b 모델 가용성 — `ollama list | grep gemma` 결과 필요. 미발견 시 27b 변종으로 다운그레이드.

## Phase 3. TEXTBOOK + SCRIPTS ✅ (2026-05-15)

### 작업 항목

- [x] `source/01_textbook.md` 본문 619줄 (10개 §섹션 + 부록 A/B/C)
- [x] `scripts_py/01_state_backend.py` (Phase 0)
- [x] `scripts_py/02_filesystem_backend.py` (Phase 0)
- [x] `scripts_py/03_store_backend.py` (Phase 0)
- [x] `scripts_py/04_composite_backend.py` (Phase 0)
- [x] `scripts_py/README.md` (Phase 0)
- [x] `scripts/walkthrough.ipynb` 셀 구조 (Phase 0 — 본문 통합은 Phase 4 후)
- [x] `scripts/requirements.txt` (Phase 1)
- [x] 코드 인용 라인 정합성 — 4종 데모 모두 실 라인과 일치 (검증 완료)
- [x] research 5건 모두 본문에서 한 번 이상 참조 (`grep -c` 로 확인)

### 검증

- 619줄 (목표 ~800 의 77%) — week1 800줄과 차이는 부록·시각 보강 영역
- 코드 인용 라인 정확 (spot-check: 4종 데모 핵심 블록 모두 verify 됨)
- 부록 A(코드 인용 표) / B(research 인덱스) / C(환경 점검) 모두 작성

## Phase 4. SLIDES ✅ (2026-05-15)

- [x] `source/slides.md` — 22장 (DESIGN §4 표 1:1 일치)
- [ ] `content/slides.html` — 빌드 대기 (사용자 환경 dep 설치 후)
- [ ] `content/slides.pdf` — 빌드 대기

### 빌드 사전 조건 (사용자 환경)

`build.py` 는 `template/` 의존성을 사용. 다음 설치 후 빌드 가능:

```bash
pip install -r /Users/jaden/projects/langchain-docs/template/requirements.txt
# markdown-it-py, mdit-py-plugins, selenium, pypdf, pyyaml
```

설치 후:

```bash
cd /Users/jaden/projects/langchain-docs/deep-agents/week2-backend-jh-lee
python archives/source/build.py --html-only  # HTML 만 (1차 검증)
python archives/source/build.py              # HTML + PDF (Chrome + chromedriver 필요)
```

### 페이스 추정 (20분 / 22장)

- 데모 슬라이드(#8, #10, #12, #14) 90초씩 = 6분
- 그 외 18장 47초씩 = 14분
- 합계 20분 정확히 맞음

## Phase 5. 다이어그램 ✅ (2026-05-15)

- [x] `fig01_four_backends_overview.svg` (83L, 53 elements) — 4종 3축 비교 표
- [x] `fig02_state_lifecycle.svg` (85L, 48 elements) — thread/checkpoint 흐름 + 새 thread 빈 state
- [x] `fig03_filesystem_mount.svg` (66L, 36 elements) — virtual_mode True/False 두 모드 비교
- [x] `fig04_store_namespace.svg` (81L, 45 elements) — tuple namespace 트리 + 경로 매핑
- [x] `fig05_composite_routing.svg` (58L, 31 elements) — 도구 호출 → 라우터 → 3 백엔드 분기
- [x] 양 디렉토리 동기화 — `archives/source/figs/` + `content/figs/`
- [x] XML 유효성 (Python `ET.parse`) 5/5 통과
- [x] 동일 팔레트 (week1 컨벤션): `#FAFAF9`(bg) · `#0F2C59`(navy) · `#6B6B72`(gray) · `#FFFFFF`

### 결과 — 발표 자료 핵심 완료

textbook + slides + 5 figures = 발표 가능 상태. 빌드만 환경 dep 설치 후 1회.
