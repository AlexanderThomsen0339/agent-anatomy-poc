# Hvorfor CAG?

**Vælg CAG, når al den viden, der skal bruges, kan ligge i modellens kontekst, og den sjældent ændrer sig.**

## Problemet, CAG løser

[RAG](RAG) står og falder med søgningen. Finder den ikke det rigtige stykke, fordi kravet er formuleret med andre ord, eller fordi svaret er spredt over flere steder, så får modellen aldrig chancen for at svare rigtigt. Og en RAG-løsning har mange dele, der skal bygges, tunes og vedligeholdes: indlæsning, opdeling, indeks og søgning.

Moderne modeller kan læse meget lange kontekster. Når vidensgrundlaget er lille nok, kan man derfor fjerne søgningen helt og give modellen det hele. Cachen sørger for, at det ikke bliver dyrt eller langsomt at gøre det ved hvert spørgsmål.

## Hvorfor man vælger CAG

| Grund | Hvad det betyder i praksis |
|---|---|
| **Ingen søgefejl** | Modellen ser altid alt, så intet krav overses, fordi det var formuleret anderledes. |
| **Helhedsbillede** | Modellen kan se sammenhænge på tværs af hele grundlaget, ikke kun i få udvalgte stykker. |
| **Enkel arkitektur** | Ingen indeks, ingen vektordatabase, ingen chunking. Kun en prompt og en cache. |
| **Hurtig at bygge** | God til POC'er og demoer, hvor man vil vise værdi hurtigt. |
| **Hurtige svar efter opstart** | Når cachen er bygget, skal modellen kun bearbejde det nye spørgsmål. |
| **Billigere end det lyder** | Cachede tokens koster typisk kun en brøkdel af almindelige input-tokens hos udbyderne. |

## Hvorfor CAG i AI Platform POC'en

De tre regneark med user stories og testcases er små. De kan sagtens ligge i konteksten på én gang. Med CAG ville agenten altid se alle acceptkriterier for en side, også dem som ordsøgningen ikke finder, og den ville bruge færre skridt, fordi den ikke skal søge. Det gør CAG til en oplagt sammenligning med RAG i demoen.

## Hvornår CAG *ikke* er svaret

- Når vidensgrundlaget vokser ud over kontekstvinduet, eller når modellen begynder at overse detaljer i en meget lang kontekst. Så er [RAG](Hvorfor-RAG) vejen.
- Når data ændrer sig hele tiden, så cachen hele tiden skal bygges igen.
- Når svarene kræver præcise opslag i flere led over strukturerede data. Så giver [KAG](Hvorfor-KAG) mere.
