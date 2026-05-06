from dataclasses import dataclass, asdict


@dataclass
class Sale:
    """Represents a single sales transaction."""
    sale_id: str
    product_sku: str
    product_name: str
    quantity: int
    unit_price: float
    sale_date: str
    total_amount: float

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Sale":
        return cls(
            sale_id=data["sale_id"],
            product_sku=data["product_sku"],
            product_name=data["product_name"],
            quantity=int(data["quantity"]),
            unit_price=float(data["unit_price"]),
            sale_date=data["sale_date"],
            total_amount=float(data["total_amount"]),
        )