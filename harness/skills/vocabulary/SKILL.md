---
name: vocabulary
description: Maps how our users refer to the dev/staging and production environments and branches, so their wording can be translated to the right branch and Azure resources. Feeds the Target Environment Branch step in evaluation's State Definition.
---

This skill is a quality gate for the `evaluation` skill's **State Definition** step: before evaluation can decide whether to pull `dev` or `main`, the user's own wording has to be resolved to one of those two branches. Resolve the wording below first, then hand the resolved branch to evaluation.

When our users are referencing our developer branch (dev), they'll usually say something like 'Test hjemmeside', 'det der ligger på test', 'det, der ikke ligger i produktionsmiljøet' and so on. All of those words will reference our staging environment / developer environment / testing environment.

And vice versa for the production environment, and thus, our main branch, we'll map the users wording such as 'produktion', 'produktionsmilj', 'ude hos kunden' and so on, to reference the source code that is placed in the main branch, and in the main ressources for the production subscription in Azure and so on.

Per evaluation's constraint, a resolved branch is always `dev` or `main`: never resolve wording to a local or feature branch, even if the user names one explicitly.

