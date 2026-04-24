from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHBoxLayout,
    QMessageBox,
)

from hardware_inventory.services.inventory_service import InventoryService
from hardware_inventory.storage.json_store import JsonStore
from hardware_inventory.utils.paths import PRODUCTS_FILE
from hardware_inventory.ui.product_dialog import ProductDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hardware Inventory")
        self.resize(1000, 700)

        self.inventory_service = InventoryService(JsonStore(PRODUCTS_FILE))

        self._build_ui()
        # self._load_table()
        self._connect_signals()
        self.refresh_table()

    def _build_ui(self) -> None:
        central = QWidget()

        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Product")
        self.edit_button = QPushButton("Edit Product")
        self.delete_button = QPushButton("Delete Product")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)

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

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def _connect_signals(self) -> None:
        self.add_button.clicked.connect(self.add_product)
        self.edit_button.clicked.connect(self.edit_product)
        self.delete_button.clicked.connect(self.delete_product)

    def refresh_table(self) -> None:
        products = self.inventory_service.get_all_products()
        self.table.setRowCount(len(products))

        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(product.sku))
            self.table.setItem(row, 1, QTableWidgetItem(product.name))
            self.table.setItem(row, 2, QTableWidgetItem(product.category))
            self.table.setItem(row, 3, QTableWidgetItem(str(product.quantity)))
            self.table.setItem(row, 4, QTableWidgetItem(
                f"{product.cost_price:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(
                f"{product.sell_price:.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(
                str(product.min_quantity)))

        self.table.resizeColumnsToContents()

    def get_selected_sku(self) -> str | None:
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return None

        item = self.table.item(selected_row, 0)
        if item is None:
            return None

        return item.text()

    def add_product(self) -> None:
        dialog = ProductDialog(parent=self)

        if dialog.exec():
            try:
                product = dialog.get_product()
                self.inventory_service.add_product(product)
                self.refresh_table()
            except ValueError as exc:
                QMessageBox.warning(self, "Error", str(exc))

    def edit_product(self) -> None:
        sku = self.get_selected_sku()
        if sku is None:
            QMessageBox.information(
                self, "No Selection", "Please select a product to edit.")
            return

        product = self.inventory_service.get_product_by_sku(sku)
        if product is None:
            QMessageBox.warning(
                self, "Error", "Selected product was not found.")
            return

        dialog = ProductDialog(product=product, parent=self)

        if dialog.exec():
            try:
                updated_product = dialog.get_product()
                self.inventory_service.update_product(sku, updated_product)
                self.refresh_table()
            except ValueError as exc:
                QMessageBox.warning(self, "Error", str(exc))

    def delete_product(self) -> None:
        sku = self.get_selected_sku()
        if sku is None:
            QMessageBox.information(
                self, "No Selection", "Please select a product to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete product with SKU '{sku}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.inventory_service.delete_product(sku)
                self.refresh_table()
            except ValueError as exc:
                QMessageBox.warning(self, "Error", str(exc))

    # def _load_table(self) -> None:
    #     products = self.inventory_service.get_all_products()
    #     self.table.setRowCount(len(products))

    #     for row, product in enumerate(products):
    #         self.table.setItem(row, 0, QTableWidgetItem(product.sku))
    #         self.table.setItem(row, 1, QTableWidgetItem(product.name))
    #         self.table.setItem(row, 2, QTableWidgetItem(product.category))
    #         self.table.setItem(row, 3, QTableWidgetItem(str(product.quantity)))
    #         self.table.setItem(row, 4, QTableWidgetItem(f"{product.cost_price:.2f}"))
    #         self.table.setItem(row, 5, QTableWidgetItem(f"{product.sell_price:.2f}"))
    #         self.table.setItem(row, 6, QTableWidgetItem(str(product.min_quantity)))
