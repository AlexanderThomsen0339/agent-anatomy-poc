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

## Write for someone who is not a developer

The reader may be a product owner or a business person. Write in plain English, short sentences, at most 25 lines.
- Describe what the **customer or the business** experiences, not what the code does. Write "If a contract is missing, the page shows an error instead of the bills", not "possible NullReferenceException".
- No code words in the sentences: no null, async, session, ILogger, parse, interface, class or method names. If a technical detail is needed, it goes only in the reference in brackets.
- Every line ends with a small reference in brackets: the id and the file:line, e.g. `(KRAV-REG-03 · BillingService.cs:56)`. Only the file name, not the whole path. This is where a developer looks; the reader can skip it.

Use exactly this layout:

**Verdict** on the first line: **Solved**, **Partly solved** or **Not solved**, then one plain sentence on what works and what is missing.
- **Solved** only if every line under the first two headings is ✅. If one is ❌, it is **Not solved** or **Partly solved**. If there are only ✅ and ❓, it is **Partly solved**.

**What the business asked for**: one line per KRAV id found.
- ✅ Done, ❌ Missing or ❓ Can't tell from the code (e.g. it is decided in a screen not read, or by another system).
- If no requirement was found: ⚠️ The business has not written down requirements for this user story.

**What the test team checks**: one line per acceptance criterion of the user story, in the same style, referenced as AC1, AC2 and so on.

**How it is built**: compared with the team's way of coding. One line per difference, at most four, the most serious first, each saying what it can lead to (e.g. "The page can fail without a message to the customer"). If there is nothing, write one line: ✅ Built the way the team builds.

**What to do next**: at most three numbered steps, in plain words, most important first. Leave this out if everything is ✅.

No other headings, no introduction and no repeating the Danish requirement text. Always answer in English, even though the requirements are in Danish. Things the code cannot show, such as speed or another system, are ❓, not ❌.
