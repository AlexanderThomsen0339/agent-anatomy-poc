---
name: audience-product
description: How to write the answer for a product owner, communication or other business person. Use together with code-review when the person asking is not a developer.
---

# Answer for a product or communication person

The reader looks at the product, not the code. They want to know if the customer gets what the business ordered, not how the code works.
- **Answer only what was asked.** If the question is about one thing (e.g. "Is the date format right?"), answer only that, in one or two lines.
- **Show only what is wrong.** Never list what works. What works is covered by the count on the first line.
- Plain English, short sentences. Describe what the customer or the business experiences, e.g. "The newest bill is not shown first". No code words such as null, session, parse, exception, class or method names.
- Each line ends with a reference in brackets for the developer: ids and file:line, e.g. `(KRAV-REG-04, AC3 · BillingView.cshtml:12)`. Only the file name, not the whole path.
- At most 8 lines in total.

Use exactly this layout:

The verdict line from code-review.

**Missing** (leave out if nothing is missing): at most 5 lines, the most important for the customer first, starting with ❌. If a KRAV and an acceptance criterion say the same thing, write one line with both ids. Things the code can't show (speed, another system) are left out here and only counted.

**Risk** (leave out if there is none): at most 2 lines, starting with ⚠️, for the most serious ways the code differs from how the team builds, said as what can happen to the customer, e.g. "The page can crash for old contracts".

Nothing else: no "what to do next", no introduction, no headings, no repeating the Danish requirement text.
