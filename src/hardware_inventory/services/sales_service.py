from hardware_inventory.models.product import Product
from hardware_inventory.models.sale import Sale, SaleItem
from hardware_inventory.storage.sales_store import SalesStore
from hardware_inventory.services.inventory_service import InventoryService


class SalesService:
    """Handles sales transactions and inventory updates."""

    def __init__(self, sales_store: SalesStore, inventory_service: InventoryService):
        self.sales_store = sales_store
        self.inventory_service = inventory_service

    def get_all_sales(self) -> list[Sale]:
        return self.sales_store.load_sales()

    def record_sale(
        self,
        sale_lines: list[dict],
        sale_date: str | None = None,
    ) -> Sale:
        if not sale_lines:
            raise ValueError("A sale must contain at least one item")

        sale_items: list[SaleItem] = []
        stock_updates: list[tuple[str, Product]] = []

        for line in sale_lines:
            sku = str(line["sku"]).strip()
            quantity = int(line["quantity"])
            unit_price = float(line["unit_price"])

            if quantity <= 0:
                raise ValueError(
                    f"Quantity must be greater than zero for SKU {sku}")

            product = self.inventory_service.get_product_by_sku(sku)
            if product is None:
                raise ValueError(f"Product not found for SKU: {sku}")

            if product.quantity < quantity:
                raise ValueError(
                    f"Insufficient stock for {product.name} (SKU: {sku})"
                )

            sale_item = SaleItem.from_product(
                product_sku=product.sku,
                product_name=product.name,
                quantity=quantity,
                unit_price=unit_price,
            )
            sale_items.append(sale_item)

            product_data = product.to_dict()
            product_data["quantity"] = product.quantity - quantity
            updated_product = product.__class__.from_dict(product_data)

            stock_updates.append((product.sku, updated_product))

        sale = Sale.create(items=sale_items, sale_date=sale_date)

        for sku, updated_product in stock_updates:
            self.inventory_service.update_product(sku, updated_product)

        sales = self.sales_store.load_sales()
        sales.append(sale)
        self.sales_store.save_sales(sales)

        return sale

    def get_total_sales_amount(self) -> float:
        sales = self.sales_store.load_sales()
        return sum(sale.grand_total for sale in sales)
    
    def get_total_items_sold(self) -> int:
        sales = self.sales_store.load_sales()
        return sum(sale.total_items for sale in sales)
    
    def get_sale_by_id(self, sale_id: str) -> Sale | None:
        sales = self.sales_store.load_sales()
        for sale in sales:
            if sale.sale_id == sale_id:
                return sale
        return None