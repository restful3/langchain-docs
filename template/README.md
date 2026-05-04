# template

Markdown → **리포트** (A4 PDF) + **슬라이드** (1280×720 16:9) 듀얼 빌더. 페르소나(워드마크·러닝 헤더·키커 텍스트·팔레트)는 단일 `brand.yaml` 한 파일로 분리되어 있어, 폴더 한 번 복사 + brand.yaml 한 번 수정으로 다른 출판물에 그대로 재사용된다.

자족 패키지 — 외부 의존성 없이 폴더만 다른 프로젝트로 복사 가능.

## 1. Install

```bash
pip install -r template/requirements.txt
```

PDF 렌더는 시스템에 **Chrome + chromedriver** 가 설치되어 있어야 한다 (Selenium headless). HTML 만 필요하면 `--html-only` 로 PDF 단계 스킵.

```bash
# Linux
sudo apt-get install -y google-chrome-stable chromium-driver
# macOS
brew install --cask google-chrome && brew install chromedriver
```

## 2. Quick start (코딩 에이전트 한 줄 호출)

```bash
# 리포트 — 콘텐츠 폴더에서 한 줄
python -m template build report path/to/content/

# 슬라이드 — MD 한 장에서 한 줄
python -m template build slides path/to/slides.md
```

`brand.yaml` 미존재 시 `template/brand.default.yaml` (AI Odyssey 페르소나) 가 자동 적용된다. 다른 페르소나는 `brand.yaml` 을 콘텐츠 폴더 안에 두거나 `--brand FILE` 로 명시.

레거시 호출 (`python -m template.build_report ...` / `.build_slides ...`) 도 그대로 동작.

## 3. brand.yaml — 페르소나 단일 conf

```yaml
brand:
  name: "AI Odyssey"
  sub: "Deep Research"
  signature: "YouTube · @AI_odysseys"
  running_header_left: "AI Odyssey · Independent Research"
  running_header_right: "AI ODYSSEY"
  cover_kicker: "Research Report"
  slides_kicker: "Research Deck"
  monogram: "AIO"
palette:
  primary: "#0F2C59"
  primary-deep: "#091F40"
  primary-active: "#2563EB"
  bg: "#FAFAF9"
  surface: "#FFFFFF"
  text: "#0F0F10"
  text-secondary: "#6B6B72"
  positive: "#059669"
  negative: "#E11D48"
  warning: "#D97706"
  # normalize: monochrome   # (옵션) 다색 콘텐츠를 단색+명도단계로 강등
```

해소 우선순위 (load_brand):

```text
--brand <file> > <content_dir>/brand.yaml > template/brand.default.yaml
```

오버라이드 파일은 부분 정의해도 무방 — 미정의 키는 default 에서 보충된다.

## 4. 두 빌더, 같은 brand.yaml

| 출력 | 진입점 | 입력 | 산출물 |
|---|---|---|---|
| 리서치 리포트 | `python -m template build report` | 콘텐츠 폴더 (NN_*.md) + `sections.yaml` | A4 HTML/PDF + 네이버 MD + PNG @2x |
| 발표 슬라이드 | `python -m template build slides` | 단일 MD 또는 *.md 디렉토리 | 1280×720 16:9 HTML/PDF |

## 5. Content convention — 리포트

```text
content/
├── 00_front_matter.md       # h1 + 메타 + ## Executive Summary (옵션)
├── 01_section1_*.md         # 본 섹션 (lexicographic 정렬)
├── 02_section2_*.md
├── ...
├── 99_references.md         # 각주 — ### Group / [^N]: body
├── sections.yaml            # 옵션 — 섹션 라벨 매핑
└── brand.yaml               # 옵션 — 페르소나 override
```

**필수 컨벤션:**

- 파일명 prefix `NN_` (2-digit). `--sections` 가 이 prefix 로 매칭.
- `00_front_matter.md` 는 옵션. h1 이 있으면 `--title` 미지정 시 커버 제목으로 사용된다.
- Executive Summary 를 출력하려면 `## Executive Summary` 헤딩(영문, slug `executive-summary`) 정확히 사용.

**선택 패턴 (`apply_visual_transforms` 가 인식):**

- `**핵심 메시지**: 본문` → hero callout
- `**실무 시사점 (...)**` 다음 블록 → insight callout
- `**표 N. 제목**` 다음 표 → cmp-table + 캡션 칩
- `**더 깊이 읽기**` 다음 리스트 → reading-more 박스
- `[risk:high]`, `[diff:mid|구현 복잡]` 인라인 토큰 → badge
- `<!-- hero-kpi: {kpis: [...], summary: "..."} -->` (00_front_matter.md 내부) → Executive Summary KPI 그리드
- `<!-- positioning-map: {title, subtitle, legend: [...]} -->` → Chart.js scatter map. 데이터 미제공 시 placeholder 제거

**hero-kpi 주석 예시:**

```html
<!-- hero-kpi:
{
  "kpis": [
    {"value": 75, "suffix": "%", "label": "메인 지표", "sub": "근거 한 줄"},
    {"value": 21, "suffix": "K+", "label": "두 번째 지표", "sub": "근거"}
  ],
  "summary": "한 줄 요약 — <strong>강조</strong> HTML 가능."
}
-->
```

## 6. Content convention — 슬라이드

```text
content/slides.md            # 또는 디렉토리 — *.md 사전순 concat
content/brand.yaml           # 옵션
```

**파일 구조:**

````markdown
---
title: 발표 제목
subtitle: 발표 부제 (커버용)
author: 발표자
version: v1 · 2026-05-01
date: 2026년 5월 1일
---

<!-- slide: variant=cover -->
# 발표 제목

> 한 줄 부제

<!-- slide: variant=section, num=01 -->
# 섹션 01.<br>섹션 제목

> 섹션 부제

<!-- slide: tag="Section 01 · Hook" -->
# 일반 슬라이드 제목

> 부제 (blockquote → .slide-subtitle)

본문 마크다운, 표 등...

<!-- slide: variant=closing -->
# 감사합니다

> 한 줄 인용
````

frontmatter 의 `org` / `kicker` 는 brand.yaml 의 `name` / `slides_kicker` 가 default 로 들어오므로, 같은 브랜드를 쓰는 한 적지 않아도 된다.

**Slide variants:** `default`(생략) / `cover` / `section` / `closing`.

**Slide meta keys (`<!-- slide: ... -->`):** `variant`, `tag`, `num`, `aria`, `untitled`, `kicker`.

## 7. CLI reference

### Report

```text
python -m template build report SRC_DIR [options]
```

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--out DIR` | `SRC_DIR.parent` | 산출물 저장 폴더 |
| `--brand FILE` | None | brand.yaml 경로. 미지정 시 `<src>/brand.yaml > brand.default.yaml` |
| `--tier {1,2,all}` | `all` | Tier 1 = HTML/PDF, Tier 2 = 네이버 MD + PNG |
| `--name STEM` | `detailed_report_external` | 출력 stem |
| `--title TEXT` | (frontmatter h1 → brand.name + " Report") | 커버 제목 |
| `--subtitle TEXT` | (frontmatter 메타) | 커버 부제 |
| `--version-badge TEXT` | "" | 커버 우상단 버전 |
| `--doc-title TEXT` | (== --title) | HTML `<title>` |
| `--author TEXT` | brand.name | 커버 저자 |
| `--date TEXT` | "" | 커버 발행일 |
| `--html-only` | (false) | PDF 스킵 |
| `--monochrome` | (false) | 다색 SVG/배경 → 페르소나 단색+명도단계 |
| `--sections "02,03"` | None (전체) | NN_*.md prefix 부분집합 |
| `--pages "5-8"` | None | PDF 페이지 범위 추출 (CDP pageRanges) |
| `--no-cover` | (false) | 커버 페이지 스킵 |
| `--no-toc` | (false) | 목차 스킵 |
| `--no-references` | (false) | References 부록 스킵 |
| `--continuous` | (false) | 자연 흐름 모드 (build_local.py hack 정식화) |
| `--per-section` | (false) | 통합 PDF + 섹션별 개별 PDF 동시 생성 |

### Slides

```text
python -m template build slides SRC [options]
```

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `SRC` (위치) | (필수) | `slides.md` 또는 *.md 디렉토리 |
| `--out DIR` | `SRC.parent` | 산출물 저장 폴더 |
| `--brand FILE` | None | brand.yaml 경로 |
| `--html-only` | (false) | PDF 스킵 |
| `--monochrome` | (false) | 동일 |
| `--slides "1,3,5-7"` | None (전체) | 1-based H1 인덱스 부분집합 |
| `--variant cover,default` | None | variant 화이트리스트 |
| `--per-slide` | (false) | 슬라이드 한 장씩 개별 PDF |

## 8. 부분 빌드 — 코딩 에이전트용 한 줄 호출

```bash
# 섹션 02, 03 만 + cover/toc/refs 제외
python -m template build report content/ --sections 02,03 --no-cover --no-toc --no-references

# 빌드 후 5\~8 페이지만 추출
python -m template build report content/ --pages 5-8

# 슬라이드 1·3·7 만
python -m template build slides content/slides.md --slides 1,3,7

# 섹션별 개별 PDF + 통합 PDF 동시
python -m template build report content/ --per-section

# 슬라이드 한 장씩 분리 PDF
python -m template build slides content/slides.md --per-slide

# 자연 흐름 + 커버/TOC 없음 (build_local.py 의 hack 대체)
python -m template build report content/ --continuous --no-cover --no-toc

# 다색 SVG 단색 강등
python -m template build report content/ --monochrome
```

## 9. Output artifacts

- **Report Tier 1**: `<out>/<name>.{html,pdf}` (A4 portrait)
- **Report Tier 2**: `<out>/<name>.naver.md` + `<src>/figs/figure-NN.png` (@2x)
- **Slides**: `<src.parent>/<stem>.{html,pdf}` (1280×720 16:9 landscape)
- **--per-section**: `<out>/<name>-sNN.{html,pdf}` (각 섹션 별 추가)
- **--per-slide**: `<out>/<stem>-NN.pdf`

## 10. Customization (1-knob — brand.yaml)

페르소나 (워드마크·러닝 헤더·키커·시그니처·모노그램) 는 모두 `brand.yaml` 에서 한 번에 정의된다. 빌드 시 SHELL 의 `<style id="brand-vars">:root{...}</style>` 가 동적으로 주입되어, theme CSS 의 `var(--running-header-left, ...)` fallback 을 override 한다.

다음 항목은 brand.yaml 에서 관리하지 *않는다* — theme 수준 디자인 토큰:

- spacing/radius/elevation 단계 ([DESIGN.md](DESIGN.md) 참조)
- 컴포넌트 레이아웃 (`.report-section` 그리드, 표 스타일 등)
- 차트 스크립트 (`report.js`)

이들은 모든 페르소나가 공유하는 디자인 시스템 — 손대면 빌더 전체에 영향이 간다.

## 11. Architecture

```text
build_report.py  ─→  brand.py           (load_brand · make_brand_style_block)
                 ─→  core.py            (마크다운 → HTML · visual transforms · hero-kpi · positioning-map)
                 ─→  palette.py         (COLOR_MAP + MONOCHROME_MAP 정규화)
                 ─→  render.py::html_to_pdf      (Selenium → A4 PDF · pageRanges)
                 ─→  theme_report.css   (A4 토큰 + 컴포넌트 + .continuous-mode)
                 ─→  report.js          (TOC · 차트 · 카운터)

build_slides.py  ─→  brand.py           (동일 헬퍼)
                 ─→  core.py::build_md  (마크다운 파서만 공유)
                 ─→  palette.py         (안전장치)
                 ─→  render.py::slides_to_pdf    (Selenium → 1280×720 PDF · pageRanges)
                 ─→  theme_slides.css   (슬라이드 토큰 + 컴포넌트)
                 ─→  deck.js            (키보드 nav · 테마 토글 · PNG export)
```

`render.py` 의 `make_header(brand)` / `make_footer(brand)` 는 CDP fallback 헤더/푸터 (CSS @page 마진박스가 동작하지 않을 때) 용. 일반 경로는 theme CSS 의 `@page` + var() 기반.

## 12. Troubleshooting

| 증상 | 원인 | 해결 |
|---|---|---|
| `selenium.common.exceptions.WebDriverException` | chromedriver 버전 불일치 | `chromedriver --version` ↔ Chrome 메이저 일치 확인. `--html-only` 우회 가능 |
| PDF 폰트가 시스템 기본으로 렌더 | `document.fonts.ready` 전에 PDF 캡쳐 | `render.py` 의 `setTimeout` 값 늘려 폰트 로드 대기 |
| (리포트) Tier 2 PNG 누락 | `<figure>` 안에 `.fig-chip` 없음 | `<span class="fig-chip">그림 N</span>` 추가 |
| (리포트) Executive Summary 미출력 | h2 헤딩이 영문 아님 | `## Executive Summary` 정확히 사용 |
| 페르소나 텍스트가 다른 페르소나로 안 바뀜 | brand.yaml 누락 또는 위치 오류 | `<content>/brand.yaml` 또는 `--brand FILE` 명시 |
| (슬라이드) 슬라이드 분할 안 됨 | H1(`# `) 없음 | 각 슬라이드 시작에 `# 제목` 한 줄 |
| (슬라이드) 오버플로우 경고 | 본문이 1280×720 영역 초과 | 본문 분할하거나 폰트 크기 조정 |

## 13. Repository hygiene

이 패키지는 **brand.yaml 한 파일만 갈아끼우면 그대로 재사용**되는 페르소나-중립 빌더다. 다른 페르소나가 필요하면:

1. 콘텐츠 폴더 안에 `brand.yaml` 작성 (또는 `--brand FILE` 로 명시)
2. 색상은 `palette:` 섹션, 텍스트는 `brand:` 섹션. 누락된 키는 default 에서 보충됨
3. 다색 SVG 콘텐츠가 페르소나에서 어긋나면 `--monochrome` 또는 `palette.normalize: monochrome`

빌드 엔진 (`core.py`, `render.py`, `palette.py`, theme CSS) 은 손대지 않는다.

페르소나-중립 정도가 부족해 보이면 `examples/minimal_report/` 와 `examples/minimal_slides/` 가 brand.yaml 만으로 동작하는 reference. 같은 패턴으로 새 콘텐츠 폴더를 시작.
