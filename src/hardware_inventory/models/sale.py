from dataclasses import dataclass, field
from typing import Any
import uuid
from datetime import date


@dataclass
class SaleItem:
    product_sku: str
    product_name: str
    quantity: int
    unit_price: float
    line_total: float

    @classmethod
    def from_product(
        cls,
        product_sku: str,
        product_name: str,
        quantity: int,
        unit_price: float,
    ) -> "SaleItem":
        return cls(
            product_sku=product_sku,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            line_total=quantity * unit_price,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_sku": self.product_sku,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "line_total": self.line_total,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SaleItem":
        return cls(
            product_sku=data["product_sku"],
            product_name=data["product_name"],
            quantity=int(data["quantity"]),
            unit_price=float(data["unit_price"]),
            line_total=float(data["line_total"]),
        )


@dataclass
class Sale:
    sale_id: str
    sale_date: str
    items: list[SaleItem] = field(default_factory=list)
    total_items: int = 0
    grand_total: float = 0.0

    @classmethod
    def create(cls, items: list[SaleItem], sale_date: str | None = None) -> "Sale":
        if not items:
            raise ValueError("A sale must contain at least one item")

        final_sale_date = sale_date or date.today().isoformat()
        total_items = sum(item.quantity for item in items)
        grand_total = sum(item.line_total for item in items)

        return cls(
            sale_id=str(uuid.uuid4()),
            sale_date=final_sale_date,
            items=items,
            total_items=total_items,
            grand_total=grand_total,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sale_id": self.sale_id,
            "sale_date": self.sale_date,
            "items": [item.to_dict() for item in self.items],
            "total_items": self.total_items,
            "grand_total": self.grand_total,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Sale":
        items = [SaleItem.from_dict(item) for item in data.get("items", [])]

        return cls(
            sale_id=data["sale_id"],
            sale_date=data["sale_date"],
            items=items,
            total_items=int(data["total_items"]),
            grand_total=float(data["grand_total"]),
        )
