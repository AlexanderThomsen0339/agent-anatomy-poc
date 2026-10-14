"""Samler Agent-laget: vælger hjernen og sætter alle værktøjer og skills i."""
import settings
from Agent.application.agent_service import AgentService
from MCP.api.build import build_service as build_tools
from MCP.application.tool_service import ToolService
from Skills.api.build import build_service as build_skills
from Skills.api.skill_tool import LoadSkillTool


def build_agent(fake: bool) -> AgentService:
    # Hænderne: alle værktøjer fra lag 3, plus load_skill fra lag 4.
    skills = build_skills()
    mcp_tools = build_tools()
    tools = ToolService(list(mcp_tools.tools.values()) + [LoadSkillTool(skills)])

    # Systemprompten: grundinstruktionen og kataloget over skills.
    system = settings.SYSTEM_PROMPT + "\n\nSkills:\n" + skills.catalog()

    # Hjernen. Det er det eneste sted i laget, hvor den bliver valgt.
    if fake:
        from Agent.infrastructure.brains.rule_brain import RuleBrain
        brain = RuleBrain()
    elif settings.BRAIN == "gemini":
        from Agent.infrastructure.brains.gemini_brain import GeminiBrain
        brain = GeminiBrain(model=settings.GEMINI_MODEL, api_key=settings.GEMINI_API_KEY)
    else:
        from Agent.infrastructure.brains.claude_brain import ClaudeBrain
        brain = ClaudeBrain(model=settings.MODEL)

    return AgentService(brain, tools, system, max_steps=settings.MAX_STEPS)
