# AI Agent 프로덕션 베스트 프랙티스

## 보안

### API 키 관리
```python
# ❌ 하드코딩하지 마세요
api_key = "sk-proj-abc123..."

# ✅ 환경변수 사용
import os
api_key = os.getenv("OPENAI_API_KEY")

# ✅ 비밀 관리 서비스
from aws_secretsmanager import get_secret
api_key = get_secret("openai-key")
```

### 입력 검증
```python
from pydantic import BaseModel, validator

class UserQuery(BaseModel):
    text: str

    @validator('text')
    def check_length(cls, v):
        if len(v) > 1000:
            raise ValueError('질문이 너무 깁니다')
        return v
```

### 출력 검증
- PII (개인식별정보) 마스킹
- 유해 콘텐츠 필터링
- 사실 확인

## 성능 최적화

### 1. 프롬프트 캐싱
```python
# Anthropic의 Prompt Caching
system_prompt = """
매우 긴 시스템 프롬프트...
""" # 이 부분이 캐시됨
```

### 2. 모델 선택
- **개발**: gpt-4o-mini (빠르고 저렴)
- **프로덕션**: claude-sonnet-4-5-20250929 (안정적)
- **내부 툴**: gpt-3.5-turbo (경제적)

### 3. 스트리밍
```python
for chunk in agent.stream(input):
    print(chunk, end="", flush=True)
```

### 4. 배치 처리
```python
# 여러 요청을 한번에
results = await agent.batch([
    {"input": "query1"},
    {"input": "query2"},
])
```

## 에러 처리

### Retry 전략
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def call_llm():
    return llm.invoke(prompt)
```

### Fallback
```python
try:
    result = expensive_model.invoke(input)
except Exception:
    result = cheap_model.invoke(input)
```

### Circuit Breaker
```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@breaker
def call_external_api():
    pass
```

## 모니터링

### 1. LangSmith 트레이싱
```python
import os
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "your-key"
```

### 2. 메트릭 수집
```python
import time
import prometheus_client

latency = prometheus_client.Histogram('agent_latency_seconds')

@latency.time()
def run_agent(input):
    return agent.invoke(input)
```

### 3. 로깅
```python
import logging
import structlog

logger = structlog.get_logger()

logger.info(
    "agent_invoked",
    user_id="user123",
    input_length=len(input),
    model="gpt-4o-mini"
)
```

## 비용 관리

### 1. 토큰 추적
```python
from langchain.callbacks import get_openai_callback

with get_openai_callback() as cb:
    result = agent.invoke(input)
    print(f"토큰 사용: {cb.total_tokens}")
    print(f"비용: ${cb.total_cost:.4f}")
```

### 2. 예산 설정
```python
MAX_TOKENS_PER_REQUEST = 4000

if len(input_tokens) > MAX_TOKENS_PER_REQUEST:
    raise ValueError("토큰 한도 초과")
```

### 3. 캐싱으로 절약
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_embedding(text: str):
    return embeddings.embed_query(text)
```

## 확장성

### 1. 로드 밸런싱
```nginx
upstream agent_backend {
    server agent1.example.com;
    server agent2.example.com;
    server agent3.example.com;
}
```

### 2. 비동기 처리
```python
import asyncio

async def run_agents_parallel(inputs):
    tasks = [agent.ainvoke(inp) for inp in inputs]
    return await asyncio.gather(*tasks)
```

### 3. 큐 시스템
```python
from celery import Celery

app = Celery('agent_tasks')

@app.task
def process_query(query):
    return agent.invoke(query)

# 비동기 실행
task = process_query.delay("질문")
```

## 테스트

### 단위 테스트
```python
def test_weather_tool():
    result = get_weather.invoke({"city": "Seoul"})
    assert "Seoul" in result
    assert "°C" in result
```

### 통합 테스트
```python
def test_agent_flow():
    result = agent.invoke({
        "messages": [{"role": "user", "content": "서울 날씨"}]
    })
    assert result["messages"][-1].content
```

### 평가
```python
from langsmith import evaluate

dataset = load_dataset("weather_qa")
results = evaluate(agent, dataset)
print(f"정확도: {results.accuracy}")
```

## 배포

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent
  template:
    metadata:
      labels:
        app: agent
    spec:
      containers:
      - name: agent
        image: agent:latest
        resources:
          limits:
            memory: "2Gi"
            cpu: "1"
```

### 환경 분리
- **개발**: 테스트 API 키, 작은 모델
- **스테이징**: 실제 API 키, 전체 테스트
- **프로덕션**: 모니터링 완비, 오토스케일링

## 유지보수

### 버전 관리
```python
# 모델 버전 고정
model = ChatOpenAI(model="gpt-4-0613")  # 특정 버전

# 라이브러리 버전 고정
# requirements.txt
langchain>=0.3.14
langchain-openai>=0.3.0
```

### 마이그레이션
```python
# 점진적 롤아웃
def get_agent(user_id: str):
    if user_id in beta_users:
        return new_agent
    else:
        return old_agent
```

### 백업
```python
import json
from datetime import datetime

def backup_conversation(conversation):
    filename = f"backup_{datetime.now()}.json"
    with open(filename, 'w') as f:
        json.dump(conversation, f)
```

## 체크리스트

배포 전 확인 사항:

- [ ] API 키가 환경변수로 관리됨
- [ ] 에러 처리가 구현됨
- [ ] 로깅이 설정됨
- [ ] 모니터링 대시보드 준비
- [ ] 비용 알림 설정
- [ ] 백업 전략 수립
- [ ] 롤백 계획 준비
- [ ] 부하 테스트 완료
- [ ] 보안 감사 완료
- [ ] 문서화 완료

## 참고 자료

- [LangChain Production Guide](https://python.langchain.com/docs/concepts/)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/production-best-practices)
- [LangSmith Documentation](https://docs.smith.langchain.com/observability)
