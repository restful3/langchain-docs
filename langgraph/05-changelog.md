# Changelog

Log of updates and improvements to our Python packages

**Subscribe**: Our changelog includes an [RSS feed](https://docs.langchain.com/oss/python/releases/changelog/rss.xml) that can integrate with [Slack](https://slack.com/help/articles/218688467-Add-RSS-feeds-to-Slack), [email](https://zapier.com/apps/email/integrations/rss/1441/send-new-rss-feed-entries-via-email), Discord bots like [Readybot](https://readybot.io/) or [RSS Feeds to Discord Bot](https://rss.app/en/bots/rssfeeds-discord-bot), and other subscription tools.

## May 12, 2026

### `deepagents` v0.6.0

- **`CodeInterpreterMiddleware`** (experimental): Enables code execution and programmatic tool calling through a scoped QuickJS runtime.
- Supports `version="v3"` in `stream_events` / `astream_events` (see the event streaming guide).
- **`DeltaChannel`** (beta): Message history and agent files now use incremental delta storage instead of re-serializing the full accumulated value into every checkpoint, keeping checkpoint sizes small for long threads.
- **Harness profiles**: Register configuration bundles (`HarnessProfile`) applied automatically when a model is selected — system-prompt tweaks, tool overrides, middleware changes, and subagent defaults — without modifying call sites.
- **`ContextHubBackend`**: A new filesystem backend backed by LangSmith Hub for storing agent files as Hub commits, with version history on every write and LangSmith-native durability.

### `langchain` v1.3.0

- Adds support for `version="v3"` in `stream_events` / `astream_events` for agents (see the event streaming guide).

### `langgraph` v1.2.0

- **`DeltaChannel`** (beta): New channel type storing only the incremental delta at each step rather than re-serializing the full accumulated value. Includes `snapshot_frequency=K` for full snapshots every K steps.
- **Per-node timeouts**: Pass `timeout=` to `add_node` for wall-clock (`run_timeout`) or idle limits (`idle_timeout`). Raises `NodeTimeoutError`, clears writes, and hands off to the retry policy (async nodes only).
- **Node-level error handlers**: Pass `error_handler=` to `add_node` to run recovery functions after retries are exhausted, receiving a typed `NodeError` and returning a `Command` for state updates and routing.
- **Graceful shutdown**: Stop in-flight runs cooperatively after the current superstep, saving a resumable checkpoint via `RunControl.request_drain()`.
- **New event streaming API (beta)**: Pass `version="v3"` to `stream_events()` / `astream_events()` for a content-block-centric protocol with typed, per-channel projections. Includes `run.messages` for one `ChatModelStream` per LLM call with typed sub-projections for text, reasoning, tool calls, and usage.

## Apr 7, 2026

### `deepagents` v0.5.0

- **Async subagents**: Launch non-blocking background tasks for concurrent execution while users interact with the agent (requires LangSmith Deployment).
- **Multi-modal support**: The `read_file` tool now supports PDFs, audio, and video files alongside images.
- **Backend protocol updates**: File format changes for binary file support; improved error propagation from backends to tools; direct instantiation of `StateBackend()` and `StoreBackend()` (factory pattern deprecated).
- **Anthropic prompt caching improvements**.

## Mar 10, 2026

### `langgraph` v1.1.0

- **Type-safe streaming (`version="v2"`)**: Unified `StreamPart` output with `type`, `ns`, and `data` keys; each mode has its own `TypedDict` importable from `langgraph.types`.
- **Type-safe invoke (`version="v2"`)**: `invoke()` / `ainvoke()` return `GraphOutput` objects with `.value` and `.interrupts` attributes.
- **Pydantic and dataclass coercion**: With `version="v2"`, output automatically coerces to the declared Pydantic model or dataclass types.
- Fixed time travel with interrupts and subgraphs (replays no longer reuse stale `RESUME` values; subgraphs correctly restore parent checkpoint state).
- Fully backward compatible; `version="v2"` is opt-in.

## Feb 10, 2026

### `deepagents` v0.4.0

- New integration packages for pluggable sandboxes: `langchain-modal`, `langchain-daytona`, and `langchain-runloop`.
- **Conversation history summarization**: Now triggered via `wrap_model_call` events; full message history retained; improved token counting; automatic triggering on `ContextOverflowError`.
- OpenAI model strings prefixed with `"openai:"` now default to the Responses API.

## Dec 15, 2025

### `langchain` v1.2.0

- **`create_agent`**: Simplified support for provider-specific tool parameters and definitions via a new [`extras`](https://reference.langchain.com/python/langchain/tools/#langchain.tools.BaseTool.extras) attribute on [`tools`](https://docs.langchain.com/oss/python/langchain/tools). Examples:
  - Provider-specific configuration such as Anthropic's [programmatic tool calling](https://docs.langchain.com/oss/python/integrations/chat/anthropic#programmatic-tool-calling) and [tool search](https://docs.langchain.com/oss/python/integrations/chat/anthropic#tool-search).
  - Built-in tools that are executed client-side, as supported by [Anthropic](https://docs.langchain.com/oss/python/integrations/chat/anthropic#built-in-tools), [OpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai#responses-api), and other providers.
- Support for strict schema-adherence in agent `response_format` (see [ProviderStrategy](https://docs.langchain.com/oss/python/langchain/structured-output#provider-strategy) docs).

## Dec 8, 2025

### `langchain-google-genai` v4.0.0

We've re-written the Google GenAI integration to use Google's consolidated Generative AI SDK, which provides access to the Gemini API and Vertex AI Platform under the same interface. This includes minimal breaking changes as well as deprecated packages in `langchain-google-vertexai`.

See the full [release notes and migration guide](https://github.com/langchain-ai/langchain-google/discussions/1422) for details.

## Nov 25, 2025

### `langchain` v1.1.0

- [**Model profiles**](https://docs.langchain.com/oss/python/langchain/models#model-profiles): Chat models now expose supported features and capabilities through a `.profile` attribute. These data are derived from [models.dev](https://models.dev), an open source project providing model capability data.
- [**Summarization middleware**](https://docs.langchain.com/oss/python/langchain/middleware/built-in#summarization): Updated to support flexible trigger points using model profiles for context-aware summarization.
- [**Structured output**](https://docs.langchain.com/oss/python/langchain/structured-output): [`ProviderStrategy`](https://docs.langchain.com/oss/python/langchain/structured-output#provider-strategy) support (native structured output) can now be inferred from model profiles.
- [**`SystemMessage` for `create_agent`**](https://docs.langchain.com/oss/python/langchain/middleware/custom#working-with-system-messages): Support for passing `SystemMessage` instances directly to `create_agent`'s `system_prompt` parameter, enabling advanced features like cache control and structured content blocks.
- [**Model retry middleware**](https://docs.langchain.com/oss/python/langchain/middleware/built-in#model-retry): New middleware for automatically retrying failed model calls with configurable exponential backoff.
- [**Content moderation middleware**](https://docs.langchain.com/oss/python/langchain/middleware/built-in#content-moderation): OpenAI content moderation middleware for detecting and handling unsafe content in agent interactions. Supports checking user input, model output, and tool results.

## Oct 20, 2025

### v1.0.0

#### `langchain`

- [Release notes](https://docs.langchain.com/oss/python/releases/langchain-v1)
- [Migration guide](https://docs.langchain.com/oss/python/migrate/langchain-v1)

#### `langgraph`

- [Release notes](https://docs.langchain.com/oss/python/releases/langgraph-v1)
- [Migration guide](https://docs.langchain.com/oss/python/migrate/langgraph-v1)

> If you encounter any issues or have feedback, please [open an issue](https://github.com/langchain-ai/docs/issues/new?template=01-langchain.yml) so we can improve. To view v0.x documentation, [go to the archived content](https://github.com/langchain-ai/langchain/tree/v0.3/docs/docs) and [API reference](https://reference.langchain.com/v0.3/python/).
