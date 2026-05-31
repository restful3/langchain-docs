# Closing 슬라이드 개선 리뷰

검토 대상:
- `template/theme_slides.css` 의 `.slide--closing`, `.closing-contact`, `.closing-qa*`, `.feature-card*` 규칙
- `langgraph/langgraph-04-06-taeyoung/content/slides.md` 의 closing 슬라이드 블록
- `/tmp/sl_closing2.png` 렌더 스크린샷

## Critical

없음.

## Major

없음. 이번 변경은 의도한 문제, 즉 요약문과 연락처 사이가 비어 보이고 Q&A 논의거리가 떠 보이던 문제를 충분히 해소했습니다.

## Minor

### 1. 위치: `slides.md` 181~185 / closing Q&A 카드 문구

**문제**  
Q&A 카드 3장은 슬라이드의 빈 공간을 잘 채우고, 청중에게 "이제 토론으로 넘어간다"는 행동 신호를 줍니다. 다만 Q2 문장 `interrupt() 는 어디에 둘까 — 비멱등 호출(발송·결제) 앞?`은 의미는 명확하지만 한국어 문장으로는 살짝 덜 다듬어진 느낌입니다. 발표자가 구두로 풀면 문제 없지만, closing 슬라이드는 마지막 인상이라 문장 완성도가 중요합니다.

**권장 수정**  
Q2를 다음 중 하나로 다듬는 것을 권합니다.

- `내 에이전트에서 interrupt() 는 어디에 둘까 — 발송·결제 같은 비멱등 호출 앞에?`
- `발송·결제 같은 비멱등 호출 앞에서 interrupt() 를 걸어야 하는 지점은 어디인가?`

현재 카드 폭에서는 첫 번째가 더 잘 맞습니다.

### 2. 위치: `theme_slides.css` 1502~1518 / `.closing-qa`, `.closing-qa__card`

**문제**  
Q&A 카드와 하단 `closing-contact` 3단 정보가 모두 3열 구조라 일관성은 좋습니다. 스크린샷 기준으로는 "카드 2겹"처럼 과해 보이지 않습니다. 하단 contact 는 카드가 아니라 얇은 구분선 아래 텍스트 블록이라 위계가 분리됩니다. 다만 `.closing-qa` 의 카드 그림자가 `box-shadow: 0 4px 16px rgba(15, 44, 89, 0.06)`으로 매우 은은해서, 밝은 배경에서는 세련되지만 프로젝터 환경에서는 카드 경계가 조금 약해질 수 있습니다.

**권장 수정**  
현재도 충분히 안정적입니다. 대형 스크린/프로젝터 대비를 조금 올리고 싶다면 shadow 보다 border 를 살짝 강화하는 편이 덱의 차분한 톤과 맞습니다.

```css
.closing-qa__card {
  border-color: rgba(15, 44, 89, 0.10);
  box-shadow: 0 6px 18px rgba(15, 44, 89, 0.07);
}
```

필수 수정은 아닙니다.

### 3. 위치: `theme_slides.css` 1502~1536 / closing 전용 컴포넌트 범위

**문제**  
`.closing-qa`, `.closing-qa__card`는 이름상 충분히 좁지만, 현재 선택자는 `.slide--closing` 아래로 스코프되지 않았습니다. 실제 충돌 가능성은 낮습니다. 그래도 템플릿 공용 CSS에 들어가는 컴포넌트라면, 다른 슬라이드에서 같은 클래스명을 실수로 쓰거나 향후 closing 외부에서 재사용할 때 스타일이 예상보다 넓게 적용될 수 있습니다.

**권장 수정**  
공용 템플릿 안정성을 더 높이려면 선택자를 closing 내부로 한정하세요.

```css
.slide--closing .closing-qa { ... }
.slide--closing .closing-qa__card { ... }
.slide--closing .closing-qa__card::before { ... }
```

현재 파일의 다른 컴포넌트들은 전역 클래스 방식도 쓰고 있으므로, 팀 스타일상 전역 컴포넌트로 둘 수도 있습니다.

## Nit

### 4. 위치: `theme_slides.css` 1524~1528 / `.closing-qa__q`

**문제**  
`letter-spacing: 0.12em`은 Q1/Q2에는 또렷하게 보이지만, `Q3 · 트레이드오프`처럼 긴 한글+영문 혼합 라벨에서는 약간 벌어져 보입니다. 스크린샷에서도 Q3 태그가 카드 제목이라기보다 작은 헤드라인처럼 느껴집니다.

**권장 수정**  
`0.08em~0.10em` 정도로 낮추면 세 카드의 라벨 밀도가 더 균일해집니다.

### 5. 위치: `theme_slides.css` 1474~1477 / `.closing-sub`

**문제**  
closing-sub가 두 줄로 잘 감기고 오버플로우는 없습니다. 다만 첫 줄이 길고 두 번째 줄이 짧아, 대형 H1 아래에서 약간 산문처럼 보입니다. 현재도 발표용으로 문제는 없지만, 마지막 메시지의 타격감을 더 주려면 요약문을 조금 줄일 여지가 있습니다.

**권장 수정**  
예를 들어 다음처럼 1.5줄 이내로 압축할 수 있습니다.

`LangGraph = 노드·엣지·State 로 에이전트를 분해하고, raw State·에러·사람 개입을 실행 흐름에 담는 그래프 런타임.`

단, `langgraph dev`까지 closing에서 다시 언급하려는 의도라면 현재 문장 유지가 맞습니다.

## 전반 평가

개선 후 closing 슬라이드는 충분히 정돈되고 세련됐습니다. Q&A 카드 3개가 비어 있던 중앙 영역을 채우면서도 하단 contact 3단과 시각적으로 충돌하지 않고, feature-card 계열의 surface 카드·상단 액센트 바·은은한 그림자를 closing 맥락에 맞게 낮은 밀도로 잘 가져왔습니다. 1280×720 스크린샷 기준으로 오버플로우나 답답함은 없고, slide-body flex 구조와 `.closing-contact { margin-top:auto; }`도 의도대로 작동합니다. 추가 개선은 필수라기보다 마감 품질 영역입니다. 우선순위는 Q2 문장 다듬기, 필요 시 카드 경계 대비 소폭 강화, 공용 CSS 스코프를 `.slide--closing`으로 좁히는 정도입니다.
