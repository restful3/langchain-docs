### §0. 들머리 — 이 글이 무엇을 다루나

이 글은 Deep Agents 라이브러리에 대한 **공통 지도** 한 장을 그리는 게 목표다.

지도 위에 표시할 정보는 셋이다.

1. **왜** 이 라이브러리가 따로 만들어졌나 — 단순 LLM 에이전트로 안 풀리던 문제는 무엇이었나
2. **무엇이** 들어 있나 — 4대 내장 능력과 그 도구 이름, 다섯 줄 Quickstart, 청사진(다이얼)
3. **언제** 쓰나 — `create_agent` / 직접 짠 LangGraph 워크플로 / `create_deep_agent` 결정 기준

이 글은 **지도** 만 그린다. 컨텍스트·메모리·스킬, 백엔드·샌드박스·권한, 미들웨어 깊이, HITL 패턴 같은 깊이 있는 주제는 별도 글에 미룬다.

이 글의 한 줄 요약:

> **Deep Agent 는 LangGraph 위에 *계획 수립 · 파일시스템 · 서브에이전트 · 장기 메모리* 4대 능력을 미들웨어로 내장한 라이브러리다. `create_deep_agent()` 한 호출로 시작하고, *Model · System Prompt · Tools* 세 다이얼로 자기 도메인에 맞춘다.**

---

### §1. 왜 Deep Agent 인가

#### §1.1. Vanilla LLM 에이전트의 한계

**한 줄**: 「LLM 한 번 + 도구 몇 개 + while 루프」 패턴은 짧은 작업에는 잘 동작하지만, 단계가 많아지면 무너진다.

LangChain `create_agent` 로 만들어 본 에이전트를 떠올려보자. 도구 호출이 가능한 모델, 도구 리스트, 시스템 프롬프트 한 장 — 이 셋만 묶으면 동작한다. 짧은 질의응답이나 함수 호출 한두 번으로 끝나는 작업에는 충분히 강력하다.

문제는 **작업이 길어질 때** 시작된다. Anthropic 의 엔지니어링 글은 에이전트가 "사람처럼" 일하게 하려면 다음 네 단계 루프가 반복돼야 한다고 정리한다 — **gather context → take action → verify work → repeat**[^2]. 이 루프를 단순 ReAct 한 줄로 돌리면 세 가지 지점에서 깨진다 (표.1).

**표.1**: Vanilla 에이전트가 깨지는 세 지점

| 깨지는 지점 | 무엇이 일어나는가 |
|---|---|
| 컨텍스트 오버플로 | 검색 결과·문서·대화 이력이 누적돼 모델 컨텍스트 윈도우를 잡아먹는다. 30회 검색 이후엔 시스템 프롬프트마저 잘려 나간다. |
| 계획의 부재 | 모델이 "다음 단계" 를 매 턴 즉흥으로 결정. 중간에 길을 잃거나 같은 검색을 반복한다. |
| 위임 불가 | 한 모델 인스턴스가 모든 컨텍스트를 들고 있으니, 무거운 하위 작업이 메인 흐름을 오염시킨다. |

세 지점이 따로 무너지는 게 아니라 **같은 한 가지 원인** 에서 함께 무너진다는 점이 중요하다. Vanilla 패턴은 컨텍스트 윈도우를 **하나만** 가진다. 한 모델 인스턴스의 토큰 슬롯 안에 시스템 프롬프트, 도구 정의, 메시지 이력, 도구 호출 결과가 모두 한꺼번에 들어간다. 검색 결과가 누적되면 그 슬롯이 차고(오버플로), 모델이 다음 turn 을 시작할 때 자기 계획을 적어 둔 곳이 없어 즉흥 결정을 반복하고(계획 부재), 무거운 하위 작업의 모든 turn 기록이 같은 슬롯을 더 채워 메인 흐름을 오염시킨다(위임 불가). 단일 슬롯이 깨지는 순간 셋이 동시에 깨진다.

구체 시나리오 한 컷 — 사용자가 "랭체인 미들웨어 16종 비교" 를 묻고 모델이 한 미들웨어당 두세 번 검색을 하다 보면 turn 30 즈음에 검색 결과 캐시가 토큰의 60\~80% 를 먹는다. 다음 turn 에 모델은 시작할 때 세웠던 계획 — 자기가 무엇을 찾으려 했는지 — 을 다시 떠올리지 못하고, 시스템 프롬프트의 후반부(보통 도구 호출 정책)가 잘려 나가면서 도구 호출이 거의 무작위에 가까워진다. 빌트인 도구가 적절하지 않다고 판단해 같은 검색을 다시 부르고, 또 같은 결과가 슬롯을 차지한다. 이 시점에 "왜 무거운 하위 작업을 통째로 다른 인스턴스에 맡기지 않는가" 라는 질문이 자연스럽게 따라온다 — Vanilla 패턴이 그 자리를 비워 두기 때문이다.

**그림.1**: Vanilla 에이전트 vs Deep Agent — 같은 입력에 대한 두 흐름

![Vanilla vs Deep Agent 비교](figs/fig01_vanilla_vs_deep_agent.svg)

**그림 1**은 같은 입력에 대한 두 흐름을 좌우로 나란히 보여준다. 좌측은 LangChain `create_agent` 로 만든 단순 에이전트의 흐름이다 — User → LLM ↔ Tool 의 한 루프가 응답을 만든다. 단계가 다섯 정도까지는 잘 동작하지만, 그 이상 누적되면 표.1 의 세 지점이 한꺼번에 무너진다. 우측은 `create_deep_agent` 의 흐름이다. LLM 호출 사이에 **미들웨어 체인** 한 켜가 끼어 들어가 매 turn 마다 (1) 계획을 갱신하고, (2) 큰 결과를 가상 파일시스템에 오프로드하고, (3) 무거운 하위 작업은 서브에이전트로 위임한다. 모델이 사용하는 도구 풀도 **빌트인 9종 + 사용자 도구** 로 두꺼워진다.

왜 두 그림이 이렇게 갈라지는가. Anthropic 의 4단계 루프 — *gather context → take action → verify work → repeat*[^2] — 가 단계 다섯 정도까지는 한 LLM 호출 안에 다 들어간다. 짧은 컨텍스트에서는 모델이 스스로 계획을 세우고, 도구를 부르고, 결과를 검증하고, 다음 단계를 정한다. 단계가 늘면 표.1 의 세 지점이 한꺼번에 무너지면서 그 4단계가 한 호출에 더는 다 담기지 못하게 된다. 우측 흐름은 4단계를 한 호출에 욱여넣지 않고 미들웨어 체인이 단계별로 분담한다 — TodoListMiddleware 가 *gather context* 의 계획 단계를 떠받치고, FilesystemMiddleware 가 *take action* 으로 쌓이는 결과를 받아 두고, SubAgentMiddleware 가 *verify* 와 *repeat* 의 무거운 부분을 격리한다.

이 그림이 본 글의 출발점이다. 좌측이 어떤 단계에서 무너지는지, 우측이 무엇을 새로 더해 그 무너짐을 막는지 — 이 둘의 차이가 §2 부터 본격적으로 풀어 갈 4대 능력의 존재 이유다. 결과적으로 단계 50개를 넘는 작업도 컨텍스트를 깔끔하게 유지하며 진행할 수 있게 된다. 다음 절(§1.2) 이 좌측이 우측으로 진화한 세 폐쇄 시스템을 보여준다.

Vanilla 패턴은 **컨텍스트를 외부화** 할 곳도, **계획을 명시화** 할 자리도, **컨텍스트를 격리** 할 경계도 없다. 단계 5개까지는 견디지만 50개에서는 무너진다. 표.1 의 세 지점을 굳이 우선순위로 따지면 가장 먼저 부딪히는 것이 **컨텍스트 오버플로** 다 — 모델 윈도우가 차오르는 속도가 가장 빠르기 때문이다. 그러나 가장 먼저 인지되는 것은 **계획 부재** 다 — 사용자가 "왜 같은 검색을 또 했지" 라고 느끼는 순간이 가장 눈에 띈다. 가장 늦게 인지되는 것이 **위임 불가** 인데, 이는 "왜 메인 응답이 무거운 보조 작업의 디테일에 흔들리지" 라는 형태로 한 단계 더 추상적으로 나타난다. 세 지점을 서로 다른 시점에 만나면서도 그 원인이 한 가지(단일 컨텍스트 윈도우)임을 발견한 것이 세 폐쇄 시스템 — Claude Code · Deep Research · Manus — 이 각자의 방식으로 같은 답에 도달하게 만든 길이며, 그 사실이 deepagents 의 출발점이다.[^1]

#### §1.2. 문제를 해결한 3가지 사례

**한 줄**: 폐쇄 시스템 셋이 같은 패턴으로 수렴했다 — 계획 파일, 가상 파일시스템, 서브에이전트.

##### Claude Code (Anthropic)

Anthropic 은 자사 코드 어시스턴트의 설계 원리를 한 문장으로 압축한다 — *"에이전트에 컴퓨터를 쥐여 주어, 사람이 일하듯 일하게 하라"*[^2]. 사람이 컴퓨터에서 일할 때 쓰는 도구 카테고리를 그대로 모델에 준다는 발상이다. **파일시스템(filesystem)**, **에이전틱 검색(agentic search)**, **시맨틱 검색(semantic search)**, **서브에이전트(subagents)**, **컴팩션(compaction)**, **셸·스크립트(bash & scripts)**, **코드 생성(code generation)**, **MCP** [^2]. 이 중 파일시스템·서브에이전트·컴팩션은 deepagents 의 4대 능력 중 셋과 그대로 겹친다. Claude Code 가 만난 구체적 한계는 분명했다 — 코드베이스가 수백 파일·수십만 라인으로 커지면 모델이 한 호출에 모든 파일을 읽을 수 없고, 그 모든 내용을 컨텍스트에 들고 있을 수도 없다. 컨텍스트 슬롯에 모두 우겨 넣지 않고 **필요할 때 도구로 가져오는** 패턴(파일시스템 + 검색)이 그 한계의 답이었다.

##### OpenAI Deep Research

OpenAI 의 자율 리서치 에이전트는 **5단계 프로세스** 로 한 질의를 처리한다 — Clarification → Decomposition → Iterative Search → Multi-format Reading → Synthesis with Citations[^3]. 핵심은 두 번째와 세 번째: 큰 질문을 작은 작업으로 **분해(decomposition)** 하고, 각 작업을 ReAct 루프(Plan → Act → Observe)로 돌린다. 한 작업당 평균 30\~60회 검색, 120\~150 페이지 읽기, 추론 150\~200 iteration[^3]. 이 규모에서는 컨텍스트 외부화와 계획 명시화 없이 동작 자체가 불가능하다. 검색 60회 누적 시점에는 단일 컨텍스트 윈도우가 이미 검색 결과로 가득 차 모델이 다음에 무엇을 찾을지 결정하기 어려워진다 — Deep Research 의 5단계 가운데 첫 두 단계(Clarification, Decomposition)가 이 한계를 사전에 분산시키는 장치다.

##### Manus

Manus 는 Claude 3.5/3.7 + 파인튜닝된 Qwen 위에 만들어진 자율 에이전트로, **CodeAct** 패러다임을 쓴다 — 도구 호출 대신 모델이 짧은 Python 스크립트를 생성하면 샌드박스가 실행한다[^4]. 루프는 **Analyze → Plan/Select → Execute → Observe**, 진행 상황은 가상 파일시스템 안의 `todo.md` 에 기록된다[^4]. 웹 브라우징·코딩·데이터 분석은 각각 격리된 서브에이전트가 맡고, 메인 에이전트는 이벤트 스트림으로 결과만 받는다[^4]. **계획 파일 + 가상 파일시스템 + 서브에이전트** — Claude Code 와 같은 세 축이다. Manus 가 그 세 축을 발견한 길은 또 달랐다 — 자율 에이전트가 한 turn 에 5\~10분 일한 뒤 다음 사용자 메시지에서 어디까지 했는지 잊지 않으려면 진행 상황이 **모델 컨텍스트 밖에** 있어야 했고, `todo.md` 가 그 자리를 잡았다. 메인 컨텍스트가 깨끗해야 다음 사용자 입력을 받을 여유가 생긴다는 깨달음이 multi-agent 분리로 이어졌다.

세 시스템의 진화 경로를 비교하면 한 가지 패턴이 또 보인다 — 셋 다 **출발은 단일 LLM 호출** 이었지만, 실제 사용자가 자율적인 작업을 맡기기 시작하자 같은 한계에 부딪혔고, 같은 답으로 진화했다. Claude Code 는 처음에 코드 한두 파일을 다루는 어시스턴트로 출발했다가 코드베이스 전체를 읽고 수정하는 방향으로 커졌고, Deep Research 는 처음에 한두 검색의 답을 만드는 도구였다가 보고서 한 편을 자동으로 만드는 방향으로 커졌고, Manus 는 처음에 짧은 작업을 맡기는 에이전트였다가 사용자가 떠난 사이 5\~10분 자율로 일하는 방향으로 커졌다. 모두 같은 곳 — **컨텍스트 슬롯의 단일성** — 에서 막혔고, 모두 같은 자리에 4대 능력을 박아 그 막힘을 풀었다.

> **세 시스템의 공통 분모** (Harrison Chase 의 정리)[^1]:  
> *"Deep agent 란 **계획(planning)** 을 수행하고, **서브에이전트(sub agents)** 를 사용하며, **파일시스템(file system)** 에 접근할 수 있고, **잘 다듬어진 프롬프트(detailed prompt)** 를 가진 에이전트다."*

**그림.2**: 세 시스템이 같은 디자인 축으로 수렴

![세 시스템의 공통 분모](figs/fig02_three_systems_common_pattern.svg)

**그림 2**는 세 시스템의 디자인이 어떻게 같은 네 축으로 수렴하는지를 한 장에 묶는다. 상단의 세 시스템은 출시 주체도 다르고(Anthropic / OpenAI / Manus 팀), 노출 방식도 다르고(코드 어시스턴트 / 자율 리서치 / 자율 에이전트), 구현 디테일도 다르다. Claude Code 는 사람이 컴퓨터에서 쓰는 도구를 그대로 모델에 쥐여 주는 8종의 카테고리(파일시스템·서브에이전트·컴팩션 등)로 표면을 만든다[^2]. Deep Research 는 한 질의를 5단계로 풀고 한 작업당 검색 30\~60회·페이지 120\~150장을 누적한다[^3]. Manus 는 가상 파일시스템 안의 `todo.md` 와 도메인별 multi-agent 분리 구조로 같은 규모를 다룬다[^4]. 그러나 한 발짝 떨어져서 보면 같은 네 가지 축이 보인다 — 계획을 명시 기록하는 자리(Planning), 큰 컨텍스트를 빼두는 자리(Filesystem), 무거운 하위 작업을 격리해 위임하는 자리(Subagents), 그리고 이 모든 것을 모델이 "사용하게" 만드는 한 장의 잘 짜인 시스템 프롬프트(Detailed prompt).

왜 이 수렴이 의미 있는가. 세 팀이 서로 모르고 만든 시스템이 같은 네 축으로 정착했다는 사실 자체가 이 추상화의 "안전성" 근거다. 실험적 변덕이 아니라 **같은 한계** (단일 컨텍스트 윈도우)를 만난 세 시스템이 **같은 답** 에 도달했다는 뜻이다. Harrison Chase 의 출시 발표[^1]는 이 관찰에 기댄다 — 검증된 세 패턴의 교집합을 추상으로 끌어올려 라이브러리로 묶은 것이 deepagents 다.

독자가 이 그림에서 가져갈 것은 두 가지다. 하나, 다음 절부터 다룰 4대 능력은 한 사람의 디자인 결정이 아니라 세 시스템에서 공통으로 검증된 패턴의 추출이라는 점 — "왜 하필 이 넷인가" 라는 질문에 그림 2 가 답한다. 둘, 1주차 이후 다음 발제들이 다룰 깊이(컨텍스트·메모리·스킬, 백엔드·샌드박스·권한 등)는 모두 이 네 축 중 하나의 변형이거나 그 사이를 잇는 다리라는 점 — §6 의 "다음 주차로 가는 다리" 도 그림 2 의 같은 좌표 위에 놓인다.

#### §1.3. 패턴의 일반화 — 라이브러리화

**한 줄**: 네 축(계획·파일시스템·서브에이전트·디테일한 프롬프트)을 LangGraph 위에 미들웨어로 박아 라이브러리로 묶은 것이 deepagents 다.

Harrison Chase 가 LangChain Blog 에 올린 출시 발표[^1]는 영감의 출처를 명시한다 — Claude Code 가 1차 영감, Deep Research 와 Manus 가 추가 검증. 핵심 결정은 두 가지다.

1. **새 프레임워크가 아니라 라이브러리** 로. LangGraph 를 그대로 깔고 그 위에 미들웨어 한 켜를 올린다 — `create_deep_agent()` 의 반환 타입은 `CompiledStateGraph` 다[^5]. 즉 지금 쓰는 LangGraph 도구·관측성·배포 인프라가 그대로 쓰인다.
2. **선택을 강요하지 않는다**. 4대 능력은 모두 미들웨어 형태로 들어 있어 켜고 끌 수 있다 — to-do list 미들웨어, Filesystem 미들웨어, Subagent 미들웨어 등이 LangChain core 의 prebuilt middleware 카탈로그(16종) 안에 함께 정리돼 있다[^6].

라이브러리 vs 프레임워크 의 결정에는 비용과 이익이 갈린다. 둘의 차이는 *제어 흐름의 주인이 누구인가* 다 — **라이브러리** 에서는 사용자 코드가 라이브러리를 부르고, **프레임워크** 에서는 프레임워크가 사용자 코드를 부른다 (*Inversion of Control*). deepagents 가 라이브러리라는 말은 진입점이 사용자에게 있어 사용자가 직접 `agent.invoke()` 를 호출하고, 그 결과 LangSmith 추적·LangGraph Platform 배포·체크포인터·Store 같은 기존 인프라가 그대로 굴러간다는 뜻이다 — 사용자는 LangGraph 를 이미 안다는 부담을 떠안지만, 그 인프라를 두 번 학습할 필요가 없다. 프레임워크였다면 진입점이 deepagents 쪽에 있어 사용자는 정해진 슬롯(콜백, 설정, 베이스 클래스 추상 메서드)에 자기 코드를 끼우고 루프·스케줄링은 deepagents 가 돌렸을 것이며, deepagents 가 자체 런타임·관측성·배포 도구를 따로 만들고 사용자는 두 생태계 사이에서 어느 쪽이 어느 책임을 지는지 매 결정마다 따져야 했을 것이다. Harrison Chase 의 Acknowledgements[^1]가 "Claude Code 에서 영감을 받았고 그것을 더 일반화한다" 라고 적은 것은 이 맥락에서 읽힌다 — 새 추상을 도입하지 않고 기존 추상의 사용 패턴만 추출했다는 뜻이다.

같은 결정의 또 다른 결과 한 가지 — 미들웨어가 LangChain core 의 prebuilt middleware 카탈로그(16종)에 같이 정리돼 있다는 사실이다[^6]. 즉 deepagents 의 4대 능력 미들웨어는 deepagents 안에 갇혀 있지 않고, LangChain core 가 제공하는 미들웨어 표준의 한 인스턴스다. 사용자가 `create_agent` 만 쓰면서 deepagents 의 `FilesystemMiddleware` 한 개만 끼우는 사용도 가능하고, 반대로 `create_deep_agent` 가 디폴트로 까는 미들웨어를 명시적으로 빼는 것도 가능하다. 이 양방향 호환이 라이브러리 결정의 가장 큰 실용적 이득이다 — "전부 쓰거나 전부 안 쓰거나" 가 아니라, 필요한 만큼만 끼울 수 있다.

16종 미들웨어와 4대 능력의 관계를 보면 deepagents 의 의미가 더 명확해진다. 16종은 LangChain core 가 제공하는 "에이전트가 흔히 필요로 하는 보강 한 켜" 의 카탈로그다 — Summarization, Human-in-the-loop, Model fallback, PII detection 등 다양한 영역. 4대 능력은 그 16종 중에서 **자율성이 높아질 때 가장 자주 같이 켜지는 조합** 의 추출이다 — Todo list + Filesystem + Subagent. deepagents 는 이 조합을 라이브러리화하면서 BASE_AGENT_PROMPT 한 장과 미들웨어 체인 순서까지 묶었다. 사용자가 그 조합 전체를 쓰고 싶으면 `create_deep_agent` 한 호출이고, 부분만 쓰고 싶으면 `create_agent` 에 미들웨어를 직접 끼우는 길이 열려 있다.

**스택 위치** 를 한 그림으로 본다.

**그림.3**: deepagents 의 스택 위치

![deepagents 스택 위치](figs/fig03_stack_position.svg)

**그림 3**은 deepagents 가 LangGraph 생태계 안에서 어디에 끼는지를 4단 스택으로 보여준다. 가장 아래에는 **LangGraph** 가 있다 — `StateGraph`, 체크포인터(thread 상태 영속), Store(thread 횡단 영속) 같은 그래프 실행·상태 관리 인프라를 제공한다. 그 위에 **LangChain** 이 올라가 ChatModel · Runnable · 도구 호출 표준을 통일한다. **deepagents 는 그 위 한 켜** 다 — 4대 능력을 미들웨어 형태로 박아 넣고 `BASE_AGENT_PROMPT` 한 장을 합성한다. 가장 위는 **사용자** 가 채우는 칸 — `model=`, `tools=`, `system_prompt=` 셋이 디폴트로 가장 자주 만지는 다이얼이다.

왜 이렇게 얹었나. `create_deep_agent()` 의 반환 타입이 새 추상이 아니라 LangGraph 의 `CompiledStateGraph` 다[^5]. 즉 라이브러리는 LangGraph 위에 별도 런타임을 만들지 않았고, 같은 `.invoke / .stream / .ainvoke / .astream` API 가 그대로 작동한다. §1.3 에서 본 라이브러리 결정[^1]의 무게가 바로 이 한 줄(반환 타입)에 압축돼 있다 — LangSmith 추적·LangGraph Platform 배포·체크포인터·Store 가 모두 별도 학습 없이 그대로 쓰인다.

이 그림이 나머지 모든 절의 좌표다. §2 가 그 한 켜 안의 4대 능력을 푼다. §3 이 그 한 켜를 켜는 5줄 코드를 보여준다. §4 가 그 한 켜의 17개 파라미터(다이얼)를 정리한다. §5 가 언제 이 한 켜를 끼우고 언제 빼야 하는지 결정한다. 매 절이 이 그림 어디쯤에 있는지 자기 위치를 잊지 않는 것이 1주차 발표를 따라가는 가장 빠른 길이다.

---

### §2. 4가지 내장 능력

**§2 한 줄**: 비서에게 「할 일 목록·노트·인턴·일기장」 을 쥐여 준다 — Planning · Filesystem · Subagents · Long-term Memory.

**그림.4**: 4대 내장 능력의 비유 — Deep Agent 는 잘 갖춰진 비서

![4대 능력 비유](figs/fig04_four_capabilities_metaphor.svg)

**그림 4**는 4대 능력을 일상의 비서 비유로 옮긴 것이다. **계획 수립(Planning)** 은 비서의 "할 일 목록" 이다 — 큰 작업을 시작 전에 4\~7개 항목으로 쪼개 적어두고, 한 항목씩 끝낼 때마다 체크 표시를 한다. **파일시스템(Filesystem)** 은 비서의 "노트" 다 — 책상에 늘 펼쳐 둘 수 없는 큰 자료는 노트에 적어 서랍에 넣어 두고, 필요할 때만 꺼내 본다. **서브에이전트(Subagents)** 는 "인턴" 이다 — 무거운 하위 작업은 인턴에게 통째로 맡기고, 본인은 인턴이 들고 온 한 단락짜리 요약만 받는다. **장기 메모리(Long-term Memory)** 는 "일기장" 이다 — 매일의 책상은 비우지만, 일기장은 1년 뒤에도 남아 다음 해의 결정을 돕는다.

각 비유는 미들웨어 한 개 + 도구 한두 개로 정확히 매핑된다. 할 일 목록 ↔ `TodoListMiddleware` ↔ `write_todos`, 노트 ↔ `FilesystemMiddleware` ↔ `ls`/`read_file`/`write_file`/`edit_file`, 인턴 ↔ `SubAgentMiddleware` ↔ `task`, 일기장 ↔ Store(영속 계층) ↔ `/memories/` 경로[^6]. 16종이 정리된 LangChain core 의 prebuilt middleware 카탈로그[^6] 중 deepagents 가 기본으로 켜는 것이 위 셋(+ `SummarizationMiddleware`, `PatchToolCallsMiddleware` 등 보조)이며, `create_deep_agent` 인자로 미들웨어를 빼거나 추가로 갈아 끼울 수 있다. 즉 4대 능력은 라이브러리에 박힌 닫힌 집합이 아니라 사용자가 켜고 끌 수 있는 모듈식 조립이다.

비유가 직관적이어서 이해는 빠르지만 한 가지 단서를 붙여 둬야 한다 — 모델은 비서와 달리 매 turn 같은 컨텍스트로 처음부터 다시 시작하는 "기억력 없는 비서" 다. 이 점 때문에 일기장(Store)이 비유에서 단순 부록이 아니라 **결정적**인 자리를 차지한다. 단기 책상(state)에서 사라지는 정보가 일기장(store)에 남아 다음 thread 의 비서가 1년 뒤에도 참조할 수 있다는 것이 deepagents 의 메모리 디자인이다 — §2.4 에서 짧은 코드로 다시 본다. 4대 능력 사이의 우선순위도 비유에서 보인다 — 노트와 일기장이 빠지면 큰 작업 자체가 굴러가지 않고, 할 일 목록이 빠지면 매 turn 즉흥이 되고, 인턴이 빠지면 메인 비서가 무거운 일을 모두 떠안는다.

원문 01-overview 가 `핵심 기능` 절에서 짧게 짚고 넘어가는 4가지를 한 절씩 푼다. 각 능력의 **도구 이름** 은 `create_deep_agent` 의 빌트인 도구 리스트에서 가져온다 — `write_todos`, `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `execute`, `task`[^5].

#### §2.1. Planning — `write_todos`

**한 줄**: 모델이 "다음 단계" 를 즉흥으로 정하는 대신, 자기 계획을 파일로 적어놓고 그 파일을 보며 일한다.

내장 `write_todos` 도구는 **TodoListMiddleware** 가 제공한다[^6]. 모델이 작업 시작 시 할 일을 4\~7개 항목으로 쪼개어 todo 리스트로 기록하고, 한 항목을 끝낼 때마다 `[x]` 표시를 붙이며 진행 상황을 추적한다. 항목이 부족해 보이면 추가, 더 이상 의미 없으면 삭제 — 계획 자체를 살아 있는 문서로 다룬다.

이 발상의 뿌리는 두 곳이다.

- Claude Code 의 BASE_AGENT_PROMPT 안에 명시된 **Understand → Act → Verify** 3단 워크플로[^7] — 행동 전에 이해하고, 행동 후 검증한다.
- Manus 의 `todo.md` 패턴[^4] — 진행 상황을 파일로 외부화하면 모델이 컨텍스트 윈도우를 다 쓰고 다음 턴으로 넘어가도 계획이 살아남는다.

`write_todos` 가 만들어내는 출력은 보통 다음 모양이다 (실행 중 캡처 예시):

```text
- [x] 1. langgraph 의 핵심 추상 4가지 정의
- [x] 2. 각 추상이 LangChain 과 어떻게 다른지 정리
- [ ] 3. 코드 예제로 StateGraph + Send 패턴 시연
- [ ] 4. 보고서 초안 작성
```

이 한 장이 `agent.invoke()` 가 "백그라운드에서 일하는 동안" 의 진행 추적기 역할을 한다 — §3.4 에서 다시 본다.

todo 항목의 라이프사이클을 한 번 따라가 보면 패턴이 명확해진다. 모델은 작업을 시작할 때 4\~7개 항목을 한 번에 적는다(`status: pending` 으로). 한 항목을 시작하기 직전에 그 항목을 `in_progress` 로 바꾸고, 끝나면 `completed` 로 갱신한다. 도중에 작업의 모양이 바뀌면 항목을 추가하거나 제거하기도 한다. 매 turn 의 시스템 프롬프트에 todo 의 현재 상태가 함께 주입되기 때문에, 모델은 자기가 어디까지 했는지를 외부 메모리(state 의 `todos` 슬롯)로 잠시 외부화했다가 다시 읽어 들이는 셈이다 — 단일 컨텍스트 윈도우의 단일성을 부분적으로 회피하는 트릭이다.

**한 가지 흥미로운 사실** — `write_todos` 는 시스템에 어떤 물리적 변화도 일으키지 않는 **no-op 도구**다. Harrison Chase 의 출시 발표[^1]에 직접 언급된다:

> "Claude Code 는 Todo list 도구를 쓴다. 재미있는 사실 — 이 도구는 사실상 아무것도 하지 않는다! 거의 no-op 이다."

진짜로 어딘가에 todo list 가 저장되고 추적되는 게 아니라, 모델이 "할 일을 한 번 적어두는 행위" 자체가 컨텍스트에 계획을 남겨 다음 turn 의 모델이 자기 계획을 잊지 않게 만드는 **컨텍스트 엔지니어링 트릭**이다. 도구가 하는 일은 모델이 적은 todo 텍스트를 그대로 state 의 `todos` 슬롯에 박아두는 것뿐 — 그래도 효과가 큰 이유는, 다음 turn 의 시스템 프롬프트에 그 todo 가 다시 들어가 모델이 자기 계획을 매 turn 마주하기 때문이다.

이 "사실상 no-op 인데 효과가 크다" 라는 지점이 deepagents 의 디자인 철학을 압축한다 — 모델 자체를 바꾸지 않고도 모델이 더 잘 일하도록 만드는 가장 가벼운 길은 **모델이 자기 자신에게 메모를 남기게** 만드는 것이다. todo 를 적는 도구가 메모리도, 영속성도, 추적도 보장하지 않지만, 다음 turn 의 입력으로 그 todo 를 다시 흘려 넣어 주는 행위 하나가 모델의 판단 품질을 끌어올린다. 같은 트릭이 Filesystem 에도 적용된다 — `write_file` 한 번이 모델 컨텍스트에서 텍스트를 빼는 동시에 파일 이름이라는 짧은 핸들로 그 자리를 채운다. 4대 능력 모두 이 패턴의 변주다.

효과를 측정하는 방법은 단순하다. 같은 작업을 두 번 돌려 보면 된다 — 한 번은 `TodoListMiddleware` 를 켜고(디폴트), 한 번은 `middleware=` 로 명시적으로 빼고. 검색 30회 이상 누적되는 작업에서는 켠 쪽이 같은 검색을 반복하지 않고 4\~7개 todo 항목을 선형으로 끝내는 반면, 끈 쪽은 turn 15 즈음부터 모델이 "이걸 이미 찾았던가" 를 매 turn 다시 물으며 토큰을 태운다. 비결정성 때문에 한 번의 비교로 단정할 수는 없지만, 도구 호출 로그(LangSmith 트레이스)를 켜고 같은 질문을 5\~10회 돌려 보면 todo 가 켜진 쪽의 turn 수와 토큰 사용량이 평균적으로 더 작다는 패턴이 보인다 — 이 차이가 "no-op 도구가 효과를 내는 이유" 의 가시화다.

#### §2.2. Filesystem — `ls` / `read_file` / `write_file` / `edit_file`

**한 줄**: 큰 검색 결과·중간 산출물을 모델 컨텍스트에서 빼서 가상 파일시스템에 적어두고, 필요할 때 읽는다.

`FilesystemMiddleware`[^6] 가 네 개의 핵심 도구를 추가한다 (표.2).

**표.2**: Filesystem 미들웨어가 추가하는 4개 도구

| 도구 | 역할 |
|---|---|
| `ls()` | 가상 파일시스템의 파일 일람 |
| `read_file(path, offset, limit)` | 큰 파일을 페이지 단위로 읽기 |
| `write_file(path, content)` | 새 파일 작성 |
| `edit_file(path, old_str, new_str)` | 부분 치환 (줄 단위 정확 매칭) |

여기에 `glob`, `grep` 같은 검색 도구도 함께 노출된다[^5].

이 가상 파일시스템은 **Backend** 라는 추상으로 한 단 더 깊어진다 — `StateBackend`(LangGraph state 안에 임시 보관, 기본값) / `StoreBackend`(LangGraph Store 에 영구 보관) / `CompositeBackend`(prefix 별로 다른 backend 로 라우팅, 예: `/memories/` 는 Store, 나머지는 State)[^6]. 이 한 줄이 §2.4 장기 메모리와 자연스럽게 이어진다.

3종 backend 의 사용은 짧은 한 블록으로 시각화된다 (공식 가이드 발췌)[^6]:

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

# 디폴트 — 한 thread 안에서만 살아남는 임시 파일시스템
agent_default = create_deep_agent()  # StateBackend 가 자동으로 깔림

# Composite — /memories/ 는 영속, 나머지는 임시
make_backend = lambda rt: CompositeBackend(
    default=StateBackend(rt),
    routes={"/memories/": StoreBackend(rt)},
)
agent_composite = create_deep_agent(
    backend=make_backend,
    store=InMemoryStore(),
)
```

세 줄 코드 안에 두 개의 라우팅 정책이 들어 있다 — 디폴트는 모든 경로를 state 에, Composite 는 `/memories/` 만 store 로. 더 긴 prefix 가 짧은 prefix 를 재정의하는 우선순위 규칙도 있어 `routes={"/memories/projects/": ..., "/memories/": ...}` 같은 중첩 라우팅이 가능하다. `BackendProtocol` 을 구현한 사용자 정의 백엔드(예: S3, Postgres)도 같은 자리에 끼워 넣을 수 있어 스토리지 정책이 라이브러리 외부에서도 자유롭다.

**그림.5**: Filesystem Backend 라우팅 — 같은 도구, 다른 저장소

![Filesystem Backend 라우팅](figs/fig05_filesystem_backend_routing.svg)

**그림 5**는 같은 `write_file` 호출이 경로(prefix)에 따라 어떻게 다른 저장소로 라우팅되는지 보여준다. 모델은 `write_file` 한 도구만 알지만, 그 호출이 실제 어디에 저장되는지는 **경로(prefix)** 가 결정한다. `CompositeBackend` 가 `/memories/` 로 시작하는 경로는 `StoreBackend` (LangGraph Store, thread 횡단 영구) 로, 그 외 경로는 `StateBackend` (LangGraph state, 한 thread 안에서만) 로 라우팅한다.

라우팅 규칙을 짧은 의사코드로 풀면 명확하다 — `if path.startswith("/memories/"): store_backend.write(path, content) else: state_backend.write(path, content)`[^6]. 실제 구현은 `deepagents/backends.py` 의 `CompositeBackend` 안에 있고, 프로토콜이 `BackendProtocol` 한 개로 통일돼 있어 모든 backend 가 같은 6개 엔드포인트(`ls_info`, `read`, `grep_raw`, `glob_info`, `write`, `edit`)를 노출한다. 모델은 어느 경로가 어디로 가는지 신경 쓰지 않고 `write_file` 한 도구만 호출한다.

이 디자인이 의미하는 것 — 모델이 단기/장기 메모리를 구별하는 별도 도구를 학습할 필요가 없다. 같은 `write_file` 호출로 일관된 추상을 다루며, 미들웨어 한 켜를 갈아 끼우면 저장소 정책이 통째로 바뀐다. §2.4 가 이 디자인을 영속 메모리 사례로 풀어 보인다 — 그림 5 가 그 다리이며, 4대 능력의 두 번째(Filesystem)와 네 번째(Long-term Memory)가 같은 미들웨어 안에 있다는 사실의 가시화다.

**왜 이게 컨텍스트 관리인가** — 검색 결과를 그대로 모델에 다 박으면 한 턴에 5\~10K 토큰이 먹힌다. 검색 결과를 `write_file("results/search_01.md", ...)` 로 빼두고, 본문에는 "결과는 search_01.md 에 저장됨" 한 줄만 남기면 모델 컨텍스트는 간결하게 유지되고, 다음 턴에 필요한 부분만 `read_file` 로 끌어올 수 있다. 이게 Anthropic 이 말한 **compaction** 의 LangGraph 버전이다[^2].

`read_file` 도 같은 디자인 덕에 **부분 읽기** 가 가능하다 — `read_file(path, offset=100, limit=50)` 으로 100\~150번째 줄만 가져온다. 모델은 "큰 파일을 한 번에 다 읽어야 한다" 는 부담을 지지 않고 필요한 부분만 끌어올 수 있다. `edit_file` 도 마찬가지로 부분 치환(`old_string` → `new_string`)이라 큰 파일을 통째로 다시 쓰지 않는다. 4개 도구가 모두 "큰 컨텍스트를 모델 밖으로 옮기되, 모델이 필요할 때만 부분적으로 끌어오는" 같은 디자인 결을 따른다는 점이 핵심이다.

#### §2.3. Subagents — `task`

**한 줄**: 무거운 하위 작업은 격리된 서브에이전트에 위임 — 메인 컨텍스트가 깨끗해진다.

`SubagentMiddleware`[^6] 가 `task` 도구 하나를 더한다. 메인 에이전트는 `task` 를 호출해 하위 작업을 띄울 수 있고, 디폴트로 **"general-purpose"** 라는 범용 서브에이전트가 항상 존재한다[^6]. 이 디폴트 서브에이전트는 **메인 에이전트와 동일한 도구 풀**을 가진 단순한 복제다 — 실질적으로 "메인의 똑같은 카피본인데 컨텍스트만 격리된 또 한 명" 인 셈이다. 사용자가 도메인 전용 서브에이전트(예: 코딩 전용·검색 전용)를 추가로 정의하면 그것도 후보에 추가된다.

API 레퍼런스는 서브에이전트를 세 형식으로 받는다고 명시한다[^5] — `SubAgent` (선언형 동기), `CompiledSubAgent` (이미 컴파일된 runnable), `AsyncSubAgent` (원격/백그라운드). 이 글에서는 가장 일반적인 `SubAgent` (선언형) 만 다루고, async/compiled 까지 확장되는 패턴은 별도 글에 미룬다.

서브에이전트가 격리해 주는 것은 두 가지다.

1. **컨텍스트** — 서브에이전트는 자기만의 메시지 히스토리·도구 로그를 가지고 일한다. 메인 에이전트에게는 최종 결과(짧은 요약 또는 문서 한 편)만 돌아온다.
2. **권한** — 서브에이전트마다 도구 풀을 다르게 줄 수 있다. 예: 코드 실행 권한은 코드 서브에이전트에만, 검색은 리서치 서브에이전트에만.

디폴트 `general-purpose` 서브에이전트와 사용자 정의 서브에이전트는 짧은 한 블록으로 비교된다 (공식 가이드 발췌)[^6]:

```python
# 디폴트 — 추가 정의 없이 task 도구가 자동으로 켜진다
agent_default = create_deep_agent(
    model="claude-sonnet-4-6",
    tools=[internet_search],
)
# 메인이 task("research-question", ...) 을 호출하면
# general-purpose 서브에이전트(메인과 동일 도구·동일 모델)가 응답

# 사용자 정의 — 도메인 격리 + 권한/모델 별도
research_subagent = {
    "name": "research-agent",
    "description": "Used to research more in depth questions",
    "system_prompt": "You are a great researcher",
    "tools": [internet_search],          # 메인 도구 풀 일부만
    "model": "openai:gpt-4o",            # 메인 모델과 다른 모델
}
agent_custom = create_deep_agent(
    model="claude-sonnet-4-6",
    subagents=[research_subagent],
)
```

위 코드 두 단의 차이가 서브에이전트의 두 모드를 구분한다. 디폴트는 "메인의 카피본인데 컨텍스트만 격리된 또 한 명" 이라 가장 빠르게 위임 패턴을 켤 수 있고, 사용자 정의는 도구·모델·시스템 프롬프트를 도메인에 맞게 좁힌다. 권한 격리의 실용 시나리오 한 줄 — 메인 에이전트는 셸을 못 만지지만 코딩 서브에이전트만 `execute` 도구를 가지게 만들면, 메인이 위임 결정을 잘못해도 셸 명령이 메인 컨텍스트로 돌아오지 않는다. 이 분리가 보안·감사 측면에서도 의미가 있다.

이 패턴이 곧 Claude Code 의 sub-agents[^2], Manus 의 multi-agent 구조[^4] 의 추상화다. 이 글에서는 "위임이 가능하다" 까지만 짚는다 — 서브에이전트 정의 디테일은 별도 글에서 다룬다.

서브에이전트의 또 다른 형식 두 가지(`CompiledSubAgent`, `AsyncSubAgent`)도 짧게 짚어 둔다 — 이 글에서는 깊게 풀지 않지만 이름만이라도 `general-purpose` 하나로 끝나지 않는 위임의 스펙트럼이 있음을 알 필요가 있다. `CompiledSubAgent` 는 사용자가 LangGraph 로 직접 짠 그래프(`workflow.compile()` 의 결과)를 서브에이전트로 박는 길이다 — 같은 `task` 도구로 호출되지만 내부 흐름은 사용자가 결정한 그래프다. `AsyncSubAgent` 는 원격/백그라운드 작업이라 `task` 가 아닌 별도 도구(`launch`, `check`, `cancel` 등)로 다뤄진다 — long-running 작업을 메인 흐름과 분리해 돌리는 패턴이다[^5]. 디테일은 별도 글에 미루지만 "위임" 의 모양이 셋이라는 사실을 챙겨 두면 다음 발제들이 빨리 이해된다.

**그림.6**: 서브에이전트의 컨텍스트 격리

![Subagent 컨텍스트 격리](figs/fig06_subagent_isolation.svg)

**그림 6**은 서브에이전트 위임이 메인 컨텍스트와 어떻게 분리되는지를 좌우 두 칸으로 그린다. 좌측 메인 에이전트는 사용자와 대화하며 `task("스펙 분석", ...)` 한 줄로 하위 작업을 위임한다. 그 한 줄 뒤에서 우측 서브에이전트가 자체 컨텍스트(자체 메시지 히스토리·자체 도구 풀·자체 권한)로 검색 30회를 돌리고 한 단락짜리 결과만 메인에 회신한다. 메인 컨텍스트에는 `task` 호출 한 줄과 그 결과 한 단락만 남는다 — 30회 검색의 모든 turn 기록은 보이지 않는다.

이 격리가 두 가지를 동시에 해결한다. **컨텍스트 격리** — 메인 메시지 히스토리에는 `task` 호출과 결과 요약만 남으니 다음 turn 의 시스템 프롬프트가 30회 검색 기록으로 부풀지 않는다. **권한 격리** — `permissions=` 파라미터로 서브에이전트마다 도구 풀을 다르게 줄 수 있다[^5]. 코드 실행 권한은 코딩 서브에이전트에만, 검색은 리서치 서브에이전트에만 — 메인 에이전트가 셸을 못 만지더라도 서브에이전트는 만질 수 있다. 사용자가 별도 서브에이전트를 정의하지 않아도 디폴트 `general-purpose` 서브에이전트가 항상 존재해 메인 카피본의 컨텍스트 격리만으로도 위임이 가능하다[^6].

구체 시나리오 한 컷 — 사용자가 "랭체인 미들웨어 16종을 비교해 줘" 를 묻는다. 메인이 `task('각 미들웨어 검색', ...)` 을 호출, 서브에이전트가 자체 컨텍스트로 검색 16회 + write_file 16개 + 종합을 거쳐 메인에 한 단락 보고서만 회신한다. 다음 turn 의 메인 시스템 프롬프트에는 그 한 단락만 들어간다. 이 패턴이 Claude Code 의 sub-agents[^2] 와 Manus 의 multi-agent 구조[^4] 를 같은 자리에 모은다 — "위임이 가능하다" 라는 한 마디 뒤에 컨텍스트 절약과 권한 분리가 함께 들어 있다는 것이 핵심이다.

#### §2.4. Long-term Memory — LangGraph Store

**한 줄**: 대화/스레드를 넘어 살아남는 기억은 LangGraph Store 가 맡는다 — Filesystem 의 `/memories/` prefix 가 그곳으로 라우팅된다.

LangGraph 에는 두 종류의 영속 계층이 있다 (표.3).

**표.3**: LangGraph 의 영속 계층 두 종류

| 계층 | 수명 | deepagents 매핑 |
|---|---|---|
| Checkpointer | 한 thread (한 대화) | 단기 메모리, `agent.invoke` 의 중간 상태 |
| Store | 모든 thread 가 공유 | **장기 메모리** |

`CompositeBackend(state_backend=..., store_backend=..., prefix="/memories/")` 한 줄로 가상 파일시스템의 `/memories/` 아래 경로는 Store 에, 나머지는 State 에 저장된다[^6]. 결과적으로 모델은 **같은 도구 (`write_file`, `read_file`)** 로 단기·장기 메모리를 다룬다 — 차이는 경로뿐이다. 모델 입장에서 추상이 일관된다는 것이 deepagents 디자인의 우아한 점이다.

장기 메모리가 의미를 갖는 도메인은 사용자 환경설정·도메인 메모·자기 개선 지침의 셋이다. 사용자 환경설정은 매 thread 마다 다시 묻기엔 어색하므로 한 번 저장해 두면 다음 thread 가 그대로 읽는 게 자연스럽다. 도메인 메모는 모델이 한 도메인에 대한 사실(고정된 용어집, API 시그니처, 회사 정책 등)을 점진적으로 누적하는 자리다. 자기 개선 지침은 모델이 자기 행동의 피드백을 받아 다음 thread 의 자기 시스템 프롬프트에 그 교훈을 끼워 넣는 패턴 — 이 셋이 deepagents 가 LangGraph Store 위에 깐 **장기 메모리** 의 주된 용도다.

cross-thread 영속성을 짧은 한 블록으로 시연한다 (공식 가이드 발췌)[^6]:

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    store=InMemoryStore(),
    checkpointer=MemorySaver(),
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)},
    ),
)

# Thread 1 — 영속 메모에 사용자 이름 저장
config_1 = {"configurable": {"thread_id": "thread-1"}}
agent.invoke(
    {"messages": [("user", "Save my name 'Alice' to /memories/user.txt")]},
    config_1,
)

# Thread 2 — 다른 thread 에서 같은 파일 읽기
config_2 = {"configurable": {"thread_id": "thread-2"}}
response = agent.invoke(
    {"messages": [("user", "What is my name?")]},
    config_2,
)
# 에이전트가 /memories/user.txt 를 read_file 로 확인하고 'Alice' 를 회신
```

두 `agent.invoke()` 가 **다른 thread_id** 인데도 두 번째 호출이 첫 번째에서 저장한 파일을 읽는다는 점이 핵심이다. `StateBackend` 만 있으면 두 번째 호출은 빈 파일시스템을 본다 — thread 간 격리가 디폴트이기 때문이다. `CompositeBackend` 가 `/memories/` 만 `StoreBackend` 로 라우팅하기 때문에 그 prefix 의 파일만 thread 를 넘어 살아남는다. 사용자 환경설정·도메인 메모·자기 개선 지침을 thread 간 공유하는 데 이 패턴을 그대로 쓴다 — 다음 주차의 「컨텍스트·메모리·스킬」 발제가 이 패턴의 깊은 변형(skills, AGENTS.md 로딩, 자기 개선 메모리 등)을 다룬다.

이 부분도 깊이는 「컨텍스트·메모리·스킬」 주제의 별도 글에 미룬다.

#### §2.5. 그 외 — `execute` (5번째 빌트인 도구)

**한 줄**: 셸 명령을 실행하는 빌트인 도구. 4대 능력 어디에도 직접 매핑되지 않으며, 적절한 sandbox 백엔드가 있을 때만 동작한다.

빌트인 도구 9종 중 5번째 카테고리에 해당하는 `execute` 는 §2.1\~§2.4 의 4대 능력 어디에도 들어가지 않는다. API 레퍼런스가 명시한다[^5]:

> "`execute` 도구는 백엔드가 `SandboxBackendProtocol` 을 구현했을 때만 셸 명령을 실행한다. 그 외 백엔드에서는 에러 메시지만 반환한다."

즉 기본 `StateBackend` 에서 `execute` 를 호출하면 모델이 받는 건 에러 메시지뿐이다. 셸을 실제로 돌리려면 sandbox 능력을 가진 백엔드(예: 컨테이너 격리)를 끼워야 한다. 이 글에서는 "있다는 사실만" 챙기고, 백엔드·샌드박스의 실제 구성은 별도 글에 미룬다.

`execute` 가 4대 능력 어디에도 들어가지 않는다는 사실은 작은 디자인 단서다 — 4대 능력은 **모델이 자기 컨텍스트를 다스리는 도구** 이고, `execute` 는 **외부 시스템에 영향을 주는 도구** 다. 이 둘이 다른 자리에 분리돼 있는 이유는 책임이 다르기 때문이다. 4대 능력은 sandbox 가 없어도 작동하지만, 셸 명령은 격리 정책이 깔려 있을 때만 안전하게 작동한다 — 그래서 백엔드 프로토콜이 `SandboxBackendProtocol` 을 별도 인터페이스로 분리해 둔 것이다.

---

### §3. 5줄로 시작하기 — Quickstart

**§3 한 줄**: 검색 도구 한 개 + 시스템 프롬프트 한 장 + `create_deep_agent` 한 줄 — Quickstart 의 코어는 정말로 다섯 줄이다.

#### §3.1. 환경 준비

`pip install deepagents tavily-python` 한 줄이 라이브러리 본체와 검색 의존성을 모두 가져온다. 모델 호출용 패키지(`langchain-openai` 또는 `langchain-anthropic` 등)는 사용할 모델에 따라 추가 설치 — 이 발표에서는 OpenAI 호환 API 를 베이스로 하므로 `langchain-openai` 가 필요하다.

발표 환경의 환경변수 설정:

```bash
# 1. 샘플을 .env 로 복사
cp .env_sample .env

# 2. 빈 값 채우기
#    OPENAI_API_KEY    : OpenAI 또는 OpenAI 호환 프록시(clipproxyapi)의 키
#    OPENAI_BASE_URL   : 비우면 OpenAI 직접 / clipproxyapi 시 http://localhost:8317/v1
#    DEEPAGENT_MODEL   : gpt-4o-mini, gpt-4o, gpt-5.5 등
#    TAVILY_API_KEY    : https://tavily.com/ 에서 발급
```

> **Note**: deepagents 는 도구 호출(tool calling)을 지원하는 모델을 요구한다. 도구 호출이 안 되는 모델을 끼우면 미들웨어가 작동하지 않는다.

#### §3.2. 검색 도구 정의

Tavily 클라이언트 한 개를 만들고 함수 하나로 감싼다. 이 함수가 그대로 LangChain 도구로 인식된다 — 시그니처와 docstring 이 자동으로 도구 스키마가 된다.

```python
import os
from typing import Literal

from dotenv import find_dotenv, load_dotenv
from tavily import TavilyClient

load_dotenv(find_dotenv())

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
```

(전체 실행 가능한 형태는 `scripts/01_quickstart_research_agent.py` 와 sync.)

#### §3.3. `create_deep_agent` 호출

모델 객체와 시스템 프롬프트, 도구 한 개를 묶는다.

```python
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

MODEL_NAME = os.environ.get("DEEPAGENT_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")

extra = {"base_url": OPENAI_BASE_URL} if OPENAI_BASE_URL else {}
model = init_chat_model(f"openai:{MODEL_NAME}", **extra)


research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.
You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=research_instructions,
)
```

이 5\~10줄이 제공하는 것:

- `internet_search` 외에 빌트인 도구 9종(`write_todos`, `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `execute`, `task`)이 자동으로 매달림[^5]
- 사용자가 넘긴 `research_instructions` 가 BASE_AGENT_PROMPT 위에 합성됨[^7]
- 반환 객체 `agent` 는 LangGraph `CompiledStateGraph` — `.invoke` / `.stream` / `.ainvoke` 가 그대로 작동[^5]

반환 타입이 새 클래스가 아니라 LangGraph 의 `CompiledStateGraph` 라는 사실은 단순한 구현 디테일이 아니다 — 그것이 deepagents 가 **라이브러리** 라고 불릴 수 있는 결정적 근거다. `agent.invoke()` 가 작동하는 것뿐만 아니라 `.stream()` 으로 매 turn 의 미들웨어 흐름을 받을 수 있고, `.ainvoke()` / `.astream()` 으로 비동기 호출이 가능하며, LangSmith 가 자동으로 트레이스를 잡고, LangGraph Platform 으로 그대로 배포할 수 있다. 즉 `create_deep_agent` 가 만든 객체에 별도 학습이 필요 없고, LangGraph 를 이미 쓰고 있던 도구·관측·배포 인프라가 그대로 작동한다 — §1.3 의 "라이브러리 vs 프레임워크 결정" 의 결과가 여기서 코드로 보인다.

또 한 가지 — `agent` 는 LangGraph 의 표준 `CompiledStateGraph` 이므로 사용자가 직접 짠 다른 LangGraph workflow 의 노드로 그대로 끼워 넣을 수 있다. 예를 들어 분류 → deep agent 호출 → 결과 검증 같은 큰 흐름의 한 노드로 deep agent 를 박는 것이 가능하다. 반대로 `create_deep_agent(subagents=[CompiledSubAgent(name=..., runnable=my_graph)])` 로 사용자가 만든 그래프를 deep agent 의 서브에이전트로 끼울 수도 있다[^5]. LangGraph 의 합성성(composability)이 그대로 살아 있다는 점이 라이브러리 결정의 마지막 이득이다.

#### §3.4. `agent.invoke()` 백그라운드 5단계

호출은 한 줄이다.

```python
result = agent.invoke({
    "messages": [{"role": "user", "content": "What is langgraph?"}]
})
print(result["messages"][-1].content)
```

입력의 `{"messages": [...]}` 형식은 LangGraph 의 `AgentState` 스키마를 따른다 — 핵심 필드는 `messages` (대화 이력 누적) 이고, 같은 자리에 `files=`, `todos=` 도 넣을 수 있다. 응답에서도 같은 키로 받는다.

**4대 능력이 정말 작동했는지 들여다보기** — 위 한 줄로는 최종 메시지만 본다. 같은 `result` 안에 4대 능력의 흔적이 함께 들어 있다.

```python
print("--- 메시지 ---")
print(result["messages"][-1].content)
print("--- 가상 파일시스템 ---")
print(list(result.get("files", {}).keys()))   # write_file 로 만든 파일들
print("--- todo 리스트 ---")
print(result.get("todos", []))                # write_todos 의 흔적
```

작업형 질문에 대한 출력은 보통 다음 모양이다 (실제 캡처 예시):

```text
--- 메시지 ---
LangGraph 와 LangChain 의 차이는 다음 세 축으로 정리됩니다 ...
(1페이지 분량 리포트)

--- 가상 파일시스템 ---
['research/langgraph_overview.md', 'research/langchain_overview.md',
 'research/comparison_axes.md']

--- todo 리스트 ---
[{'content': 'LangGraph 정의·핵심 추상 정리', 'status': 'completed'},
 {'content': 'LangChain 정의·역할 정리', 'status': 'completed'},
 {'content': '두 라이브러리의 차이 세 축 추출', 'status': 'completed'},
 {'content': '리포트 1페이지 작성', 'status': 'completed'}]
```

세 슬롯(`messages`, `files`, `todos`)이 모두 채워져 있는 모습이 4대 능력이 발동된 흔적이다. `files` 키에 검색 결과가 오프로드돼 있고(`FilesystemMiddleware`), `todos` 키에 4개 항목이 모두 `completed` 로 끝나 있고(`TodoListMiddleware`), `messages` 의 마지막에는 1페이지 리포트가 들어 있다.

> 단순한 질문("랭그래프가 뭐야?") 한 번으로는 todo 가 비어 있을 수 있다. "랭그래프와 랭체인의 차이를 1페이지 리포트로 써줘" 처럼 작업형 질문을 주면 4대 능력이 모두 발동되는 모습이 보인다.

이 한 줄 뒤에서 일어나는 일을 원문 02-quickstart 가 다섯 단계로 정리한다.

**그림.7**: `agent.invoke()` 백그라운드 5단계

![invoke 5단계 플로우](figs/fig07_invoke_five_phases.svg)

**그림 7**은 `agent.invoke()` 한 줄이 백그라운드에서 거치는 5단계를 시간 순으로 보여준다. ① 먼저 `write_todos` 로 작업을 4\~7개 항목으로 분해한다. ② 그 항목 하나씩을 `internet_search` 같은 사용자 도구로 처리한다. ③ 검색 결과가 컨텍스트를 잡아먹기 시작하면 `write_file`/`read_file` 로 오프로드한다. ④ 한 항목이 너무 무거우면 `task` 로 서브에이전트에 위임한다. ⑤ todo 의 모든 항목이 `[x]` 가 되면 결과를 종합한다.

다섯 단계는 미들웨어 체인의 7개 미들웨어와 한 줄로 매핑된다 — ① 분해는 `TodoListMiddleware` 가 떠받치고, ② 도구 처리는 모델 + tools 단계(미들웨어 외)에서 일어나고, ③ 오프로드는 `FilesystemMiddleware`, ④ 위임은 `SubAgentMiddleware` (+ `AsyncSubAgentMiddleware`), ⑤ 종합은 모든 미들웨어가 완료된 후의 최종 응답이다[^5][^6]. 다만 다섯 단계가 한 turn 안에 모두 일어나는 게 아니라 **여러 turn 에 걸쳐** 매번 같은 미들웨어 체인을 위→아래로 흘렸다가 도구 실행 후 다시 아래→위로 도는 구조다. 첫 turn 은 ①에서 멈춰 todo 만 적고 끝날 수도 있고, 다음 turn 들이 ②∼④를 반복하다가 마지막에 ⑤로 종합하는 식이다 — 모델은 매 turn 자기 todo 의 어디까지 했는지 다시 확인하고 다음 항목을 골라 도구를 부른다.

체인이 모델에게 보이지 않는다는 점이 결정적이다 — 모델은 `write_todos`, `read_file`, `task` 같은 도구가 거기 있다고만 인식하지 단계 자체를 보지 못한다. 즉 deepagents 는 미들웨어를 **도구로 위장** 시켜 모델이 자기 작업 흐름을 도구 호출로 표현하게 만든다. 이 점이 LangGraph 의 "직접 짠 워크플로(StateGraph + 노드)" 와 결정적으로 다른 지점이다 — 그쪽은 흐름이 사용자에게 보이는 그래프 노드로 정의되지만, deepagents 는 흐름이 모델의 도구 호출 결정으로 자라난다.

한 thread 내의 turn 간 상태가 어떻게 유지되는지도 짚고 가야 한다. `agent.invoke()` 를 같은 `thread_id` 로 두 번 부르면, 두 번째 호출은 첫 번째의 `messages`/`files`/`todos` 를 모두 이어받는다 — `CompiledStateGraph` 가 체크포인터(`checkpointer=` 가 켜져 있으면)에 매 turn 종료 시점의 state 를 자동으로 저장하기 때문이다. 사용자가 `agent.invoke({"messages": [...]}, config={"configurable": {"thread_id": "session-A"}})` 로 같은 thread_id 를 계속 쓰면 5단계 흐름이 이어지고, thread_id 를 바꾸면 깨끗한 새 흐름이 시작된다. 이 차이는 §2.4 의 cross-thread 영속성과 자연스럽게 이어진다 — 한 thread 안의 일관성은 체크포인터가, thread 간의 일관성은 Store 가 책임진다.

매 turn 의 흐름을 직접 보고 싶으면 `.invoke()` 대신 `.stream()` 을 쓰면 된다 — `CompiledStateGraph` 가 LangGraph 의 표준 스트리밍 인터페이스를 그대로 노출하기 때문이다.

```python
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "랭그래프와 랭체인 차이를 1페이지로 정리해줘"}]},
    stream_mode="updates",
):
    # 각 chunk 는 한 미들웨어가 state 를 갱신할 때마다 한 번씩 emit 됨
    # 키 이름이 어느 단계인지 알려준다 — 'agent', 'tools', 'todos', 'files' 등
    print(list(chunk.keys()))
```

이 한 블록으로 5단계가 turn 별로 어떻게 진행되는지 직접 관측할 수 있다 — turn 1 에서 `todos` 가 갱신되고, turn 2\~N 에서 `tools` 호출이 누적되고, turn N+1 에서 `files` 가 갱신되고, 마지막 turn 에서 `messages` 의 마지막 항목이 최종 응답으로 채워지는 모습이 보인다. 미들웨어 체인은 모델에게 안 보이지만 사용자에게는 이 스트림으로 보인다.

다섯 단계가 일어나는 자리는 `create_deep_agent` 가 LangGraph 위에 깐 미들웨어 체인이다[^6]. API 레퍼런스가 명시한 base stack 의 실제 순서는 다음과 같다[^5]:

- TodoListMiddleware (계획 갱신)
- SkillsMiddleware (`skills=` 인자가 있을 때)
- FilesystemMiddleware (오프로드/로드)
- SubAgentMiddleware (선언형 서브에이전트가 있을 때)
- SummarizationMiddleware (필요 시 컨텍스트 압축)
- PatchToolCallsMiddleware
- AsyncSubAgentMiddleware (async 서브에이전트가 있을 때)

체인 안에서 모든 turn 은 위에서 아래로 흐른 뒤 모델 호출로 들어가고, 도구 실행이 끝나면 같은 순서로 다시 위로 돈다. 위 그림.7 의 5단계는 **개념적 흐름** 이며, 실제 미들웨어 chain 순서와 정확히 1:1 대응하는 것은 아니다 — 미들웨어 깊이는 별도 글에서 다룬다.

---

### §4. 청사진 — `create_deep_agent` 의 다이얼

`create_deep_agent` 의 시그니처는 17개 파라미터를 받지만[^5], 그 17개를 한 장의 그림으로 누르면 **두 가지** 만 보인다 — 손이 가장 자주 가는 셋과, 도메인이 까다로워지면 펼치는 그 외. 원문 03-customization 의 첫 다이어그램이 같은 두 묶음으로 나누고 있다는 점이 이 청사진의 검증이다. 이 절은 그 다이어그램을 본 글의 좌표로 옮기고, §4.1 에서 좌측(Core Config) 셋을 풀고, §4.2 에서 우측(Features) 셋을 표 한 장으로 닫는다.

원문 03-customization 의 첫 다이어그램이 청사진을 한 장에 담는다.

**그림.8**: `create_deep_agent` 의 두 분기 — Core Config + Features

![create_deep_agent 청사진](figs/fig08_blueprint_dials.svg)

**그림 8**은 `create_deep_agent` 의 17개 파라미터를 의미상 두 묶음으로 가르는 청사진이다. 좌측의 **Core Config 세 다이얼** (`model`, `system_prompt`, `tools`) 은 거의 모든 도메인에서 첫 손이 가는 자리다 — 어떤 모델로 돌릴지, 어떤 도메인 프롬프트를 한 장 더할지, 어떤 사용자 도구를 도구 풀에 추가할지. 우측의 **Features** (`backend`, `subagents`, `interrupt_on`) 는 켜고 끄는 옵션이다 — 도메인이 영속 메모리를 요구하면 `backend` 를 갈아 끼우고, 위임 패턴이 필요하면 `subagents` 를 정의하고, 사람의 승인이 필요한 도구가 있으면 `interrupt_on` 으로 HITL 을 건다.

그림이 좌·우 셋씩만 보이지만, API 시그니처는 17개 파라미터를 받는다[^5] — 그 외 11개(`middleware`, `skills`, `memory`, `permissions`, `response_format`, `context_schema`, `checkpointer`, `store`, `debug`, `name`, `cache`)는 한 단계 더 안쪽 다이얼들이다. 라이브러리 저자가 의도적으로 표면을 좁게 잡았다 — 첫 90% 사용자가 좌측 셋만 만져도 작동하도록, 나머지 11개는 LangGraph 직속 인프라(`store`, `checkpointer`)거나 고급 패턴(`permissions`, `response_format`)이라 도메인이 까다로워질 때만 펼친다. 이 좁히기는 우연이 아니라 `03-customization` 공식 가이드의 첫 다이어그램[^5]이 같은 셋만 보여주는 이유이기도 하다.

이 글의 범위가 그림과 일치한다 — §4.1 이 좌측 셋을 다루고, §4.2 가 우측 셋을 표 한 장으로 좁히고, §6 이 그 외 11개 다이얼의 영역(컨텍스트·메모리·스킬, 백엔드·샌드박스·권한)을 다음 발제에 미룬다. 그림 8 이 §4 의 좌표면 §4 가 본 글 후반의 좌표다 — 깊이는 별도 글에 미룬다.

#### §4.1. Core Config — Model · System Prompt · Tools

**한 줄**: 17개 파라미터 중 처음 손 대는 셋이 Model · System Prompt · Tools.

`create_deep_agent` 의 시그니처는 17개 파라미터를 받는다[^5]: `model`, `tools`, `system_prompt`, `middleware`, `subagents`, `skills`, `memory`, `permissions`, `backend`, `interrupt_on`, `response_format`, `context_schema`, `checkpointer`, `store`, `debug`, `name`, `cache`. 첫 90% 사용자는 앞 셋만 만지면 된다.

17개 전체를 의미상 세 묶음으로 묶으면 그림 8 의 좌·우 분할이 더 선명해진다.

**표.3.5**: 17개 파라미터의 세 묶음

| 묶음 | 파라미터 (개수) | 언제 만지나 |
|---|---|---|
| **Core Config** | `model`, `system_prompt`, `tools` (3) | 첫 90% 사용자 — 모델·프롬프트·사용자 도구 한 장 |
| **Features** | `backend`, `subagents`, `interrupt_on`, `permissions`, `memory` (5) | 메모리 영속·위임·HITL·권한 격리·외부 AGENTS.md 로딩이 필요할 때 |
| **Advanced** | `middleware`, `skills`, `response_format`, `context_schema`, `checkpointer`, `store`, `debug`, `name`, `cache` (9) | 미들웨어 직접 조립·구조화 출력·체크포인터/캐시 정밀 제어 등 |

상단 묶음에서 아래로 내려갈수록 만지는 빈도가 줄고 도메인 의존성이 커진다. 본 글은 Core Config 셋과 Features 일부(§4.2)만 풀고, Advanced 9개는 §6 의 다음 발제 영역에 미룬다.

**표.4**: Core Config — 세 다이얼

| 파라미터 | 기본값 | 무엇이 들어가나 |
|---|---|---|
| `model` | `claude-sonnet-4-6`[^5] | LangChain ChatModel 객체 또는 `"provider:model"` 문자열 |
| `system_prompt` | BASE_AGENT_PROMPT (Claude Code 영감)[^7] | 위에 합성될 도메인 한 장 |
| `tools` | `[]` | 빌트인 9종에 추가될 사용자 도구 리스트 |


기본값 `claude-sonnet-4-6` 은 의미가 있다 — 4대 능력의 도구를 잘 호출하는 (특히 `task` 위임 결정을 잘 내리는) 모델로 검증된 선택이다. 하지만 OpenAI 호환 API · 사내 프록시 · 로컬 Ollama 등으로 갈아 끼우는 게 일상적인 시나리오 (§4.3).

`tools=` 의 빌트인 9종은 디폴트로 자동 추가되며, 사용자가 넘긴 도구는 그 위에 더해진다. 즉 사용자는 자기 도메인 도구만 신경 쓰면 되고, 4대 능력 도구는 라이브러리가 알아서 깔아 준다. 사용자 도구는 LangChain `BaseTool` 을 상속한 객체, `@tool` 데코레이터를 붙인 함수, 또는 단순 callable 모두 가능하다 — `internet_search` 처럼 docstring + 시그니처가 있는 함수면 LangChain 이 자동으로 도구 스키마를 만든다. `tools=` 만 잘 채워도 deepagents 의 사용자 영역 90% 가 끝난다.

> **버전 주의**: 공식 한국어 번역본 `03-customization_ko.md` 는 한 단계 이전 식별자 `claude-sonnet-4-5-20250929` 를 적고 있다. 라이브러리 현재 디폴트는 API 레퍼런스 기준 `claude-sonnet-4-6` 이다[^5] — 두 문서를 같이 펼치면 헷갈릴 수 있어 짚어둔다.

#### §4.2. Features — Backend · Subagents · Interrupts (개요만)

**한 줄**: 켜고 끌 수 있는 기능 셋 — 1주차에서는 이름만 안다.

**표.5**: Features 3종 — 1주차에서 다루는 깊이

| Feature | 핵심 인자 | 1주차에서 다루는 깊이 |
|---|---|---|
| Backend | `backend=`, `memory=`, `store=` | "Filesystem 의 라우팅 경로를 결정한다" 까지만 (§2.2) |
| Subagents | `subagents=`, `permissions=` | "위임이 가능하다" 까지만 (§2.3) |
| Interrupts | `interrupt_on=` | 이름만 — HITL 패턴은 이 글의 범위 밖 |

세 인자가 어떻게 켜지는지 한 줄씩 본다. **Backend** 는 §2.2 에서 본 `CompositeBackend` 한 줄로 켠다 — `backend=lambda rt: CompositeBackend(default=StateBackend(rt), routes={"/memories/": StoreBackend(rt)})` 로 영속 메모리가 `/memories/` prefix 에서 작동한다[^6]. 디폴트 `StateBackend` 는 한 thread 안에서만 살아남고, `FilesystemBackend(root_dir=...)` 로 로컬 디스크에 직접 쓸 수도 있다. backend 를 갈아 끼우면 같은 `write_file` 호출이 다른 저장소로 라우팅된다는 점이 이 인자의 본질이다.

**Subagents** 는 §2.3 에서 본 SubAgent 딕셔너리(필수: name·description·system_prompt·tools)의 리스트로 켠다 — `subagents=[{"name": "research-agent", "description": "...", "system_prompt": "...", "tools": [...]}]`[^6]. 정의된 서브에이전트는 메인 에이전트의 `task` 도구를 통해 호출 가능하다. `permissions=` 는 메인과 서브에이전트의 도구 풀을 다르게 잘라 주는 역할 — 코드 실행은 코딩 서브에이전트만, 검색은 리서치 서브에이전트만 같은 격리를 만든다[^5].

**Interrupts** 는 가장 단순한 켜짐이다 — `interrupt_on={"write_file": True}` 한 줄이 모든 `write_file` 호출 직전에 실행을 멈추고 사람의 승인을 기다리게 만든다[^5]. `True` 대신 `InterruptOnConfig` 객체로 더 정교한 정책(특정 인자값에서만 멈춤 등)도 가능하다. 체크포인터가 필요한 패턴이라 `checkpointer=MemorySaver()` 를 함께 켜야 동작한다 — HITL 의 깊이(메시지 편집·도구 인자 수정·resume 패턴)는 별도 글의 영역.

세 인자 모두 "켜는 한 줄" 은 위처럼 짧지만, 디자인의 의미는 깊다. 이 셋이 §6 의 다음 발제들이 풀어 갈 영역의 시작점이다 — 이 글에서는 표와 한두 줄 코드까지만 보고 닫는다.

세 Feature 가 한 호출에 모두 켜진 모습은 다음과 같다 (개념 시연용, 상세 디테일은 §6 의 다음 발제 영역):

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    model="claude-sonnet-4-6",
    tools=[internet_search],
    system_prompt=research_instructions,
    backend=lambda rt: CompositeBackend(           # Backend
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)},
    ),
    subagents=[research_subagent],                 # Subagents
    interrupt_on={"write_file": True},             # Interrupts
    store=InMemoryStore(),
    checkpointer=MemorySaver(),
)
```

좌측 Core Config 셋(`model`, `tools`, `system_prompt`)과 우측 Features 셋(`backend`, `subagents`, `interrupt_on`)이 한 호출에 같이 들어간다 — 그 외 11개는 디폴트로 충분하다. 도메인이 까다로워질 때만 11개 다이얼을 한두 개씩 펼치면 된다.

#### §4.3. Model 바꾸기 — 문자열 vs LangChain 객체

**한 줄**: 두 가지 길이 있다 — 한 줄 문자열로 빠르게, 또는 객체로 정밀하게.

##### 길 1 — `provider:model` 문자열

`init_chat_model` 의 한 줄로 끝난다.

```python
import os

from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import init_chat_model

from deepagents import create_deep_agent

load_dotenv(find_dotenv())

MODEL_NAME = os.environ.get("DEEPAGENT_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")

extra = {"base_url": OPENAI_BASE_URL} if OPENAI_BASE_URL else {}
model = init_chat_model(f"openai:{MODEL_NAME}", **extra)

agent = create_deep_agent(model=model)
```

(전체 실행 형태는 `scripts/02_model_string_swap.py` 와 sync.)

`OPENAI_BASE_URL` 을 환경변수로 두면 OpenAI 호환 프록시(이 발표 환경의 clipproxyapi 같은) 로 그대로 라우팅된다. 코드 손댈 일 없이 `.env` 만 갈아 끼우면 된다.

이 패턴이 사내 환경에서 특히 유용하다. 외부 API 키를 직접 노출하지 않고 사내 프록시(예: clipproxyapi, vLLM 호환 프론트엔드)를 통해 라우팅하면, 키 관리는 프록시가 맡고 클라이언트 코드는 `OPENAI_BASE_URL` 한 줄만 가리키면 된다. 같은 코드가 OpenAI 직접 호출, 사내 프록시, Bedrock 호환 게이트웨이, 로컬 vLLM 까지 모두에서 동작한다 — deepagents 는 이 모든 백엔드 차이에 무관하게 작동한다.

##### 길 2 — LangChain 모델 객체

`temperature`, `num_ctx`, `top_p` 같은 세부 다이얼을 잡고 싶거나 OpenAI 호환이 아닌 백엔드 (Ollama, Bedrock, Vertex 등) 로 갈 때 이 길로 간다.

```python
import os

from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import init_chat_model

from deepagents import create_deep_agent

load_dotenv(find_dotenv())

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

model = init_chat_model(
    model=OLLAMA_MODEL,
    model_provider="ollama",
    temperature=0,
)

agent = create_deep_agent(model=model)
```

(전체 실행 형태는 `scripts/03_model_object_ollama.py` 와 sync.)

> **Tip** (원문 03-customization): "`provider:model` 형식을 사용하여 모델 간에 빠르게 전환하세요." — 즉 길 1 이 디폴트, 길 2 는 디테일이 필요할 때.

두 길이 같은 일을 한다는 점도 중요하다. `init_chat_model("openai:gpt-5")` 도 결국은 LangChain `BaseChatModel` 인스턴스를 만드는 한 줄이고, `init_chat_model(model="llama3.1", model_provider="ollama", temperature=0)` 도 같은 인터페이스의 인스턴스를 만든다. 두 길의 차이는 **인자를 어디서 채우느냐** 뿐이다 — 길 1 은 환경 변수 + 디폴트로 채우고, 길 2 는 코드에서 직접 채운다. 이런 단순함 덕에 사용자는 모델을 바꾸기 위해 deepagents 의 추상을 건드릴 필요가 없다.

다만 모델을 바꿀 때 챙겨야 할 한 가지 — **도구 호출 (tool calling) 지원** 여부다. deepagents 의 4대 능력은 모두 모델이 도구를 호출할 수 있다는 가정에 서 있다. 도구 호출이 안 되는 모델(예: 일부 오픈소스 베이스 모델)을 끼우면 `write_todos`/`task` 미들웨어가 발동되지 않고 모델이 그냥 텍스트만 회신한다 — 미들웨어는 살아 있지만 모델이 그것을 부르지 않으니 효과가 없다. `init_chat_model` 이 만든 객체가 `bind_tools()` 를 지원하는지(LangChain ChatModel 추상의 한 메서드) 확인하는 것이 안전 검증의 한 줄이다. 또 OpenAI Responses API 를 쓸 때는 `init_chat_model("openai:gpt-5", use_responses_api=False)` 처럼 명시 옵션이 필요할 수 있다는 점도 API 레퍼런스에 짚혀 있다[^5].

#### §4.4. System Prompt 패턴

**한 줄**: 기본 BASE_AGENT_PROMPT 위에 도메인 한 장을 얹는다 — 사용자가 통째로 덮어쓰지 않는다.

deepagents 의 시스템 프롬프트는 3단 합성 구조다[^7].

**그림.9**: 시스템 프롬프트의 3단 합성 — `USER → (BASE 또는 CUSTOM) → SUFFIX`

![시스템 프롬프트 3단 합성](figs/fig09_system_prompt_layers.svg)

**그림 9**는 매 turn 마다 모델에게 전달되는 최종 시스템 프롬프트가 세 segment 의 합성임을 보여준다 — `USER → (BASE 또는 CUSTOM) → SUFFIX`, 사이는 빈 줄(`\n\n`)로 결합된다.

세 segment 가 따로 있는 이유는 각자 책임이 다르기 때문이다[^7]. **USER** 만 있으면 모델이 4대 능력 도구(`write_todos`, `task`, `write_file` 등)를 언제 어떻게 써야 할지 모른다 — 그 책임은 BASE 의 자리. **BASE** 만 있으면 도메인 일관성이 없다 — 사용자의 도메인 톤(연구원·코더·서포트 등)을 고정하는 책임은 USER 의 자리. **BASE+USER** 만 있으면 모델별 best practice 가 누락된다 — Sonnet 4.6 의 `<use_parallel_tool_calls>` / `<investigate_before_answering>` / `<tool_result_reflection>` XML 태그 같은 미세 튜닝[^7]을 끝에 붙이는 책임은 SUFFIX 의 자리. 셋이 모두 있어야 deepagents 의 시스템 프롬프트가 완성된다.

- **USER** — 사용자가 `system_prompt=` 인자로 넘긴 도메인 한 장. 없으면 이 segment 는 비워진다.
- **BASE** — 라이브러리의 `BASE_AGENT_PROMPT` (graph.py 56\~97행). 매칭되는 `HarnessProfile` 이 등록돼 있고 그 프로필이 자체 `base_system_prompt` 를 갖고 있으면, BASE 자리가 **CUSTOM** 으로 통째 교체된다.
- **SUFFIX** — `HarnessProfile.system_prompt_suffix`. 매칭되는 모델(예: Sonnet 4.6)이면 끝에 자동 부착되는 XML 태그 묶음(`<use_parallel_tool_calls>` 등).

핵심: `system_prompt=` 인자는 BASE 를 **교체하는 게 아니라 그 앞(USER 자리)에 prepend** 된다. 사용자가 도메인 프롬프트를 넘겨도 라이브러리의 BASE 와 모델별 SUFFIX 는 그대로 살아남는다 — Understand → Act → Verify 워크플로와 도구 호출 정책이 사용자 커스텀 한 장에 의해 지워지지 않는 이유다. BASE 자체를 갈아 끼우려면 `HarnessProfile` 까지 손대야 한다.

`BASE_AGENT_PROMPT` 자체는 `langchain-ai/deepagents` 리포의 `libs/deepagents/deepagents/graph.py` 56\~97행에 있다 — 약 42줄·2,100자[^7]. 핵심 지침 세 줄:

- *"NEVER add unnecessary preamble"* (불필요한 서두는 절대 붙이지 말 것)
- **Understand → Act → Verify** 3단 워크플로를 강하게 박는다
- 빌트인 도구(`write_todos`, `read_file`, `task` 등) 사용 시점을 구체적으로 안내

본문에서 그 3단 워크플로 부분을 그대로 인용하면 다음 다섯 줄이다[^7]:

> **1. Understand first** — read relevant files, check existing patterns. Quick but thorough — gather enough evidence to start, then iterate.
> **2. Act** — implement the solution. Work quickly but accurately.
> **3. Verify** — check your work against what was asked, not against your own output. Your first attempt is rarely correct — iterate.
>
> *"Keep working until the task is fully complete. Don't stop partway and explain what you would do — just do it. Only yield back to the user when the task is done or you're genuinely blocked."*

이 다섯 줄이 4대 능력의 "왜 그것을 모델이 쓰는가" 의 근거다. Understand 가 `read_file`/`grep` 의 자리, Act 가 사용자 도구 + `write_file` 의 자리, Verify 가 `task` 위임 후 결과 점검의 자리. BASE 가 도구 카탈로그를 그저 나열하는 게 아니라 **언제 어떤 단계에서 부르는가** 를 박아 두기 때문에 4대 능력 도구가 매 turn 자리를 잡는다.

Sonnet 4.6 의 SUFFIX 가 끝에 붙이는 세 XML 태그도 비슷한 결의 메타지침이다 — `<use_parallel_tool_calls>` 는 독립 도구 호출은 동시에 부르라는 지시, `<investigate_before_answering>` 은 코드를 보지 않고 추측하지 말라는 지시, `<tool_result_reflection>` 은 도구 결과를 받은 뒤 다음 행동을 정하기 전에 한 번 더 생각하라는 지시[^7]. 셋 다 모델이 도구 호출을 더 잘하도록 만드는 미세 튜닝이며, Anthropic 공식 prompting guide 의 패턴 그대로다. 모델군이 바뀌면 이 SUFFIX 도 다른 패턴으로 갈리는데(다른 `HarnessProfile` 이 매칭되면), 사용자는 그 변경을 신경 쓸 필요가 없다 — 라이브러리가 매칭되는 모델별 SUFFIX 를 자동으로 부착한다.

`system_prompt=` 인자가 BASE 를 정말로 덮어쓰지 않는지 검증하는 가장 간단한 방법은 모델 호출 직전의 최종 시스템 프롬프트를 한 번 캡처하는 것이다. LangSmith 트레이스를 켜고 `agent.invoke()` 를 한 번 돌리면 트레이스 첫 줄에 합성된 시스템 프롬프트(USER + BASE + SUFFIX)가 그대로 찍힌다 — 사용자가 짧은 한 줄(`research_instructions`)을 넘겼는데도 그 아래에 BASE 의 42줄이 그대로 따라오고, Sonnet 4.6 으로 돌렸으면 끝에 SUFFIX 의 XML 태그 셋이 붙어 있는 모습이 보인다. 이 캡처가 "USER 가 BASE 를 prepend 한다" 라는 사실의 직접 증거다.

README 의 Acknowledgements 가 명시한다 — *"이 프로젝트는 주로 Claude Code 에서 영감을 받았다"* (This project was primarily inspired by Claude Code)[^7]. BASE 의 톤·구조가 Claude Code 의 시스템 프롬프트와 닮은 이유다.

가장 작은 커스텀 프롬프트 적용은 다음 한 장이다:

```python
from deepagents import create_deep_agent

research_instructions = """\
You are an expert researcher. Your job is to conduct \
thorough research, and then write a polished report. \
"""

agent = create_deep_agent(
    model=model,
    system_prompt=research_instructions,
)
```

(전체 실행 형태는 `scripts/04_custom_system_prompt.py` 와 sync.)

여기서 `research_instructions` 는 **BASE 를 교체** 하는 게 아니라 그래프의 시스템 프롬프트 슬롯에 박힌다 — Quickstart 의 길고 친절한 프롬프트가 도메인을 좁히는 짧은 한 장으로 줄어든 형태일 뿐이다.

---

### §5. 언제 쓰나

#### §5.1. `create_agent` vs LangGraph workflow vs `create_deep_agent`

**한 줄**: 단계 수·컨텍스트 양·위임/메모리 필요성 — 세 축으로 결정한다.

원문 01-overview 가 deepagents 사용 시점을 네 줄로 정리한다.

> 다음과 같은 기능이 필요한 에이전트가 필요할 때 deep agents 를 사용하세요:
>
> - **복잡한 다단계 작업** 처리 (계획 수립과 분해)
> - **대량의 컨텍스트 관리** (파일시스템 도구)
> - **작업 위임** (전문화된 서브에이전트)
> - 대화/스레드 간 **메모리 유지**

뒤집으면, 위 네 가지 중 어느 것도 필요 없으면 `create_agent` 가 더 적합하다 — 미들웨어 체인의 오버헤드 없이 더 빠르게 응답한다.

세 도구가 놓이는 자리는 사실 그림 3 의 스택 위에서 보인다. `create_agent` 는 LangChain 한 켜만 쓰고 미들웨어를 사용자가 직접 조립하는 길, **직접 짠 LangGraph 워크플로** 는 LangGraph `StateGraph` 를 사용자가 노드·엣지로 직접 만드는 길, `create_deep_agent` 는 그 위에 deepagents 가 미들웨어 한 켜를 미리 깔아 둔 길이다. 셋 다 같은 LangGraph 위에 서 있으므로 같은 관측·배포 인프라를 공유하지만, 사용자가 어떤 책임을 지고 어떤 책임을 라이브러리에 맡기는지가 다르다 — `create_agent` 는 "도구·프롬프트만 주고 흐름은 모델에게 맡긴다", LangGraph workflow 는 "흐름을 내가 정한다", `create_deep_agent` 는 "흐름은 모델이 도구 호출로 표현하되 4대 능력의 자리는 라이브러리가 깔아 둔다".

`create_agent` 와 `create_deep_agent` 의 결정은 따로 보고, **직접 짠 LangGraph 워크플로** 는 또 다른 위치에 있다 — 흐름이 정해져 있고 노드 단위로 통제하고 싶을 때 (예: RAG 파이프라인, 평가 체인). 결정 표 한 장으로 정리한다.

세 도구를 도메인별로 매핑하면 자기 작업이 어디에 속하는지 빠르게 보인다. 짧은 챗봇·FAQ 응답·단일 도구 호출(현재 날씨 조회 등)은 `create_agent`. 결정적 RAG 파이프라인(문서 검색 → 재순위 → 답변)·정형 평가 체인·다단계 데이터 변환은 직접 짠 LangGraph workflow. 자율 리서치(질문 → 분해 → 다중 검색 → 종합)·코드베이스 분석·복합 보고서 작성·자율 에이전트 작업은 `create_deep_agent`. 도메인이 셋 사이의 경계에 있으면 — 예를 들어 검색 후 결정적으로 답변하지만 검색이 가끔 다단계가 되는 경우 — `create_agent` 에 미들웨어를 직접 끼우는 길이 가장 가벼운 답이 될 수 있다.

#### §5.2. 의사결정 표

**표.6**: `create_agent` / 직접 LangGraph / `create_deep_agent` 의사결정

| 상황 | 추천 | 이유 |
|---|---|---|
| 짧은 Q&A, 단일 도구 호출 | `create_agent` | 미들웨어 오버헤드 없이 가볍게 동작 |
| 복잡한 다단계 + 큰 컨텍스트 + 위임/메모리 | `create_deep_agent` | 4대 능력이 즉시 켜짐, BASE 프롬프트로 워크플로 검증됨 |
| 흐름이 결정적이고 노드 통제 필요 | 직접 짠 LangGraph workflow | StateGraph 로 명시 모델링, 분기·병렬·HITL 자유 |
| 짧은 작업이지만 도구 호출 정책이 까다롭다 | `create_agent` + 미들웨어 직접 조립 | 필요한 미들웨어만 골라 끼움 — `create_deep_agent` 의 부분집합으로 만들 수 있음[^6] |

> 결정의 한 줄 룰: **"단계가 5개 이상이고, 컨텍스트가 모델 윈도우의 절반을 넘으며, 부분 작업을 위임할 만하다"** — 이 셋이 동시에 참이면 `create_deep_agent`. 하나만 참이면 다른 길을 검토.

표를 거꾸로 읽으면 안티패턴이 보인다. 짧은 Q&A 에 `create_deep_agent` 를 쓰면 매 turn 미들웨어 체인 7개가 도는 오버헤드를 짧은 응답에 그대로 떠안는다 — 응답 지연이 늘고 토큰 소비가 불필요하게 커진다. 흐름이 결정적인 RAG 파이프라인에 `create_deep_agent` 를 끼우면 모델이 자기 도구 호출 결정으로 흐름을 만들기 때문에 같은 입력에서 매번 다른 노드 순서가 나올 수 있어 평가·관측이 어려워진다 — 이 자리에는 직접 짠 LangGraph workflow 의 결정성이 더 맞다. 반대로 다단계 + 큰 컨텍스트 + 위임이 모두 필요한 작업에 `create_agent` 를 고집하면 §1.1 의 세 지점(컨텍스트 오버플로·계획 부재·위임 불가)을 그대로 만난다 — 미들웨어를 직접 조립하는 길이 있지만 결국 deepagents 가 먼저 만든 조합이라 처음부터 그쪽으로 가는 편이 빠르다.

결정의 또 다른 단서는 **재현성 요구 수준** 이다. 평가·디버그·정확성 보장이 결정적인 도메인(금융 자동화, 의료 결정 보조 등)에서는 같은 입력이 같은 출력을 내야 한다는 요구가 강하다. 이런 자리에는 직접 짠 LangGraph workflow 가 더 맞고, deepagents 의 자율성은 오히려 단점이 된다. 반대로 탐색·창작·리서치 같은 도메인은 모델의 자율적 결정이 답의 풍부함을 만든다 — 여기서는 `create_deep_agent` 가 자연스럽다. 같은 시스템 안에 두 도메인이 섞여 있으면 결정적 부분은 LangGraph workflow 로 짜고 그 한 노드에 deep agent 를 박는 합성 패턴도 가능하다 — §3.3 에서 짚었듯 `CompiledStateGraph` 가 그대로 노드로 쓰일 수 있기 때문이다.

---

### §6. 이 글에서 다루지 않은 것

**§6 한 줄**: 이 글은 지도. 깊이는 별도 글에 미룬다.

#### §6.1. 컨텍스트·메모리·스킬

§2.2 Filesystem 의 Backend 추상과 §2.4 Long-term Memory 가 만나는 지점. `CompositeBackend` 의 prefix 라우팅[^6], LangGraph Store 의 영속화 모델, 그리고 deepagents 가 추후 추가한 `skills` 파라미터 — 이 셋을 한 줄로 묶는 디자인은 별도 글의 재료다.

#### §6.2. 백엔드·샌드박스·권한

§2.3 Subagents 의 권한 격리, 그리고 본 글에서 언급만 한 Shell tool / Context editing[^6] 은 백엔드·샌드박스 주제의 재료다. `permissions` 파라미터[^5]가 모델·도구·서브에이전트 레벨에서 어떻게 분리되는지, sandbox 가 코드 실행을 어떻게 격리하는지는 별도 글에서 다뤄진다.

---

### 부록 A. 용어집

**표.7**: 본 교안의 핵심 용어

| 용어 | 정의 |
|---|---|
| **Deep Agent** / **Deep Agents** | LangGraph 위에 4대 능력을 미들웨어로 내장한 에이전트 (개념) / 라이브러리 |
| `deepagents` | PyPI 패키지명 (소문자 그대로) |
| `create_deep_agent()` | 라이브러리의 메인 팩토리 함수 — `CompiledStateGraph` 반환[^5] |
| BASE_AGENT_PROMPT | 기본 시스템 프롬프트 (Claude Code 영감, ~42줄)[^7] |
| 미들웨어 (middleware) | LangChain core 가 제공하는 prebuilt 16종 + Deep Agents 전용 (Filesystem, Subagent)[^6] |
| Backend | Filesystem 미들웨어의 저장 추상 — `StateBackend` / `StoreBackend` / `CompositeBackend`[^6] |
| Store | LangGraph 의 thread 횡단 영속 계층 — 장기 메모리의 기반 |
| Subagent | 격리된 컨텍스트·권한으로 일하는 하위 에이전트 — `task` 도구로 호출 |
| `general-purpose` subagent | 디폴트로 항상 존재하는 범용 서브에이전트 — 메인과 동일한 도구 풀을 가지며 컨텍스트 격리만 제공[^6] |
| HarnessProfile | 모델별 프롬프트·미들웨어 튜닝 묶음 — 매칭되는 모델일 때 `BASE_AGENT_PROMPT` 자리에 자체 `base_system_prompt` 를 넣고 `system_prompt_suffix` 를 끝에 부착[^7] |
| Tool calling | 모델이 도구 함수를 자율적으로 호출하는 능력 — deepagents 의 모든 동작이 이 위에 서 있다 (지원 안 하는 모델로는 구동 불가)[^5] |
| `CompiledStateGraph` | LangGraph 의 컴파일된 상태 그래프 — `create_deep_agent()` 의 반환 타입. `.invoke / .stream / .ainvoke` 가 모두 작동[^5] |
| Checkpointer | LangGraph 의 한 thread 내 영속 계층 — `agent.invoke` 의 중간 상태를 저장해 다음 호출에서 이어가게 한다 |
| CodeAct | 도구 호출 대신 Python 스크립트를 생성·실행하는 패러다임 (Manus)[^4] |

### 부록 B. 실행 스크립트 안내

**표.8**: `scripts/` 4종 — 교안 매핑

| 파일 | 보이는 패턴 | 교안 매핑 |
|---|---|---|
| `scripts/01_quickstart_research_agent.py` | Tavily + create_deep_agent 풀 예제 | §3.2\~§3.4 |
| `scripts/02_model_string_swap.py` | `init_chat_model("openai:<model>")` 한 줄 | §4.3 길 1 |
| `scripts/03_model_object_ollama.py` | LangChain 모델 객체 (ChatOllama) 패턴 | §4.3 길 2 |
| `scripts/04_custom_system_prompt.py` | 커스텀 system_prompt 한 장 합성 | §4.4 |

셋업·실행은 `scripts/README.md` 참조. 환경변수 컨벤션:

- `OPENAI_API_KEY` / `OPENAI_BASE_URL` (선택) / `DEEPAGENT_MODEL` — 01·02·04 공통
- `TAVILY_API_KEY` — 01 전용
- `OLLAMA_MODEL` — 03 전용

> 발표 환경(태영 노트북)에서는 clipproxyapi 를 OpenAI 호환 프록시로 사용 — `OPENAI_BASE_URL=http://localhost:8317/v1`. 키만 갈아 끼우면 동일 코드가 OpenAI 직접/사내 프록시/Bedrock 호환 프록시 모두에서 작동한다.

