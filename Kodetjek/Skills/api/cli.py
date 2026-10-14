"""Kommandolinjen til Skills-laget.

Kør fra projektets rod:
    python -m Skills.api.cli list
    python -m Skills.api.cli catalog
    python -m Skills.api.cli show mail
"""
import argparse

from Skills.api.build import build_service


def main():
    # 1. Læs hvad brugeren skrev i terminalen.
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="Show all skills")
    commands.add_parser("catalog", help="Show the catalog exactly as the LLM sees it")
    show_parser = commands.add_parser("show", help="Show one skill in full")
    show_parser.add_argument("name")
    args = parser.parse_args()

    # 2. Byg servicen.
    service = build_service()

    # 3. Gør det, brugeren bad om.
    if args.command == "list":
        for skill in service.list_skills():
            print(f"{skill.name}\n  {skill.description}\n")

    elif args.command == "catalog":
        print(service.catalog())

    else:
        try:
            skill = service.load(args.name)
            print(skill.instructions)
        except ValueError as error:
            print(f"ERROR: {error}")


if __name__ == "__main__":
    main()
