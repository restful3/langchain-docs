#!/usr/bin/env python3
"""langgraph-04-06-taeyoung 콘텐츠를 로컬에서 바로 열리는 self-contained HTML 로 빌드한다.

claude-code-officeflow/course/site/build_units.py 의 인라인 패턴을 단일 유닛에 맞춘 것.

[self-contained 정책]
- 렌더 필수 자산은 전부 인라인한다:
  report  → theme_report.css + report.js + figs(SVG data URI)
  slides  → theme_slides.css + deck.js   + figs(SVG data URI)
  → ../../../template 상대경로·repo 절대경로 참조가 0 이 되어 file:// / VS Code 프리뷰
    어디서 열어도, 파일을 다른 곳으로 복사해도 렌더된다.
- 허용된 외부 참조(검증에서 예외): Google Fonts(fonts.googleapis/gstatic) ·
  cdn.jsdelivr(Chart.js·html-to-image). 이들은 없어도 본문 렌더에 지장 없다(폰트는
  시스템 fallback, Chart.js 는 미사용, html-to-image 는 슬라이드 PNG 내보내기 전용).
- 본문 anchor(`<a href=...>`)의 외부 링크는 정상(콘텐츠), 검증 대상 아님.

빌드는 산출물을 검증(validate)하고, 허용되지 않은 외부 리소스 참조가 남으면 실패한다.

사용 (어디서든 — 경로는 이 파일 기준):
    python langgraph/langgraph-04-06-taeyoung/build_local.py
"""
from __future__ import annotations

import base64
import re
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent              # .../langgraph-04-06-taeyoung
CONTENT = PROJECT / "content"
REPORT_SRC = CONTENT / "report"                        # 멀티 섹션 리포트 소스 (NN_*.md + sections.yaml)
FIGS = CONTENT / "figs"
SITE = PROJECT / "site"
REPO = PROJECT.parents[1]                              # .../langchain-docs (template 패키지 위치)
TEMPLATE = REPO / "template"
TITLE = "LangGraph 노드·엣지·State 편"
DATE = "2026-05-30"
SESSION_LABEL = "LangGraph 스터디 · 노드·엣지·State 편"
PRESENTER = "태영"

# 검증에서 허용하는 외부 리소스 호스트 (렌더 비필수 / graceful degradation)
ALLOWED_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com", "cdn.jsdelivr.net")

_MIME = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
         ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}


def data_uri(path: Path) -> str:
    mime = _MIME.get(path.suffix.lower(), "application/octet-stream")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _inline_css(text: str, cssname: str) -> tuple[str, int]:
    path = TEMPLATE / cssname
    if not path.is_file():
        return text, 0
    block = f"<style data-inlined=\"{cssname}\">\n" + path.read_text(encoding="utf-8") + "\n</style>"
    # href 가 절대/상대 어느 형태든 …/<cssname> 로 끝나는 link 를 잡는다.
    pat = r'<link[^>]*href="[^"]*' + re.escape(cssname) + r'"[^>]*>'
    text2, n = re.subn(pat, lambda m: block, text, count=1)
    # 새 템플릿은 일부 산출물(report)의 CSS 를 자체 인라인(<style data-source=…>)해 내보낸다.
    # 그 경우 치환할 외부 link 가 없으므로, 이미 인라인된 블록을 1회로 인정한다.
    if n == 0 and re.search(r'<style[^>]*data-(?:source|inlined)="' + re.escape(cssname) + r'"', text):
        return text, 1
    return text2, n


def _inline_js(text: str, jsname: str) -> tuple[str, int]:
    path = TEMPLATE / jsname
    if not path.is_file():
        return text, 0
    body = path.read_text(encoding="utf-8").replace("</script>", "<\\/script>")
    block = f"<script data-inlined=\"{jsname}\">\n" + body + "\n</script>"
    pat = r'<script[^>]*src="[^"]*' + re.escape(jsname) + r'"[^>]*>\s*</script>'
    text2, n = re.subn(pat, lambda m: block, text, count=1)
    # 새 템플릿은 일부 산출물의 JS 를 자체 인라인(<script data-source=…>)해 내보낸다.
    if n == 0 and re.search(r'<script[^>]*data-(?:source|inlined)="' + re.escape(jsname) + r'"', text):
        return text, 1
    return text2, n


def _inline_figs(text: str) -> tuple[str, int]:
    n = 0

    def repl(m: re.Match) -> str:
        nonlocal n
        attr, quote, name = m.group(1), m.group(2), m.group(3)
        f = FIGS / name
        if f.is_file():
            n += 1
            return f'{attr}={quote}{data_uri(f)}{quote}'
        return m.group(0)

    # src|href = "figs/NAME"  또는  'figs/NAME'  (쿼리스트링 허용)
    text = re.sub(r'(src|href)=(["\'])figs/([^"\'?]+)(?:\?[^"\']*)?\2', repl, text)
    return text, n


def inline_assets(html_path: Path, kind: str) -> dict[str, int]:
    """kind: 'report' | 'slides'. 필수 자산을 인라인하고 자산별 치환 수를 반환."""
    text = html_path.read_text(encoding="utf-8")
    counts: dict[str, int] = {}
    if kind == "report":
        text, counts["theme_report.css"] = _inline_css(text, "theme_report.css")
        text, counts["report.js"] = _inline_js(text, "report.js")
    elif kind == "slides":
        text, counts["theme_slides.css"] = _inline_css(text, "theme_slides.css")
        text, counts["deck.js"] = _inline_js(text, "deck.js")
    text, counts["figs"] = _inline_figs(text)
    html_path.write_text(text, encoding="utf-8")
    return counts


# ---------- 검증 ----------

class BuildError(SystemExit):
    pass


def validate(html_path: Path, required_assets: list[str], expected_figs: int) -> None:
    """산출물이 self-contained 정책을 지키는지 검사. 위반 시 BuildError."""
    text = html_path.read_text(encoding="utf-8")
    name = html_path.name
    errs: list[str] = []

    # 1) 인라인되어야 할 자산이 link/script 로 남아있으면 실패
    for asset in required_assets:
        if re.search(r'<(?:link|script)[^>]*(?:href|src)="[^"]*' + re.escape(asset) + r'"', text):
            errs.append(f"{asset} 가 인라인되지 않고 외부 참조로 남음")

    # 2) figs/ · ../template · repo 절대경로 리소스 참조 금지
    for bad, why in [
        (r'(?:src|href)="figs/', 'figs/ 상대참조 잔존(인라인 실패)'),
        (r'(?:src|href)="[^"]*\.\./[^"]*template', '../template 상대참조 잔존'),
        (r'(?:src|href)="(?:/media/restful3|/home/restful3)[^"]*"', 'repo 절대경로 참조 잔존'),
    ]:
        if re.search(bad, text):
            errs.append(why)

    # 3) 리소스 로더(link rel=stylesheet / script src / img src)의 외부 URL 은 allowlist 만 허용
    for m in re.finditer(r'<link[^>]*\srel="stylesheet"[^>]*href="(https?://[^"]+)"', text):
        if not any(h in m.group(1) for h in ALLOWED_HOSTS):
            errs.append(f"비허용 외부 stylesheet: {m.group(1)[:60]}")
    for m in re.finditer(r'<script[^>]*\ssrc="(https?://[^"]+)"', text):
        if not any(h in m.group(1) for h in ALLOWED_HOSTS):
            errs.append(f"비허용 외부 script: {m.group(1)[:60]}")
    for m in re.finditer(r'<img[^>]*\ssrc="(https?://[^"]+)"', text):
        errs.append(f"외부 img(인라인돼야 함): {m.group(1)[:60]}")

    # 4) figs data URI 개수 확인
    got = len(re.findall(r'data:image/svg\+xml;base64', text))
    if got != expected_figs:
        errs.append(f"figs data URI {got}개 (기대 {expected_figs}개)")

    if errs:
        for e in errs:
            print(f"  ✗ [{name}] {e}", file=sys.stderr)
        raise BuildError(f"validate 실패: {name}")
    print(f"  ✓ [{name}] self-contained 검증 통과 (figs {got}, 허용 외부참조=fonts·cdn)")


def run(cmd: list[str]) -> None:
    print("run", " ".join(cmd))
    if subprocess.run(cmd, cwd=str(REPO)).returncode != 0:
        raise BuildError(f"build 실패: {' '.join(cmd)}")


def fig_inventory() -> int:
    """content/figs 의 SVG 목록과 본문/슬라이드 참조를 대조. 미존재 참조는 실패, 미참조는 경고."""
    figs = sorted(p.name for p in FIGS.glob("*.svg"))
    md_text = "".join(p.read_text(encoding="utf-8") for p in sorted(REPORT_SRC.glob("*.md"))) + \
              (CONTENT / "slides.md").read_text(encoding="utf-8")
    referenced = set(re.findall(r'figs/([A-Za-z0-9_]+\.svg)', md_text))
    missing = referenced - set(figs)
    if missing:
        for m in sorted(missing):
            print(f"  ✗ 참조되지만 없는 figure: {m}", file=sys.stderr)
        raise BuildError("figure 참조 무결성 실패")
    unref = set(figs) - referenced
    for u in sorted(unref):
        print(f"  ⚠ 사용되지 않는 figure: {u}")
    print(f"  figs inventory: {len(figs)}개 전부 참조됨" if not unref else f"  figs inventory: {len(figs)}개 중 {len(unref)}개 미참조")
    return len(figs)


def write_index() -> None:
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LangGraph 노드·엣지·State 편 — 발표 자료</title>
<style>
  :root {{ --navy:#0F2C59; --blue:#2563EB; --bg:#FAFAF9; --surface:#FFFFFF; --text:#0F0F10; --muted:#6B6B72; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,'Segoe UI','Noto Sans KR','Malgun Gothic',sans-serif; background:var(--bg); color:var(--text); }}
  header {{ background:linear-gradient(135deg,var(--navy),#091F40); color:#fff; padding:48px 24px 40px; }}
  .wrap {{ max-width:880px; margin:0 auto; }}
  header .kicker {{ font-size:13px; letter-spacing:.12em; text-transform:uppercase; opacity:.8; }}
  header h1 {{ margin:.3em 0 .2em; font-size:28px; line-height:1.3; }}
  header p {{ margin:0; opacity:.85; font-size:15px; }}
  .meta {{ margin-top:16px; font-size:13px; opacity:.8; }}
  ul.units {{ list-style:none; margin:32px auto; padding:0; max-width:880px; }}
  .card {{ display:flex; align-items:center; gap:18px; background:var(--surface); border:1px solid #ECEAE6;
           border-radius:14px; padding:18px 20px; margin:0 24px 14px; box-shadow:0 1px 3px rgba(15,44,89,.05); }}
  .card__no {{ flex:0 0 44px; height:44px; border-radius:50%; background:#E9F2FB; color:var(--blue);
               font-weight:800; font-size:15px; display:flex; align-items:center; justify-content:center; }}
  .card__body {{ flex:1 1 auto; min-width:0; }}
  .card__title {{ font-weight:700; font-size:16px; }}
  .card__sum {{ color:var(--muted); font-size:13px; margin-top:4px; line-height:1.5; }}
  .card__links {{ flex:0 0 auto; display:flex; gap:8px; }}
  .btn {{ display:inline-block; padding:9px 16px; border-radius:8px; font-size:13px; font-weight:700;
          text-decoration:none; background:var(--blue); color:#fff; white-space:nowrap; }}
  .btn--alt {{ background:var(--navy); }}
  footer {{ text-align:center; color:var(--muted); font-size:12px; padding:24px; }}
</style>
</head>
<body>
<header><div class="wrap">
  <div class="kicker">AI 오딧세이 세미나 · LangGraph 스터디 노드·엣지·State 편 발제 · 태영</div>
  <h1>LangGraph 로 사고하기 — 노드·엣지·State</h1>
  <p>Thinking in LangGraph · Run a local server · Changelog 를 핵심 5주제로 통합</p>
  <div class="meta">상세 교과서(단독 학습용) + 발표 슬라이드(16:9 · 19장) · 그림 9개 · 표 9개</div>
</div></header>
<ul class="units">
  <li class="card">
    <div class="card__no" aria-hidden="true">교안</div>
    <div class="card__body">
      <div class="card__title">상세 교과서 (Report)</div>
      <div class="card__sum">§0 들머리 ~ §6 + 부록 — 노드·엣지·State, 설계 5단계, State/에러, 사람 개입·내구성, 로컬 실행·근황. 발표 전후 단독 학습용.</div>
    </div>
    <div class="card__links"><a class="btn" href="report.html" aria-label="상세 교과서 report.html 열기">리포트 열기</a></div>
  </li>
  <li class="card">
    <div class="card__no" aria-hidden="true">발표</div>
    <div class="card__body">
      <div class="card__title">발표 슬라이드 (Slides)</div>
      <div class="card__sum">19장 · 1280×720 16:9 — 방향키(→/←)로 넘김, 우상단 메뉴에서 라이트/다크·PNG 내보내기(PNG 는 네트워크 필요).</div>
    </div>
    <div class="card__links"><a class="btn btn--alt" href="slides.html" aria-label="발표 슬라이드 slides.html 열기">슬라이드 열기</a></div>
  </li>
</ul>
<footer>AI 오딧세이 세미나 · 로컬 self-contained 미리보기 (ai-odyssey template 빌드) · {DATE}</footer>
</body>
</html>
'''
    (SITE / "index.html").write_text(html, encoding="utf-8")
    print(f"  index -> {SITE / 'index.html'}")


def main() -> int:
    # preflight
    if not TEMPLATE.is_dir():
        raise BuildError(f"template 패키지를 찾을 수 없음: {TEMPLATE}")
    if not (REPORT_SRC / "00_front_matter.md").is_file():
        raise BuildError(f"content/report/00_front_matter.md 없음: {REPORT_SRC}")
    if not (CONTENT / "slides.md").is_file():
        raise BuildError(f"content/slides.md 없음: {CONTENT}")

    SITE.mkdir(parents=True, exist_ok=True)
    expected_figs = fig_inventory()

    # 리포트는 content/report/ 의 멀티 섹션(00_front_matter + NN_*.md + 99_references)을 통째로 빌드.
    # 슬라이드는 content/slides.md 를 별도로 빌드한다(섹션 글롭과 분리).
    run([sys.executable, "-m", "template", "build", "report", str(REPORT_SRC),
         "--html-only", "--tier", "1", "--continuous", "--no-toc",
         "--session-label", SESSION_LABEL, "--author", PRESENTER,
         "--name", "report", "--out", str(SITE), "--title", TITLE, "--date", DATE])
    run([sys.executable, "-m", "template", "build", "slides", str(CONTENT / "slides.md"),
         "--html-only", "--out", str(SITE)])

    rc = inline_assets(SITE / "report.html", "report")
    sc = inline_assets(SITE / "slides.html", "slides")
    print(f"  inlined: report figs={rc['figs']} css={rc['theme_report.css']} js={rc['report.js']}"
          f"; slides figs={sc['figs']} css={sc['theme_slides.css']} js={sc['deck.js']}")

    # 필수 자산이 정확히 1회 인라인됐는지
    for label, c, need in [("report theme_report.css", rc['theme_report.css'], 1),
                           ("report report.js", rc['report.js'], 1),
                           ("slides theme_slides.css", sc['theme_slides.css'], 1),
                           ("slides deck.js", sc['deck.js'], 1)]:
        if c != need:
            raise BuildError(f"{label} 인라인 {c}회 (기대 {need}회) — 템플릿 head 구조 변경 의심")

    validate(SITE / "report.html", ["theme_report.css", "report.js"], expected_figs)
    validate(SITE / "slides.html", ["theme_slides.css", "deck.js"], expected_figs)
    write_index()
    print(f"\nDONE -> {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
