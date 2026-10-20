"""Samler MCP-laget: vælger hvilke værktøjer der sættes i."""
import settings
from MCP.application.tool_service import ToolService
from MCP.infrastructure.repository.git_repository import GitRepository
from MCP.infrastructure.tools.code_list_tool import CodeListTool
from MCP.infrastructure.tools.code_read_tool import CodeReadTool
from MCP.infrastructure.tools.ot_document_search_tool import OtDocumentSearchTool
from MCP.infrastructure.tools.requirements_search_tool import RequirementsSearchTool
from MCP.infrastructure.tools.specification_search_tool import SpecificationSearchTool
from RAG.application.ingest_service import IngestService
from RAG.infrastructure.chunking.text_chunker import ParagraphChunker
from RAG.infrastructure.index.keyword_index import KeywordIndex
from RAG.infrastructure.loaders.markdown_loader import MarkdownLoader
from RAG.infrastructure.loaders.pdf_loader import PdfLoader
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

    # De fire værktøjer, AI'en kan kalde. Tilbage til build_agents() (trin 9).
    tools = [
        RequirementsSearchTool(requirements, k=settings.SEARCH_K),
        SpecificationSearchTool(specification, k=settings.SEARCH_K),
        CodeListTool(settings.CODE_FOLDER),
        CodeReadTool(settings.CODE_FOLDER),
    ]
    return ToolService(tools)


def build_code_repository() -> GitRepository | None:
    """Repoet med koden, eller None, hvis CODE_FOLDER er en mappe på computeren (CODE_REPO er tom)."""
    if not settings.CODE_REPO:
        return None
    repo = GitRepository(settings.CODE_REPO, settings.CODE_FOLDER, settings.CODE_BRANCH, settings.AZURE_DEVOPS_PAT)
    # Klon eller hent det nyeste ved start. Går det galt, starter siden alligevel, og fejlen vises igen ved første kodetjek.
    try:
        print(f"Code: {settings.CODE_REPO} at commit {repo.sync()} in {settings.CODE_FOLDER}")
    except RuntimeError as e:
        print(f"Code: could not fetch {settings.CODE_REPO}: {e}")
    return repo


def build_ot_service() -> ToolService:
    """Værktøjerne til OT-holdets dokumenter: kun søgningen i dem.

    Hvorfor ikke bare et værktøj mere i build_service()?
    Ikke alle roller ser OT. Som to sæt kan Agent-laget give hver rolle præcis de værktøjer,
    dens hold har (ROLE_TEAMS), så Vedligehold ikke kan læse kode, og Product ikke kan søge i OT.
    """
    # OT's regneark og PDF'er får hvert sit indeks. Hver række i et ark og hver side i en PDF bliver ét afsnit.
    # Hvorfor to? Signallisten har over 20.000 rækker. I ét indeks ville rækkerne skubbe PDF-siderne ud af resultaterne,
    # så et spørgsmål om fx "QAL2" kun gav signaler og aldrig dokumentet, der forklarer det.
    tables = KeywordIndex()
    rows = IngestService(XlsxTableLoader(settings.OT_FOLDER), ParagraphChunker(), tables).run()
    pdfs = KeywordIndex()
    pdf_loader = PdfLoader(settings.OT_FOLDER)
    pages = IngestService(pdf_loader, ParagraphChunker(), pdfs).run()

    # Vises i konsollen ved start, så man kan se, om dokumenterne faktisk blev læst.
    print(f"OT documents: {rows} rows from spreadsheets and {pages} PDF pages in {settings.OT_FOLDER}")
    if pdf_loader.files_without_text:
        print("  PDFs without text (scanned?), so they can't be searched: " + ", ".join(pdf_loader.files_without_text))
    # Filer, der hverken er regneark eller PDF, fx Word-dokumenter. Dem kan søgningen ikke læse endnu.
    skipped = sorted(f.name for f in settings.OT_FOLDER.rglob("*") if f.is_file() and f.suffix.lower() not in (".xlsx", ".pdf", ".md"))
    if skipped:
        print(f"  {len(skipped)} files can't be read yet (only .xlsx and .pdf): " + ", ".join(skipped[:10]) + (" ..." if len(skipped) > 10 else ""))
    return ToolService([OtDocumentSearchTool(pdfs, tables, k=settings.OT_SEARCH_K)])
