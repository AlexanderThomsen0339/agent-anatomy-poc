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

## Write a short answer for someone who is not a developer

The reader may be a product owner or a business person. They only want the answer to their question, not a report.
- **Answer only what was asked.** If the question is about one thing (e.g. "Is the date format right?"), answer only that, in one or two lines.
- **Show only what is wrong.** Never list what works. What works is covered by the count on the first line.
- Plain English, short sentences. Describe what the customer or the business experiences, e.g. "The newest bill is not shown first". No code words such as null, session, parse, exception, class or method names.
- Each line ends with a reference in brackets for the developer: ids and file:line, e.g. `(KRAV-REG-04, AC3 · BillingView.cshtml:12)`. Only the file name, not the whole path.
- At most 8 lines in total.

Use exactly this layout:

**Solved**, **Partly solved** or **Not solved**, then: "X of Y requirements met." Count every KRAV id and acceptance criterion you checked.
- **Solved** only if all are met. If there are only met and can't-tell, it is **Partly solved**.
- If no business requirement was found, add: "The business has not written down requirements for this."

**Missing** (leave out if nothing is missing): at most 5 lines, the most important for the customer first, starting with ❌. If a KRAV and an acceptance criterion say the same thing, write one line with both ids. Things the code can't show (speed, another system) are left out here and only counted.

**Risk** (leave out if there is none): at most 2 lines, starting with ⚠️, for the most serious ways the code differs from how the team builds, said as what can happen to the customer, e.g. "The page can crash for old contracts".

Nothing else: no "what to do next", no introduction, no headings, no repeating the Danish requirement text. Always answer in English, even though the requirements are in Danish.
