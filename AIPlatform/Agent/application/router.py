"""Router: afgør, hvor meget et spørgsmål kræver, før der hentes kode eller slås op."""
from Agent.domain.ports import AgentBrain

# De tre veje. CHAT svares her, DOCS slås op i testprotokollerne og kravene, CHECK er et kodetjek.
CHAT, DOCS, CHECK = "CHAT", "DOCS", "CHECK"


class Router:

    def __init__(self, brain: AgentBrain, language_note: str = ""):
        self.brain = brain
        # Sættes sidst på instruktionen, så småsnak kan svares på et andet sprog end dansk.
        self.language_note = language_note

    def route(self, asked: str, topics: str) -> tuple[str, str]:
        """Vejen for beskeden, og svaret, hvis den er småsnak.

        Hvorfor et skridt før agenten?
        "Hej, hvordan går det" og "Hvilke tests er der?" skal ikke hente repoet og læse commits.
        Ét kald uden værktøjer afgør det, og svarer samtidig på småsnak, så den kun koster det ene kald.
        """
        system = (
            "You are the assistant on a page where Aalborg Forsyning's IT and communication teams ask about "
            f"{topics}. Decide what the user's latest message needs:\n"
            f"- {CHECK}: it needs the code, e.g. whether something works, is solved, passes its tests, or what was changed. "
            "Also when it answers a question you asked earlier (e.g. \"ja\").\n"
            f"- {DOCS}: the test protocols and the business requirements are enough, without the code, e.g. which tests or "
            "user stories there are, or what a test, user story or requirement says.\n"
            "If the user follows up on an earlier answer about tests or requirements (e.g. \"du mangler nogle\", \"kun for Profil\"), "
            f"it is still {DOCS}.\n"
            f"- {CHAT}: a greeting, thanks, small talk, or a question about what you can do.\n"
            f"For {CHECK} or {DOCS}, write only that word. When in doubt between them, write {CHECK}.\n"
            f"For {CHAT}, answer it yourself in Danish, in one to three friendly sentences like a colleague, "
            "and say what you can help with. Never make up anything about the code, the changes or the tests."
            + self.language_note
        )
        try:
            text = self.brain.decide(system, asked, [], []).text.strip()
        except Exception:
            # Går kaldet galt, går agenten i gang som før.
            return CHECK, ""
        word = text.strip("*`. ").upper()
        if not text or word.startswith(CHECK):
            return CHECK, ""
        if word.startswith(DOCS):
            return DOCS, ""
        return CHAT, text.removeprefix(CHAT).lstrip(":").strip()
