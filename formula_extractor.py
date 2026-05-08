from __future__ import annotations

from typing import Any

from ollama_client import OllamaClient


class FormulaExtractor:
    def __init__(self, client: OllamaClient) -> None:
        self.client = client

    def extract_formulas(self, combined_text: str) -> dict[str, Any]:
        prompt = f"""
You are FormulaForge AI, an exam-oriented academic formula extraction assistant.

Task:
- Detect the subject automatically.
- Detect topics automatically.
- Extract formulas only from the provided notes.
- Organize formulas topic-wise.
- Remove duplicates.
- Keep explanations extremely short and useful for students.
- No long paragraphs.
- If no formula exists for a topic, omit it.
- Return only valid JSON.

Required JSON schema:
{{
  "subject": "string",
  "topics": [
    {{
      "topic_name": "string",
      "formulas": [
        {{
          "formula": "string",
          "meaning": "string",
          "variables": [
            {{
              "symbol": "string",
              "meaning": "string"
            }}
          ],
          "use": "string"
        }}
      ]
    }}
  ],
  "important_formulas": [
    {{
      "formula": "string",
      "meaning": "string",
      "use": "string"
    }}
  ]
}}

Rules:
- Use concise plain English.
- Keep variable descriptions short.
- "important_formulas" should prioritize repeated, central, or high-yield formulas from the notes.
- Do not invent formulas not supported by the notes.

Notes:
{combined_text[:18000]}
"""
        result = self.client.generate_json(prompt)
        return self._normalize_formula_payload(result)

    def answer_question(self, question: str, extracted_notes: str, formula_json: dict[str, Any]) -> str:
        prompt = f"""
You are the FormulaForge AI assistant.
Answer ONLY from the uploaded notes and extracted formula sheet.
If the answer is not present, reply with:
"I could not find that in the uploaded notes."

Keep the answer concise and student-friendly.

Question:
{question}

Formula JSON:
{formula_json}

Uploaded Notes Text:
{extracted_notes[:12000]}
"""
        return self.client.generate_text(prompt)

    def _normalize_formula_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        subject = self._safe_text(payload.get("subject"), "Unknown Subject")
        topics = payload.get("topics") or []
        important = payload.get("important_formulas") or []

        if not isinstance(topics, list):
            topics = []
        if not isinstance(important, list):
            important = []

        normalized_topics = []
        for topic in topics:
            if not isinstance(topic, dict):
                continue
            formulas = []
            for formula in topic.get("formulas", []):
                if not isinstance(formula, dict):
                    continue
                variables = formula.get("variables", [])
                if not isinstance(variables, list):
                    variables = []
                formatted_variables = []
                for variable in variables:
                    if isinstance(variable, dict):
                        symbol = self._safe_text(variable.get("symbol"))
                        meaning = self._safe_text(variable.get("meaning"))
                    else:
                        symbol = self._safe_text(variable)
                        meaning = ""
                    if symbol:
                        formatted_variables.append({"symbol": symbol, "meaning": meaning})

                formula_text = self._safe_text(formula.get("formula"))
                if not formula_text:
                    continue
                formulas.append(
                    {
                        "formula": formula_text,
                        "meaning": self._safe_text(formula.get("meaning")),
                        "variables": formatted_variables,
                        "use": self._safe_text(formula.get("use")),
                    }
                )

            if formulas:
                normalized_topics.append(
                    {
                        "topic_name": self._safe_text(topic.get("topic_name"), "Untitled Topic"),
                        "formulas": formulas,
                    }
                )

        normalized_important = []
        for formula in important:
            if isinstance(formula, dict) and self._safe_text(formula.get("formula")):
                normalized_important.append(
                    {
                        "formula": self._safe_text(formula.get("formula")),
                        "meaning": self._safe_text(formula.get("meaning")),
                        "use": self._safe_text(formula.get("use")),
                    }
                )

        return {
            "subject": subject,
            "topics": normalized_topics,
            "important_formulas": normalized_important,
        }

    def _safe_text(self, value: Any, fallback: str = "") -> str:
        if value is None:
            return fallback
        if isinstance(value, str):
            text = value.strip()
            return text or fallback
        if isinstance(value, (int, float, bool)):
            return str(value).strip() or fallback
        return fallback
