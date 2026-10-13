"""Domænemodeller for LLM-laget.

Hvorfor egne modeller i stedet for SDK'ens objekter?
Resten af systemet skal kunne tale om "en besked" og "et svar" uden at vide,
hvilken udbyder der ligger bagved. Skifter vi udbyder, ændres kun den adapter,
der oversætter til og fra disse modeller, ikke koden der bruger dem.
"""

from dataclasses import dataclass
from typing import Literal

Role = Literal["user", "assistant"]

@dataclass(frozen=True)
class Message:
    role: Role
    content: str

@dataclass(frozen=True)
class Response:
    text: str

    model: str

    input_tokens: int
    output_tokens: int

    stop_reason: str | None = None

# Hvorfor frozen=True?
# En besked, der er sendt, er en kendsgerning. Gør vi den uforanderlig, kan
# ingen del af systemet ved et uheld ændre historikken bagefter, og objekterne
# kan trygt deles mellem lag og logges præcis som de var.

#Så models = de ting, vi sender frem og tilbage (seddel og tallerken)