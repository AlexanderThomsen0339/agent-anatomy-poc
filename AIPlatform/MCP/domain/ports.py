"""Porte for MCP-laget.

Hvorfor kun én port?
Det eneste, laget har brug for udefra, er værktøjer. Alt andet (at holde styr
på dem, kalde det rigtige og fange fejl) er lagets eget arbejde og ligger i
application/.
"""

# Hvorfor Protocol?
# Samme grund som i de andre lag: et værktøj skal bare have de rigtige
# egenskaber, det behøver ikke arve fra noget.
from typing import Protocol

from .models import ToolSpec


# Hvorfor er Tool en port?
# Det er stikkets form. Alle apparater, der har dette stik, kan sættes i:
# et ur, en lommeregner, en søgning i dokumenter, senere en kalender eller
# et API. Resten af laget ser aldrig, hvad der er inde i apparatet.
class Tool(Protocol):

    # Hvorfor er spec en egenskab og ikke en metode?
    # Mærkatet ændrer sig ikke, mens apparatet kører. Det læses, før man
    # trykker på knappen.
    spec: ToolSpec

    # Hvorfor tager run() en dict og ikke rigtige parametre?
    # Argumenterne kommer fra en LLM eller en MCP-klient som JSON.
    # Alle værktøjer får dem i samme form, så de kan kaldes ens.
    def run(self, arguments: dict) -> str:
        """Udfører værktøjet og returnerer resultatet som tekst."""
        ...
