## §0. 들머리 — "LangGraph 위에 얹혀 있다" 의 그 LangGraph

<div class="section-summary">
  <div class="section-summary__kicker">한 줄 요약</div>
  <div class="section-summary__body">지난 스터디 내내 "깔개" 로만 불리던 LangGraph 를, 오늘 처음으로 직접 연다.</div>
</div>

DeepAgent 4주를 거치며 우리는 같은 문장을 반복해서 들었다 — *"Deep Agent 는 LangGraph 위에 얹혀 있다."* 계획 수립·파일시스템·서브에이전트·장기 메모리라는 4대 능력이 모두 LangGraph 라는 런타임 위에서 돈다는 뜻이었다. 그런데 정작 그 LangGraph 가 무엇인지는 블랙박스로 남겨 두었다.

이 발제는 그 블랙박스를 연다. LangGraph 는 LLM 으로 **상태를 유지하고(stateful) 여러 액터가 참여하는(multi-actor)** 복잡한 애플리케이션을 그래프 구조로 짜는 라이브러리다. 에이전트의 워크플로우를 **노드(node)** 와 **엣지(edge)**, 그리고 공유 **상태(state)** 로 모델링한다. (그 아래에서는 Pregel 계열의 런타임이 돌지만, 내부 실행 모델은 이 발제의 범위 밖이다.)

이 글이 다루는 다섯 주제는 다음과 같다.

**표 1. 이 교안이 다루는 다섯 핵심 주제**

| # | 주제 | 출처 문서 |
|:---:|---|---|
| 1 | 왜 그래프인가 — 사고 모델 | Thinking in LangGraph |
| 2 | 에이전트를 설계하는 5단계 | Thinking in LangGraph |
| 3 | State 설계 & 에러를 흐름의 일부로 | Thinking in LangGraph |
| 4 | 사람 개입과 내구성 | Thinking in LangGraph |
| 5 | 로컬에서 돌려보고, 생태계 근황 | Run a local server · Changelog |

§1\~§4 는 하나의 예제 — **평균회귀 트레이딩 에이전트** — 를 함께 따라간다. 공식 문서의 설계 흐름을 퀀트 사례로 옮겨, 추상적인 "노드와 엣지" 가 실제로 어떻게 살이 붙는지 한 사례로 관통해 보는 것이다.
