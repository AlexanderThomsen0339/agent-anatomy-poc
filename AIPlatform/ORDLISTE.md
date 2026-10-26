# AI Platform POC – ordliste

Ordene, man ser på siden og hører under demoen, forklaret kort. Siden er på engelsk, mens svarene og vurderingen er på dansk. Ordene står, som de står på skærmen. Se [DEMO.md](DEMO.md) for hele forløbet.

---

## 1. Dommen og svaret

| Ord | Betyder |
|---|---|
| **Dommen** (*verdict*) | Første linje i svaret, fx **"Delvist løst. 4 af 5 krav er opfyldt."** Den tælles af koden ud fra vurderingens linjer, ikke af AI'en, så tallet altid passer. (`Assessment.verdict` i `Agent/domain/models.py`) |
| **Løst** | Alle krav er opfyldt (MET). |
| **Delvist løst** | Nogle krav er opfyldt, men ikke alle. |
| **Ikke løst** | Ingen krav er opfyldt. |
| **"X af Y krav er opfyldt"** | X = antal MET. Y = MET + NOT_MET + CANT_TELL. RISK tæller ikke med. |
| **Intet mangler.** | Står under dommen, når alt er MET og der ingen risici er. Så skrives der ikke mere. |
| **"Forretningen har ikke skrevet krav ned for dette."** | Tilføjes dommen, når kravspec ikke har krav til den user story (agenten skrev `NO_SPEC`). Agenten må ikke finde på krav. |
| **Not finished** | Overskrift, når agenten ikke nåede frem til en vurdering: enten ramte den **step-grænsen** (svaret er så "I did not finish within the step limit."), eller den skrev ikke en vurdering, koden kunne læse. Siden viser så det, agenten nåede at skrive. Det er ikke en dom. |
| **The agent asks** | Agenten ved ikke, hvilken user story der menes, og spørger i stedet for at gætte (den skrev `QUESTION:`). Man svarer i feltet under, og svaret sendes med samtalen. Det er ikke en dom. |
| **Earlier in this conversation** | De tidligere spørgsmål og svar i samme samtale (højst 3). Siden sender dem med næste spørgsmål, så agenten kan forstå fx "Den om billing". |
| **Answer for …** | Overskriften over selve svaret, fx *Answer for IT*. Siger, hvilken rolle svaret er skrevet til. |
| **Error** | Noget gik galt (fx Gemini svarede ikke). Fejlen vises på siden, så demoen ikke bare hænger. |

## 2. Vurderingen (Assessment)

| Ord | Betyder |
|---|---|
| **Vurdering** (*Assessment*) | Agentens resultat: én linje pr. krav med status, kravet, koden og hvor i koden (fil:linje). Den er ens for alle roller; kun svaret skrives forskelligt. Vises i den foldede boks **Assessment**. |
| **Fund** (*Finding*) | Én linje i vurderingen. |
| ✅ **MET** | Koden gør det, kravet siger. Tæller som opfyldt. |
| ❌ **NOT_MET** | Koden gør det anderledes eller slet ikke. Tæller som ikke opfyldt. |
| ❓ **CANT_TELL** | Kan ikke ses i koden (fx hastighed eller noget, der kræver en rigtig server). Tæller som ikke opfyldt, fordi det ikke er bevist. |
| ⚠️ **RISK** | Koden virker, men afviger fra holdets måde at kode på (arkitektur-skillen). Tæller ikke i dommen, vises som risiko. |
| **Rettelse** (*fix*) | Forslag til, hvad der skal ændres. Står i vurderingen, så svaret til IT ikke kan finde på et andet. Produkt får det ikke at se. |
| **Modstridende linjer** | Hvis den lille model skriver samme krav både som MET og NOT_MET med den samme kode, fjernes MET-linjen, og NOT_MET vinder (`drop_contradictions`). |

## 3. Krav og kilder

| Ord | Betyder |
|---|---|
| **User story** (US-xxx) | Opgaven, fx *US-005 Download faktura*. Id'et bruges til at finde krav, testcases og en PR. |
| **Acceptkriterie** (AC) | En betingelse i user storyen, der skal være opfyldt, før den er færdig. |
| **Testcase** | Det, test-holdet tjekker. Ligger i Excel-filerne (`RAG/data/*.xlsx`) og findes med `search_requirements`. |
| **Kravspec** | Forretningens krav: det, forretningen har bestilt. Hvert krav har et id som `KRAV-REG-03` og en linje *Dækker:* med de user stories, det hører til. Ligger i `RAG/data/kravspec/` og findes med `search_specification`. |
| **Krav** (*requirement*) | Fællesord for det, koden tjekkes mod: acceptkriterier, testcases og kravspec. |
| **Not documented** | Svar fra `search_specification`, når der ingen krav er. Agenten skal sige det i stedet for at gætte. |
| **Sources** | Foldet boks over svaret: præcis hvilke dokumenter, branch, commit og filer svaret bygger på. |

## 4. Hvilken kode bliver tjekket (branch-valg)

| Ord | Betyder |
|---|---|
| **Branch-valg** | Før hvert kodetjek vælger koden (ikke AI'en), hvilken branch der læses. (`CheckoutService`) |
| **dev** | Standard-branchen. Tjekkes, når ingen åben PR passer til spørgsmålet. (`CODE_BRANCH` i `settings.py`) |
| **PR** (*pull request*) | En udviklers ændring, der venter på at komme ind i `dev`. Står user story-id'et (fx US-005) i PR'ens titel eller branch-navn, tjekkes PR'ens branch i stedet for `dev`. Er der flere, tages den nyeste. |
| **Feature-branch** | Udviklerens egen branch, fx `feature/US-005-invoice-filename`. IT's regel: feature-branch → PR ind i `dev` → `dev` ind i `main`. |
| **Commit** | Den præcise version af koden, der blev tjekket (fx `48411a3`). Står på siden og i *Sources*. |
| 🔀 **Checking pull request …** | Siden fortæller, at en PR blev fundet og tjekkes. |
| 🔀 **No open pull request matches the question, so checking dev** | Ingen PR passede, så `dev` tjekkes. |
| 🔴 **Could not look for pull requests / Could not fetch the code** | Azure DevOps svarede ikke (fx forkert nøgle). Så bruges `dev` eller den sidste kopi af koden. |
| **POC'ens kopi af repoet** | POC'en kloner Azure-repoet og henter det nyeste før hvert tjek, så en udvikler kan pushe og straks spørge. Kun ét kodetjek kører ad gangen, fordi der kun er én kopi. |

## 5. Agenten

| Ord | Betyder |
|---|---|
| **Agent** | En AI-model (Gemini) i en løkke: **tænk → handl → se**, indtil den har nok til et svar. (`AgentService`) |
| **Skridt** (*step*) | Én runde i løkken: et værktøj kaldes, og resultatet lægges i historikken. Vises live under *What I am doing*, fx "📄 Reading billing_routes.py". |
| **Step-grænse** | Højst 20 skridt (`MAX_STEPS`). Beskytter mod en agent, der kører i ring. Rammes den, står der **Not finished**. |
| **Hjernen** (*brain*) | Den AI-model, der træffer beslutningerne. Her Google Gemini (`GeminiBrain`). Kan skiftes ud med en ny fil. |
| **AnswerWriter** | Skriver vurderingen om til et svar til rollen ("✍️ Writing the answer"). Får ingen værktøjer, så den kan ikke ændre vurderingen. |
| ♻️ **Genbrugt tjek** | "The code and requirements have not changed, so the earlier check is used". Samme spørgsmål om uændret kode genbruger den gemte vurdering, så svaret er det samme og kommer med det samme. Ændres en fil, eller tjekkes en anden branch, laves et nyt tjek. Gemmes kun i hukommelsen og forsvinder ved genstart. |
| **Fingeraftryk** | Det, der afgør, om koden er uændret: indholdet af de filer og krav, agenten læste sidst. |

## 6. Roller og hold

| Ord | Betyder |
|---|---|
| **Rolle** | Den, der spørger, valgt i dropdownen: **Product / communication**, **IT** eller **Vedligehold**. Rollen bestemmer, hvilke værktøjer agenten får, og hvordan svaret skrives. AI'en vælger det ikke selv. |
| **Hold** (*team*) | Et IT-hold: **web** (bygger Mit Aalborg Forsyning) eller **ot** (anlæggets styresystemer). (`TEAMS`) |
| **Rolle → hold** | Product ser web, IT ser web og OT, Vedligehold ser kun OT. (`ROLE_TEAMS`) |
| **Kodetjek** | Det, roller med web får: tjek koden mod krav, kravspec og holdets måde at kode på. |
| **OT-opslag** | Det, roller med OT får: søg i OT-holdets signalliste og PDF'er og svar direkte, uden dom. |

## 7. Lagene og byggestenene

| Ord | Betyder |
|---|---|
| **Lag** | Løsningen har fire: **Agent** (hjernen), **MCP** (hænderne), **RAG** (hukommelsen), **Skills** (arbejdsinstrukserne). |
| **MCP-værktøj** (*tool*) | Noget, agenten kan kalde: `search_requirements`, `search_specification`, `list_code_files`, `read_code_file`, `search_ot_documents` og `load_skill` (kun når der er skills, agenten selv kan vælge). Agenten kan kun læse, aldrig ændre koden. |
| **RAG** | *Retrieval-Augmented Generation*: AI'en slår op i dokumenter, før den svarer, i stedet for at svare ud fra hukommelsen. |
| **Afsnit** (*chunk*) | Et stykke af et dokument, som søgningen finder: én testcase, ét krav, én række i signallisten eller én side i en PDF. |
| **Nøgleordssøgning** (`KeywordIndex`) | Søgningen i POC'en: et afsnit får ét point pr. ord, det deler med søgningen. Finder ord, ikke betydning, så spørg med id og titel. |
| **Ordret søgning** (*exact*) | OT-søgning, der kun finder dokumenter med præcis de ord, fx "BERAN backup". |
| **Skill** | En arbejdsinstruks i en `SKILL.md`. Agenten ser kun navn og beskrivelse og henter teksten, når den skal bruge den. |
| `code-review` | Skill: hvordan koden vurderes (slå krav op, læs koden, én linje pr. krav, aldrig gætte). |
| `architecture-web` | Skill: hvordan web-holdet koder (routes → services → managers, interfaces, dependency injection). Giver RISK-linjer. |
| `audience-product` / `audience-it` | Skills: hvordan svaret skrives til rollen. Produkt: højst 8 linjer, almindeligt sprog, kun det, der mangler. IT: fil:linje, kode, rettelse og hvad der skal rettes først. |
| **Port / adapter** | En port er en fast grænseflade (fx `AgentBrain`), en adapter er det, der opfylder den (fx `GeminiBrain`). Gør det muligt at skifte Gemini, Azure eller søgningen ud uden at røre resten. |
| **POC** | *Proof of concept*: en lille, fungerende prøve, ikke et færdigt produkt. |
