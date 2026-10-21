---
name: vocabulary
description: Use when the question names an environment in everyday words (test hjemmeside, det der ligger på test, produktion, ude hos kunden) to know which branch it means: test is dev, production is main.
---

When our users are referencing our developer branch (dev), they'll usually say something like 'Test hjemmeside', 'det der ligger på test', 'det, der ikke ligger i produktionsmiljøet' and so on. All of those words will reference our staging environment / developer environment / testing environment.

And vice versa for the production environment, and thus, our main branch, we'll map the users wording such as 'produktion', 'produktionsmilj', 'ude hos kunden' and so on, to reference the source code that is placed in the main branch, and in the main ressources for the production subscription in Azure and so on.

