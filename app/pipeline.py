class ProductPipeline:
    def __init__(self, vtex_client, batch_size: int = 5):
        self.vtex_client = vtex_client
        self.batch_size = batch_size

    def run(self, product_ids: list) -> list:
        products = []

        for product_id in product_ids:
            product = self.vtex_client.get_product_description(product_id)

            # Caso erro na VTEX
            if product.get("error") is not None:
                product["quick_score"] = None
                product["reason"] = None

            else:
                product["quick_score"] = self._quick_score(
                    product.get("description", "")
                )

            products.append(product)  # 👈 SEMPRE adiciona

        batches = [
            products[i:i + self.batch_size]
            for i in range(0, len(products), self.batch_size)
        ]

        print("DEBUG | batches gerados:", batches)
        return batches

    def _quick_score(self, description: str) -> int | None:
        if not description or len(description.strip()) < 20:
            return 5
        return None
