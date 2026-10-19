"""Samler MCP-laget: vælger hvilke værktøjer der sættes i."""
import settings
from MCP.application.tool_service import ToolService
from MCP.infrastructure.tools.code_list_tool import CodeListTool
from MCP.infrastructure.tools.code_read_tool import CodeReadTool
from MCP.infrastructure.tools.ot_document_search_tool import OtDocumentSearchTool
from MCP.infrastructure.tools.requirements_search_tool import RequirementsSearchTool
from MCP.infrastructure.tools.specification_search_tool import SpecificationSearchTool
from RAG.application.ingest_service import IngestService
from RAG.infrastructure.chunking.text_chunker import ParagraphChunker
from RAG.infrastructure.index.keyword_index import KeywordIndex
from RAG.infrastructure.loaders.markdown_loader import MarkdownLoader
from RAG.infrastructure.loaders.xlsx_loader import XlsxLoader
from RAG.infrastructure.loaders.xlsx_table_loader import XlsxTableLoader


def build_service() -> ToolService:
    # 4: VÆRKTØJER: Først fyldes søgeindekset med kravene, så search_requirements har noget at søge i.
    # 5: INDLÆS KRAV: Fortsæt i RAG/application/ingest_service.py.
    requirements = KeywordIndex()
    IngestService(XlsxLoader(settings.DATA_FOLDER), ParagraphChunker(), requirements).run()

    # Kravspec får sit eget indeks, så et krav ikke drukner mellem testcases i søgningen.
    specification = KeywordIndex()
    IngestService(MarkdownLoader(settings.SPEC_FOLDER), ParagraphChunker(), specification).run()

    # OT's dokumenter får også deres eget indeks. Hver række i et ark bliver ét afsnit.
    ot_documents = KeywordIndex()
    IngestService(XlsxTableLoader(settings.OT_FOLDER), ParagraphChunker(), ot_documents).run()

    # De fem værktøjer, AI'en kan kalde. Tilbage til build_agent() (trin 9).
    tools = [
        RequirementsSearchTool(requirements, k=settings.SEARCH_K),
        SpecificationSearchTool(specification, k=settings.SEARCH_K),
        CodeListTool(settings.CODE_FOLDER),
        CodeReadTool(settings.CODE_FOLDER),
        OtDocumentSearchTool(ot_documents, k=settings.OT_SEARCH_K),
    ]
    return ToolService(tools)
