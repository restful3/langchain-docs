#!/usr/bin/env python3
"""SVG/Markdown 의 비-페르소나 hex/CSS 변수를 페르소나 토큰으로 일괄 정규화.

사용:
    python palette.py < input.md > output.md
    python palette.py --check < input.md       # 매칭 라인만 출력 (변경 없음)
    python palette.py --self-test              # 합성 입력 단위 테스트

적용 범위: 인라인 SVG fill/stroke, CSS 변수, rgba(), Tailwind/CSS hex.
"""
from __future__ import annotations

import argparse
import sys

# (비-페르소나 패턴, 페르소나 치환) — 순서 의존: 더 긴 변수명을 짧은 것보다 먼저.
COLOR_MAP: list[tuple[str, str]] = [
    # ── 1. Primary brand → Deep Navy ──
    ("#A50034", "#0F2C59"),
    ("#a50034", "#0f2c59"),
    ("#6E0022", "#091F40"),
    ("#6e0022", "#091f40"),
    ("#E4002B", "#2563EB"),
    ("#e4002b", "#2563eb"),
    # rgba 변형
    ("rgba(165,0,52,", "rgba(15,44,89,"),
    ("rgba(165, 0, 52,", "rgba(15, 44, 89,"),
    ("rgba(228,0,43,", "rgba(37,99,235,"),
    ("rgba(228, 0, 43,", "rgba(37, 99, 235,"),

    # ── 2. 토큰 외 회색 → text-secondary (#6B6B72) ──
    # Tailwind zinc/slate 계열 변형을 단일 토큰으로 통합.
    ("#5B5B62", "#6B6B72"),
    ("#5b5b62", "#6b6b72"),
    ("#3F3F46", "#6B6B72"),
    ("#3f3f46", "#6b6b72"),
    ("#475569", "#6B6B72"),
    ("#27272A", "#6B6B72"),
    ("#27272a", "#6b6b72"),
    ("#334155", "#6B6B72"),
    ("#64748B", "#6B6B72"),
    ("#64748b", "#6b6b72"),
    # 연회색 → bg/surface-hover 계열 (배경에서 사용)
    ("#D4D4D8", "#F5F5F4"),
    ("#d4d4d8", "#f5f5f4"),
    ("#E5E5E5", "#F5F5F4"),
    ("#e5e5e5", "#f5f5f4"),

    # ── 3. 녹색 변형 → positive (#059669) ──
    ("#10B981", "#059669"),
    ("#10b981", "#059669"),
    ("#047857", "#059669"),
    ("#0F9D58", "#059669"),
    ("#0f9d58", "#059669"),
    # 연녹 배경 → 그대로 유지 (positive-soft 역할)

    # ── 4. red 우회 → negative (#E11D48) ──
    ("#DC2626", "#E11D48"),
    ("#dc2626", "#e11d48"),
    ("#991B1B", "#9F1239"),  # red-900 → rose-900 변형
    ("#991b1b", "#9f1239"),
    ("#EA4335", "#E11D48"),  # Google red → negative (벤더 식별 잔존이 부정적)
    ("#ea4335", "#e11d48"),
    # 연빨강 → primary-soft 톤 일관성 유지
    ("#FFF7F9", "#F5F5F4"),
    ("#fff7f9", "#f5f5f4"),
    ("#FEE2E2", "#FEF2F2"),  # 가장 연한 red bg 만 유지
    # rgba 연빨강 → 회색 톤
    ("rgba(255,186,186,", "rgba(107,107,114,"),
    ("rgba(255, 186, 186,", "rgba(107, 107, 114,"),

    # ── 5. 청색 변형 → primary-active (#2563EB) — 차트 컨벤션 ──
    ("#1E40AF", "#2563EB"),
    ("#1e40af", "#2563eb"),
    ("#0369A1", "#2563EB"),  # sky-700 → primary-active
    ("#0369a1", "#2563eb"),
    ("#4285F4", "#2563EB"),  # Google blue → primary-active
    ("#4285f4", "#2563eb"),
    ("#1E293B", "#0F2C59"),  # slate-800 → primary
    ("#1e293b", "#0f2c59"),
    ("#0F172A", "#091F40"),  # slate-900 → primary-deep
    ("#0f172a", "#091f40"),
    ("#020617", "#091F40"),  # near-black → primary-deep
    ("#94A3B8", "#6B6B72"),  # slate-400 → text-secondary
    ("#94a3b8", "#6b6b72"),
    # 연청 배경 → 그대로 유지 (primary-soft 대응)
]

# ─────────────────────────────────────────────────────────────────────────
# MONOCHROME_MAP — `--monochrome` 모드에서 COLOR_MAP 위에 적용.
# 따뜻한 hex(노랑/오렌지/핑크/라일락) → primary-soft (8% alpha).
# 차가운 hex(하늘/민트) → primary-active (10% alpha).
# 채도 높은 fill (orange/pink/yellow saturated) → primary 단색.
# Material/Tailwind 팔레트 기준. 페르소나 단색 + 명도 단계로 강등.
# ─────────────────────────────────────────────────────────────────────────
MONOCHROME_MAP: list[tuple[str, str]] = [
    # ── 연한 배경 (warm) → primary-soft ──
    ("#FFF7E6", "rgba(15,44,89,0.08)"), ("#fff7e6", "rgba(15,44,89,0.08)"),
    ("#FEF3C7", "rgba(15,44,89,0.08)"), ("#fef3c7", "rgba(15,44,89,0.08)"),
    ("#FFF9C4", "rgba(15,44,89,0.08)"), ("#fff9c4", "rgba(15,44,89,0.08)"),
    ("#FCE7F3", "rgba(15,44,89,0.08)"), ("#fce7f3", "rgba(15,44,89,0.08)"),
    ("#F3E8FF", "rgba(15,44,89,0.08)"), ("#f3e8ff", "rgba(15,44,89,0.08)"),
    ("#E1BEE7", "rgba(15,44,89,0.08)"), ("#e1bee7", "rgba(15,44,89,0.08)"),
    ("#FFCDD2", "rgba(15,44,89,0.08)"), ("#ffcdd2", "rgba(15,44,89,0.08)"),
    ("#C8E6C9", "rgba(15,44,89,0.08)"), ("#c8e6c9", "rgba(15,44,89,0.08)"),
    # ── 연한 배경 (cool) → primary-active alpha ──
    ("#D1FAE5", "rgba(37,99,235,0.10)"), ("#d1fae5", "rgba(37,99,235,0.10)"),
    ("#DBEAFE", "rgba(37,99,235,0.10)"), ("#dbeafe", "rgba(37,99,235,0.10)"),
    ("#BBDEFB", "rgba(37,99,235,0.10)"), ("#bbdefb", "rgba(37,99,235,0.10)"),
    # ── 채도 높은 fill (warm/saturated) → primary ──
    ("#F59E0B", "#0F2C59"), ("#f59e0b", "#0f2c59"),
    ("#F9A825", "#0F2C59"), ("#f9a825", "#0f2c59"),
    ("#EC4899", "#0F2C59"), ("#ec4899", "#0f2c59"),
    ("#4A148C", "#0F2C59"), ("#4a148c", "#0f2c59"),
    ("#6A1B9A", "#0F2C59"), ("#6a1b9a", "#0f2c59"),
    ("#C62828", "#0F2C59"), ("#c62828", "#0f2c59"),
    ("#1565C0", "#0F2C59"), ("#1565c0", "#0f2c59"),
    ("#2E7D32", "#0F2C59"), ("#2e7d32", "#0f2c59"),
    # ── 회색 단계 (Material) → text-secondary / 단계 ──
    ("#455A64", "#6B6B72"), ("#455a64", "#6b6b72"),
    ("#37474F", "#6B6B72"), ("#37474f", "#6b6b72"),  # blue gray 800
    ("#5D4037", "#6B6B72"), ("#5d4037", "#6b6b72"),  # brown 700
    ("#212121", "#0F0F10"),  # near-black → text
    ("#CFD8DC", "#F5F5F4"), ("#cfd8dc", "#f5f5f4"),
    # ── Material 50 (가장 연한 배경) — 위 100 보다 더 연한 단계 ──
    ("#FFF8E1", "rgba(15,44,89,0.08)"), ("#fff8e1", "rgba(15,44,89,0.08)"),  # yellow 50
    ("#E3F2FD", "rgba(15,44,89,0.08)"), ("#e3f2fd", "rgba(15,44,89,0.08)"),  # blue 50
    ("#E8F5E9", "rgba(15,44,89,0.08)"), ("#e8f5e9", "rgba(15,44,89,0.08)"),  # green 50
    ("#F3E5F5", "rgba(15,44,89,0.08)"), ("#f3e5f5", "rgba(15,44,89,0.08)"),  # purple 50
    ("#FCE4EC", "rgba(15,44,89,0.08)"), ("#fce4ec", "rgba(15,44,89,0.08)"),  # pink 50
    # ── Material 800/900 채도 높은 dark fill → primary / primary-deep ──
    ("#0D47A1", "#091F40"), ("#0d47a1", "#091f40"),  # blue 900 → primary-deep
    ("#1B5E20", "#0F2C59"), ("#1b5e20", "#0f2c59"),  # green 900
    ("#880E4F", "#0F2C59"), ("#880e4f", "#0f2c59"),  # pink 900
    ("#AD1457", "#0F2C59"), ("#ad1457", "#0f2c59"),  # pink 800
    ("#BF360C", "#0F2C59"), ("#bf360c", "#0f2c59"),  # deep orange 900
    ("#F57F17", "#0F2C59"), ("#f57f17", "#0f2c59"),  # yellow 800
]


def normalize_palette(text: str, mode: str = "strict") -> tuple[str, int]:
    """Return (normalized_text, total_replacements).

    mode="strict" (기본): COLOR_MAP 만 적용. 비-페르소나 → 페르소나 토큰.
    mode="monochrome": COLOR_MAP + MONOCHROME_MAP. 다색 콘텐츠를 단색 + 명도 단계로 강등.
    """
    rules = COLOR_MAP if mode == "strict" else COLOR_MAP + MONOCHROME_MAP
    total = 0
    for old, new in rules:
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            total += count
    return text, total


def check(text: str) -> list[tuple[int, str]]:
    """Return [(lineno, line)] for lines containing any non-persona color pattern."""
    patterns = [old for old, _ in COLOR_MAP]
    matches: list[tuple[int, str]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if any(p in line for p in patterns):
            matches.append((i, line.rstrip()))
    return matches


def self_test() -> int:
    """Synthetic-input self-test. Returns process exit code."""
    cases: list[tuple[str, str, int]] = [
        # (input, expected_output, expected_count)
        # ── Phase 1: Primary brand ──
        ('fill="#A50034"', 'fill="#0F2C59"', 1),
        ('color: #a50034;', 'color: #0f2c59;', 1),
        ('rgba(165,0,52,0.08)', 'rgba(15,44,89,0.08)', 1),
        ('rgba(165, 0, 52, 0.08)', 'rgba(15, 44, 89, 0.08)', 1),
        ('rgba(228,0,43,0.10)', 'rgba(37,99,235,0.10)', 1),
        # 페르소나 hex 는 변경 없음
        ('fill="#0F2C59"', 'fill="#0F2C59"', 0),
        # ── Phase 2: 토큰 외 회색 → text-secondary ──
        ('fill="#5B5B62"', 'fill="#6B6B72"', 1),
        ('fill="#3f3f46"', 'fill="#6b6b72"', 1),
        ('fill="#475569"', 'fill="#6B6B72"', 1),
        # ── Phase 3: 녹색 변형 → positive ──
        ('fill="#10B981"', 'fill="#059669"', 1),
        ('fill="#047857"', 'fill="#059669"', 1),
        # ── Phase 4: red 우회 → negative ──
        ('fill="#DC2626"', 'fill="#E11D48"', 1),
        ('fill="#EA4335"', 'fill="#E11D48"', 1),
        ('fill="#FFF7F9"', 'fill="#F5F5F4"', 1),
        ('rgba(255,186,186,1)', 'rgba(107,107,114,1)', 1),
        # ── Phase 5: 청색 변형 → primary-active / primary ──
        ('fill="#1E40AF"', 'fill="#2563EB"', 1),
        ('fill="#1e293b"', 'fill="#0f2c59"', 1),
        ('fill="#4285f4"', 'fill="#2563eb"', 1),
        # ── 외부판 토큰은 변경 없음 ──
        ('fill="#6B6B72"', 'fill="#6B6B72"', 0),
        ('fill="#059669"', 'fill="#059669"', 0),
        ('fill="#E11D48"', 'fill="#E11D48"', 0),
    ]
    # ── monochrome 모드 케이스 (COLOR_MAP + MONOCHROME_MAP) ──
    mono_cases: list[tuple[str, str, int]] = [
        # 따뜻한 연배경 → primary-soft
        ('fill="#FEF3C7"', 'fill="rgba(15,44,89,0.08)"', 1),
        ('fill="#fff9c4"', 'fill="rgba(15,44,89,0.08)"', 1),
        # 차가운 연배경 → primary-active alpha
        ('fill="#bbdefb"', 'fill="rgba(37,99,235,0.10)"', 1),
        # 채도 높은 fill → primary
        ('fill="#f9a825"', 'fill="#0f2c59"', 1),
        ('fill="#4a148c"', 'fill="#0f2c59"', 1),
        # 회색 → text-secondary
        ('fill="#455a64"', 'fill="#6b6b72"', 1),
        ('fill="#212121"', 'fill="#0F0F10"', 1),
        # strict 모드 매핑은 monochrome 에서도 통과
        ('fill="#A50034"', 'fill="#0F2C59"', 1),
    ]
    failures = 0
    for i, (inp, want_out, want_count) in enumerate(cases, start=1):
        got_out, got_count = normalize_palette(inp)
        if got_out != want_out or got_count != want_count:
            failures += 1
            print(f"FAIL strict {i}: input={inp!r}", file=sys.stderr)
            print(f"  expected: ({want_out!r}, {want_count})", file=sys.stderr)
            print(f"  got     : ({got_out!r}, {got_count})", file=sys.stderr)
    for i, (inp, want_out, want_count) in enumerate(mono_cases, start=1):
        got_out, got_count = normalize_palette(inp, mode="monochrome")
        if got_out != want_out or got_count != want_count:
            failures += 1
            print(f"FAIL mono {i}: input={inp!r}", file=sys.stderr)
            print(f"  expected: ({want_out!r}, {want_count})", file=sys.stderr)
            print(f"  got     : ({got_out!r}, {got_count})", file=sys.stderr)
    total = len(cases) + len(mono_cases)
    if failures:
        print(f"\n{failures}/{total} cases failed", file=sys.stderr)
        return 1
    print(f"PASS: {total}/{total} self-test cases", file=sys.stderr)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="비-페르소나 색상 → 페르소나 토큰 일괄 정규화.",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="비-페르소나 색상 패턴이 포함된 라인만 출력 (변경 없음)",
    )
    parser.add_argument(
        "--self-test", action="store_true",
        help="합성 입력으로 단위 테스트 실행",
    )
    parser.add_argument(
        "--monochrome", action="store_true",
        help="다색 콘텐츠를 페르소나 단색 + 명도 단계로 강등 (MONOCHROME_MAP 추가 적용)",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    text = sys.stdin.read()
    if args.check:
        for lineno, line in check(text):
            print(f"{lineno}: {line}")
        print(f"\n총 {len(check(text))} 매칭", file=sys.stderr)
        return 0

    mode = "monochrome" if args.monochrome else "strict"
    out, count = normalize_palette(text, mode=mode)
    sys.stdout.write(out)
    print(f"치환 {count} 건 (mode={mode})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
