# MCP

**What it is:** the agent's hands. A fixed list of tools, each with a name, a description and the input it takes. The name comes from the Model Context Protocol, the standard for describing tools to an LLM. The AI Platform POC uses the same idea (`ToolSpec`, `ToolCall`, `ToolResult`) inside the program, without running an MCP server.

**What it does:** it gives a role five code-check tools if it sees web, and `search_ot_documents` if it sees OT (`ROLE_TEAMS` in `settings.py`) and runs them when asked:

| Tool | Does | Why |
|---|---|---|
| `search_requirements` | Searches the user stories and test cases | Wraps the RAG search as a tool, so the agent chooses what to search for. |
| `search_specification` | Searches the business requirements (kravspec) | A separate source from the tests. A US id returns exactly the requirements that cover it, or "not documented", so the agent can't invent one. |
| `search_ot_documents` | Searches the OT team's documents, such as the signal list and PDFs. It returns PDF pages first and signal rows second, from separate indexes, so the signal list never hides a document. With `exact: true` it returns only the documents and pages that contain the words word for word, e.g. "BERAN backup". Only roles that see OT (IT and Vedligehold) get it, from `build_ot_service()` | Maintenance needs to find signals by code or Danish description. Its own index and tool set keep them apart from the requirements and the code. |
| `list_code_files` | Lists the files in `CODE_FOLDER` | The agent has to find the relevant files before it can read them. |
| `read_code_file` | Returns one file with line numbers | Line numbers let the answer point to `file:line`. Paths outside `CODE_FOLDER` are refused. |
| `list_recent_changes` | Shows the newest commits on the branch with their changed lines | A fresh change in a file further down (e.g. a manager) can break a task. Without the history the agent only reads the files whose names match the task. |

`load_skill` comes from the Skills layer but uses the same `ToolSpec`, so the agent would see it as just another tool. It is only given when there are skills the agent can choose itself; `code-review` and `architecture-<TEAM>` are put in the system prompt.

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
| `domain/` | `ToolSpec`, `ToolCall`, `ToolResult`, `PullRequest`, `Checkout` and the `Tool`, `CodeRepository` and `PullRequestFinder` ports | One shape for every tool, so the agent treats them all the same. |
| `application/` | `ToolService`: find a tool by name and run it. `CheckoutService`: pick the branch for a question (an open pull request into `dev` with the user story id, otherwise `dev`) and fetch it | One place for lookup and error handling, and one place for IT's git rule. |
| `infrastructure/` | The five tools above, `GitRepository`, which clones `CODE_REPO` into `CODE_FOLDER` and fetches a branch, and `AzurePullRequestFinder`, which finds open pull requests through Azure DevOps' REST API | Each tool is one file. Adding a tool means adding a file. The code tools only read a folder, so they don't need to know the code comes from a repo. |
| `api/` | `build.py`: `build_service()` loads the requirements into RAG and creates the code-check tools; `build_ot_service()` loads OT's documents and creates `search_ot_documents`; `build_checkout_service()` creates the repo, the pull request search and the branch choice, and fetches the code at start | Settings (`CODE_REPO`, `CODE_FOLDER`, `SEARCH_K`, `OT_FOLDER`, `OT_SEARCH_K`) are read here and passed in. |
