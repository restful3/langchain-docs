# 발표 브레인스토밍 — 2주차 / jh-lee (Backends)

## 1. 청중과 역할 재정의

- **누가 듣는가**: week1 을 들은 동료. `create_deep_agent()` 한 줄 시작은 알지만 내부 파일시스템 추상화는 처음.
- **왜 듣는가**: ephemeral 데모를 운영 환경(영속·멀티 테넌트·보안)으로 옮길 때 어디를 손대야 하는지.
- **떠나면서 가져갈 것**: "백엔드 = 라우팅 가능한 가상 파일시스템" 한 문장 + 4종 백엔드 선택 기준 표.

## 2. 다섯 페르소나 관점

### (a) 교육자 — "어떻게 click 시킬까"
- 디스크/메모리/DB 비유로 시작. "에이전트도 똑같다, 어디에 쓰고 읽느냐의 문제."
- mermaid 라우팅 다이어그램은 슬라이드 1장에 박는 게 가장 효과적.

### (b) 아키텍트 — "시스템 위치"
- `Backend` 프로토콜은 LangGraph runtime 과 tool 사이의 인터페이스 계층.
- Backend 갈아끼기 = 같은 에이전트 코드를 dev/staging/prod 로 옮기는 방법.

### (c) 실무자 — "내가 뭘 할 수 있나"
- "S3/Postgres 가상 FS 구현 가능"이 강력한 훅. 실제 코드 패턴 한 장 제시.
- Policy hooks 로 권한·감사·redaction 추가.

### (d) 회의론자 — "그냥 디스크 쓰면 안 되나"
- 답: 멀티 테넌트 격리, thread-scoped 휘발성, 영속 메모리 — 한 가지로 안 됨. 그래서 Composite.

### (e) 스토리텔러 — "왜 지금"
- DeepAgents 가 "agent 의 운영체제 표면"을 표준화하려는 시도. 백엔드는 그 핵심.

## 3. 발표 구성 — 3개 안

### 안 A: **문제 주도형 (추천)** — "내 에이전트를 운영에 올리려면?"
1. ephemeral 데모의 한계 (week1 의 예시)
2. 백엔드 추상화 = 해결책
3. 4종 built-in 비교 (State/FS/Store/Composite)
4. virtual FS 직접 만들기 (Protocol 준수)
5. Policy hooks 로 권한·감사

### 안 B: 도큐먼트 순서형
- 05-backends.md 의 목차를 그대로 따라감. 안전하지만 지루.

### 안 C: 데모 우선형
- 4개 데모 먼저 → 사후에 추상화 설명. 시간 부족 위험.

## 4. 슬라이드/시각 아이디어 풀

- `fig01`: 4 backends 한 장 비교 (lifecycle/persistence/scope 축)
- `fig02`: State lifecycle (thread checkpoint 흐름)
- `fig03`: Filesystem mount + virtual_mode 경로 정규화
- `fig04`: Store namespace 트리 + 영속성 도표
- `fig05`: Composite routing rules — `/memories/* → Store`, `/tmp/* → State`, default → FS
- (선택) `fig06`: Backend Protocol 인터페이스 시그니처

## 5. 데모/코드 아이디어

1. `01_state_backend.py` — write/read 후 thread 재개 시 잔존 확인
2. `02_filesystem_backend.py` — `root_dir` sandbox + `virtual_mode=True` 경로 변환
3. `03_store_backend.py` — namespace 별 분리 + 다른 thread 에서 read
4. `04_composite_backend.py` — 라우팅 규칙 3개 동시 운영

## 6. 빠뜨리면 안 되는 포인트

- 모든 백엔드는 같은 도구(`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`) 인터페이스를 노출 — 에이전트 코드는 안 바뀐다.
- `root_dir` 은 반드시 절대경로.
- StoreBackend 는 thread-cross 가능 (장기 메모리).
- Policy hook 으로 path-level 권한·감사 가능.

## 7. 표기/용어 일관성

- "백엔드" (한글), 코드폰트로 `Backend` 프로토콜 / `StateBackend` 등 구체 클래스.
- "가상 파일시스템" = virtual filesystem (병기 1회).

## 8. 다음 발제와의 다리 (마지막 30초)

- "다음은 04-harness 또는 06-subagents — 백엔드 위에 격리된 워커가 어떻게 자기 컨텍스트를 가지는지."

## 9. 결정 필요 사항 (사용자 답변 요청) — ✅ 해결 (2026-05-15)

- [x] 슬라이드 분량 → **22장 확정** (DESIGN.md §4 매핑표 참조)
- [x] walkthrough 시연 → **Ollama `gemma4:31b` 실 LLM 호출** (OpenAI 의존 제거)
- [x] virtual FS 예시 → **S3 스타일** (§7) ; Postgres 는 제외

## 10. 다음 액션 후보

1. PLAN.md 채우기 (섹션 분할 확정)
2. research/ 수집 (LangGraph Store, S3 가상 FS 사례)
3. 데모 4종 prototyping (실 LLM 키 필요)
