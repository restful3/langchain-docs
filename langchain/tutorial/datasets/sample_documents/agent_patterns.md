# AI Agent 디자인 패턴

## ReAct 패턴

**Reasoning + Acting**의 결합입니다.

### 작동 방식
1. **생각(Think)**: 현재 상황 분석
2. **행동(Act)**: 도구 호출
3. **관찰(Observe)**: 결과 확인
4. 반복

### 예시
```
생각: 서울 날씨를 알아야 한다
행동: get_weather("서울")
관찰: 서울은 맑고 22도다
생각: 사용자에게 날씨 정보를 전달하면 된다
답변: 서울은 현재 맑고 22도입니다
```

## Chain of Thought (CoT)

단계별 추론을 명시적으로 표현합니다.

### 장점
- 복잡한 문제 해결
- 추론 과정 추적 가능
- 오류 디버깅 용이

## Tool Use 패턴

### 도구 선택 전략
1. **명시적 매핑**: 특정 질문 → 특정 도구
2. **의미 기반**: 질문의 의도 파악
3. **다단계**: 여러 도구 순차 실행

## 멀티에이전트 패턴

### 1. Subagents (부하 패턴)
- 메인 Agent가 작업을 서브 Agent에 위임
- 각 서브 Agent는 전문화된 역할

```python
main_agent = create_agent(
    tools=[research_agent, writer_agent]
)
```

### 2. Handoffs (인계 패턴)
- Agent 간 제어권 전달
- 고객 서비스 → 전문가 → 관리자

### 3. Router (라우터 패턴)
- 입력 분석 후 적절한 Agent로 라우팅
- 티켓 분류, 의도 파악

### 4. Skills (온디맨드 패턴)
- 필요시에만 특정 기능 로드
- 메모리 효율적

## 메모리 패턴

### Short-term Memory
- 대화 내 메시지 기억
- 세션 단위 유지

### Long-term Memory
- 영구 저장소 (DB)
- 사용자 선호도, 이력

### Summarization
- 긴 대화를 요약
- 컨텍스트 윈도우 관리

## 가드레일 패턴

### Input Guardrails
- 부적절한 입력 필터링
- PII 감지

### Output Guardrails
- 유해 콘텐츠 차단
- 사실 확인

## Human-in-the-Loop (HITL)

### Approval
- 중요한 작업 전 승인 요청
- 예: 결제, 이메일 발송

### Correction
- Agent 응답을 사람이 수정
- 피드백 학습

## 스트리밍 패턴

### Token Streaming
- 실시간으로 토큰 전송
- 사용자 경험 향상

### Event Streaming
- 중간 단계 진행 상황 전송
- 투명성 제공

## 에러 처리 패턴

### Retry with Exponential Backoff
```python
@retry(max_attempts=3, backoff=2)
def call_api():
    # API 호출
    pass
```

### Fallback Strategy
- 주 모델 실패 시 대체 모델 사용
- GPT-4 → GPT-3.5

### Graceful Degradation
- 일부 기능 실패해도 계속 작동
- 필수 vs 선택적 기능 구분

## 최적화 패턴

### Prompt Caching
- 자주 사용하는 프롬프트 캐싱
- 비용 및 지연 시간 감소

### Batch Processing
- 여러 요청을 배치로 처리
- 처리량 증가

### Parallel Tool Calls
- 독립적인 도구를 동시 실행
- 총 실행 시간 단축

## 테스트 패턴

### Unit Tests
- 개별 도구 테스트
- 모의 객체 사용

### Integration Tests
- 전체 Agent 플로우 테스트
- 실제 API 사용

### Evaluation Sets
- 벤치마크 데이터셋
- 성능 측정

## 모니터링 패턴

### Observability
- LangSmith로 트레이싱
- 각 단계 시간 측정

### Logging
- 구조화된 로그
- 에러 추적

### Metrics
- 성공률, 응답 시간
- 토큰 사용량

## 참고 자료

- [LangChain Agents 문서](https://python.langchain.com/docs/concepts/agents/)
- [ReAct 논문](https://arxiv.org/abs/2210.03629)
- [Multi-Agent 패턴](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
