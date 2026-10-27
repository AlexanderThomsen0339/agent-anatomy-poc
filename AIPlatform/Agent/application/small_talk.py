"""SmallTalk: svarer selv på en hilsen eller et spørgsmål, der ikke kræver et kig i koden."""
from Agent.domain.ports import AgentBrain

# Det, Gemini skriver, når beskeden kræver, at agenten ser i koden, kravene eller dokumenterne.
CHECK = "CHECK"


class SmallTalk:

    def __init__(self, brain: AgentBrain):
        self.brain = brain

    def reply(self, asked: str, topics: str) -> str | None:
        """Svaret, hvis beskeden er småsnak. None, hvis agenten skal i gang.

        Hvorfor et skridt før agenten?
        "Hej, hvordan går det" skal ikke hente repoet, læse commits og slå testcases op.
        Ét kald uden værktøjer afgør det, og svarer samtidig, så småsnak kun koster det ene kald.
        """
        system = (
            "You are the assistant on a page where Aalborg Forsyning's IT and communication teams ask about "
            f"{topics}.\n"
            f"If the message asks about that, or answers a question you asked earlier in the conversation (e.g. \"ja\"), "
            f"write only the word {CHECK}. When in doubt, write {CHECK}.\n"
            "Otherwise (a greeting, thanks, small talk, or a question about what you can do) answer it yourself, "
            "in Danish, in one to three friendly sentences like a colleague, and say what you can help with. "
            "Never make up anything about the code, the changes or the tests."
        )
        try:
            text = self.brain.decide(system, asked, [], []).text.strip()
        except Exception:
            # Går kaldet galt, går agenten i gang som før.
            return None
        if not text or text.strip("*`. ").upper().startswith(CHECK):
            return None
        return text
