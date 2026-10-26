---
name: audience-product
description: How to write the answer for a product owner, communication or other business person. Used to turn the code-review assessment into the answer when the person asking is not a developer.
---

# Answer for a product or communication person

The reader looks at the product, not the code. They want to know if the customer gets what the business ordered, not how the code works.
- **Answer only what was asked.** If the question is about one thing (e.g. "Er datoformatet rigtigt?"), answer only that, in one or two lines.
- **Show only what is wrong.** Never list what works. What works is covered by the count on the first line.
- Write in Danish, in short sentences. Say what the customer or the business experiences and **why**, e.g. "Den nyeste regning vises ikke øverst, fordi regningerne vises i den rækkefølge, regningssystemet sender dem". Use the "why, in plain words" part of the assessment for the cause; never write a vague cause such as "en teknisk fejl". No code words such as null, session, parse, exception, controller, service, class or method names. Ignore what the assessment says about the code and the fix.
- If a recent change caused it, say who made it and what they changed, in plain words, as the assessment says.
- At most 3 ids on a line, in brackets at the end, e.g. `(KRAV-REG-04, AC3)`. Never a long list of ids: the table under the answer has every id. No file names, line numbers or code: the developer has their own answer for that.
- At most 8 lines in total.

You get the assessment from code-review: one line per requirement with its status (MET, NOT_MET, CANT_TELL) and RISK lines. The verdict line is already written above your text, so start with the first section below. Never repeat or change the verdict.

Use exactly this layout. Leave out a section that would have no lines, heading and all, and never write these instructions in the answer.

**Mangler**: the NOT_MET lines, the most important for the customer first, starting with ❌. At most 5 lines.
- When several requirements fail for the same reason, write the reason once, as the first line, and then one line per thing the customer can't do because of it, in plain words, e.g.:
  ❌ Siden med regninger kan ikke åbne, fordi Katjas ændring i går fjernede den del, der henter regningerne.
  ❌ Derfor kan kunden hverken se, sortere eller downloade sine regninger (AC1, AC3, AC5).
- If there are more than fit, end with "Og N krav mere, se tabellen." rather than adding ids.
- CANT_TELL lines are left out; they are only counted in the verdict.

**Risiko**: at most 2 lines, starting with ⚠️, for the most serious RISK lines, said as what can happen to the customer or the business, e.g. "Ændringer på regningssiden tager længere tid og går lettere i stykker".

Nothing else: no "what to do next", no introduction, no headings, no repeating the Danish requirement text.
