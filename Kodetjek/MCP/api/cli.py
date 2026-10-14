"""Kommandolinjen til MCP-laget: se og prøv værktøjerne selv.

Kør fra projektets rod:
    python -m MCP.api.cli list
    python -m MCP.api.cli call search_docs query="lånerkort"
    python -m MCP.api.cli call search_requirements query="acceptkriterier telefonnummer"
    python -m MCP.api.cli call list_code_files
    python -m MCP.api.cli call read_code_file path=telefon.py
"""
import argparse
import json

from MCP.api.build import build_service
from MCP.domain.models import ToolCall


def parse_arguments(pairs: list[str]) -> dict:
    """Laver ["a=12", "operation=divide"] om til {"a": 12, "operation": "divide"}."""
    arguments = {}
    for pair in pairs:
        key, value = pair.split("=", 1)
        try:
            arguments[key] = json.loads(value)  # tal bliver til tal
        except json.JSONDecodeError:
            arguments[key] = value  # alt andet forbliver tekst
    return arguments


def main():
    # 1. Læs hvad brugeren skrev i terminalen.
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="Vis alle værktøjer")
    call_parser = commands.add_parser("call", help="Kald et værktøj")
    call_parser.add_argument("name")
    call_parser.add_argument("arguments", nargs="*", help="navn=værdi")
    args = parser.parse_args()

    # 2. Byg servicen med alle værktøjer.
    service = build_service()

    # 3. Vis værktøjerne eller kald ét.
    if args.command == "list":
        for spec in service.list_tools():
            params = ", ".join(spec.input_schema.get("properties", {})) or "ingen"
            print(f"{spec.name}({params})\n  {spec.description}\n")
    else:
        result = service.call(ToolCall(args.name, parse_arguments(args.arguments)))
        prefix = "FEJL: " if result.is_error else ""
        print(prefix + result.content)


if __name__ == "__main__":
    main()
