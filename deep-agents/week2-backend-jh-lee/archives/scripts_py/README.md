# scripts_py — 2주차 백엔드 데모 4종

`archives/source/01_textbook.md` 본문에 인용되는 코드의 **소스 오브 트루스**. 검증된 후 `scripts/walkthrough.ipynb` 로 통합된다.

## 매핑

| 파일 | 교안 § | 다루는 백엔드 | 핵심 시연 |
| --- | --- | --- | --- |
| `01_state_backend.py` | §3 | `StateBackend` | thread-scoped 휘발성 — 같은 thread 잔존 / 다른 thread 부재 |
| `02_filesystem_backend.py` | §4 | `FilesystemBackend` | `root_dir` + `virtual_mode` on/off 경로 정규화 차이 |
| `03_store_backend.py` | §5 | `StoreBackend` | LangGraph Store — thread-cross 영속 |
| `04_composite_backend.py` | §6 | `CompositeBackend` | 라우팅 3개 규칙 동시 운영 |

## 사전 준비

```bash
# Ollama 모델 사전 다운로드 (한 번만)
ollama pull gemma4:31b

cd /Users/jaden/projects/langchain-docs/deep-agents/week2-backend-jh-lee
cp .env_sample .env   # 기본값으로 로컬 Ollama 사용 — API 키 불필요
pip install -r scripts/requirements.txt
```

## 개별 실행

```bash
python archives/scripts_py/01_state_backend.py
python archives/scripts_py/02_filesystem_backend.py
python archives/scripts_py/03_store_backend.py
python archives/scripts_py/04_composite_backend.py
```

## 일괄 실행 (walkthrough)

```bash
jupyter lab scripts/walkthrough.ipynb
```

## 환경변수

| 변수 | 필수 | 비고 |
| --- | --- | --- |
| `OLLAMA_MODEL` | 선택 | 기본 `gemma4:31b` — `ollama list` 의 모델명과 일치해야 함 |
| `OLLAMA_BASE_URL` | 선택 | 원격 Ollama 사용 시만 (기본: `http://127.0.0.1:11434`) |
| `LANGSMITH_API_KEY` | 선택 | Store 영속을 LangSmith 로 바꿀 경우 트레이싱용 |

## 검증 컨벤션

각 스크립트는:
- `__future__ import annotations` 기준
- `.env` 자동 로드 (`dotenv.find_dotenv`)
- `ChatOllama(model=OLLAMA_MODEL)` 로 모델 초기화 (DESIGN.md §4 확정)
- `main()` 진입점 + `if __name__ == "__main__"`

라인 번호가 교안에서 인용되므로, 스크립트를 수정하면 교안 §섹션의 `라인 X-Y` 참조도 동기화할 것.
