---
name: audience-developer
description: How to write the answer for a developer. Used to turn the code-review assessment into the answer when the person asking is a developer.
---

# Answer for a developer

The reader wrote or will fix the code. They want to know exactly where the code falls short and why, so they can fix it.
- **Answer only what was asked.** If the question is about one thing, answer only that.
- **Show only what is wrong or uncertain.** What works is covered by the count on the first line.
- Be technical and precise: name the file, line, method and the value or branch that is wrong. Code words are fine.
- Every point has a reference: requirement ids and `File.cs:line`, e.g. `(KRAV-REG-04, AC3 · BillingService.cs:48)`.
- Use the ids and file:line from the assessment exactly as they are.
- At most 20 lines in total.

You get the assessment from code-review: one line per requirement with its status (MET, NOT_MET, CANT_TELL) and RISK lines. The verdict line is already written above your text, so start with the first section below. Never repeat or change the verdict.

Use exactly this layout:

**Missing** (leave out if there is no NOT_MET): one line per NOT_MET, starting with ❌: what the requirement asks, what the code does instead, and where.

**Can't tell** (leave out if there is no CANT_TELL): one line per CANT_TELL, starting with ❓, and what would show it (a test, a log, another repo).

**Architecture** (leave out if there is no RISK): one line per RISK, starting with ⚠️, with file:line and what the team's way would be, e.g. "Business logic in the controller; move it to a service in Core/Billing/Services".

**Fix first** (leave out if nothing is missing): one line with the single change that closes the most requirements.

No introduction and no repeating the Danish requirement text.
