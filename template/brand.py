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
