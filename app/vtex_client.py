import os
import requests
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


class VtexClient:
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock

        self.account = os.getenv("VTEX_ACCOUNT")
        self.app_key = os.getenv("VTEX_APP_KEY")
        self.app_token = os.getenv("VTEX_APP_TOKEN")

        if not self.use_mock:
            self._validate_env()

        self.base_url = f"https://{self.account}.vtexcommercestable.com.br"

    def _validate_env(self):
        if not all([self.account, self.app_key, self.app_token]):
            raise RuntimeError("Credenciais VTEX não configuradas corretamente")

    def get_product_description(self, product_id: str) -> dict:
        if self.use_mock:
            return {
                "product_id": product_id,
                "description": "Mock description",
                "error": None,
            }

        url = f"{self.base_url}/api/catalog/pvt/product/{product_id}"
        headers = {
            "X-VTEX-API-AppKey": self.app_key,
            "X-VTEX-API-AppToken": self.app_token,
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.RequestException as e:
            return {
                "product_id": product_id,
                "description": "",
                "error": f"request_error: {str(e)}",
            }

        if response.status_code == 404:
            return {
                "product_id": product_id,
                "description": "",
                "error": "product_not_found",
            }
        
        if response.status_code != 200:
            return {
                "product_id": product_id,
                "description": "",
                "error": f"vtex_status_{response.status_code}",
            }

        data = response.json()
        description = self._extract_description(data)

        return {
            "product_id": product_id,
            "description": description or "",
            "error": None,
        }

    def _extract_description(self, data: dict) -> str:
        """
        Tenta extrair a melhor descrição possível do produto.
        """
        if isinstance(data.get("Description"), str):
            return data["Description"]

        if isinstance(data.get("MetaTagDescription"), str):
            return data["MetaTagDescription"]

        # fallback comum em contas mal configuradas
        if isinstance(data.get("Name"), str):
            return data["Name"]

        return ""
