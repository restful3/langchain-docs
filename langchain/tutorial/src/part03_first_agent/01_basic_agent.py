"""
================================================================================
LangChain AI Agent 마스터 교안
Part 3: 첫 번째 Agent
================================================================================

파일명: 01_basic_agent.py
난이도: ⭐⭐☆☆☆ (초급)
예상 시간: 30분

📚 학습 목표:
  - create_agent() API 이해
  - 첫 번째 Agent 만들기
  - Agent의 동작 원리 이해
  - System Prompt로 Agent 성격 커스터마이징
  - 역할 기반 페르소나 및 제약사항 설정

📖 공식 문서:
  • Agents: /official/06-agents.md
  • System Prompt: /official/06-agents.md (라인 242-283)
  • Quickstart: /official/03-quickstart.md

📄 교안 문서:
  • Part 3 개요: /docs/part03_first_agent.md (섹션 1, 4)

🚀 실행 방법:
  python 01_basic_agent.py

================================================================================
"""

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("❌ 오류: OPENAI_API_KEY가 설정되지 않았습니다.")
    print("📝 .env 파일을 확인하고 API 키를 설정하세요.")
    exit(1)

# ============================================================================
# 공통 도구 정의
# ============================================================================

@tool
def get_weather(city: str) -> str:
    """주어진 도시의 현재 날씨를 알려줍니다.

    Args:
        city: 도시 이름 (예: 서울, 부산, 뉴욕)
    """
    weather_info = {
        "서울": "맑음, 기온 22도, 습도 60%",
        "부산": "흐림, 기온 20도, 습도 70%",
        "뉴욕": "비, 기온 15도, 습도 85%",
        "파리": "맑음, 기온 18도, 습도 55%",
        "도쿄": "구름 많음, 기온 19도, 습도 65%",
    }
    weather = weather_info.get(city, f"{city}의 날씨 정보를 찾을 수 없습니다")
    return f"{city}의 현재 날씨: {weather}"


@tool
def calculate(expression: str) -> str:
    """수학 계산을 수행합니다.

    Args:
        expression: 계산식 (예: "2 + 2", "10 * 5")
    """
    try:
        # 보안 주의: 실제 프로덕션에서는 eval 사용 금지!
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"계산 오류: {str(e)}"


# ============================================================================
# 예제 1: 가장 간단한 Agent
# ============================================================================

def example_1_simple_agent():
    """가장 기본적인 Agent 생성 및 실행"""
    print("=" * 70)
    print("📌 예제 1: 가장 간단한 Agent")
    print("=" * 70)

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    tools = [get_weather, calculate]

    agent = create_agent(
        model=model,
        tools=tools,
    )

    print("\n🤖 Agent 생성 완료!")
    print(f"📋 사용 가능한 도구: {[t.name for t in tools]}")

    question = "서울 날씨는 어때?"
    print(f"\n👤 사용자: {question}")
    print("🤔 Agent가 생각하고 있습니다...\n")

    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })

    final_message = result["messages"][-1]
    print(f"🤖 Agent: {final_message.content}\n")


# ============================================================================
# 예제 2: Agent vs 일반 LLM 비교
# ============================================================================

def example_2_agent_vs_llm():
    """Agent와 일반 LLM의 차이 비교"""
    print("=" * 70)
    print("📌 예제 2: Agent vs 일반 LLM 비교")
    print("=" * 70)

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    question = "서울의 현재 날씨는?"

    # 일반 LLM (도구 없음)
    print("\n🔹 일반 LLM (도구 없음):")
    print(f"   👤 사용자: {question}")
    llm_response = model.invoke(question)
    print(f"   🤖 LLM: {llm_response.content}")

    # Agent (도구 있음)
    print("\n🔹 Agent (날씨 도구 있음):")
    print(f"   👤 사용자: {question}")
    agent = create_agent(model=model, tools=[get_weather])
    agent_response = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })
    final_message = agent_response["messages"][-1]
    print(f"   🤖 Agent: {final_message.content}")

    print("\n💡 Agent는 실제 도구를 사용하여 정확한 정보를 제공합니다!\n")


# ============================================================================
# 예제 3: Agent의 도구 사용 과정 관찰
# ============================================================================

def example_3_agent_reasoning():
    """Agent가 도구를 사용하는 과정 관찰"""
    print("=" * 70)
    print("📌 예제 3: Agent의 추론 과정 관찰")
    print("=" * 70)

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(
        model=model,
        tools=[get_weather, calculate],
        system_prompt="도구를 사용할 때마다 무엇을 하는지 설명하세요."
    )

    question = "서울과 도쿄의 평균 기온은 몇 도인가요?"
    print(f"\n👤 사용자: {question}")
    print("\n🔍 Agent의 추론 과정:\n")

    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })

    for msg in result["messages"]:
        role = msg.__class__.__name__
        if role == "HumanMessage":
            print(f"   👤 사용자: {msg.content}")
        elif role == "AIMessage":
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    print(f"   🔧 도구 호출: {tool_call['name']}({tool_call['args']})")
            elif msg.content:
                print(f"   🤖 Agent: {msg.content}")
        elif role == "ToolMessage":
            print(f"   ✅ 도구 결과: {msg.content}")

    print()


# ============================================================================
# 예제 4: Default vs Custom System Prompt 비교
# ============================================================================

def example_4_default_vs_custom():
    """System Prompt 없음 vs 있음 비교"""
    print("=" * 70)
    print("📌 예제 4: Default vs Custom System Prompt")
    print("=" * 70)

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    # Agent 1: System Prompt 없음 (기본)
    agent_default = create_agent(model=model, tools=[get_weather])

    # Agent 2: Custom System Prompt 있음
    agent_custom = create_agent(
        model=model,
        tools=[get_weather],
        system_prompt="""당신은 친근하고 다정한 날씨 안내원입니다.

항상 이모티콘을 사용하여 밝고 긍정적으로 답변하세요.
날씨가 좋으면 "외출하기 좋은 날씨네요!", 날씨가 나쁘면 "실내 활동을 추천드려요!" 같은 조언을 추가하세요."""
    )

    question = {"messages": [{"role": "user", "content": "서울 날씨 어때?"}]}

    print("\n🔹 Agent 1 (System Prompt 없음):")
    result1 = agent_default.invoke(question)
    print(f"답변: {result1['messages'][-1].content}")

    print("\n🔹 Agent 2 (Custom System Prompt):")
    result2 = agent_custom.invoke(question)
    print(f"답변: {result2['messages'][-1].content}")

    print("\n💡 핵심 차이:")
    print("  - Agent 1: 정보만 전달하는 중립적 답변")
    print("  - Agent 2: 친근하고 조언을 포함한 답변")
    print("  - System Prompt로 Agent의 성격이 완전히 달라집니다!\n")


# ============================================================================
# 예제 5: 역할 기반 Prompt (선생님, 과학자, 코미디언)
# ============================================================================

def example_5_role_based_prompts():
    """같은 도구, 다른 역할의 Agent들"""
    print("=" * 70)
    print("📌 예제 5: 역할 기반 Prompt - 3가지 페르소나")
    print("=" * 70)

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    teacher_prompt = """당신은 초등학교 선생님입니다.

성격:
- 아이들에게 설명하듯이 쉽고 친절하게 말합니다
- 어려운 용어는 피하고 비유를 많이 사용합니다
- "~구나", "~란다" 같은 부드러운 말투를 사용합니다

예시:
"온도가 22도란다. 반팔 입기 딱 좋은 날씨구나!" """

    scientist_prompt = """당신은 전문 기상학자입니다.

성격:
- 과학적이고 정확한 용어를 사용합니다
- 기온, 습도, 기압 등을 상세히 설명합니다
- 날씨 현상의 원인을 과학적으로 분석합니다

예시:
"현재 기온은 섭씨 22도이며, 상대습도는 60%입니다. 고기압의 영향으로..." """

    comedian_prompt = """당신은 유머러스한 코미디언입니다.

성격:
- 날씨를 재치있고 웃기게 표현합니다
- 말장난과 과장을 즐겨 사용합니다
- 긍정적이고 에너지 넘치는 톤입니다

예시:
"오늘 날씨는 '짱-창'해요! 태양님이 완전 '빛-나'고 계시네요!" """

    agent_teacher = create_agent(model, tools=[get_weather], system_prompt=teacher_prompt)
    agent_scientist = create_agent(model, tools=[get_weather], system_prompt=scientist_prompt)
    agent_comedian = create_agent(model, tools=[get_weather], system_prompt=comedian_prompt)

    question = {"messages": [{"role": "user", "content": "서울 날씨 알려줘"}]}

    print("\n👩‍🏫 선생님 Agent:")
    result1 = agent_teacher.invoke(question)
    print(f"{result1['messages'][-1].content}")

    print("\n🔬 기상학자 Agent:")
    result2 = agent_scientist.invoke(question)
    print(f"{result2['messages'][-1].content}")

    print("\n😄 코미디언 Agent:")
    result3 = agent_comedian.invoke(question)
    print(f"{result3['messages'][-1].content}")

    print("\n💡 핵심 포인트:")
    print("  - 같은 도구, 같은 데이터로 완전히 다른 답변!")
    print("  - System Prompt가 Agent의 '정체성'을 만듭니다")
    print("  - 타겟 사용자에 맞춰 적절한 페르소나를 선택하세요\n")


# ============================================================================
# 예제 6: 제약사항과 도메인별 전문 Prompt
# ============================================================================

def example_6_constraints_and_domain():
    """제약사항으로 Agent 행동 제어 + 도메인 전문 Prompt"""
    print("=" * 70)
    print("📌 예제 6: 제약사항과 도메인별 전문 Prompt")
    print("=" * 70)

    @tool
    def search_info(query: str) -> str:
        """정보를 검색합니다."""
        info_db = {
            "두통": "일반적인 원인: 스트레스, 수면 부족, 탈수. 권장 조치: 충분한 휴식과 수분 섭취.",
            "계약서": "계약서 작성 시 주의사항: 계약 당사자 명시, 계약 기간, 위약 조건 등을 명확히 기재.",
        }
        for key, value in info_db.items():
            if key in query:
                return value
        return f"'{query}'에 대한 정보를 찾을 수 없습니다"

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    # 의료 상담 Agent (제약사항 포함)
    medical_prompt = """당신은 의료 정보 제공 Agent입니다. (주의: 실제 진단은 불가)

역할:
- 일반적인 건강 정보를 제공합니다
- 증상에 대한 일반적인 원인을 설명합니다

응답 구조 (항상 따르세요):
1. 증상 확인: 사용자가 말한 증상 요약
2. 일반적 원인: 가능한 원인 2-3가지
3. 권장 조치: 집에서 할 수 있는 조치
4. 병원 방문: 병원에 가야 하는 경우 안내

⚠️ 중요한 제약:
- 절대 확정 진단을 하지 않습니다
- 모든 답변 끝에 "정확한 진단은 의사와 상담하세요"를 추가합니다
- 심각한 증상은 즉시 병원 방문을 권유합니다"""

    agent_medical = create_agent(model, tools=[search_info], system_prompt=medical_prompt)

    print("\n🏥 의료 상담 Agent (제약사항 적용):")
    print("👤 사용자: 두통이 있어요. 어떻게 해야 하나요?")
    result = agent_medical.invoke({"messages": [{"role": "user", "content": "두통이 있어요. 어떻게 해야 하나요?"}]})
    print(f"🤖 Agent:\n{result['messages'][-1].content}")

    print("\n💡 핵심 포인트:")
    print("  - 도메인별로 특화된 Prompt를 작성하세요")
    print("  - 응답 구조를 명시하면 일관된 품질을 유지할 수 있습니다")
    print("  - '절대 ~하지 않습니다' 같은 강력한 표현으로 제약사항을 명시하세요")
    print("  - 의료, 법률 등 민감한 분야에서 책임 제한 문구는 필수입니다\n")


# ============================================================================
# 메인 실행
# ============================================================================

def main():
    print("\n🎓 Part 3: Agent 기본과 System Prompt\n")

    example_1_simple_agent()
    input("⏎ 계속하려면 Enter...")

    example_2_agent_vs_llm()
    input("⏎ 계속하려면 Enter...")

    example_3_agent_reasoning()
    input("⏎ 계속하려면 Enter...")

    example_4_default_vs_custom()
    input("⏎ 계속하려면 Enter...")

    example_5_role_based_prompts()
    input("⏎ 계속하려면 Enter...")

    example_6_constraints_and_domain()

    print("=" * 70)
    print("🎉 Agent 기본과 System Prompt 학습 완료!")
    print("=" * 70)
    print("\n💡 주요 학습 내용:")
    print("   ✅ create_agent() API 사용법")
    print("   ✅ Agent에 도구 연결하기")
    print("   ✅ Agent vs 일반 LLM 차이")
    print("   ✅ System Prompt로 페르소나 지정")
    print("   ✅ 제약사항과 도메인별 전문 Prompt")
    print("\n📖 다음: 02_react_agent.py - ReAct 패턴과 날씨 Agent")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()


# ============================================================================
# 📚 핵심 포인트
# ============================================================================
#
# 1. create_agent()의 주요 파라미터:
#    - model: 사용할 LLM
#    - tools: Agent가 사용할 도구 리스트
#    - system_prompt: Agent의 역할 정의 (선택)
#
# 2. Agent의 작동 방식 (ReAct 패턴):
#    Thought (생각) → Action (도구 호출) → Observation (결과 관찰) → 반복
#
# 3. Agent vs 일반 LLM:
#    - LLM: 학습된 지식만 사용
#    - Agent: 도구를 사용하여 실시간 정보 접근 및 작업 수행
#
# 4. 좋은 System Prompt의 특징:
#    - 명확성: 역할과 책임이 분명함
#    - 구체성: "친절하게"보다 "초등학생에게 설명하듯이"
#    - 일관성: 응답 형식을 명시
#    - 안전성: 제약사항과 책임 제한 포함
#
# 5. Temperature 설정:
#    - 0.0: 일관적이고 결정적 (금융, 의료)
#    - 0.3~0.5: 균형잡힌 (일반적 사용)
#    - 0.7~1.0: 창의적 (마케팅, 크리에이티브)
#
# ============================================================================
