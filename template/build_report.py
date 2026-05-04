#!/usr/bin/env python3
"""ai_odyssey_publisher — Tier 1 (HTML/PDF) + Tier 2 (네이버 마크다운 + PNG).

자족 패키지 — 외부 의존성 없이 폴더만 복사해서 다른 프로젝트에서 사용 가능.
AI Odyssey · Deep Navy 페르소나 동결.

usage:
    # Tier 1 — 풀디자인 HTML/PDF
    python -m ai_odyssey_publisher.build content/ --tier 1

    # Tier 1 HTML 만 (PDF 스킵)
    python -m ai_odyssey_publisher.build content/ --tier 1 --html-only

    # Tier 2 — 네이버용 단순 마크다운 + 인라인 SVG → PNG @2x export
    python -m ai_odyssey_publisher.build content/ --tier 2

    # 둘 다
    python -m ai_odyssey_publisher.build content/ --tier all

콘텐츠 폴더 컨벤션:
    content/
    ├── 00_front_matter.md      # 필수 ## Executive Summary
    ├── 01_*.md ... 07_*.md     # 본 섹션
    ├── 99_references.md        # [^N]: body
    └── sections.yaml           # (옵션) 섹션 라벨 매핑

sections.yaml 부재 시: 파일명 NN_*.md 에서 NN 추출해 ("NN", f"섹션 NN", "", "") 자동 생성.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()

# 양쪽 호출 스타일 지원: `python -m ai_odyssey_publisher.build` (패키지) / `python build.py` (직접)
try:
    from .core import (
        build_md,
        parse_references,
        extract_ref_urls,
        convert_footrefs,
        apply_visual_transforms,
        wrap_section,
        build_section_divider,
        build_toc_stub,
        build_references_appendix,
        strip_h1_and_front_matter,
        split_front_matter_sections,
        parse_hero_kpi,
        build_hero_kpi,
    )
    from .palette import normalize_palette
    from .brand import load_brand, make_brand_style_block
except ImportError:
    from core import (  # type: ignore  # noqa: E402
        build_md,
        parse_references,
        extract_ref_urls,
        convert_footrefs,
        apply_visual_transforms,
        wrap_section,
        build_section_divider,
        build_toc_stub,
        build_references_appendix,
        strip_h1_and_front_matter,
        split_front_matter_sections,
        parse_hero_kpi,
        build_hero_kpi,
    )
    from palette import normalize_palette  # type: ignore  # noqa: E402
    from brand import load_brand, make_brand_style_block  # type: ignore  # noqa: E402


# ---------- sections.yaml ----------

SectionMeta = tuple[str, str, str, str]  # (number, kicker, title, subtitle)


def load_sections(content_dir: Path) -> dict[str, SectionMeta]:
    """sections.yaml 로드. 부재 시 빈 dict 반환 (파일명 fallback 사용)."""
    yaml_path = content_dir / "sections.yaml"
    if not yaml_path.exists():
        print(f"  ℹ️  no sections.yaml in {content_dir} — auto-derive from filenames")
        return {}
    import yaml
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    sections = (raw or {}).get("sections") or {}
    return {k: tuple(v) for k, v in sections.items()}


_NUM_PREFIX_RE = re.compile(r"^(\d{2})_")
_HEADING_RE = re.compile(r"^#{1,2}\s+(.+?)\s*$")
_SECTION_PREFIX_RE = re.compile(r"^섹션\s+\S+\.\s*")
_APPENDIX_PREFIX_RE = re.compile(r"^부록\s+\S+\.\s*")


def _extract_title_subtitle(filepath: Path) -> tuple[str, str, bool]:
    """첫 H1/H2 에서 title/subtitle/is_appendix 추출.

    인식 패턴 (콘텐츠 컨벤션과 일치):
      `## 섹션 N. Title — Subtitle` → (Title, Subtitle, False)
      `## 섹션 N. Title`            → (Title, "",       False)
      `## 부록 X. Title`            → (Title, "",       True)
      `## Title`                    → (Title, "",       False)
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError:
        return ("", "", False)
    for line in text.splitlines():
        m = _HEADING_RE.match(line)
        if not m:
            continue
        heading = m.group(1).strip()
        is_appendix = _APPENDIX_PREFIX_RE.match(heading) is not None
        cleaned = _APPENDIX_PREFIX_RE.sub("", _SECTION_PREFIX_RE.sub("", heading)).strip()
        if " — " in cleaned:
            t, _, s = cleaned.partition(" — ")
            return (t.strip(), s.strip(), is_appendix)
        return (cleaned, "", is_appendix)
    return ("", "", False)


def section_meta_for(filepath: Path, sections: dict[str, SectionMeta]) -> SectionMeta:
    """sections.yaml 우선, 없으면 파일명 NN_ + 첫 H1/H2 에서 fallback."""
    filename = filepath.name
    if filename in sections:
        return sections[filename]
    m = _NUM_PREFIX_RE.match(filename)
    if not m:
        return ("??", "", "", "")
    n = m.group(1)
    title, subtitle, is_appendix = _extract_title_subtitle(filepath)
    if is_appendix:
        return (n, "부록", "", subtitle or title)
    return (n, f"섹션 {n}", title, subtitle)


# ---------- cover ----------

def build_cover_external(title: str, subtitle: str, version_badge: str,
                         meta: dict, author: str, brand: dict) -> str:
    """리포트 커버 — brand.yaml 의 페르소나 워드마크/서명/키커 주입."""
    b = brand["brand"]
    return f"""
    <section class="report-cover">
      <div class="report-cover__wordmark">
        <span class="report-cover__wordmark-name">{b['name']}</span>
        <span class="report-cover__wordmark-sub">{b['sub']}</span>
      </div>
      <span class="report-cover__signature">{b['signature']}</span>
      <span class="report-cover__kicker">{b['cover_kicker']} · {version_badge}</span>
      <h1 class="report-cover__title">{title}</h1>
      <p class="report-cover__subtitle">{subtitle}</p>
      <dl class="report-cover__meta">
        <div><dt>저자</dt><dd>{author}</dd></div>
        <div><dt>발행</dt><dd>{meta.get('date','2026-04')}</dd></div>
      </dl>
    </section>
    """


# ---------- shell ----------

SHELL_TIER1 = """<!DOCTYPE html>
<html lang="ko" class="theme-light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{doc_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
  <script>Chart.defaults.animation = false;</script>
  <link rel="stylesheet" href="{css_href}">
  {brand_style}
  <style>
    sup.ref-cite a {{
      color: var(--brand-primary);
      text-decoration: none;
      font-weight: 700;
      font-size: 8pt;
      padding: 0 2px;
    }}
    sup.ref-cite a:hover {{ text-decoration: underline; }}
    .references li a {{ word-break: break-all; }}
    .report-section h3 {{ margin-top: 14pt; }}
    .report-section h4 {{ margin-top: 10pt; font-weight: 800; }}
    .report-appendix ol.references {{ padding-left: 0 !important; }}
    .report-appendix ol.references li {{ padding-left: 0 !important; }}
    .report-appendix ol.references li::before {{ content: none !important; }}
  </style>
</head>
<body>
  <article class="report">
{body}
  </article>
  <script src="{js_href}"></script>
</body>
</html>
"""


# ---------- Tier 1 build ----------

def _resolve_doc_meta(args, fm_meta: dict, brand: dict) -> dict:
    """문서 메타 우선순위: CLI 인자 > 00_front_matter h1/메타 > brand.yaml fallback."""
    bname = brand["brand"]["name"]
    title = args.title or fm_meta.get("title") or f"{bname} Report"
    subtitle = args.subtitle or " · ".join(fm_meta.get("subtitle_meta", [])) or ""
    return {
        "title": title,
        "subtitle": subtitle,
        "version_badge": args.version_badge or "",
        "doc_title": args.doc_title or title,
        "author": args.author or bname,
        "date": args.date or "",
    }


def build_tier1(src: Path, out_dir: Path, args, brand: dict) -> tuple[Path, Path | None]:
    """Tier 1 (풀디자인) HTML + PDF 생성."""
    md = build_md()
    sections = load_sections(src)

    # 1) 레퍼런스 수집
    refs = parse_references((src / "99_references.md").read_text())
    known_nums = {r["num"] for r in refs}
    url_map = extract_ref_urls(refs)

    # 2) Front-matter 선행 파싱 — 커버 메타와 hero-kpi 데이터를 cover 빌드 전에 확보.
    fm_path = src / "00_front_matter.md"
    fm_raw = fm_path.read_text() if fm_path.exists() else ""
    if fm_raw:
        fm_html_full = md.render(fm_raw)
        fm_html, fm_meta = strip_h1_and_front_matter(fm_html_full)
        kpis, kpi_summary = parse_hero_kpi(fm_raw)
    else:
        fm_html, fm_meta = "", {"title": "", "subtitle_meta": []}
        kpis, kpi_summary = [], ""

    doc = _resolve_doc_meta(args, fm_meta, brand)

    body_chunks: list[str] = []

    # 3) 커버 + TOC
    body_chunks.append(build_cover_external(
        title=doc["title"].replace("—", "<br><span style=\"color:var(--brand-primary);\">—</span>"),
        subtitle=doc["subtitle"],
        version_badge=doc["version_badge"],
        meta={"date": doc["date"]},
        author=doc["author"],
        brand=brand,
    ))
    body_chunks.append(build_toc_stub())

    # 4) Executive Summary (00_front_matter)
    fm_sections = split_front_matter_sections(fm_html)
    if fm_sections:
        body_chunks.append(build_section_divider(
            "00", "섹션 00", "Executive Summary",
            "임원 5분 핵심 요약 — §1~§6 의 결론을 한 페이지에"))
    for es in fm_sections:
        section_label = f'섹션 0. {es["title"]}'
        body_html = f'<h2>{section_label}</h2>{build_hero_kpi(kpis, kpi_summary)}{es["body"]}'
        body_html = apply_visual_transforms(body_html)
        wrapped = wrap_section(body_html, number="00",
                               title_override=section_label,
                               kicker_prefix="Section")
        body_chunks.append(convert_footrefs(wrapped, known_nums, url_map))

    # 4) 본 섹션
    section_files = sorted(p for p in src.glob("*.md")
                           if p.name not in ("00_front_matter.md", "99_references.md"))
    for p in section_files:
        num, part_tag, part_title, part_sub = section_meta_for(p, sections)
        if part_tag:
            body_chunks.append(build_section_divider(num, part_tag, part_title, part_sub or ""))
        raw = p.read_text()
        html = md.render(raw)
        html = convert_footrefs(html, known_nums, url_map)
        html = apply_visual_transforms(html)
        # 부록 분기: kicker == "부록" 일 때 첫 h2 유지 (파일명 무관)
        if part_tag == "부록":
            wrapped = wrap_section(html, number=num, title_override="부록",
                                   kicker_prefix="Appendix", keep_first_h2=True)
        else:
            wrapped = wrap_section(html, number=num, kicker_prefix="Section")
        body_chunks.append(wrapped)

    # 5) 레퍼런스 부록
    body_chunks.append(build_references_appendix(refs))

    # 6) 출력 — 사용자 콘텐츠의 비-페르소나 색상을 한 번 더 정규화.
    full_html = SHELL_TIER1.format(
        doc_title=doc["doc_title"],
        body="\n".join(body_chunks),
        brand_style=make_brand_style_block(brand),
        css_href=str((HERE / "theme_report.css").resolve()).replace("file://", ""),
        js_href=str((HERE / "report.js").resolve()).replace("file://", ""),
    )
    mode = (
        "monochrome"
        if (args.monochrome or brand.get("palette", {}).get("normalize") == "monochrome")
        else "strict"
    )
    full_html, n_recolor = normalize_palette(full_html, mode=mode)
    print(f"  🎨 비-페르소나 색상 정규화: {n_recolor} 건 (mode={mode})")

    out_html = out_dir / f"{args.name}.html"
    out_html.write_text(full_html)
    print(f"  💾 HTML: {out_html}  ({out_html.stat().st_size // 1024} KB)")

    if args.html_only:
        return out_html, None

    # PDF 렌더
    try:
        from .render import html_to_pdf
    except ImportError:
        from render import html_to_pdf  # type: ignore
    out_pdf = out_dir / f"{args.name}.pdf"
    print("  🖨️  PDF 변환 중 ...")
    html_to_pdf(out_html, out_pdf, brand=brand)
    print(f"  💾 PDF:  {out_pdf}")
    return out_html, out_pdf


# ---------- Tier 2 — SVG → PNG export ----------

def export_svgs_to_png(html_path: Path, figs_dir: Path) -> dict[int, Path]:
    """Tier 1 HTML 을 selenium 으로 열고 .svg-figure 내부 SVG 를 figure-{N}.png 로 저장.

    figure 번호는 .svg-figure > .svg-figure__title > .fig-chip 의 텍스트("그림 N") 에서 추출.
    deviceScaleFactor=2 + 투명 배경.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

    figs_dir.mkdir(parents=True, exist_ok=True)

    options = Options()
    for arg in ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                "--hide-scrollbars", "--force-device-scale-factor=2",
                "--window-size=1200,2000"]:
        options.add_argument(arg)
    driver = webdriver.Chrome(options=options)

    out: dict[int, Path] = {}
    try:
        driver.get(f"file://{html_path}")
        driver.execute_script("if (typeof applyTheme === 'function') applyTheme('light');")
        driver.execute_async_script(
            "const cb = arguments[arguments.length - 1];"
            "document.fonts.ready.then(() => setTimeout(cb, 800));"
        )
        # 차트/카운터 강제 빌드
        driver.execute_script(
            "if (typeof buildCharts === 'function') {"
            "  if (typeof chartsBuilt !== 'undefined') chartsBuilt = false;"
            "  buildCharts();"
            "}"
            "document.querySelectorAll('[data-count]').forEach(el => {"
            "  if (el.dataset.counted === '1') return;"
            "  const t = parseFloat(el.dataset.count);"
            "  const isF = String(t).indexOf('.') > -1;"
            "  el.textContent = (el.dataset.prefix||'') + (isF ? t.toFixed(1) : Math.round(t).toLocaleString()) + (el.dataset.suffix||'');"
            "  el.dataset.counted = '1';"
            "});"
        )
        import time as _t
        _t.sleep(1.5)

        all_figures = driver.find_elements(By.CSS_SELECTOR, "figure")
        figures = [f for f in all_figures
                   if f.find_elements(By.CSS_SELECTOR, ".fig-chip")]
        print(f"  🔎 발견된 figure (fig-chip 포함): {len(figures)}")
        for i, fig in enumerate(figures, start=1):
            chip = fig.find_elements(By.CSS_SELECTOR, ".fig-chip")
            chip_text = chip[0].text.strip() if chip else ""
            m = re.search(r"\d+", chip_text)
            num = int(m.group(0)) if m else i
            png_path = figs_dir / f"figure-{num:02d}.png"
            try:
                png_data = fig.screenshot_as_png
                png_path.write_bytes(png_data)
                out[num] = png_path
                print(f"    ✅ 그림 {num} → {png_path.name} ({len(png_data)//1024} KB)")
            except Exception as e:
                print(f"    ⚠️  그림 {num} screenshot 실패: {e}")
    finally:
        driver.quit()

    return out


# ---------- Tier 2 — Naver markdown ----------

FIGURE_RE = re.compile(
    r'<figure\b[^>]*>((?:(?!</figure>).)*?<span class="fig-chip">.*?)</figure>',
    re.DOTALL,
)
FIG_CHIP_RE = re.compile(r'<span class="fig-chip">그림\s+(\d+)</span>(.*?)(?:</span>|</figcaption>)', re.DOTALL)
FIGCAPTION_RE = re.compile(r'<figcaption[^>]*>(.*?)</figcaption>', re.DOTALL)


def replace_figures_in_md(text: str, figs_dir_rel: str) -> tuple[str, int]:
    """본문 마크다운에서 <figure>...</figure> 블록을 ![cap](figs/figure-N.png) 로 치환."""
    count = 0

    def replace(m: re.Match) -> str:
        nonlocal count
        block = m.group(1)
        chip_m = FIG_CHIP_RE.search(block)
        if not chip_m:
            return m.group(0)
        num = int(chip_m.group(1))
        title_raw = chip_m.group(2)
        title = re.sub(r"<[^>]+>", "", title_raw)
        title = re.sub(r"\s+", " ", title).strip()
        cap_m = FIGCAPTION_RE.search(block)
        cap = ""
        if cap_m:
            cap = re.sub(r"<[^>]+>", "", cap_m.group(1)).strip()
            cap = re.sub(r"\s+", " ", cap)
        alt = title or f"그림 {num}"
        count += 1
        lines = [
            f"![{alt}]({figs_dir_rel}/figure-{num:02d}.png)",
        ]
        if cap:
            lines.append(f"")
            lines.append(f"> 그림 {num}. {alt} — {cap}" if title and cap.lower() != alt.lower()
                         else f"> 그림 {num}. {alt}")
        return "\n".join(lines)

    new_text = FIGURE_RE.sub(replace, text)
    return new_text, count


def build_tier2_markdown(src: Path, out_md: Path, figs_dir: Path,
                         doc_title: str = "외부 공개판") -> int:
    """본문 .md 를 합치며 figure 블록 → 이미지 링크."""
    figs_rel = f"{figs_dir.name}"

    chunks: list[str] = []

    chunks.append(f"# {doc_title}")
    chunks.append("")
    chunks.append("> AI Odyssey · External Publishing — 외부 공개판")
    chunks.append("> YouTube [@AI_odysseys](https://www.youtube.com/@AI_odysseys)")
    chunks.append("")
    chunks.append("---")
    chunks.append("")

    total_figs = 0

    # 00 — Executive Summary 만 추출
    fm_text = (src / "00_front_matter.md").read_text()
    es_match = re.search(r'(?ms)^##\s+Executive Summary\s*$(.*?)(?=^---|^##\s+\S|\Z)', fm_text)
    if es_match:
        chunks.append("## Executive Summary")
        chunks.append("")
        body, n = replace_figures_in_md(es_match.group(1).strip(), figs_rel)
        chunks.append(body)
        chunks.append("")
        chunks.append("---")
        chunks.append("")
        total_figs += n

    # 01~07
    section_files = sorted(p for p in src.glob("*.md")
                           if p.name not in ("00_front_matter.md", "99_references.md"))
    for p in section_files:
        body = p.read_text()
        body, n = replace_figures_in_md(body, figs_rel)
        total_figs += n
        chunks.append(body)
        chunks.append("")
        chunks.append("---")
        chunks.append("")

    # 99 references
    refs_text = (src / "99_references.md").read_text()
    chunks.append(refs_text)

    out_md.write_text("\n".join(chunks))
    print(f"  💾 MD:   {out_md}  ({out_md.stat().st_size // 1024} KB)")
    print(f"  📷 figure 치환: {total_figs} 건")
    return total_figs


# ---------- main ----------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--brand", type=Path, default=None,
                    help="brand.yaml 경로. 미지정 시 <src>/brand.yaml > template/brand.default.yaml")
    ap.add_argument("--tier", choices=["1", "2", "all"], default="all")
    ap.add_argument("--name", default="detailed_report_external")
    ap.add_argument("--title", default=None,
                    help="없으면 frontmatter h1 → '<brand.name> Report'")
    ap.add_argument("--subtitle", default=None,
                    help="없으면 frontmatter 메타 문단")
    ap.add_argument("--version-badge", default=None)
    ap.add_argument("--doc-title", default=None,
                    help="HTML <title>. 없으면 --title 과 동일")
    ap.add_argument("--author", default=None,
                    help="없으면 brand.name")
    ap.add_argument("--date", default=None)
    ap.add_argument("--html-only", action="store_true")
    ap.add_argument("--monochrome", action="store_true",
                    help="다색 SVG/배경을 페르소나 단색+명도 단계로 강등 (MONOCHROME_MAP)")
    args = ap.parse_args()

    src = args.src.resolve()
    if not src.is_dir():
        sys.exit(f"❌ not a dir: {src}")
    out_dir = (args.out.resolve() if args.out else src.parent)
    out_dir.mkdir(parents=True, exist_ok=True)

    brand = load_brand(content_dir=src, override=args.brand)

    html_path: Path | None = None

    if args.tier in ("1", "all"):
        print(f"▶  Tier 1 (풀디자인 HTML/PDF) 빌드 — {args.name}")
        html_path, _pdf = build_tier1(src, out_dir, args, brand)

    if args.tier in ("2", "all"):
        print(f"▶  Tier 2 (네이버 본문 + PNG @2x) 빌드")
        if html_path is None:
            html_path = out_dir / f"{args.name}.html"
            if not html_path.exists():
                sys.exit(f"❌ Tier 1 HTML 없음 — 먼저 --tier 1 또는 --tier all 실행: {html_path}")
        figs_dir = src / "figs"
        png_map = export_svgs_to_png(html_path, figs_dir)
        out_md = out_dir / f"{args.name}.naver.md"
        replaced = build_tier2_markdown(src, out_md, figs_dir, doc_title=args.title)
        if replaced != len(png_map):
            print(f"  ⚠️  치환 {replaced} 건 vs PNG {len(png_map)} 개 — 불일치, 검증 필요")

    print("✨ 완료")


if __name__ == "__main__":
    main()
