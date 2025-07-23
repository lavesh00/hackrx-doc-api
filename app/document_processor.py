from .helpers import extract_text_from_any
from .vector_store import VectorStore
from typing import Iterable

class DocumentProcessor:
    def __init__(self, vector_store: VectorStore, chunk_size=350, overlap=40):
        self.vs = vector_store
        self.chunk_size = chunk_size
        self.overlap = overlap

    def _split(self, text: str) -> Iterable[str]:
        words = text.split()
        for i in range(0, len(words), self.chunk_size - self.overlap):
            yield " ".join(words[i : i + self.chunk_size])

    def ingest_binary(self, data: bytes, filename: str):
        text = extract_text_from_any(data, filename)
        chunks = list(self._split(text))
        metas = [{"source": filename} for _ in chunks]
        self.vs.add_texts(chunks, metas)
