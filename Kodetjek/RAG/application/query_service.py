"""QueryService: finder relevante afsnit og lader LLM-laget svare ud fra dem."""
from LLM.application.llm_service import LLMService
from RAG.domain.models import Answer, SearchResult
from RAG.domain.ports import SearchIndex


class QueryService:

    def __init__(self, index: SearchIndex, llm: LLMService, k: int = 3):
        # Vi får både indekset og hjernen udefra.
        self.index = index
        self.llm = llm
        self.k = k

    def ask(self, question: str) -> Answer:
        # 1. Søg i dokumenterne.
        results = self.index.search(question, self.k)

        # Findes der intet, spørger vi ikke modellen. Det sparer et kald,
        # og modellen kan ikke finde på et svar, der ikke står nogen steder.
        if not results:
            return Answer("Jeg fandt intet i dokumenterne om det.", [])

        # 2. Byg en prompt med spørgsmålet og de fundne afsnit.
        prompt = self._build_prompt(question, results)

        # 3. Lad LLM-laget svare.
        response = self.llm.ask(prompt)
        return Answer(response.text, results)

    @staticmethod
    def _build_prompt(question: str, results: list[SearchResult]) -> str:
        context = "\n".join(f"[{r.chunk.source}] {r.chunk.text}" for r in results)
        return (
            "Svar kun ud fra konteksten nedenfor. "
            "Står svaret der ikke, så sig det. Nævn kilden.\n\n"
            f"Kontekst:\n{context}\n\n"
            f"Spørgsmål: {question}"
        )
