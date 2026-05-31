# 그림(SVG) Codex 리뷰 — 결정 및 변경 (Claude)

대상: `content/figs/*.svg` + `content/01_textbook.md` · Codex 리뷰: `2026-05-30-figures-codex.md`
결과: Critical 0 · Major 0 · Minor 4 · Nit 3

## ACCEPT (반영)

| # | 항목 | 변경 |
|---|---|---|
| Minor 1 | fig 이메일그래프 `human_review` 중복 | 캡션에 "같은 노드를 두 진입 경로(분류 직후 에스컬레이션·초안 후 검토)로 나눠 그린 단순화" 명시 |
| Minor 2 | fig interrupt/resume 의 resume 주체 모호 | `Command(resume=)` 박스 하단을 "같은 thread_id 로 호출" 로, 캡션을 "외부 호출자가 같은 thread_id 로 호출하면 런타임이 체크포인트를 조회해 재개" 로 정정 |
| Minor 3 | fig granularity "search 만 재실행" 단정 | SVG 라벨 "search 만"→삭제, "체크포인트 보존"→"이전 checkpoint 보존" 으로 완화 |
| Minor 4 | fig local "등록" 라벨 | 화살표 라벨 "등록"→"로드" (langgraph dev 가 langgraph.json 을 읽어 로드) |
| Nit 7 | 그림 번호가 문서 등장 순서와 역전 | 5단계 파이프라인=그림 2, 이메일 그래프=그림 3 으로 스왑 (파일명도 fig02/fig03 교체) |

## 사용자 추가 지시 동시 반영

- **SVG 내 제목·캡션 제거** — fig01 "TypedDict·모든 노드가…" / fig07 thread_id 설명문 / fig08 "끝에서 실패→전부 재실행"·"search 실패→…" 등 캡션성 문장 삭제. 식별 라벨·핵심 키워드(:2024, interrupt(), state→update 등)는 CLAUDE.md 허용 범위로 유지.
- **그림·표 번호 통일** — 그림 1\~9 / 표 1\~9 를 각각 독립 시퀀스로 문서 순서대로 `**그림 N.**`·`**표 N.**` 형식 부착 (표 9개 신규 부착).

## REJECT / 유지

| 항목 | 사유 |
|---|---|
| Nit 5 (박스 내 설명 라벨 전면 제거) | fig04 유형 정의·fig09 ":2024 개발용" 등은 다이어그램 식별 키워드(CLAUDE.md 허용). 전면 제거 시 그림이 무의미해짐. 캡션성 "문장"만 제거 |
| Nit 6 (fig01 단방향 읽기/쓰기) | 캡션이 "모든 노드가 읽고 쓴다" 로 보완. 단방향 데모가 읽기·쓰기 두 동작을 더 명확히 보여줌 |

## 검증

- SVG XML 9/9 유효, HTML 재빌드 52KB, 그림/표 번호 문서 순서 정렬 확인
- 수정 SVG(fig01/07/08) Chrome 재렌더 — 캡션 제거 후에도 의미 전달 정상
