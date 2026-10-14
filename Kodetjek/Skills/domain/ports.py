"""Porte for Skills-laget.

Hvorfor kun én port?
Det eneste, laget har brug for udefra, er et sted at hente skills fra.
At lave kataloget og hente den rigtige skill er lagets eget arbejde.
"""

# Hvorfor Protocol?
# Samme grund som i de andre lag: en adapter skal bare have de rigtige metoder.
from typing import Protocol

from .models import Skill, SkillSummary


# Hvorfor en port til at hente skills?
# I dag ligger de som mapper med en SKILL.md. I morgen kan de ligge i en
# database, i SharePoint eller deles mellem flere teams. Resten af laget
# skal ikke mærke forskel.
class SkillRepository(Protocol):

    # Hvorfor en separat list() med kun titler?
    # Kataloget skal kunne laves billigt, uden at læse hver eneste skill
    # i sin helhed. Det er det, der gør "indlæs kun ved behov" muligt.
    def list(self) -> list[SkillSummary]:
        """Alle skills med navn og beskrivelse."""
        ...

    # Hvorfor returnere None i stedet for at kaste en fejl?
    # At en skill ikke findes, er ikke en fejl i systemet. Det er et svar.
    # application/ bestemmer, hvad der skal ske så.
    def get(self, name: str) -> Skill | None:
        """Én skill med fuldt indhold, eller None hvis den ikke findes."""
        ...
