"""Kommandolinjen til Agent-laget.

Kør fra projektets rod:
    python -m Agent.api.cli --fake
    python -m Agent.api.cli "Does our code solve US-002?" --fake
    python -m Agent.api.cli "Does our code solve US-001?"
"""
import argparse

from Agent.api.build import build_agent
from Agent.domain.models import Decision, Step


def show_step(decision: Decision, steps: list[Step]) -> None:
    """Viser hvert skridt, mens agenten arbejder."""
    print(f"Thinking: {decision.text}")
    for step in steps:
        a, o = step.action, step.observation
        status = "ERROR" if o.is_error else "OK"
        print(f"  Doing:  {a.tool}({a.arguments})")
        first_line = o.content.splitlines()[0] if o.content else ""
        print(f"  Seeing: [{status}] {first_line}")
    print()


def main():
    # 1. Læs hvad brugeren skrev i terminalen.
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?", help="The task for the agent")
    parser.add_argument("--fake", action="store_true", help="Use the rule-based apprentice, no API key")
    args = parser.parse_args()

    # Lærlingen kan kun sit manuskript, så med --fake bruges demo-opgaven.
    if args.question:
        question = args.question
    elif args.fake:
        from Agent.infrastructure.brains.rule_brain import DEMO_QUESTION
        question = DEMO_QUESTION
    else:
        parser.error("Write a task, or use --fake")

    # 2. Byg agenten.
    agent = build_agent(args.fake)

    # 3. Kør løkken og vis hvert skridt.
    print(f"Task: {question}\n")
    run = agent.run(question, on_step=show_step)

    # 4. Vis svaret.
    print("Answer:" if run.finished else "Not finished:")
    print(run.answer)
    print(f"\n({len(run.steps)} tool calls)")


if __name__ == "__main__":
    main()
