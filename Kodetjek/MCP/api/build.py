"""Samler MCP-laget: vælger hvilke værktøjer der sættes i."""
import settings
from MCP.application.tool_service import ToolService
from MCP.infrastructure.tools.code_list_tool import CodeListTool
from MCP.infrastructure.tools.code_read_tool import CodeReadTool
from MCP.infrastructure.tools.requirements_search_tool import RequirementsSearchTool
from RAG.application.ingest_service import IngestService
from RAG.infrastructure.chunking.text_chunker import ParagraphChunker
from RAG.infrastructure.index.keyword_index import KeywordIndex
from RAG.infrastructure.loaders.xlsx_loader import XlsxLoader


def build_service() -> ToolService:
    # Fyld RAG-lagets indeks med user stories og testcases, så kravsøgningen har noget at søge i.
    requirements = KeywordIndex()
    IngestService(XlsxLoader(settings.DATA_FOLDER), ParagraphChunker(), requirements).run()

    # Her vælger vi, hvilke apparater der sættes i. Det eneste sted, det sker.
    tools = [
        RequirementsSearchTool(requirements, k=settings.SEARCH_K),
        CodeListTool(settings.CODE_FOLDER),
        CodeReadTool(settings.CODE_FOLDER),
    ]
    return ToolService(tools)
