# 2주차 발표 — Deep Agents Backends 심층

**발표자**: jh-lee (이종훈)
**주제**: State · Filesystem · Store · Composite 백엔드 + Virtual FS · Policy Hooks
**한 줄 요약**: Deep Agent 의 가상 파일시스템은 4종 백엔드(휘발성 State / 로컬 디스크 / LangGraph Store 영속 / 합성 라우팅)로 추상화된다. 백엔드 선택과 정책 훅 설정만으로 같은 에이전트 코드가 ephemeral 데모부터 멀티 테넌트 운영까지 확장된다.

---

## 최종 산출물

| 산출물 | 파일 | 용도 |
| --- | --- | --- |
| 교과서 (PDF) | [content/textbook.pdf](content/textbook.pdf) | A4 — 발표 전후 단독 학습용 |
| 슬라이드 (PDF) | [content/slides.pdf](content/slides.pdf) | 발표장 보조 |
| Walkthrough 노트북 | [scripts/walkthrough.ipynb](scripts/walkthrough.ipynb) | 4개 백엔드 데모를 한 자리에서 실행 |

발표 시각자료는 [content/figs/](content/figs/) 의 SVG (노트북·교안에서 직접 참조).

---

## 노트북 실행

```bash
# 1) Ollama 모델 사전 준비 (한 번만)
ollama pull gemma4:31b

# 2) 가상환경·의존성
cd /Users/jaden/projects/langchain-docs/deep-agents/week2-backend-jh-lee
cp .env_sample .env   # 없으면. 값은 기본값 그대로 두어도 동작
pip install -r scripts/requirements.txt

# 3) 노트북
jupyter lab scripts/walkthrough.ipynb
```

환경변수 (모두 선택 — 기본값으로 로컬 Ollama 사용):

| 변수 | 기본 | 비고 |
| --- | --- | --- |
| `OLLAMA_MODEL` | `gemma4:31b` | `ollama list` 의 모델명과 일치해야 함 |
| `OLLAMA_BASE_URL` | (비움 → `http://127.0.0.1:11434`) | 원격 Ollama 서버 사용 시만 채움 |
| `LANGSMITH_API_KEY` | (선택) | `StoreBackend` 데모 트레이싱 시 |
| `LANGSMITH_PROJECT` | (선택) | 트레이싱 프로젝트 라벨 |

---

## 폴더 구조

```text
week2-backend-jh-lee/
├── README.md
├── .env / .env_sample
├── content/
│   ├── textbook.pdf            ★ 최종
│   ├── slides.pdf              ★ 최종
│   └── figs/                   SVG 다이어그램
├── scripts/
│   ├── walkthrough.ipynb       ★ 최종
│   └── requirements.txt
└── archives/                   중간 산출물·소스
    ├── meta/                   BRAINSTORM · PLAN · DESIGN · STATUS · NEXT_SESSION_PROMPT
    ├── source/                 PDF 빌드 소스 (01_textbook.md / slides.md / build.py / sections.yaml / 99_references.md / figs/)
    ├── scripts_py/             walkthrough.ipynb 의 소스가 되는 4종 백엔드 .py 데모 + README
    ├── original_docs/          공식 원문 (05-backends.md 영·한) + deepagents_backends/ 패키지 verbatim 스냅샷
    └── research/               보강자료 + INDEX
```

PDF 재빌드:

```bash
python archives/source/build.py             # HTML + PDF (한 번에)
python archives/source/build.py --html-only # PDF 스킵
```

`build.py` 는 week1 의 스크립트를 재사용 — 단일 섹션 빌더, `template/` 가 부모 레포에 있어야 동작.

---

## 1주차와의 관계

| | week1 (overview-taeyoung) | week2 (backend-jh-lee) |
| --- | --- | --- |
| 추상화 레벨 | 사용자 API (`create_deep_agent`) | 내부 메커니즘 (`Backend` 프로토콜) |
| 핵심 코드 인용 | `deepagents` 진입점 | `deepagents/backends/*.py` 11개 모듈 |
| 데모 4종 | 모델 스왑 · 시스템 프롬프트 | 4개 백엔드 (State/FS/Store/Composite) |

week1 의 4대 능력 중 *파일시스템·장기 메모리* 두 축을 깊이 파고드는 후속편으로 구성.
