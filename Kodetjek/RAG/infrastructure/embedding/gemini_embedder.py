"""Embeddings fra Googles Gemini: tekst ind, vektorer ud.

Bruger samme GEMINI_API_KEY som agenten, så der ikke skal en ny nøgle til.
Det er den eneste fil i RAG-laget, der kender til Google.
"""
from google import genai
from google.genai import types

# Hvor mange tekster Gemini tager imod i ét kald.
BATCH_SIZE = 100


class GeminiEmbedder:

    def __init__(self, model: str, api_key: str, dimensions: int):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Hvorfor en task_type?
        # Gemini laver lidt forskellige vektorer til det, der gemmes, og det, der søges med.
        # Det giver bedre træf end at behandle begge ens.
        vectors = []
        for start in range(0, len(texts), BATCH_SIZE):
            vectors.extend(self._embed(texts[start:start + BATCH_SIZE], "RETRIEVAL_DOCUMENT"))
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], "RETRIEVAL_QUERY")[0]

    def _embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        result = self.client.models.embed_content(
            model=self.model,
            contents=texts,
            config=types.EmbedContentConfig(task_type=task_type, output_dimensionality=self.dimensions),
        )
        return [e.values for e in result.embeddings]
