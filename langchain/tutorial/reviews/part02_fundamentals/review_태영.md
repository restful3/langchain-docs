# Part 2: LangChain 핵심 구성 요소 리뷰 - 태영

> 작성일: 2026-02-27

## 리뷰 범위

- [x] 교안: `docs/part02_fundamentals.md`
- [x] 예제 코드: `src/part02_fundamentals/`

---

## 문서 갈무리 (전체 요약)

### 문서 개요

Part 2는 LangChain Agent의 세 가지 핵심 구성 요소인 **Chat Models**, **Messages**, **Tools** 를 다루는 기초 교안이다. Part 1에서 소개한 개념적 이해를 실제 코드 레벨로 확장하며, Part 3(첫 번째 Agent 만들기)에서 본격적으로 Agent를 구축하기 위한 전제 지식을 제공한다.

- 분량: 2,233줄 (전체 교안 중 최대)
- 난이도 표기: ⭐⭐☆☆☆ (초급)
- 대응 소스 코드: 5개 파일, 총 2,316줄
- 실습 과제: 3개 (다중 프로바이더, 대화 기록 관리, 실용적 Tool 만들기)

### 섹션별 핵심 내용 요약

**섹션 1. Chat Models 이해하기** (L43~L434)
- `init_chat_model()` 통합 API를 통해 OpenAI, Anthropic, Google, Azure 등 다양한 프로바이더를 동일한 인터페이스로 사용하는 방법을 설명한다.
- Temperature와 주요 파라미터(max_tokens, timeout, max_retries)를 다루고, Beta 기능인 Model Profiles를 통한 모델 능력 탐지(context window, multimodal, tool calling 지원 여부)까지 소개한다.

**섹션 2. Messages 다루기** (L436~L1020)
- SystemMessage, HumanMessage, AIMessage, ToolMessage 4가지 메시지 타입의 역할과 속성을 설명한다.
- Dictionary 포맷과 객체 포맷 간 변환 방법을 다루고, Multimodal Content Handling(이미지, PDF, 오디오, 비디오)을 약 200줄에 걸쳐 상세히 다룬다.

**섹션 3. Tools 기초** (L1022~L1178)
- `@tool` 데코레이터로 도구를 정의하는 기본 방법, Docstring이 LLM의 도구 선택에 미치는 영향, Type Hints가 스키마 자동 생성에 어떻게 활용되는지를 설명한다.

**섹션 4. ToolRuntime - 고급 Tool 기능** (L1180~L1492)
- ToolRuntime을 통해 도구 내에서 Agent 상태(state), 요청 컨텍스트(context), 장기 저장소(store), 스트림(writer), Tool Call ID에 접근하는 방법을 다룬다.
- Type-Safe 패턴과 3가지 실전 활용 패턴(대화 이력 기반 추천, 진행률 보고, 사용자별 설정)을 소개한다.

**섹션 5. Tools 고급** (L1495~L1618)
- Pydantic BaseModel을 사용한 복잡한 입력 스키마 정의, Field를 통한 상세 설명과 검증 규칙 부여, 중첩된 Pydantic 모델로 계층적 데이터 구조를 표현하는 방법을 다룬다.

**섹션 6. Tool Calling 이해하기** (L1622~L1791)
- LLM이 도구를 선택하는 전체 과정(bind_tools -> 모델 선택 -> 파싱 -> 실행 -> ToolMessage 반환 -> 최종 응답)을 Mermaid 시퀀스 다이어그램과 함께 설명한다.
- 병렬 Tool Calls 개념도 다룬다.

### 소스 코드 매핑

| 소스 파일 | 라인 수 | 대응 교안 섹션 |
|-----------|------:|-------------|
| `01_chat_models.py` | 189 | 섹션 1 (Chat Models) |
| `02_messages.py` | 305 | 섹션 2 (Messages) |
| `03_tools_basic.py` | 239 | 섹션 3 (Tools 기초) |
| `04_tools_advanced.py` | 467 | 섹션 5 (Tools 고급) |
| `05_tool_calling.py` | 445 | 섹션 6 (Tool Calling) |
| solutions/ (3개 파일) | 671 | 실습 과제 해답 |
| **합계** | **2,316** | |

> 참고: 섹션 4(ToolRuntime)에 대응하는 소스 파일이 없다.

### 학습 흐름 분석

전체적으로 **Bottom-up** 접근을 취한다: 모델(엔진) -> 메시지(입력) -> 도구(확장) -> 도구 호출(통합)의 순서로, 각 구성 요소를 개별적으로 이해한 뒤 Tool Calling에서 하나로 묶는 구조이다.

```
Chat Models ─→ Messages ─→ Tools 기초 ─→ ToolRuntime ─→ Tools 고급 ─→ Tool Calling
 (엔진)        (입력)       (확장)        (고급 접근)     (스키마)       (통합)
```

Part 1의 개념적 소개에서 Part 2의 실제 코드로 전환되는 흐름은 자연스럽다. 다만 Part 2 내부에서 섹션 3(기초) -> 4(ToolRuntime) -> 5(고급) 순서의 난이도 급등 구간이 존재한다.

---

## 교안 피드백 (`docs/part02_fundamentals.md`)

### 오류/수정

- [ ] L105: `01_chat_models.py 라인 10-20` 참조 오류 -> 실제 기본 사용 예제는 `example_1_basic_chat()` 함수로 **L39~L50** 에 위치함
- [ ] L205: `01_chat_models.py 라인 30-80` 참조 오류 -> 프로바이더별 설정 예제는 `example_5_multiple_providers()` 함수로 **L129~** 에 위치함
- [ ] L269: `01_chat_models.py 라인 90-130` 참조 오류 -> Temperature 예제는 `example_3_temperature()` 함수로 **L81~L101** 에 위치함
- [ ] L1061: `03_tools_basic.py 라인 10-30` 참조 오류 -> 첫 번째 Tool 정의는 **L32~L36** 에 위치함
- [ ] L1172: `03_tools_basic.py 라인 40-80` 참조 오류 -> 해당 위치에 Type Hints 전용 예제가 아닌 `example_1_simple_tool()` 함수가 있음
- [ ] L1531: `03_tools_basic.py 라인 90-120` -> **파일명 오류**. Pydantic 스키마 내용은 `03_tools_basic.py`가 아닌 **`04_tools_advanced.py`** 에 있음 (L40~L77)
- [ ] L1618: `03_tools_basic.py 라인 130-180` -> **파일명 오류**. 중첩 모델 내용 역시 **`04_tools_advanced.py`** 에 있음 (L301~)
- [ ] L366: `from langchain.agents import create_agent` -> LangGraph 기반 현행 API에서는 `from langgraph.prebuilt import create_react_agent`가 올바른 import 경로. L874, L909에서도 동일한 문제
- [ ] L156, L160, L164-166: Anthropic 모델명 `claude-sonnet-4-5-20250929`, `claude-opus-4-5-20251101` 등이 사용됨 -> 실제 모델 ID와 일치하는지 검증 필요 (현재 Anthropic 공식 모델 ID는 `claude-sonnet-4-5-20250514` 등의 형식)
- [ ] L200: Azure OpenAI 모델명 `gpt-4.1` -> 실제 존재하는 Azure 배포 모델명인지 확인 필요

### 개선 제안

- [ ] 섹션 4 (ToolRuntime, L1180~L1492): 대응하는 실행 가능한 소스 파일이 없음. 학습자가 직접 실행하며 따라갈 수 있도록 `04b_tool_runtime.py` 또는 유사한 예제 파일 추가를 제안
- [ ] 섹션 배치 순서: 현재 3(Tools 기초) -> 4(ToolRuntime) -> 5(Tools 고급) 순서인데, ToolRuntime은 Agent 상태 접근 등 상위 개념을 다루므로 난이도가 급등함. **3 -> 5 -> 4 -> 6** 순서로 재배치하거나, ToolRuntime을 Part 3 또는 Part 4로 이관하는 것을 검토. 그대로 유지한다면 "심화 내용" 표시를 명확히 추가
- [ ] 섹션 1.5 (Model Profiles, L271~L434): 초급(⭐⭐☆☆☆) 난이도 표기 대비 상당히 고급 내용. `model.profile`은 Beta 기능이기도 함 -> "(선택) 심화 학습" 등으로 표시하여 초급 학습자가 부담 없이 건너뛸 수 있도록 안내
- [ ] 섹션 2.7 (Multimodal, L717~L991): 약 270줄에 달하는 분량으로 Messages 섹션의 절반 이상을 차지. 핵심(이미지 URL 방식)만 본문에 유지하고, PDF/오디오/비디오 및 세부 방법론은 심화 학습이나 별도 부록으로 분리 제안
- [ ] 전반: async 도구 예제가 전혀 없음. 심화 학습(L2182)에서 "Async Tools"를 언급하고 있으므로, 최소한 1개의 async tool 정의/호출 예제를 본문 또는 소스 코드에 추가 제안
- [ ] 섹션 번호 vs 파일 번호: 교안 6개 섹션에 소스 파일 5개가 대응하는데, 섹션 4(ToolRuntime) 때문에 번호가 어긋남 (교안 섹션 5 = 소스 `04_tools_advanced.py`, 교안 섹션 6 = 소스 `05_tool_calling.py`). 학습자 혼란을 줄이기 위해 번호 체계 정렬 검토
- [ ] 섹션 5 -> 6 전환부 (L1618~L1622): 섹션 5에서 복잡한 스키마 정의를 배운 뒤 섹션 6의 Tool Calling으로 넘어가는 전환 문장이 없음. "도구를 정의하는 방법을 배웠으니, 이제 모델이 이 도구를 실제로 어떻게 호출하는지 알아보겠습니다" 정도의 브릿지 문장을 추가하면 흐름이 자연스러워질 것

---

## 예제 코드 피드백 (`src/part02_fundamentals/`)

### 오류/수정

- [ ] `04_tools_advanced.py` L31: `from pydantic import BaseModel, Field, validator` -> Pydantic v2에서 `validator`는 deprecated되었고 `field_validator`로 대체됨. LangChain 1.x는 Pydantic v2를 사용하므로 호환성 문제 발생 가능 -> `from pydantic import BaseModel, Field, field_validator`로 수정
- [ ] `04_tools_advanced.py` L70: `get_weather_advanced.args_schema.schema()` -> Pydantic v2에서 `.schema()`는 deprecated, `.model_json_schema()`가 올바른 API -> `.model_json_schema()`로 수정
- [ ] `05_tool_calling.py` L79: `eval(expression)` 사용 -> 임의의 문자열을 `eval()`로 실행하는 것은 보안 취약점(코드 인젝션 위험). 데모 코드라 하더라도 학습자가 이 패턴을 그대로 복사할 수 있음 -> `# WARNING: eval()은 보안 위험! 프로덕션에서는 절대 사용하지 마세요` 주석 추가, 또는 `ast.literal_eval` / `numexpr.evaluate` 등 안전한 대안으로 교체

### 개선 제안

- [ ] ToolRuntime 전용 소스 파일 부재: 교안 섹션 4의 예제 코드를 실행할 수 있는 파일이 없음 -> `04b_tool_runtime.py` 또는 기존 파일에 ToolRuntime 예제 함수 추가
- [ ] `02_messages.py`: 교안 섹션 2.7에서 Multimodal을 상세히 다루지만 소스 코드에는 Multimodal 예제가 없음 -> 최소한 이미지 URL 방식의 간단한 Multimodal 예제 추가 제안

---

## 기타 의견 (리뷰어 종합 소견)

### 강점

1. **체계적인 Bottom-up 구성**: 모델 -> 메시지 -> 도구 -> 도구 호출 순서의 학습 흐름이 논리적이고, 각 섹션이 이전 섹션 위에 쌓이는 구조가 명확하다.
2. **Mermaid 다이어그램 활용**: 섹션 1의 Chat Models 아키텍처, 섹션 6의 Tool Calling 시퀀스 다이어그램 등 시각적 자료가 이해를 크게 돕는다.
3. **실전 팁과 FAQ 구성**: 교안 후반부의 실전 팁 5개와 FAQ 5개는 실무에서 자주 만나는 의문점을 선제적으로 해소해준다.
4. **풍부한 코드 예제**: 40개 이상의 코드 블록이 포함되어 있어 설명 -> 코드 -> 결과의 사이클이 잘 유지된다.
5. **공식 문서 링크**: 각 섹션마다 관련 공식 문서(official/) 링크가 첨부되어 있어 심화 학습 경로가 명확하다.

### 구조적 제안

1. **ToolRuntime 배치 재검토**: 현재 위치(섹션 4)는 "Tools 기초"와 "Tools 고급" 사이인데, Agent state나 store 같은 개념은 Part 3~4에서 Agent를 본격적으로 다룬 후에야 체감이 된다. 초급 학습자 기준에서 섹션 3 직후에 ToolRuntime이 나오면 아직 Agent를 만들어본 적 없는 상태에서 Agent 상태에 접근하는 코드를 만나게 되어 혼란이 올 수 있다.
2. **Multimodal 분리 고려**: 섹션 2의 Messages는 핵심 개념(4가지 메시지 타입 + Dictionary 포맷)과 심화 개념(Multimodal)으로 나뉘는데, Multimodal 부분이 약 270줄로 과도하게 크다. "2.7 Multimodal"을 별도 섹션이나 부록으로 분리하면 Messages의 핵심 학습 흐름이 더 간결해질 것이다.
3. **섹션간 전환 문구 보강**: 섹션 5에서 6으로의 전환이 갑작스럽다. 각 섹션 사이에 1-2줄의 전환 안내 문구를 두면 학습 흐름이 자연스러워진다.

### 난이도 평가

교안의 표기 난이도는 ⭐⭐☆☆☆(초급)이나, 실제 내용의 난이도 분포는 다음과 같이 편차가 크다:

| 섹션 | 체감 난이도 | 비고 |
|------|-----------|------|
| 1.1~1.4 (Chat Models 기본) | ⭐⭐☆☆☆ | 초급에 적합 |
| 1.5 (Model Profiles) | ⭐⭐⭐☆☆ | Beta 기능, 동적 처리 패턴 포함 |
| 2.1~2.6 (Messages 기본) | ⭐⭐☆☆☆ | 초급에 적합 |
| 2.7 (Multimodal) | ⭐⭐⭐☆☆ | 다양한 입력 방식, 파일 처리 |
| 3 (Tools 기초) | ⭐⭐☆☆☆ | 초급에 적합 |
| 4 (ToolRuntime) | ⭐⭐⭐⭐☆ | Agent 상태, Store, 스트리밍 접근 |
| 5 (Tools 고급) | ⭐⭐⭐☆☆ | Pydantic, 중첩 모델 |
| 6 (Tool Calling) | ⭐⭐⭐☆☆ | 전체 루프 이해 필요 |

섹션 4(ToolRuntime)의 난이도가 특히 높아, 교안 전체를 "초급"으로 표기하기에는 무리가 있다. 전체 난이도를 ⭐⭐⭐☆☆(초중급)으로 상향하거나, 고급 섹션에 명시적인 난이도 표시를 추가하는 것을 제안한다.

### Part 1 -> 2 -> 3 연결성

- **Part 1 -> 2**: Part 1 마지막의 "다음 단계" 섹션에서 Part 2의 학습 내용(Chat Models, Messages, Tools, Tool Calling)을 명시적으로 안내하고 있어, 전환이 자연스럽다. Part 1에서 `create_agent()`와 `@tool`을 표면적으로 소개한 뒤, Part 2에서 각 구성 요소를 심층적으로 다루는 구조가 효과적이다.
- **Part 2 -> 3**: Part 2의 섹션 6에서 `bind_tools()` + 수동 실행 루프를 가르친 뒤, Part 3에서 `create_agent()`로 이를 자동화하는 흐름이다. 이 전환은 논리적이나, Part 2 교안 내에서 "수동 루프를 이해했으니, 다음 파트에서는 이 전체 과정을 자동으로 처리하는 `create_agent()`를 배웁니다"와 같은 예고가 "다음 단계"(L2193~) 섹션에만 짧게 나와 있다. 섹션 6 본문 내에서도 간단히 언급하면 학습 동기 부여에 도움이 될 것이다.
