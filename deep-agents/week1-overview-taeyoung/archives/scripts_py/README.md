# 실행 스크립트 — 1주차 발표

> 교안 [`content/01_textbook.md`](../content/01_textbook.md) 의 코드 블록은 모두 이 폴더의 실제 파일에서 가져온다.

---

## 1. 파일 목록

| 파일 | 무엇을 보이나 | 교안 매핑 | 필수 키 |
|---|---|---|---|
| `01_quickstart_research_agent.py` | Tavily 검색 도구 + `create_deep_agent` 풀 예제 | §3.2\~§3.4 | `OPENAI_API_KEY`, `TAVILY_API_KEY` |
| `02_model_string_swap.py` | `init_chat_model("openai:<model>")` 한 줄로 모델 교체 | §4.3 | `OPENAI_API_KEY` |
| `03_model_object_ollama.py` | LangChain 모델 객체(ChatOllama) 패턴 | §4.3 | (Ollama 로컬) |
| `04_custom_system_prompt.py` | 커스텀 `system_prompt` 한 장 합성 | §4.4 | `OPENAI_API_KEY` |

---

## 2. 셋업

### 2-1. 의존성 설치

```bash
cd /home/restful3/workspace/langchain-docs/deep-agents/week1-overview-taeyoung
pip install -r scripts/requirements.txt
```

### 2-2. 환경변수

`.env_sample` 을 `.env` 로 복사하고 빈 값을 채운다.

```bash
cp .env_sample .env
$EDITOR .env
```

| 변수 | 의미 | 기본값 / 비고 |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI 또는 OpenAI 호환 프록시의 키 | 필수 |
| `OPENAI_BASE_URL` | OpenAI 호환 프록시의 베이스 URL | 비우면 OpenAI 직접. clipproxyapi 예: `http://localhost:8317/v1` |
| `DEEPAGENT_MODEL` | 사용할 모델 식별자 (`provider:model` 의 `model` 부분) | `gpt-4o-mini` |
| `TAVILY_API_KEY` | Tavily 검색 API 키 | `01` 에서만 필수. <https://tavily.com/> |
| `OLLAMA_MODEL` | Ollama 모델명 | `llama3.1`. `03` 에서만 사용 |

### 2-3. (선택) Ollama 준비 — `03` 만

```bash
# 별도 셸에서 ollama 데몬이 떠 있어야 한다
ollama pull llama3.1
```

---

## 3. 실행

```bash
# 작업 디렉토리는 week1-overview-taeyoung/ 로 둔다
cd /home/restful3/workspace/langchain-docs/deep-agents/week1-overview-taeyoung

# Quickstart — 리서치 에이전트
python scripts/01_quickstart_research_agent.py

# 모델 갈아 끼우기 — 문자열 패턴
python scripts/02_model_string_swap.py

# 모델 갈아 끼우기 — LangChain 모델 객체 패턴
python scripts/03_model_object_ollama.py

# 커스텀 system_prompt
python scripts/04_custom_system_prompt.py
```

> 각 스크립트는 `find_dotenv()` 로 상위 디렉토리의 `.env` 를 찾으므로,
> 위치는 `week1-overview-taeyoung/` 어디에서 실행해도 자동으로 잡힌다.

---

## 4. 동작 모델 결정 흐름

```text
                .env (또는 OS 환경변수)
                       │
                       ▼
        ┌─────────────────────────────┐
        │ OPENAI_BASE_URL 비어있는가? │
        └──────┬───────────────┬──────┘
               │ Yes           │ No
               ▼               ▼
        OpenAI 공식        clipproxyapi
        엔드포인트         (또는 임의 호환 프록시)
               │               │
               └───────┬───────┘
                       ▼
            init_chat_model("openai:" + DEEPAGENT_MODEL, base_url=...)
                       ▼
            create_deep_agent(model=...)
```

`02`, `04` 는 `01` 과 동일한 결정 흐름을 따른다. `03` 만 Ollama 로 분기한다.

---

## 5. 트러블슈팅

| 증상 | 원인 / 해결 |
|---|---|
| `KeyError: 'TAVILY_API_KEY'` | `.env` 에 `TAVILY_API_KEY` 비어 있음. `01` 만 필요. |
| `openai.AuthenticationError` | `OPENAI_API_KEY` 잘못됨 — clipproxyapi 의 키가 OpenAI 공식 키로 잘못 흘러 들어갔거나 그 반대. `OPENAI_BASE_URL` 일치 여부 확인. |
| `Connection refused` (clipproxyapi) | 프록시 데몬 (예: 포트 8317) 안 떠 있음. |
| `httpx.ConnectError` (Ollama) | `ollama serve` 안 돌고 있음. |
| `ImportError: langchain_ollama` | `pip install langchain-ollama` |

---

## 6. 발표 시 라이브 데모용 명령

```bash
# 슬라이드 §10~§11 (코드 한 페이지 + invoke 5단계) 시연
python scripts/01_quickstart_research_agent.py 2>&1 | tee /tmp/01_run.log

# 슬라이드 §14 (모델 갈아 끼우기) 시연 — 출력은 짧다
python scripts/02_model_string_swap.py
```
