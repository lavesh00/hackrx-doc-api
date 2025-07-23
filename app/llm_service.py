import google.generativeai as genai
import os
from .schemas import DecisionResponse, Clause

class GeminiService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def _build_prompt(self, query: str, docs: list[str]) -> str:
        joined = "\n---\n".join(docs[:20])
        return (
            "You are an insurance rules engine.\n"
            f"User query: {query}\n"
            f"Relevant clauses:\n{joined}\n"
            "Return JSON with keys decision, amount (or null), justification, clauses."
        )

    def reason(self, query: str, documents: list[str]):
        prompt = self._build_prompt(query, documents)
        resp = self.model.generate_content(prompt, stream=False)
        return DecisionResponse.model_validate_json(resp.text)
