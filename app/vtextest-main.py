from app.vtex_client import VtexClient


def main():
    client = VtexClient(use_mock=False)

    test_product_id = "1"  # use um ID real
    result = client.get_product_description(test_product_id)

    print(result)


if __name__ == "__main__":
    main()
