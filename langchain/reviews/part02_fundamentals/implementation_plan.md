# Part 2 교안 수정 구현 계획

## Context

2026-02-28 리뷰 회의에서 확정된 10개 수정 사항을 `agent_requests.md` 기반으로 구현한다. 핵심 목표는 **2,233줄 교안의 분량 축소** (목표 1,489줄 이하)와 **deprecated API / 보안 이슈 수정**이다.

## 수정 대상 파일

- `docs/part02_fundamentals.md` (2,233줄) — 교안 본문
- `src/part02_fundamentals/04_tools_advanced.py` — Pydantic v2 마이그레이션
- `src/part02_fundamentals/05_tool_calling.py` — eval() 보안 경고

## 작업 순서

agent_requests.md의 권장 순서를 따른다: **점 수정 → 대량 삭제(뒤→앞) → 검증**.

---

### Step 1: 백업 생성

```bash
cp docs/part02_fundamentals.md docs/part02_fundamentals.md.bak
cp src/part02_fundamentals/04_tools_advanced.py src/part02_fundamentals/04_tools_advanced.py.bak
cp src/part02_fundamentals/05_tool_calling.py src/part02_fundamentals/05_tool_calling.py.bak
```

---

### Step 2: 요청 8 — 셋업 가이드 링크 추가 (교안 L3\~L6)

파일: `docs/part02_fundamentals.md` L3\~L6

메타 정보 블록에 셋업 가이드 링크를 삽입한다.

**변경**: L5(📖 공식 문서) 위에 새 줄 추가:

```
> 🛠️ **환경 설정**: [SETUP_GUIDE.md](../SETUP_GUIDE.md) — API 키 설정, 패키지 설치, 실행 환경 구성
```

**검증**: `SETUP_GUIDE.md`는 `/media/restful3/data/workspace/langchain-docs/langchain/SETUP_GUIDE.md`에 존재 확인됨. 상대 경로 `../SETUP_GUIDE.md`가 올바름.

---

### Step 3: 요청 4 — deprecated API 수정 (교안)

파일: `docs/part02_fundamentals.md`

**(a)** L366\~L367:
- `from langchain.agents import create_agent` → `from langgraph.prebuilt import create_react_agent`
- `return create_agent(model=model, tools=[get_weather])` → `return create_react_agent(model=model, tools=[get_weather])`

**(b)** L874/L909 — 요청 1에서 해당 섹션(L870\~L921) 전체 삭제 예정이므로 **스킵**.

**(c)** L1764 텍스트 참조:
- `create_agent()` → `create_react_agent()` (LangGraph의)

**(d)** L2194 텍스트 참조:
- `create_agent()`로 완전한 Agent 구축 → `create_react_agent()`로 완전한 Agent 구축

---

### Step 4: 요청 7 — eval() 보안 경고 추가

파일: `src/part02_fundamentals/05_tool_calling.py` L79

방안 A(최소 변경) 채택. `eval()` 호출 직전에 경고 주석 삽입:

```python
        # ⚠️ 주의: eval()은 임의 코드 실행 위험이 있습니다.
        # 프로덕션에서는 ast.literal_eval() 또는 numexpr.evaluate()를 사용하세요.
        result = eval(expression)
```

**검증**: `grep -rn "eval(" src/part02_fundamentals/`로 다른 eval 없음 확인.

---

### Step 5: 요청 5 — deprecated API 수정 (소스코드)

파일: `src/part02_fundamentals/04_tools_advanced.py`

참고: `solutions/exercise_03.py`가 이미 올바른 Pydantic v2 패턴 사용 중.

**(a)** L31: `from pydantic import BaseModel, Field, validator` → `from pydantic import BaseModel, Field, field_validator`

**(b)** L70: `get_weather_advanced.args_schema.schema()` → `get_weather_advanced.args_schema.model_json_schema()`

**(c)** L93\~L94:
```python
# Before:
    @validator('email')
    def validate_email(cls, v):

# After:
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
```

**검증**: `python -m py_compile src/part02_fundamentals/04_tools_advanced.py` 통과 확인.

---

### Step 6: 요청 6 — 모델명 최신화 검증

파일: `docs/part02_fundamentals.md`, `src/part02_fundamentals/*.py`

Anthropic 공식 모델 목록과 대조하여 실존 여부를 확인해야 하는 모델 ID:

| 위치 | 모델 ID | 확인 사항 |
|------|---------|-----------|
| 교안 L156, L160 등 | `claude-sonnet-4-5-20250929` | 공식 docs 대조 |
| 교안 L164 | `claude-opus-4-5-20251101` | 공식 docs 대조 |
| 교안 L166 | `claude-haiku-4-5-20251001` | 시스템 메시지에서 확인됨 (유효) |
| 교안 L200 | `gpt-4.1` (Azure) | OpenAI 공식 목록 대조 |
| 소스 L147 | `claude-haiku-4-5-20251001` | 유효 |
| 소스 L154 | `gemini-2.5-flash-lite` | 이미 최신 |

**실행 시**: Anthropic docs 웹 검색으로 claude-sonnet-4-5, claude-opus-4-5 실존 여부를 확인한 뒤, 불일치 시 실제 ID로 교체한다.

---

### Step 7: 요청 3 — Pydantic 스키마 섹션 축소 (L1495\~L1618)

파일: `docs/part02_fundamentals.md`

**대량 삭제는 뒤쪽부터 진행** (라인 번호 보존).

**(a)** L1575\~L1620 삭제 (5.3 중첩 복잡 입력 타입 전체 + 예제 코드 참조)

**(b)** L1533\~L1573 축소 (5.2 Field Descriptions):
- `Field(description=...)` 기본 사용법 2\~3줄 요약만 남기기
- SearchInput 코드 블록, Field 검증 옵션 표 삭제

**(c)** 축소된 섹션 5 말미에 안내 문구 추가:
```
> 💡 독스트링과 타입힌트만으로도 대부분의 Tool은 잘 동작합니다. Pydantic 스키마는 복잡한 입력 검증이 필요할 때 사용하세요.
```

**(d)** 섹션 제목 경량화 검토: `## 5. Tools 고급` → `## 5. Tools 고급 — Pydantic 스키마`

**예상 감축**: \~70줄

---

### Step 8: 요청 2 — ToolRuntime 섹션 축소 (L1176\~L1492)

파일: `docs/part02_fundamentals.md`

**(a)** L1292\~L1492 삭제 (4.3 Type-Safe, 4.4 실전 패턴, 4.5 주의사항, 4.6 성능 고려사항)

**(b)** L1202\~L1290 축소 (4.2 Runtime 속성):
- 5가지 속성을 **요약 테이블 1개** 로 대체:

```markdown
| 속성 | 용도 | 설명 |
|------|------|------|
| `runtime.state` | Agent 상태 접근 | 메시지 기록 등 현재 상태 조회 |
| `runtime.context` | 요청 컨텍스트 | 사용자 ID, 언어 등 요청별 정보 |
| `runtime.store` | 장기 메모리 | 사용자 선호도 등 영속 데이터 접근 |
| `runtime.stream_writer` | 실시간 이벤트 | 진행률 등 중간 결과 스트리밍 |
| `runtime.tool_call_id` | Tool Call ID | 현재 호출의 고유 식별자 |
```

**(c)** 안내 문구 추가:
```
> 💡 ToolRuntime의 상세 활용법은 Agent/MCP를 다루는 후속 파트에서 실습합니다.
```

**예상 감축**: \~260줄

---

### Step 9: 요청 1 — Multimodal 섹션 축소 (L712\~L998)

파일: `docs/part02_fundamentals.md`

**(a)** L802\~L868 삭제 (PDF 문서 입력, 오디오 입력, 비디오 입력)
- 그 전에 L801 뒤에 이미지 방법 3(File ID, L781\~L800)이 있으므로 L801까지 유지

**(b)** L870\~L921 삭제 (실전 예제: 이미지 분석 Agent — deprecated create_agent 포함)

**(c)** L923\~L997 축소 (주의사항 + 포맷 테이블):
- 파일 크기 제한 코드(L925\~L944): 이미지 관련이므로 간략화하여 유지
- 지원 포맷 테이블(L946\~L952): 삭제 (프로바이더 특화 내용)
- Base64 vs URL vs File ID 비교(L954\~L968): 간략히 텍스트로 유지
- 비용 고려 코드(L970\~L991): 삭제
- 핵심 포인트 박스(L993\~L997): 이미지 중심으로 수정:

```markdown
> 💡 **핵심 포인트**:
> - Multimodal은 이미지를 비롯해 다양한 형식을 지원하지만, 여기서는 이미지 입력만 다룹니다
> - 2가지 주요 입력 방법: URL, Base64
> - PDF, 오디오, 비디오 등 추가 멀티모달 입력은 [공식 문서](../official/08-messages_ko.md)를 참조하세요
```

**예상 감축**: \~160줄

---

### Step 10: 요청 9 — 라인 참조 재검증

축소 작업 완료 후 교안 내 모든 `예제 코드` 라인 참조를 추출하여 실제 소스 코드와 대조한다.

```bash
grep -n "예제 코드" docs/part02_fundamentals.md
```

교안 내 라인 참조가 가리키는 **소스 코드** 파일의 라인은 변경되지 않으므로 (소스 코드 자체는 큰 구조 변경 없음), 주로 **교안 라인에서 해당 참조가 남아있는지** 확인한다. 삭제된 섹션 내 참조(L1618의 `04_tools_advanced.py 라인 301-340` 등)는 자연히 제거됨.

---

### Step 11: 요청 10 — 최종 분량 확인

```bash
wc -l docs/part02_fundamentals.md
```

- 예상: \~1,740줄 (요청 1\~3 합산 약 490줄 감축)
- 1,489줄 목표에 구애받지 않고, 10개 요청을 충실히 이행하는 것에 집중
- 최종 줄 수는 기록만 남김

---

### Step 12: 최종 확인

- [ ] `python -m py_compile src/part02_fundamentals/04_tools_advanced.py`
- [ ] `python -m py_compile src/part02_fundamentals/05_tool_calling.py`
- [ ] `grep -rn "from langchain.agents import" docs/part02_fundamentals.md` → 0건
- [ ] `grep -rn "@validator" src/part02_fundamentals/` → 0건
- [ ] `grep -rn "eval(" src/part02_fundamentals/` → 경고 주석 동반 확인
- [ ] `grep -n "claude-\|gemini-\|gpt-" docs/part02_fundamentals.md` → 모델 ID 전수 확인
- [ ] 교안 전체 흐름이 자연스러운지 통독 확인
- [ ] git diff로 변경 사항 리뷰
- [ ] 모두 통과 시 백업 삭제: `rm *.bak`
