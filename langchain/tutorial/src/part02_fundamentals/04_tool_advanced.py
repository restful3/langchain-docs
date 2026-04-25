"""
================================================================================
LangChain AI Agent 마스터 교안
Part 2: LangChain 기초
================================================================================

파일명: 04_tool_advanced.py
난이도: ⭐⭐⭐☆☆ (중급)
예상 시간: 25분

📚 학습 목표:
  - Pydantic BaseModel을 사용한 Tool 스키마 정의
  - Field를 사용한 파라미터 검증 및 설명
  - bind_tools()로 LLM에 도구 연결하기
  - Tool call 실행 (전체 워크플로우)
  - Tool call 에러 핸들링

📖 공식 문서:
  • Tools: /official/09-tools.md
  • Tool Calling: /official/09-tools.md

🔧 필요한 패키지:
  pip install langchain langchain-openai pydantic python-dotenv

🚀 실행 방법:
  python 04_tool_advanced.py

================================================================================
"""

import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from pydantic import BaseModel, Field, field_validator
from typing import Optional


# ============================================================================
# 예제 1: Pydantic BaseModel로 Tool 입력 스키마 정의
# ============================================================================

class WeatherInput(BaseModel):
    """날씨 조회를 위한 입력 스키마"""
    city: str = Field(description="날씨를 조회할 도시 이름 (예: 서울, 부산)")
    country: str = Field(default="한국", description="국가 이름")


@tool(args_schema=WeatherInput)
def get_weather_advanced(city: str, country: str = "한국") -> str:
    """주어진 도시의 날씨를 상세하게 조회합니다."""
    # 실제로는 API를 호출
    weather_data = {
        ("서울", "한국"): "맑음, 22도, 습도 60%",
        ("부산", "한국"): "흐림, 20도, 습도 75%",
        ("뉴욕", "미국"): "비, 15도, 습도 85%",
    }

    weather = weather_data.get((city, country), "날씨 정보를 찾을 수 없습니다")
    return f"{country} {city}의 날씨: {weather}"


def example_1_pydantic_schema():
    """Pydantic BaseModel을 사용한 스키마 정의"""
    print("=" * 70)
    print("📌 예제 1: Pydantic BaseModel로 Tool 입력 스키마 정의")
    print("=" * 70)

    # Tool 정보 확인
    print(f"\n🔧 도구 이름: {get_weather_advanced.name}")
    print(f"📝 도구 설명: {get_weather_advanced.description}")
    print(f"\n📋 입력 스키마:")
    print(f"   {get_weather_advanced.args_schema.model_json_schema()}")

    # Tool 실행
    result1 = get_weather_advanced.invoke({"city": "서울"})
    print(f"\n🌤️  {result1}")

    result2 = get_weather_advanced.invoke({"city": "뉴욕", "country": "미국"})
    print(f"🌤️  {result2}")

    print("\n💡 Pydantic으로 타입 검증, 기본값, 설명을 한번에 정의!\n")


# ============================================================================
# 예제 2: Field 설명과 검증
# ============================================================================

class UserProfileInput(BaseModel):
    """사용자 프로필 생성 입력"""
    name: str = Field(description="사용자 이름", min_length=2, max_length=50)
    age: int = Field(description="사용자 나이", ge=0, le=150)  # ge=greater or equal
    email: str = Field(description="이메일 주소")
    bio: Optional[str] = Field(default=None, description="자기소개 (선택사항)")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """이메일 형식 검증"""
        if '@' not in v:
            raise ValueError('올바른 이메일 형식이 아닙니다')
        return v


@tool(args_schema=UserProfileInput)
def create_user_profile(name: str, age: int, email: str, bio: Optional[str] = None) -> str:
    """사용자 프로필을 생성합니다."""
    profile = f"👤 이름: {name}\n   나이: {age}세\n   이메일: {email}"
    if bio:
        profile += f"\n   소개: {bio}"
    return profile


def example_2_field_validation():
    """Field를 사용한 상세 검증"""
    print("=" * 70)
    print("📌 예제 2: Field 설명과 검증")
    print("=" * 70)

    # 정상 케이스
    print("\n✅ 정상 케이스:")
    result1 = create_user_profile.invoke({
        "name": "김철수",
        "age": 30,
        "email": "kim@example.com",
        "bio": "파이썬 개발자입니다."
    })
    print(result1)

    # bio 없이 (Optional)
    print("\n✅ bio 없이 (Optional):")
    result2 = create_user_profile.invoke({
        "name": "이영희",
        "age": 25,
        "email": "lee@example.com"
    })
    print(result2)

    # 에러 케이스 처리
    print("\n❌ 잘못된 입력 (나이 음수):")
    try:
        result3 = create_user_profile.invoke({
            "name": "박민수",
            "age": -5,  # 잘못된 나이
            "email": "park@example.com"
        })
    except Exception as e:
        print(f"   오류 발생: {str(e)}")

    print("\n💡 Field로 최소/최대값, 길이 등을 자동으로 검증!\n")


# ============================================================================
# Tool Calling용 도구 정의 (예제 3-5에서 사용)
# ============================================================================

@tool
def get_weather(city: str) -> str:
    """주어진 도시의 날씨를 조회합니다.

    Args:
        city: 도시 이름 (예: 서울, 부산, 뉴욕)
    """
    weather_data = {
        "서울": "맑음, 22도",
        "부산": "흐림, 20도",
        "뉴욕": "비, 15도",
        "도쿄": "맑음, 18도",
    }
    return weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다")


@tool
def calculate(expression: str) -> str:
    """수학 계산을 수행합니다.

    Args:
        expression: 계산할 수식 (예: "2 + 2", "10 * 5")
    """
    try:
        # 주의: eval()은 임의 코드 실행 위험이 있습니다.
        # 프로덕션에서는 ast.literal_eval() 또는 numexpr.evaluate()를 사용하세요.
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"계산 오류: {str(e)}"


@tool
def search_web(query: str) -> str:
    """웹에서 정보를 검색합니다.

    Args:
        query: 검색어
    """
    # 실제로는 검색 API를 호출
    return f"'{query}'에 대한 검색 결과: LangChain은 LLM 애플리케이션 개발 프레임워크입니다."


@tool
def divide_numbers(a: float, b: float) -> str:
    """두 숫자를 나눕니다.

    Args:
        a: 분자
        b: 분모
    """
    if b == 0:
        raise ValueError("0으로 나눌 수 없습니다")
    result = a / b
    return f"{a} ÷ {b} = {result}"


# ============================================================================
# 예제 3: bind_tools()로 도구 연결하기
# ============================================================================

def example_3_bind_tools():
    """LLM에 도구를 연결하는 기본 방법"""
    print("=" * 70)
    print("📌 예제 3: bind_tools()로 도구 연결하기")
    print("=" * 70)

    # LLM 초기화
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 도구를 LLM에 연결
    model_with_tools = model.bind_tools([get_weather, calculate])

    print("\n🔧 연결된 도구:")
    print(f"   - {get_weather.name}: {get_weather.description}")
    print(f"   - {calculate.name}: {calculate.description}")

    # LLM 호출 (도구가 필요한 질문)
    response = model_with_tools.invoke("서울의 날씨는 어때?")

    print(f"\n📩 응답 타입: {type(response).__name__}")
    print(f"📩 응답 내용: {response.content}")

    # Tool call 요청 확인
    if response.tool_calls:
        print(f"\n🛠️  도구 호출 요청:")
        for tool_call in response.tool_calls:
            print(f"   도구: {tool_call['name']}")
            print(f"   인자: {tool_call['args']}")
    else:
        print("\n⚠️  도구 호출 요청 없음")

    print("\n💡 LLM이 필요한 도구를 자동으로 선택!\n")


# ============================================================================
# 예제 4: Tool call 실행하기
# ============================================================================

def example_4_execute_tool_calls():
    """Tool call을 실제로 실행하기"""
    print("=" * 70)
    print("📌 예제 4: Tool call 실행하기")
    print("=" * 70)

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [get_weather, calculate, search_web]
    model_with_tools = model.bind_tools(tools)

    # 도구 이름으로 매핑
    tools_map = {tool.name: tool for tool in tools}

    # 사용자 질문
    user_question = "서울의 날씨는 어때?"
    print(f"\n👤 사용자: {user_question}")

    # 1단계: LLM이 도구 호출 요청
    messages = [HumanMessage(content=user_question)]
    response = model_with_tools.invoke(messages)

    print(f"\n🤖 LLM 응답:")
    if response.tool_calls:
        print(f"   도구 호출 요청: {response.tool_calls[0]['name']}")

        # 2단계: 도구 실행
        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']

            print(f"\n🔧 도구 실행: {tool_name}({tool_args})")

            # 도구 실행
            selected_tool = tools_map[tool_name]
            tool_result = selected_tool.invoke(tool_args)

            print(f"📤 도구 결과: {tool_result}")

            # 3단계: 도구 결과를 LLM에 전달
            messages.append(response)  # LLM의 tool call 요청
            messages.append(
                ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call['id']
                )
            )

        # 4단계: 최종 답변 생성
        final_response = model_with_tools.invoke(messages)
        print(f"\n🤖 최종 답변: {final_response.content}")

    print("\n💡 LLM 요청 → 도구 실행 → 결과 반환 → 최종 답변!\n")


# ============================================================================
# 예제 5: Tool call 에러 핸들링
# ============================================================================

def example_5_error_handling():
    """Tool call 에러 핸들링"""
    print("=" * 70)
    print("📌 예제 5: Tool call 에러 핸들링")
    print("=" * 70)

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [divide_numbers, calculate]
    model_with_tools = model.bind_tools(tools)

    tools_map = {tool.name: tool for tool in tools}

    # 에러가 발생할 수 있는 질문
    user_question = "10을 0으로 나누면?"
    print(f"\n👤 사용자: {user_question}")

    messages = [HumanMessage(content=user_question)]
    response = model_with_tools.invoke(messages)

    if response.tool_calls:
        messages.append(response)

        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']

            print(f"\n🔧 도구 실행: {tool_name}({tool_args})")

            try:
                selected_tool = tools_map[tool_name]
                tool_result = selected_tool.invoke(tool_args)
                print(f"✅ 결과: {tool_result}")

                messages.append(
                    ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call['id']
                    )
                )

            except Exception as e:
                error_message = f"오류 발생: {str(e)}"
                print(f"❌ {error_message}")

                # 에러를 ToolMessage로 LLM에 전달
                messages.append(
                    ToolMessage(
                        content=error_message,
                        tool_call_id=tool_call['id'],
                        status="error"
                    )
                )

        # LLM이 에러를 이해하고 답변
        final_response = model_with_tools.invoke(messages)
        print(f"\n🤖 LLM의 에러 처리:\n   {final_response.content}")

    print("\n💡 에러도 ToolMessage로 전달하면 LLM이 처리!\n")


# ============================================================================
# 메인 실행
# ============================================================================

def main():
    print("\n🎓 Part 2: LangChain 기초 - Tools 고급 & Tool Calling\n")

    # Part A: Pydantic 스키마 (API 키 불필요)
    example_1_pydantic_schema()
    input("⏎ 계속하려면 Enter...")

    example_2_field_validation()
    input("⏎ 계속하려면 Enter...")

    # Part B: Tool Calling (OPENAI_API_KEY 필요)
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("\n" + "=" * 70)
        print("⚠️  OPENAI_API_KEY가 설정되지 않아 예제 3-5를 건너뜁니다.")
        print("📝 .env 파일에 API 키를 설정하면 Tool Calling 예제를 실행할 수 있습니다.")
        print("=" * 70 + "\n")
    else:
        example_3_bind_tools()
        input("⏎ 계속하려면 Enter...")

        example_4_execute_tool_calls()
        input("⏎ 계속하려면 Enter...")

        example_5_error_handling()

    print("=" * 70)
    print("🎉 Tools 고급 & Tool Calling 학습 완료!")
    print("📖 다음: Part 3 - 첫 번째 Agent 만들기")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()


# ============================================================================
# 📚 추가 학습 포인트
# ============================================================================
#
# 1. Pydantic BaseModel 장점:
#    - 자동 타입 검증 + 명확한 스키마 정의
#    - Field로 설명, 기본값, 검증 조건을 한번에 지정
#    - field_validator로 커스텀 검증 로직 추가 가능
#
# 2. Tool Calling 프로세스:
#    ① 사용자 질문 → LLM
#    ② LLM이 필요한 도구 선택 및 인자 생성
#    ③ 도구 실행
#    ④ 결과를 ToolMessage로 LLM에 전달
#    ⑤ LLM이 최종 답변 생성
#
# 3. bind_tools() vs Agent:
#    - bind_tools(): 수동으로 tool call 실행 필요
#    - Agent: 자동으로 tool call 실행 (Part 3에서 학습)
#
# 4. ToolMessage의 역할:
#    - 도구 실행 결과를 LLM에 전달
#    - tool_call_id로 어떤 요청의 결과인지 연결
#    - 에러도 ToolMessage(status="error")로 전달 가능
#
# ============================================================================
# 🐛 자주 발생하는 문제
# ============================================================================
#
# 문제: "validation error"가 계속 발생
# 해결: Pydantic 스키마와 실제 함수 시그니처가 일치하는지 확인
#
# 문제: tool_call_id 매칭 오류
# 해결: ToolMessage의 tool_call_id는 반드시 원래 요청의 ID와 일치해야 함
#
# 문제: 도구 실행 에러가 발생하면 전체 중단
# 해결: try-except로 에러를 잡아 ToolMessage로 전달하면 LLM이 처리
#
# ============================================================================
