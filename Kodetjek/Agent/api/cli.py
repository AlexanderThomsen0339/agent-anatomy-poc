"""Kommandolinjen til Agent-laget.

Kør fra projektets rod:
    python -m Agent.api.cli --fake
    python -m Agent.api.cli "Løser vores kode US-002 Opdater telefonnummer?" --fake
    python -m Agent.api.cli "Løser vores kode US-001 Vis regningsoversigt?"
"""
import argparse

from Agent.api.build import build_agent
from Agent.domain.models import Decision, Step


def show_step(decision: Decision, steps: list[Step]) -> None:
    """Viser hvert skridt, mens agenten arbejder."""
    print(f"Tænker: {decision.text}")
    for step in steps:
        a, o = step.action, step.observation
        status = "FEJL" if o.is_error else "OK"
        print(f"  Gør:  {a.tool}({a.arguments})")
        first_line = o.content.splitlines()[0] if o.content else ""
        print(f"  Ser:  [{status}] {first_line}")
    print()


def main():
    # 1. Læs hvad brugeren skrev i terminalen.
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?", help="Opgaven til agenten")
    parser.add_argument("--fake", action="store_true", help="Brug den regelbaserede lærling, ingen API-nøgle")
    args = parser.parse_args()

    # Lærlingen kan kun sit manuskript, så med --fake bruges demo-opgaven.
    if args.question:
        question = args.question
    elif args.fake:
        from Agent.infrastructure.brains.rule_brain import DEMO_QUESTION
        question = DEMO_QUESTION
    else:
        parser.error("Skriv en opgave, eller brug --fake")

    # 2. Byg agenten.
    agent = build_agent(args.fake)

    # 3. Kør løkken og vis hvert skridt.
    print(f"Opgave: {question}\n")
    run = agent.run(question, on_step=show_step)

    # 4. Vis svaret.
    print("Svar:" if run.finished else "Ikke færdig:")
    print(run.answer)
    print(f"\n({len(run.steps)} værktøjskald)")


if __name__ == "__main__":
    main()
