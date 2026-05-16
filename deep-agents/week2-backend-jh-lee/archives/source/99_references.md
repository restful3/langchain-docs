# 참고 문헌 — 2주차 Backends

> 본 문서는 텍스트북·슬라이드에서 인용된 모든 외부·내부 출처를 모은다. 인용 시 본문에서는 (¹) 식으로 번호 매기고, 여기서 펼친다.

## 일차 원문 (LangChain / DeepAgents)

1. **DeepAgents 공식 문서 — Backends**
   - 파일: `archives/original_docs/05-backends.md` (EN, 305L)
   - 한글본: `archives/original_docs/05-backends_ko.md`
   - 원본 URL: https://docs.langchain.com/labs/deep-agents/backends (확인 필요)

2. **deepagents 패키지 소스 (verbatim)**
   - 디렉토리: `archives/original_docs/deepagents_backends/`
   - 커밋 SHA: `4421bec94ffbe1f3a3bf44088ebcf8ab8c24a736`
   - 11개 모듈 (protocol/state/filesystem/store/composite/sandbox/local_shell/langsmith/context_hub/utils/__init__)
   - 자세한 카탈로그: `archives/original_docs/deepagents_backends/README.md`

## 보조 자료 (Phase 2 RESEARCH 단계에서 등재)

→ `archives/research/INDEX.md` 의 등재 목록 참조.

## 내부 자료 (langchain-docs 레포)

- week1 발표자료: `deep-agents/week1-overview-taeyoung/` (구조 참조)

## LangGraph 영속성 관련

- LangGraph Store: https://langchain-ai.github.io/langgraph/concepts/persistence/ (확인 필요)
- Checkpointer / BaseStore 인터페이스

## 인용 형식 (텍스트북 작성 시)

- 원문 인용: `[원문 §섹션 (L<line>-<line>)](archives/original_docs/05-backends.md)`
- 코드 인용: ``[`backends/state.py` L<line>-<line>](archives/original_docs/deepagents_backends/state.py)``
- 데모 코드: ``[`scripts_py/01_state_backend.py` L<line>-<line>](archives/scripts_py/01_state_backend.py)``
