# 프롬프트 엔지니어링 가이드

## 기본 원칙

### 1. 명확성
```
❌ 나쁜 예:
"날씨 알려줘"

✅ 좋은 예:
"서울의 현재 날씨를 온도와 습도를 포함해서 알려주세요"
```

### 2. 구체성
```
❌ 나쁜 예:
"Python 코드 작성해줘"

✅ 좋은 예:
"두 숫자를 더하는 Python 함수를 작성해주세요.
함수명은 add이고, 파라미터는 a, b입니다.
타입 힌트와 docstring을 포함해주세요."
```

### 3. 컨텍스트 제공
```python
prompt = f"""
당신은 Python 전문가입니다.

작업: {task}
제약사항: Python 3.10 이상
출력 형식: 완전한 실행 가능한 코드

코드:
"""
```

## System Prompt 작성

### Agent용 System Prompt
```python
SYSTEM_PROMPT = """
**역할**: 당신은 고객 서비스 담당자입니다.

**목표**:
- 고객 문의에 정확히 답변
- 친절하고 공손한 톤 유지
- 3문장 이내로 간결하게 답변

**가능한 작업**:
1. 주문 조회 (tool: check_order)
2. 환불 처리 (tool: process_refund)
3. 배송 추적 (tool: track_shipment)

**제약사항**:
- 환불 금액 10만원 초과 시 관리자에게 에스컬레이션
- 개인정보는 절대 공유하지 않음
- 확실하지 않으면 "잘 모르겠습니다"라고 답변

**응답 형식**:
1. 고객 문제 확인
2. 해결 방법 제시
3. 추가 도움 필요 여부 확인
"""
```

### Few-Shot Examples
```python
EXAMPLES = """
예시 1:
사용자: 주문번호 12345 환불해주세요
답변: 주문번호 12345를 확인했습니다. 총 50,000원 환불 처리하겠습니다.
     영업일 기준 3-5일 내 계좌로 입금됩니다. 다른 도움이 필요하신가요?

예시 2:
사용자: 배송이 왜 이렇게 늦나요?
답변: 불편을 드려 죄송합니다. 주문번호를 알려주시면 배송 상태를 확인해드리겠습니다.
"""
```

## Chain of Thought (CoT)

### 기본 CoT
```python
prompt = """
문제: 73 + 48은 무엇인가요?

단계별로 생각해봅시다:
1단계: 일의 자리 더하기
2단계: 십의 자리 더하기
3단계: 최종 답
"""
```

### Zero-Shot CoT
```python
prompt = "73 + 48은 무엇인가요? 단계별로 생각해봅시다:"
```

### 복잡한 문제 해결
```python
prompt = """
당신은 논리적 추론을 하는 AI입니다.

문제: 서울에서 부산까지 기차로 2시간 30분 걸립니다.
     기차는 오전 10시에 출발합니다.
     부산 도착 후 30분 뒤 회의가 있습니다.
     회의는 몇 시에 시작하나요?

단계별 분석:
1. 출발 시간:
2. 이동 시간:
3. 도착 시간:
4. 회의 시작 시간:
"""
```

## Tool Calling 프롬프트

### 도구 설명 (Docstring)
```python
@tool
def get_weather(city: str, units: str = "metric") -> str:
    """
    주어진 도시의 현재 날씨를 조회합니다.

    Args:
        city: 도시 이름 (예: "Seoul", "서울", "New York")
        units: 온도 단위 ("metric" = 섭씨, "imperial" = 화씨)

    Returns:
        날씨 정보 문자열 (온도, 습도, 날씨 상태 포함)

    Examples:
        >>> get_weather("서울")
        "서울: 맑음, 22°C, 습도 65%"

        >>> get_weather("New York", "imperial")
        "New York: Clear, 72°F, Humidity 60%"
    """
    pass
```

### 여러 도구가 있을 때
```python
TOOL_SELECTION_PROMPT = """
사용 가능한 도구:
1. get_weather: 날씨 조회
2. search_web: 웹 검색
3. calculate: 계산

질문에 가장 적합한 도구를 선택하세요:
- 날씨 관련 → get_weather
- 최신 정보 필요 → search_web
- 수학 계산 → calculate
"""
```

## 구조화된 출력

### JSON 출력
```python
prompt = """
다음 텍스트에서 정보를 추출하고 JSON으로 반환하세요:

텍스트: "홍길동은 서울에 살며, 이메일은 hong@example.com입니다."

JSON 형식:
{
  "name": "이름",
  "city": "도시",
  "email": "이메일"
}
"""
```

### Pydantic 모델
```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
    city: str

# LangChain에서 자동으로 프롬프트 생성
result = llm.with_structured_output(Person).invoke(
    "홍길동은 30살이고 서울에 삽니다"
)
```

## 테스트와 반복

### A/B 테스트
```python
prompts = {
    "A": "간단히 설명해주세요",
    "B": "초등학생도 이해할 수 있게 설명해주세요"
}

for version, prompt in prompts.items():
    result = llm.invoke(prompt)
    print(f"{version}: {result}")
```

### 평가
```python
from langsmith import evaluate

def my_evaluator(run, example):
    # 답변의 길이가 적절한지 확인
    response_length = len(run.outputs["output"])
    return {"score": 1 if 50 < response_length < 200 else 0}

results = evaluate(
    agent,
    dataset,
    evaluators=[my_evaluator]
)
```

## 고급 기법

### Self-Ask
```python
prompt = """
질문: LangChain을 만든 회사의 CEO는 누구인가?

하위 질문을 만들고 답하세요:
1. LangChain을 만든 회사는?
2. 그 회사의 CEO는?
"""
```

### ReAct (Reasoning + Acting)
```python
prompt = """
생각: 사용자가 날씨를 물어봤다
행동: get_weather("서울")
관찰: 서울은 맑고 22도다
생각: 이 정보를 친절하게 전달하면 된다
답변: ...
"""
```

### Tree of Thoughts
```python
prompt = """
문제를 푸는 3가지 다른 접근법을 제시하세요:

접근법 1:
- 장점:
- 단점:

접근법 2:
- 장점:
- 단점:

접근법 3:
- 장점:
- 단점:

최선의 접근법:
"""
```

## 안티패턴

### 1. 너무 긴 프롬프트
```
❌ 3000단어짜리 지시사항
✅ 핵심만 간결하게
```

### 2. 모호한 표현
```
❌ "좀 더 나은 답변"
✅ "50자 이내로 답변"
```

### 3. 과도한 제약
```
❌ 30개의 규칙과 제약사항
✅ 3-5개의 핵심 규칙
```

## 디버깅

### 단계별 확인
```python
# 1. 간단한 프롬프트로 시작
prompt_v1 = "날씨 알려줘"

# 2. 구체화
prompt_v2 = "서울 날씨 알려줘"

# 3. 세부사항 추가
prompt_v3 = """
서울의 현재 날씨를 다음 형식으로 알려주세요:
- 온도: X°C
- 날씨: [맑음/흐림/비/눈]
"""
```

### 프롬프트 템플릿
```python
from langchain.prompts import PromptTemplate

template = PromptTemplate(
    input_variables=["city", "format"],
    template="""
    {city}의 날씨를 {format} 형식으로 알려주세요.
    """
)

prompt = template.format(city="서울", format="JSON")
```

## 참고 자료

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Library](https://docs.anthropic.com/en/prompt-library/library)
- [LangChain Prompt Templates](https://python.langchain.com/docs/concepts/prompt_templates/)
- [ReAct 논문](https://arxiv.org/abs/2210.03629)
