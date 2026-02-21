# 리뷰 프로세스 가이드

> langchain/ 교재의 파트별 리뷰를 위한 가이드입니다.

## 리뷰 일정

주 1파트씩, Part 2부터 진행합니다.

| 주차 | 파트 | 리뷰어 | 리뷰 대상 |
|------|------|--------|-----------|
| 1주 | Part 2: LangChain 기초 | S종훈, L종훈 | `docs/part02_fundamentals.md` + `src/part02_fundamentals/` |
| 2주 | Part 3: 첫 번째 Agent | L종훈, S종훈 | `docs/part03_first_agent.md` + `src/part03_first_agent/` |
| 3주 | Part 4: 메모리 시스템 | 재익, 우석 | `docs/part04_memory.md` + `src/part04_memory/` |
| 4주 | Part 5: 미들웨어 | 우석, 재익 | `docs/part05_middleware.md` + `src/part05_middleware/` |
| 5주 | Part 6: 컨텍스트와 런타임 | 보현, 태호 | `docs/part06_context.md` + `src/part06_context/` |
| 6주 | Part 7: 멀티에이전트 시스템 | 태호, 보현 | `docs/part07_multi_agent.md` + `src/part07_multi_agent/` |
| 7주 | Part 8: RAG와 MCP | C성진, 태호 | `docs/part08_rag_mcp.md` + `src/part08_rag_mcp/` |
| 8주 | Part 9: 프로덕션 | C성진, S종훈 | `docs/part09_production.md` + `src/part09_production/` |
| 9주 | Part 10: 배포와 관측성 | L종훈 | `docs/part10_deployment.md` + `src/part10_deployment/` |

## 주간 사이클

```
월~금 (스터디 전)    1. 리뷰어가 review_이름.md 작성 후 git push
토 스터디 회의       2. 리뷰 논의 -> decisions.md 작성
토~일 (스터디 후)    3. 편집자가 agent_requests.md 정리 (요청별 검증 체크리스트 포함)
                     4. 코딩에이전트 실행
                     5. 요청별 검증 체크리스트 확인 + 최종 확인 수행
                     6. 검증 통과 시 push
```

## 리뷰어 가이드

### 1. 리뷰 파일 작성

`TEMPLATE.md`를 복사하여 해당 파트 폴더에 `review_이름.md`로 저장합니다.

```bash
# 예시: Part 2 리뷰어 S종훈
cp reviews/TEMPLATE.md reviews/part02_fundamentals/review_S종훈.md

# 리뷰 작성 후 push
git add reviews/part02_fundamentals/review_S종훈.md
git commit -m "Part 2 리뷰: S종훈"
git push
```

### 2. 리뷰 범위

각 파트의 리뷰 대상은 두 가지입니다:

- **교안**: `docs/partXX_*.md` -- 개념 설명, 코드 해설, 실습 과제
- **예제 코드**: `src/partXX_*/` -- 실행 가능한 Python 예제

### 3. 리뷰 항목 분류

| 분류 | 설명 | 예시 |
|------|------|------|
| **오류/수정** | 반드시 고쳐야 할 문제 | 오타, 잘못된 코드, deprecated API, 링크 깨짐 |
| **개선 제안** | 논의 후 결정할 사항 | 설명 보충, 예제 추가, 구조 변경, 난이도 조정 |

### 4. 피드백 작성 팁

- 수정이 필요한 위치를 **라인 번호** 또는 **섹션 번호**로 명시해 주세요
- 코드 수정의 경우 **현재 코드**와 **제안 코드**를 함께 적어 주시면 반영이 빠릅니다
- 큰 변경이 필요한 경우 이유와 함께 구체적인 방향을 적어 주세요

## 폴더 구조

```
reviews/
├── README.md                     # 이 파일
├── TEMPLATE.md                   # 리뷰 작성 템플릿
├── AGENT_REQUESTS_TEMPLATE.md    # 에이전트 요청 템플릿 (검증 체크리스트 포함)
├── part02_fundamentals/
│   ├── review_이름.md            # 리뷰어별 피드백 (리뷰어가 push)
│   ├── decisions.md              # 스터디 회의 후 확정사항 (편집자 작성)
│   └── agent_requests.md         # 에이전트 요청 + 검증 체크리스트 (편집자 작성)
├── part03_first_agent/
│   └── ...
└── ...
```

## 역할

| 역할 | 담당 | 작성 파일 |
|------|------|-----------|
| 리뷰어 | 배정된 스터디원 | `review_이름.md` |
| 편집자 | 교재 관리자 | `decisions.md`, `agent_requests.md` |

## 에이전트 요청 및 검증 가이드 (편집자용)

### agent_requests.md 작성

`AGENT_REQUESTS_TEMPLATE.md`를 복사하여 해당 파트 폴더에 `agent_requests.md`로 작성합니다.

각 요청에는 다음을 포함합니다:

- **대상 파일 경로**: 정확한 상대 경로
- **수정 위치**: 라인 번호 또는 섹션 번호
- **현재/변경**: 현재 내용과 변경할 내용을 명시
- **검증 체크리스트**: 해당 요청의 결과를 어떻게 확인할지

### 검증 절차

에이전트 실행 후 다음 순서로 검증합니다:

1. **요청별 검증**: 각 요청의 체크리스트 항목을 하나씩 확인
2. **최종 확인**: 모든 요청 반영 후 전체 검증 수행
   - 교안 통독하여 흐름 확인
   - 예제 코드 `python -m py_compile` 통과 여부
   - `decisions.md` 확정 항목과 대조하여 누락 없는지 확인
   - `git diff`로 변경 사항 최종 리뷰
3. **검증 통과 시** push, 미통과 시 에이전트에게 재요청
