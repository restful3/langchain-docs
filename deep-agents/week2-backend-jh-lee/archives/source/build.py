"""단일 진입점 — textbook + slides 한 번에 빌드.

template/ 의 두 빌더(`build report` / `build slides`)를 순차 호출하는 wrapper.

template/build_report.py 가 기본 지원하는 플래그:
  --single-section   : --no-cover --no-toc --continuous --show-divider 메타
  --inline-svgs      : 외부 figs/*.svg 참조를 인라인 <svg> 로 치환
  --monochrome       : SVG/배경 색상을 brand 단색 + 명도 단계로 강등

폴더 레이아웃:
  archives/source/  → 01_textbook.md, slides.md, build.py, sections.yaml, figs/
  content/          → textbook.{html,pdf}, slides.{html,pdf}

사용:
    python archives/source/build.py                  # textbook + slides (HTML + PDF)
    python archives/source/build.py --html-only      # 둘 다 HTML 만
    python archives/source/build.py --no-monochrome  # 원본 다색 SVG 유지
    python archives/source/build.py --skip-slides    # textbook 만
    python archives/source/build.py --skip-textbook  # slides 만
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent           # .../week2-backend-jh-lee/archives/source/
WEEK_ROOT = HERE.parents[1]                      # .../week2-backend-jh-lee/
OUT_DIR = WEEK_ROOT / "content"                  # .../week2-backend-jh-lee/content/
PROJECT_ROOT = HERE.parents[3]                   # .../langchain-docs/  (template/ 의 부모)
TEMPLATE_DIR = PROJECT_ROOT / "template"

DOC_TITLE = "Deep Agents — Backends 심층"
SLIDES_SRC = HERE / "slides.md"

# week2 backend — overflow 완화용 CSS overrides.
# slides.html 의 <head> 에 <style> 로 인라인 삽입 (별도 파일 생성 안 함).
# template/theme_slides.css 는 손대지 않고 다른 week 와 공유.
CSS_OVERRIDES_INLINE = """<style id="week2-overrides">
/* slide padding 축소 — 위아래 38px, 좌우 24px 절감 */
.slide                              { padding: 40px 60px 50px 60px !important; }
.slide-header                       { margin-bottom: 14px !important; }
.slide-title-rule                   { margin: 6px 0 10px 0 !important; }
.slide-subtitle                     { margin-bottom: 12px !important; font-size: 0.95em !important; }
.slide-body                         { font-size: 0.96em; }
/* 미디어·코드·표 강제 축소 */
.slide img, .slide svg              { max-height: 230px; height: auto; width: auto; object-fit: contain; }
.slide pre code                     { font-size: 0.78em; line-height: 1.3; }
.slide table                        { font-size: 0.83em; }
.slide table th, .slide table td    { padding: 4px 10px; }
.slide blockquote                   { margin-top: 6px; margin-bottom: 6px; }
.slide .slide-body p img + ul,
.slide .slide-body p svg + ul       { margin-top: 4px; }
.slide .slide-body ul.bullets li    { margin-bottom: 3px; }
.slide-footer                       { margin-top: 8px !important; }
</style>
"""


def _build_textbook(args) -> int:
    cmd = [
        sys.executable, "-m", "template", "build", "report", str(HERE),
        "--single-section",
        "--inline-svgs",
        "--tier", "1",
        "--sections", "01",
        "--out", str(OUT_DIR),
        "--name", "textbook",
        "--doc-title", DOC_TITLE,
    ]
    if not args.no_monochrome:
        cmd.append("--monochrome")
    if args.html_only:
        cmd.append("--html-only")

    print(f"$ {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=str(PROJECT_ROOT))


def _build_slides(args) -> int:
    """slides 빌드 — 2단계 분리:

    1) build_slides --html-only 로 HTML 생성 (template/* 외부 참조)
    2) 자기완결 후처리: ./* 치환 + CSS overrides 적용
    3) (html-only 아니면) 후처리된 HTML 로 PDF 별도 생성

    이렇게 분리해야 CSS overrides 가 PDF 측정·렌더에 반영됨.
    """
    if not SLIDES_SRC.exists():
        print(f"❌ slides.md not found: {SLIDES_SRC}", file=sys.stderr)
        return 1

    # ─── 1단계: HTML 만 생성 ───
    cmd = [
        sys.executable, "-m", "template", "build", "slides", str(SLIDES_SRC),
        "--out", str(OUT_DIR),
        "--html-only",  # 항상 HTML 만. PDF 는 후처리 후 별도로.
    ]
    if not args.no_monochrome:
        cmd.append("--monochrome")

    print(f"$ {' '.join(cmd)}")
    rc = subprocess.call(cmd, cwd=str(PROJECT_ROOT))
    if rc != 0:
        return rc

    # ─── 2단계: 후처리 (PDF 변환 전) — deck.js sanity + CSS overrides 인라인 ───
    _post_process_slides()

    # ─── 3단계: PDF 변환 (--html-only 아닐 때만) ───
    if not args.html_only:
        rc = _slides_html_to_pdf()
        if rc != 0:
            return rc

    return 0


def _slides_html_to_pdf() -> int:
    """후처리된 slides.html 을 PDF 로 변환."""
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from template.render import slides_to_pdf
        html_path = OUT_DIR / "slides.html"
        pdf_path = OUT_DIR / "slides.pdf"
        print(f"  🖨️  후처리된 HTML 로 PDF 변환 중 ...")
        slides_to_pdf(html_path, pdf_path)
        print(f"  💾 PDF:  {pdf_path}  ({pdf_path.stat().st_size // 1024} KB)")
        return 0
    except Exception as e:
        print(f"❌ PDF 변환 실패: {e}", file=sys.stderr)
        return 1
    finally:
        if str(PROJECT_ROOT) in sys.path:
            sys.path.remove(str(PROJECT_ROOT))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html-only", action="store_true", help="PDF 단계 스킵 (HTML 만)")
    ap.add_argument(
        "--no-monochrome", action="store_true",
        help="원본 다색 SVG 유지 (기본은 brand 단색 강등)",
    )
    ap.add_argument("--skip-textbook", action="store_true", help="textbook 빌드 생략")
    ap.add_argument("--skip-slides", action="store_true", help="slides 빌드 생략")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not args.skip_textbook:
        print("\n=== [1/2] textbook ===")
        rc = _build_textbook(args)
        if rc != 0:
            print(f"❌ textbook 빌드 실패 (exit {rc}) — slides 단계 건너뜀", file=sys.stderr)
            sys.exit(rc)

    if not args.skip_slides:
        print("\n=== [2/2] slides ===")
        rc = _build_slides(args)  # 내부에서 HTML → 후처리 → PDF 순서로 처리
        if rc != 0:
            print(f"❌ slides 빌드 실패 (exit {rc})", file=sys.stderr)
            sys.exit(rc)

    print("\n✅ 빌드 완료 →", OUT_DIR)


def _post_process_slides() -> None:
    """slides.html 후처리 두 가지:
       1) template/deck.js sanity check — palette.py stderr 잔재("치환 N 건") 자동 정화
       2) slides.html <head> 에 CSS overrides 를 <style> 로 인라인 삽입

    중복 사본(content/{deck.js, theme_slides.css})은 만들지 않음 — 둘 다 template/ 직접 참조.
    """
    slides_html = OUT_DIR / "slides.html"
    if not slides_html.exists():
        return  # --skip-slides 케이스 등

    # 1) template/deck.js 오염 자동 정화 (재발 방지)
    tpl = TEMPLATE_DIR / "deck.js"
    tpl_text = tpl.read_text(encoding="utf-8")
    tpl_cleaned = [ln for ln in tpl_text.splitlines() if not ln.strip().startswith("치환 ")]
    if len(tpl_cleaned) != len(tpl_text.splitlines()):
        tpl.write_text("\n".join(tpl_cleaned) + "\n", encoding="utf-8")
        print("  ⚠️  template/deck.js 오염(palette stderr 잔재) 자동 제거")

    # 2) slides.html <head> 끝에 CSS overrides 인라인 (이미 있으면 스킵)
    html = slides_html.read_text(encoding="utf-8")
    if "week2-overrides" not in html:
        html = html.replace("</head>", CSS_OVERRIDES_INLINE + "</head>", 1)
        slides_html.write_text(html, encoding="utf-8")

    print("  🔧 후처리: deck.js sanity check + CSS overrides 인라인 삽입")


if __name__ == "__main__":
    main()
