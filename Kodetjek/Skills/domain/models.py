"""Domænemodeller for Skills-laget.

Hvad er en skill?
En skill er genbrugelig know-how: en fast opskrift på, hvordan en bestemt
slags opgave løses hos os. Fx hvordan vi vurderer, om kode løser en user story.
"""

# Hvorfor kun standardbiblioteket?
# domain/ må ikke afhænge af noget udefra, præcis som i de andre lag.
from dataclasses import dataclass


# Hvorfor to modeller i stedet for én?
# Det er hele idéen med skills. LLM'en ser ALTID kataloget (navn + beskrivelse),
# men indholdet hentes KUN, når det skal bruges. Med 50 skills ville det være
# dyrt og forvirrende at sende al deres tekst med hvert eneste kald.


# Hvorfor frozen=True?
# En skill ændrer sig ikke, mens den bliver brugt. Den læses, ikke redigeres.
@dataclass(frozen=True)
class SkillSummary:
    """Titlen i indholdsfortegnelsen. Det, LLM'en altid ser."""

    name: str

    # Hvorfor er beskrivelsen så vigtig?
    # LLM'en vælger skill ud fra beskrivelsen alene, ligesom med værktøjer i lag 3.
    # Den skal sige, HVORNÅR skillen skal bruges, ikke hvad der står i den.
    description: str


@dataclass(frozen=True)
class Skill:
    """Hele nodearket. Hentes først, når skillen skal bruges."""

    name: str
    description: str

    # Hvorfor bare tekst?
    # En skill er instruktioner til en LLM, og en LLM læser tekst.
    # Det gør også, at alle kan skrive en skill uden at kunne programmere.
    instructions: str
