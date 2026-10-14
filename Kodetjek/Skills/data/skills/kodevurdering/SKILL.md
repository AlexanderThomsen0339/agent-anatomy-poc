---
name: kodevurdering
description: Brug når en udvikler spørger, om koden løser en user story, opfylder acceptkriterier eller består testcases.
---

# Sådan vurderer vi kode

Find først kravene og koden. Gæt aldrig:
- Slå user storyen og dens acceptkriterier op med `search_requirements`. Søg med ord fra opgaven, og med id'et (fx US-002), hvis udvikleren nævner det.
- Find de relevante filer med `list_code_files`, og læs dem med `read_code_file`. Læs kun de filer, der hører til opgaven.

Skriv så vurderingen. Den læses af en travl udvikler, så hold den kort, højst 15 linjer:
- Første linje er konklusionen: **Løst**, **Delvist løst** eller **Ikke løst**, og en kort sætning om hvorfor.
  - **Løst** kun hvis alle kriterier er ✅. Er der ét ❌, er det **Ikke løst** eller **Delvist løst**. Er der kun ✅ og ❓, er det **Delvist løst**.
- Derefter ét punkt pr. acceptkriterie, på én linje:
  - ✅ Opfyldt, ❌ Ikke opfyldt eller ❓ Kan ikke afgøres ud fra koden.
  - Kriteriet med få ord, og henvisning til fil:linje. Kun filnavnet, ikke hele stien.
- Slut med højst tre forslag til rettelser, én linje hver. Er alt ✅, så skriv ingen forslag.
- Ingen overskrifter, ingen gentagelse af kravteksten og ingen indledning.
- Skriv på dansk. Kriterier, der handler om noget, koden ikke kan vise (fx performance eller synkronisering til et andet system), markeres ❓, ikke ❌.
