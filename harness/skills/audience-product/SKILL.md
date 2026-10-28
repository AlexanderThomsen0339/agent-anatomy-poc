---
name: audience-product
description: How to write the answer for a product owner, communication or other business person. Used to turn the code-review assessment into the answer when the person asking is not a developer. Formats evaluation's finished Node 4 result; it never re-evaluates it.
---

# Answer for a product or communication person

This runs strictly after `evaluation`'s Node 4 ("Evaluate User Story & Test Case Conflicts") has already produced its result via `code-review`. This skill only rewrites that finished result for a non-technical reader: it is a presentation gate, not an evaluation gate, so it must never add, remove or re-score a finding — only change how each one reads.

The reader looks at the product, not the code. They want to know, as if they asked a colleague, whether the customer gets what the business ordered and whether the test can be passed.

## How it should sound
- **Talk like a helpful colleague**, in Danish, in whole sentences. A short paragraph, not a list: no headings, no bullet points, no ❌ or ⚠️.
- **Answer the question in the first sentence.** If they ask which module fails, the first sentence names it, e.g. "Det er regningerne, der fejler." If they ask whether it works, say yes, partly or no.
- Then say what the customer experiences and **why**, using the "why, in plain words" part of the assessment. Never a vague cause such as "en teknisk fejl".
- If a recent change caused it, say who made it and what they changed, in plain words, as the assessment says.
- End with what it means for the test, e.g. "Testen af regningsoversigten kan ikke gennemføres, før IT har rettet det."
- Mention a RISK line only if it is serious for the customer or the business, in one sentence.
- **Answer only what was asked.** A small question gets one or two sentences.
- At most 5 sentences.

## What to leave out
- No requirement ids, file names, line numbers or code: the table under the answer has every id, and the developer has their own answer.
- No code words such as null, session, parse, exception, controller, service, manager, class or method names.
- Never list what works, and never list every requirement that fails. When many fail for the same reason, say the reason once and sum up what the customer can't do, e.g. "kunden kan hverken se adresser, beløb eller datoer".
- CANT_TELL lines are left out; they are only counted in the verdict.
- No filler such as "Godt spørgsmål" or "Jeg håber, det hjælper", and no repeating the verdict.

You get the assessment from code-review: one line per requirement with its status (MET, NOT_MET, CANT_TELL) and RISK lines. The verdict line is already written above your text. Never repeat or change it, and never write these instructions in the answer.

For example, to "Hvad for et modul er det, der fejler?":

Det er regningerne. Lige nu kan kunderne slet ikke se deres regninger på selvbetjeningen, så hverken adresser, beløb eller datoer bliver vist. Det skyldes en ændring, Diaco Nori har lavet i forbindelsen til regningssystemet, som gør, at svaret med fakturaerne bliver slettet, før siden får det. Testen af regningsoversigten kan derfor ikke gennemføres, før IT har rettet det.
