# LangGraph 로 사고하기 — 노드·엣지·State, 그리고 실행

> 에이전트를 노드·엣지·State 의 그래프로 모델링하는 런타임 — 그 사고법과 실행을 한 번에

## Executive Summary

<div class="callout--hero">
  <span class="callout__kicker">핵심 메시지</span>
  <span class="callout__body">LangGraph 는 에이전트를 <strong>노드·엣지·State 의 그래프</strong> 로 모델링하는 런타임이다. 업무를 노드로 분해하고, raw State 로 잇고, 에러와 사람 개입을 흐름 안에서 다루며, <code>langgraph dev</code> 로 띄워 Studio 로 디버깅한다.</span>
</div>

이 교안은 LangGraph 공식 문서 세 편 — **Thinking in LangGraph**, **Run a local server**, **Changelog** — 을 하나로 합쳐 핵심 주제 다섯 가지로 다시 짠 것이다. 발표 전후로 혼자 읽어도 이해되도록, 슬라이드가 생략하는 맥락을 채우는 데 목적이 있다.

<div class="section-summary">
  <div class="section-summary__kicker">이 리포트가 답하는 것</div>
  <div class="section-summary__body">
    <ul>
      <li><strong>왜 그래프인가</strong> — 한 번의 LLM 호출로 부족한 순간, 그리고 노드·엣지·State 라는 세 부품.</li>
      <li><strong>어떻게 설계하나</strong> — 분해 → 스텝 유형 식별 → State → 노드 구현 → 연결의 5단계.</li>
      <li><strong>어떻게 멈추고 잇나</strong> — 에러 4전략과 <code>interrupt()</code>·checkpointer 로 사람 개입과 재개.</li>
      <li><strong>어떻게 띄우나</strong> — <code>langgraph dev</code> 로컬 서버, 그리고 v1 이후 생태계 근황.</li>
    </ul>
  </div>
</div>

§1\~§4 는 공식 문서가 끝까지 끌고 가는 하나의 예제 — **고객지원 이메일 에이전트** — 를 함께 따라간다. 추상적인 "노드와 엣지" 가 한 사례로 어떻게 살이 붙는지 관통해 본다.
