---
version: alpha
name: AI Odyssey · External Publishing
description: Deep Navy 단색 액센트의 외부 공개 출판물(A4 리포트 + 16:9 슬라이드) 디자인 시스템. Inter + Noto Sans KR. Stitch DESIGN.md alpha 사양 준수.
colors:
  primary: "#0F2C59"
  primary-deep: "#091F40"
  primary-active: "#2563EB"
  on-primary: "#FFFFFF"
  bg: "#FAFAF9"
  surface: "#FFFFFF"
  surface-hover: "#F5F5F4"
  text: "#0F0F10"
  text-secondary: "#6B6B72"
  positive: "#059669"
  negative: "#E11D48"
  warning: "#D97706"
typography:
  display:
    fontFamily: Inter, Noto Sans KR, sans-serif
    fontWeight: 900
    fontSize: 52px
    letterSpacing: -0.03em
    lineHeight: 1.08
  h1:
    fontFamily: Inter, Noto Sans KR, sans-serif
    fontWeight: 800
    fontSize: 42px
    letterSpacing: -0.028em
    lineHeight: 1.1
  h2:
    fontFamily: Inter, Noto Sans KR, sans-serif
    fontWeight: 800
    fontSize: 32px
    letterSpacing: -0.024em
    lineHeight: 1.15
  h3:
    fontFamily: Inter, Noto Sans KR, sans-serif
    fontWeight: 700
    fontSize: 22px
    letterSpacing: -0.02em
    lineHeight: 1.2
  body:
    fontFamily: Inter, Noto Sans KR, sans-serif
    fontWeight: 400
    fontSize: 16px
    letterSpacing: -0.01em
    lineHeight: 1.7
  caption:
    fontFamily: Inter, Noto Sans KR, sans-serif
    fontWeight: 500
    fontSize: 12px
    lineHeight: 1.45
  eyebrow:
    fontFamily: Inter, Noto Sans KR, sans-serif
    fontWeight: 800
    fontSize: 11px
    letterSpacing: 0.22em
  mono:
    fontFamily: JetBrains Mono, monospace
    fontWeight: 500
    fontSize: 14px
spacing:
  xxs: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 56px
  xxxl: 72px
rounded:
  none: 0
  xs: 2px
  sm: 4px
  md: 8px
  lg: 12px
  pill: 999px
elevation:
  none: none
  card: 0 6px 40px rgba(0,0,0,0.08)
  stage: 0 24px 80px rgba(15,44,89,0.10)
components:
  section-tag:
    textColor: "{colors.primary}"
    typography: "{typography.eyebrow}"
  link:
    textColor: "{colors.primary}"
    typography: "{typography.body}"
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: 8px 16px
  button-primary-hover:
    backgroundColor: "{colors.primary-deep}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: 8px 16px
  brand-mark:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    typography: "{typography.h3}"
  body-text:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.text}"
    typography: "{typography.body}"
  caption:
    textColor: "{colors.text-secondary}"
    typography: "{typography.caption}"
  link-hover:
    backgroundColor: "{colors.surface-hover}"
    textColor: "{colors.primary}"
    typography: "{typography.body}"
  accent-dark:
    textColor: "{colors.primary-active}"
    typography: "{typography.body}"
  callout-positive:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.positive}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: 12px 16px
  callout-warning:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.warning}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: 12px 16px
  callout-negative:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.negative}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: 12px 16px
  fig-chip:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.eyebrow}"
    rounded: "{rounded.pill}"
    padding: 2px 8px
  title-rule:
    backgroundColor: "{colors.primary}"
    rounded: "{rounded.xs}"
  cover-gradient:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.text}"
---

## Overview

진중한 아카이브 톤의 리서치 리포트 디자인 시스템. NYT The Upshot · Stratechery · ben-evans.com 계열. 본문은 거의 무채색, 액센트는 **Deep Navy `#0F2C59` 단색**. 형광·고채도 보조 색 없음.

**디자인 헌장 5줄.**

1. **액센트는 진청 한 색.** 한 페이지에 액센트는 2곳 이하.
2. **숫자·코드는 모노스페이스.** `tabular-nums` 로 정렬 일관.
3. **여백이 정보 위계를 만든다.** 단락 간 24\~32px, 섹션 간 56\~72px.
4. **AI 에이전트가 읽을 것을 가정한다.** 토큰 + 본문 근거를 함께 둬 사람·모델 모두에게 "왜 이 색인가" 를 설명한다.
5. **본문 line-height 는 1.7.** 한글 모바일 가독성 우선.

> **사양 외 카테고리 주의.** Stitch DESIGN.md alpha 사양은 colors / typography / rounded / spacing / components 5개만 정의한다. 본 헌장의 `elevation:` 토큰은 사양 외 확장이며, 공식 lint 는 이를 검증하지 않는다.

## Components

| 컴포넌트 | 핵심 스타일 |
| --- | --- |
| `brand-mark` | `surface` 위 `4px solid primary` 좌측 보더 + 워드마크 |
| `section-tag` | `eyebrow` 타이포 + `primary` 색 |
| `title-rule` | 56×4px linear-gradient(`primary` → `primary-deep`) + `rounded.xs` |
| `fig-chip` | "그림 N" 칩, `primary` 배경 + `on-primary` 텍스트 |
| `link` | `primary` 색 + 1px 30% alpha 언더라인 |
| `link-hover` | `surface-hover` 배경 + 풀 알파 언더라인 |
| `button-primary` | `primary` 배경 + `on-primary` 텍스트 + `rounded.md` |
| `button-primary-hover` | `primary-deep` 배경 |
| `callout-positive` | `surface` + 좌측 `positive` 보더 + 0.08 alpha 배경 |
| `callout-warning` | `surface` + 좌측 `warning` 보더 + 0.08 alpha 배경 |
| `callout-negative` | `surface` + 좌측 `negative` 보더 + 0.08 alpha 배경 |
| `accent-dark` | `primary-active` 텍스트 (다크 테마 강조 · 라이트 테마 본문 사용 금지) |
| `cover-gradient` | radial(primary 8%) + linear(white→bg) 커버 배경 |

> **WCAG false positive.** `callout-positive/warning` 의 frontmatter 정의는 `surface` 위 `positive`/`warning` 텍스트라 lint 가 contrast 3.77:1 (positive) · 3.19:1 (warning) 으로 AA 4.5:1 미달 경고. 실 디자인은 0.08 alpha 배경 + 좌측 보더로 액센트 색을 표현하지 텍스트 색이 아니다 — alpha 모델 미지원의 사양 한계.

## Do's and Don'ts

### Do

- **액센트는 한 페이지/슬라이드에 2곳 이하** — 헤더 마크 + 강조 텍스트 1개.
- **숫자는 `mono` + `tabular-nums`** — 비교표·KPI 정렬 일관.
- **본문 인용·하이라이트는 `primary-soft` 박스** — `primary` 직접 배경은 버튼·KPI 한정.
- **링크는 본문 `primary` 색 + 0.3 알파 언더라인** — 호버에서만 풀 알파.
- **다크 테마 토글 시 `primary` → `primary-active` 자동 스왑** — 어두운 배경 가독성.

### Don't

- **❌ `primary` 를 본문 텍스트 색으로 사용** — 가독성 급락 + 액센트 가치 희석.
- **❌ 본문에 `primary-active` (#2563EB) 직접 사용** — 라이트 테마에선 다크 인터랙션 색이라 인지 충돌.
- **❌ 다크 테마에서 `card` 그림자** — 검정 위 그림자 무의미. 보더로 대체.
- **❌ 한글 italic** — 강조는 `bold` 또는 `primary-soft` 박스로.
- **❌ 8px 그리드 위반 여백** — `13px`, `27px` 등은 의도된 마이크로 조정 한정.
- **❌ 가독성용이 아닌 그라데이션 배경** — `cover-gradient` 한 곳만 허용. 본문·카드·섹션 배경에 그라데이션 사용 금지 (AI slop 트로프).
- **❌ 둥근 모서리 + 좌측 컬러 보더 컨테이너 (callout 외)** — 이 패턴은 `callout-positive/warning/negative` 한정. 일반 카드·박스·인용에 좌측 액센트 보더 사용 금지 (AI slop 트로프).
- **❌ SVG 로 사람·아이콘·일러스트 그리기** — placeholder 박스 또는 실제 자산 사용. 인라인 SVG 는 차트·다이어그램·타임라인 한정.

## Notes — DESIGN 토큰 vs brand.yaml 분리

이 문서의 디자인 토큰(spacing/elevation/typography·컴포넌트 룰)은 **모든 페르소나가 공유하는 디자인 시스템** 이다. 페르소나별로 갈아끼우는 것은 `brand.yaml` 의 `brand:` 텍스트와 `palette:` 색상 한정.

| 카테고리 | 위치 | 페르소나별 갈아끼움 |
|---|---|---|
| 워드마크·러닝 헤더·키커·시그니처·모노그램 | `brand.yaml` `brand:` | ✅ 권장 |
| 핵심 색상 (`primary` / `primary-deep` / `primary-active` / `text` / `bg`) | `brand.yaml` `palette:` | ✅ 권장 |
| spacing/radius/elevation 단계, typography 메트릭 | `template/DESIGN.md` + theme CSS `:root` | ❌ 모든 페르소나 공유 |
| 컴포넌트 룰 (`.callout--*`, `.cmp-table`, `.kpi-grid`) | theme CSS | ❌ 변경 시 전체 영향 |

같은 디자인 시스템 위에서 brand.yaml 의 페르소나 한 줄을 바꾸면, 워드마크/러닝 헤더가 즉시 반영되고 `--brand-primary` 등 토큰을 통해 본문 컴포넌트 색상이 동기화된다.

## Notes — AI slop 트로프 의도적 비회피

흔히 "AI 가 만든 디자인" 시그니처로 지목되는 트로프 중 본 디자인 시스템이 **의도적으로 채택** 한 것들. 페르소나-독립적 결정이라 brand.yaml 갈아끼움으로 영향받지 않는다.

- **Inter + Noto Sans KR**: 진부한 라틴 폰트 조합으로 인식되지만, **Noto Sans KR 와 x-height·메트릭 호환** 이 목적. 한·영 혼용 본문에서 weight 시각 매칭이 안정적인 거의 유일한 라틴 페어라 의도적 채택. 대안(Söhne, GT America 등 유료 페어) 은 외부 공개 라이선스 부담.
- **`fig-chip` 둥근 pill**: pill 형태 chip 자체가 트로프이지만, figure numbering 가독성 우선 — 의도적 허용. `rounded.pill` 사용처는 chip 한정이며 다른 곳 확장 금지.
- **`cover-gradient` 라디얼**: 단일 그라데이션이지만 커버 한 페이지·슬라이드 한정. 본문 영역에 누설 금지.
