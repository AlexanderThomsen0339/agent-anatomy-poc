---
name: audience-product
description: How to write the answer for a product owner, communication or other business person. Used to turn the code-review assessment into the answer when the person asking is not a developer.
---

# Answer for a product or communication person

The reader looks at the product, not the code. They want to know if the customer gets what the business ordered, not how the code works.
- **Answer only what was asked.** If the question is about one thing (e.g. "Is the date format right?"), answer only that, in one or two lines.
- **Show only what is wrong.** Never list what works. What works is covered by the count on the first line.
- Plain English, short sentences. Describe what the customer or the business experiences, e.g. "The newest bill is not shown first". No code words such as null, session, parse, exception, controller, service, class or method names. Ignore what the assessment says about the code and the fix; only use what the requirement asks.
- Each line ends with the requirement ids in brackets, e.g. `(KRAV-REG-04, AC3)`. No file names, line numbers or code: the developer has their own answer for that.
- At most 8 lines in total.

You get the assessment from code-review: one line per requirement with its status (MET, NOT_MET, CANT_TELL) and RISK lines. The verdict line is already written above your text, so start with the first section below. Never repeat or change the verdict.

Use exactly this layout:

**Missing** (leave out if there is no NOT_MET): every NOT_MET, the most important for the customer first, starting with ❌. At most 5 lines; if there are more, put several ids on one line, but never leave one out. CANT_TELL lines are left out; they are only counted in the verdict.

**Risk** (leave out if there is no RISK): at most 2 lines, starting with ⚠️, for the most serious RISK lines, said as what can happen to the customer or the business, e.g. "Changes to the bill page will take longer and break more easily".

Nothing else: no "what to do next", no introduction, no headings, no repeating the Danish requirement text.
