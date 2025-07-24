import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

class VectorStore:
    def __init__(self, persist_path="/data/chroma", collection="policies"):
        self.persist_path = persist_path
        
        # Simple PersistentClient without telemetry settings
        # (PostHog is already mocked, so no errors will occur)
        self.client = chromadb.PersistentClient(path=persist_path)
        
        self.emb_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.col = self.client.get_or_create_collection(name=collection)

    def add_texts(self, texts: list[str], metadatas: list[dict]):
        embeds = self.emb_model.encode(texts).tolist()
        ids = [str(abs(hash(t))) for t in texts]
        self.col.upsert(documents=texts, embeddings=embeds, metadatas=metadatas, ids=ids)

    def semantic_search(self, query: str, k: int = 5) -> list[str]:
        q_emb = self.emb_model.encode([query]).tolist()
        results = self.col.query(query_embeddings=q_emb, n_results=k)
        return results["documents"][0]
