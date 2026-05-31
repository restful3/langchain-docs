## §6. 다음으로 가는 다리, 그리고 한 문장

<div class="section-summary">
  <div class="section-summary__kicker">한 줄 요약</div>
  <div class="section-summary__body">오늘은 LangGraph 의 <strong>사고법</strong>(노드·엣지·State)과 <strong>실행</strong>(<code>langgraph dev</code>)을 봤다. 다음은 이 사고법을 떠받치는 메커니즘의 깊이다.</div>
</div>

오늘 그린 것은 **지도** 다. 여기서 더 들어갈 길들:

- **Graph API 깊이** — `add_conditional_edges`, 리듀서(`add_messages`), 병렬 분기 등 노드/엣지의 본격 문법
- **Persistence · Memory** — checkpointer 의 실제 백엔드(Postgres·Redis), 스레드 간 장기 메모리(Store)와 시맨틱 검색
- **Streaming** — `values`/`updates`/`messages`/`custom` 스트림 모드로 실시간 진행 노출
- **Subgraphs** — 복잡한 다단계 작업을 하위 그래프로 캡슐화
- **Time Travel** — 과거 체크포인트로 돌아가 분기(fork) 실행

마지막으로, 발표가 끝났을 때 청중이 한 문장으로 답할 수 있어야 할 것:

<div class="callout--hero">
  <span class="callout__kicker">한 문장으로</span>
  <span class="callout__body">LangGraph 는 에이전트를 <strong>노드·엣지·State 의 그래프</strong> 로 모델링하는 런타임이다. 업무를 노드로 분해하고, raw State 로 잇고, 에러와 사람 개입을 흐름 안에서 다루며, <code>langgraph dev</code> 로 띄워 Studio 로 디버깅한다.</span>
</div>
