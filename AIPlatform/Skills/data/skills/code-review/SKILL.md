---
name: code-review
description: Checks whether the code meets a user story's acceptance criteria and the business requirements, and writes one status line per requirement. Use when someone asks whether the code solves a user story, passes its test cases or meets the requirements.
---

# How we review code

A **requirement** is either an acceptance criterion or a business requirement. The code is checked against both:
- **Acceptance criteria** (AC1, AC2 ...): the user story's Acceptkriterier, from `search_requirements`. They say what the test team checks.
- **Business requirements** (ids like KRAV-REG-03): the kravspec, from `search_specification`. They say what the business ordered.

## 1. Find the requirements and the code

Never guess. Do these steps in order:
1. Look up the user story with `search_requirements`, using its id (e.g. US-002) and Danish words from its title. Use the user story whose id and title match the question.
2. Look up the business requirements with `search_specification`, using the user story id and Danish words. Keep every business requirement whose "Dækker" line names this user story and whose file covers the same area.
3. Look at the newest commits: they are in the question, or use `list_recent_changes`. A change in a file the task depends on (e.g. a manager the service calls) can break it, even if the file's name doesn't match the task.
4. Find the files with `list_code_files`, and read them with `read_code_file`: the controller, view (`.cshtml`), service, model and manager that belong to the task, and the files changed in the newest commits.

Only judge against the requirements you found and the team's way of coding below. Never invent a requirement or a file:line.

If you cannot tell which user story the question is about (the question names none, the newest commits don't show it, and several user stories could fit), don't guess and don't assess. Write only one line: `QUESTION:` followed by a short question in Danish that lists the user stories that could fit, with id and title, e.g. `QUESTION: Mener du US-004 Vis betalingsstatus eller US-005 Download faktura?`. The user's answer comes back with the earlier conversation.

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
