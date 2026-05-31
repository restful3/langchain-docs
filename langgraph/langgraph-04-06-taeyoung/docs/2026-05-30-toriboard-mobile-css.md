# 2026-05-30 ToriBoard 모바일 CSS 보정 기록

## 배경

LangGraph 04-06 정적 사이트를 ToriBoard Sites에 등록한 뒤, iPhone 폭에서 `index.html` 카드 레이아웃이 깨지는 문제가 확인됐다. OfficeFlow에서 발견한 동일 계열 문제를 LangGraph 사이트에도 반영했다.

## 증상

- `index.html` 카드에서 번호/본문/버튼이 한 줄 flex로 폭 경쟁
- `상세 교과서`, `발표 슬라이드` 제목과 설명이 좁게 접힘
- 한글 문장이 단어 중간에서 과도하게 끊김
- report/slides 페이지도 iPhone safe-area 및 좁은 화면에서 컨트롤 겹침 가능성 존재

## 수정

파일:
- `site/index.html`
- `site/report.html`
- `site/slides.html`

수정 요약:
- index 모바일 카드: `grid-template-columns: 44px minmax(0,1fr)`로 번호/본문 분리, 버튼은 다음 줄로 이동
- index 한글 줄바꿈: `word-break: keep-all`, `overflow-wrap: break-word`
- header: `env(safe-area-inset-top)` 반영
- report: cover title `nowrap` 해제, 이미지/SVG 폭 제한, meta 1열화, 한글 줄바꿈 보정
- slides: nav/toc/viz controls safe-area 반영, TOC 모바일 폭 제한, `fitStage()`에서 모바일 하단 컨트롤 여유공간 반영

## 검증

ToriBoard URL 기준 390px 폭에서 확인:

- `/sites-static/langgraph-04-06/index.html` — 카드 제목/설명/버튼 정상
- `/sites-static/langgraph-04-06/report.html` — 표지/본문 화면폭 내 표시
- `/sites-static/langgraph-04-06/slides.html` — 슬라이드 fit 및 컨트롤 safe-area 보정 확인

## 재발방지

정적 사이트를 다시 생성하거나 HTML을 교체할 경우, 최소 아래 3개 URL을 390x844 폭에서 확인한다.

```text
/sites-static/langgraph-04-06/index.html
/sites-static/langgraph-04-06/report.html
/sites-static/langgraph-04-06/slides.html
```

판정 기준:
- 카드 제목이 1~2글자 단위로 세로처럼 접히면 실패
- 버튼이 본문 옆 폭을 과도하게 잡아먹으면 실패
- 제목/본문이 화면 밖으로 넘치면 실패
- 슬라이드 하단 네비게이션이 safe-area와 겹치면 실패
