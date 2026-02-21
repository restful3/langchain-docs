# Part [번호] 에이전트 요청사항

> 작성일: YYYY-MM-DD
> 기반: `decisions.md` 확정 사항

---

## 요청 1: [변경 요약]

- **파일**: `docs/partXX_*.md`
- **위치**: L42 (섹션 1.1)
- **현재**: `init_chat_model(model="gpt-4o")`
- **변경**: `model_provider` 파라미터 설명 추가
- **상세**: 최신 API에서는 model_provider를 명시적으로 지정해야 함. 예제 코드와 설명 모두 업데이트

### 검증

- [ ] 변경된 코드가 문법적으로 올바른가
- [ ] 전후 문맥과 자연스럽게 이어지는가

---

## 요청 2: [변경 요약]

- **파일**: `src/partXX_*/01_chat_models.py`
- **위치**: L25
- **현재**: `model.predict("Hello")`
- **변경**: `model.invoke("Hello")` 로 교체
- **상세**: predict()는 deprecated, invoke()가 현재 권장 API

### 검증

- [ ] `python -m py_compile` 통과하는가
- [ ] 교안의 해당 코드 블록과 일치하는가

---

<!-- 요청을 추가할 때 위 형식을 복사하여 사용 -->

## 최종 확인

모든 요청 반영 후 아래를 확인합니다.

- [ ] 수정된 교안 전체를 한 번 읽어 흐름이 자연스러운지 확인
- [ ] 수정된 예제 코드가 `python -m py_compile` 통과
- [ ] decisions.md의 확정 항목이 빠짐없이 반영되었는지 대조
- [ ] git diff로 변경 사항 최종 리뷰
