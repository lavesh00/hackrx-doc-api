import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

class VectorStore:
    def __init__(self, persist_path="/data/chroma", collection="policies"):
        self.persist_path = persist_path
        self.client = chromadb.Client(
            Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_path)
        )
        self.emb_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.col = self.client.get_or_create_collection(collection_name=collection)

    def _persist(self):
        # mandatory when running in Jupyter / long-lived processes[71]
        self.client.persist()

    def add_texts(self, texts: list[str], metadatas: list[dict]):
        embeds = self.emb_model.encode(texts).tolist()
        ids = [str(abs(hash(t))) for t in texts]
        self.col.upsert(documents=texts, embeddings=embeds, metadatas=metadatas, ids=ids)
        self._persist()

    def semantic_search(self, query: str, k: int = 5) -> list[str]:
        q_emb = self.emb_model.encode([query]).tolist()
        results = self.col.query(query_embeddings=q_emb, n_results=k)
        return results["documents"][0]
