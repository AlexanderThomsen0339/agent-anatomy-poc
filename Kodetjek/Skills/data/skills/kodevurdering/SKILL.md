---
name: kodevurdering
description: Brug når en udvikler spørger, om koden løser en user story, opfylder acceptkriterier eller består testcases.
---

# Sådan vurderer vi kode

Find først kravene og koden. Gæt aldrig:
- Slå user storyen og dens acceptkriterier op med `search_requirements`. Søg med ord fra opgaven, og med id'et (fx US-002), hvis udvikleren nævner det.
- Find de relevante filer med `list_code_files`, og læs dem med `read_code_file`. Læs kun de filer, der hører til opgaven.

Skriv så vurderingen:
- Start med én linje med konklusionen: **Løst**, **Delvist løst** eller **Ikke løst**.
- Gå derefter acceptkriterierne igennem ét ad gangen:
  - ✅ Opfyldt, ❌ Ikke opfyldt eller ❓ Kan ikke afgøres ud fra koden.
  - Én sætning om hvorfor, med henvisning til fil:linje.
- Nævn de testcases (TC-id), der hører til, og om koden ser ud til at kunne bestå dem.
- Slut med højst tre konkrete forslag til, hvad udvikleren skal rette.
- Skriv på dansk. Kriterier, der handler om noget, koden ikke kan vise (fx performance eller synkronisering til et andet system), markeres ❓, ikke ❌.
