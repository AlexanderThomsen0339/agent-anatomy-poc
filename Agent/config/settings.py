"""Indstillinger for Agent-laget."""

# Modellen, der tænker, når den rigtige hjerne bruges.
MODEL = "claude-sonnet-5-5"

# Grænsen for antal skridt. Beskytter mod en agent, der kører i ring.
MAX_STEPS = 8

# Grundinstruktionen. Kataloget over skills sættes på i api/build.py.
SYSTEM_PROMPT = (
    "Du er en hjælpsom assistent for Biblioteket Anatomi. Svar på dansk.\n"
    "Brug værktøjerne, når du har brug for viden eller skal regne. Gæt aldrig.\n"
    "Passer en opgave til en skill, så hent den med load_skill, før du går i gang."
)
