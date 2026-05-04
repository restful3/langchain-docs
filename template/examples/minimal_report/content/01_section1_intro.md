## 빌더 동작 확인

이 섹션은 `apply_visual_transforms` 의 주요 패턴이 정상 변환되는지 확인한다.

### 콜아웃과 표

본문에 hero callout · cmp-table · footnote 가 들어 있어야 한다 [^1].

**핵심 메시지**: 빌더는 마크다운 시각 패턴을 컴포넌트로 승격한다.

**실무 시사점 (검증용)**

- 핵심 메시지 콜아웃 변환
- 실무 시사점 박스 변환
- 표의 cmp-table 클래스 부여
- 각주의 외부 URL 링크 변환

**표 1. 빌더 동작 매트릭스**

| 패턴 | 입력 | 출력 컴포넌트 |
|---|---|---|
| 핵심 메시지 | `**핵심 메시지**: 본문` | `.callout--hero` |
| 실무 시사점 | `**실무 시사점**` + 다음 블록 | `.callout--insight` |
| 표 | 마크다운 표 | `<table class="cmp-table">` |

### 인라인 배지

위험도 [risk:low] · 난이도 [diff:mid] · 비용 [cost:high] 같은 토큰은 [`badge`](https://example.com) 클래스로 치환된다.

**더 깊이 읽기**

- [GitHub 저장소](https://github.com/example/repo)
- [공식 문서](https://example.com/docs)
