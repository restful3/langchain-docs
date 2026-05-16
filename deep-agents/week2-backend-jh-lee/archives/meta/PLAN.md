# 구현 계획서 — 2주차 발표 자료 (Backends) v0

## 0. 산출물 (최종)

| 산출물 | 경로 | 분량 목표 |
| --- | --- | --- |
| 교과서 | `content/textbook.pdf` | A4 15~20p |
| 슬라이드 | `content/slides.pdf` | 22~25장 (미결정) |
| Walkthrough | `scripts/walkthrough.ipynb` | 4개 백엔드 데모 |
| SVG 다이어그램 | `content/figs/fig0[1-5]_*.svg` | 최소 5장 |

## 1. 폴더 구조 (확정)

week1 미러링 — README.md 의 트리 참조.

## 2. 워크플로우 (4단계)

| Phase | 목적 | 산출 | 상태 |
| --- | --- | --- | --- |
| Phase 1 | DESIGN — 목차·메시지·시각자료 명세 | `DESIGN.md` | ⏸ |
| Phase 2 | RESEARCH — 5~7건 보강자료 수집 | `research/INDEX.md` + N건 | ⏸ |
| Phase 3 | TEXTBOOK + SCRIPTS — 본문 + 데모 4종 | `source/01_textbook.md` + `scripts_py/*.py` | ⏸ |
| Phase 4 | SLIDES — 발표 자료 | `source/slides.md` + content/slides.pdf | ⏸ |

## 3. 텍스트북 섹션 안 (DESIGN 단계에서 확정)

```text
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

## 4. 데모 ↔ 섹션 매핑

| 데모 파일 | 매핑 섹션 | 시연 포인트 |
| --- | --- | --- |
| `01_state_backend.py` | §3 | thread 재개 시 잔존 / 다른 thread 에서 사라짐 |
| `02_filesystem_backend.py` | §4 | `virtual_mode` on/off 경로 차이 |
| `03_store_backend.py` | §5 | namespace 별 분리, thread-cross 영속 |
| `04_composite_backend.py` | §6 | 라우팅 규칙 3개 (`/tmp` → state, `/memories` → store, default → FS) |

## 5. Verify (Phase 별)

- Phase 1: DESIGN.md 의 목차·시각·메시지가 본 PLAN 과 모순 없는가
- Phase 2: research/INDEX.md 5~7건, verbatim 보존, URL·수집일 명시
- Phase 3: 텍스트북 코드 인용 라인 ↔ scripts_py 실파일 라인 일치 / 4개 데모 모두 실행 성공
- Phase 4: 슬라이드 ↔ 교안 메시지 매핑 표 (DESIGN.md 의 §4)

## 6. 남은 결정

- 슬라이드 분량 (22 vs 25)
- 실 LLM 호출 vs 모킹
- 가상 FS 예시: S3 / Postgres / 둘 다
