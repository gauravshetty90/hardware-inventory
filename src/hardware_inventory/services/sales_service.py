from datetime import date
from uuid import uuid4

from hardware_inventory.models.sale import Sale
from hardware_inventory.models.product import Product


class SalesService:
    """Handles sales transactions and inventory updates."""

    def __init__(self, sales_store, inventory_service):
        self.sales_store = sales_store
        self.inventory_service = inventory_service

    def get_all_sales(self) -> list[Sale]:
        return self.sales_store.load_sales()

    def record_sale(
        self,
        product_sku: str,
        quantity: int,
        unit_price: float | None = None,
        sale_date: str | None = None,
    ) -> Sale:
        product = self.inventory_service.get_product_by_sku(product_sku)
        if product is None:
            raise ValueError("Product not found.")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        if product.quantity < quantity:
            raise ValueError("Not enough stock available for this sale.")

        final_unit_price = product.sell_price if unit_price is None else float(unit_price)
        if final_unit_price < 0:
            raise ValueError("Unit price cannot be negative.")

        final_sale_date = sale_date or date.today().isoformat()
        total_amount = quantity * final_unit_price

        sale = Sale(
            sale_id=str(uuid4()),
            product_sku=product.sku,
            product_name=product.name,
            quantity=quantity,
            unit_price=final_unit_price,
            sale_date=final_sale_date,
            total_amount=total_amount,
        )

        sales = self.sales_store.load_sales()
        sales.append(sale)
        self.sales_store.save_sales(sales)

        updated_product = Product(
            sku=product.sku,
            name=product.name,
            category=product.category,
            quantity=product.quantity - quantity,
            cost_price=product.cost_price,
            sell_price=product.sell_price,
            min_quantity=product.min_quantity,
        )
        self.inventory_service.update_product(product.sku, updated_product)

        return sale

    def get_total_sales_amount(self) -> float:
        sales = self.sales_store.load_sales()
        return sum(sale.total_amount for sale in sales)