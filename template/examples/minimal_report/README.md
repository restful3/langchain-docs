# Minimal report sample

`build_report.py` 가 정상 동작하는지 검증하기 위한 1-섹션 리포트 샘플.

## 실행

패키지 폴더가 `templates/ai_odyssey_publisher/` 에 있다고 가정:

```bash
cd templates
python -m ai_odyssey_publisher.build_report \
    ai_odyssey_publisher/examples/minimal_report/content/ \
    --tier 1 --html-only \
    --title "미니멀 샘플 리포트" \
    --version-badge "demo · 2026-04-30"
```

출력: `examples/minimal_report/detailed_report_external.html`. 브라우저로 열어 다음을 확인:

- 커버에 "AI Odyssey · External Publishing" 워드마크
- 섹션 디바이더 "섹션 01 · 빌더 동작 확인"
- 핵심 메시지 콜아웃 (Deep Navy)
- 실무 시사점 박스
- 표가 cmp-table 스타일 (캡션 · 칩 포함)
- 본문 `[^1]` 이 외부 URL 로 점프

전체 PDF 까지 검증하려면 `--tier all` (Chrome/chromedriver 필요).
