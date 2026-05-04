"""ai_odyssey_publisher — 리포트 빌드 코어 헬퍼.

원본 키트에서 추출한 12 심볼. 페르소나-중립 토큰을 사용하며,
상위 빌더(build_report.py / build_slides.py) 가 palette.normalize_palette
패스로 사용자 콘텐츠의 비-페르소나 색상까지 정규화한다.
"""
from __future__ import annotations

import re

from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin


# ---------- markdown ----------

def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[\s/]+", "-", text)
    text = re.sub(r"[^0-9A-Za-zㄱ-힝\-\.]+", "", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "section"


def build_md() -> MarkdownIt:
    return (
        MarkdownIt("commonmark", {"html": True, "linkify": True, "typographer": False})
        .enable(["table", "strikethrough"])
        .use(anchors_plugin, max_level=4, permalink=False, slug_func=_slugify)
    )


# ---------- reference parsing ----------

REF_LINE_RE = re.compile(r"^\[\^(\d+)\]:\s*(.+?)\s*$", re.MULTILINE)
REF_GROUP_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)


def parse_references(md_text: str) -> list[dict]:
    """99_references.md 를 파싱해서 레퍼런스 목록을 반환.

    반환 구조:
        [{num:int, group:str, body:str(html 변환 안 된 raw)}...]
        순번은 원본 [^N] 숫자 기준으로 정렬.
    """
    groups = []  # [(start_idx, name), ...]
    for m in REF_GROUP_RE.finditer(md_text):
        groups.append((m.start(), m.group(1).strip()))

    def group_for(pos: int) -> str:
        name = ""
        for start, gname in groups:
            if start <= pos:
                name = gname
        return name

    items: list[dict] = []
    for m in REF_LINE_RE.finditer(md_text):
        num = int(m.group(1))
        body = m.group(2).strip()
        items.append({"num": num, "group": group_for(m.start()), "body": body})

    items.sort(key=lambda x: x["num"])
    return items


def render_ref_body(body: str) -> str:
    """각주 본문의 URL 을 <a> 로, 백틱을 <code> 로 치환."""
    body = re.sub(r"`([^`]+)`", r"<code>\1</code>", body)

    def urlize(m):
        url = m.group(0)
        return f'<a href="{url}" target="_blank" rel="noopener">{url}</a>'

    body = re.sub(r"https?://[^\s<>)]+", urlize, body)
    return body


def extract_ref_urls(items: list[dict]) -> dict[int, str]:
    """참고문헌 본문에서 첫 번째 URL 을 추출해 {num: url} 로 반환."""
    url_re = re.compile(r"https?://[^\s<>)]+")
    out: dict[int, str] = {}
    for it in items:
        m = url_re.search(it["body"])
        if m:
            out[it["num"]] = m.group(0)
    return out


def convert_footrefs(html: str, known: set[int], url_map: dict[int, str] | None = None) -> str:
    """본문의 [^N] 을 외부 URL 링크(있으면)로, 없으면 내부 #ref-N 으로 변환."""
    url_map = url_map or {}

    def rep(m):
        n = int(m.group(1))
        if n not in known:
            return m.group(0)
        href = url_map.get(n, f"#ref-{n}")
        is_external = href.startswith("http")
        tgt = ' target="_blank" rel="noopener"' if is_external else ""
        return f'<sup class="ref-cite"><a href="{href}"{tgt}>[{n}]</a></sup>'

    return re.sub(r"\[\^(\d+)\]", rep, html)


# ---------- visual component post-processing ----------

_BADGE_LABELS = {
    ("risk", "low"):   ("badge--low",   "낮음"),
    ("risk", "mid"):   ("badge--mid",   "중간"),
    ("risk", "high"):  ("badge--high",  "높음"),
    ("diff", "low"):   ("badge--low",   "쉬움"),
    ("diff", "mid"):   ("badge--mid",   "중간"),
    ("diff", "high"):  ("badge--high",  "어려움"),
    ("cost", "low"):   ("badge--low",   "저"),
    ("cost", "mid"):   ("badge--mid",   "중"),
    ("cost", "high"):  ("badge--high",  "고"),
    ("tier", "1"):     ("badge--tier1", "Tier 1"),
    ("tier", "2"):     ("badge--tier2", "Tier 2"),
    ("tier", "3"):     ("badge--tier3", "Tier 3"),
    ("trend", "up"):   ("badge--up",    "상승"),
    ("trend", "down"): ("badge--down",  "하락"),
    ("trend", "flat"): ("badge--flat",  "유지"),
    ("status", "ok"):     ("badge--ok",     "정상"),
    ("status", "warn"):   ("badge--warn",   "주의"),
    ("status", "danger"): ("badge--danger", "위험"),
}

_BADGE_TOKEN_RE = re.compile(
    r"\[(risk|diff|cost|tier|trend|status):([a-z0-9]+)(?:\|([^\]]+))?\]"
)


def _apply_badges(html: str) -> str:
    """[risk:high], [diff:mid|구현 복잡] 같은 인라인 토큰을 <span class="badge"> 로 치환."""
    def rep(m: re.Match) -> str:
        kind, key, override = m.group(1), m.group(2), m.group(3)
        hit = _BADGE_LABELS.get((kind, key))
        if not hit:
            return m.group(0)
        mod, default_label = hit
        label = override.strip() if override else default_label
        return f'<span class="badge {mod}">{label}</span>'

    return _BADGE_TOKEN_RE.sub(rep, html)


def apply_visual_transforms(html: str) -> str:
    """마크다운의 의미 패턴을 시각 컴포넌트로 승격.

    - <strong>핵심 메시지</strong>: 로 시작하는 <p> → hero callout
    - <strong>실무 시사점...</strong> 뒤의 콘텐츠 → insight callout
    - <strong>배경 설명</strong> / <strong>상세 내용</strong> → h4 스타일
    - <strong>더 깊이 읽기</strong> 뒤의 list → 푸터 reading-more 박스
    - <table> → cmp-table 클래스
    - <ul>/<ol> 최상위 → bullets/nums 클래스
    """
    # 1. 핵심 메시지 → hero callout
    html = re.sub(
        r'<p><strong>핵심 메시지</strong>\s*[:：]\s*(.+?)</p>',
        r'<div class="callout callout--hero">'
        r'<span class="callout__kicker">핵심 메시지</span>'
        r'<span class="callout__body">\1</span>'
        r'</div>',
        html, flags=re.DOTALL
    )

    # 2. 실무 시사점 → insight callout
    html = re.sub(
        r'<p><strong>실무 시사점([^<]*)</strong></p>\s*'
        r'(<(p|ul|ol)(?:\s[^>]*)?>.+?</\3>)',
        r'<div class="callout callout--insight">'
        r'<span class="callout__kicker">실무 시사점\1</span>'
        r'<div class="callout__body">\2</div>'
        r'</div>',
        html, flags=re.DOTALL
    )

    # 2b. 섹션 요약 → section-summary 박스
    def _promote_section_summary(m: re.Match) -> str:
        subtitle = (m.group("subtitle") or "").strip()
        kicker = f"Section Summary · {subtitle}" if subtitle else "Section Summary · 핵심 요약"
        return (
            '<div class="section-summary">'
            f'<span class="section-summary__kicker">{kicker}</span>'
            f'<div class="section-summary__body">{m.group("listblock")}</div>'
            '</div>'
        )

    html = re.sub(
        r'<p><strong>섹션 요약(?:\s*[—–-]\s*(?P<subtitle>[^<]+?))?\s*</strong></p>\s*'
        r'(?P<listblock><(?P<tag>ul|ol)(?:\s[^>]*)?>.+?</(?P=tag)>)',
        _promote_section_summary,
        html, flags=re.DOTALL
    )

    # 3. 배경 설명 / 상세 내용 / 배경 → h4 스타일
    for label in ["배경 설명", "상세 내용", "배경", "개요", "요약"]:
        html = re.sub(
            rf'<p><strong>{label}</strong></p>',
            rf'<h4 class="sub-h4">{label}</h4>',
            html
        )
        html = re.sub(
            rf'<p><strong>{label}</strong>\s+(.+?)</p>',
            rf'<h4 class="sub-h4">{label}</h4>\n<p>\1</p>',
            html, flags=re.DOTALL
        )

    # 4. 더 깊이 읽기 → 푸터 reading-more 박스
    html = re.sub(
        r'<p><strong>더 깊이 읽기</strong></p>\s*'
        r'(<(?:ul|ol)(?:\s[^>]*)?>.+?</(?:ul|ol)>)',
        r'<aside class="reading-more">'
        r'<span class="reading-more__kicker">Further Reading · 더 깊이 읽기</span>'
        r'\1'
        r'</aside>',
        html, flags=re.DOTALL
    )
    html = re.sub(
        r'<p><strong>더 깊이 읽기</strong></p>\s*'
        r'((?:<p(?:\s[^>]*)?>.+?</p>\s*){1,3})',
        r'<aside class="reading-more">'
        r'<span class="reading-more__kicker">Further Reading · 더 깊이 읽기</span>'
        r'\1'
        r'</aside>',
        html, flags=re.DOTALL
    )

    # 5. 모든 <table> 에 cmp-table 클래스 부여
    html = re.sub(r'<table>', '<table class="cmp-table">', html)

    # 5a-bis. 테이블 캡션
    def _wrap_table_caption(m: re.Match) -> str:
        num = m.group(1)
        title = m.group(2).strip()
        rest = (m.group(3) or '').strip()
        sub_html = f'<span class="cmp-table__sub">{rest}</span>' if rest else ''
        table_html = m.group(4)
        if '<caption' in table_html:
            return table_html
        caption = (
            f'<caption class="cmp-table__caption">'
            f'<div class="cmp-table__caption-inner">'
            f'<span class="cmp-table__chip">표 {num}</span>'
            f'<span class="cmp-table__title">{title}</span>'
            f'{sub_html}'
            f'</div>'
            f'</caption>'
        )
        return table_html.replace(
            '<table class="cmp-table">',
            f'<table class="cmp-table">{caption}', 1
        )

    html = re.sub(
        r'<p>\s*<strong>\s*표\s+([\w\.\-]+)\s*[\.·:]\s*([^<]+?)\s*</strong>\s*(.*?)</p>\s*'
        r'(<table class="cmp-table">.*?</table>)',
        _wrap_table_caption,
        html, flags=re.DOTALL
    )

    # 5b. 인라인 배지 토큰 치환
    html = _apply_badges(html)

    # 5c. 포지셔닝 맵 자리표시자 → <canvas> 블록 — 데이터는 콘텐츠 주석에서 받음.
    #     `<!-- positioning-map: { "title": "...", "subtitle": "...",
    #                              "legend": [{"label":"X","color":"#..."}] } -->`
    #     데이터 미제공 시 placeholder 는 제거 (빈 자리표시자 출력 안 함).
    html = _POSITIONING_MAP_RE.sub(lambda m: _build_scatter_map(m.group(1)), html)

    # 6. 최상위 리스트에 bullets / nums 클래스
    html = re.sub(r'<ul>\s*\n<li>', '<ul class="bullets">\n<li>', html)
    html = re.sub(r'<ol>\s*\n<li>', '<ol class="nums">\n<li>', html)

    # 8a. .prompt-card__body 내부의 <p>/</p> 제거
    def _strip_p_in_prompt_body(m: re.Match) -> str:
        inner = m.group(1)
        inner = re.sub(r"</?p(?:\s[^>]*)?>", "", inner)
        return f'<div class="prompt-card__body">{inner}</div>'

    html = re.sub(
        r'<div class="prompt-card__body">(.*?)</div>',
        _strip_p_in_prompt_body, html, flags=re.DOTALL
    )

    # 8. <h3>슬라이드 N. 제목</h3> → 슬라이드 chip 삽입
    def slide_chip(m):
        title = m.group(1).strip()
        chip_m = re.match(r'슬라이드\s+([\d\~가-힣]+)\.?\s*(.*)', title)
        if not chip_m:
            return m.group(0)
        num, rest = chip_m.group(1), chip_m.group(2).strip()
        return (
            f'<h3 class="slide-h3">'
            f'<span class="slide-chip">SLIDE {num}</span>'
            f'<span class="slide-h3__text">{rest}</span>'
            f'</h3>'
        )

    html = re.sub(r'<h3[^>]*>(슬라이드[^<]+)</h3>', slide_chip, html)

    return html


# Executive Summary hero KPI grid — 데이터는 콘텐츠 frontmatter 의
# `<!-- hero-kpi: {kpis: [...], summary: "..."} -->` 주석에서 받는다.
_HERO_KPI_RE = re.compile(r'<!--\s*hero-kpi:\s*(.+?)\s*-->', re.DOTALL)

# 포지셔닝 맵 — 데이터는 콘텐츠 본문의
# `<!-- positioning-map: {title, subtitle, legend: [...]} -->` 주석에서 받는다.
# 데이터 미제공(`<!-- positioning-map -->`) 시 placeholder 제거.
_POSITIONING_MAP_RE = re.compile(
    r'<!--\s*positioning-map(?:\s*:\s*(.+?))?\s*-->', re.DOTALL
)


def _build_scatter_map(json_text: str | None) -> str:
    """positioning-map JSON → scatter-map HTML. JSON 미제공 시 빈 문자열."""
    if not json_text:
        return ""
    import json
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        return ""
    title = data.get("title", "")
    subtitle = data.get("subtitle", "")
    legend = data.get("legend", [])
    title_html = f'<div class="scatter-map__title">{title}</div>' if title else ""
    subtitle_html = f'<div class="scatter-map__subtitle">{subtitle}</div>' if subtitle else ""
    legend_items = "".join(
        f'<span class="scatter-map__legend-item">'
        f'<span class="scatter-map__legend-dot" style="background:{item["color"]}"></span>'
        f'{item["label"]}</span>'
        for item in legend
    )
    legend_html = f'<div class="scatter-map__legend">{legend_items}</div>' if legend else ""
    return (
        '<div class="scatter-map">'
        f'{title_html}'
        f'{subtitle_html}'
        '<div class="scatter-map__canvas-wrap">'
        '<canvas id="positioningMap" role="img" aria-label="positioning map"></canvas>'
        '</div>'
        f'{legend_html}'
        '</div>'
    )


def parse_hero_kpi(md_text: str) -> tuple[list[dict], str]:
    """`<!-- hero-kpi: {...} -->` JSON 추출. 없으면 ([], "")."""
    import json
    m = _HERO_KPI_RE.search(md_text)
    if not m:
        return [], ""
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return [], ""
    return data.get("kpis", []), data.get("summary", "")


def build_hero_kpi(kpis: list[dict], summary: str = "") -> str:
    """Executive Summary 의 KPI 그리드 + 한 줄 요약 callout. kpis 비면 빈 문자열."""
    if not kpis:
        return ""
    cols = len(kpis)
    cards: list[str] = []
    for k in kpis:
        cards.append(
            '  <div class="kpi">\n'
            f'    <span class="kpi__value">{k["value"]}'
            f'<span class="kpi__value-suf">{k.get("suffix","")}</span></span>\n'
            f'    <span class="kpi__label">{k.get("label","")}</span>\n'
            f'    <span class="kpi__sub">{k.get("sub","")}</span>\n'
            '  </div>'
        )
    summary_html = (
        '\n<div class="callout callout--hero">\n'
        '  <span class="callout__kicker">한 줄 요약</span>\n'
        f'  <span class="callout__body">{summary}</span>\n'
        '</div>'
    ) if summary else ""
    return (
        f'\n<div class="kpi-grid hero-kpi" style="--cols: {cols};">\n'
        + "\n".join(cards)
        + "\n</div>"
        + summary_html
        + "\n"
    )


def build_section_divider(num: str, tag: str, title: str, subtitle: str = "") -> str:
    title_html = f'<h2 class="section-divider__title">{title}</h2>' if title else ''
    return f"""
    <aside class="section-divider" aria-hidden="true">
      <div class="section-divider__tag">{tag}</div>
      {title_html}
      {'<p class="section-divider__subtitle">' + subtitle + '</p>' if subtitle else ''}
      <div class="section-divider__rule"></div>
      <div class="section-divider__num">{num}</div>
    </aside>
    """


# ---------- section wrapping ----------

def strip_h1_and_front_matter(html: str) -> tuple[str, dict]:
    """00_front_matter 의 h1 과 메타 문단, '## 목차' 는 커버·TOC 로 이동·삭제."""
    meta = {"title": "", "subtitle_meta": []}

    h1_m = re.search(r"<h1[^>]*>(.+?)</h1>", html, flags=re.DOTALL)
    if h1_m:
        meta["title"] = re.sub(r"<[^>]+>", "", h1_m.group(1)).strip()
        html = html[h1_m.end():]

    p_m = re.search(r"<p>(.+?)</p>", html, flags=re.DOTALL)
    if p_m:
        inner = p_m.group(1)
        meta["subtitle_meta"] = [x.strip() for x in inner.split("<br />")]
        html = html[:p_m.start()] + html[p_m.end():]

    html = re.sub(r"^\s*<hr\s*/>\s*", "", html, count=1)

    toc_m = re.search(r'<h2[^>]*id="목차"[^>]*>.*?</h2>\s*<ul>.*?</ul>', html, flags=re.DOTALL)
    if toc_m:
        html = html[:toc_m.start()] + html[toc_m.end():]

    return html, meta


def split_front_matter_sections(html: str) -> list[dict]:
    """Executive Summary 영역만 별도 섹션으로. 나머지는 드롭.

    front-matter 의 h2 헤딩은 영문 "Executive Summary" (slug `executive-summary`) 를 유지해야 한다.
    """
    sections: list[dict] = []
    es_m = re.search(r'<h2[^>]*id="executive-summary"[^>]*>(.+?)</h2>(.*?)(?=<hr\s*/>|$)',
                     html, flags=re.DOTALL)
    if es_m:
        title = re.sub(r"<[^>]+>", "", es_m.group(1)).strip()
        body = es_m.group(2)
        sections.append({"title": title, "body": body})
    return sections


def wrap_section(html_body: str, number: str, title_override: str | None = None,
                 kicker_prefix: str = "Section",
                 keep_first_h2: bool = False) -> str:
    """섹션 HTML 을 <section class="report-section page-break"> 로 감싸고 kicker·lede 추가.

    keep_first_h2=True 면 첫 h2 를 교체하지 않고 kicker 만 본문 앞에 삽입한다
    (예: 부록 — 빈 표지 페이지를 피하려고 첫 h2 를 '부록 A.' 로 그대로 둔다).
    """
    h2_m = re.search(r"<h2[^>]*>(.+?)</h2>", html_body, flags=re.DOTALL)
    if h2_m and not title_override:
        title_text = re.sub(r"<[^>]+>", "", h2_m.group(1)).strip()
    else:
        title_text = title_override or ""

    kicker = f'{kicker_prefix} {number} · {title_text}'
    if keep_first_h2:
        replacement = f'<div class="report-section__kicker">{kicker}</div>\n'
        html_body = replacement + html_body
    else:
        replacement = (
            f'<div class="report-section__kicker">{kicker}</div>\n'
            f'<h2>{title_text}</h2>'
        )
        if h2_m:
            html_body = html_body[:h2_m.start()] + replacement + html_body[h2_m.end():]
        else:
            html_body = replacement + html_body

    html_body = re.sub(
        r'(<h2>[^<]*</h2>\s*)<p>(.+?)</p>',
        r'\1<p class="report-section__lede">\2</p>',
        html_body, count=1, flags=re.DOTALL
    )

    return (
        f'<section class="report-section s{int(number)} page-break">\n'
        f'{html_body}\n'
        f'</section>'
    )


# ---------- reference appendix ----------

def build_references_appendix(items: list[dict]) -> str:
    """참고문헌 부록 — var(--brand-primary) 사용."""
    from collections import OrderedDict
    grouped: "OrderedDict[str, list[dict]]" = OrderedDict()
    for it in items:
        grouped.setdefault(it["group"] or "기타", []).append(it)

    parts = [
        '<section class="report-appendix s-refs page-break">',
        '  <div class="report-section__kicker">Appendix · References</div>',
        '  <h2>참고 문헌 · 원본 출처</h2>',
        '  <p class="report-section__lede">본문의 각주 번호 <code>[N]</code> 는 아래 목록의 항목과 1:1 매칭된다. 모든 URL 은 공개 접근 가능한 원본이다 (수집 시점 2026-04-20).</p>',
    ]
    for gname, entries in grouped.items():
        parts.append(f'  <h3>{gname}</h3>')
        parts.append('  <ol class="references" style="list-style:none; padding:0;">')
        for it in entries:
            body_html = render_ref_body(it["body"])
            parts.append(
                f'    <li id="ref-{it["num"]}" style="display:flex;gap:10px;padding:6px 0;border-bottom:1px dashed var(--border);">'
                f'<span style="flex:0 0 auto;font-family:\'JetBrains Mono\',monospace;font-weight:800;color:var(--brand-primary);min-width:36px;">[{it["num"]}]</span>'
                f'<span style="flex:1;font-size:9.5pt;line-height:1.5;">{body_html}</span>'
                '</li>'
            )
        parts.append('  </ol>')
    parts.append('</section>')
    return "\n".join(parts)


# ---------- toc stub ----------

def build_toc_stub() -> str:
    return """
    <nav class="report-toc page-break">
      <h1 class="report-toc__title">목차</h1>
      <ol class="report-toc__list"></ol>
    </nav>
    """
