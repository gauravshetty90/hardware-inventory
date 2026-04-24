from pathlib import Path

from PySide6.QtWidgets import (
  QMainWindow,
  QWidget,
  QVBoxLayout,
  QPushButton,
  QTableWidget,
  QTableWidgetItem,
)

from hardware_inventory.services.inventory_service import InventoryService
from hardware_inventory.storage.json_store import JsonStore
from hardware_inventory.utils.paths import PRODUCTS_FILE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hardware Inventory")
        self.resize(1000, 700)

        self.inventory_service = InventoryService(JsonStore(PRODUCTS_FILE))

        self._build_ui()
        self._load_table()

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout()

        self.add_button = QPushButton("Add Product")
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "SKU",
            "Name",
            "Category",
            "Qty",
            "Cost",
            "Sell",
            "Min Qty",
        ])

        layout.addWidget(self.add_button)
        layout.addWidget(self.table)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _load_table(self) -> None:
        products = self.inventory_service.get_all_products()
        self.table.setRowCount(len(products))

        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(product.sku))
            self.table.setItem(row, 1, QTableWidgetItem(product.name))
            self.table.setItem(row, 2, QTableWidgetItem(product.category))
            self.table.setItem(row, 3, QTableWidgetItem(str(product.quantity)))
            self.table.setItem(row, 4, QTableWidgetItem(f"{product.cost_price:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{product.sell_price:.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(str(product.min_quantity)))