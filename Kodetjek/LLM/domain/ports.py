"""Porte for LLM-laget.

En port er en kontrakt: den siger HVAD laget har brug for udefra, men ikke HVORDAN.
Implementeringerne (adapterne) ligger i infrastructure/providers/.

Hvorfor en port?
application/ skal kunne bede om et svar uden at vide, om det kommer fra Anthropic,
en anden udbyder eller en falsk testmodel. Den kender kun denne kontrakt.
"""

# Hvorfor Protocol frem for en abstrakt basisklasse (ABC)?
# Med Protocol behøver en adapter ikke arve fra noget. Har den de rigtige metoder,
# opfylder den kontrakten. Det holder infrastructure/ løst koblet til domain/
# og gør det let at lave en falsk udbyder på få linjer.
from typing import Iterator, Protocol

# Hvorfor importere fra models og intet andet?
# Porten taler kun i domænets eget sprog. Ser man "anthropic" i denne fil,
# er det et tegn på, at noget er havnet det forkerte sted.
from .models import Message, Response


class LLMProvider(Protocol):
    """Alt, der kan tage en samtale ind og give et svar tilbage."""

    # Hvorfor er system et separat argument og ikke en Message?
    # Systemprompten gælder hele samtalen og ændrer sig sjældent, mens beskederne
    # vokser for hvert skridt. Holdes de adskilt, kan application/ skifte den ene
    # uden at røre den anden.
    #
    # Hvorfor ingen model, temperatur eller API-nøgle i signaturen?
    # Det er konfiguration, ikke en del af spørgsmålet. Adapteren får dem, når den
    # bliver oprettet (fra config/), så kalderen ikke skal kende dem.
    def complete(self, system: str, messages: list[Message]) -> Response:
        """Returnerer hele svaret på én gang."""
        ...

    # Hvorfor en separat stream-metode?
    # Lange svar føles hurtigere, når teksten vises løbende. Det er en anden
    # måde at levere på (bidder af tekst i stedet for ét Response), så den får
    # sin egen metode frem for et flag, der ændrer returtypen.
    def stream(self, system: str, messages: list[Message]) -> Iterator[str]:
        """Returnerer svaret i bidder, efterhånden som det bliver skrevet."""
        ...


# Hvorfor ikke flere metoder, fx til værktøjer eller struktureret output?
# Porten skal kun indeholde det, laget har brug for i dag. Når agent-laget
# kræver værktøjskald, udvides kontrakten, og alle adaptere følger med.
# En lille port er nem at implementere og nem at skifte ud.