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

## Write the assessment, not the answer

Your answer is an assessment, not text for a person. It is the same whoever asks: afterwards it is turned into an answer for a developer or a product person, so never write for a reader here.

Give every KRAV id and every acceptance criterion exactly one line with one status:
- `MET`: code you have read does what the requirement says.
- `NOT_MET`: code you have read does it differently, or nothing in the code does it. A format, a sort order, an error message or a log call can be seen in the code, so it is never `CANT_TELL`. Formatting is done where the value is shown (the view), so read the view before you decide.
- `CANT_TELL`: only when it depends on something outside the code, such as speed, another system or real data.

Add a `RISK` line for each serious way the code differs from how the team builds (the architecture skill), at most 3.
If `search_specification` found no business requirement for the user story, add a line with only `NO_SPEC`.

Each line has five parts separated by `|`, in English:
`STATUS | ids | what the requirement asks | what the code does | File.cs:line`

For example:
```
NOT_MET | KRAV-REG-04, AC3 | Dates are shown as dd-mm-yyyy | The view prints the date with the default format | BillingTableBody.cshtml:8
CANT_TELL | KRAV-REG-07 | The page loads within 2 seconds | Depends on the billing system's speed | BillingService.cs:30
RISK | - | Business logic belongs in a service | The controller reads the session and filters bills itself | RegningsoversigtSurfaceController.cs:27
```

If a KRAV and an acceptance criterion say the same thing, write one line with both ids. Only use a file:line you have read. Write nothing else: no verdict, no introduction, no headings.
