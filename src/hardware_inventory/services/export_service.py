import csv
from pathlib import Path


class ExportService:
    REQUIRED_IMPORT_FIELDS = {"sku", "name", "quantity"}

    def export_products_to_csv(self, products: list[dict], file_path: str) -> None:
        if not products:
            raise ValueError("There are no products to export.")

        all_columns = []
        seen = set()

        for product in products:
            for key in product.keys():
                if key not in seen:
                    seen.add(key)
                    all_columns.append(key)

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_columns)
            writer.writeheader()
            writer.writerows(products)

    def import_products_from_csv(self, file_path: str) -> list[dict]:
        path = Path(file_path)

        with path.open("r", newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)

            if reader.fieldnames is None:
                raise ValueError("The CSV file has no header row.")

            headers = {
                header.strip() for header in reader.fieldnames if header
            }
            missing = self.REQUIRED_IMPORT_FIELDS - headers

            if missing:
                missing_list = ", ".join(sorted(missing))
                raise ValueError(f"Missing required columns: {missing_list}")

            products = []
            for row_number, row in enumerate(reader, start=2):
                cleaned = {
                    k.strip(): (v.strip() if isinstance(v, str) else v)
                    for k, v in row.items() if k
                }

                if not any(cleaned.values()):
                    continue

                try:
                    cleaned["quantity"] = int(
                        float(cleaned.get("quantity", 0) or 0))
                except ValueError:
                    raise ValueError(
                        f"Invalid quantity at row {row_number}: {cleaned.get('quantity')}"
                    )

                if "cost_price" in cleaned and cleaned["cost_price"] != "":
                    try:
                        cleaned["cost_price"] = float(cleaned["cost_price"])
                    except ValueError:
                        raise ValueError(
                            f"Invalid cost_price at row {row_number}: {cleaned['cost_price']}"
                        )

                if "sell_price" in cleaned and cleaned["sell_price"] != "":
                    try:
                        cleaned["sell_price"] = float(cleaned["sell_price"])
                    except ValueError:
                        raise ValueError(
                            f"Invalid sell_price at row {row_number}: {cleaned['sell_price']}"
                        )

                if "min_quantity" in cleaned and cleaned["min_quantity"] != "":
                    try:
                        cleaned["min_quantity"] = int(
                            float(cleaned["min_quantity"]))
                    except ValueError:
                        raise ValueError(
                            f"Invalid min_quantity at row {row_number}: {cleaned['min_quantity']}"
                        )

                products.append(cleaned)

        return products
