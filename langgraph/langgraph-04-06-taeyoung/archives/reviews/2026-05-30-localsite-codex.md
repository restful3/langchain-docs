# LangGraph 로컬 self-contained HTML 빌드 리뷰

검토 대상:
- `build_local.py`
- `site/index.html`, `site/report.html`, `site/slides.html`
- 참고 패턴: `claude-code-officeflow/course/site/build_units.py`

검증 스팟체크:
- `grep -RInE 'src="figs/|href="figs/|\.\./.*template|src="https?://|href="https?://|@import|url\(https?://' site/*.html`
- `grep -RInE '/media/restful3|/home/restful3|href="/|src="/' site/report.html site/slides.html`
- `grep -nE '<link|<script' site/report.html site/slides.html`

## Critical

### 1. 위치: `site/report.html` 14, 894 / `build_local.py` 57~64

**문제**  
`report.html` 이 self-contained 가 아닙니다. 산출물에 절대 파일 경로가 그대로 남아 있습니다.

```html
<link rel="stylesheet" href="/media/restful3/data/workspace/langchain-docs/template/theme_report.css">
...
<script src="/media/restful3/data/workspace/langchain-docs/template/report.js"></script>
```

이 경로는 현재 머신의 특정 checkout 에서만 동작하고, 파일을 다른 디렉터리로 복사하거나 다른 사용자가 `file://` 로 열면 깨집니다. 목표가 "template 상대경로나 CDN 없이 file:// / VS Code 프리뷰에서 렌더"라면 가장 큰 요구사항 미충족입니다. 현재 `inline_assets()` 는 `theme_slides.css` 와 `deck.js` 만 치환하고 report 용 `theme_report.css`/`report.js` 는 전혀 처리하지 않습니다.

**권장 수정**  
`inline_assets()` 에 report 자산도 포함하세요. 예:

- `<link ... theme_report.css ...>` → `<style data-source="theme_report.css">...</style>`
- `<script ... report.js ...></script>` → `<script data-source="report.js">...</script>`

`deck.js` 와 동일하게 `</script>` 는 `<\\/script>` 로 이스케이프하세요. 또한 템플릿 경로가 절대경로로 나오는 현재 출력 특성상 정규식은 상대/절대 모두 잡아야 합니다.

### 2. 위치: `site/slides.html` 11, 13 / `site/report.html` 12

**문제**  
CDN 스크립트가 남아 있습니다.

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.js"></script>
```

`slides.html` 에서는 Chart.js 와 html-to-image 가 외부 CDN 의존입니다. `report.html` 에도 Chart.js CDN 이 남아 있습니다. "폰트/CDN 제외"라고 하셨지만, 배경/의도에는 `deck.js`·`theme_slides.css` 를 포함해 CDN 없이 렌더되게 하는 것이 목표라고 되어 있어 서로 충돌합니다. 특히 슬라이드의 PNG 내보내기 기능은 `html-to-image` 로 보이므로 네트워크가 없으면 기능이 깨질 수 있습니다.

**권장 수정**  
정책을 명확히 하세요. 진짜 self-contained 라면 CDN 스크립트도 로컬 vendor 파일로 저장해 인라인하거나, 네트워크 없이 없어도 되는 기능이면 해당 기능을 graceful degradation 하도록 처리해야 합니다. 최소한 빌드 후 검증에서 `https://cdn.jsdelivr.net` 이 남으면 실패시키세요. 폰트만 예외로 둘 거라면 검증 정규식도 "fonts.googleapis/fonts.gstatic 만 허용"처럼 명시적으로 예외 처리하세요.

### 3. 위치: `build_local.py` 39~67, 149~151

**문제**  
인라인 누락이 조용히 지나갑니다. `inline_assets()` 는 파일이 없으면 `0` 을 반환하고, CSS/JS 치환 정규식이 매치되지 않아도 실패하지 않습니다. 현재 실제로 `report.html` 의 핵심 자산 누락과 CDN 잔존이 있는데도 빌드는 성공하고 `inlined figs: report=9, slides=7` 정도만 출력합니다.

**권장 수정**  
빌드 종료 전에 산출물을 검증하고 실패시키세요. 예:

- `src="figs/`, `href="figs/`, `../template`, `/template/`, repo 절대경로, `/media/restful3`, `/home/restful3` 잔존 시 실패
- 허용하지 않은 `src="http(s)://`, `href="http(s)://` 잔존 시 실패
- report 에 `theme_report.css`/`report.js` 링크가 남으면 실패
- slides 에 `theme_slides.css`/`deck.js` 링크가 남으면 실패
- 기대 SVG 개수와 실제 data URI 개수 비교

`inline_assets()` 도 치환 개수를 자산별로 반환해 `report_css=1`, `report_js=1`, `slides_css=1`, `deck_js=1` 같은 식으로 assert 하는 편이 안전합니다.

## Major

### 4. 위치: `build_local.py` 55

**문제**  
figs 인라인 정규식이 `src="figs/..."` 또는 `href="figs/..."` 의 double quote 만 처리합니다. HTML 빌더가 single quote 를 쓰거나, `srcset`, CSS `url(figs/...)`, `<source srcset=...>`, `<use href=...>` 같은 형태를 만들면 놓칩니다. 현재 입력에서는 SVG `<img src="figs/...">` 이라 동작하지만, "self-contained 빌더"로는 취약합니다.

**권장 수정**  
최소한 `src|href|srcset` 과 single/double quote 를 처리하거나, HTML 파서(BeautifulSoup/lxml)로 DOM 속성을 순회해 `figs/` prefix 를 가진 값을 치환하세요. CSS 내부 `url(...)` 을 인라인할 필요가 있다면 별도 정규식을 두세요. 단일 프로젝트용이라면 "현재 템플릿 출력 형태만 지원"이라고 주석으로 범위를 명확히 하고, post-build grep 검증으로 누락을 잡는 방식도 괜찮습니다.

### 5. 위치: `build_local.py` 57~64

**문제**  
CSS/JS 치환이 `count=1` 이고 치환 성공 여부를 확인하지 않습니다. slides 산출물에서는 theme/deck 이 한 번씩 잘 인라인된 것으로 보이지만, 템플릿이 head 구조를 바꾸면 조용히 외부 참조가 남습니다. report 자산처럼 아예 대상에 없는 경우도 현재는 감지하지 못합니다.

**권장 수정**  
`re.subn()` 을 사용해 치환 횟수를 검사하세요. slides 빌드라면 `theme_slides.css` 와 `deck.js` 가 각각 정확히 1회 치환되어야 합니다. report 빌드라면 `theme_report.css` 와 `report.js` 가 각각 정확히 1회 치환되어야 합니다. optional 자산과 required 자산을 분리해 실패 조건을 명확히 두세요.

### 6. 위치: `build_local.py` 20~25, 70~73

**문제**  
경로 가정이 `PROJECT.parents[1]` 에 강하게 묶여 있습니다. 현재 구조(`/.../langchain-docs/langgraph/langgraph-04-06-taeyoung`)에서는 `REPO=.../langchain-docs` 가 맞지만, 프로젝트를 다른 깊이로 복사하거나 symlink 로 실행하면 깨질 수 있습니다. 또한 `TEMPLATE` 존재 여부를 사전에 확인하지 않아, 실패 메시지가 `python -m template` 실패로 늦게 나옵니다.

**권장 수정**  
`PROJECT` 에서 위로 올라가며 `template/__main__.py` 또는 `template/build_report.py` 가 있는 디렉터리를 찾는 식으로 repo root 를 탐색하세요. 최소한 `if not TEMPLATE.is_dir(): raise SystemExit(...)` 와 `if not (CONTENT / "01_textbook.md").is_file()` 같은 preflight 를 추가하세요. 스크립트 설명의 "repo 루트에서 실행"은 실제로 `Path(__file__)` 기준이라 cwd 와 무관하므로, 그 점도 주석을 정리하면 좋습니다.

### 7. 위치: officeflow 대비 / `build_units.py` 119~142

**문제**  
원본 패턴에는 `copy_figs()` 에 basename+sha256 dedup 과 충돌 실패가 있습니다. 이번 프로젝트는 단일 `content/figs` 만 쓰므로 당장 같은 충돌 가능성은 낮지만, 현재 빌드는 복사 단계를 생략하고 원본 `FIGS` 에서 직접 data URI 를 만들기 때문에 "입력 파일명 충돌"보다는 "참조 누락" 검증이 더 중요합니다. 그럼에도 원본 대비 빠진 안전장치의 핵심인 "asset inventory 와 기대치 검증"이 없습니다.

**권장 수정**  
단일 유닛에 맞게 다음 정도의 inventory 검증을 넣으세요.

- `content/figs/*.svg` 개수와 본문/슬라이드 참조 목록을 출력
- 참조된 `figs/...` 가 모두 존재하지 않으면 실패
- 존재하지만 참조되지 않는 그림은 warning
- report/slides 별 expected inline count 를 명시하거나 자동 계산

basename 충돌 검사는 현 구조에서는 선택 사항이지만, input inventory 검사는 넣는 편이 좋습니다.

## Minor

### 8. 위치: `site/report.html` 7~11, `site/slides.html` 7~10

**문제**  
Google Fonts 링크가 남아 있습니다. 사용자가 "폰트/CDN 제외"라고 했으므로 허용일 수 있지만, "외부 참조 0" 검증에서는 계속 잡힙니다. 또한 네트워크 없는 `file://` 환경에서는 폰트가 시스템 fallback 으로 바뀝니다.

**권장 수정**  
폰트는 허용한다면 README/스크립트 출력에 "Google Fonts 는 외부 참조로 남김, 렌더는 fallback 가능"이라고 명시하세요. 엄격한 self-contained 가 목표라면 폰트 링크를 제거하고 시스템 폰트 stack 만 쓰거나, woff2 를 로컬로 vendoring 해서 data URI 로 넣어야 합니다.

### 9. 위치: `build_local.py` 76~138 / `site/index.html`

**문제**  
`index.html` 의 링크는 정확하고 구조도 단순합니다. 다만 카드 전체가 클릭 가능한 구조가 아니라 버튼만 링크이며, 두 링크가 새 탭/현재 탭 정책을 명시하지 않습니다. 접근성 측면에서는 큰 문제는 없지만, 카드형 랜딩이라면 카드 제목과 버튼 간 클릭 목표가 좁게 느껴질 수 있습니다.

**권장 수정**  
현재도 충분합니다. 더 다듬는다면 카드 전체를 `<a>` 로 만들거나, `aria-label="상세 교과서 report.html 열기"` 같은 구체 라벨을 추가하세요. 로컬 파일용이면 현재 탭 이동이 자연스럽습니다.

### 10. 위치: `build_local.py` 76~138

**문제**  
`write_index()` 는 f-string 으로 HTML 을 직접 조립합니다. 현재 값들은 상수라 XSS/escape 문제는 사실상 없지만, 원본 패턴처럼 meta 파일에서 title/summary 를 읽도록 확장하면 escape 가 필요합니다.

**권장 수정**  
상수 기반 단일 페이지라면 유지해도 됩니다. 확장 가능성을 염두에 둔다면 `html.escape()` 를 적용하는 작은 helper 를 두세요.

## Nit

### 11. 위치: `build_local.py` 39~40, 151

**문제**  
docstring 과 출력은 "외부 참조 0 이 목표", "inlined figs" 정도만 말합니다. 실제로는 CSS/JS 인라인도 중요한 결과인데 수치가 노출되지 않습니다.

**권장 수정**  
빌드 로그를 `inlined: report figs=9 css=1 js=1; slides figs=7 css=1 js=1` 처럼 자산별로 출력하면 회귀를 빨리 볼 수 있습니다.

### 12. 위치: `site/report.html` 749

**문제**  
공식 changelog 링크는 의도된 외부 링크입니다. "외부 참조 0" 검증에서 anchor `href="https://docs.langchain.com/..."` 까지 실패로 볼지, 리소스 로딩(`src`, stylesheet, preconnect)만 실패로 볼지 기준이 필요합니다.

**권장 수정**  
self-contained 검증은 렌더링에 필요한 외부 리소스와 일반 문서 링크를 분리하세요. 예를 들어 `a[href^="https://"]` 는 허용하되, `link rel=stylesheet`, `script src`, `img src`, CSS `url()` 의 외부 URL 은 실패로 처리하는 방식이 실용적입니다.

## 전반 평가

현재 빌드는 SVG 그림을 data URI 로 인라인하고 slides 의 `theme_slides.css`/`deck.js` 를 인라인하는 데는 성공했습니다. 그러나 산출물은 아직 "로컬에서 바로 열리는 self-contained HTML" 목표를 만족하지 못합니다. `report.html` 에 template CSS/JS 절대경로가 남아 있고, report/slides 양쪽에 CDN 스크립트가 남아 있으며, 스크립트가 이런 누락을 검증 실패로 잡지 못합니다. 우선 report 자산 인라인과 post-build 외부 리소스 검증을 넣고, CDN/폰트 예외 정책을 명확히 한 뒤 재빌드하면 목적에 훨씬 가까워집니다.
