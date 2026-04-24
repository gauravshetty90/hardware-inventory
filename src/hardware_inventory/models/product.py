from dataclasses import dataclass, asdict


@dataclass
class Product:
    """Class that creates items or products for the inventory"""
    sku: str
    name: str
    category: str
    quantity: int
    cost_price: float
    sell_price: float
    min_quantity: int

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        return cls(
            sku=data["sku"],
            name=data["name"],
            category=data["category"],
            quantity=int(data["quantity"]),
            cost_price=float(data["cost_price"]),
            sell_price=float(data["sell_price"]),
            min_quantity=int(data["min_quantity"]),
        )
