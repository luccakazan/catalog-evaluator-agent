from app.vtex_client import VtexClient
from app.pipeline import ProductPipeline
from app.evaluator import ProductDescriptionEvaluator
from app.storage import CsvStorage
from app.loaders import load_product_ids_from_csv


def main():
    # 1. Carregar ProductIds
    product_ids = load_product_ids_from_csv("product_ids.csv")
    print(f"📦 {len(product_ids)} produtos carregados do CSV")

    # 2. Inicializar componentes
    vtex_client = VtexClient(use_mock=False)
    pipeline = ProductPipeline(vtex_client=vtex_client, batch_size=5)
    evaluator = ProductDescriptionEvaluator()
    storage = CsvStorage(file_path="results.csv")

    # 3. Rodar pipeline (VTEX + quick_score)
    batches = pipeline.run(product_ids)

    # 4. Processar batch a batch
    for idx, batch in enumerate(batches, start=1):
        print(f"\n🔹 Avaliando batch {idx} ({len(batch)} produtos)")

        # ─────────────────────────────
        # FLUXO 1 — Erros de dado (VTEX)
        # ─────────────────────────────
        error_results = [
            {
                "product_id": item["product_id"],
                "score": None,
                "reason": None,
                "error": item["error"],
            }
            for item in batch
            if item.get("error") is not None
        ]

        if error_results:
            storage.save_batch(error_results)

        # ─────────────────────────────
        # FLUXO 2 — Descrição vazia ou muito curta
        # ─────────────────────────────
        quick_results = [
            {
                "product_id": item["product_id"],
                "score": 5,
                "reason": "Descrição vazia ou muito curta",
                "error": None,
            }
            for item in batch
            if item.get("error") is None and item.get("quick_score") == 5
        ]

        if quick_results:
            storage.save_batch(quick_results)

        # ─────────────────────────────
        # FLUXO 3 — Avaliação via LLM
        # ─────────────────────────────
        to_evaluate = [
            item
            for item in batch
            if item.get("error") is None and item.get("quick_score") is None
        ]

        if not to_evaluate:
            continue

        llm_results = evaluator.evaluate_batch(to_evaluate)

        enriched_results = [
            {
                "product_id": r["product_id"],
                "score": r["score"],
                "reason": r["reason"],
                "error": None,
            }
            for r in llm_results
        ]

        storage.save_batch(enriched_results)
        print(f"✅ Batch {idx} salvo com sucesso")

    print("\n🎉 Processamento finalizado com sucesso")


if __name__ == "__main__":
    main()
