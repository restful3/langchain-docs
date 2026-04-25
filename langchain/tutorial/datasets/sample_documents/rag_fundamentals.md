# RAG (Retrieval Augmented Generation) 기초

## 소개

RAG는 대규모 언어 모델(LLM)의 지식을 외부 문서로 확장하는 기술입니다.

## RAG의 작동 원리

### 1. 문서 처리
- 문서를 작은 청크로 분할
- 각 청크를 벡터로 변환 (임베딩)
- 벡터 데이터베이스에 저장

### 2. 검색 단계
사용자 질문이 들어오면:
1. 질문을 벡터로 변환
2. 유사한 문서 청크 검색
3. 관련성 높은 청크를 선택

### 3. 생성 단계
- 검색된 문서를 컨텍스트로 제공
- LLM이 컨텍스트를 참고하여 답변 생성
- 환각(hallucination) 감소

## RAG의 장점

1. **최신 정보**: 모델 학습 이후의 정보도 활용 가능
2. **도메인 특화**: 특정 분야의 전문 지식 제공
3. **투명성**: 답변의 출처를 추적 가능
4. **비용 효율**: 전체 모델을 재학습할 필요 없음

## 구현 예시 (LangChain)

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# 벡터 저장소 생성
vectorstore = Chroma.from_documents(documents, OpenAIEmbeddings())

# RAG 체인 구성 (LCEL 방식)
retriever = vectorstore.as_retriever()

prompt = ChatPromptTemplate.from_template(
    "다음 문서를 참고하여 질문에 답하세요:\n{context}\n\n질문: {question}"
)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | ChatOpenAI()
)

# 질문
result = chain.invoke("RAG가 무엇인가요?")
```

## 주요 구성 요소

### 벡터 데이터베이스
- Chroma
- Pinecone
- Weaviate
- FAISS

### 임베딩 모델
- OpenAI Embeddings
- HuggingFace Embeddings
- Sentence Transformers

## 모범 사례

1. **청크 크기**: 500-1000 토큰이 적절
2. **오버랩**: 청크 간 50-100 토큰 중복
3. **메타데이터**: 출처, 날짜 등 추가 정보 포함
4. **하이브리드 검색**: 키워드 + 벡터 검색 결합

## 한계와 해결책

### 한계
- 검색 품질에 의존
- 긴 문서 처리 어려움
- 컨텍스트 윈도우 제한

### 해결책
- 다단계 검색 (HyDE)
- 리랭킹 (Reranking)
- 문서 요약 활용

## Agentic RAG

Agent가 검색 전략을 결정하는 고급 RAG:
- 여러 소스 동시 검색
- 반복적 검색
- 결과 검증

## 참고 자료

- [LangChain RAG 튜토리얼](https://python.langchain.com/docs/tutorials/rag/)
- [RAG 원본 논문](https://arxiv.org/abs/2005.11401)
