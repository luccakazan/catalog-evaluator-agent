import os
import json
import re
from typing import List, Dict

from google import genai


class ProductDescriptionEvaluator:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = "gemini-2.0-flash"

    def evaluate_batch(self, batch: List[Dict]) -> List[Dict]:
        prompt = self._build_prompt(batch)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return self._parse_response(response.text)

    def _build_prompt(self, batch: List[Dict]) -> str:
        return f"""
Você é um avaliador especialista em descrições de produtos de e-commerce.

Avalie cada descrição usando a escala:
1 = Excelente
2 = Boa
3 = Média
4 = Ruim
5 = Péssima

Critérios:
- Clareza
- Completude
- Linguagem comercial
- Benefícios explícitos

Retorne SOMENTE JSON válido no formato:

[
  {{
    "product_id": "string",
    "score": number,
    "reason": "string curta"
  }}
]

Descrições:
{json.dumps(batch, ensure_ascii=False)}
"""

    def _parse_response(self, text: str) -> List[Dict]:
        """
        Extrai JSON mesmo quando o modelo retorna markdown,
        texto extra ou fenced code blocks.
        """
        # 1. Tenta direto (caso raro, mas rápido)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. Remove fenced code blocks ```json ... ```
        fenced_json = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if fenced_json:
            try:
                return json.loads(fenced_json.group(1))
            except json.JSONDecodeError:
                pass

        # 3. Tenta achar o primeiro array JSON no texto
        array_match = re.search(r"\[\s*{.*?}\s*\]", text, re.DOTALL)
        if array_match:
            try:
                return json.loads(array_match.group(0))
            except json.JSONDecodeError:
                pass

        # 4. Falhou tudo → erro explícito
        raise ValueError(f"Resposta inválida do modelo:\n{text}")


