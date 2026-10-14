"""ToolService: holder styr på værktøjerne og kalder det rigtige."""
from MCP.domain.models import ToolCall, ToolResult, ToolSpec
from MCP.domain.ports import Tool


class ToolService:

    def __init__(self, tools: list[Tool]):
        # Vi får værktøjerne udefra og slår dem op på navn.
        self.tools = {tool.spec.name: tool for tool in tools}

    def list_tools(self) -> list[ToolSpec]:
        """Mærkaterne på alle værktøjer. Det er det, en LLM får at se."""
        return [tool.spec for tool in self.tools.values()]

    def call(self, call: ToolCall) -> ToolResult:
        """Kalder ét værktøj. Går det galt, får man en fejl tilbage i stedet for et nedbrud."""
        tool = self.tools.get(call.name)
        if tool is None:
            return ToolResult(call.name, f"Ukendt værktøj: {call.name}", is_error=True)

        try:
            content = tool.run(call.arguments)
            return ToolResult(call.name, content)
        except Exception as error:
            # Sikringen slår fra: fejlen bliver til et resultat, som en LLM kan læse.
            return ToolResult(call.name, str(error), is_error=True)
