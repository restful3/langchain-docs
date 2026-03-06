# Part 3: 첫 번째 Agent 만들기 리뷰 - 태영

> 작성일: 2026-03-06

## 리뷰 범위

- [x] 교안: `docs/part03_first_agent.md`
- [x] 예제 코드: `src/part03_first_agent/`

---

## 문서 갈무리 (전체 요약)

### 문서 개요

Part 3는 Part 2에서 학습한 Chat Models, Messages, Tools를 결합하여 **첫 번째 동작하는 Agent** 를 만드는 교안이다. `create_agent()` API 사용법부터 시작하여 ReAct 패턴, System Prompt 커스터마이징, Streaming까지 Agent 개발의 핵심 기술을 단계적으로 다룬다.

- 분량: 2,034줄
- 난이도 표기: ⭐⭐☆☆☆ (초급)
- 대응 소스 코드: 3개 파일, 총 1,301줄
- 실습 과제: 3개 (계산기 Agent, 여행 플래너 Agent, 멀티 에이전트 대화)
- 학습 시간: 3\~4시간

### 섹션별 핵심 내용 요약

**섹션 1. create_agent() 기본** (L73\~L259)
- Agent의 정의(Model + Tools + Execution Loop)를 복습하고, `bind_tools()` vs `create_agent()` 비교표로 Part 2에서의 전환점을 명확히 제시한다.
- `create_agent()` API의 4가지 파라미터(model, tools, system_prompt, checkpointer)를 설명하고, Agent 실행 루프(LangGraph 자동 관리)를 Mermaid 다이어그램으로 시각화한다.
- 첫 Agent를 만들어 `invoke()`로 실행하고, 중간 메시지를 관찰하는 실습을 안내한다.

**섹션 2. 날씨 Agent 구현** (L261\~L490)
- 날씨 도구(`get_weather_for_location`, `get_user_location`)를 정의하고 `ToolRuntime[Context]`를 활용한 컨텍스트 주입 패턴을 소개한다.
- 구조화된 응답(`ResponseFormat`)과 유머 있는 System Prompt로 실전 Agent를 구현한다.
- Agent의 실행 과정을 단계별로 추적하며 ReAct 사이클을 체감시킨다.

**섹션 3. ReAct 패턴** (L493\~L729)
- ReAct(Reasoning + Acting) 패턴의 4단계 순환 구조(추론 → 행동 → 관찰 → 반복/종료)를 체계적으로 설명한다.
- Reasoning(상황 분석, 목표 확인, 전략 수립), Acting(도구 호출 유형), Observation(결과 해석, 상태 업데이트)을 각각 코드와 출력 예시로 보여준다.
- 순차적 도구 호출(검색 → 재고 확인)과 병렬 도구 호출(여러 도시 날씨 동시 조회)의 차이를 실습한다.

**섹션 4. System Prompt 커스터마이징** (L739\~L1001)
- 좋은 System Prompt 작성의 5가지 팁(명확성, 도구 사용 지침, Few-shot, 응답 형식, 에러 처리)을 제시한다.
- 역할(Role) 정의를 통한 페르소나 설정(선생님, 과학자, 코미디언)과 도메인별 제약사항(의료 Agent) 예제를 다룬다.

**섹션 5. Streaming Agent** (L1005\~L1589)
- Streaming의 개념과 UX 효과를 설명하고, `invoke()` vs `stream()` 비교로 동기/비동기 차이를 체감시킨다.
- 3가지 stream_mode(values, updates, messages)의 용도와 트레이드오프를 비교한다.
- `astream_events()` 비동기 이벤트 스트리밍의 사용법을 소개한다.
- **섹션 5.5** (L1256\~L1589): Content Blocks 구조, Thinking Blocks(Claude), Reasoning Tokens(GPT-4o), Thought Blocks(Gemini 2.5)를 약 330줄에 걸쳐 상세히 다룬다. Caching, 모델별 지원 현황, 주의사항, 실전 예제까지 포함한다.

### 소스 코드 매핑

| 소스 파일 | 라인 수 | 대응 교안 섹션 |
|-----------|------:|-------------|
| `01_basic_agent.py` | 420 | 섹션 1 (create_agent 기본), 섹션 4 (System Prompt) |
| `02_react_agent.py` | 476 | 섹션 2 (날씨 Agent), 섹션 3 (ReAct 패턴) |
| `03_streaming_agent.py` | 405 | 섹션 5 (Streaming, 5.1\~5.4만) |
| solutions/ (3개 파일) | 786 | 실습 과제 해답 |
| **합계** | **2,087** | |

> 참고: 섹션 5.5(Content Blocks/Thinking Blocks)에 대응하는 소스 파일이 없다.

### 학습 흐름 분석

전체적으로 **Top-down** 접근을 취한다: 먼저 Agent를 만들어 실행해보고(섹션 1), 실전 예제로 확장한 뒤(섹션 2), 내부 동작 원리를 이해하고(섹션 3), 커스터마이징(섹션 4)과 UX 개선(섹션 5)으로 나아가는 구조이다.

```text
create_agent() 기본 ─→ 날씨 Agent 구현 ─→ ReAct 패턴 이해 ─→ System Prompt ─→ Streaming
   (만들기)              (확장)             (원리)              (커스터마이징)     (UX)
```

Part 2의 Bottom-up 접근(구성 요소 개별 학습)에서 Part 3의 Top-down 접근(먼저 만들고 이해)으로 전환되는 흐름이 효과적이다. 다만 섹션 5.5에서 Content Blocks/Thinking Blocks라는 새로운 심화 주제가 등장하여 학습 흐름이 끊기는 구간이 존재한다.

---

## 교안 피드백 (`docs/part03_first_agent.md`)

### 오류/수정

- [ ] L4: 난이도 ⭐⭐☆☆☆(초급) 표기이나, 섹션 5.5(Content Blocks/Thinking Blocks)는 모델별 reasoning API, caching 전략 등 ⭐⭐⭐⭐ 수준의 내용을 포함함 -> 전체 난이도를 ⭐⭐⭐☆☆(초중급)으로 상향하거나, 섹션 5.5에 "(심화)" 표시를 명시적으로 추가
- [ ] L361: Anthropic 모델명 `claude-sonnet-4-5-20250929` -> 실제 Anthropic 모델 ID 형식은 `claude-sonnet-4-5-20250514` 등. 정확한 모델 ID로 수정하거나, 날짜 부분 없이 `claude-sonnet-4-5` 형태로 기재
- [ ] L1286\~L1298: `response.content_blocks` 속성 사용 -> LangChain의 `ChatAnthropic` 래퍼를 통해 호출할 경우 반환되는 `AIMessage` 객체에서 `content_blocks`에 직접 접근하는 방식이 올바른지 확인 필요. LangChain 래퍼에서는 `response.content`가 리스트 형태로 블록을 반환할 수 있음
- [ ] L1445/L1450: "GPT-4o"를 Reasoning 지원 모델로 기재 -> 실제 OpenAI의 reasoning 모델은 `o1`, `o3-mini` 등 별도 모델 라인업. GPT-4o 자체는 reasoning tokens를 생성하지 않음 -> 모델명을 `o1` 또는 `o3-mini`로 수정
- [ ] L1436: Gemini 2.5의 `think_mode=True` 파라미터 -> 텍스트로만 언급되고 실제 코드 예제가 없음. Claude의 `extended_thinking=True`와 마찬가지로 간단한 코드 예제를 추가하거나, 지원 여부가 불확실하면 삭제

### 개선 제안

- [ ] 섹션 5.5 (Content Blocks/Thinking, L1256\~L1589, ~330줄): "첫 번째 Agent 만들기"라는 Part 3의 핵심 주제와 거리가 있는 심화 내용. Agent Streaming을 다루다가 갑자기 모델별 Reasoning 내부 구조로 전환됨. 별도 파트(예: Part 5 미들웨어 또는 부록)로 이관하거나, 최소한 "(선택) 심화 학습" 표시를 추가하여 초급 학습자가 건너뛸 수 있도록 안내
- [ ] 섹션 4 -> 5 전환부 (L1001\~L1005): 섹션 4(System Prompt)에서 섹션 5(Streaming)로의 전환 문구가 없음. "Agent의 성격을 설정하는 방법을 배웠으니, 이제 Agent의 응답을 실시간으로 전달하는 Streaming을 알아보겠습니다" 정도의 브릿지 문장을 추가하면 흐름이 자연스러워질 것
- [ ] L2013\~L2029 ("다음 단계"): Part 4(Memory)로의 전환에서 메모리 필요성의 동기 부여가 약함. "현재 Agent는 대화를 기억하지 못합니다. 사용자가 '아까 물어본 서울 날씨 다시 알려줘'라고 하면 이전 대화를 참조할 수 없습니다" 같은 한계 체감 문구를 추가 제안
- [ ] L3: 학습 시간 "약 3\~4시간" -> 섹션 5.5의 심화 내용(~330줄)까지 포함하면 4\~5시간이 더 현실적. 섹션 5.5를 분리하지 않을 경우 학습 시간 상향 검토
- [ ] 전반: `create_agent()`의 `max_iterations` 파라미터 사용 예제가 FAQ(L1842\~L1875)에만 등장. 섹션 1 또는 2 본문에서 무한 루프 방지를 위한 기본 설정으로 소개하면 학습자가 실습 중 문제를 예방할 수 있음

---

## 예제 코드 피드백 (`src/part03_first_agent/`)

### 오류/수정

- [ ] `01_basic_agent.py` L76: `eval(expression)` 사용 -> 주석에 "보안 주의: 실제 프로덕션에서는 eval 사용 금지!"라고 경고하고 있으나, 학습자가 이 패턴을 그대로 복사할 위험이 있음. `ast.literal_eval()` 또는 `simpleeval` 라이브러리 등 안전한 대안으로 교체하거나, 최소한 `# WARNING` 수준의 강조 주석으로 변경
- [ ] `02_react_agent.py` L111\~L128: `get_weather()` 도구가 `example_2_single_tool_call()` 함수 내부에 로컬로 정의됨. 이 패턴 자체는 문제없으나, 예제 6(`example_6_parallel_tool_calls`, L366\~L378)에서도 동일한 이름의 `get_weather()` 도구가 로컬로 재정의됨 -> 학습자에게 "왜 같은 이름의 도구를 두 번 정의하는지" 혼란을 줄 수 있음. 함수 내부 주석으로 "이 예제에서는 독립적인 도구를 사용합니다" 정도의 안내 추가

### 개선 제안

- [ ] 섹션 5.5(Content Blocks/Thinking Blocks)에 대응하는 소스 파일이 없음. 교안에서 ~330줄에 걸쳐 상세히 다루는 내용인데, 학습자가 직접 실행해볼 수 있는 코드가 부재함 -> `03_streaming_agent.py`에 `example_6_thinking_blocks()` 함수를 추가하거나, 별도의 `04_thinking_blocks.py` 파일 생성 검토
- [ ] `03_streaming_agent.py`: 교안 L1219에서 `astream_events()` 비동기 이벤트 스트리밍을 코드 블록으로 소개하지만, 소스 파일에는 이에 대응하는 예제가 없음. 심화 보너스 예제로 추가 검토
- [ ] 전체: solutions/ 파일 3개가 모두 자기 완결적(self-contained)으로 잘 작성되어 있음. 다만 `exercise_03.py`에서 `make_final_decision()` 함수(L140\~L177)가 두 Agent의 응답을 단순 문자열 비교하는데, 실제로는 LLM을 활용한 종합 판단이 더 교육적일 수 있음

---

## 기타 의견 (리뷰어 종합 소견)

### 강점

1. **bind_tools() vs create_agent() 비교표** (L45\~L53): Part 2에서 Part 3로의 핵심 전환점을 한눈에 보여주는 효과적인 비교. 학습자가 "왜 Agent가 필요한지"를 즉시 이해할 수 있다.
2. **ReAct 패턴의 체계적 설명** (섹션 3): Reasoning, Acting, Observation을 각각 분리하여 설명한 뒤 실전 예제(무선 헤드폰 검색)에서 통합하는 구성이 교육적으로 우수하다.
3. **소스 파일 3개로 정리된 깔끔한 매핑**: 이전의 5개 파일에서 3개로 통합된 후, 교안 섹션과 소스 파일의 대응이 명확해졌다 (01=섹션1+4, 02=섹션2+3, 03=섹션5).
4. **Streaming 3가지 모드의 실용적 비교** (섹션 5.3): values/updates/messages 모드를 동일한 질문으로 비교하고, 각 모드의 용도(디버깅/네트워크 최적화/UI)를 명시한 것이 실무에 직접 적용 가능하다.
5. **실습 과제의 난이도 progression**: 계산기(⭐⭐) -> 여행 플래너(⭐⭐⭐) -> 멀티 에이전트(⭐⭐⭐⭐)로 자연스럽게 상승하며, 각 과제가 교안의 핵심 개념을 하나씩 심화한다.

### 구조적 제안

1. **섹션 5.5 분리 검토**: Content Blocks/Thinking Blocks(~330줄)는 "첫 번째 Agent 만들기"의 범위를 벗어나는 심화 주제이다. Streaming 자체(5.1\~5.4)는 Agent UX와 직결되지만, 모델별 Reasoning 내부 구조는 별도 파트가 적합하다. 분리하면 Part 3의 분량이 ~1,700줄로 줄어들어 "3\~4시간" 학습 시간에 부합하게 된다.
2. **섹션 순서 조정 고려**: 현재 1(기본) -> 2(날씨 Agent) -> 3(ReAct) -> 4(System Prompt) -> 5(Streaming) 순서에서, 섹션 4(System Prompt)는 난이도가 낮고(⭐⭐) 섹션 3(ReAct)은 중간(⭐⭐⭐)이다. 1 -> 2 -> 4 -> 3 -> 5 순서로 재배치하면 난이도 상승이 더 완만해질 수 있다. 다만 현재 순서도 "만들기 -> 확장 -> 원리 -> 커스터마이징 -> UX"라는 논리적 흐름이 있으므로 유지해도 무방하다.
3. **섹션간 전환 문구 보강**: 섹션 4에서 5로의 전환이 특히 갑작스럽다. 각 섹션 끝에 1\~2줄의 전환 안내 문구를 두면 학습 흐름이 자연스러워진다.

### 난이도 평가

교안의 표기 난이도는 ⭐⭐☆☆☆(초급)이나, 실제 내용의 난이도 분포는 다음과 같이 편차가 크다:

| 섹션 | 체감 난이도 | 비고 |
|------|-----------|------|
| 1 (create_agent 기본) | ⭐⭐☆☆☆ | 초급에 적합, API 사용법 위주 |
| 2 (날씨 Agent) | ⭐⭐⭐☆☆ | ToolRuntime, 구조화된 응답 등장 |
| 3 (ReAct 패턴) | ⭐⭐⭐☆☆ | 개념 이해 + 순차/병렬 패턴 |
| 4 (System Prompt) | ⭐⭐☆☆☆ | 초급에 적합, 텍스트 작성 위주 |
| 5.1\~5.4 (Streaming) | ⭐⭐⭐☆☆ | 3가지 모드 비교, 비동기 개념 |
| 5.5 (Content Blocks/Thinking) | ⭐⭐⭐⭐☆ | 모델별 reasoning API, caching 전략 |

섹션 5.5의 난이도가 특히 높아, 교안 전체를 "초급"으로 표기하기에는 무리가 있다. 전체 난이도를 ⭐⭐⭐☆☆(초중급)으로 상향하거나, 섹션 5.5를 분리/선택사항으로 표기하는 것을 제안한다.

### Part 2 -> 3 -> 4 연결성

- **Part 2 -> 3**: Part 2의 섹션 6에서 `bind_tools()` + 수동 실행 루프를 가르친 뒤, Part 3에서 `create_agent()`로 이를 자동화하는 흐름이다. Part 3 개요(L25)에서 "Part 2에서 Chat Models, Messages, Tools를 학습했습니다. 이제 이 모든 것을 결합하여"라고 명시적으로 연결하고 있으며, 비교표(L45\~L53)가 전환점을 효과적으로 보여준다. 연결성이 우수하다.
- **Part 3 -> 4**: "다음 단계" 섹션(L2013\~L2029)에서 Part 4의 학습 내용(Short-term Memory, 체크포인터, 멀티턴 대화 등)을 나열하고 있다. 다만 Part 3 본문에서 "Agent가 이전 대화를 기억하지 못하는 한계"를 학습자에게 체감시키는 예제가 없다. 예를 들어 섹션 1이나 2에서 동일 Agent에게 연속 질문을 하고 "이전 답변을 기억하지 못함"을 관찰하는 간단한 시연이 있으면, Part 4(Memory)로의 전환 동기가 강화될 것이다.
