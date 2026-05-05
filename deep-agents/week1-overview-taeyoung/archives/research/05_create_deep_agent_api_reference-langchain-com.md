---
title: create_deep_agent — API Reference (deepagents)
url: https://reference.langchain.com/python/deepagents/graph/create_deep_agent
fetched: 2026-05-04
note: 1주차 발표 §3.3, §4.1 "create_deep_agent 호출 / Core Config 다이얼" 보강용. 함수 시그니처와 파라미터 1차 자료.
---

# create_deep_agent

> **Function** in `deepagents`

Create a deep agent.

!!! warning "Deep agents require a LLM that supports tool calling!"

By default, this agent has access to the following tools:

- `write_todos`: manage a todo list
- `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`: file operations
- `execute`: run shell commands
- `task`: call subagents

The `execute` tool allows running shell commands if the backend implements `SandboxBackendProtocol`.
For non-sandbox backends, the `execute` tool will return an error message.

## Signature

```python
create_deep_agent(
    model: str | BaseChatModel | None = None,
    tools: Sequence[BaseTool | Callable | dict[str, Any]] | None = None,
    *,
    system_prompt: str | SystemMessage | None = None,
    middleware: Sequence[AgentMiddleware] = (),
    subagents: Sequence[SubAgent | CompiledSubAgent | AsyncSubAgent] | None = None,
    skills: list[str] | None = None,
    memory: list[str] | None = None,
    permissions: list[FilesystemPermission] | None = None,
    backend: BackendProtocol | BackendFactory | None = None,
    interrupt_on: dict[str, bool | InterruptOnConfig] | None = None,
    response_format: ResponseFormat[ResponseT] | type[ResponseT] | dict[str, Any] | None = None,
    context_schema: type[ContextT] | None = None,
    checkpointer: Checkpointer | None = None,
    store: BaseStore | None = None,
    debug: bool = False,
    name: str | None = None,
    cache: BaseCache | None = None,
) -> CompiledStateGraph[AgentState[ResponseT], ContextT, _InputAgentState, _OutputAgentState[ResponseT]]
```

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `model` | `str \| BaseChatModel \| None` | No | The model to use. Defaults to `claude-sonnet-4-6`. Accepts a `provider:model` string (e.g., `openai:gpt-5`); see `init_chat_model` for supported values. You can also pass a pre-initialized `BaseChatModel` instance directly. !!! note "OpenAI Models and Data Retention" If an `openai:` model is used, the agent will use the OpenAI Responses API by default. To use OpenAI chat completions instead, initialize the model with `init_chat_model("openai:...", use_responses_api=False)` and pass the initialized model instance here. To disable data retention with the Responses API, use `init_chat_model("openai:...", use_responses_api=True, store=False, include=["reasoning.encrypted_content"])` and pass the initialized model instance here. (default: `None`) |
| `tools` | `Sequence[BaseTool \| Callable \| dict[str, Any]] \| None` | No | Additional tools the agent should have access to. These are merged with the built-in tool suite listed above (`write_todos`, filesystem tools, `execute`, and `task`). (default: `None`) |
| `system_prompt` | `str \| SystemMessage \| None` | No | Custom system instructions placed at the front of the system prompt sent to the model. Whatever you pass here always sits before the SDK's default deep-agent prompt and any model-tuning suffix from a registered `HarnessProfile`. With `system_prompt=None`, the SDK default is used on its own (plus the profile suffix when one applies). Sections are joined by a blank line. Passing a `SystemMessage` instead of a string preserves any `cache_control` markers on the message's content blocks — useful for placing explicit Anthropic prompt-cache breakpoints. The same ordering applies (caller's blocks first, SDK content appended as an additional text block). See [Prompt assembly](https://docs.langchain.com/oss/deepagents/customization#prompt-assembly) for the full case-by-case breakdown. (default: `None`) |
| `middleware` | `Sequence[AgentMiddleware]` | No | Additional middleware to apply after the base stack but before the tail middleware. The full ordering is: Base stack: `TodoListMiddleware`, `SkillsMiddleware` (if `skills` is provided), `FilesystemMiddleware`, `SubAgentMiddleware` (if any inline subagents — declarative `SubAgent` or `CompiledSubAgent` — are available), `SummarizationMiddleware`, `PatchToolCallsMiddleware`, `AsyncSubAgentMiddleware` (if async `subagents` are provided). *User middleware is inserted here.* Tail stack: Harness profile `extra_middleware` (if any), `_ToolExclusionMiddleware` (if profile has `excluded_tools`), `AnthropicPromptCachingMiddleware` (unconditional; no-ops for non-Anthropic models), `MemoryMiddleware` (if `memory` is provided), `HumanInTheLoopMiddleware` (if `interrupt_on` is provided). After assembly, any entries in the profile's `excluded_middleware` are filtered from the final stack. Class entries match exact type; string entries match `AgentMiddleware.name` exactly (e.g. `"SummarizationMiddleware"` drops the summarization middleware via its public alias). Entries that match nothing in the assembled stack raise `ValueError`, as does excluding scaffolding classes (`FilesystemMiddleware`, `SubAgentMiddleware`). To run without the `task` tool, set `general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False)` on the active harness profile and pass no synchronous subagents via `subagents=`. Async subagents are unaffected. (default: `()`) |
| `subagents` | `Sequence[SubAgent \| CompiledSubAgent \| AsyncSubAgent] \| None` | No | Subagent specs available to the main agent. This collection supports three forms: `SubAgent` (declarative synchronous subagent spec), `CompiledSubAgent` (a pre-compiled runnable subagent), `AsyncSubAgent` (a remote/background subagent spec). `SubAgent` entries are invoked through the `task` tool. They should provide `name`, `description`, and `system_prompt`, and may also override `tools`, `model`, `middleware`, `interrupt_on`, and `skills`. `CompiledSubAgent` entries are also exposed through the `task` tool, but provide a pre-built `runnable` instead of a declarative prompt and tool configuration. `AsyncSubAgent` entries are identified by their async-subagent fields (`graph_id`, and optionally `url`/`headers`) and are routed into `AsyncSubAgentMiddleware` instead of `SubAgentMiddleware`. They should provide `name`, `description`, and `graph_id`, and may optionally include `url` and `headers`. These subagents run as background tasks and expose the async subagent tools for launching, checking, updating, cancelling, and listing tasks. If no subagent named `general-purpose` is provided, a default general-purpose synchronous subagent is added automatically unless the active harness profile disables it. With no synchronous subagents in play — none passed and the default disabled via `general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False)` — the `task` tool is not exposed. Async subagents are independent. (default: `None`) |
| `skills` | `list[str] \| None` | No | List of skill source paths (e.g., `["/skills/user/", "/skills/project/"]`). Paths must be specified using POSIX conventions (forward slashes) and are relative to the backend's root. When using `StateBackend` (default), provide skill files via `invoke(files={...})`. With `FilesystemBackend`, skills are loaded from disk relative to the backend's `root_dir`. Later sources override earlier ones for skills with the same name (last one wins). (default: `None`) |
| `memory` | `list[str] \| None` | No | List of memory file paths (`AGENTS.md` files) to load (e.g., `["/memory/AGENTS.md"]`). Display names are automatically derived from paths. Memory is loaded at agent startup and added into the system prompt. (default: `None`) |
| `permissions` | `list[FilesystemPermission] \| None` | No | List of `FilesystemPermission` rules for the main agent and its subagents. Rules are evaluated in declaration order; the first match wins. If no rule matches, the call is allowed. Subagents inherit these rules unless they specify their own `permissions` field, which replaces the parent's rules entirely. `FilesystemMiddleware` applies these permissions at the tool level for its built-in filesystem tools, not at the backend level. Direct backend usage does not currently incorporate `permissions`. (default: `None`) |
| `backend` | `BackendProtocol \| BackendFactory \| None` | No | Optional backend for file storage and execution. Pass a `Backend` instance (e.g. `StateBackend()`). For execution support, use a backend that implements `SandboxBackendProtocol`. (default: `None`) |
| `interrupt_on` | `dict[str, bool \| InterruptOnConfig] \| None` | No | Mapping of tool names to interrupt configs. Pass to pause agent execution at specified tool calls for human approval or modification. This config always applies to the main agent. For subagents: Declarative `SubAgent` specs inherit the top-level `interrupt_on` config by default. If a declarative `SubAgent` provides its own `interrupt_on`, that subagent-specific config overrides the inherited top-level config. `CompiledSubAgent` runnables do not inherit top-level `interrupt_on`; configure human-in-the-loop behavior inside the compiled runnable itself. Remote `AsyncSubAgent` specs do not inherit top-level `interrupt_on`; configure any approval behavior on the remote subagent itself. For example, `interrupt_on={"edit_file": True}` pauses before every edit. (default: `None`) |
| `response_format` | `ResponseFormat[ResponseT] \| type[ResponseT] \| dict[str, Any] \| None` | No | A structured output response format to use for the agent. (default: `None`) |
| `context_schema` | `type[ContextT] \| None` | No | Schema class that defines immutable run-scoped context. Passed through to `create_agent`. (default: `None`) |
| `checkpointer` | `Checkpointer \| None` | No | Optional `Checkpointer` for persisting agent state between runs. Passed through to `create_agent`. (default: `None`) |
| `store` | `BaseStore \| None` | No | Optional store for persistent storage (required if backend uses `StoreBackend`). Passed through to `create_agent`. (default: `None`) |
| `debug` | `bool` | No | Whether to enable debug mode. Passed through to `create_agent`. (default: `False`) |
| `name` | `str \| None` | No | The name of the agent. Passed through to `create_agent`. (default: `None`) |
| `cache` | `BaseCache \| None` | No | The cache to use for the agent. Passed through to `create_agent`. (default: `None`) |

## Returns

`CompiledStateGraph[AgentState[ResponseT], ContextT, _InputAgentState, _OutputAgentState[ResponseT]]`

A configured deep agent.

---

[View source on GitHub](https://github.com/langchain-ai/deepagents/blob/ef4c71763086a4e4899ba7ced6f9eb478d38069e/libs/deepagents/deepagents/graph.py#L203)

---
출처: https://reference.langchain.com/python/deepagents/graph/create_deep_agent
