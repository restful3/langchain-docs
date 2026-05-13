# 구현 계획서 — 2주차 발표 자료

> 흐름: 위임 → 전문화 → 승인 → 재개 → 서브에이전트 승인  
> 청중: 1주차 Overview를 들은 LangChain 경험자  
> 산출물: 상세 교안 + 슬라이드 + 실행 스크립트

---

## 최종 산출물

| # | 산출물 | 경로 |
|---:|---|---|
| 1 | 상세 교안 | `archives/source/01_textbook.md` |
| 2 | 교안 HTML/PDF | `content/textbook.{html,pdf}` |
| 3 | 슬라이드 원본 | `archives/source/slides.md` |
| 4 | 슬라이드 HTML/PDF | `content/slides.{html,pdf}` |
| 5 | 실행 스크립트 + 가이드 | `scripts/*.py`, `scripts/README.md` |
| 6 | 원문 보관 | `archives/original_docs/06-subagents_ko.md`, `07-human-in-the-loop_ko.md` |

---

## 목차

1. 2주차 목표와 큰 그림
2. 왜 서브에이전트인가: 컨텍스트 비대화와 위임
3. SubAgent 구성: 필수 필드와 선택 필드
4. 일반 패턴: 범용, 전문, CompiledSubAgent
5. Human-in-the-loop 기본: `interrupt_on`, `MemorySaver`, `thread_id`
6. 승인 처리: `approve`, `edit`, `reject`, 여러 도구 호출
7. 서브에이전트와 승인 결합
8. 부록: 트러블슈팅, 실행 스크립트, 참고 문서

---

## 검증 기준

- 원문 06/07의 주요 섹션이 교안과 슬라이드에 모두 매핑된다.
- 스크립트 5종은 독립 실행 가능하며 `.env_sample` 패턴을 공유한다.
- HITL 예제는 `__interrupt__` 확인과 `Command(resume=...)` 재개 흐름을 보여준다.
- 시각자료는 SVG 파일로 보관하고 교안/슬라이드에서 같은 파일을 참조한다.
