#!/usr/bin/env python3
"""ai_odyssey_publisher — Slides MD → HTML → PDF (1280×720 16:9).

리포트(build_report.py) 와 같은 패키지 안의 자매 빌더. AI Odyssey 페르소나로
1280×720 슬라이드 덱을 생성한다. 마크다운은 H1 단위로 분할되며,
`<!-- slide: variant=cover|section|closing, tag=..., num=... -->` 메타 주석으로
변형을 지정한다.

usage:
    python -m ai_odyssey_publisher.build_slides content/slides.md
    python -m ai_odyssey_publisher.build_slides content/slides_dir/         # 디렉토리 (per-section split)
    python -m ai_odyssey_publisher.build_slides content/slides_dir/ --html-only

MD 포맷:

    ---
    title: 발표 제목
    subtitle: 발표 부제 (커버 슬라이드용)
    author: 발표자
    version: v1 · 2026-05-01
    org: AI Odyssey
    kicker: Research Deck
    ---

    <!-- slide: variant=cover -->
    # 발표 제목

    <!-- slide: variant=section, num=01 -->
    # 섹션 01.<br>섹션 제목
    > 섹션 부제

    <!-- slide: tag="Section 01 · Hook" -->
    # 일반 슬라이드 제목
    > 부제 (blockquote → .slide-subtitle)

    본문 마크다운, 인라인 SVG, 표 등...

    <!-- slide: variant=closing -->
    # 감사합니다
    > "Charting the AI seas, one episode at a time"

variant: default(생략) | cover | section | closing
slide meta: variant, tag(섹션 태그), num(섹션 번호), aria(접근성 라벨), kicker, untitled
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()

# 양쪽 호출 스타일 지원
try:
    from .core import build_md
    from .palette import normalize_palette
    from .brand import load_brand, make_brand_style_block
except ImportError:
    from core import build_md  # type: ignore  # noqa: E402
    from palette import normalize_palette  # type: ignore  # noqa: E402
    from brand import load_brand, make_brand_style_block  # type: ignore  # noqa: E402


# ---------- frontmatter ----------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """단순 key: value 만 파싱하는 가벼운 YAML-ish frontmatter 파서."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 5:]
    meta: dict[str, str] = {}
    for line in fm_text.split("\n"):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


# ---------- slide split ----------

SLIDE_META_RE = re.compile(r"^\s*<!--\s*slide:\s*(.+?)\s*-->\s*$", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*$")


def parse_meta_comment(comment_body: str) -> dict[str, str]:
    """key=value, key="value with spaces", ... 형식 파싱."""
    meta: dict[str, str] = {}
    tokens = re.findall(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^,]+))', comment_body)
    for k, qd, qs, raw in tokens:
        v = qd or qs or raw
        meta[k.strip()] = v.strip()
    return meta


def split_slides(md_text: str) -> list[dict]:
    """MD 를 H1 단위 슬라이드 블록으로 분할."""
    lines = md_text.split("\n")
    slides: list[dict] = []
    pending_meta: dict[str, str] = {}
    current: dict | None = None
    in_code = False

    def push():
        nonlocal current
        if current is not None:
            slides.append(current)
        current = None

    for line in lines:
        if re.match(r"^\s*```", line):
            in_code = not in_code
            if current is not None:
                current["body_lines"].append(line)
            continue

        if not in_code:
            m = SLIDE_META_RE.match(line)
            if m:
                pending_meta = parse_meta_comment(m.group(1))
                continue

            h1m = H1_RE.match(line)
            if h1m:
                push()
                current = {
                    "meta": pending_meta,
                    "h1": h1m.group(1).strip(),
                    "body_lines": [],
                }
                pending_meta = {}
                continue

        if current is not None:
            current["body_lines"].append(line)

    push()
    return slides


# ---------- subtitle extraction ----------

def extract_subtitle(body_md: str) -> tuple[str, str]:
    """본문이 blockquote(`> ...`) 로 시작하면 subtitle 로 분리."""
    lines = body_md.split("\n")
    idx = 0
    while idx < len(lines):
        s = lines[idx].strip()
        if s == "" or (s.startswith("<!--") and s.endswith("-->")):
            idx += 1
        else:
            break
    if idx < len(lines) and lines[idx].lstrip().startswith(">"):
        end = idx
        sub_lines = []
        while end < len(lines) and lines[end].lstrip().startswith(">"):
            sub_lines.append(re.sub(r"^\s*>\s?", "", lines[end]))
            end += 1
        subtitle = " ".join(sub_lines).strip()
        rest = "\n".join(lines[:idx] + lines[end:])
        return subtitle, rest
    return "", body_md


# ---------- visual transforms ----------

def apply_visual_transforms(html: str) -> str:
    """슬라이드용 최소 자동 승격. 표·최상위 리스트만 처리."""
    html = re.sub(r"<table>", '<table class="cmp-table">', html)
    html = re.sub(r"<ul>\s*\n<li>", '<ul class="bullets">\n<li>', html)
    html = re.sub(r"<ol>\s*\n<li>", '<ol class="nums">\n<li>', html)
    return html


# ---------- slide rendering ----------

def _make_brand_mark(brand: dict) -> str:
    """슬라이드 헤더 워드마크 HTML — brand.yaml 의 name/sub 주입."""
    b = brand["brand"]
    return (
        '<div class="brand-mark">'
        '<div class="brand-mark__stack">'
        f'<span class="brand-mark__name">{b["name"]}</span>'
        f'<span class="brand-mark__sub">{b["sub"]}</span>'
        '</div>'
        '</div>'
    )


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def render_default(slide: dict, page: int, total: int, deck: dict, brand: dict) -> str:
    md = build_md()
    body_md = "\n".join(slide["body_lines"])
    subtitle_md, rest_md = extract_subtitle(body_md)
    body_html = md.render(rest_md)
    body_html = apply_visual_transforms(body_html)

    section_tag = slide["meta"].get("tag", "")
    aria_label = slide["meta"].get("aria", _strip_html(slide["h1"]))
    untitled = "untitled" in slide["meta"]

    subtitle_html = (
        f'<p class="slide-subtitle animate-in delay-1">{md.renderInline(subtitle_md)}</p>'
        if subtitle_md and not untitled
        else ""
    )
    section_tag_html = (
        f'<div class="slide-section-tag">{section_tag}</div>' if section_tag else ""
    )

    org = deck["org"]
    page_str = f"{page:02d}"
    total_str = f"{total:02d}"

    title_block = (
        ""
        if untitled
        else f'<h1 class="slide-title animate-in">{slide["h1"]}</h1>\n  <div class="slide-title-rule"></div>'
    )

    return f"""<section class="slide" aria-label="{aria_label}">
  <div class="slide-header">
    {_make_brand_mark(brand)}
    {section_tag_html}
  </div>
  {title_block}
  {subtitle_html}
  <div class="slide-body">
{body_html}
  </div>
  <div class="slide-footer">
    <span>{org}</span>
    <span class="slide-footer__page"><span>{page_str}</span> / {total_str}</span>
  </div>
</section>"""


def render_section(slide: dict, deck: dict) -> str:
    md = build_md()
    body_md = "\n".join(slide["body_lines"])
    subtitle_md, _ = extract_subtitle(body_md)
    subtitle_html = (
        f'<p class="section-subtitle">{md.renderInline(subtitle_md)}</p>'
        if subtitle_md
        else ""
    )
    num = slide["meta"].get("num", "")
    aria = slide["meta"].get("aria", f"Section {num} divider")
    return f"""<section class="slide slide--section" aria-label="{aria}">
  <div class="section-tag">Section</div>
  <h1>{slide["h1"]}</h1>
  {subtitle_html}
  <div class="section-rule"></div>
  <div class="section-num">{num}</div>
</section>"""


def render_cover(slide: dict, deck: dict, brand: dict) -> str:
    md = build_md()
    b = brand["brand"]
    body_md = "\n".join(slide["body_lines"])
    subtitle_md, _ = extract_subtitle(body_md)
    subtitle_text = subtitle_md or deck.get("subtitle", "")
    subtitle_html = md.renderInline(subtitle_text) if subtitle_text else ""

    kicker = deck["kicker"]
    author = deck.get("author", "")
    org = deck["org"]
    date = deck.get("date", "")

    return f"""<section class="slide slide--cover" aria-label="Cover">
  <div class="cover-wordmark">
    <span class="cover-wordmark__name">{b['name']}</span>
    <span class="cover-wordmark__sub">{b['sub']}</span>
  </div>
  <div class="cover-signature">{b['signature']}</div>
  <div class="cover-hero">
    <div class="cover-kicker animate-in">{kicker}</div>
    <h1 class="animate-in delay-1">{slide["h1"]}</h1>
    <p class="cover-subtitle animate-in delay-2">{subtitle_html}</p>
  </div>
  <div class="cover-meta">
    <div><strong>발표자</strong>{author}</div>
    <div><strong>채널</strong>{org}</div>
    <div><strong>일시</strong>{date}</div>
  </div>
</section>"""


def render_closing(slide: dict, deck: dict, brand: dict) -> str:
    md = build_md()
    body_md = "\n".join(slide["body_lines"])
    subtitle_md, rest_md = extract_subtitle(body_md)
    body_html = md.render(rest_md) if rest_md.strip() else ""
    body_html = apply_visual_transforms(body_html)

    kicker = slide["meta"].get("kicker", "Q&A")
    aria = slide["meta"].get("aria", _strip_html(slide["h1"]))
    sub_html = md.renderInline(subtitle_md) if subtitle_md else ""

    return f"""<section class="slide slide--closing" aria-label="{aria}">
  <div class="slide-header">
    {_make_brand_mark(brand)}
    <div class="slide-section-tag">Thank you</div>
  </div>
  <div class="slide-body" style="justify-content:flex-start;">
    <div class="cover-kicker animate-in">{kicker}</div>
    <h1 class="animate-in delay-1">{slide["h1"]}</h1>
    <p class="closing-sub animate-in delay-2">{sub_html}</p>
{body_html}
  </div>
</section>"""


# ---------- shell ----------

SHELL = """<!DOCTYPE html>
<html lang="ko" class="theme-light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{doc_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
  <script>Chart.defaults.animation = false;</script>
  <script src="https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.js"></script>
  <link rel="stylesheet" href="{css_href}">
  {brand_style}
</head>
<body>
  <a href="#main-content" class="skip-to-content" style="position:absolute;left:-9999px;">Skip to content</a>
  <div class="viz-menu">
    <button class="viz-menu-toggle" onclick="toggleMenu()" aria-label="Menu">
      <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <line x1="3" y1="5" x2="17" y2="5"/><line x1="3" y1="10" x2="17" y2="10"/><line x1="3" y1="15" x2="17" y2="15"/>
      </svg>
    </button>
    <div class="viz-menu-dropdown" id="vizMenuDropdown">
      <button onclick="cycleTheme()"><span id="themeIcon">☀️</span><span id="themeLabel">Light</span></button>
      <button onclick="downloadImage()"><span>📥</span><span>Download PNG</span></button>
      <button onclick="window.print()"><span>🖨️</span><span>Print / PDF</span></button>
    </div>
  </div>
  <div class="deck-progress"><div class="deck-progress__fill" id="progressFill"></div></div>
  <main id="main-content" role="main">
    <div class="deck">
      <div class="stage">
        <div class="slides" id="slidesContainer">
{slides}
        </div>
      </div>
    </div>
    <nav class="slide-nav" aria-label="Slide navigation">
      <button onclick="prevSlide()" aria-label="Previous slide">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
      </button>
      <span class="slide-counter"><span id="slideCur">1</span> / <span id="slideTotal">{total_all}</span></span>
      <button onclick="nextSlide()" aria-label="Next slide">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
      </button>
    </nav>
  </main>
  <script src="{js_href}"></script>
</body>
</html>
"""


def load_src(src: Path) -> tuple[str, str]:
    """단일 MD 또는 디렉토리의 *.md concat. (md_text, stem) 반환."""
    if src.is_file():
        return src.read_text(), src.stem
    if src.is_dir():
        parts = sorted(p for p in src.iterdir() if p.suffix == ".md" and p.is_file())
        if not parts:
            sys.exit(f"❌ {src} 안에 *.md 파일이 없음")
        chunks = [p.read_text() for p in parts]
        joined = ""
        for chunk in chunks:
            if joined and not joined.endswith("\n"):
                joined += "\n"
            joined += chunk
        print(f"  📂 dir mode: {len(parts)} files → {sum(len(c) for c in chunks)} chars")
        for p in parts:
            print(f"     · {p.name}")
        return joined, src.name
    sys.exit(f"❌ not a file or directory: {src}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path, help="MD source file or directory of *.md")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--brand", type=Path, default=None,
                    help="brand.yaml 경로. 미지정 시 <src 부모>/brand.yaml > template/brand.default.yaml")
    ap.add_argument("--html-only", action="store_true")
    args = ap.parse_args()

    src = args.src.resolve()
    md_text, stem = load_src(src)

    out_dir = args.out.resolve() if args.out else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_html = out_dir / f"{stem}.html"
    out_pdf = out_dir / f"{stem}.pdf"

    # brand 로드: 콘텐츠 기준 폴더는 src 자신(디렉토리) 또는 src.parent(파일).
    brand_lookup_dir = src if src.is_dir() else src.parent
    brand = load_brand(content_dir=brand_lookup_dir, override=args.brand)

    deck_meta, body = parse_frontmatter(md_text)

    deck_meta.setdefault("title", f"{brand['brand']['name']} 슬라이드")
    deck_meta.setdefault("subtitle", "")
    deck_meta.setdefault("author", "")
    deck_meta.setdefault("version", "")
    deck_meta.setdefault("kicker", brand["brand"]["slides_kicker"])
    deck_meta.setdefault("org", brand["brand"]["name"])

    css_rel = os.path.relpath(HERE / "theme_slides.css", out_html.parent).replace("\\", "/")
    js_rel = os.path.relpath(HERE / "deck.js", out_html.parent).replace("\\", "/")

    slides = split_slides(body)
    if not slides:
        sys.exit("❌ 슬라이드를 찾을 수 없음 (`# H1` 한 줄 이상 필요)")

    content_total = sum(
        1 for s in slides if s["meta"].get("variant", "default") == "default"
    )
    content_idx = 0
    rendered: list[str] = []
    for slide in slides:
        variant = slide["meta"].get("variant", "default")
        if variant == "cover":
            rendered.append(render_cover(slide, deck_meta, brand))
        elif variant == "section":
            rendered.append(render_section(slide, deck_meta))
        elif variant == "closing":
            rendered.append(render_closing(slide, deck_meta, brand))
        else:
            content_idx += 1
            rendered.append(render_default(slide, content_idx, content_total, deck_meta, brand))

    full_html = SHELL.format(
        doc_title=deck_meta["title"],
        slides="\n".join(rendered),
        total_all=len(slides),
        brand_style=make_brand_style_block(brand),
        css_href=css_rel,
        js_href=js_rel,
    )

    # 콘텐츠 안에 비-페르소나 색상이 있을 경우를 대비한 안전장치 (사용자 콘텐츠 출처 다양)
    full_html, n_recolor = normalize_palette(full_html)
    if n_recolor:
        print(f"  🎨 비-페르소나 색상 정규화: {n_recolor} 건")

    out_html.write_text(full_html)
    print(
        f"  💾 HTML: {out_html}  ({out_html.stat().st_size // 1024} KB)  "
        f"· {len(slides)}장 (콘텐츠 {content_total})"
    )

    if args.html_only:
        return

    try:
        from .render import slides_to_pdf
    except ImportError:
        from render import slides_to_pdf  # type: ignore

    print("  🖨️  PDF 변환 중 ...")
    slides_to_pdf(out_html, out_pdf)
    print(f"  💾 PDF:  {out_pdf}  ({out_pdf.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
