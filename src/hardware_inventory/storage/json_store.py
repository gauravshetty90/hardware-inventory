import json
from pathlib import Path
from hardware_inventory.models.product import Product

class JsonStore:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def load_products(self) -> list[Product]:
        if not self.file_path.exists():
            return []

        with self.file_path.open("r", encoding="utf-8") as f:
            raw_data = json.load(f)

        return [Product.from_dict(item) for item in raw_data]

    def save_products(self, products: list[Product]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in products], f, indent=2)