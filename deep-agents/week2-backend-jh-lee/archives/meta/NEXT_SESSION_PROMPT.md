# 세션 재시작 프롬프트 — 2주차 발표 자료 (jh-lee / Backends)

## 복사용 프롬프트

```text
deep-agents/week2-backend-jh-lee/ 작업을 이어서 진행한다.
현재 Phase 0·1·2·3·4·5 완료. 콘텐츠 측면(textbook + slides + 5 figures)은 전부 채워짐.
남은 단계는 빌드 + 발표 리허설.

빌드 사전: pip install -r /Users/jaden/projects/langchain-docs/template/requirements.txt
빌드:      python archives/source/build.py --html-only  (HTML 1차 검증)
           python archives/source/build.py              (PDF — Chrome + chromedriver 필요)

산출 검증: ls content/  → textbook.{html,pdf}, slides.{html,pdf}, figs/fig0[1-5]*.svg
발표 리허설: 슬라이드 22장 × 약 55초 페이스 = 정확히 20분

사용자 확인 필요: gemma4:31b 가용성 (`ollama list | grep gemma`).
```

## 작업 폴더 (절대경로)

`/Users/jaden/projects/langchain-docs/deep-agents/week2-backend-jh-lee/`

## 핵심 컨텍스트

- 발표자: jh-lee
- 주제: Deep Agents Backends (State / Filesystem / Store / Composite + virtual FS + policy)
- 원문: `archives/original_docs/05-backends.md` (영) / `_ko.md` (한)
- 패키지 소스 스냅샷: `archives/original_docs/deepagents_backends/` (SHA 고정, **수정 금지**)
- 빌드 명령: `python archives/source/build.py`

## 결정된 사항 (변경 금지)

- 폴더 구조는 week1 1:1 미러
- 데모는 4종 (4개 백엔드 1:1)
- 텍스트북 분량 목표: A4 15~20p

## 현재 상태 — Phase 0·1·2·3·4·5 완료, 빌드 + 리허설만 남음

`archives/meta/STATUS.md` 의 진행 게이지 참조. 확정된 사항:
- 슬라이드 22장 (`DESIGN.md` §4 매핑표)
- LLM = Ollama `gemma4:31b` (4개 스크립트·노트북·requirements 일괄 반영)
- 가상 FS 예시 = S3 스타일 (§7)
- 보강 자료 5건 등재 (`archives/research/INDEX.md`)
- 텍스트북 본문 619줄 (`archives/source/01_textbook.md`)
- 슬라이드 22장 (`archives/source/slides.md`)
- 다이어그램 5종 (`archives/source/figs/`, `content/figs/`)

## 새 세션 시작 시 읽는 순서 (1순위 → 5순위)

1. `archives/meta/STATUS.md`
2. 본 파일
3. `archives/meta/PLAN.md`
4. `archives/meta/BRAINSTORM.md` (미결 3개)
5. `archives/original_docs/05-backends.md`

## 다음 액션 — Phase 4 (SLIDES)

### 4-A. 슬라이드 본문 (`archives/source/slides.md`)

DESIGN.md §4 22장 매핑표를 따라 본문 채움. 슬라이드별 형식:

```markdown
## N. 슬라이드 제목

- 글머리 4~6개
- (해당 시) 짧은 코드 블록 1개
- (해당 시) figs/figNN_*.svg 참조
```

### 4-B. 다이어그램 5종 (`content/figs/`)

DESIGN.md §7 명세대로 fig01~fig05 SVG 작성 (Phase 5). 슬라이드는 SVG 가 없어도 빌드는 가능.

### 4-C. 빌드

```bash
python archives/source/build.py             # HTML + PDF (한 번에)
python archives/source/build.py --html-only # PDF 스킵 (검토 용)
```

산출물: `content/textbook.{pdf,html}` + `content/slides.{pdf,html}`

### 4-D. Verify

- 슬라이드 22장 모두 존재 (DESIGN.md §4 표 대조)
- 발표 시간 20분 시뮬레이션 (1장 ~55초 페이스)
- PDF/HTML 모두 정상 렌더 (특히 코드 블록·표·`fig` 참조)

### 4-E. ✋ 사용자 최종 검수

슬라이드 완성 후 Phase 5 (다이어그램 SVG) 또는 발표 리허설 진입 승인 받기.

## 작업 컨벤션

- 한글 텍스트, 영문 용어는 코드폰트 또는 괄호 병기
- 코드 인용 라인 번호는 `scripts_py/*.py` 실파일 기준
- 원문(`05-backends.md`, `deepagents_backends/*.py`) 절대 수정 금지
- mermaid → svg 변환은 직접 svg 작성 권장 (week1 패턴)

## 미결정 / 보류 항목

- 04-harness 와의 페어링 여부 — 본 주차는 백엔드 단독 (사용자 확정)
- Sandbox / Local shell / LangSmith 백엔드 다룰지 (현재: 부록 후보)

## 시작 명령

```bash
cd /Users/jaden/projects/langchain-docs/deep-agents/week2-backend-jh-lee
cat archives/meta/STATUS.md
cat archives/meta/BRAINSTORM.md  # §9 결정 항목 확인
```

## 변경 시 갱신 포인트

`STATUS.md` 게이지 + 본 파일 "현재 상태" 줄.
