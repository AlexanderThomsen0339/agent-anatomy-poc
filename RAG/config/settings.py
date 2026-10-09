"""Indstillinger for RAG-laget."""
from pathlib import Path

# Mappen med de dokumenter, der skal kunne søges i.
DOCS_FOLDER = Path(__file__).resolve().parent.parent / "data" / "docs"

# Hvor mange afsnit der sendes med til modellen.
TOP_K = 3
