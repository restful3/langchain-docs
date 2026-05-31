# 슬라이드 Codex 리뷰 — 결정 및 변경 (Claude)

대상: `content/slides.md` · Codex 리뷰: `2026-05-30-slides-codex.md`
결과: Critical 0 · Major 1 · Minor 4 · Nit 3 → **전부 ACCEPT 반영**

| # | 슬라이드 | 변경 |
|---|---|---|
| Major 1 | 14 사람 입력 1급 | 부제 "며칠 뒤라도 thread_id 로 재개" → "checkpoint 가 남아 있으면 같은 thread_id + Command(resume=) 로 재개" (thread_id 단독 장기재개 오해 제거) |
| Minor 2 | 4 함수 vs 그래프 | 표 셀 "멈춘 노드부터 재개" → "checkpointer 로 멈춘 노드부터 재개" (durable 전제 명시) |
| Minor 3 | 8 노드로 분해 | 하단에 "human_review 가 두 번 보이는 건 같은 노드의 레이아웃 단순화" 추가 |
| Minor 4 | 15 granularity | "노드 많아도 느려지지 않는다" → "기본 async durability 는 checkpoint write 를 매번 기다리지 않는다 — 단, 의미 있는 경계로 쪼갠다" |
| Minor 5 | 18 changelog | 2025-12 한 행에 합쳐졌던 두 릴리스를 2025-12-08(Google GenAI v4) / 2025-12-15(create_agent extras) 두 행으로 분리 |
| Nit 6 | 2 인트로 | `"…있다" 던` → `"…있다"던` 띄어쓰기 |
| Nit 7 | 7 5단계 | 제목 "다섯 단계로 짠다" → "설계는 다섯 단계로 좁힌다" (메시지성 강화) |
| Nit 8 | 19 closing | 자료 표기 `content/textbook · figs/01~09` → `content/01_textbook.md · figs/fig01~09` |

## 검증

- 슬라이드 재빌드 — 19장 유지, **오버플로우 경고 0** (표 4행으로 늘어난 18장 포함)
