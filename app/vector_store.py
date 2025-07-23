import os
import sys

# CRITICAL: Disable telemetry BEFORE importing chromadb
os.environ['ANONYMIZED_TELEMETRY'] = 'false'
os.environ['CHROMA_TELEMETRY_DISABLED'] = 'true'

# Monkey patch to completely disable PostHog before ChromaDB imports it
class MockPostHog:
    def __init__(self, *args, **kwargs):
        pass
    def capture(self, *args, **kwargs):
        pass
    def identify(self, *args, **kwargs):
        pass
    def alias(self, *args, **kwargs):
        pass
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

# Replace posthog module before chromadb imports it
sys.modules['posthog'] = type(sys)('posthog')
sys.modules['posthog'].Posthog = MockPostHog

import chromadb
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, persist_path="/data/chroma", collection="policies"):
        self.persist_path = persist_path
        
        # Create client without any telemetry
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