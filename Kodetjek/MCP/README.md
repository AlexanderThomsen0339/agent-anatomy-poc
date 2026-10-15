# MCP

**What it is:** the agent's hands. A fixed list of tools, each with a name, a description and the input it takes. The name comes from the Model Context Protocol, the standard for describing tools to an LLM. Kodetjek uses the same idea (`ToolSpec`, `ToolCall`, `ToolResult`) inside the program, without running an MCP server.

**What it does:** it gives Gemini three tools and runs them when asked:

| Tool | Does | Why |
|---|---|---|
| `search_requirements` | Searches the user stories and test cases | Wraps the RAG search as a tool, so the agent chooses what to search for. |
| `list_code_files` | Lists the files in `CODE_FOLDER` | The agent has to find the relevant files before it can read them. |
| `read_code_file` | Returns one file with line numbers | Line numbers let the answer point to `file:line`. Paths outside `CODE_FOLDER` are refused. |

The fourth tool, `load_skill`, comes from the Skills layer but uses the same `ToolSpec`, so the agent sees four tools of the same kind.

**Why it's there:** without tools, Gemini can only guess. MCP lets it look things up and read the code, while keeping the access small and read-only. `ToolService.call()` turns any error into a result Gemini can read, so a failing tool never crashes the agent.

## Why MCP is not the entry point

It is tempting to draw the flow as MCP → Agent → RAG, but the question goes to the agent first: **agent → MCP → RAG → back to the agent.**

- **MCP doesn't decide anything.** A tool runs when it is called, with the arguments it is given. It can't tell which tool a question needs, in which order, or when to stop. Only the agent can.
- **The user asks for an outcome, not a tool call.** "Does our code solve US-005?" needs a search, a file list and several file reads. Turning that into tool calls is the agent's job.
- **Tools are shared, the decision is not.** The same tools could serve other agents or other questions. Putting the entry point in MCP would tie them to one flow.
- **This is how MCP is meant to be used.** In the protocol, the *client* (the agent: Claude Desktop, an IDE, here `AgentService`) calls the *server* (the tools). The server never starts the conversation.

So MCP is the wall socket and RAG is one of the appliances plugged into it. The agent decides what to plug in.

| Folder | Contents | Why |
|---|---|---|
| `domain/` | `ToolSpec`, `ToolCall`, `ToolResult` and the `Tool` port | One shape for every tool, so the agent treats them all the same. |
| `application/` | `ToolService`: find a tool by name and run it | One place for lookup and error handling. |
| `infrastructure/` | The three tools above | Each tool is one file. Adding a tool means adding a file. |
| `api/` | `build.py`: loads the requirements into RAG and creates the tools | Settings (`CODE_FOLDER`, `SEARCH_K`) are read here and passed in. |
