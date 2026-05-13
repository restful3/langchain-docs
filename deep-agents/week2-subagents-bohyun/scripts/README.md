# 실행 스크립트 — 2주차 발표

> 교안 `archives/source/01_textbook.md`의 코드 흐름을 실제 파일로 분리한 데모 세트다.

## 파일 목록

| 파일 | 무엇을 보이나 | 필수 키 |
|---|---|---|
| `01_basic_subagent.py` | 딕셔너리 기반 SubAgent 구성 | `OPENAI_API_KEY` |
| `02_specialized_subagents.py` | 여러 전문 서브에이전트 구성 | `OPENAI_API_KEY` |
| `03_interrupt_approval.py` | `delete_file` 승인/거부 흐름 | `OPENAI_API_KEY` |
| `04_interrupt_edit.py` | 도구 인자 `edit` 후 재개 | `OPENAI_API_KEY` |
| `05_subagent_interrupt.py` | 서브에이전트 내부 `interrupt_on` 재정의 | `OPENAI_API_KEY` |

## 셋업

```bash
cd langchain-docs/deep-agents/week2-subagents-bohyun
cp .env_sample .env
pip install -r scripts/requirements.txt
```

`OPENAI_BASE_URL`을 비우면 OpenAI 공식 엔드포인트를 사용하고, 값을 넣으면 OpenAI 호환 프록시로 라우팅한다.

## 실행

```bash
python scripts/01_basic_subagent.py
python scripts/02_specialized_subagents.py
python scripts/03_interrupt_approval.py
python scripts/04_interrupt_edit.py
python scripts/05_subagent_interrupt.py
```

HITL 스크립트는 첫 호출 결과의 `__interrupt__`를 출력한 뒤, 예제 결정 목록을 만들어 같은 `thread_id`로 재개한다.
