---
name: audience-developer
description: How to write the answer for a developer. Use together with code-review when the person asking is a developer.
---

# Answer for a developer

The reader wrote or will fix the code. They want to know exactly where the code falls short and why, so they can fix it.
- **Answer only what was asked.** If the question is about one thing, answer only that.
- **Show only what is wrong or uncertain.** What works is covered by the count on the first line.
- Be technical and precise: name the file, line, method and the value or branch that is wrong. Code words are fine.
- Every point has a reference: requirement ids and `File.cs:line`, e.g. `(KRAV-REG-04, AC3 · BillingService.cs:48)`.
- Never invent a file:line. Only use lines you have read with `read_code_file`.
- At most 20 lines in total.

Use exactly this layout:

The verdict line from code-review.

**Missing** (leave out if nothing is missing): one line per requirement that is not met, starting with ❌: what the requirement asks, what the code does instead, and where.

**Can't tell** (leave out if there is none): requirements the code can't show (speed, another system, data), starting with ❓, and what would show it (a test, a log, another repo).

**Architecture** (leave out if there is none): at most 5 lines, starting with ⚠️, for where the code differs from how the team builds (the architecture skill), with file:line and what the team's way would be, e.g. "Business logic in the controller; move it to a service in Core/Billing/Services".

**Fix first** (leave out if nothing is missing): one line with the single change that closes the most requirements.

No introduction and no repeating the Danish requirement text.
