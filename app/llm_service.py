import google.generativeai as genai
import os
import re
import json
from .schemas import DecisionResponse, Clause

class GeminiService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # FIXED: Configured for shorter, more concise responses
        self.model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.1,
                "max_output_tokens": 300,  # Limit response length
                "top_p": 0.8,
                "top_k": 10
            }
        )

    def _build_prompt(self, query: str, docs: list[str]) -> str:
        joined = "\n---\n".join(docs[:10])  # Limit documents to avoid token overuse
        return (
            "You are an insurance claims processor. Analyze quickly and respond concisely.\n\n"
            f"Query: {query}\n\n"
            f"Policy clauses:\n{joined}\n\n"
            "IMPORTANT: Respond with ONLY JSON in this exact format:\n"
            "{\n"
            '  "decision": "approved|rejected|partial",\n'
            '  "amount": 25000.0 or null,\n'
            '  "justification": "Brief 1-sentence explanation",\n'
            '  "clauses": [{"text": "Key clause", "source": "document.pdf"}]\n'
            "}\n\n"
            "Rules: Keep justification under 50 words. Include max 3 clauses. Be direct and concise."
        )

    def _extract_json_from_response(self, text: str) -> dict:
        """Extract and parse JSON from Gemini response"""
        try:
            # Remove potential markdown code blocks
            pattern = r'```(?:json)?\s*(.*?)\s*```'
            match = re.search(pattern, text.strip(), re.DOTALL)

            if match:
                clean_text = match.group(1).strip()
            else:
                clean_text = text.strip()

            # Try to parse as JSON
            return json.loads(clean_text)

        except (json.JSONDecodeError, Exception) as e:
            # Fallback response for parsing errors
            return {
                "decision": "error",
                "amount": None,
                "justification": f"Failed to parse response: {str(e)[:30]}",
                "clauses": []
            }

    def reason(self, query: str, documents: list[str]) -> DecisionResponse:
        """Generate concise decision with proper error handling"""
        try:
            # Build prompt with clear JSON instructions
            prompt = self._build_prompt(query, documents)

            # Generate content
            response = self.model.generate_content(prompt, stream=False)

            # Extract and validate JSON
            json_data = self._extract_json_from_response(response.text)

            # Create DecisionResponse object
            return DecisionResponse.model_validate(json_data)

        except Exception as e:
            # Ultimate fallback
            return DecisionResponse(
                decision="error",
                amount=None,
                justification=f"Service error: {str(e)[:30]}",
                clauses=[]
            )
