# Agent Anatomy POC – wiki

Wikien er samlingspunktet for tre måder at give en sprogmodel (LLM) viden, den ikke selv har lært under træningen:

| Mappe | Navn | Kort sagt |
|---|---|---|
| [RAG](RAG) | Retrieval-Augmented Generation | Slår op i vores dokumenter, hver gang der stilles et spørgsmål |
| [CAG](CAG) | Cache-Augmented Generation | Lægger al relevant viden i modellens kontekst på forhånd og genbruger den |
| [KAG](KAG) | Knowledge-Augmented Generation | Bygger en vidensgraf af fakta og relationer og ræsonnerer over den |

Hver mappe beskriver, hvad metoden er, hvad den gør, og hvornår den passer.

## Sådan opdateres wikien

Siderne ligger i mappen `wiki/` i repoet. Ændringer laves via almindelige pull requests, og når de merges til `main`, kopierer workflowet `Synk wiki` dem til GitHub-wikien. Ret derfor ikke siderne direkte i wikien, for de bliver overskrevet ved næste synk.
