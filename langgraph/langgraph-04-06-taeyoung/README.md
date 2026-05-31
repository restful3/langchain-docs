# LangGraph 04~06 발표 — 노드·엣지·State 로 사고하기

**발표자**: 태영
**주제**: Thinking in LangGraph · Run a local server · Changelog (20분, 이론 발제)
**한 줄 요약**: LangGraph 는 에이전트를 *노드·엣지·State 의 그래프* 로 모델링하는 런타임이다. 업무를 노드로 분해하고, raw State 로 잇고, 에러와 사람 개입을 흐름 안에서 다루며, `langgraph dev` 로 띄워 Studio 로 디버깅한다.

DeepAgent 스터디 내내 "그 위에 얹혀 있다" 던 LangGraph 자체를 처음으로 직접 여는 발제. 공식 문서 04~06 세 편을 합쳐 **핵심 주제 5개** 로 다시 짰다.

---

## 산출물

| 산출물 | 파일 | 상태 |
| --- | --- | --- |
| 상세 교과서 (소스) | [content/01_textbook.md](content/01_textbook.md) | ✅ 완료 (이번 단계 집중) |
| 교과서 HTML 미리보기 | [content/textbook.html](content/textbook.html) | ✅ 빌드 검증됨 |
| 디자인·설계 | [archives/meta/DESIGN.md](archives/meta/DESIGN.md) | ✅ |
| 브레인스토밍 | [archives/meta/BRAINSTORM.md](archives/meta/BRAINSTORM.md) | ✅ |
| 진행 추적 | [archives/meta/STATUS.md](archives/meta/STATUS.md) | ✅ |
| 시각자료 SVG | content/figs/ (9개) | ✅ 완료 (Chrome 렌더 검증) |
| 실행 스크립트 | scripts/ | ⬜ 후속 (이메일 에이전트 예제) |
| 슬라이드 (소스) | [content/slides.md](content/slides.md) | ✅ 19장 |
| 슬라이드 HTML | [content/slides.html](content/slides.html) | ✅ 빌드 검증됨 |
| **로컬 사이트 (self-contained)** | [site/index.html](site/index.html) | ✅ index + report + slides, file:// 바로 열림 |

## 로컬에서 바로 보기

```bash
xdg-open langgraph/langgraph-04-06-taeyoung/site/index.html   # 서버 불필요
# 재생성: python langgraph/langgraph-04-06-taeyoung/build_local.py  (repo 루트에서)
```

`site/` 의 HTML 은 그림(SVG)·deck.js·CSS 를 모두 인라인한 자족형이라 어디서 열어도(VS Code 프리뷰·file://) 렌더된다.

### ToriBoard / iPhone 모바일 검증

2026-05-30에 ToriBoard Sites 표시용 모바일 CSS를 보정했다. `site/` HTML을 다시 생성하거나 교체하면 아래 3개 페이지를 최소 390×844 폭에서 확인한다.

- `site/index.html`
- `site/report.html`
- `site/slides.html`

카드 제목이 1~2글자 단위로 접히거나, 버튼이 본문 폭을 잡아먹거나, 슬라이드 네비게이션이 safe-area와 겹치면 실패로 본다. 상세 기록: `docs/2026-05-30-toriboard-mobile-css.md`.
| 교과서 PDF | content/textbook.pdf | ⬜ 후속 (chromedriver 설치 후) |

---

## 핵심 주제 5개 (04~06 통합)

§1~§4 는 **고객지원 이메일 에이전트** 하나의 예제로 관통한다.

1. **왜 그래프인가** — 노드(작업)·엣지(다음 결정)·State(공유 메모리) — `06`
2. **에이전트 설계 5단계** — 분해 → 스텝 유형 → State → 노드 → 연결 — `06`
3. **State 설계 & 에러** — raw 저장 원칙 + 4가지 에러 전략 — `06`
4. **사람 개입과 내구성** — `interrupt()`·`Command(resume)`·checkpointer — `06`
5. **로컬 실행 & 근황** — `langgraph dev`·Studio·SDK/REST + changelog v1 — `04`+`05`

---

## 원문 매핑

| 절 | 원문 (langgraph/) |
| --- | --- |
| §1~§4 | `06-thinking-in-langgraph.md` |
| §5.1 | `04-local-server.md` |
| §5.2 | `05-changelog.md` |

---

## 폴더 구조

```text
langgraph-04-06-taeyoung/
├── README.md
├── content/
│   ├── 01_textbook.md       ★ 상세 교과서
│   ├── sections.yaml         빌드용 섹션 라벨 매핑
│   └── figs/                 (후속) SVG
├── scripts/                  (후속) 실행 예제
└── archives/meta/
    ├── BRAINSTORM.md
    ├── DESIGN.md
    └── STATUS.md
```

---

## PDF 재빌드 (후속)

`template` 듀얼 빌더로 교과서를 A4 PDF 로 낼 수 있다. chromedriver 설치 후:

```bash
cd /home/restful3/workspace/langchain-docs
# HTML 만 (chromedriver 불필요)
python -m template build report langgraph/langgraph-04-06-taeyoung/content/ --html-only
# PDF 까지 (Chrome + chromedriver 필요)
python -m template build report langgraph/langgraph-04-06-taeyoung/content/
```
