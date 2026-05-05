"""단일 섹션 빌더 — template/ 의 정식 플래그를 사용한 한 줄 wrapper.

template/build_report.py 가 다음 플래그를 기본 지원:
  --single-section   : --no-cover --no-toc --continuous --show-divider 메타 플래그
  --inline-svgs      : 외부 figs/*.svg 참조를 인라인 <svg> 로 치환 (Syncthing 안전)
  --monochrome       : SVG/배경 색상을 brand 단색 + 명도 단계로 강등

산출:
    content/01_textbook.html
    content/01_textbook.pdf

사용:
    python content/build.py             # HTML + PDF
    python content/build.py --html-only # PDF 스킵
    python content/build.py --no-monochrome  # 원본 다색 SVG 유지
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent       # .../week1-overview-taeyoung/content/
PROJECT_ROOT = HERE.parents[2]               # .../langchain-docs/


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html-only", action="store_true", help="PDF 단계 스킵")
    ap.add_argument(
        "--no-monochrome", action="store_true",
        help="원본 다색 SVG 유지 (기본은 brand 단색 강등)",
    )
    args = ap.parse_args()

    cmd = [
        sys.executable, "-m", "template", "build", "report", str(HERE),
        "--single-section",
        "--inline-svgs",
        "--tier", "1",
        "--sections", "01",
        "--out", str(HERE),
        "--name", "01_textbook",
        "--doc-title", "Deep Agents 첫 걸음 — Overview",
    ]
    if not args.no_monochrome:
        cmd.append("--monochrome")
    if args.html_only:
        cmd.append("--html-only")

    print(f"$ {' '.join(cmd)}")
    sys.exit(subprocess.call(cmd, cwd=str(PROJECT_ROOT)))


if __name__ == "__main__":
    main()
