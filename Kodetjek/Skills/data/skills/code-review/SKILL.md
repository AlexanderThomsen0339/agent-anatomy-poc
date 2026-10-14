---
name: code-review
description: Use when a developer asks whether their code solves a user story, meets acceptance criteria or passes test cases.
---

# How we review code

First find the requirements and the code. Never guess:
- Look up the user story and its acceptance criteria with `search_requirements`. The requirements are written in Danish, so search with the user story id (e.g. US-002) and Danish words from the task.
- Find the relevant files with `list_code_files`, and read them with `read_code_file`. Only read the files that belong to the task.

Then write the review in English. It is read by a busy developer, so keep it short, at most 15 lines:
- The first line is the verdict: **Solved**, **Partly solved** or **Not solved**, followed by one short sentence on why.
  - **Solved** only if every criterion is ✅. If one is ❌, it is **Not solved** or **Partly solved**. If there are only ✅ and ❓, it is **Partly solved**.
- Then one bullet per acceptance criterion, on one line:
  - ✅ Met, ❌ Not met or ❓ Cannot be decided from the code.
  - The criterion in a few English words, and a file:line reference. Only the file name, not the whole path.
- End with at most three suggested fixes, one line each. If everything is ✅, write no suggestions.
- No headings, no repeating the requirement text and no introduction.
- Always answer in English, even though the requirements are in Danish. Criteria about something the code cannot show (e.g. performance or syncing to another system) are marked ❓, not ❌.
