---
name: audience-it
description: How to write the answer for IT. Used to turn the code-review assessment into the answer when the person asking is from IT (developers).
---

# Answer for IT

The reader wrote or will fix the code. They want to know exactly where the code falls short and why, so they can fix it.
- **Answer only what was asked.** If the question is about one thing, answer only that.
- **Show only what is wrong or uncertain.** What works is covered by the count on the first line.
- Write in Danish. Code, method names and values stay as they are in the code.
- Be technical and precise. Use the method, expression and value from the assessment, in backticks. Code words are fine, and plain-language explanations of the requirement are not needed.
- Every point starts with the place and the ids, so the developer can jump straight to it.
- When one cause breaks several requirements, write it as one point with every id it breaks, and name the commit that caused it if the assessment does.
- Use the ids and file:line from the assessment exactly as they are.
- At most 20 lines in total.

You get the assessment from code-review: one line per requirement with its status (MET, NOT_MET, CANT_TELL) and RISK lines. The verdict line is already written above your text, so start with the first section below. Never repeat or change the verdict.

Use exactly this layout. Leave out a section that would have no lines, heading and all, and never write these instructions in the answer.

**Mangler**: one line per NOT_MET, in this form:
`❌ file.cs:line (ids): what the code does, and why it breaks the requirement. Ret: how to fix.`
e.g. ❌ `Views/Partials/BillingTableBody.cshtml:8` (KRAV-REG-04, AC7): `@row.InvoiceDate` udskrives i ISO-format. Ret: `date.ToString("dd-MM-yyyy", CultureInfo.InvariantCulture)` i mappingen.

**Kan ikke afgøres**: one line per CANT_TELL, starting with ❓ and `file.cs:line` (ids), and what would show it.

**Arkitektur**: one line per RISK, starting with ⚠️ and `file.cs:line`, what the code does and the fix, e.g. ⚠️ `Controllers/BillingController.cs:27`: `Index()` filtrerer selv fakturaerne. Ret: flyt det til `IBillingService` og injicér den.

**Ret først**: one line naming the file to change first, because it closes the most requirements.

Nothing else: no introduction, no summary sentence, no repeating the Danish requirement text. Your first line is the **Mangler** heading (or the first section that is not left out).
