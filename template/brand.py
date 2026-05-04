"""brand.yaml 로더 — 페르소나 텍스트/색상 단일 conf.

우선순위:
  1. --brand FILE (CLI 인자)
  2. <content_dir>/brand.yaml (콘텐츠 폴더 옆)
  3. template/brand.default.yaml (패키지 기본 — AI Odyssey)

반환 dict 구조: {"brand": {...}, "palette": {...}}.
"""
from __future__ import annotations

from pathlib import Path

import yaml

_HERE = Path(__file__).parent.resolve()
_DEFAULT = _HERE / "brand.default.yaml"


def load_brand(content_dir: Path | None = None, override: Path | None = None) -> dict:
    """brand.yaml 로드. 우선순위: override > content_dir/brand.yaml > brand.default.yaml.

    오버라이드 파일은 부분만 정의해도 되며, 미정의 키는 brand.default.yaml 에서 보충된다.
    """
    base = yaml.safe_load(_DEFAULT.read_text(encoding="utf-8")) or {}

    user_path: Path | None = None
    if override is not None:
        user_path = override
    elif content_dir is not None and (content_dir / "brand.yaml").exists():
        user_path = content_dir / "brand.yaml"

    if user_path is None:
        return base

    user = yaml.safe_load(user_path.read_text(encoding="utf-8")) or {}
    return _deep_merge(base, user)


def _deep_merge(base: dict, override: dict) -> dict:
    """dict 깊이 병합 — override 우선. 중첩 dict 만 재귀, 그 외는 override 값으로 대체."""
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def make_brand_style_block(brand: dict) -> str:
    """`<style>:root{...}</style>` — theme CSS 의 var() fallback 을 override 한다.

    러닝 헤더/모노그램 텍스트만 주입 (페이지 마진박스 content 가 var() 로 받음).
    페이지 색상 토큰은 theme CSS 의 :root 가 이미 페르소나 fallback 을 들고 있으므로
    여기서는 미주입 — 추후 phase 에서 palette 까지 확장 예정.
    """
    b = brand["brand"]
    return (
        '<style id="brand-vars">:root{\n'
        f'  --running-header-left: "{b["running_header_left"]}";\n'
        f'  --running-header-right: "{b["running_header_right"]}";\n'
        f'  --slide-section-monogram: "{b["monogram"]}";\n'
        '}</style>'
    )
