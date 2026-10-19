# Skills

**What it is:** instructions the agent can load when a task needs them. Each skill is a folder in `data/skills/` with a `SKILL.md`: a name, a one-line description and the full instructions.

**What it does:** the names and descriptions go into the system prompt as a catalog (flow step 3). When Gemini sees a task that fits, it calls `load_skill` and gets the full instructions (step 16a). Kodetjek has two skills. `code-review` sets the answer format for a reader who is not a developer: a verdict with "X of Y requirements met", then only what is *Missing* and at most two *Risks*, at most 8 lines in plain English, with the id and `file:line` in brackets at the end of each line. It also forbids invented requirements: if none is found, the answer says so. `architecture-web` describes how the Web team codes: Umbraco Surface controllers → services in `Core/<Feature>/Services` → managers in `Shared/Managers`, interfaces and constructor injection, mapping to the feature's own models, and the quality the team expects. It is defined in advance and has no link to a project or to the requirements in RAG, so it works for every Web project without being updated alongside it. `TEAM` in `settings.py` tells the agent which team's skill to load, so FDAP could get its own `architecture-fdap`. The content is a draft, not yet approved by the team.

**Why it's there:**
- **The rules are text, not code.** Changing the answer format means editing `SKILL.md`, not Python.
- **The system prompt stays short.** Only the catalog is always there. The full instructions are loaded when they are needed.
- **New kinds of tasks are a new folder.** A `test-plan` skill could be added next to `code-review`, and the same agent would pick the right one.

`LoadSkillTool` lives here but uses MCP's `ToolSpec`, so the agent sees it as just another tool.

| Folder | Contents | Why |
|---|---|---|
| `domain/` | `Skill`, `SkillSummary` and the `SkillRepository` port | Describes a skill without knowing where it is stored. |
| `application/` | `SkillService`: list, catalog, load | One place to build the catalog and handle unknown names. |
| `infrastructure/` | `FileSkillRepository`: reads `SKILL.md` files | Skills could come from a database instead by replacing this file. |
| `api/` | `build.py` and `skill_tool.py` (`load_skill`) | Connects the skills to the agent as a tool. |
| `data/skills/` | `code-review/SKILL.md`, `architecture-web/SKILL.md` | The skills themselves. |
