"""Samler alt: hjernen, alle værktøjer og skills."""
import settings
from agent import AgentService, AnswerWriter, Router, Step, parse_assessment
from rag import IngestService, KeywordIndex, ParagraphChunker, XlsxLoader
from repository import AzurePullRequestFinder, GitRepository
from skills import FileSkillRepository, LoadSkillTool, SkillService
from tools import CheckoutService, ToolService
from tools_impl import CodeChangesTool, CodeListTool, CodeReadTool, RequirementsListTool, RequirementsSearchTool


def make_brain():
    """Hjernen, BRAIN i settings.py peger på. Kun den valgte hjernes kode importeres."""
    if settings.BRAIN == "mistral":
        from agent import MistralBrain
        return MistralBrain(settings.MISTRAL_MODEL, settings.MISTRAL_BASE_URL, settings.MISTRAL_CONTEXT)
    from gemini_brain import GeminiBrain
    return GeminiBrain(model=settings.GEMINI_MODEL, api_key=settings.GEMINI_API_KEY, thinking=settings.GEMINI_THINKING)


def usable(answer: str, steps: list[Step]) -> bool:
    """Kan siden bruge kodetjekkets svar? Vurderingslinjer eller et spørgsmål (QUESTION: i web.py)."""
    return answer.strip().upper().startswith("QUESTION:") or parse_assessment(answer) is not None


def build_skill_service() -> SkillService:
    # Skills ligger som mapper med en SKILL.md i harness/skills/. FileSkillRepository læser dem, når der bliver spurgt.
    repository = FileSkillRepository(settings.SKILLS_FOLDER)
    return SkillService(repository)


def build_tool_service() -> ToolService:
    # Først fyldes søgeindekset med kravene, så search_requirements har noget at søge i.
    requirements = KeywordIndex()
    IngestService(XlsxLoader(settings.DATA_FOLDER), ParagraphChunker(), requirements).run()

    # De fem værktøjer, AI'en kan kalde.
    tools = [
        RequirementsSearchTool(requirements, k=settings.SEARCH_K),
        # Oversigten over alle tests, så "Hvilke tests er der?" ikke kun får de få bedste søgetræf.
        RequirementsListTool(XlsxLoader(settings.DATA_FOLDER).load()),
        CodeListTool(settings.CODE_FOLDER),
        CodeReadTool(settings.CODE_FOLDER),
        CodeChangesTool(settings.CODE_FOLDER),
    ]
    return ToolService(tools)


def build_checkout_service() -> CheckoutService | None:
    """Vælger branch pr. spørgsmål, eller None, hvis CODE_FOLDER er en mappe på computeren (CODE_REPO er tom)."""
    if not settings.CODE_REPO:
        return None
    repository = GitRepository(settings.CODE_REPO, settings.CODE_FOLDER, settings.AZURE_DEVOPS_PAT)
    # PR'er findes kun i Azure DevOps' API. Et andet repo tjekker altid CODE_BRANCH.
    finder = None
    if "dev.azure.com" in settings.CODE_REPO:
        finder = AzurePullRequestFinder(settings.CODE_REPO, settings.AZURE_DEVOPS_PAT, settings.CODE_BRANCH)
    # Klon eller hent det nyeste ved start. Går det galt, starter siden alligevel, og fejlen vises igen ved første kodetjek.
    try:
        print(f"Code: {settings.CODE_REPO}, {settings.CODE_BRANCH} at commit {repository.sync(settings.CODE_BRANCH)} in {settings.CODE_FOLDER}")
    except RuntimeError as e:
        print(f"Code: could not fetch {settings.CODE_REPO}: {e}")
    return CheckoutService(repository, finder, settings.CODE_BRANCH, CodeChangesTool(settings.CODE_FOLDER))


def build_agents() -> tuple[dict[str, AgentService], AgentService]:
    """Én agent pr. rolle, plus agenten til opslag uden kode.

    Opslagsagenten får kun søgningen i testprotokollerne og kravene, så den aldrig rører repoet.
    """
    skills = build_skill_service()
    code_tools = build_tool_service()

    # Hjernen, der taler med Gemini eller lokal Mistral (BRAIN i settings.py).
    brain = make_brain()

    def build_agent() -> AgentService:
        # Kodetjek: krav og kode. evaluation (processen), code-review og holdets architecture-skill skal
        # bruges i hvert kodetjek, så koden sætter dem ind i systemprompten i stedet for at lade en lille
        # model vælge selv at hente dem med load_skill, hvilket den ikke er til at stole på at gøre.
        # audience-skills skjules: rollen bruges først, når svaret skrives (AnswerWriter), aldrig i vurderingen.
        # load_skill gives kun, hvis der er andre skills tilbage, agenten selv kan vælge.
        tools = list(code_tools.tools.values())
        architecture = f"architecture-{settings.TEAM}"
        hide = ("audience-", "evaluation", "code-review", architecture)
        system = (
            settings.SYSTEM_PROMPT
            + f"\nThe code belongs to IT's {settings.TEAM} team, which {settings.TEAMS[settings.TEAM]}"
            + "\n\n" + skills.load("evaluation").instructions
            + "\n\n" + skills.load("code-review").instructions
            + "\n\n" + skills.load(architecture).instructions
        )
        if any(not s.name.startswith(hide) for s in skills.list_skills()):
            tools.append(LoadSkillTool(skills))
            system += "\n\nIf a task fits a skill, load it with load_skill before you start.\nSkills:\n" + skills.catalog(hide=hide)
        return AgentService(
            brain, ToolService(tools), system + settings.LANGUAGE_NOTE, max_steps=settings.MAX_STEPS,
            accept=usable, reminder=settings.FORMAT_REMINDER,
        )

    agents = {role: build_agent() for role in settings.ROLE_TEAMS}
    docs_tools = [code_tools.tools[name] for name in ("list_requirements", "search_requirements")]
    docs = AgentService(brain, ToolService(docs_tools), settings.DOCS_PROMPT + settings.LANGUAGE_NOTE, max_steps=settings.DOCS_MAX_STEPS)
    return agents, docs


def build_writer() -> AnswerWriter:
    # Skribenten, der laver vurderingen om til et svar til den valgte rolle.
    # Den får rollens skill (audience-<rolle>) fra Skills, men ingen værktøjer.
    skills = build_skill_service()
    brain = make_brain()
    return AnswerWriter(brain, lambda role: skills.load(f"audience-{role}").instructions, settings.LANGUAGE_NOTE)


def build_router() -> Router:
    # Det første skridt for hvert spørgsmål: småsnak, opslag uden kode eller kodetjek.
    brain = make_brain()
    return Router(brain, settings.LANGUAGE_NOTE)
