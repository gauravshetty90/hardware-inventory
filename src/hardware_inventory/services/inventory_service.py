from hardware_inventory.models.product import Product
from hardware_inventory.storage.json_store import JsonStore


class InventoryService:
    def __init__(self, store: JsonStore):
        self.store = store
        self.products = self.store.load_products()

    def get_all_products(self) -> list[Product]:
        return self.products

    def add_product(self, product: Product) -> None:
        if any(p.sku == product.sku for p in self.products):
            raise ValueError("SKU already exists")
        self.products.append(product)
        self.store.save_products(self.products)

    def update_product(self, original_sku: str, updated_product: Product) -> None:
        for index, product in enumerate(self.products):
            if product.sku == original_sku:
                if updated_product.sku != original_sku and any(
                    p.sku == updated_product.sku for p in self.products
                ):
                    raise ValueError("Updated SKU already exists")

                self.products[index] = updated_product
                self.store.save_products(self.products)
                return

        raise ValueError("Product not found")

    def delete_product(self, sku: str) -> None:
        for index, product in enumerate(self.products):
            if product.sku == sku:
                del self.products[index]
                self.store.save_products(self.products)
                return

        raise ValueError("Product not found")

    def get_product_by_sku(self, sku: str) -> Product | None:
        for product in self.products:
            if product.sku == sku:
                return product
        return None
