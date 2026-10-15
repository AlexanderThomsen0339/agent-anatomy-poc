"""Samler Agent-laget: hjernen, alle værktøjer og skills."""
import settings
from Agent.application.agent_service import AgentService
from Agent.infrastructure.brains.gemini_brain import GeminiBrain
from MCP.api.build import build_service as build_tools
from MCP.application.tool_service import ToolService
from Skills.api.build import build_service as build_skills
from Skills.api.skill_tool import LoadSkillTool


def build_agent() -> AgentService:
    # Hænderne: alle værktøjer fra lag 3, plus load_skill fra lag 4.
    skills = build_skills()
    mcp_tools = build_tools()
    tools = ToolService(list(mcp_tools.tools.values()) + [LoadSkillTool(skills)])

    # Systemprompten: grundinstruktionen og kataloget over skills.
    system = settings.SYSTEM_PROMPT + "\n\nSkills:\n" + skills.catalog()

    # Hjernen.
    brain = GeminiBrain(model=settings.GEMINI_MODEL, api_key=settings.GEMINI_API_KEY, thinking=settings.GEMINI_THINKING)

    return AgentService(brain, tools, system, max_steps=settings.MAX_STEPS)
