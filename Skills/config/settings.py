"""Indstillinger for Skills-laget."""
from pathlib import Path

# Mappen med skills. Hver skill er en undermappe med en SKILL.md.
SKILLS_FOLDER = Path(__file__).resolve().parent.parent / "data" / "skills"
