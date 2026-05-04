# ai_odyssey_publisher

AI Odyssey 페르소나(**Deep Navy** 단색 액센트) 의 외부 공개 출판물 듀얼 빌더. 한 폴더에 **리포트 빌더**(A4 PDF + 네이버 마크다운) + **슬라이드 빌더**(1280×720 16:9) 가 함께 들어 있다.

자족 패키지 — 외부 의존성 없이 폴더만 다른 프로젝트로 복사해서 사용 가능.

## 1. Install

```bash
pip install -r ai_odyssey_publisher/requirements.txt
```

PDF 렌더는 시스템에 **Chrome + chromedriver** 가 설치되어 있어야 한다 (Selenium headless). HTML 만 필요하면 `--html-only` 로 PDF 단계 스킵.

```bash
# Linux
sudo apt-get install -y google-chrome-stable chromium-driver
# macOS
brew install --cask google-chrome && brew install chromedriver
```

## 2. 두 빌더, 한 페르소나

| 출력 | 빌더 | 입력 | 산출물 |
|---|---|---|---|
| 리서치 리포트 | `build_report.py` | 콘텐츠 폴더 (00\~99 컨벤션) + `sections.yaml` | A4 HTML/PDF (100p+) + 네이버 MD + PNG @2x |
| 발표 슬라이드 | `build_slides.py` | 단일 MD (frontmatter + H1 분할) | 1280×720 16:9 HTML/PDF |

디자인 토큰 · 색상 팔레트 · AI Odyssey 워드마크는 **공유**. 콘텐츠 마크다운은 빌더별로 다른 컨벤션을 따른다 (리포트와 슬라이드는 정보 밀도가 다름).

## 3. Quick start — 리포트

```bash
cp -r templates/ai_odyssey_publisher /path/to/new_report/
cd /path/to/new_report
mkdir content && $EDITOR content/00_front_matter.md   # 본문 작성

cp ai_odyssey_publisher/sections.example.yaml content/sections.yaml
$EDITOR content/sections.yaml                          # 섹션 라벨 매핑

python -m ai_odyssey_publisher.build_report content/ --tier all \
    --title "내 리포트 제목" \
    --subtitle "한 줄 부제" \
    --version-badge "v1.0 · 2026-05-01"
```

출력: `./detailed_report_external.{html,pdf,naver.md}` + `./content/figs/figure-NN.png`

샘플 검증: [examples/minimal_report/](examples/minimal_report/) README 참조.

## 4. Quick start — 슬라이드

```bash
$EDITOR content/slides.md   # frontmatter + H1 분할

python -m ai_odyssey_publisher.build_slides content/slides.md
```

출력: `./content/slides.{html,pdf}`. 디렉토리도 입력 가능 (`*.md` 파일들을 사전순 concat).

샘플 검증: [examples/minimal_slides/](examples/minimal_slides/) README 참조.

## 5. Content convention — 리포트

```text
content/
├── 00_front_matter.md       # 필수 — h1 + 메타 + ## Executive Summary
├── 01_section1_*.md         # 본 섹션 (lexicographic 정렬)
├── 02_section2_*.md
├── ...
├── 07_appendix.md           # 부록 (sections.yaml 의 kicker 가 "부록" 이면 첫 h2 유지)
├── 99_references.md         # 각주 — ### Group / [^N]: body
└── sections.yaml            # 옵션 — 섹션 라벨 매핑
```

**필수 컨벤션:**

- 파일명 prefix `NN_` (2-digit)
- `00_front_matter.md` 안에 정확히 `## Executive Summary` 헤딩 (영문 그대로) — slug `executive-summary` 매칭
- `99_references.md` 의 각주: `[^N]: 본문`. `### Group` 헤딩으로 그룹핑

**선택 패턴 (`apply_visual_transforms` 가 인식):**

- `**핵심 메시지**: 본문` → hero callout
- `**실무 시사점 (...)**` 다음 블록 → insight callout
- `**표 N. 제목**` 다음 표 → cmp-table + 캡션 칩
- `**더 깊이 읽기**` 다음 리스트 → reading-more 박스
- `[risk:high]`, `[diff:mid|구현 복잡]` 인라인 토큰 → badge 컴포넌트
- `<!-- positioning-map -->` 주석 → 3사 scatter map (Chart.js)

## 6. Content convention — 슬라이드

```text
content/slides.md
```

**파일 구조:**

````markdown
---
title: 발표 제목
subtitle: 발표 부제 (커버 슬라이드용)
author: 발표자
version: v1 · 2026-05-01
org: AI Odyssey
kicker: Research Deck
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

본문 마크다운, 인라인 SVG, 표 등...

<!-- slide: variant=closing -->
# 감사합니다

> 한 줄 인용
````

**Slide variants:**

| variant | 용도 |
|---|---|
| (생략) `default` | 일반 콘텐츠 슬라이드. 헤더(brand-mark + section-tag) + 제목 + 본문 + 푸터(org + 페이지) |
| `cover` | 첫 슬라이드. 큰 제목 + 부제 + 메타데이터 |
| `section` | 섹션 디바이더. 큰 번호 + 제목 + 부제 |
| `closing` | 마지막 슬라이드. "감사합니다" + 인용 |

**Slide meta keys (`<!-- slide: ... -->`):**

- `variant=cover|section|closing` — 슬라이드 타입
- `tag="Section 01 · Hook"` — 헤더 우상단 섹션 태그 (default 슬라이드만)
- `num=01` — 섹션 디바이더 번호 (section variant)
- `aria="..."` — 접근성 라벨
- `untitled` — 제목 영역 숨김 (이미지·SVG 가 큰 슬라이드용)
- `kicker="Q&A"` — closing 슬라이드 상단 kicker

## 7. `sections.yaml` (리포트 전용)

콘텐츠 폴더 안에 두는 작은 YAML. 부재 시 파일명에서 자동 생성된다.

```yaml
sections:
  "01_section1_overview.md":     ["01", "섹션 01", "Computer Use",        "무엇이고, 왜 지금인가"]
  "07_appendix.md":              ["07", "부록",    "",                    "용어집 · 체크리스트"]
```

| 필드 | 설명 |
|---|---|
| number | 2-digit zero-padded |
| kicker | 디바이더 상단 칩. `"부록"` 으로 두면 첫 h2 유지 |
| title | 디바이더 큰 제목. 빈 문자열 = 미표시 |
| subtitle | 제목 아래 한 줄 캡션 |

YAML 부재 시 `01_anything.md` → `("01", "섹션 01", "", "")` 자동 생성.

## 8. CLI reference

### Report

```text
python -m ai_odyssey_publisher.build_report SRC_DIR [options]
```

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--out DIR` | `SRC_DIR.parent` | 산출물 저장 폴더 |
| `--tier {1,2,all}` | `all` | 빌드 대상 |
| `--name STEM` | `detailed_report_external` | 출력 stem |
| `--title TEXT` | (예시값) | 커버 제목 |
| `--subtitle TEXT` | (예시값) | 커버 부제 |
| `--version-badge TEXT` | (예시값) | 커버 우상단 버전 |
| `--author TEXT` | `AI Odyssey` | 커버 저자 |
| `--date TEXT` | (예시값) | 커버 발행일 |
| `--html-only` | (false) | PDF 스킵 |

### Slides

```text
python -m ai_odyssey_publisher.build_slides SRC [options]
```

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `SRC` (위치) | (필수) | 단일 .md 또는 *.md 디렉토리 |
| `--out DIR` | `SRC.parent` | 산출물 저장 폴더 |
| `--html-only` | (false) | PDF 스킵 |

슬라이드는 frontmatter 가 메타 소스이므로 CLI 옵션 최소.

## 9. Output artifacts

**Report Tier 1**: `<out>/<name>.{html,pdf}` (A4 portrait, 100p+)
**Report Tier 2**: `<out>/<name>.naver.md` + `<src>/figs/figure-NN.png` (@2x)
**Slides**: `<src>/<stem>.{html,pdf}` (1280×720 16:9 landscape)

## 10. Customization (4 knobs)

| 항목 | 위치 | 비고 |
|---|---|---|
| 커버 워드마크 | [build_report.py::build_cover_external](build_report.py) · [build_slides.py::render_cover](build_slides.py) | "AI Odyssey · External Publishing" 텍스트 |
| 러닝 헤더 텍스트 | [theme_report.css](theme_report.css) `@page` (top-left / top-right) · [render.py](render.py) `HEADER_TEMPLATE` · [theme_slides.css](theme_slides.css) `.slide--section::after` | 모든 페이지에 노출되는 브랜드 텍스트. 페르소나의 가장 visible 한 표면 — fork 시 첫 번째로 갈아끼울 것 |
| 색상 매핑 | [svg_recolor.py::COLOR_MAP](svg_recolor.py) | 콘텐츠 인라인 SVG 색상 일괄 치환 룰 |
| 테마 토큰 | [theme_report.css](theme_report.css) · [theme_slides.css](theme_slides.css) `:root` | `--brand-primary` 등 CSS 변수 |

이 넷을 건드리면 페르소나가 깨질 수 있다 — AI Odyssey 동결 패키지의 의도와 어긋난다면 fork 권장.

## 11. Architecture

```text
build_report.py  ─→  core.py            (마크다운 → HTML · visual transforms)
                 ─→  svg_recolor.py     (LG 잔재 → Deep Navy 일괄 치환)
                 ─→  render.py::html_to_pdf      (Selenium → A4 PDF)
                 ─→  theme_report.css   (A4 리포트 CSS 토큰 + 컴포넌트)
                 ─→  report.js          (TOC · 차트 · 카운터)

build_slides.py  ─→  core.py::build_md  (마크다운 파서만 공유)
                 ─→  svg_recolor.py     (안전장치)
                 ─→  render.py::slides_to_pdf    (Selenium → 1280×720 PDF)
                 ─→  theme_slides.css   (슬라이드 CSS 토큰 + 컴포넌트)
                 ─→  deck.js            (키보드 nav · 테마 토글 · PNG export)
```

`core.py` 는 양 빌더 공유. `render.py` 안에 `html_to_pdf` (A4) + `slides_to_pdf` (16:9) 두 함수.

## 12. Troubleshooting

| 증상 | 원인 | 해결 |
|---|---|---|
| `selenium.common.exceptions.WebDriverException` | chromedriver 버전 불일치 | `chromedriver --version` ↔ Chrome 메이저 일치 확인. `--html-only` 우회 가능 |
| PDF 폰트가 시스템 기본으로 렌더 | `document.fonts.ready` 전에 PDF 캡쳐 | `render.py` 의 `setTimeout` 값 늘려 폰트 로드 대기 |
| (리포트) Tier 2 PNG 누락 | `<figure>` 안에 `.fig-chip` 없음 | `<span class="fig-chip">그림 N</span>` 추가 |
| (리포트) Executive Summary 미출력 | h2 헤딩이 영문 아님 | `## Executive Summary` 정확히 사용 |
| (슬라이드) 슬라이드 분할 안 됨 | H1(`# `) 없음 | 각 슬라이드 시작에 `# 제목` 한 줄 |
| (슬라이드) 오버플로우 경고 | 본문이 1280×720 영역 초과 | 본문 분할하거나 폰트 크기 조정 |

## 13. Repository hygiene

이 패키지는 **단일 페르소나 동결 키트**. 다른 페르소나가 필요하면:

1. 폴더 통째 복사 → 새 이름 (`ai_odyssey_publisher_rose/` 등)
2. `svg_recolor.py::COLOR_MAP` 매핑 hex 갈아치움
3. `theme_report.css` · `theme_slides.css` 의 `:root` 변수 갈아치움
4. `build_report.py::build_cover_external` · `build_slides.py::render_cover` 의 워드마크 텍스트 갈아치움
5. **러닝 헤더 텍스트 갈아치움** — `theme_report.css` 의 `@page` `top-left`/`top-right` + `render.py` 의 `HEADER_TEMPLATE` + `theme_slides.css` 의 `.slide--section::after`. 누락 시 모든 페이지에 이전 페르소나의 브랜드 텍스트가 새어나간다.

빌드 엔진 (`core.py`, `render.py`, 빌더 로직) 은 손대지 않아도 동작한다.
