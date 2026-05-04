#!/usr/bin/env python3
"""SVG/Markdown 의 LG 브랜드 hex/CSS 변수를 AI Odyssey 외부판으로 일괄 치환.

사용:
    python svg_recolor.py < input.md > output.md
    python svg_recolor.py --check < input.md       # 매칭 라인만 출력 (변경 없음)
    python svg_recolor.py --self-test              # 합성 입력 단위 테스트

매핑 출처: DESIGN.lg-seminar.md → DESIGN.external.md.
적용 범위: 인라인 SVG fill/stroke, CSS 변수, rgba(), Tailwind/CSS hex.
"""
from __future__ import annotations

import argparse
import sys

# (LG 패턴, 외부판 치환) — 순서 의존: 더 긴 변수명을 짧은 것보다 먼저.
COLOR_MAP: list[tuple[str, str]] = [
    # ── 1. Primary brand (LG → Deep Navy) ──
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
    # CSS 변수명 — 긴 이름 먼저
    ("--lg-red-deep", "--brand-deep"),
    ("--lg-red-soft", "--brand-soft"),
    ("--lg-red", "--brand-primary"),

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


def recolor(text: str) -> tuple[str, int]:
    """Return (recolored_text, total_replacements)."""
    total = 0
    for old, new in COLOR_MAP:
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            total += count
    return text, total


def check(text: str) -> list[tuple[int, str]]:
    """Return [(lineno, line)] for lines containing any LG brand pattern."""
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
        ('var(--lg-red)', 'var(--brand-primary)', 1),
        ('var(--lg-red-soft)', 'var(--brand-soft)', 1),
        ('var(--lg-red-deep)', 'var(--brand-deep)', 1),
        ('rgba(165,0,52,0.08)', 'rgba(15,44,89,0.08)', 1),
        ('rgba(165, 0, 52, 0.08)', 'rgba(15, 44, 89, 0.08)', 1),
        ('rgba(228,0,43,0.10)', 'rgba(37,99,235,0.10)', 1),
        # 외부판 hex 는 변경 없음
        ('fill="#0F2C59"', 'fill="#0F2C59"', 0),
        # 다중 매칭
        ('a:#A50034 b:--lg-red-deep', 'a:#0F2C59 b:--brand-deep', 2),
        # 순서 함정 — --lg-red-soft 가 --lg-red 보다 먼저 매핑되는지
        ('--lg-red-soft + --lg-red', '--brand-soft + --brand-primary', 2),
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
    failures = 0
    for i, (inp, want_out, want_count) in enumerate(cases, start=1):
        got_out, got_count = recolor(inp)
        if got_out != want_out or got_count != want_count:
            failures += 1
            print(f"FAIL {i}: input={inp!r}", file=sys.stderr)
            print(f"  expected: ({want_out!r}, {want_count})", file=sys.stderr)
            print(f"  got     : ({got_out!r}, {got_count})", file=sys.stderr)
    total = len(cases)
    if failures:
        print(f"\n{failures}/{total} cases failed", file=sys.stderr)
        return 1
    print(f"PASS: {total}/{total} self-test cases", file=sys.stderr)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LG 브랜드 색상 → AI Odyssey 외부판 색상 일괄 치환.",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="LG 브랜드 패턴이 포함된 라인만 출력 (변경 없음)",
    )
    parser.add_argument(
        "--self-test", action="store_true",
        help="합성 입력으로 단위 테스트 실행",
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

    out, count = recolor(text)
    sys.stdout.write(out)
    print(f"치환 {count} 건", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
