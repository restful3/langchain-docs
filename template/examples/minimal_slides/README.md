# Minimal slides sample

`build_slides.py` 가 정상 동작하는지 검증하기 위한 5-슬라이드 샘플 (cover + section + content + content + closing).

## 실행

```bash
cd templates
python -m ai_odyssey_publisher.build_slides \
    ai_odyssey_publisher/examples/minimal_slides/content/slides.md \
    --html-only
```

출력: `examples/minimal_slides/content/slides.html`. 브라우저로 열어 다음을 확인:

- **Cover** 슬라이드 — "AI Odyssey · External Publishing" 워드마크 + "YouTube · @AI_odysseys" 시그니처
- **Section divider** — `섹션 01.<br>빌더 검증` + 부제 + 큰 번호 `01`
- **Content** 슬라이드 — `slide-section-tag` "Section 01 · Hook" 표시
- 표가 `cmp-table` 스타일
- 리스트가 `bullets` 클래스
- **Closing** 슬라이드 — "감사합니다" + 한 줄 인용

전체 PDF (1280×720 16:9) 까지 검증하려면 `--html-only` 제거 (Chrome/chromedriver 필요).
