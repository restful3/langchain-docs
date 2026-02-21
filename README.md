# LangChain 생태계 한국어 학습 가이드

> LangChain, LangGraph, Deep Agents -- AI Agent 개발의 모든 것을 다루는 체계적인 한국어 교육 자료

LangChain 생태계의 핵심 프레임워크 3가지를 한국어로 학습할 수 있는 종합 교육 저장소입니다. 공식 문서 기반의 교안, 실행 가능한 예제 코드, 실전 프로젝트를 통해 AI Agent 개발 역량을 체계적으로 쌓을 수 있습니다.

---

## 저장소 구성

이 저장소는 세 개의 독립적인 교재로 구성되어 있으며, 각각 별도로 학습하거나 순서대로 진행할 수 있습니다.

```
langchain-docs/
├── langchain/       # LangChain AI Agent 마스터 교안
├── langgraph/       # LangGraph 완벽 가이드
└── deep-agents/     # Deep Agents 한국어 문서
```

---

## 1. LangChain AI Agent 마스터 교안

> **경로**: [`langchain/`](langchain/)

LangChain 1.0 기반 AI Agent 개발의 전 과정을 다루는 한국어 교안입니다. 공식 문서 34개를 100% 반영하였으며, 기초부터 프로덕션 배포까지 10개 파트로 구성되어 있습니다.

| 항목 | 내용 |
|------|------|
| 교안 | 10개 파트 + 부록 4개 |
| 예제 코드 | 132개 Python 파일 (전체 실행 가능) |
| 미니 프로젝트 | 4개 (날씨 비서, 문서 Q&A, 리서치 Agent, 고객 서비스) |
| 난이도 시스템 | 모든 예제에 1~5단계 난이도 표시 |
| 학습 시간 | 약 38~47시간 |

### 파트 구성

| 단계 | 파트 | 핵심 내용 |
|------|------|----------|
| 기초 | Part 1~3 | LangChain 개요, Chat Models, Tools, 첫 번째 Agent |
| 중급 | Part 4~6 | 메모리 시스템, 미들웨어/가드레일, 컨텍스트 엔지니어링 |
| 고급 | Part 7~8 | 멀티에이전트, RAG, MCP 통합 |
| 프로덕션 | Part 9~10 | 스트리밍, HITL, 테스트, LangSmith, 배포 |

상세 내용: [langchain/README.md](langchain/README.md)

---

## 2. LangGraph 완벽 가이드

> **경로**: [`langgraph/`](langgraph/)

LangGraph의 핵심 개념(State, Node, Edge)부터 프로덕션 배포까지 다루는 종합 가이드입니다. 5개 Part, 20개 Chapter로 구성되어 있으며, 5개의 완성 프로젝트 예제를 포함합니다.

| 항목 | 내용 |
|------|------|
| 교안 | 5개 Part, 20개 Chapter + 부록 3개 |
| 완성 프로젝트 | 5개 (Chatbot, Research Assistant, Multi-Agent Team, RAG Agent, Code Assistant) |
| 연습 문제 | 파트별 연습 문제 + 해답 |

### Part 구성

| Part | 제목 | 핵심 내용 |
|------|------|----------|
| Part 1 | Foundation | LangGraph 소개, 핵심 개념, State 관리 |
| Part 2 | Workflows | 워크플로우 패턴, 조건부 라우팅, 병렬 실행 |
| Part 3 | Agent | 도구/에이전트, ReAct Agent, Multi-Agent, 서브그래프 |
| Part 4 | Production | Persistence, 메모리, 스트리밍, HITL, Time Travel |
| Part 5 | Advanced | Functional API, Durable Execution, 배포 |

상세 내용: [langgraph/README.md](langgraph/README.md)

---

## 3. Deep Agents 한국어 문서

> **경로**: [`deep-agents/`](deep-agents/)

LangGraph 기반의 고급 에이전트 라이브러리인 Deep Agents의 공식 문서를 한국어로 번역한 자료입니다. 계획 수립, 서브에이전트, 파일 시스템 기반 컨텍스트 관리 등 복잡한 다단계 작업을 처리하는 에이전트 구축 방법을 다룹니다.

| 항목 | 내용 |
|------|------|
| 문서 | 10개 (영문 원본 + 한국어 번역 각각) |
| 핵심 주제 | 계획 수립, 서브에이전트, 파일 시스템, 장기 메모리, HITL |

### 핵심 역량

- **계획 및 작업 분해**: `write_todos` 도구를 통한 체계적 작업 관리
- **컨텍스트 관리**: 가상 파일 시스템을 통한 대규모 컨텍스트 처리
- **서브에이전트 위임**: 컨텍스트 격리와 병렬 실행
- **장기 메모리**: 스레드 간 영구 메모리 구현

상세 내용: [deep-agents/README.md](deep-agents/README.md)

---

## 권장 학습 순서

```
1. langchain/   -- LangChain 기초와 Agent 개발의 전체 흐름을 익힘
       |
2. langgraph/   -- 그래프 기반 워크플로우와 상태 관리를 심화 학습
       |
3. deep-agents/ -- 복잡한 다단계 에이전트 아키텍처를 학습
```

- **입문자**: `langchain/` Part 1~3 부터 시작
- **LangChain 경험자**: `langgraph/` 또는 관심 있는 `langchain/` 파트부터 시작
- **고급 사용자**: `deep-agents/`로 바로 진입 가능

---

## 요구사항

- **Python** 3.10+ (3.11 권장)
- **API 키**: OpenAI, Anthropic, Google AI 중 하나 이상
- **Docker**: PostgreSQL 연동 실습 시 필요 (선택)

---

## 빠른 시작

```bash
# 원하는 교재 디렉토리로 이동
cd langchain    # 또는 langgraph

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt  # langgraph의 경우
pip install -r src/requirements.txt  # langchain의 경우

# 환경변수 설정
cp .env.example .env
# .env 파일에 API 키 입력
```

---

## 라이선스

MIT License

- 공식 LangChain/LangGraph 문서 및 이미지는 별도 라이선스 적용
- 교육 목적 Fair Use 원칙 준수

---

## 관련 링크

- [LangChain 공식 문서](https://python.langchain.com/docs/introduction/)
- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [Deep Agents 공식 문서](https://langchain-ai.github.io/deep-agents/)
- [LangSmith](https://smith.langchain.com/)

---

*마지막 업데이트: 2025-02-21*
