---
name: code-review
description: Checks whether the code meets a user story's acceptance criteria and the business requirements, and writes one status line per requirement. Use when someone asks whether the code solves a user story, passes its test cases or meets the requirements. Implements evaluation's Node 1-4 quality gates for this codebase.
---

# How we review code

This skill is where `evaluation`'s node graph is actually implemented for a code check. Each step below satisfies one of evaluation's quality gates, in the same order:

| evaluation node | Gate | Satisfied by |
|---|---|---|
| Node 1: Initial Prompt Analysis | Identify the module (here: the area — Regninger, Profil or Overblik) from the prompt | Step 1 below: "Find the area the question is about" |
| Node 2: Contribution Scan (fallback) | If the area can't be identified from the prompt, resolve it from recent changes | Step 1.3 below: `list_recent_changes`, when the question doesn't name an area |
| Node 3: Retrieve Testing Protocols | Locate and parse the testing protocol for the module | Step 1.1-1.2 below: `search_requirements` and `search_specification` |
| Node 4: Evaluate User Story & Test Case Conflicts | Cross-reference the changes against the module's user stories and test cases | Section 2 below: giving each requirement a status |

A requirement line this skill writes is a Node 4 result; do not skip straight to writing one without having gone through Nodes 1-3 first (never guess the area, the testing protocol or the code, as section 1 says).

A **requirement** is either an acceptance criterion or a business requirement. The code is checked against both:
- **Acceptance criteria** (AC1, AC2 ...): the user story's Acceptkriterier, from `search_requirements`. They say what the test team checks.
- **Business requirements** (ids like KRAV-REG-03): the kravspec, from `search_specification`. They say what the business ordered.

## 1. Find the requirements and the code

Never guess what the requirements or the code say. Do these steps in order:
1. Find the area the question is about, e.g. Regninger, Profil or Overblik. Each area numbers its user stories from US-001, so an id alone is not enough: every block from `search_requirements` starts with `Område:`. Look up the user story with `search_requirements`, using the area, the id (e.g. US-002) and Danish words from its title. Use only the user story whose area, id and title match the question.
2. Look up the business requirements with `search_specification`, using the user story id and Danish words. Keep every business requirement whose "Dækker" line names this user story and whose file covers the same area.
3. Look at the newest commits: they are in the question, or use `list_recent_changes`. A change in a file the task depends on (e.g. a manager the service calls) can break it, even if the file's name doesn't match the task.
4. Find the files with `list_code_files`, and read them with `read_code_file`: the controller, view (`.cshtml`), service, model and manager that belong to the task, and the files changed in the newest commits.

Only judge against the requirements you found and the team's way of coding below. Never invent a requirement or a file:line.

### Is the question clear enough?
Before you assess, decide if you know what the user wants checked.
- **Clear**: the question names a user story, or a page or feature that only one user story covers, or it asks about the latest changes and the newest commits all belong to one feature. Then assess it.
- **Broad**: the question asks about everything, e.g. "Hvilke tests mangler at blive løst?" or "alle tests". That is clear too: assess every user story in the area it names, or else in the areas the newest commits change. Put the user story id in front of each AC, e.g. `US-002 AC1`, so lines from different user stories can be told apart.
- **Unclear**: the question could mean several things, or you would have to guess what to check, e.g. "Virker det?", "Er regningerne ok?" or "Diaco siger, de seneste ændringer virker. Gør de det?" when his commits touch more than one feature. Then don't assess yet.

When it is unclear, first look (the newest commits, `search_requirements`) so you can make a good guess. Then write only one line: `QUESTION:` followed by your best guess as a question to the user, in plain Danish, like a colleague would ask. Say what you think they mean, why you think so, and the most likely alternative. No code words, file names or AC numbers; a user story is named by its title. For example:
`QUESTION: Jeg tror, du spørger, om regningsoversigten stadig virker, fordi Diacos seneste ændring er i forbindelsen til regningssystemet. Skal jeg tjekke det, eller mener du hans ændring af profilsiden?`

Ask at most once. If the earlier conversation already has your question, the user's answer settles it: "ja" or similar means your guess, otherwise use what they wrote. Then assess, and never ask again.

## 2. Give each requirement one status

- `MET`: code you have read does what the requirement says. When the requirement names an exact value (a text, a file name, a format or a status word), the code must use the same value, character for character. A translation or another name is `NOT_MET`.
- `NOT_MET`: code you have read does it differently, or nothing in the code does it. A format, a sort order, an error message or a log call can be seen in the code, so it is never `CANT_TELL`. Formatting can happen in the service, the view model or the view, so read all of them before you decide.
- `CANT_TELL`: only when it depends on something outside the code, such as speed, another system or real data.

Add a `RISK` line for each serious way the code differs from how the team codes, at most 3.
If `search_specification` found no business requirement for the user story, add a line with only `NO_SPEC`.

## 3. Write the assessment

Before you write, check:
- [ ] Every AC number from the user story has exactly one line.
- [ ] Every business requirement you kept has exactly one line. If it says the same as an AC, both ids share one line.
- [ ] Every file:line is in a file you have read.

Your text is an assessment, not an answer: it is the same whoever asks, and another step writes the answer for the reader. ALWAYS use exactly this format, one line per requirement, seven parts separated by `|`. The status word stays in English; the rest is in Danish:
`STATUS | ids | what the requirement asks | why, in plain words | what the code does | file.cs:line | how to fix`

- **Why, in plain words** is for a reader who never sees code, such as the communication team. Say what the customer sees or can't do, and the cause in everyday words. If a recent commit caused it, name its author and what they changed, in plain words. No code words: no file, class, method, variable, value in backticks, null, session, exception or parse. One sentence. For `MET`, write what the customer gets.
- **What the code does** is technical and exact: the method, the expression or the value, in backticks.
- **How to fix** is the concrete code change. Leave it empty for `MET`. For `CANT_TELL`, say what would show it (a test, a log, another repo).

When one cause breaks several requirements (e.g. the page fails to load), every line still gets its own status, but they share the same why.

For example:
```
NOT_MET | KRAV-REG-04, AC7 | Datoer vises som dd-mm-åååå | Kunden ser datoen som 2026-03-01 i stedet for 01-03-2026, fordi datoen vises, som den kommer fra regningssystemet | `@row.InvoiceDate` udskriver den rå værdi i ISO-format | Views/Partials/BillingTableBody.cshtml:8 | Formatér i mappingen med `date.ToString("dd-MM-yyyy", CultureInfo.InvariantCulture)`
NOT_MET | AC1 | Kunden kan se sine regninger | Siden med regninger kan ikke åbne, fordi Katjas ændring af forbindelsen til regningssystemet i går fjernede den del, siden henter regningerne med | `GetInvoices()` findes ikke længere i `XellentManager`, så `BillingService` fejler | Core/Billing/Services/BillingService.cs:30 | Genindfør `GetInvoices()` i `XellentManager` eller kald den nye metode
CANT_TELL | AC9 | Siden indlæses på under 2 sekunder | Det afhænger af, hvor hurtigt regningssystemet svarer, og det kan ikke ses i koden | `GetBillingOverview()` kalder regningssystemet én gang pr. kontrakt | Core/Billing/Services/BillingService.cs:30 | Mål det med en belastningstest mod testmiljøet
RISK | - | Forretningslogik hører til i en service | Ændringer på regningssiden tager længere tid og går lettere i stykker | `Index()` læser sessionen og filtrerer selv fakturaerne | Controllers/BillingController.cs:27 | Flyt filtreringen til `IBillingService` i Core/Billing/Services og injicér den
```

Never put a `|` inside a part. Write nothing else: no verdict, no introduction, no headings.
