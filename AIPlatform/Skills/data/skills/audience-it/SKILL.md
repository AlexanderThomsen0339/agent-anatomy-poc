---
name: audience-it
description: How to write the answer for IT. Used to turn the code-review assessment into the answer when the person asking is from IT (developers).
---

# Answer for IT

The reader wrote or will fix the code. They want to know exactly where the code falls short and why, so they can fix it.
- **Answer only what was asked.** If the question is about one thing, answer only that.
- **Show only what is wrong or uncertain.** What works is covered by the count on the first line.
- Be technical and precise. Use the method, expression and value from the assessment, in backticks. Code words are fine, and plain-language explanations of the requirement are not needed.
- Every point starts with the place and the ids, so the developer can jump straight to it.
- Use the ids and file:line from the assessment exactly as they are.
- At most 20 lines in total.

You get the assessment from code-review: one line per requirement with its status (MET, NOT_MET, CANT_TELL) and RISK lines. The verdict line is already written above your text, so start with the first section below. Never repeat or change the verdict.

Use exactly this layout:

**Missing** (leave out if there is no NOT_MET): one line per NOT_MET, in this form:
`❌ File.cs:line (ids): what the code does. Fix: how to fix.`
e.g. ❌ `BillingTableBody.cshtml:8` (KRAV-REG-04, AC3): `@bill.InvoiceDate` uses the default culture. Fix: `bill.InvoiceDate.ToString("dd-MM-yyyy")`.

**Can't tell** (leave out if there is no CANT_TELL): one line per CANT_TELL, starting with ❓ and `File.cs:line` (ids), and what would show it.

**Architecture** (leave out if there is no RISK): one line per RISK, starting with ⚠️ and `File.cs:line`, what the code does and the fix, e.g. ⚠️ `RegningsoversigtSurfaceController.cs:27`: `Index()` filters bills itself. Fix: move it to `IBillingService` and inject it.

**Fix first** (leave out if there is no NOT_MET): one line naming the file to change first, because it closes the most requirements.

Nothing else: no introduction, no summary sentence, no repeating the Danish requirement text. Your first line is the **Missing** heading (or the first section that is not left out).
