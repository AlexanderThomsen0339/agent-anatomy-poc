"""Lommeregneren: regner præcist med to tal.

LLM'er er gode til sprog, men kan regne forkert. Et værktøj regner altid rigtigt.
"""
from MCP.domain.models import ToolSpec


class CalculatorTool:

    spec = ToolSpec(
        name="calculate",
        description="Regner præcist med to tal. Brug det i stedet for at regne selv.",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "Første tal"},
                "b": {"type": "number", "description": "Andet tal"},
                "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
            },
            "required": ["a", "b", "operation"],
        },
    )

    def run(self, arguments: dict) -> str:
        a = float(arguments["a"])
        b = float(arguments["b"])
        operation = arguments["operation"]

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Man kan ikke dividere med 0.")
            result = a / b
        else:
            raise ValueError(f"Ukendt regneart: {operation}")

        # 5.0 vises som 5, men 2.5 forbliver 2.5.
        return f"{result:g}"
