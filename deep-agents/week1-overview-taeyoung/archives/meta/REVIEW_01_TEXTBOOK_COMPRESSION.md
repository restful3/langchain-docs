# Review Report: 01_textbook.md

검토 대상: `archives/source/01_textbook.md`  
검토 일자: 2026-05-06  
검토 범위: 압축 리라이트 결과의 기술 정확성, 구조 불변, 상호참조, 마크다운 위생, 발표 적합성

## 점수표

| 메트릭 | 점수 (1-5) | 한 줄 평가 |
|---|---:|---|
| 1. 원본 자료 충실도 | 3 | 큰 인용 축은 맞지만 `permissions`, README 각주, "4대 능력" 분류가 일부 섞임 |
| 2. 기술적 정확성 | 3 | 17개 파라미터, BASE_PROMPT, no-op 주장은 검증됨. 권한/미들웨어/기본값 설명은 수정 필요 |
| 3. 압축 품질 | 4 | 반복 제거는 대체로 수술적. §4.4 일부 검증 문장이 줄었지만 핵심은 남음 |
| 4. 한국어 표현 | 4 | 기술 문체는 자연스러움. 일부 긴 em-dash 문장과 `OK 지만` 같은 구어 흔적 있음 |
| 5. 교육적 명료성 | 4 | §1 -> §3 흐름은 좋음. "Detailed prompt vs Long-term Memory" 축 구분은 더 명확해야 함 |
| 6. 상호참조 무결성 | 5 | 섹션, 그림, 표, 각주, SVG 경로 모두 매칭 |
| 7. 구조 불변 | 5 | 9그림, 9표, 15코드블록, 7각주 유지, /tmp HTML 빌드 성공 |
| 8. 마크다운 위생 | 4 | 코드블록 언어 OK. `~42줄`, bold 뒤 한글, trailing whitespace 후보 있음 |
| **종합** | 3.8 | 구조는 안정적이고 발표 흐름도 좋지만, 출간 전 기술 블로커 몇 개는 고쳐야 함 |

## 블로커 (출간 전 반드시 수정)

- `archives/source/01_textbook.md:191` — 클래스명 오기. 공식 코드/문서는 `SubAgentMiddleware`임.
  - `SubagentMiddleware[^6] 가 task 도구 하나를 더한다.`
  - -> `SubAgentMiddleware[^6] 가 task 도구 하나를 더한다.`

- `archives/source/01_textbook.md:198`, `:233`, `:527`, `:724` — `permissions=` 를 "도구 풀 분리"로 설명함. 현재 `permissions`는 built-in filesystem 도구의 파일 경로 read/write 규칙임. 도구 풀은 `SubAgent.tools`로 제한함.
  - `permissions= 로 메인과 서브의 도구 풀을 다르게 자른다`
  - -> `tools 로 서브에이전트별 도구 풀을 제한하고, permissions= 는 built-in filesystem 도구의 경로 접근 규칙을 제어한다`

- `archives/source/01_textbook.md:81`, `:85`, `:107` — "기본 미들웨어를 빼거나 갈아 끼울 수 있다"는 표현이 과함. 현재 `FilesystemMiddleware`, `SubAgentMiddleware`는 scaffolding이라 제거 시 `ValueError`.
  - `인자로 미들웨어를 빼거나 갈아 끼울 수 있다`
  - -> `backend=, subagents=, middleware= 로 저장소, 위임, 추가 동작을 조정한다. 단, FilesystemMiddleware 와 SubAgentMiddleware 같은 scaffolding 미들웨어는 제거 대상이 아니다.`

- `archives/source/01_textbook.md:509` — API 기본값 오기. `tools` 기본값은 `[]`가 아니라 `None`임.
  - ``| `tools` | `[]` | 빌트인 9종에 추가될 사용자 도구 리스트 |``
  - -> ``| `tools` | `None` (추가 도구 없음) | 빌트인 9종에 추가될 사용자 도구 리스트 |``

- `archives/source/01_textbook.md:652` — footnote 불일치. `[^7]`은 `graph.py`의 `BASE_AGENT_PROMPT`이고 README Acknowledgements 출처가 아님. Harrison 블로그의 Acknowledgements 문맥이면 `[^1]`이 맞음.
  - `README 의 Acknowledgements 가 명시한다 ... [^7]`
  - -> `Harrison Chase 의 출시 글이 명시한다 ... [^1]`

## 개선 권장 (수정 권유)

- `archives/source/01_textbook.md:156`, `:254`, `:531` — backend factory 패턴(`lambda rt`, `StateBackend(rt)`)은 현재 문서에서 deprecated.
  - `backend=lambda rt: CompositeBackend(default=StateBackend(rt), routes={"/memories/": StoreBackend(rt)})`
  - -> `backend=CompositeBackend(default=StateBackend(), routes={"/memories/": StoreBackend()})`

- `archives/source/01_textbook.md:162` — `create_deep_agent()` 무인자 호출은 현재 `model=None` deprecation 경고와 Anthropic 키 요구를 유발.
  - `agent_default = create_deep_agent()`
  - -> `agent_default = create_deep_agent(model=model)`

- `archives/source/01_textbook.md:457` — streaming 설명이 현재 Deep Agents v2 streaming 포맷과 다름. `todos`, `files`가 top-level chunk key로 나온다는 식의 설명은 위험함.
  - 제안: `version="v2"` 예시로 바꾸고 `chunk["type"]`, `chunk["ns"]`, `chunk["data"]` 구조를 설명.

- `archives/source/01_textbook.md:15`, `:63-70`, `:99` — Harrison의 4축은 `detailed prompt`이고, 현행 docs의 core capabilities에는 long-term memory가 따로 있음. 둘을 "원형 4축"과 "이 교안의 4대 실습 축"으로 분리하면 혼선이 줄어듦.

- `archives/source/01_textbook.md:523` — `memory=`는 Backend 라우팅 인자가 아니라 AGENTS.md 파일을 시스템 프롬프트에 로드하는 인자.
  - `Backend | backend=, memory=, store=`
  - -> `Backend | backend=, store=`

## 선택 사항 / Nitpick

- `archives/source/01_textbook.md:737` — 이스케이프되지 않은 tilde.
  - `~42줄`
  - -> `\~42줄`

- `archives/source/01_textbook.md:133` — `**no-op 도구**다`는 CJK bold 뒤 한글 붙음 후보.
  - `**no-op 도구**다`
  - -> `**no-op 도구** 다` 또는 `사실상 no-op인 도구다`

- `archives/source/01_textbook.md:63` — blockquote 줄 끝 trailing spaces 2개. 의도적 hard break가 아니면 제거 권장.

## 절별 관찰

- §0: 범위 선언이 명확함. 다만 첫 요약의 "장기 메모리 4대 능력"은 Harrison 4축과 구분 필요.
- §1.1: 문제 제기가 잘 압축됨. "단계 5/50"은 휴리스틱임을 한 단어로 표시하면 더 안전.
- §1.2: Anthropic, PromptLayer, Manus Gist 대조 결과 큰 의미 변질은 없음. OpenAI/Manus는 2차 자료 기반임을 유지하는 편이 좋음.
- §1.3: 라이브러리 vs 프레임워크 설명은 좋음. 미들웨어 제거 가능성 표현은 현재 API와 충돌.
- §2: 비서 비유는 교육적으로 좋음. "일기장"은 기본 미들웨어라기보다 StoreBackend/Store 조합임을 더 분명히.
- §2.1: no-op 주장은 Harrison 글과 일치. 렌더링 nit만 있음.
- §2.2: Backend 라우팅 개념은 정확. 코드가 deprecated factory 패턴.
- §2.3: 가장 수정이 필요한 절. `SubAgentMiddleware` 오기와 `permissions` 설명 오류가 있음.
- §2.4: Store 기반 cross-thread 예시는 메시지가 선명함. 최신 backend 인스턴스 패턴으로 갱신 권장.
- §2.5: `execute`/`SandboxBackendProtocol` 설명은 공식 API와 일치.
- §3.1: 환경 준비는 충분함. `langchain-openai` 필요성을 짚은 점 좋음.
- §3.2: Tavily wrapper는 스크립트와 일치, Python syntax OK.
- §3.3: Quickstart 코드 흐름은 스크립트와 일치. API default 설명은 §4.1에서 수정 필요.
- §3.4: 5단계 개념 그림은 명료함. streaming 예시는 현재 docs 기준으로 갱신 권장.
- §4: 17개 파라미터 수는 검증됨. "두 묶음"과 "세 묶음" 표현이 약간 흔들림.
- §4.1: 모델 기본값 자체는 맞지만 deprecated 상태를 반영해야 함. `tools` 기본값은 수정 필요.
- §4.2: `permissions`, `memory`, backend 설명이 섞임. 표와 본문을 분리하면 해결됨.
- §4.3: 모델 교체 흐름은 좋음. OpenAI Responses API 주의 문구는 선택적으로 복원 가능.
- §4.4: prompt assembly 설명은 현재 `graph.py`와 잘 맞음. 마지막 Acknowledgements 각주만 수정.
- §5.1: 의사결정 축이 실용적임. 압축 후에도 메시지 손실은 크지 않음.
- §5.2: 표와 한 줄 룰이 잘 남음. 재현성 단락도 교육적으로 유용.
- §6.1: `skills`는 이미 현행 파라미터이므로 "추후 추가" 표현은 버전 맥락을 달아야 함.
- §6.2: `permissions` 범위를 filesystem permissions로 수정 필요.
- 부록 A: 용어 정의는 대체로 본문과 일치. `~42줄`만 escaping 필요.
- 부록 B: 본문 `scripts/01_*.py` 참조는 실제 파일이 `archives/scripts_py/`에 있음. 요청 조건상 prefix 차이는 허용 가능하나, week root `scripts/`에는 해당 py 파일이 없어 독자용 경로라면 혼란 가능.

## 검증 명령 결과

- `wc -l archives/source/01_textbook.md` -> `766`
- `git show HEAD:.../01_textbook.md | wc -l` -> `844`
- `git diff --stat HEAD -- archives/source/01_textbook.md` -> `73 insertions(+), 151 deletions(-)`
- 구조 카운트: headings `34`, 그림 캡션 `9`, 표 캡션 `9`, fenced code blocks `15`, missing code language `0`
- 각주: 본문 사용 `[^1]`~`[^7]`, `99_references.md` 정의 `[^1]`~`[^7]`, 누락 없음
- SVG: 본문 참조 9개와 `archives/source/figs/` 실제 파일 9개 일치, orphan 없음
- 섹션 참조: 모든 `§N.M` 참조가 본문 헤딩에 존재
- Python syntax: 본문 Python 코드블록 12개 `ast.parse` OK, `archives/scripts_py/*.py` 4개 `ast.parse` OK
- Runtime import: local 환경에 `deepagents` 미설치 -> 실제 import/runtime 실행은 unverified
- Build: workspace를 쓰지 않고 `/tmp/codex_review_textbook_build`로 HTML-only 빌드 성공, SVG inline 9개, HTML 125 KB
- 작업트리 확인: 빌드 후에도 변경 파일은 기존 `M archives/source/01_textbook.md`뿐
- 외부 대조 출처: LangChain blog, Anthropic blog, PromptLayer, Manus Gist, GitHub `graph.py`, LangChain Deep Agents overview/backends/streaming/middleware docs

## 결론

블로커 수정 후 발표 가능.

---

# Claude 2차 검토용 프롬프트

아래 프롬프트를 Claude에 그대로 붙여 넣고, 이 저장소 또는 파일 내용을 함께 첨부한다.

```text
당신은 한국어 기술 교안과 Python/LangChain 문서의 기술 리뷰어입니다. 다음 Codex 리뷰 보고서를 2차 검증하세요.

검토 대상 파일:
- /home/restful3/workspace/langchain-docs/deep-agents/week1-overview-taeyoung/archives/source/01_textbook.md

참고 파일:
- /home/restful3/workspace/langchain-docs/deep-agents/week1-overview-taeyoung/archives/meta/REVIEW_01_TEXTBOOK_COMPRESSION.md
- /home/restful3/workspace/langchain-docs/deep-agents/week1-overview-taeyoung/archives/source/99_references.md
- /home/restful3/workspace/langchain-docs/deep-agents/week1-overview-taeyoung/archives/source/slides.md
- /home/restful3/workspace/langchain-docs/deep-agents/week1-overview-taeyoung/archives/scripts_py/*.py

공식/1차 대조 출처:
- https://github.com/langchain-ai/deepagents
- https://docs.langchain.com/oss/python/deepagents/overview
- https://docs.langchain.com/oss/python/deepagents/quickstart
- https://docs.langchain.com/oss/python/deepagents/customization
- https://docs.langchain.com/oss/python/deepagents/middleware
- https://docs.langchain.com/oss/python/deepagents/backends
- https://docs.langchain.com/oss/python/deepagents/streaming
- https://reference.langchain.com/python/deepagents/graph/create_deep_agent
- https://blog.langchain.com/deep-agents/

요청:
1. Codex 리뷰의 블로커 5개가 실제로 맞는지 최신 공식 문서와 GitHub 코드 기준으로 검증하세요.
2. 틀린 블로커가 있으면 "reject"로 표시하고 이유와 근거 링크를 주세요.
3. 맞는 블로커는 "confirm"으로 표시하고, 더 정확한 제안 패치를 old_string -> new_string 형식으로 주세요.
4. Codex가 놓친 추가 블로커가 있으면 최대 5개만 제시하세요.
5. 압축 품질 관점에서 삭제가 파괴적인 곳이 있으면 라인 번호와 이유를 주세요.
6. 검증할 수 없는 주장은 반드시 "unverified"로 표시하세요.

출력 형식:

# Claude Second Review

## Verdict
- 이대로 발표 가능 / 블로커 수정 후 발표 가능 / 큰 재작업 필요 중 하나

## Codex Blocker Validation
| 항목 | confirm/reject/unverified | 근거 | 제안 패치 |
|---|---|---|---|

## Additional Blockers

## Compression Risks

## Markdown / Korean Writing Issues

## Final Patch Priority
```
