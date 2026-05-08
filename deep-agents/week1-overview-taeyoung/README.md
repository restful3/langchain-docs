# 1주차 발표 — Deep Agents 첫 걸음

**발표자**: 태영
**주제**: Overview · Quickstart · Customization (20분, 첫 발제)
**한 줄 요약**: Deep Agent 는 LangGraph 위에 *계획 수립 · 파일시스템 · 서브에이전트 · 장기 메모리* 4대 능력을 미들웨어로 내장한 라이브러리다. `create_deep_agent()` 한 줄로 시작해 *Model · System Prompt · Tools* 세 다이얼로 자기 도메인에 맞춘다.

---

## 최종 산출물

| 산출물 | 파일 | 용도 |
| --- | --- | --- |
| 교과서 (PDF) | [content/textbook.pdf](content/textbook.pdf) | 18p A4 — 발표 전후 단독 학습용 |
| 슬라이드 (PDF) | [content/slides.pdf](content/slides.pdf) | 17장 — 발표장 보조 |
| Walkthrough 노트북 | [scripts/walkthrough.ipynb](scripts/walkthrough.ipynb) | 4개 데모를 한 자리에서 실행 |
| 단독 실행 스크립트 5종 | [scripts/](scripts/) (`01`\~`05`) | 노트북과 동일 데모를 CLI 한 줄로 — 자세한 셋업·트러블슈팅은 [scripts/README.md](scripts/README.md) |

발표 시각자료는 [content/figs/](content/figs/) 의 SVG 9개 (노트북이 직접 참조).

---

## 노트북 실행

```bash
cd /home/restful3/workspace/langchain-docs/deep-agents/week1-overview-taeyoung
cp .env_sample .env   # 없으면. 키 채워넣기
pip install -r scripts/requirements.txt
jupyter lab scripts/walkthrough.ipynb
```

필수 환경변수 (자세한 의미는 `.env_sample` 참조):

| 변수 | 비고 |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI 또는 OpenAI 호환 프록시의 키 |
| `OPENAI_BASE_URL` | 비우면 OpenAI 직접. clipproxyapi 등 사용 시 베이스 URL |
| `DEEPAGENT_MODEL` | 모델 식별자 (기본: `gpt-4o-mini`) |
| `TAVILY_API_KEY` | Demo 1 (리서치 에이전트)에서만 필수 |
| `OLLAMA_MODEL` | Demo 3 (Ollama 객체)에서만 사용 |

---

## 폴더 구조

```text
week1-overview-taeyoung/
├── README.md
├── .env / .env_sample
├── content/
│   ├── textbook.pdf            ★ 최종
│   ├── slides.pdf              ★ 최종
│   └── figs/                   SVG 9개 (노트북에서 참조)
├── scripts/
│   ├── walkthrough.ipynb       ★ 최종 (라이브 데모)
│   ├── 01_quickstart_research_agent.py
│   ├── 02_model_string_swap.py
│   ├── 03_model_object_ollama.py
│   ├── 04_custom_system_prompt.py
│   ├── 05_persistent_memory.py
│   ├── README.md               셋업·실행·트러블슈팅
│   └── requirements.txt
└── archives/                   중간 산출물·소스
    ├── meta/                   BRAINSTORM · PLAN · STATUS · DESIGN · NEXT_SESSION_PROMPT
    ├── source/                 PDF 빌드 소스 (md/html/build.py/sections.yaml/99_references) + 옛 통합본
    ├── original_docs/          공식 원문 6개 (Overview/Quickstart/Customization, 한·영)
    └── research/               Phase 2 보강자료 (7건 + INDEX + RAG 합성)
```

PDF 재빌드가 필요할 경우 [archives/source/build.py](archives/source/build.py) 참조 (`content/01_textbook.md`, `content/sections.yaml` 같은 경로 가정이 있어 archives 안에서는 그대로 동작 안 함 — 필요 시 content/ 로 잠깐 복원해서 빌드).
