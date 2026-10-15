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
    # 4: VÆRKTØJER: Først fyldes søgeindekset med kravene, så search_requirements har noget at søge i.
    # 5: INDLÆS KRAV: Fortsæt i RAG/application/ingest_service.py.
    requirements = KeywordIndex()
    IngestService(XlsxLoader(settings.DATA_FOLDER), ParagraphChunker(), requirements).run()

    # De tre værktøjer, AI'en kan kalde. Tilbage til build_agent() (trin 9).
    tools = [
        RequirementsSearchTool(requirements, k=settings.SEARCH_K),
        CodeListTool(settings.CODE_FOLDER),
        CodeReadTool(settings.CODE_FOLDER),
    ]
    return ToolService(tools)
