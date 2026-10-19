---
name: code-review
description: Use when someone asks whether the code solves a user story, meets acceptance criteria, passes test cases or meets the business requirements.
---

# How we review code

There are two sources of requirements, and the code is checked against both:
- **Test criteria**: the user story and its acceptance criteria, from `search_requirements`. They say what the test team checks.
- **Business requirements (kravspec)**: requirements with ids like KRAV-REG-03, from `search_specification`. They say what the business ordered.

First find the requirements and the code. Never guess:
- Look up the user story with `search_requirements`. The data is in Danish, so search with the user story id (e.g. US-002) and Danish words from the title.
- **Pick the right user story.** The same US id exists in several areas (Regninger, Min Profil, Mit Overblik). Use the one whose title or area matches the question. If the question gives no title, use the area the code is about (e.g. billing code means Regninger). Never use a user story whose text is only "Opdateres…"; it has no criteria yet.
- Look up the business requirements with `search_specification`, using the user story id and Danish words. Keep every requirement whose "Dækker" line names this user story and whose file is for the same area (e.g. `Kravspec_Regninger.md` for Regninger).
- Load how the team that owns the code builds its solutions with `load_skill` (e.g. `architecture-web`). The system prompt names the team.
- Find the relevant files with `list_code_files`, and read them with `read_code_file`. Read the controller, view, script and service that belong to the task, not only one file.

Only judge against the requirements you found and the team's way of coding. Never invent a requirement, a criterion or a file:line. If `search_specification` finds no requirement for the user story, say so.

## Who is asking

The question says who is asking: a developer or a product/communication person. Load the matching skill with `load_skill` after you have judged the requirements (below), and write it exactly as that skill says:
- `audience-developer` for a developer.
- `audience-product` for a product owner, communication or other business person.
If the question does not say, use `audience-product`.

## Judge first, then write

Who is asking only changes how the answer is written, never what you find. A developer and a product person asking about the same code must get the same verdict, the same count and the same missing requirements.

So before you load the audience skill, give every KRAV id and acceptance criterion exactly one status:
- **Met**: code you have read does what the requirement says.
- **Not met**: code you have read does it differently, or nothing in the code does it. A format, a sort order, an error message or a log call can be seen in the code, so it is never "can't tell". Formatting is done where the value is shown (the view), so read the view before you decide.
- **Can't tell**: only when it depends on something outside the code, such as speed, another system or real data.

Then the verdict follows from the statuses, whoever is asking:
- **Solved**, **Partly solved** or **Not solved**, then: "X of Y requirements met." X is the number of Met, Y is the number of all statuses.
- **Solved** only if all are Met. **Not solved** if none are Met. Otherwise **Partly solved**.
- Every Not met id is named under Missing in the answer, so Met + Not met + Can't tell adds up to Y. If there are more than the audience skill allows lines, put several ids on one line; never drop one.
- If no business requirement was found, add: "The business has not written down requirements for this."

Always answer in English, even though the requirements are in Danish.
