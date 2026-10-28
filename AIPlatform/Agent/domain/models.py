"""Domænemodeller for Agent-laget.

Hvad er en agent?
En LLM i en løkke. Den tænker, beslutter at gøre noget, ser resultatet,
og tænker igen, indtil opgaven er løst. Modellerne her beskriver hvert led
i den løkke.
"""

# Hvorfor kun standardbiblioteket?
# domain/ må ikke afhænge af noget udefra, præcis som i de andre lag.
from dataclasses import dataclass, field


# Hvorfor frozen=True?
# Det, der er sket i løkken, er sket. Ingen del af systemet må kunne
# ændre historikken bagefter, for så kan man ikke stole på loggen.


@dataclass(frozen=True)
class Action:
    """Én ting, agenten vil gøre: kalde et værktøj med bestemte argumenter."""

    # Hvorfor et id?
    # Agenten kan bede om flere ting på én gang. Id'et parrer hver handling
    # med sit resultat, så LLM'en ved, hvilket svar der hører til hvad.
    id: str
    tool: str
    arguments: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Decision:
    """Hvad hjernen besluttede i ét skridt."""

    # Hvorfor både tekst og handlinger?
    # LLM'en forklarer ofte, hvad den vil gøre, og gør det så.
    # Teksten gør løkken let at følge for et menneske.
    text: str

    # Hvorfor betyder en tom liste "færdig"?
    # Vil agenten ikke gøre mere, er teksten det endelige svar.
    # Det er det eneste stop-signal, løkken har brug for.
    actions: list[Action] = field(default_factory=list)

    @property
    def is_final(self) -> bool:
        return not self.actions


@dataclass(frozen=True)
class Observation:
    """Det, agenten ser, efter en handling er udført."""

    action_id: str
    content: str

    # Hvorfor et fejl-flag?
    # Gik værktøjet galt, skal agenten kunne se det og prøve noget andet,
    # i stedet for at hele løkken stopper.
    is_error: bool = False


@dataclass(frozen=True)
class Step:
    """Én handling og dens resultat. Det, man viser et menneske bagefter."""

    action: Action
    observation: Observation


@dataclass(frozen=True)
class AgentRun:
    """Hele kørslen: svaret og vejen derhen."""

    answer: str

    # Hvorfor gemme alle skridt?
    # Et svar fra en agent er kun troværdigt, hvis man kan se, hvad den gjorde.
    # Og når svaret er forkert, viser skridtene, hvor det gik galt.
    steps: list[Step]

    # Hvorfor et flag for, om den blev færdig?
    # En agent, der rammer grænsen for antal skridt, har ikke løst opgaven.
    # Det skal kunne ses tydeligt, ikke gemmes i en tekst.
    finished: bool = True


# Hvorfor en type for historikken?
# Historikken er skiftevis hjernens beslutninger og det, den så bagefter.
# Det er præcis den samtale, hjernen skal have med i næste skridt.
History = list[Decision | list[Observation]]


# Hvorfor en vurdering for sig?
# Hvem der spørger, må kun ændre, hvordan svaret skrives, ikke hvad der er fundet.
# Derfor laver agenten først en vurdering pr. krav, som deles af alle roller,
# og svaret til hver rolle skrives bagefter ud fra den samme vurdering.
@dataclass(frozen=True)
class Finding:
    """Ét krav og hvordan koden klarer det, eller én risiko i måden koden er bygget på."""

    # MET, NOT_MET, CANT_TELL eller RISK.
    status: str
    ids: str
    requirement: str
    code: str
    where: str

    # Hvorfor et rettelsesforslag i vurderingen?
    # Udvikleren vil vide, hvad der skal ændres. Står det i vurderingen, kan svaret ikke finde på et andet.
    # Svaret til produkt bruger det ikke.
    fix: str = ""

    # Hvorfor en forklaring uden kode?
    # Kommunikation skal kunne forstå, hvorfor et krav fejler, uden at læse koden.
    # Den skrives af agenten, der har læst koden, så svaret til produkt ikke skal gætte årsagen.
    why: str = ""


@dataclass(frozen=True)
class Assessment:
    """Agentens vurdering af koden. Den samme, uanset hvem der spørger."""

    findings: list[Finding]

    # Hvorfor et flag?
    # Har forretningen ikke skrevet krav ned, skal svaret sige det i stedet for at gætte.
    no_spec: bool = False

    # Sproget, dommen skrives på: "da" eller "en".
    language: str = "da"

    def count(self, status: str) -> int:
        return sum(1 for f in self.findings if f.status == status)

    @property
    def verdict(self) -> str:
        """Dommen regnes ud her og ikke af AI'en, så tallet altid passer med listen."""
        met = self.count("MET")
        total = met + self.count("NOT_MET") + self.count("CANT_TELL")
        words = VERDICT_WORDS.get(self.language, VERDICT_WORDS["da"])
        word = words[0] if met == total else words[2] if met == 0 else words[1]
        line = f"**{word}**. " + words[3].format(met=met, total=total)
        if self.no_spec:
            line += " " + words[4]
        return line


# Dommen på hvert sprog: løst, delvist løst, ikke løst, tallet og linjen, når der ingen krav er.
VERDICT_WORDS = {
    "da": ("Løst", "Delvist løst", "Ikke løst", "{met} af {total} krav er opfyldt.", "Forretningen har ikke skrevet krav ned for dette."),
    "en": ("Solved", "Partly solved", "Not solved", "{met} of {total} requirements are met.", "The business has not written requirements for this."),
}
