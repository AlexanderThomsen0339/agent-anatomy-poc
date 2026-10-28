"""Agent: en LLM i en løkke. Den tænker, beslutter at gøre noget, ser resultatet,
og tænker igen, indtil opgaven er løst.

Kræver Ollama kørende lokalt (ollama serve) med en Mistral-model hentet
(fx `ollama pull mistral:7b-instruct-v0.3-q4_K_M`).
"""
import json
import re
import urllib.request
import uuid
from dataclasses import dataclass, field
from typing import Callable, Protocol

from tools import ToolCall, ToolService, ToolSpec


# Hvorfor frozen=True?
# Det, der er sket i løkken, er sket. Ingen del af systemet må kunne
# ændre historikken bagefter, for så kan man ikke stole på loggen.


@dataclass(frozen=True)
class Action:
    """Én ting, agenten vil gøre: kalde et værktøj med bestemte argumenter."""

    # Hvorfor et id?
    # Agenten kan bede om flere ting på én gang. Id'et parrer hver handling
    # med sit resultat, så LLM'en ved, hvilket svar der hører til hvad.
    id: str
    tool: str
    arguments: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Decision:
    """Hvad hjernen besluttede i ét skridt."""

    # Hvorfor både tekst og handlinger?
    # LLM'en forklarer ofte, hvad den vil gøre, og gør det så.
    # Teksten gør løkken let at følge for et menneske.
    text: str

    # Hvorfor betyder en tom liste "færdig"?
    # Vil agenten ikke gøre mere, er teksten det endelige svar.
    actions: list[Action] = field(default_factory=list)

    @property
    def is_final(self) -> bool:
        return not self.actions


@dataclass(frozen=True)
class Observation:
    """Det, agenten ser, efter en handling er udført."""

    action_id: str
    content: str

    # Hvorfor et fejl-flag?
    # Gik værktøjet galt, skal agenten kunne se det og prøve noget andet,
    # i stedet for at hele løkken stopper.
    is_error: bool = False


@dataclass(frozen=True)
class Step:
    """Én handling og dens resultat. Det, man viser et menneske bagefter."""

    action: Action
    observation: Observation


@dataclass(frozen=True)
class AgentRun:
    """Hele kørslen: svaret og vejen derhen."""

    answer: str

    # Hvorfor gemme alle skridt?
    # Et svar fra en agent er kun troværdigt, hvis man kan se, hvad den gjorde.
    steps: list[Step]

    # Hvorfor et flag for, om den blev færdig?
    # En agent, der rammer grænsen for antal skridt, har ikke løst opgaven.
    finished: bool = True


# Hvorfor en type for historikken?
# Historikken er skiftevis hjernens beslutninger og det, den så bagefter.
History = list[Decision | list[Observation]]


# Hvorfor en vurdering for sig?
# Hvem der spørger, må kun ændre, hvordan svaret skrives, ikke hvad der er fundet.
# Derfor laver agenten først en vurdering pr. krav, som deles af alle roller,
# og svaret til hver rolle skrives bagefter ud fra den samme vurdering.
@dataclass(frozen=True)
class Finding:
    """Ét krav og hvordan koden klarer det, eller én risiko i måden koden er bygget på."""

    # MET, NOT_MET, CANT_TELL eller RISK.
    status: str
    ids: str
    requirement: str
    code: str
    where: str

    # Hvorfor et rettelsesforslag i vurderingen?
    # Udvikleren vil vide, hvad der skal ændres. Står det i vurderingen, kan svaret ikke finde på et andet.
    fix: str = ""

    # Hvorfor en forklaring uden kode?
    # Kommunikation skal kunne forstå, hvorfor et krav fejler, uden at læse koden.
    why: str = ""


@dataclass(frozen=True)
class Assessment:
    """Agentens vurdering af koden. Den samme, uanset hvem der spørger."""

    findings: list[Finding]

    # Sproget, dommen skrives på: "da" eller "en".
    language: str = "da"

    def count(self, status: str) -> int:
        return sum(1 for f in self.findings if f.status == status)

    @property
    def verdict(self) -> str:
        """Dommen regnes ud her og ikke af AI'en, så tallet altid passer med listen."""
        met = self.count("MET")
        total = met + self.count("NOT_MET") + self.count("CANT_TELL")
        words = VERDICT_WORDS.get(self.language, VERDICT_WORDS["da"])
        word = words[0] if met == total else words[2] if met == 0 else words[1]
        return f"**{word}**. " + words[3].format(met=met, total=total)


# Dommen på hvert sprog: løst, delvist løst, ikke løst, og tallet.
VERDICT_WORDS = {
    "da": ("Løst", "Delvist løst", "Ikke løst", "{met} af {total} krav er opfyldt."),
    "en": ("Solved", "Partly solved", "Not solved", "{met} of {total} requirements are met."),
}


# Hvorfor en port og ikke bare tekst ind og tekst ud?
# En agent skal også kunne:
#   - fortælle modellen, hvilke værktøjer der findes
#   - få at vide, at modellen vil bruge et værktøj
#   - sende resultatet tilbage
# Porten siger præcis det, og MistralBrain opfylder den.
class AgentBrain(Protocol):

    # Hvorfor får hjernen hele historikken hver gang?
    # Modellen husker intet mellem kald. Skal den vide, hvad den allerede
    # har gjort og set, skal det hele sendes med.
    #
    # Hvorfor får den værktøjernes mærkater (ToolSpec)?
    # Det er dem, den vælger imellem.
    def decide(
        self,
        system: str,
        question: str,
        history: History,
        tools: list[ToolSpec],
    ) -> Decision:
        """Beslutter næste skridt: et endeligt svar eller en eller flere handlinger."""
        ...


class AgentService:

    def __init__(
        self,
        brain: AgentBrain,
        tools: ToolService,
        system: str,
        max_steps: int = 8,
        accept: Callable[[str, list[Step]], bool] | None = None,
        reminder: str = "",
    ):
        # Vi får hjernen og værktøjerne udefra.
        self.brain = brain
        self.tools = tools
        self.system = system
        self.max_steps = max_steps
        # Hvorfor accept og reminder?
        # Kan svaret ikke bruges (accept siger nej), får agenten én chance mere med reminder sat på opgaven.
        # Det hjælper en lille model, der glemmer formatet. Uden accept er løkken som før.
        self.accept = accept
        self.reminder = reminder

    def run(self, question: str, on_step: Callable[[list[Step]], None] | None = None, first: list[Action] = ()) -> AgentRun:
        """Løs opgaven. on_step kaldes efter hvert skridt, så man kan følge med.

        first er værktøjskald, koden laver, før modellen tænker første gang (fx søg kravene, læs de ændrede filer).
        Hvorfor? En lille model springer tit værktøjerne over og gætter. Kaldene står i historikken, som havde
        agenten selv bedt om dem, så modellen ser resultaterne, og siden viser dem som skridt og kilder.
        """
        history: History = []
        steps: list[Step] = []
        reminded = False
        if first:
            decision = Decision(text="", actions=list(first))
            history.append(decision)
            observations, new_steps = self._act(decision)
            history.append(observations)
            steps.extend(new_steps)
            if on_step:
                on_step(new_steps)

        for _ in range(self.max_steps):
            # TÆNK: Mistral ser spørgsmålet, alt hidtil og værktøjerne og beslutter, hvad der skal ske.
            decision = self.brain.decide(self.system, question, history, self.tools.list_tools())
            history.append(decision)

            # FÆRDIG? Beder modellen ikke om flere værktøjer, er teksten svaret.
            if decision.is_final:
                if self.accept and not reminded and not self.accept(decision.text, steps):
                    # Svaret kan ikke bruges. Det fjernes, og agenten prøver igen med påmindelsen og alt, den har set.
                    history.pop()
                    question += self.reminder
                    reminded = True
                    continue
                # SVAR: Løkken slutter.
                return AgentRun(decision.text, steps)

            # HANDL: Hvert værktøj, modellen bad om, kaldes.
            observations, new_steps = self._act(decision)

            # SE: Resultaterne lægges i historikken, så modellen ser dem i næste runde.
            history.append(observations)
            steps.extend(new_steps)
            # VIS SKRIDT: Fortæl web-siden, hvad der lige skete.
            if on_step:
                on_step(new_steps)

        # Grænsen for antal skridt beskytter mod en agent, der kører i ring.
        return AgentRun("I did not finish within the step limit.", steps, finished=False)

    def _act(self, decision: Decision) -> tuple[list[Observation], list[Step]]:
        """Kalder hvert værktøj i beslutningen og parrer resultatet med handlingen."""
        observations = []
        new_steps = []
        for action in decision.actions:
            result = self.tools.call(ToolCall(action.tool, action.arguments))
            observation = Observation(action.id, result.content, result.is_error)
            observations.append(observation)
            new_steps.append(Step(action, observation))
        return observations, new_steps


STATUSES = ("MET", "NOT_MET", "CANT_TELL", "RISK")
# Det, svaret siger, når alt er opfyldt, på hvert sprog.
NOTHING_MISSING = {"da": "Intet mangler.", "en": "Nothing is missing."}
LOCATION = re.compile(r"^`?[\w./\\-]+\.\w+(:\d+)?`?$")
# Hvor langt svaret højst må være. Skillsne siger det også, men en lille lokal model overholder det ikke,
# så koden skærer resten væk. Produkt / kommunikation tælles i sætninger, IT i linjer.
MAX_SENTENCES = {"product": 5}
MAX_LINES = {"it": 12}


def shorten(text: str, sentences: int = 0, lines: int = 0) -> str:
    """Svaret skåret ned til højst så mange hele sætninger eller ikke-tomme linjer."""
    if sentences:
        parts = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
        text = " ".join(parts[:sentences])
    if lines:
        kept = [line for line in text.splitlines() if line.strip()]
        text = "\n".join(kept[:lines])
    return text


def parse_assessment(text: str, language: str = "da") -> Assessment | None:
    """Læser vurderingen, som skillen code-review beder agenten skrive: én linje pr. krav.

    Hvorfor linjer med | og ikke JSON?
    En lille model laver oftere fejl i JSON end i en simpel linje, og linjerne kan læses af et menneske.
    """
    findings = []
    for line in text.splitlines():
        parts = [p.strip() for p in line.lstrip(" -*`").split("|")]
        if parts and parts[0].upper() in STATUSES:
            # Syv dele: status | ids | krav | hvorfor (uden kode) | koden | hvor | ret.
            # Er den sidste af seks dele et sted (fil:linje), har agenten udeladt den tomme rettelse på en MET-linje.
            # Ellers mangler forklaringen uden kode, og resten læses som før.
            if len(parts) == 6 and LOCATION.search(parts[5]):
                parts.append("")
            why = parts.pop(3) if len(parts) >= 7 else ""
            parts += [""] * (6 - len(parts))
            findings.append(Finding(parts[0].upper(), *parts[1:6], why=why))
    findings = drop_contradictions(findings)
    if not any(f.status != "RISK" for f in findings):
        return None
    return Assessment(findings, language=language)


def drop_contradictions(findings: list[Finding]) -> list[Finding]:
    """Fjerner en MET-linje, der citerer den samme kode på samme sted som en NOT_MET-linje.

    Hvorfor?
    En lille model skriver nogle gange det samme krav to gange med to numre: én gang MET og én gang NOT_MET,
    begge med den samme fejlbehæftede kode. Så tæller dommen et krav for meget som opfyldt.
    Koden kan ikke både opfylde og ikke opfylde kravet, så NOT_MET-linjen vinder.
    """
    def same_code(a: Finding, b: Finding) -> bool:
        x, y = a.code.strip("` ").lower(), b.code.strip("` ").lower()
        return a.where == b.where and bool(x) and bool(y) and (x in y or y in x)

    not_met = [f for f in findings if f.status == "NOT_MET"]
    return [f for f in findings if not (f.status == "MET" and any(same_code(f, n) for n in not_met))]


class AnswerWriter:

    def __init__(self, brain: AgentBrain, instructions_for: Callable[[str], str], language_note: str = ""):
        # instructions_for henter skillen audience-<rolle>. Den kommer udefra fra Skills.
        # language_note sættes sidst på instruktionen, når svaret skal på et andet sprog end skillen siger.
        self.brain = brain
        self.instructions_for = instructions_for
        self.language_note = language_note

    def write(self, question: str, assessment: Assessment, role: str) -> str:
        # Er alt opfyldt, og er der ingen risici, er der intet at skrive ud over dommen. Så spares et kald til modellen,
        # og svaret kan ikke komme til at indeholde skillens overskrifter uden indhold.
        if all(f.status == "MET" for f in assessment.findings):
            return assessment.verdict + "\n\n" + NOTHING_MISSING.get(assessment.language, NOTHING_MISSING["da"])
        # SKRIV SVARET: Modellen får kun vurderingen og rollens skill, ingen værktøjer.
        # Den kan derfor ikke vurdere koden igen, kun skrive om. Dommen sættes på af koden.
        findings = "\n".join(
            f"{f.status} | {f.ids} | {f.requirement} | {f.why} | {f.code} | {f.where} | {f.fix}" for f in assessment.findings
        )
        prompt = (
            f"The question was: {question}\n\n"
            f"The verdict, already written above your text: {assessment.verdict}\n\n"
            f"The assessment (status | ids | requirement | why, in plain words | what the code does | where | how to fix):\n{findings}"
        )
        system = (
            self.instructions_for(role)
            + "\n\nOnly use the assessment you are given. Never add, remove or change a status, an id or a file:line."
            + self.language_note
        )
        text = self.brain.decide(system, prompt, [], []).text.strip()
        text = shorten(text, MAX_SENTENCES.get(role, 0), MAX_LINES.get(role, 0))
        return assessment.verdict + "\n\n" + text


# De tre veje. CHAT svares her, DOCS slås op i testprotokollerne og kravene, CHECK er et kodetjek.
CHAT, DOCS, CHECK = "CHAT", "DOCS", "CHECK"


class Router:
    """Afgør, hvor meget et spørgsmål kræver, før der hentes kode eller slås op."""

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
            f"- {CHECK}: it needs the code, e.g. whether something works, is solved, passes its tests, is ready, "
            "or what was changed. Also when it answers a question you asked earlier (e.g. \"ja\").\n"
            f"- {DOCS}: the test protocols are enough, without the code, e.g. which tests or user stories there are, "
            "or what a test or user story says.\n"
            "If the user follows up on an earlier answer about tests (e.g. \"du mangler nogle\", \"kun for Profil\"), "
            f"it is still {DOCS}.\n"
            f"- {CHAT}: ONLY a greeting, thanks, small talk, or a question about what you can do, with nothing left "
            "to find out. A single word or emoji with no other text is always this.\n"
            f"For {CHECK} or {DOCS}, write only that word. If the message asks or hints at anything about the code, "
            f"the product, a module, a test or what is ready, it is never {CHAT}, even disguised as small talk "
            f"(e.g. \"hvad er der sket siden sidst?\" or \"er der noget klar til mig?\" is {CHECK}, not {CHAT}). "
            f"When in doubt, write {CHECK}: never guess or invent an answer about the code, the changes or the tests "
            f"yourself — that is always {CHECK}'s or {DOCS}'s job, never yours here.\n"
            f"Only for {CHAT}, answer it yourself in Danish, in one to three friendly sentences like a colleague, "
            "and say what you can help with."
            + self.language_note
        )
        try:
            text = self.brain.decide(system, asked, [], []).text.strip()
        except Exception:
            # Går kaldet galt, går agenten i gang som før.
            return CHECK, ""
        word = text.strip("*`. ").upper()
        if word.startswith(DOCS):
            return DOCS, ""
        if word.startswith(CHAT):
            # Instruktionen siger én til tre sætninger. En lille model skriver mere, så koden skærer resten væk.
            return CHAT, shorten(text.removeprefix(CHAT).lstrip(":").strip(), sentences=3)
        # Alt andet, inklusive frit tekstsvar en lille model har fundet på i stedet for at skrive et af ordene,
        # går til CHECK. Et gættet svar her ville ellers nå brugeren uden at være tjekket mod koden.
        return CHECK, ""


class MistralBrain:
    """Den rigtige hjerne: lokal Mistral gennem Ollama (tool use).

    Hvorfor Ollamas eget API (/api/chat) og ikke det OpenAI-kompatible?
    Kun det eget API lader os sætte num_ctx, hvor meget tekst modellen må se.
    Ollamas standard er 2.048-4.096 tokens, og systemprompten alene fylder ca. 4.000.
    Er der ikke plads, smider Ollama det ældste væk, og det er reglerne.
    """

    def __init__(self, model: str, base_url: str = "http://localhost:11434", context: int = 32768, temperature: float = 0.1):
        # Det gamle OpenAI-endpoint (.../v1) virker også som adresse: /v1 fjernes.
        self.url = base_url.rstrip("/").removesuffix("/v1") + "/api/chat"
        self.model = model
        # Lav temperatur: en lille model holder sig bedre til formatet, når den ikke "improviserer".
        self.options = {"num_ctx": context, "temperature": temperature}

    def decide(self, system: str, question: str, history: History, tools: list[ToolSpec]) -> Decision:
        body = {
            "model": self.model,
            "messages": self._to_messages(system, question, history),
            "stream": False,
            "options": self.options,
        }
        if tools:
            body["tools"] = [
                {"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.input_schema}}
                for t in tools
            ]
        request = urllib.request.Request(self.url, json.dumps(body).encode(), {"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=600) as response:
            message = json.loads(response.read())["message"]

        text = message.get("content") or ""
        calls = [(c["function"]["name"], c["function"].get("arguments") or {}) for c in message.get("tool_calls") or []]
        if not calls and tools:
            # En lille model skriver tit værktøjskaldet som tekst i stedet for et rigtigt kald.
            calls = self._calls_in_text(text, {t.name for t in tools})
            if calls:
                text = ""
        actions = [
            Action(id=uuid.uuid4().hex[:8], tool=name, arguments=json.loads(args) if isinstance(args, str) else args)
            for name, args in calls
        ]
        return Decision(text=text, actions=actions)

    @staticmethod
    def _calls_in_text(text: str, names: set[str]) -> list[tuple[str, dict]]:
        """Værktøjskald skrevet som tekst, fx `[TOOL_CALLS] [{"name": "search_requirements", "arguments": {...}}]`."""
        raw = text.replace("[TOOL_CALLS]", "").strip().strip("`")
        raw = re.sub(r"^json\s*", "", raw)
        if not raw.startswith(("[", "{")):
            return []
        try:
            data = json.loads(raw)
        except ValueError:
            return []
        items = data if isinstance(data, list) else [data]
        calls = []
        for item in items:
            if isinstance(item, dict) and item.get("name") in names:
                calls.append((item["name"], item.get("arguments") or item.get("parameters") or {}))
        return calls

    @staticmethod
    def _to_messages(system: str, question: str, history: History) -> list[dict]:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": question}]
        # Ollama vil gerne vide, hvilket værktøj et resultat kommer fra.
        tool_of = {}

        for item in history:
            if isinstance(item, Decision):
                tool_of.update({a.id: a.tool for a in item.actions})
                entry = {"role": "assistant", "content": item.text or ""}
                if item.actions:
                    entry["tool_calls"] = [
                        {"function": {"name": action.tool, "arguments": action.arguments}} for action in item.actions
                    ]
                messages.append(entry)
            else:
                observations: list[Observation] = item
                for o in observations:
                    messages.append({"role": "tool", "content": o.content, "tool_name": tool_of.get(o.action_id, "")})

        return messages
