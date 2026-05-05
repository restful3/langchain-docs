"""1주차 §4.3 Model — LangChain 모델 객체 패턴.

원문: 03-customization_ko.md (LangChain 모델 객체 절)
교안: content/01_textbook.md §4.3

문자열 한 줄 대신 LangChain 모델 객체(ChatOllama 등)를 만들어 model= 로
통째로 넘기는 패턴. temperature, num_ctx 같은 세부 파라미터를 잡고 싶을 때
이 길로 간다.

사전 준비:
    ollama pull llama3.1   # 또는 .env 의 OLLAMA_MODEL 값

실행:
    python scripts/03_model_object_ollama.py
"""
from __future__ import annotations

import os

from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import init_chat_model

from deepagents import create_deep_agent

load_dotenv(find_dotenv())

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

# init_chat_model + provider 를 명시하면 ChatOllama 객체가 반환된다.
# (langchain-ollama 패키지가 설치돼 있어야 한다)
model = init_chat_model(
    model=OLLAMA_MODEL,
    model_provider="ollama",
    temperature=0,
)

agent = create_deep_agent(model=model)


def main() -> None:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Ollama, 안녕?"}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
