"""Samler MCP-laget: vælger hvilke værktøjer der sættes i.

Både cli.py og mcp_server.py bruger build_service(), så de altid har
præcis de samme værktøjer.
"""
import settings
from MCP.application.tool_service import ToolService
from MCP.infrastructure.tools.calculator_tool import CalculatorTool
from MCP.infrastructure.tools.docs_search_tool import DocsSearchTool
from MCP.infrastructure.tools.time_tool import TimeTool
from RAG.application.ingest_service import IngestService
from RAG.infrastructure.chunking.text_chunker import ParagraphChunker
from RAG.infrastructure.index.keyword_index import KeywordIndex
from RAG.infrastructure.loaders.markdown_loader import MarkdownLoader


def build_service() -> ToolService:
    # Fyld RAG-lagets indeks, så dokumentsøgningen har noget at søge i.
    index = KeywordIndex()
    IngestService(MarkdownLoader(settings.DOCS_FOLDER), ParagraphChunker(), index).run()

    # Her vælger vi, hvilke apparater der sættes i. Det eneste sted, det sker.
    tools = [
        TimeTool(),
        CalculatorTool(),
        DocsSearchTool(index, k=settings.SEARCH_K),
    ]
    return ToolService(tools)
