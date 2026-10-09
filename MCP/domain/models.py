"""Domænemodeller for MCP-laget.

Hvorfor egne modeller?
Et værktøj skal kunne beskrives, kaldes og give et resultat på samme måde,
uanset om det er et ur, en lommeregner eller en søgning i dokumenter,
og uanset om kaldet kommer fra terminalen, en MCP-klient eller agent-laget.
"""

# Hvorfor kun standardbiblioteket?
# domain/ må ikke afhænge af noget udefra. Heller ikke af MCP-pakken.
# MCP er én måde at åbne værktøjerne op på, ikke det, værktøjerne ER.
from dataclasses import dataclass, field


# Hvorfor en ToolSpec?
# Det er mærkatet på apparatet: hvad det hedder, hvad det gør, og hvilke
# knapper det har. Det er netop det, en LLM skal læse for at vælge det rigtige
# værktøj, så beskrivelsen er lige så vigtig som koden bag.
@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str

    # Hvorfor et JSON-skema?
    # Det er det fælles sprog for "hvilke argumenter tager værktøjet".
    # Både Claude og MCP forstår det direkte, så vi skal ikke oversætte.
    input_schema: dict = field(default_factory=lambda: {"type": "object", "properties": {}})


# Hvorfor en ToolCall?
# Det er at trykke på knappen: hvilket værktøj og med hvilke argumenter.
# Det er præcis det, en LLM svarer med, når den vil bruge et værktøj.
@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ToolResult:
    name: str

    # Hvorfor altid tekst?
    # Resultatet skal tilbage til en LLM, og den læser tekst.
    # Et værktøj, der giver tal eller lister, laver det om til tekst selv.
    content: str

    # Hvorfor et fejl-flag i stedet for at kaste en fejl?
    # Går et værktøj galt, skal det ikke vælte hele systemet. LLM'en skal
    # i stedet kunne læse fejlen og prøve noget andet, ligesom en sikring,
    # der slår fra i ét rum uden at slukke strømmen i hele huset.
    is_error: bool = False
