"""Samler Agent-laget: hjernen, alle værktøjer og skills."""
import settings
from Agent.application.agent_service import AgentService
from Agent.application.answer_writer import AnswerWriter
from Agent.application.small_talk import SmallTalk
from Agent.infrastructure.brains.gemini_brain import GeminiBrain
from MCP.api.build import build_ot_service, build_service as build_tools
from MCP.application.tool_service import ToolService
from Skills.api.build import build_service as build_skills
from Skills.api.skill_tool import LoadSkillTool


def build_agents() -> dict[str, AgentService]:
    """Én agent pr. rolle. Rollen får kun værktøjerne til de hold, den ser (ROLE_TEAMS i settings.py)."""
    # 2: BYG AGENTERNE: Her samles alle lag. Det sker én gang, når serveren starter.

    # 3: SKILLS: Fortsæt i Skills/api/build.py.
    skills = build_skills()

    # 4: VÆRKTØJER: Fortsæt i MCP/api/build.py. Her indlæses også xlsx-filerne (trin 5-8).
    # Hvert sæt værktøjer bygges én gang og deles af de roller, der ser holdet, så filerne kun indlæses én gang.
    code_tools = build_tools()
    ot_tools = build_ot_service()

    # Hjernen, der taler med Gemini.
    brain = GeminiBrain(model=settings.GEMINI_MODEL, api_key=settings.GEMINI_API_KEY, thinking=settings.GEMINI_THINKING)

    def build_agent(teams: list[str]) -> AgentService:
        # 9: SAML: Værktøjerne til rollens hold lægges i én ToolService, og systemprompten skrives til de samme hold.
        tools, prompts = [], []
        if settings.TEAM in teams:
            # Kodetjek: krav, kravspec og kode. code-review og holdets architecture-skill skal bruges i hvert
            # kodetjek, så koden sætter dem ind i systemprompten i stedet for at lade agenten vælge at hente dem.
            # audience-skills skjules: rollen bruges først, når svaret skrives (AnswerWriter), aldrig i vurderingen.
            # load_skill gives kun, hvis der er andre skills, agenten selv kan vælge.
            tools += list(code_tools.tools.values())
            architecture = f"architecture-{settings.TEAM}"
            system = (
                settings.SYSTEM_PROMPT
                + f"\nThe code belongs to IT's {settings.TEAM} team, which {settings.TEAMS[settings.TEAM]}"
                + "\n\n" + skills.load("code-review").instructions
                + "\n\n" + skills.load(architecture).instructions
            )
            hide = ("audience-", "code-review", architecture)
            if any(not s.name.startswith(hide) for s in skills.list_skills()):
                tools.append(LoadSkillTool(skills))
                system += "\n\nIf a task fits a skill, load it with load_skill before you start.\nSkills:\n" + skills.catalog(hide=hide)
            prompts.append(system)
        if settings.DOCUMENT_TEAM in teams:
            # Opslag i OT's dokumenter: kun søgningen, og agenten svarer direkte.
            tools += list(ot_tools.tools.values())
            team = settings.DOCUMENT_TEAM
            prompts.append(settings.OT_PROMPT + f"\nThe documents are made by IT's {team.upper()} team, which {settings.TEAMS[team]}")

        system = prompts[0]
        if len(prompts) > 1:
            # Ser rollen begge hold, afgør agenten ud fra spørgsmålet, hvilken slags det er.
            system = (
                "You can do two things. Decide from the question which one it is about.\n\n"
                "A. Check whether the code solves a task:\n" + prompts[0]
                + "\n\nB. Look something up in OT's documents. Then answer directly, and do not write an assessment:\n" + prompts[1]
            )
        return AgentService(brain, ToolService(tools), system, max_steps=settings.MAX_STEPS)

    # Agenterne er klar. Tilbage til main() i Agent/api/web.py (trin 10).
    return {role: build_agent(teams) for role, teams in settings.ROLE_TEAMS.items()}


def build_writer() -> AnswerWriter:
    # Skribenten, der laver vurderingen om til et svar til den valgte rolle (trin 20b).
    # Den får rollens skill (audience-<rolle>) fra Skills-laget, men ingen værktøjer.
    skills = build_skills()
    brain = GeminiBrain(model=settings.GEMINI_MODEL, api_key=settings.GEMINI_API_KEY, thinking=settings.GEMINI_THINKING)
    return AnswerWriter(brain, lambda role: skills.load(f"audience-{role}").instructions)


def build_small_talk() -> SmallTalk:
    # Det første skridt for hvert spørgsmål (trin 11b): er det småsnak, svares der uden at se i koden.
    brain = GeminiBrain(model=settings.GEMINI_MODEL, api_key=settings.GEMINI_API_KEY, thinking=settings.GEMINI_THINKING)
    return SmallTalk(brain)
