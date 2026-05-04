"""`python -m template build {report|slides} ...` 단일 진입점.

용례:
    python -m template build report content/                     # 리포트 빌드
    python -m template build slides content/slides.md            # 슬라이드 빌드
    python -m template build report content/ --sections 02       # 부분 빌드
    python -m template                                           # 도움말

레거시 호출 (`python -m template.build_report ...`) 도 그대로 동작.
"""
from __future__ import annotations

import sys


_HELP = """usage: python -m template <command> ...

commands:
  build report <content_dir>     Markdown 폴더 → A4 리포트 HTML/PDF
  build slides <slides.md|dir>   Markdown → 1280×720 슬라이드 HTML/PDF

각 빌더의 옵션은 다음으로 확인:
  python -m template build report --help
  python -m template build slides --help
"""


def _dispatch(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help", "help"):
        print(_HELP)
        return 0

    if argv[1] != "build":
        print(f"❌ 알 수 없는 명령어: {argv[1]}", file=sys.stderr)
        print(_HELP, file=sys.stderr)
        return 2

    if len(argv) < 3:
        print("❌ build 의 대상 (report|slides) 미지정.", file=sys.stderr)
        print(_HELP, file=sys.stderr)
        return 2

    target = argv[2]
    if target == "report":
        from .build_report import main as report_main
        sys.argv = [argv[0]] + argv[3:]
        report_main()
        return 0
    if target == "slides":
        from .build_slides import main as slides_main
        sys.argv = [argv[0]] + argv[3:]
        slides_main()
        return 0

    print(f"❌ 알 수 없는 build 대상: {target}", file=sys.stderr)
    print(_HELP, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(_dispatch(sys.argv))
