"""Domænemodeller for RAG-laget.

Hvorfor egne modeller?
Resten af laget skal kunne tale om "et dokument", "et afsnit" og "et søgeresultat"
uden at vide, om dokumenterne kommer fra filer, SharePoint eller en database,
eller om søgningen sker på ord eller på betydning.
"""

# Hvorfor kun standardbiblioteket?
# domain/ må ikke afhænge af noget udefra.
from dataclasses import dataclass


# Hvorfor frozen=True?
# Et dokument eller et afsnit ændrer sig ikke, mens vi arbejder med det.
# Uforanderlige objekter kan trygt deles mellem indlæsning, indeks og svar.
@dataclass(frozen=True)
class Document:
    # Hvorfor gemme kilden?
    # Et svar er kun troværdigt, hvis man kan se, hvor det kommer fra.
    # Kilden følger med hele vejen fra filen til svaret.
    source: str
    text: str


@dataclass(frozen=True)
class Chunk:
    """Et afsnit af et dokument. Det er afsnit, vi søger i, ikke hele dokumenter."""

    # Hvorfor dele dokumenter op?
    # Et helt dokument er for stort at sende med hvert spørgsmål og indeholder
    # meget, der ikke er relevant. Små afsnit giver præcise opslag og billigere kald.
    source: str
    text: str

    # Hvorfor position?
    # Så man kan se, hvor i dokumentet afsnittet stod, og senere hente naboafsnit.
    position: int


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk

    # Hvorfor en score?
    # Søgningen skal kunne sige, hvor godt et afsnit passer, så de bedste
    # kommer først, og helt irrelevante kan sorteres fra.
    score: float

