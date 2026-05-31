# 로컬 사이트 Codex 리뷰 — 결정 및 변경 (Claude)

대상: `build_local.py` + `site/` · Codex 리뷰: `2026-05-30-localsite-codex.md`
결과: **Critical 3 · Major 4 · Minor 3 · Nit 2** → 핵심 전부 반영

## Critical (전부 반영)

| # | 항목 | 사실확인 | 변경 |
|---|---|---|---|
| C1 | report.html 이 `theme_report.css`·`report.js` 를 **repo 절대경로**로 참조 → 자족형 아님 | ✅ 실제 버그 확인 (`/media/restful3/.../template/...`) | `inline_assets` 를 report 자산(theme_report.css·report.js)까지 인라인하도록 일반화. /tmp 복사본 file:// 렌더로 포터블 실증 |
| C2 | Chart.js·html-to-image CDN 잔존이 "CDN 없이" 의도와 충돌 | ✅ | 정책 명문화: **렌더 필수자산(template CSS/JS·figs)만 인라인**, 폰트·cdn.jsdelivr 는 **허용 외부참조**(없어도 본문 렌더 OK — 폰트 fallback·Chart 미사용·html-to-image 는 PNG 내보내기 전용). docstring·index 에 명시 |
| C3 | 인라인 누락이 조용히 통과 | ✅ | `re.subn` 카운트 + 필수자산 ==1 assert + **post-build `validate()`**(허용외 외부 리소스/누락/figs 수 불일치 시 빌드 실패) |

## Major (반영)

| # | 항목 | 변경 |
|---|---|---|
| 4 | figs 정규식이 double-quote 만 처리 | `src|href` × single/double quote 모두 처리 (쿼리스트링 허용). 범위는 주석으로 명시 |
| 5 | CSS/JS 치환 count 미검증 | `re.subn` 으로 치환 횟수 반환, 필수자산 정확히 1회 아니면 실패 |
| 6 | 경로 가정·preflight 부재 | `TEMPLATE`·`content/*.md` preflight 추가, docstring "어디서든 — 경로는 이 파일 기준" 으로 정정 |
| 7 | asset inventory 검증 부재 | `fig_inventory()` — figs 수 집계 + 참조 무결성(없는 참조 실패, 미참조 경고) |

## Minor / Nit

| # | 항목 | 처리 |
|---|---|---|
| 8 | Google Fonts 외부참조 | 허용 정책 명시(docstring), index 에 "PNG 는 네트워크 필요" 표기 |
| 9 | index 카드 접근성 | 버튼에 `aria-label`, 장식 라벨에 `aria-hidden` 추가 |
| 11 | 자산별 로그 부재 | `inlined: report figs=9 css=1 js=1; slides figs=9 css=1 js=1` 형태 로그 |
| 12 | 외부 anchor vs 리소스 구분 | `validate` 는 link rel=stylesheet·script src·img src 만 검사, 본문 `<a href=https://>` 는 통과 |
| 10 | write_index f-string escape | 상수 전용이라 유지(REJECT). 확장 시 `html.escape` 도입 권고만 |

## 검증

- 재빌드: figs inventory 9/9, 인라인 report css=1 js=1 / slides css=1 js=1, **validate 양쪽 통과**
- report.html `/media|/home/restful3` 절대경로 **0건**, 외부 리소스 로더 = fonts·cdn.jsdelivr 만
- **포터블 실증**: `site/*.html` 을 `/tmp/portable/`(template 없음)로 복사 → file:// 렌더 시 사이드바·워드마크·목차까지 완전 스타일 적용
