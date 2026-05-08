from __future__ import annotations

import json
import os
from typing import Any

import requests


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")


class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_URL, model: str = OLLAMA_MODEL) -> None:
        self.base_url = base_url
        self.model = model

    def generate_json(self, prompt: str) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2,
                "num_ctx": 8192,
            },
        }
        response = requests.post(self.base_url, json=payload, timeout=180)
        response.raise_for_status()
        content = response.json().get("response", "").strip()
        return self._parse_json(content)

    def generate_text(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 8192,
            },
        }
        response = requests.post(self.base_url, json=payload, timeout=180)
        response.raise_for_status()
        return response.json().get("response", "").strip()

    def _parse_json(self, content: str) -> dict[str, Any]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start == -1 or end == -1:
                raise ValueError("Model did not return valid JSON.") from None
            return json.loads(content[start : end + 1])
