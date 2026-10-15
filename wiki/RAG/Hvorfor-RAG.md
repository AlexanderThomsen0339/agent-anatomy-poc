# Hvorfor RAG?

**Vælg RAG, når I har mere viden, end der kan være i prompten, og den ændrer sig løbende.**

## Problemet, RAG løser

En sprogmodel ved intet om jeres virksomhed. Den har aldrig set jeres krav, manualer, sager eller kode. Spørger man alligevel, gætter den, og gættet lyder lige så overbevisende som et rigtigt svar.

Man kunne træne (fine-tune) modellen på sin egen viden, men det er dyrt, tager tid, skal gentages ved hver ændring, og modellen kan stadig ikke sige, *hvor* den har svaret fra. RAG giver i stedet modellen de rigtige papirer i hånden, hver gang den skal svare.

## Hvorfor man vælger RAG

| Grund | Hvad det betyder i praksis |
|---|---|
| **Skalerer til store mængder** | Tusindvis af dokumenter er ikke et problem. Kun de få relevante stykker sendes med. |
| **Altid opdateret** | Et nyt dokument i indekset er med i næste svar. Ingen genoptræning. |
| **Kilder kan vises** | Svaret kan henvise til præcis det stykke, det bygger på, så brugeren kan tjekke det. |
| **Færre gæt** | Modellen svarer ud fra fundne fakta i stedet for sin hukommelse. Finder søgningen intet, kan den sige det. |
| **Adgangsstyring** | Man kan filtrere i søgningen, så en bruger kun får svar fra dokumenter, vedkommende må se. |
| **Billig pr. spørgsmål** | Prompten er kort, fordi kun top-k stykker kommer med. |
| **Modenhed** | RAG er det mest udbredte mønster. Der findes masser af værktøjer, databaser og erfaring. |

## Hvorfor RAG i Kodetjek

Kodetjek skal vurdere, om en udviklers kode løser en opgave. Kravene ligger i regneark med user stories og testcases, som opdateres løbende, og løsningen skal kunne udvides med flere projekter. RAG lader agenten hente præcis de krav, der hører til opgaven, og henvise til det konkrete `US-…` eller `TC-…`, den vurderer ud fra.

## Hvornår RAG *ikke* er svaret

- Når al viden er lille nok til at ligge i prompten. Så er [CAG](Hvorfor-CAG) enklere og overser intet.
- Når spørgsmålene kræver at koble mange fakta i flere led. Så giver [KAG](Hvorfor-KAG) mere præcise svar.
