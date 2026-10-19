# Hvorfor KAG?

**Vælg KAG, når spørgsmålene handler om sammenhænge mellem mange ting, og svarene skal være præcise og kunne forklares.**

## Problemet, KAG løser

[RAG](RAG) og [CAG](CAG) arbejder begge med tekst. Det er fint til "hvad står der om X?", men mange vigtige spørgsmål i en virksomhed handler om *relationer*:

- Hvilke krav er ikke dækket af en testcase?
- Hvilke testcases skal køres igen, hvis vi ændrer denne komponent?
- Hvilke kunder er berørt af en fejl i denne funktion?

Svaret står ikke i ét stykke tekst. Det kræver at følge flere led: komponent → user story → acceptkriterie → testcase → resultat. RAG finder måske nogle af stykkerne, men overser let et led, og modellen må gætte resten. KAG gemmer relationerne direkte, så de kan følges sikkert.

## Hvorfor man vælger KAG

| Grund | Hvad det betyder i praksis |
|---|---|
| **Spørgsmål i flere led** | Agenten følger relationerne trin for trin i stedet for at håbe på, at søgningen rammer alle stykker. |
| **Præcision** | Fakta som ID'er, resultater og datoer ligger som data, ikke som tekst, der skal fortolkes. |
| **Forklarlighed** | Svaret kan vise stien gennem grafen. Det er vigtigt, hvor man skal kunne stå på mål for svaret. |
| **Fuldstændighed** | "Alle krav uden testcase" kan beregnes ud fra grafen, ikke bare anslås ud fra de top-k stykker. |
| **Konsistens** | Den samme ting har ét navn og én node, også når den omtales forskelligt i forskellige dokumenter. |
| **Genbrug** | Grafen er et aktiv i sig selv og kan også bruges til rapporter, sporbarhed og analyser uden en LLM. |

## Hvorfor KAG i AI Platform POC'en

Testdataene i AI Platform POC'en er allerede næsten en graf: sider har user stories, user stories har acceptkriterier, testcases tester user stories og har resultater pr. testdato. Med KAG kunne Kodetjek gå fra "løser koden opgaven?" til spørgsmål om sporbarhed, for eksempel hvilke krav på en side der mangler en testcase, der er bestået. Det er den slags svar, der er svære at give med ordsøgning alene.

## Hvornår KAG *ikke* er svaret

- Når spørgsmålene er simple opslag. Så er [RAG](Hvorfor-RAG) eller [CAG](Hvorfor-CAG) billigere og hurtigere at bygge.
- Når data er fritekst uden tydelige ting og relationer. Så skal grafen udtrækkes med en LLM, og fejl i udtrækket giver fejl i svarene.
- Når der ikke er tid eller folk til at modellere domænet og vedligeholde grafen.
