# Deep Agent -> LangChain -> LangGraph 스터디 계획서

**운영 방식:** 주 1회 / 1시간 / 총 4주 진행 (방식 2 채택)
*   **1, 3주차 (이론):** 구성원 절반이 컨셉과 이론을 파악하여 20분씩 발표
*   **2, 4주차 (실습):** 나머지 절반이 코드를 직접 구동해보고 20~30분씩 시연 및 결과 발표

---

## 📖 [1주차 & 3주차] 이론 파트: 핵심 주제 및 인원 분배

### 1주차 이론: Deep Agent의 기본 구조와 환경 이해
*   **인원 1: 에이전트 개요 및 커스터마이징 구조 (20분)**
    *   **핵심 주제:** Overview, Quickstart, Customization, Models
    *   **발표 포인트:** Deep Agent가 무엇인지(Planning, Subagents, Filesystem 등의 내장 기능) 파악하고, `create_deep_agent`를 사용할 때 모델, 도구(Tools), 시스템 프롬프트 등을 어떻게 조립하는지 전체적인 청사진을 발표합니다.
*   **인원 2: 컨텍스트 관리와 기억/스킬 시스템 (20분)**
    *   **핵심 주제:** Context engineering, Memory, Skills
    *   **발표 포인트:** 에이전트가 문맥을 잃지 않도록 압축(Summarization)하고 오프로딩하는 원리와, 장기 기억(Memory, `AGENTS.md`) 및 필요할 때만 불러오는 전문 지식(Skills, `SKILL.md`)의 차이와 작동 방식을 설명합니다.
*   **인원 3: 실행 환경과 보안 (20분)**
    *   **핵심 주제:** Backends, Sandboxes, Permissions
    *   **발표 포인트:** 에이전트가 코드를 실행하고 파일을 읽고 쓰는 가상 파일시스템(Backends)의 종류, 샌드박스(Modal, LangSmith 등)를 통한 안전한 코드 실행 환경, 그리고 파일시스템 접근을 제어하는 권한(Permissions) 설정법을 다룹니다.

### 3주차 이론: 복잡한 워크플로우와 프로덕션 배포
*   **인원 7: 멀티 에이전트 협력 및 인간 개입 (20분)**
    *   **핵심 주제:** Subagents, Async subagents, Human-in-the-loop (HITL)
    *   **발표 포인트:** 컨텍스트 팽창을 막기 위해 작업을 위임하는 서브에이전트(동기/비동기)의 개념과, 민감한 도구 사용 전 인간의 승인을 받는 HITL 워크플로우를 설명합니다.
*   **인원 8: 프로덕션 배포 및 스트리밍 (20분)**
    *   **핵심 주제:** Deploy with the CLI, Going to production, Streaming
    *   **발표 포인트:** 로컬 테스트를 넘어 LangSmith Deployment로 배포하는 방법, 사용자별 메모리 격리(Multi-tenancy), 그리고 에이전트 및 서브에이전트의 실행 과정을 실시간으로 스트리밍하는 원리를 발표합니다.
*   **인원 9: 고급 프로토콜 및 프론트엔드 연동 (20분)**
    *   **핵심 주제:** Protocols (MCP, A2A, ACP), Frontend (Overview, Patterns)
    *   **발표 포인트:** 외부 도구를 연결하는 Model Context Protocol (MCP), 에이전트 간 통신(A2A), 에디터 통합(ACP)과 이를 UI(Todo list, Sandbox UI 등)에 어떻게 표현하는지 구조를 설명합니다.

---

## 💻 [2주차 & 4주차] 실습 파트: 중요도 및 인원 분배
*(이론에서 배운 내용을 코드로 직접 돌려보고 결과를 공유)*

### 2주차 실습: Deep Agent 구축 및 기본 환경 통제
*   **인원 4 [중요도: High]: Quickstart 및 CLI 기본 구동 (20분)**
    *   **진행 항목:** 기본 Research 에이전트 만들기, CLI를 통한 에이전트 실행 (`deepagents` CLI 명령어 사용).
    *   **발표 포인트:** API 키를 세팅하고 에이전트가 자체적으로 `write_todos`로 계획을 세우고 검색하는 과정을 직접 시연합니다.
*   **인원 5 [중요도: High]: Memory와 Skills 적용 실습 (20분)**
    *   **진행 항목:** 사용자 정의 `AGENTS.md` 파일 작성 및 `SKILL.md` 생성 후 에이전트 반응 변화 확인.
    *   **발표 포인트:** 특정 코딩 스타일(예: "항상 Python 타입 힌트를 써라")을 메모리에 넣었을 때와, 특정 라이브러리 사용법을 Skill 폴더에 넣었을 때 에이전트가 이를 어떻게 꺼내어 쓰는지 비교 시연합니다.
*   **인원 6 [중요도: Medium]: 샌드박스와 권한(Permissions) 제어 (20분)**
    *   **진행 항목:** 로컬 또는 클라우드 샌드박스 연결, 파일시스템 권한 차단 실습.
    *   **발표 포인트:** 에이전트에게 쉘 명령어 실행(`execute`)을 시켜보고, 특정 디렉토리(예: 민감한 파일)에 `deny` 권한을 주었을 때 접근이 차단되는 과정을 시연합니다.

### 4주차 실습: 고급 워크플로우와 프로덕션 적용
*   **인원 10 [중요도: High]: Subagent 위임과 HITL (승인) 시스템 (30분)**
    *   **진행 항목:** 메인 에이전트와 서브에이전트(예: Researcher, Coder) 구성, 특정 작업에 대한 `interrupt_on` 적용.
    *   **발표 포인트:** 메인 에이전트가 서브에이전트에게 작업을 위임하여 컨텍스트를 깔끔하게 유지하는 모습과, 파일을 쓰거나 코드를 실행하기 전 사용자에게 (y/N) 승인을 대기하는 과정을 시연합니다.
*   **인원 11 [중요도: High]: MCP 연결 및 배포(Deploy) 실습 (30분)**
    *   **진행 항목:** 외부 MCP 서버(예: 로컬 파일시스템 접근이나 날씨 API 등) 연결 및 CLI 배포.
    *   **발표 포인트:** `.mcp.json` 파일을 구성하여 에이전트가 외부 도구를 사용하는 것을 시연하고, `deepagents deploy` 명령어를 통해 LangSmith Deployment로 올리는 과정을 가볍게 보여줍니다.

---

## 🔗 주차별 GitHub 번역 문서 매핑 테이블

| 주차 | 구분 | 발제자 | 핵심 주제 | 참고해야 할 마크다운 문서 |
| :--- | :--- | :--- | :--- | :--- |
| **1주차** | 이론 | **태영** | Overview, Quickstart, Customization, Models | `01-overview_ko.md`<br>`02-quickstart_ko.md`<br>`03-customization_ko.md` |
| **1주차** | 이론 | **종훈S** | Context engineering, Memory, Skills | `04-harness_ko.md`<br>`08-long-term-memory_ko.md` |
| **1주차** | 이론 | **종훈L** | Backends, Sandboxes, Permissions | `05-backends_ko.md` |
| **2주차** | 실습 | **종훈S** | Quickstart 및 CLI 기본 구동 실습 | `02-quickstart_ko.md`<br>`10-cli_ko.md` |
| **2주차** | 실습 | **재익** | Memory와 Skills 적용 실습 | `04-harness_ko.md`<br>`08-long-term-memory_ko.md` |
| **2주차** | 실습 | **태영** | 샌드박스와 권한(Permissions) 제어 실습 | `05-backends_ko.md` |
| **3주차** | 이론 | **보현** | Subagents, Async subagents, HITL | `06-subagents_ko.md`<br>`07-human-in-the-loop_ko.md` |
| **3주차** | 이론 | **수경** | 배포(Deploy), Production, Streaming | `10-cli_ko.md` (Deploy 파트)<br>`09-middleware_ko.md` |
| **3주차** | 이론 | **세훈** | Protocols (MCP, A2A, ACP), Frontend | `09-middleware_ko.md`<br>`10-cli_ko.md` (MCP 파트) |
| **4주차** | 실습 | **11번?** | Subagent 위임과 HITL (승인) 시스템 실습 | `06-subagents_ko.md`<br>`07-human-in-the-loop_ko.md` |
| **4주차** | 실습 | **9번?** | MCP 연결 및 CLI 배포 실습 | `10-cli_ko.md` |




**혹시 인원 (9,10,11번) 안채워 지면 해당 부분은 종훈S가 커버하는 것으로 함**
