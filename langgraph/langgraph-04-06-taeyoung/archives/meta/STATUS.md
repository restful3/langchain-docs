# STATUS — LangGraph 04~06 발표 자료

> 진행 추적. 최신 항목이 위.

## 2026-05-30

- ✅ BRAINSTORM / DESIGN 확정 — 세 문서 통합 → 핵심 주제 5개, worked example=이메일 에이전트
- ✅ 폴더 구조 생성 (`langgraph-04-06-taeyoung/`)
- ✅ `archives/meta/{BRAINSTORM,DESIGN,STATUS}.md`
- ✅ `content/textbook.md` 본문 (§0~§6 + 부록 A/B)
- ✅ `content/sections.yaml`, `README.md`
- ✅ HTML 미리보기 빌드 검증 — `content/textbook.html` (46KB, 코드블록 19개 정상, `\~`→`~` 정상)
  - `python -m template build report content/ --html-only --tier 1 --name textbook`
- ✅ `content/figs/*.svg` — 9개 시각화 추가, §2.1 mermaid → SVG 교체
  - fig01 세 부품 / fig02 에이전트 그래프 / fig03 설계5단계 / fig04 스텝유형 / fig05 State raw / fig06 에러전략 / fig07 interrupt·resume / fig08 granularity / fig09 로컬 토폴로지
  - Chrome headless 로 9개 전수 렌더 검증 (한글·화살표·오버플로우 OK). HTML 재빌드 51KB
- ⬜ (후속) `scripts/*.py` — 이메일 에이전트 실행 예제 (본문 코드와 sync)
- ✅ `content/slides.md` + `slides.html` — 19장(cover + 5 섹션 divider + 12 콘텐츠 + closing), figs 9개 임베드, 빌더 오버플로우 경고 0
  - `python -m template build slides content/slides.md --html-only`
  - 기본 AI Odyssey 브랜드 사용(week1 동일). LangGraph 전용 브랜드 원하면 content/brand.yaml 추가
- ✅ 슬라이드 Codex 리뷰 — Critical 0·Major 1·Minor 4·Nit 3, **전부 반영**. 재빌드 19장·오버플로우 0
  - thread_id/장기재개·durable 전제·async durability 표현 정밀화, changelog 행 분리, 자료표기 수정 등
  - 기록: `archives/reviews/2026-05-30-slides-{codex,decisions}.md`
- ⬜ (후속) PDF 빌드 — chromedriver 미설치. 설치 후 `python -m template build report content/`

## 2026-05-30 (Codex 리뷰)

- ✅ 교과서 Codex 피어리뷰 — **2라운드 만에 최종 승인** (`===CODEX_FINAL_APPROVAL===`)
  - R1: 13건(Critical 0·Major 5·Minor 6·Nit 2) → ACCEPT 11 / REJECT 2 / DEFER 1
  - 영속성·interrupt 규칙·축약코드·langgraph.json·`or {}` 버그·용어 통일 등 반영
  - 기록: `archives/reviews/2026-05-30-textbook-{round-1-codex,round-1-decisions,final-summary}.md`
- ⬜ (DEFER) changelog 2026 릴리스 실값 — 발표 시점 공식 changelog 확인 또는 사용자 요청 시 WebFetch 로 추가

## 2026-05-30 (그림 리뷰 + 그림/표 번호)

- ✅ 그림(SVG) Codex 리뷰 — Critical 0·Major 0·Minor 4·Nit 3. Minor 4건 + Nit 7(번호 순서) 반영
  - fig 번호를 문서 순서와 일치(5단계=그림2, 이메일그래프=그림3), 파일명도 fig02/fig03 스왑
  - 기록: `archives/reviews/2026-05-30-figures-{codex,decisions}.md`
- ✅ 사용자 지시 1차: SVG 내 제목·캡션 문장 제거, 그림 1~9 / 표 1~9 독립 번호 제목 통일 부착
- ✅ 사용자 지시 2차(미니멀): 박스 내부 설명·키워드까지 비우고 **식별 이름·핵심 토큰만** 유지(fig01·02·04·05·06·07·09 재작성, 박스 크기·중앙정렬 재조정). 제거 정보는 캡션·표가 전담. fig03(그래프)·fig08(비교)은 이미 식별 라벨 위주라 유지. 변경 figs Chrome 재렌더 검증
- ✅ HTML 재빌드 52KB, 수정 SVG Chrome 재렌더 검증

## 2026-05-30 (로컬 self-contained HTML 사이트)

- ✅ `build_local.py` + `site/` — claude-code-officeflow/course/site/build_units.py 패턴 적용
  - figs SVG → data URI, deck.js·theme_slides.css → inline 으로 **자족형 HTML** (../../../template 깨짐·CDN 의존 없이 file:// 에서 렌더)
  - `site/index.html`(카드형 랜딩) + `site/report.html`(교과서, figs 9 인라인) + `site/slides.html`(19장, deck+figs 인라인)
  - report 빌드는 `--sections 01` 로 01_textbook.md 만 (content/ 에 slides.md 공존 → 미지정 시 num='??' 크래시)
  - 잔여 외부참조: Google Fonts(없으면 시스템 폰트 폴백) + 미사용 CDN(Chart.js·html-to-image) — officeflow 동일
  - 열기: `xdg-open site/index.html` (서버 불필요)
  - index·report·slides 모두 Chrome file:// 렌더 검증
- ✅ 로컬 사이트 Codex 리뷰 — Critical 3·Major 4·Minor 3·Nit 2, **핵심 전부 반영**
  - **C1 실제 버그 수정**: report.html 이 theme_report.css·report.js 를 repo 절대경로 참조하던 것 → 인라인. /tmp 복사본 렌더로 포터블 실증
  - post-build `validate()`(허용외 외부참조/누락/figs수 불일치 시 빌드 실패), re.subn 카운트 assert, preflight, fig_inventory, figs 정규식 확장, index aria
  - 정책 명문화: 렌더 필수자산만 인라인 / 폰트·cdn.jsdelivr 는 허용 외부참조
  - 기록: `archives/reviews/2026-05-30-localsite-{codex,decisions}.md`
  - ✅ round 2 재리뷰 → **`===CODEX_FINAL_APPROVAL===`** (추가 수정 없음, 최종 승인)

## 메모

- PDF 우선순위 낮음 (사용자 지시: "PDF 는 나중에, 우선 상세 교과서에 집중").
- chromedriver: 시스템에 Chrome 148 은 있으나 chromedriver 없음. 최신 Selenium 자동 다운로드 시도하거나 `--html-only`.
- 본문 코드 블록은 06 원문 기준. 후속 `scripts/` 작성 시 양쪽 sync 유지.
