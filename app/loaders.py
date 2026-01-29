import csv
from typing import List


def load_product_ids_from_csv(path: str) -> List[str]:
    product_ids = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if "product_id" not in reader.fieldnames:
            raise ValueError("CSV precisa conter a coluna 'product_id'")

        for row in reader:
            pid = row["product_id"].strip()
            if pid:
                product_ids.append(pid)

    # remove duplicados mantendo ordem
    return list(dict.fromkeys(product_ids))
