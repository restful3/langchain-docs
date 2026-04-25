"""
================================================================================
LangChain AI Agent 마스터 교안
Part 3: 첫 번째 Agent 만들기
================================================================================

파일명: 02_react_agent.py
난이도: ⭐⭐⭐☆☆ (중급)
예상 시간: 30분

📚 학습 목표:
  - ReAct 패턴(Reasoning + Acting)의 개념 이해
  - 날씨 Agent 구현과 ToolRuntime 활용
  - 단일/순차/병렬 도구 호출 패턴 학습
  - Agent 실행 과정 상세 분석

📖 공식 문서:
  • Agents: /official/06-agents.md
  • ReAct 패턴: https://arxiv.org/abs/2210.03629
  • Quickstart: /official/03-quickstart.md

📄 교안 문서:
  • Part 3 개요: /docs/part03_first_agent.md (섹션 2, 3)

🚀 실행 방법:
  python 02_react_agent.py

================================================================================
"""

import os
import time
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool, ToolRuntime

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("❌ 오류: OPENAI_API_KEY가 설정되지 않았습니다.")
    print("📝 .env 파일을 확인하고 API 키를 설정하세요.")
    exit(1)


# ============================================================================
# 예제 1: ReAct란? (개념 설명)
# ============================================================================

def example_1_what_is_react():
    """ReAct 패턴의 개념과 구조"""
    print("=" * 70)
    print("📌 예제 1: ReAct 패턴이란?")
    print("=" * 70)

    print("""
🔹 ReAct (Reasoning + Acting):
   AI Agent가 문제를 해결하는 핵심 패턴입니다.
   추론(Reasoning)과 행동(Acting)을 번갈아가며 목표를 달성합니다.

🔄 ReAct 루프:

   1️⃣ Reasoning (추론)
      → "무엇을 알아야 하는가?"
      → "어떤 도구를 사용할 것인가?"

   2️⃣ Acting (행동)
      → 도구 실행
      → 외부 시스템 호출

   3️⃣ Observation (관찰)
      → 도구 실행 결과 확인
      → 새로운 정보 획득

   4️⃣ 반복 또는 종료
      → 정보가 충분하면: 최종 답변
      → 정보가 부족하면: 1번으로 돌아가기

📊 실제 예시:

   [사용자] "서울과 부산 중 어디가 더 따뜻해?"

   [Reasoning 1] "두 도시의 온도를 비교해야 하므로 날씨 정보가 필요하다"
   [Acting 1]    get_weather("서울"), get_weather("부산") 호출
   [Observation] 서울: 22°C, 부산: 20°C

   [Reasoning 2] "이제 비교할 수 있다. 서울이 2도 더 높다"
   [Final]       "서울이 부산보다 2도 더 따뜻합니다"

💡 ReAct의 장점:
   - 해석 가능성: 각 단계의 추론 과정을 확인 가능
   - 유연성: 예상치 못한 상황에 대응 가능
   - 효율성: 필요한 만큼만 도구를 사용
   - 디버깅 용이: 어느 단계에서 문제가 발생했는지 파악 가능
    """)

    print("💡 핵심: LangChain의 create_agent()는 자동으로 ReAct 루프를 구현합니다\n")


# ============================================================================
# 예제 2: 단일 도구 호출 - 기본 ReAct
# ============================================================================

def example_2_single_tool_call():
    """가장 간단한 ReAct: 한 번의 도구 호출"""
    print("=" * 70)
    print("📌 예제 2: 단일 도구 호출 - 기본 ReAct")
    print("=" * 70)

    @tool
    def get_weather(city: str) -> str:
        """주어진 도시의 현재 날씨를 조회합니다.

        Args:
            city: 도시 이름 (예: 서울, 부산)
        """
        print(f"      [도구 실행] get_weather('{city}') 호출")
        time.sleep(0.5)
        weather_data = {
            "서울": "맑음, 22°C, 습도 60%",
            "부산": "흐림, 20°C, 습도 70%",
            "뉴욕": "비, 15°C, 습도 85%",
            "파리": "맑음, 18°C, 습도 55%",
        }
        result = weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다")
        print(f"      [도구 결과] {result}")
        return result

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(
        model=model,
        tools=[get_weather],
        system_prompt="당신은 날씨 정보를 제공하는 Agent입니다. 항상 도구를 사용하세요.",
    )

    print("\n👤 사용자: 서울 날씨는?")
    print("\n🔄 ReAct 루프 시작:\n")
    print("   1️⃣ [Reasoning] Agent가 생각 중...")
    print("      '서울의 날씨 정보가 필요하므로 get_weather 도구를 사용해야겠다'")
    print("\n   2️⃣ [Acting] 도구 호출 중...")

    result = agent.invoke({
        "messages": [{"role": "user", "content": "서울 날씨는?"}]
    })

    print("\n   3️⃣ [Observation] 결과를 바탕으로 최종 답변 생성")
    print(f"\n🤖 Agent: {result['messages'][-1].content}")

    print("\n💡 핵심: 단순한 질문도 Reasoning → Acting → Observation 과정을 거칩니다\n")


# ============================================================================
# 예제 3: 두 도구 조합 + ToolRuntime
# ============================================================================

def example_3_two_tools_with_runtime():
    """get_weather_for_location과 get_user_location 도구 + ToolRuntime"""
    print("=" * 70)
    print("📌 예제 3: 두 도구 조합 + ToolRuntime 컨텍스트")
    print("=" * 70)

    @tool
    def get_weather_for_location(city: str) -> str:
        """주어진 도시의 날씨를 조회합니다.

        Args:
            city: 날씨를 조회할 도시 이름
        """
        weather_data = {
            "서울": "맑음, 22°C, 습도 60%",
            "부산": "흐림, 20°C, 습도 70%",
            "뉴욕": "비, 15°C, 습도 85%",
            "플로리다": "맑음, 28°C, 습도 75%",
        }
        return weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다")

    @dataclass
    class Context:
        """런타임 컨텍스트 스키마"""
        user_id: str

    @tool
    def get_user_location(runtime: ToolRuntime[Context]) -> str:
        """현재 사용자의 위치를 조회합니다.

        ToolRuntime을 통해 런타임 컨텍스트에 접근합니다.
        """
        user_id = runtime.context.user_id
        location_map = {
            "1": "서울",
            "2": "부산",
            "3": "뉴욕",
        }
        return location_map.get(user_id, "서울")

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    agent = create_agent(
        model=model,
        tools=[get_weather_for_location, get_user_location],
        context_schema=Context,
    )

    print("\n👤 사용자 1: 밖에 날씨 어때?")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "밖에 날씨 어때?"}]},
        context=Context(user_id="1")
    )

    print(f"🤖 Agent: {result['messages'][-1].content}")

    print("\n💡 포인트:")
    print("  - Agent가 '밖에'라는 표현에서 위치 파악이 필요함을 인지했습니다")
    print("  - get_user_location → get_weather_for_location 순서로 도구를 사용했습니다")
    print("  - ToolRuntime[Context]로 런타임 컨텍스트에 접근했습니다\n")


# ============================================================================
# 예제 4: Agent 실행 과정 상세 분석
# ============================================================================

def example_4_execution_analysis():
    """Agent의 실행 과정을 단계별로 분석"""
    print("=" * 70)
    print("📌 예제 4: Agent 실행 과정 상세 분석")
    print("=" * 70)

    @tool
    def get_weather_for_location(city: str) -> str:
        """주어진 도시의 날씨를 조회합니다."""
        weather_data = {
            "서울": "맑음, 22°C, 습도 60%",
            "부산": "흐림, 20°C, 습도 70%",
        }
        return weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다")

    @dataclass
    class Context:
        user_id: str

    @tool
    def get_user_location(runtime: ToolRuntime[Context]) -> str:
        """현재 사용자의 위치를 조회합니다."""
        user_id = runtime.context.user_id
        location_map = {"1": "서울", "2": "부산"}
        return location_map.get(user_id, "서울")

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(
        model=model,
        tools=[get_weather_for_location, get_user_location],
        context_schema=Context,
        system_prompt="당신은 날씨 정보를 제공하는 친절한 Agent입니다.",
    )

    print("\n👤 사용자: 현재 날씨 알려줘")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "현재 날씨 알려줘"}]},
        context=Context(user_id="1")
    )

    print("\n🔍 실행 과정 분석:\n")
    for i, msg in enumerate(result["messages"], 1):
        role = msg.__class__.__name__

        if role == "HumanMessage":
            print(f"[Step {i}] 👤 사용자 입력")
            print(f"         '{msg.content}'")

        elif role == "AIMessage":
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"\n[Step {i}] 🤔 Agent 추론 + 도구 호출")
                for tc in msg.tool_calls:
                    print(f"         도구: {tc['name']}({tc['args']})")
            else:
                print(f"\n[Step {i}] 💡 최종 답변")
                print(f"         {msg.content}")

        elif role == "ToolMessage":
            print(f"\n[Step {i}] 👀 도구 실행 결과")
            print(f"         결과: {msg.content}")

    print("\n💡 포인트:")
    print("  - HumanMessage → AIMessage (tool_calls) → ToolMessage → AIMessage (final)")
    print("  - 각 단계를 추적하여 디버깅할 수 있습니다\n")


# ============================================================================
# 예제 5: 순차적 도구 호출
# ============================================================================

def example_5_sequential_tool_calls():
    """여러 도구를 순차적으로 호출하는 ReAct"""
    print("=" * 70)
    print("📌 예제 5: 순차적 도구 호출 - 복잡한 ReAct")
    print("=" * 70)

    @tool
    def search_product(query: str) -> str:
        """제품을 검색합니다.

        Args:
            query: 검색할 제품 키워드
        """
        print(f"      [도구 실행] search_product('{query}')")
        time.sleep(0.5)
        products = {
            "wireless headphones": "상위 5개 제품: WH-1000XM5, AirPods Max, Bose QC45, Sennheiser Momentum, Bang & Olufsen H95",
            "laptop": "상위 5개 제품: MacBook Pro, Dell XPS, ThinkPad X1, Surface Laptop, HP Spectre",
        }
        result = products.get(query, f"'{query}'에 대한 검색 결과가 없습니다")
        print(f"      [도구 결과] {result}")
        return result

    @tool
    def check_inventory(product_id: str) -> str:
        """제품 재고를 확인합니다.

        Args:
            product_id: 제품 ID 또는 이름
        """
        print(f"      [도구 실행] check_inventory('{product_id}')")
        time.sleep(0.5)
        inventory = {
            "WH-1000XM5": "재고 10개 있음",
            "AirPods Max": "품절",
            "MacBook Pro": "재고 5개 있음",
        }
        result = inventory.get(product_id, f"'{product_id}' 재고 정보가 없습니다")
        print(f"      [도구 결과] {result}")
        return result

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(
        model=model,
        tools=[search_product, check_inventory],
        system_prompt="당신은 제품 검색과 재고 확인을 도와주는 쇼핑 Agent입니다.",
    )

    print("\n👤 사용자: 지금 가장 인기있는 무선 헤드폰을 찾아서 재고가 있는지 확인해줘")
    print("\n🔄 ReAct 루프 시작:\n")

    result = agent.invoke({
        "messages": [{"role": "user", "content": "지금 가장 인기있는 무선 헤드폰을 찾아서 재고가 있는지 확인해줘"}]
    })

    print(f"\n🤖 Agent: {result['messages'][-1].content}")

    print("\n💡 핵심 포인트:")
    print("  - Agent가 자동으로 2개의 도구를 순차적으로 호출했습니다")
    print("  - 첫 번째 도구의 결과가 두 번째 도구의 입력이 되었습니다")
    print("  - 이것이 ReAct 패턴의 힘: 체인처럼 연결된 추론과 행동\n")


# ============================================================================
# 예제 6: 병렬 도구 호출
# ============================================================================

def example_6_parallel_tool_calls():
    """독립적인 도구들을 병렬로 호출하는 ReAct"""
    print("=" * 70)
    print("📌 예제 6: 병렬 도구 호출 - 효율적인 ReAct")
    print("=" * 70)

    @tool
    def get_weather(city: str) -> str:
        """도시의 날씨를 조회합니다."""
        print(f"      [도구 실행] get_weather('{city}')")
        time.sleep(0.5)
        weather_data = {
            "서울": "맑음, 22°C",
            "부산": "흐림, 20°C",
            "제주": "비, 18°C",
        }
        result = weather_data.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다")
        print(f"      [도구 결과] {result}")
        return result

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(
        model=model,
        tools=[get_weather],
        system_prompt="당신은 날씨 비교를 도와주는 Agent입니다. 여러 도시를 비교할 때는 효율적으로 처리하세요.",
    )

    print("\n👤 사용자: 서울, 부산, 제주 중 어디가 가장 따뜻해?")
    print("\n🔄 ReAct 루프 시작:\n")

    print("   1️⃣ [Reasoning] '세 도시의 온도가 모두 필요하다. 독립적이므로 병렬로 조회하자'")
    print("\n   2️⃣ [Acting] 병렬 도구 호출...")
    print("      → get_weather('서울')")
    print("      → get_weather('부산')")
    print("      → get_weather('제주')")

    result = agent.invoke({
        "messages": [{"role": "user", "content": "서울, 부산, 제주 중 어디가 가장 따뜻해?"}]
    })

    print("\n   3️⃣ [Observation] 모든 결과를 동시에 받음")
    print("\n   4️⃣ [Final Answer] 온도 비교 후 최종 답변")

    print(f"\n🤖 Agent: {result['messages'][-1].content}")

    print("\n💡 핵심 포인트:")
    print("  - 독립적인 도구 호출은 병렬로 실행되어 효율적입니다")
    print("  - Agent가 자동으로 병렬 실행 가능 여부를 판단합니다")
    print("  - 순차 vs 병렬 결정은 LLM의 추론 능력에 달려있습니다\n")


# ============================================================================
# 메인 실행
# ============================================================================

def main():
    print("\n🎓 Part 3: ReAct 패턴과 날씨 Agent\n")

    example_1_what_is_react()
    input("\n⏎ 계속하려면 Enter를 누르세요...")

    example_2_single_tool_call()
    input("\n⏎ 계속하려면 Enter를 누르세요...")

    example_3_two_tools_with_runtime()
    input("\n⏎ 계속하려면 Enter를 누르세요...")

    example_4_execution_analysis()
    input("\n⏎ 계속하려면 Enter를 누르세요...")

    example_5_sequential_tool_calls()
    input("\n⏎ 계속하려면 Enter를 누르세요...")

    example_6_parallel_tool_calls()

    print("\n" + "=" * 70)
    print("🎉 ReAct 패턴과 날씨 Agent 학습 완료!")
    print("=" * 70)
    print("\n💡 주요 학습 내용:")
    print("   ✅ ReAct 패턴: Reasoning → Acting → Observation")
    print("   ✅ ToolRuntime으로 런타임 컨텍스트 활용")
    print("   ✅ Agent 실행 과정 분석 (messages 추적)")
    print("   ✅ 순차적 vs 병렬 도구 호출")
    print("\n📖 다음: 03_streaming_agent.py - Streaming Agent")
    print("📚 참고: ReAct 논문 https://arxiv.org/abs/2210.03629")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()


# ============================================================================
# 📚 핵심 포인트
# ============================================================================
#
# 1. ReAct vs Chain-of-Thought (CoT):
#    - CoT: 순수한 추론만 (도구 사용 없음)
#    - ReAct: 추론 + 도구 사용 (더 실용적)
#    - ReAct = CoT + Tool Calling
#
# 2. 런타임 컨텍스트 (ToolRuntime):
#    - 도구가 실행 시점의 정보에 접근할 수 있게 해줍니다
#    - user_id, session_id, 시간 등을 전달 가능
#    - 타입 힌트로 컨텍스트 구조를 명시: ToolRuntime[Context]
#
# 3. 순차 vs 병렬 도구 호출:
#    - 순차: 이전 결과가 다음 입력이 되는 경우
#    - 병렬: 독립적인 도구들을 동시 실행
#    - LLM이 자동으로 판단하여 결정
#
# 4. Agent 디버깅:
#    result["messages"]를 출력하여 모든 중간 단계를 확인하세요
#    각 메시지의 타입(HumanMessage, AIMessage, ToolMessage)을 체크하세요
#
# ============================================================================
