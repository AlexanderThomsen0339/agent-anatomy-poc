# Kravspecifikation: Mit Aalborg Forsyning › Regninger
## Om dokumentet
EKSEMPEL til demoen. Kravene er skrevet af Claude ud fra user stories og er ikke godkendt af forretningen.
Hvert krav står som én blok adskilt af en tom linje. "Dækker" viser, hvilke user stories og testcases kravet hører til.

KRAV-REG-01: Kun kundens egne regninger
Krav: Oversigten må kun vise regninger for den kontrakt/adresse, kunden har valgt, og kun kontrakter, kunden har adgang til. Adgangen tjekkes på serveren, ikke kun i browseren.
Begrundelse: Persondata. En kunde må aldrig kunne se en anden kundes regning, heller ikke ved at ændre en URL.
Dækker: US-001, US-006, TC-028, TC-032
Ejer: Kommunikation og IT-sikkerhed

KRAV-REG-02: Felter i oversigten
Krav: Hver regning viser fakturanummer, fakturadato, forfaldsdato, beløb og betalingsstatus. Nyeste regning står øverst.
Begrundelse: Det er de oplysninger, kundeservice oftest bliver spurgt om.
Dækker: US-001, TC-001, TC-002, TC-003
Ejer: Kommunikation

KRAV-REG-03: Beløb i danske kroner
Krav: Beløb vises inkl. moms i danske kroner med to decimaler, komma som decimaltegn og punktum som tusindtalsseparator, fx 1.234,50 kr.
Begrundelse: Kunden skal kunne genkende beløbet fra den trykte faktura og fra netbanken.
Dækker: US-001, TC-004
Ejer: Kommunikation

KRAV-REG-04: Datoformat
Krav: Fakturadato og forfaldsdato vises som dd-mm-åååå.
Begrundelse: Samme format som på fakturaen og i resten af Mit Aalborg Forsyning.
Dækker: US-001, TC-004
Ejer: Kommunikation

KRAV-REG-05: Betalingsstatus med ord
Krav: Status skrives som "Betalt" eller "Ikke betalt". En ubetalt regning, hvis forfaldsdato er overskredet, markeres tydeligt som "Forfalden". Status må ikke kun vises med farve.
Begrundelse: Kunden skal hurtigt se udeståender, og farve alene er ikke tilgængeligt for alle (WCAG).
Dækker: US-004, TC-018, TC-019, TC-020
Ejer: Kommunikation

KRAV-REG-06: Tekst når der ingen regninger er
Krav: Når kontrakten endnu ikke har regninger, vises teksten "Der er endnu ikke oprettet regninger på denne kontrakt." Når regningerne ikke længere er tilgængelige, vises en anden tekst, der forklarer det og henviser til kundeservice.
Begrundelse: To forskellige situationer giver to forskellige spørgsmål til kundeservice, så teksterne må ikke være ens.
Dækker: US-002, US-003, TC-016, TC-017
Ejer: Kommunikation

KRAV-REG-07: Download af faktura
Krav: Fakturaen downloades som PDF med filnavnet invoice_<fakturanummer>.pdf. Serveren tjekker, at fakturaen tilhører den indloggede kunde, før filen sendes.
Begrundelse: Filnavnet skal kunne genkendes i kundens overførsler, og adgangen skal beskyttes som i KRAV-REG-01.
Dækker: US-005, TC-021, TC-022, TC-023, TC-024
Ejer: Kommunikation og IT-sikkerhed

KRAV-REG-08: Fejl fra faktureringssystemet
Krav: Svarer faktureringssystemet ikke, vises en venlig fejlbesked på dansk i stedet for en tom liste eller en teknisk fejl. Fejlen logges.
Begrundelse: En tom liste får kunden til at tro, at der ingen regninger er.
Dækker: US-007, TC-034
Ejer: Kommunikation og IT-drift
