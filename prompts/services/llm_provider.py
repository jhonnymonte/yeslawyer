import os
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # if sdk is not installed, we use the mock


class LLMProvider:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        self._client: Optional["OpenAI"] = None

        if api_key and OpenAI is not None:
            # if sdk and api key are available, we use the real OpenAI
            self._client = OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        if not self._client:
            return f"[mocked-llm_response] {prompt[:120]}"

        try:
            response = self._client.responses.create(
                model=self.model,
                input=prompt,
                max_output_tokens=400,
            )
            return response.output_text.strip()
        except Exception:
            # if any error occurs, we use the mock
            return f"[mocked-llm_response] {prompt[:120]}"
