# 디자인 — 2주차 발표 자료 (Backends) v1

> Phase 1 (DESIGN) **완료**. BRAINSTORM §9 결정 3건 반영.
> 확정 사항: 슬라이드 22장 / walkthrough 는 Ollama `gemma4:31b` / 가상 FS 예시는 S3 스타일.

## 1. 청중 프로파일

- week1 발표를 들은 사내 동료 (배경: Python / LangChain 입문 이상)
- `create_deep_agent()` 한 줄 시작은 익숙, 내부 추상화는 처음
- 로컬 GPU/Ollama 환경 보유 (gemma4:31b 구동 가능 가정)

## 2. 학습 목표

발표 후 청중이 할 수 있어야 하는 것:

- **L1**. 4종 백엔드의 차이(lifecycle / persistence / scope)를 한 표로 설명
- **L2**. 자신의 프로젝트에 맞는 백엔드를 선택
- **L3**. Composite 라우팅 규칙을 직접 작성
- **L4**. 자체 가상 FS 구현 시 `BackendProtocol` 의 어떤 메서드를 채워야 하는지 안다

## 3. 교안 목차 (TEXTBOOK 뼈대) — 10개 섹션 확정

```text
§0. 학습 목표
§1. 왜 백엔드인가 — ephemeral 데모의 한계
§2. Backend 프로토콜 — 인터페이스 한 장
§3. StateBackend — thread-scoped 휘발성
§4. FilesystemBackend — 로컬 디스크 + virtual_mode
§5. StoreBackend — LangGraph Store 영속
§6. Composite — 라우팅 규칙
§7. 직접 만들기 — S3 가상 FS 패턴
§8. Policy hooks — 권한·감사·redaction
§9. 선택 가이드 — 의사결정 표
§10. 다음 발제와의 연결 (harness / subagents)
```

## 4. 슬라이드 ↔ 교안 ↔ 학습목표 매핑 (22장 확정)

| # | 슬라이드 제목 | §교안 | 학습목표 | 핵심 메시지 |
| --- | --- | --- | --- | --- |
| 1 | 표지 | — | — | "Deep Agents — Backends 심층 · jh-lee · 2주차" |
| 2 | 한 줄 요약 | §0 | — | "백엔드 = 라우팅 가능한 가상 파일시스템 표면" |
| 3 | 왜 백엔드인가 (1) — ephemeral 의 한계 | §1 | L2 | week1 데모는 휘발·단일 thread |
| 4 | 왜 백엔드인가 (2) — 운영 환경 요구 | §1 | L2 | 영속·멀티 테넌트·권한·외부 저장소 |
| 5 | 4종 한 장 비교 | §3-§6 | L1 | lifecycle × persistence × scope (`fig01`) |
| 6 | Backend Protocol 다이어그램 | §2 | L4 | 6개 메서드 시그니처 |
| 7 | StateBackend — 개념 | §3 | L1,L2 | thread-scoped 휘발, checkpoint 동행 (`fig02`) |
| 8 | StateBackend — 데모 | §3 | L1 | 같은 thread 잔존 / 다른 thread 부재 |
| 9 | FilesystemBackend — 개념 | §4 | L1,L2 | root_dir + virtual_mode 정규화 (`fig03`) |
| 10 | FilesystemBackend — 데모 | §4 | L1 | virtual_mode on/off 호스트 디스크 비교 |
| 11 | StoreBackend — 개념 | §5 | L1,L2 | LangGraph BaseStore, thread-cross (`fig04`) |
| 12 | StoreBackend — 데모 | §5 | L1 | 다른 thread 에서 같은 파일 read |
| 13 | Composite — 개념 | §6 | L1,L3 | 라우팅 규칙, longer prefix wins (`fig05`) |
| 14 | Composite — 데모 | §6 | L3 | `/memories/*`, `/shared/*`, default 3개 동시 |
| 15 | Virtual FS — 왜 직접 만드나 | §7 | L4 | 외부 저장소(S3) 를 가상 표면으로 |
| 16 | Virtual FS — S3 스타일 패턴 | §7 | L4 | `BackendProtocol` 6개 메서드 구현 스켈레톤 |
| 17 | Policy hooks — 개념 | §8 | — | 권한·감사·redaction 3축 |
| 18 | Policy hooks — `GuardedBackend` 예시 | §8 | — | 서브클래싱 패턴 (`deny_prefixes`) |
| 19 | 선택 가이드 — 의사결정 표 | §9 | L2 | 시나리오 ↔ 추천 백엔드 |
| 20 | 다음 발제로의 다리 | §10 | — | harness / subagents 연결 |
| 21 | Q&A | — | — | 자유 토론 |
| 22 | (백업) Backend Protocol 전체 시그니처 | §2 | L4 | 풀 시그니처 표 — 시간 남을 때 |

- 발표 시간 20분 기준 = 슬라이드당 ~55초 페이스.
- 데모 슬라이드(#8, #10, #12, #14) 는 노트북 화면 전환을 포함하므로 ~90초씩 잡고, 나머지에서 압축.

## 5. 핵심 메시지 (한 문장)

> "백엔드는 에이전트의 가상 파일시스템 표면이며, 4종 built-in + Composite 라우팅 + Protocol 준수로 ephemeral 데모부터 멀티 테넌트 운영까지 한 코드로 확장된다."

## 6. 포함 / 제외 정책

### 포함 (확정)

- 4종 built-in 백엔드 (State / Filesystem / Store / Composite)
- `Backend` Protocol 인터페이스 한 장 + 6개 메서드 시그니처
- 가상 FS 구현 패턴 — **S3 스타일 1개** (Postgres 는 제외)
- Policy hooks — `GuardedBackend` 서브클래싱 1개 예시
- Composite 라우팅 3개 규칙 동시 운영 데모

### 제외 (다음 발제로 미룬다)

- Subagent 격리 (06-subagents)
- Harness 실행 모델 (04-harness)
- Sandbox / Local shell / LangSmith 백엔드 (시간 남으면 백업 슬라이드)
- Postgres 가상 FS — S3 와 패턴 중복, 시간 부족

## 7. 시각자료 명세 (5장 + 보조)

| 파일 | 슬라이드 # | 용도 | 출처 |
| --- | --- | --- | --- |
| `fig01_four_backends_overview.svg` | #5 | 4종 한 장 비교 (lifecycle × persistence × scope 축) | 직접 작성 |
| `fig02_state_lifecycle.svg` | #7 | thread checkpoint 흐름 | 직접 작성 |
| `fig03_filesystem_mount.svg` | #9 | virtual_mode 경로 정규화 | 직접 작성 |
| `fig04_store_namespace.svg` | #11 | Store namespace 트리 | 직접 작성 |
| `fig05_composite_routing.svg` | #13 | 라우팅 규칙 시각화 (mermaid → svg) | 직접 작성 (`05-backends.md` mermaid 보강) |

## 8. 용어 · 표기 가이드

### 용어 (한글 우선, 첫 등장 시 영문 병기)

- 백엔드 (backend)
- 가상 파일시스템 (virtual filesystem)
- 영속 (persistence)
- 휘발 (ephemeral)
- 라우팅 (routing)

### 코드폰트 고정

- 클래스명: `StateBackend`, `FilesystemBackend`, `StoreBackend`, `CompositeBackend`, `BackendProtocol`
- 도구명: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`
- 메서드명: `ls_info`, `read`, `write`, `edit`, `glob_info`, `grep_raw`
- 환경변수: `OLLAMA_MODEL`, `OLLAMA_BASE_URL`

### 한국어 번역 룰

- "deep agent" → "deep agent" (소문자 유지) 또는 "Deep Agent" (고유명사 취급)
- "Composite" → "Composite" (클래스명 유지)
- "State / Store" → 한글 번역 안 함 (혼란 방지)

### 마크다운 표기 규칙

- 영문↔한글 사이 띄어쓰기 1칸 (CJK 룰)
- 코드 블록은 언어 ID 명시 (`python`, `bash`, `text`)

## 9. Phase 2 검색 주제 우선순위 (RESEARCH)

DESIGN 확정에 따라 다음 수집 후보 재정렬:

1. LangGraph Store 공식 문서 — §5 보강
2. `deepagents/backends/protocol.py` 전체 시그니처 — §2 (이미 로컬 스냅샷)
3. **S3 가상 FS 사례** — §7 (boto3 + BackendProtocol 결합 예시 1~2건)
4. Policy hooks 사례 — §8 (RBAC 또는 redaction 1건)
5. (선택) Ollama gemma4:31b 도구 호출 안정성 — `walkthrough.ipynb` 사전 검증용

## 10. Verify 체크리스트 (Phase 1 종료 기준)

- [x] §3 목차가 PLAN.md 와 일치 (10개 §)
- [x] §4 매핑표 22장 완성 + 학습목표 L1~L4 모두 한 번 이상 등장
- [x] §6 포함/제외가 분량 안에 들어맞는지 추정 (20분 / 22장 / 데모 4개 = ok)
- [x] §7 시각자료 5장이 발표 흐름에 한 번씩 자리잡음
- [x] BRAINSTORM §9 결정 3건 모두 해소

## 11. Phase 2 진입 조건

- 본 문서 사용자 검토 통과 시 `archives/meta/STATUS.md` 의 Phase 1 게이지를 ✅ 로 마킹
- Phase 2 액션은 `NEXT_SESSION_PROMPT.md` 의 갱신본 참조
