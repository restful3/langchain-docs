# 2주차 발표 — Subagents & Human-in-the-loop

**발표자**: 보현  
**주제**: Subagents · Human-in-the-loop (20분)  
**한 줄 요약**: 서브에이전트는 무거운 하위 작업을 격리해 메인 컨텍스트를 지키고, Human-in-the-loop은 위험한 도구 호출 앞에서 실행을 멈춰 사람의 승인·수정·거부를 받게 한다.

---

## 최종 산출물

| 산출물 | 파일 | 용도 |
| --- | --- | --- |
| 교과서 (PDF) | [content/textbook.pdf](content/textbook.pdf) | 발표 전후 단독 학습용 |
| 교과서 (HTML) | [content/textbook.html](content/textbook.html) | 빠른 브라우저 확인 |
| 슬라이드 (PDF) | [content/slides.pdf](content/slides.pdf) | 발표장 보조 자료 |
| 슬라이드 (HTML) | [content/slides.html](content/slides.html) | 브라우저 발표/검수 |
| Walkthrough 노트북 | [scripts/walkthrough.ipynb](scripts/walkthrough.ipynb) | 5개 데모를 한 자리에서 실행 |
| 단독 실행 스크립트 5종 | [scripts/](scripts/) | 서브에이전트와 HITL 패턴별 CLI 데모 |

시각자료는 [content/figs/](content/figs/) 의 SVG 5개를 사용한다.

---

## 노트북 실행

```bash
cd langchain-docs/deep-agents/week2-subagents-bohyun
cp .env_sample .env
pip install -r scripts/requirements.txt
jupyter lab scripts/walkthrough.ipynb
```

필수 환경변수는 `.env_sample`을 참고한다.

| 변수 | 비고 |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI 또는 OpenAI 호환 프록시 키 |
| `OPENAI_BASE_URL` | 비우면 OpenAI 직접, 채우면 호환 프록시 |
| `DEEPAGENT_MODEL` | 기본값 `gpt-4o-mini` |

---

## 폴더 구조

```text
week2-subagents-bohyun/
├── README.md
├── .env_sample
├── content/
│   ├── textbook.html
│   ├── textbook.pdf
│   ├── slides.html
│   ├── slides.pdf
│   └── figs/
├── scripts/
│   ├── walkthrough.ipynb
│   ├── 01_basic_subagent.py
│   ├── 02_specialized_subagents.py
│   ├── 03_interrupt_approval.py
│   ├── 04_interrupt_edit.py
│   ├── 05_subagent_interrupt.py
│   ├── README.md
│   └── requirements.txt
└── archives/
    ├── meta/
    ├── source/
    └── original_docs/
```

PDF 재빌드는 다음 명령으로 수행한다.

```bash
python archives/source/build.py
```
