import csv
import os
from typing import List, Dict


class CsvStorage:
    def __init__(self, file_path: str = "results.csv"):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["product_id", "score", "reason", "error"],
                )
                writer.writeheader()

    def save_batch(self, results: List[Dict]):
        existing_ids = self._load_existing_ids()

        with open(self.file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["product_id", "score", "reason", "error"],
            )

            for item in results:
                if item["product_id"] in existing_ids:
                    continue  # idempotência simples

                writer.writerow({
                    "product_id": item["product_id"],
                    "score": item["score"],
                    "reason": item["reason"],
                    "error": item.get("error"),
                })


    def _load_existing_ids(self) -> set:
        if not os.path.exists(self.file_path):
            return set()

        with open(self.file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row["product_id"] for row in reader}
