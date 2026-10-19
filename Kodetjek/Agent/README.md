# Agent

**What it is:** the brain and the entry point. It owns the web page, the loop and the connection to Gemini.

**What it does:** it takes the developer's question, lets Gemini decide the next step, runs the tools Gemini asks for, and repeats until Gemini has an answer. Each step is shown live on the page (flow steps 1, 2, 9–15 and 17–20 in the [main README](../README.md#the-flow)).

**Why it's there:** a question like "does our code solve US-005?" can't be answered in one go. Someone has to decide what to look up, what to read next, and when there is enough to answer. That someone is the agent. The other layers only do what they are told.

| Folder | Contents | Why |
|---|---|---|
| `domain/` | `Decision`, `Action`, `Observation`, `Step`, `AgentRun`, `Finding`, `Assessment` and the `AgentBrain` port | Describes a step without knowing which model takes it. |
| `application/` | `AgentService.run()`: think, act, observe, repeat. `AnswerWriter`: turns the assessment into the answer for a role | The loop is the same whatever the model or tools are. The writer gets no tools, so the role can only change how the answer is written, not what was found. |
| `infrastructure/` | `GeminiBrain`: the only file that knows the Gemini SDK | Changing model means replacing this file, nothing else. |
| `api/` | `web.py` (the page) and `build.py` (wires all four layers together) | The only place that knows every layer, so the rest stay independent. |

`MAX_STEPS` in `settings.py` stops an agent that goes in circles.
