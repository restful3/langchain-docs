#!/usr/bin/env python3
"""AI Odyssey Publisher — HTML → A4 PDF 렌더러

Selenium headless Chrome + CDP Page.printToPDF 파이프라인. 페이지 규격은
**A4 세로(210×297 mm)** 고정. 슬라이드 빌더(`build_slides.py`) 가 1280×720
16:9 PDF 를 만들 때는 `slides_to_pdf` 함수를 별도로 사용한다.

우선순위는 CSS `@page` 마진박스 기반 러닝 헤더/페이지 번호이다. 만약 현재 Chrome
버전에서 `@page @top-left` / `string-set` 이 정상 동작하지 않아 헤더·푸터가
비어 있게 나오면 `--fallback-header` 옵션으로 CDP 수준의 header/footer 템플릿
주입으로 전환할 수 있다.

usage:
    python render.py                                   # sample_report.html 을 렌더
    python render.py my_report.html                    # 지정 파일 렌더
    python render.py my_report.html --out output/      # 출력 디렉토리 지정
    python render.py my_report.html --fallback-header  # CDP headerTemplate 사용
"""
from __future__ import annotations

import argparse
import base64
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

HERE = Path(__file__).parent.resolve()

# A4 portrait (inches): 210mm / 25.4 = 8.2677, 297mm / 25.4 = 11.6929
A4_WIDTH_IN = 8.2677
A4_HEIGHT_IN = 11.6929

# CDP fallback 헤더/푸터 템플릿 (CSS @page 마진박스가 동작하지 않을 때만 사용)
HEADER_TEMPLATE = (
    '<div style="width:100%;padding:0 14mm;font:500 9pt \'Inter\',sans-serif;'
    'color:#6B6B72;display:flex;justify-content:space-between;">'
    '<span>AI Odyssey · Independent Research</span>'
    '<span class="title"></span>'
    '</div>'
)
FOOTER_TEMPLATE = (
    '<div style="width:100%;padding:0 14mm;font:700 9pt \'Inter\',sans-serif;'
    'color:#6B6B72;text-align:center;font-variant-numeric:tabular-nums;">'
    '<span class="pageNumber"></span> / <span class="totalPages"></span>'
    '</div>'
)


def _make_driver() -> webdriver.Chrome:
    options = Options()
    for arg in [
        "--headless=new",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--window-size=900,1200",
    ]:
        options.add_argument(arg)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(900, 1200)
    return driver


def html_to_pdf(html_path: Path, pdf_path: Path, fallback_header: bool = False) -> None:
    driver = _make_driver()
    try:
        driver.get(f"file://{html_path}")
        driver.set_script_timeout(30)

        # 인쇄에 라이트 테마 고정
        driver.execute_script("if (typeof applyTheme === 'function') applyTheme('light');")

        # 웹폰트 로딩 대기
        driver.execute_async_script(
            "const cb = arguments[arguments.length - 1];"
            "document.fonts.ready.then(() => setTimeout(cb, 800));"
        )

        # TOC / 각주 / 카운터 / 차트 강제 리빌드 (beforeprint 이벤트도 발화)
        driver.execute_script(
            "if (typeof buildTOC === 'function') buildTOC();"
            "if (typeof numberFootnotes === 'function') numberFootnotes();"
            "document.querySelectorAll('.animate-in').forEach(e => {"
            "  e.classList.remove('animate-in', 'is-visible', 'delay-1', 'delay-2', 'delay-3', 'delay-4');"
            "  e.style.opacity = '1'; e.style.transform = 'none'; e.style.animation = 'none';"
            "});"
            "document.querySelectorAll('[data-count]').forEach(el => {"
            "  if (el.dataset.counted === '1') return;"
            "  const t = parseFloat(el.dataset.count);"
            "  const isF = String(t).indexOf('.') > -1;"
            "  el.textContent = (el.dataset.prefix||'') + (isF ? t.toFixed(1) : Math.round(t).toLocaleString()) + (el.dataset.suffix||'');"
            "  el.dataset.counted = '1';"
            "});"
            "if (typeof buildCharts === 'function') {"
            "  if (typeof chartsBuilt !== 'undefined') chartsBuilt = false;"
            "  buildCharts();"
            "}"
        )
        time.sleep(1.5)

        params = {
            "landscape": False,
            "printBackground": True,
            "paperWidth": A4_WIDTH_IN,
            "paperHeight": A4_HEIGHT_IN,
            "marginTop": 0,
            "marginBottom": 0,
            "marginLeft": 0,
            "marginRight": 0,
            "preferCSSPageSize": True,
            "scale": 1.0,
            "displayHeaderFooter": False,
            # 태그드 PDF — TOC `<a href="#section-N">` 내부 앵커를
            # 클릭 가능한 PDF 링크로 보존. Chrome 98+ 지원.
            "generateTaggedPDF": True,
            "generateDocumentOutline": True,
        }
        if fallback_header:
            params.update({
                "preferCSSPageSize": False,
                "marginTop": 18 / 25.4,      # 18mm
                "marginBottom": 22 / 25.4,   # 22mm
                "marginLeft": 16 / 25.4,     # 16mm
                "marginRight": 16 / 25.4,    # 16mm
                "displayHeaderFooter": True,
                "headerTemplate": HEADER_TEMPLATE,
                "footerTemplate": FOOTER_TEMPLATE,
            })

        result = driver.execute_cdp_cmd("Page.printToPDF", params)
        pdf_path.write_bytes(base64.b64decode(result["data"]))

        # PDF 사이드바 outline 재구성 — 부록 A·B·C + 참고 문헌을 단일 "부록" 부모로 묶음.
        # Chrome generateDocumentOutline 은 H2 를 모두 최상위로 평면 처리하기에 후처리.
        try:
            restructure_appendix_outline(pdf_path)
        except Exception as exc:
            print(f"  ⚠️  outline 재구성 건너뜀 ({exc})")

        # 간단 페이지 수 체크 (PDF xref table 의 /Count 를 쓰지 않고 스팟)
        size_kb = pdf_path.stat().st_size // 1024
        print(f"  ✅ PDF 생성 완료 ({size_kb} KB)")
    finally:
        driver.quit()


def restructure_appendix_outline(pdf_path: Path) -> None:
    """PDF outline 에서 '부록 A·B·C + 참고 문헌' 항목을 단일 '부록' 부모로 묶는다."""
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(str(pdf_path))

    def extract(items):
        result = []
        last = None
        for it in items:
            if isinstance(it, list):
                if last is not None:
                    last["children"] = extract(it)
            else:
                try:
                    page = reader.get_destination_page_number(it)
                except Exception:
                    page = 0
                last = {"title": it.title, "page": page, "children": []}
                result.append(last)
        return result

    tree = extract(reader.outline)
    if not tree:
        return

    import re
    APPENDIX_RE = re.compile(r"^부록\s+[A-Z]\.\s|^참고\s*문헌")

    def is_appendix(title: str) -> bool:
        return bool(APPENDIX_RE.match(title))

    # 부록 항목은 outline 의 임의 깊이에 있을 수 있다(예: '목차' 노드의 자식들).
    # 재귀로 모든 형제 묶음을 훑어 부록 항목들을 단일 '부록' 부모로 묶는다.
    found = [False]

    def restructure(nodes):
        for n in nodes:
            if n["children"]:
                restructure(n["children"])
        idxs = [i for i, n in enumerate(nodes) if is_appendix(n["title"])]
        if not idxs:
            return
        first = idxs[0]
        items = [nodes[i] for i in idxs]
        for i in reversed(idxs):
            del nodes[i]
        nodes.insert(first, {
            "title": "부록",
            "page": items[0]["page"],
            "children": items,
        })
        found[0] = True

    restructure(tree)
    if not found[0]:
        return  # 재구성할 부록 항목 없음

    writer = PdfWriter(clone_from=reader)
    if "/Outlines" in writer._root_object:
        del writer._root_object["/Outlines"]

    def add_nodes(nodes, parent=None):
        for n in nodes:
            item = writer.add_outline_item(n["title"], n["page"], parent=parent)
            if n["children"]:
                add_nodes(n["children"], parent=item)

    add_nodes(tree)

    with open(pdf_path, "wb") as f:
        writer.write(f)


def main():
    ap = argparse.ArgumentParser(description="AI Odyssey Publisher 렌더러 (HTML → A4 PDF)")
    ap.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=HERE / "sample_report.html",
        help="리포트 HTML 파일 (기본: sample_report.html)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="출력 디렉토리 (기본: 입력 파일 폴더)",
    )
    ap.add_argument(
        "--fallback-header",
        action="store_true",
        help="CSS @page 마진박스가 동작하지 않을 때 CDP headerTemplate/footerTemplate 사용",
    )
    args = ap.parse_args()

    input_html = args.input.resolve()
    if not input_html.exists():
        print(f"❌ 입력 파일이 없습니다: {input_html}")
        sys.exit(1)

    out_dir = (args.out.resolve() if args.out else input_html.parent)
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = out_dir / f"{input_html.stem}.pdf"

    print(f"  📄 입력: {input_html}")
    if args.fallback_header:
        print("  ↪️  fallback-header 모드 (CDP headerTemplate 사용)")
    html_to_pdf(input_html, pdf_path, fallback_header=args.fallback_header)
    print(f"  💾 PDF:  {pdf_path}")
    print("✨ 완료")


# ===========================================================================
# Slides — 1280×720 16:9 PDF
# 위 함수들(`html_to_pdf`)은 A4 portrait 리포트용. 슬라이드는 별도.
# ===========================================================================

def _make_slides_driver() -> webdriver.Chrome:
    options = Options()
    for arg in [
        "--headless=new",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--window-size=1400,820",
    ]:
        options.add_argument(arg)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1400, 820)
    return driver


def slides_to_pdf(html_path: Path, pdf_path: Path) -> None:
    """1280×720 16:9 슬라이드 HTML → PDF (landscape, no margins)."""
    driver = _make_slides_driver()
    try:
        driver.get(f"file://{html_path}")
        driver.set_script_timeout(30)

        driver.execute_script("if (typeof applyTheme === 'function') applyTheme('light');")
        driver.execute_async_script(
            "const cb = arguments[arguments.length - 1];"
            "document.fonts.ready.then(() => setTimeout(cb, 800));"
        )
        driver.execute_script(
            "if (typeof buildCharts === 'function') {"
            "  if (typeof chartsBuilt !== 'undefined') chartsBuilt = false;"
            "  buildCharts();"
            "}"
        )
        time.sleep(1.2)

        # 오버플로우 체크 (디버그 신호)
        overflowing = driver.execute_script(
            """
            const overflows = [];
            document.querySelectorAll('.slide').forEach((s, i) => {
                if (s.scrollHeight > s.clientHeight + 4) {
                    overflows.push({
                        index: i,
                        title: (s.querySelector('.slide-title, h1') || {}).innerText || '(no title)',
                        scroll: s.scrollHeight,
                        client: s.clientHeight,
                    });
                }
            });
            return overflows;
            """
        )
        if overflowing:
            print(f"  ⚠️  슬라이드 오버플로우 {len(overflowing)}건:")
            for o in overflowing:
                print(f"     [{o['index']}] {o['title']} ({o['scroll']}>{o['client']}px)")
        else:
            print("  ✅ 오버플로우 없음")

        result = driver.execute_cdp_cmd(
            "Page.printToPDF",
            {
                "landscape": True,
                "printBackground": True,
                "paperWidth": 13.333,
                "paperHeight": 7.5,
                "marginTop": 0,
                "marginBottom": 0,
                "marginLeft": 0,
                "marginRight": 0,
                "preferCSSPageSize": True,
                "scale": 1.0,
            },
        )
        pdf_path.write_bytes(base64.b64decode(result["data"]))
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
