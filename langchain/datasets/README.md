# 교안 실습 데이터셋

> 📊 LangChain AI Agent 교안의 실습 예제에서 사용하는 데이터셋 모음

이 디렉토리는 교안의 실습 예제, 프로젝트, 평가에 사용되는 데이터셋을 포함합니다.

---

## 📋 목차

1. [디렉토리 구조](#-디렉토리-구조)
2. [데이터셋 사용 방법](#-데이터셋-사용-방법)
3. [파일 포맷](#-파일-포맷)
4. [데이터셋 통계](#-데이터셋-통계)
5. [라이선스](#-라이선스)

---

## 📁 디렉토리 구조

```
datasets/
├── README.md (이 파일)
├── sample_documents/          # RAG용 샘플 문서
│   ├── langchain_overview.md
│   ├── python_basics.md
│   ├── ai_ethics.md
│   ├── rag_fundamentals.md
│   ├── agent_patterns.md
│   ├── production_best_practices.md
│   └── prompt_engineering.md
│
├── test_conversations/         # Agent 테스트용 대화 데이터
│   ├── weather_queries.json
│   ├── customer_service.json
│   └── multi_turn_conversations.json
│
└── evaluation_sets/            # Agent 평가용 벤치마크
    ├── agent_benchmarks.json
    ├── rag_qa_pairs.json
    └── rag_qa_extended.json
```

---

## 📂 디렉토리별 설명

### 1. `sample_documents/` - RAG용 문서

**용도**: Part 8 (RAG와 MCP)에서 Vector Store 구축 및 문서 검색 실습

**파일 목록**:

| 파일명 | 형식 | 설명 | 사용 파트 |
|--------|------|------|----------|
| `langchain_overview.md` | Markdown | LangChain 개요 및 핵심 개념 | Part 8.1-8.3 |
| `python_basics.md` | Markdown | Python 프로그래밍 기초 | Part 8.2 |
| `ai_ethics.md` | Markdown | 인공지능 윤리 원칙 | Part 8.2 |
| `rag_fundamentals.md` | Markdown | RAG 기초 및 구현 방법 | Part 8.1-8.3 |
| `agent_patterns.md` | Markdown | AI Agent 디자인 패턴 | Part 3, 7 |
| `production_best_practices.md` | Markdown | 프로덕션 베스트 프랙티스 | Part 9, 10 |
| `prompt_engineering.md` | Markdown | 프롬프트 엔지니어링 가이드 | Part 6 |

**주제 분류**:
- LangChain/Agent: langchain_overview, agent_patterns, rag_fundamentals (3개)
- 개발 실무: production_best_practices, prompt_engineering (2개)
- 기초 지식: python_basics, ai_ethics (2개)

**예제 사용**:
```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# 모든 Markdown 파일 로드
loader = DirectoryLoader(
    "datasets/sample_documents/",
    glob="**/*.md",
    loader_cls=TextLoader
)
documents = loader.load()

print(f"로드된 문서 수: {len(documents)}")  # 7
```

---

### 2. `test_conversations/` - 테스트용 대화 데이터

**용도**: Agent 테스트, 메모리 시스템 실습, 평가

**파일 목록**:

| 파일명 | 레코드 수 | 설명 | 사용 파트 |
|--------|----------|------|----------|
| `weather_queries.json` | 10개 | 날씨 관련 질문 (단일/멀티턴) | Part 3 |
| `customer_service.json` | 5개 | 고객 서비스 시나리오 | Part 3, 4, 10 |
| `multi_turn_conversations.json` | 8개 | 다양한 주제 멀티턴 대화 (2-6턴) | Part 4 |

**주요 특징**:
- 다양한 난이도 (1-4)
- 주제별 분류
- 예상 응답 포함

**예제 사용**:
```python
import json

# JSON 파일 로드
with open("datasets/test_conversations/customer_service.json") as f:
    data = json.load(f)

# 대화 순회
for conv in data["conversations"]:
    conv_id = conv["id"]
    turns = conv["turns"]
    difficulty = conv["metadata"]["difficulty"]

    print(f"대화 ID: {conv_id}, 난이도: {difficulty}")

    for turn in turns:
        print(f"  {turn['role']}: {turn['content']}")
```

---

### 3. `evaluation_sets/` - 평가용 벤치마크

**용도**: Part 10 (배포와 관측성)에서 Agent 성능 평가

**파일 목록**:

| 파일명 | 레코드 수 | 설명 | 사용 파트 |
|--------|----------|------|----------|
| `agent_benchmarks.json` | 21개 | Agent 성능 평가 (다양한 카테고리) | Part 10.4 |
| `rag_qa_pairs.json` | 10개 | RAG 정확도 평가 (문서 기반 Q&A) | Part 8.3, 10.4 |
| `rag_qa_extended.json` | 10개 | 확장 RAG 평가 (키워드 기반) | Part 8.3, 10.4 |

**평가 메트릭**:
- 정확도 (Accuracy)
- 응답 시간 (Latency)
- 도구 사용 정확도 (Tool Calling Precision)
- 검색 적합성 (Retrieval Relevance)

**예제 사용**:
```python
import json

# 평가 데이터 로드
with open("datasets/evaluation_sets/agent_benchmarks.json") as f:
    benchmarks = json.load(f)

# Agent 평가
results = []
for item in benchmarks["test_cases"]:
    question = item["question"]

    # Agent 실행
    actual = agent.invoke({"messages": [{"role": "user", "content": question}]})
    actual_answer = actual["messages"][-1].content

    # 예상 답변이 있는 경우 비교
    if "expected_answer" in item:
        expected = item["expected_answer"]
        is_correct = expected.lower() in actual_answer.lower()
        results.append({"question": question, "correct": is_correct})

# 정확도 계산
accuracy = sum(r["correct"] for r in results) / len(results)
print(f"정확도: {accuracy:.2%}")
```

---

## 🔧 데이터셋 사용 방법

### Python에서 로드

#### 1. JSON 파일 로드
```python
import json

with open("datasets/test_conversations/customer_service.json") as f:
    data = json.load(f)

# 데이터 구조 확인
print(data.keys())  # ['conversations']
print(len(data["conversations"]))  # 5
```

#### 2. Markdown 파일 로드
```python
# 단일 파일
with open("datasets/sample_documents/langchain_overview.md") as f:
    content = f.read()

print(f"문서 길이: {len(content)} 글자")

# 여러 파일
import os

docs_dir = "datasets/sample_documents/"
for filename in os.listdir(docs_dir):
    if filename.endswith(".md"):
        filepath = os.path.join(docs_dir, filename)
        with open(filepath) as f:
            content = f.read()
            print(f"{filename}: {len(content)} 글자")
```

#### 3. LangChain DocumentLoader 사용
```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# 디렉토리 전체 로드
loader = DirectoryLoader(
    "datasets/sample_documents/",
    glob="**/*.md",
    loader_cls=TextLoader
)
documents = loader.load()

# 각 문서는 Document 객체
for doc in documents:
    print(doc.page_content[:100])  # 첫 100자
    print(doc.metadata)  # 파일 경로 등
```

---

### RAG 시스템에서 사용

```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1. 문서 로드
loader = DirectoryLoader(
    "datasets/sample_documents/",
    glob="**/*.md",
    loader_cls=TextLoader
)
documents = loader.load()

# 2. 문서 분할
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
splits = text_splitter.split_documents(documents)

# 3. Vector Store 생성
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# 4. 검색
retriever = vectorstore.as_retriever()
results = retriever.invoke("LangChain이란?")

for result in results:
    print(result.page_content)
```

---

## 📄 파일 포맷

### JSON 포맷 예시

#### `test_conversations/customer_service.json`
```json
{
  "conversations": [
    {
      "id": "cs_001",
      "category": "product_inquiry",
      "turns": [
        {"role": "user", "content": "이 제품 재고 있나요?"},
        {"role": "assistant", "content": "어떤 제품을 찾으시나요?"}
      ],
      "metadata": {"difficulty": 2}
    }
  ]
}
```

#### `evaluation_sets/agent_benchmarks.json`
```json
{
  "test_cases": [
    {
      "id": "bench_001",
      "category": "math",
      "question": "25 곱하기 4는 얼마인가요?",
      "expected_answer": "100",
      "expected_tool": "multiply",
      "difficulty": 1
    }
  ]
}
```

#### `evaluation_sets/rag_qa_pairs.json`
```json
{
  "qa_pairs": [
    {
      "id": "rag_001",
      "question": "LangChain은 누가 개발했나요?",
      "answer": "Harrison Chase",
      "source_document": "langchain_overview.md",
      "difficulty": 1
    }
  ]
}
```

---

## 📊 데이터셋 통계

### 전체 통계

| 카테고리 | 파일 수 | 총 레코드 수 | 설명 |
|---------|---------|------------|------|
| 샘플 문서 | 7개 | - | Markdown 문서 |
| 테스트 대화 | 3개 | 23개 | JSON 대화 데이터 |
| 평가 셋 | 3개 | 41개 | JSON 평가 데이터 |
| **합계** | **13개** | **64개** | - |

### 상세 통계

#### 샘플 문서 (`sample_documents/`)
- Markdown 파일: 7개
- 주제: LangChain, Python, AI 윤리, RAG, Agent 패턴, 프로덕션, 프롬프트

#### 테스트 대화 (`test_conversations/`)
- 총 대화 세션: 23개
- 평균 턴 수: 약 3.5턴
- 난이도 분포:
  - 난이도 1: 4개 (17%)
  - 난이도 2: 8개 (35%)
  - 난이도 3: 7개 (30%)
  - 난이도 4: 4개 (17%)

#### 평가 셋 (`evaluation_sets/`)
- 총 평가 항목: 41개
- Agent 벤치마크: 21개
- RAG Q&A 쌍: 10개
- RAG 확장 평가: 10개

---

## 🆕 데이터셋 추가 방법

### 자신만의 데이터셋 추가

#### 1. 문서 추가
```bash
# sample_documents/에 Markdown 파일 추가
cp your_document.md datasets/sample_documents/
```

#### 2. 대화 데이터 추가
```python
import json

# 기존 데이터 로드
with open("datasets/test_conversations/customer_service.json") as f:
    data = json.load(f)

# 새 대화 추가
new_conv = {
    "id": "cs_006",
    "category": "refund",
    "turns": [
        {"role": "user", "content": "환불 요청합니다"},
        {"role": "assistant", "content": "환불 사유를 알려주세요"}
    ],
    "metadata": {"difficulty": 2}
}
data["conversations"].append(new_conv)

# 저장
with open("datasets/test_conversations/customer_service.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

#### 3. 평가 셋 추가
```python
import json

with open("datasets/evaluation_sets/agent_benchmarks.json") as f:
    benchmarks = json.load(f)

new_benchmark = {
    "id": "bench_022",
    "category": "math",
    "question": "새로운 질문",
    "expected_answer": "예상 답변",
    "difficulty": 3
}
benchmarks["test_cases"].append(new_benchmark)

with open("datasets/evaluation_sets/agent_benchmarks.json", "w") as f:
    json.dump(benchmarks, f, indent=2, ensure_ascii=False)
```

---

## 📝 라이선스

### 데이터 출처 및 라이선스

| 파일/디렉토리 | 출처 | 라이선스 | 용도 |
|-------------|------|---------|------|
| `sample_documents/*.md` | 교안 자체 제작 | MIT | RAG 실습 |
| `test_conversations/*.json` | 교안 자체 제작 | MIT | Agent 테스트 |
| `evaluation_sets/*.json` | 교안 자체 제작 | MIT | 평가 |

### 사용 조건

모든 데이터셋은 **교육 목적**으로만 사용됩니다.

**허용**:
- 학습 및 실습
- 개인 프로젝트
- 연구 및 실험

**금지**:
- 상업적 재배포
- 데이터 판매
- 원본 출처 표기 없는 사용

---

## 🔗 관련 파트

| 데이터셋 | 사용 파트 | 파일 경로 |
|---------|----------|----------|
| 샘플 문서 | Part 8.1-8.3 | `docs/part08_rag_mcp.md` |
| 테스트 대화 | Part 3, 4 | `docs/part03_first_agent.md`, `docs/part04_memory.md` |
| 평가 셋 | Part 10.3-10.4 | `docs/part10_deployment.md` |

---

## ❓ FAQ

<details>
<summary>Q1: 데이터셋을 수정해도 되나요?</summary>

**A**: 네, 학습 목적으로 자유롭게 수정하셔도 됩니다. 단, 원본은 백업해두는 것을 권장합니다.
</details>

<details>
<summary>Q2: 더 많은 데이터가 필요한데 어디서 구할 수 있나요?</summary>

**A**: 다음 리소스를 활용하세요:
- [Hugging Face Datasets](https://huggingface.co/datasets)
- [Papers with Code Datasets](https://paperswithcode.com/datasets)
- [Kaggle Datasets](https://www.kaggle.com/datasets)
- 공개 데이터 포털 (data.go.kr 등)
</details>

<details>
<summary>Q3: 실제 프로덕션에서 이 데이터셋을 사용해도 되나요?</summary>

**A**: 이 데이터셋은 교육용입니다. 프로덕션에서는:
1. 실제 사용자 데이터 수집
2. 도메인 특화 데이터 준비
3. 라이선스 확인
4. 프라이버시 보호 (PII 제거)
</details>

---

*마지막 업데이트: 2025-02-18*
*버전: 1.1*
