"""template — Markdown → report/slides 듀얼 빌더 + brand.yaml 페르소나.

진입점:
    python -m template build report <content_dir> [...]
    python -m template build slides <slides.md|dir> [...]

레거시 진입점 (그대로 동작):
    python -m template.build_report <content_dir> [...]
    python -m template.build_slides <slides.md> [...]
"""
from __future__ import annotations
