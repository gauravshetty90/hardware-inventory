import json
from pathlib import Path

from hardware_inventory.models.sale import Sale


class SalesStore:
    """Handles loading and saving sales data."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def load_sales(self) -> list[Sale]:
        if not self.file_path.exists():
            return []

        with self.file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return [Sale.from_dict(item) for item in data]

    def save_sales(self, sales: list[Sale]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        data = [sale.to_dict() for sale in sales]

        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)