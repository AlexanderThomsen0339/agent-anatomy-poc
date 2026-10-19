---
name: code-review
description: Use when a developer asks whether their code solves a user story, meets acceptance criteria, passes test cases or meets the business requirements.
---

# How we review code

There are two sources, and the code is checked against both:
- **Test criteria**: the user story and its acceptance criteria, from `search_requirements`. They say what the test team checks.
- **Business requirements (kravspec)**: requirements with ids like KRAV-REG-03, from `search_specification`. They say what the business ordered.

First find the requirements and the code. Never guess:
- Look up the user story with `search_requirements`. The data is in Danish, so search with the user story id (e.g. US-002) and Danish words from the task.
- Look up the business requirements with `search_specification`, using the user story id (e.g. US-002) and Danish words. Keep only requirements whose "Dækker" line names this user story and whose file is for the same area as the user story (e.g. `Kravspec_Regninger.md` for a user story in the Regninger workbook). The same US id exists in several areas.
- Find the relevant files with `list_code_files`, and read them with `read_code_file`. Only read the files that belong to the task.

Only judge against requirements you found. Never invent a requirement, a criterion or a file:line. If `search_specification` finds no requirement for the user story, say so: the verdict is then only against the test criteria.

Then write the review in English. It is read by a busy developer, so keep it short, at most 20 lines:
- The first line is the verdict: **Solved**, **Partly solved** or **Not solved**, followed by one short sentence on why.
  - **Solved** only if every line below is ✅. If one is ❌, it is **Not solved** or **Partly solved**. If there are only ✅ and ❓, it is **Partly solved**.
- Then the line **Business requirements**, with one bullet per KRAV id, on one line:
  - ✅ Met, ❌ Not met or ❓ Cannot be decided from the code.
  - The KRAV id, the requirement in a few English words, and a file:line reference. Only the file name, not the whole path.
  - If no requirement was found, write one bullet instead: ⚠️ No business requirement documented for this user story.
- Then the line **Test criteria**, with one bullet per acceptance criterion in the same format, numbered as in the user story (e.g. AC3).
- End with at most three suggested fixes, one line each. If everything is ✅, write no suggestions.
- No headings beyond the two lines above, no repeating the requirement text and no introduction.
- Always answer in English, even though the requirements are in Danish. Requirements about something the code cannot show (e.g. performance or syncing to another system) are marked ❓, not ❌.
