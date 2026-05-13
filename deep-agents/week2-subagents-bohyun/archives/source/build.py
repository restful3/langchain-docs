"""2주차 산출물 빌더.

사용:
    python archives/source/build.py
    python archives/source/build.py --html-only
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEEK_ROOT = HERE.parents[1]
OUT_DIR = WEEK_ROOT / "content"
PROJECT_ROOT = HERE.parents[3]


def run(cmd: list[str]) -> int:
    display = " ".join(
        str(part).encode("ascii", "backslashreplace").decode("ascii") for part in cmd
    )
    print(f"$ {display}")
    return subprocess.call(cmd, cwd=str(PROJECT_ROOT))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html-only", action="store_true")
    ap.add_argument("--no-monochrome", action="store_true")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    report_cmd = [
        sys.executable,
        "-m",
        "template",
        "build",
        "report",
        str(HERE),
        "--single-section",
        "--inline-svgs",
        "--tier",
        "1",
        "--sections",
        "01",
        "--out",
        str(OUT_DIR),
        "--name",
        "textbook",
        "--doc-title",
        "Subagents & Human-in-the-loop",
        "--author",
        "보현",
    ]
    slides_cmd = [
        sys.executable,
        "-m",
        "template",
        "build",
        "slides",
        str(HERE / "slides.md"),
        "--out",
        str(OUT_DIR),
    ]
    if not args.no_monochrome:
        report_cmd.append("--monochrome")
        slides_cmd.append("--monochrome")
    if args.html_only:
        report_cmd.append("--html-only")
        slides_cmd.append("--html-only")

    code = run(report_cmd)
    if code:
        sys.exit(code)
    sys.exit(run(slides_cmd))


if __name__ == "__main__":
    main()
