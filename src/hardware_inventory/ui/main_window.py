from pathlib import Path

from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush, QFont

from hardware_inventory.services.inventory_service import InventoryService
from hardware_inventory.storage.json_store import JsonStore
from hardware_inventory.utils.paths import PRODUCTS_FILE
from hardware_inventory.ui.product_dialog import ProductDialog


class MainWindow(QMainWindow):

    CORE_FIELDS = [
        "sku",
        "name",
        "category",
        "quantity",
        "cost_price",
        "sell_price",
        "min_quantity",
    ]

    def format_column_label(self, key: str) -> str:
        return key.replace("_", " ").title()

    def is_numeric_value(self, value) -> bool:
        return isinstance(value, (int, float))

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hardware Inventory")
        self.resize(1000, 700)

        self.inventory_service = InventoryService(JsonStore(PRODUCTS_FILE))

        self._build_ui()
        # self._load_table()
        self._connect_signals()
        self.columns = []
        self.refresh_table()
        

    def _build_ui(self) -> None:
        central = QWidget()

        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        filter_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Product")
        self.edit_button = QPushButton("Edit Product")
        self.delete_button = QPushButton("Delete Product")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search inventory")

        self.category_filter = QComboBox()
        self.category_filter.addItem("All")

        self.low_stock_checkbox = QCheckBox("Low stock only")
        self.out_of_stock_checkbox = QCheckBox("Out of stock only")

        filter_layout.addWidget(self.search_input, 2)
        filter_layout.addWidget(self.category_filter, 1)
        filter_layout.addWidget(self.low_stock_checkbox)
        filter_layout.addWidget(self.out_of_stock_checkbox)

        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setSortingEnabled(True)

        main_layout.addLayout(button_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.table)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def _connect_signals(self) -> None:
        self.add_button.clicked.connect(self.add_product)
        self.edit_button.clicked.connect(self.edit_product)
        self.delete_button.clicked.connect(self.delete_product)

        self.search_input.textChanged.connect(self.apply_filters)
        self.category_filter.currentTextChanged.connect(self.apply_filters)
        self.low_stock_checkbox.toggled.connect(self.apply_filters)
        self.out_of_stock_checkbox.toggled.connect(self.apply_filters)

    def normalize_text(self, text: str) -> str:
        return "".join(ch.lower() for ch in text if ch.isalnum())

    def refresh_table(self) -> None:
        products = self.inventory_service.get_all_products()
        product_dicts = [product.to_dict() for product in products]

        extra_fields = []
        seen_extra_fields = set()

        for product_dict in product_dicts:
            for key in product_dict.keys():
                if key not in self.CORE_FIELDS and key not in seen_extra_fields:
                    seen_extra_fields.add(key)
                    extra_fields.append(key)

        self.columns = self.CORE_FIELDS + extra_fields

        self.table.setSortingEnabled(False)
        self.table.clear()
        self.table.setColumnCount(len(self.columns))
        self.table.setRowCount(len(product_dicts))
        self.table.setHorizontalHeaderLabels(
            [self.format_column_label(col) for col in self.columns]
        )

        header_font = QFont()
        header_font.setBold(True)

        for col_index, column_name in enumerate(self.columns):
            header_item = self.table.horizontalHeaderItem(col_index)
            if header_item is not None:
                header_item.setFont(header_font)

        for row_index, product_dict in enumerate(product_dicts):
            for col_index, column_name in enumerate(self.columns):
                value = product_dict.get(column_name, "")
                display_value = "" if value is None else str(value)

                item = QTableWidgetItem(display_value)

                if self.is_numeric_value(value):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                    item.setForeground(QBrush(QColor("#0b5f8a")))
                else:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                    )

                self.table.setItem(row_index, col_index, item)

        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)

        self.apply_filters()

    def apply_filters(self) -> None:
        query = self.normalize_text(self.search_input.text())
        selected_category = self.category_filter.currentText()
        low_stock_only = self.low_stock_checkbox.isChecked()
        out_of_stock_only = self.out_of_stock_checkbox.isChecked()

        self.table.clearSelection()

        for row in range(self.table.rowCount()):
            sku_item = self.table.item(row, 0)
            name_item = self.table.item(row, 1)
            category_item = self.table.item(row, 2)
            quantity_item = self.table.item(row, 3)
            cost_item = self.table.item(row, 4)
            sell_item = self.table.item(row, 5)
            min_qty_item = self.table.item(row, 6)

            sku = sku_item.text() if sku_item else ""
            name = name_item.text() if name_item else ""
            category = category_item.text() if category_item else ""
            quantity = int(quantity_item.text()) if quantity_item else 0
            cost_price = cost_item.text() if cost_item else ""
            sell_price = sell_item.text() if sell_item else ""
            min_quantity = int(min_qty_item.text()) if min_qty_item else 0

            searchable_text = " ".join([
                sku,
                name,
                category,
                str(quantity),
                cost_price,
                sell_price,
                str(min_quantity),
            ])
            normalized_row_text = self.normalize_text(searchable_text)

            matches_search = not query or query in normalized_row_text
            matches_category = selected_category == "All" or category == selected_category
            matches_low_stock = not low_stock_only or quantity <= min_quantity
            matches_out_of_stock = not out_of_stock_only or quantity == 0

            show_row = (
                matches_search
                and matches_category
                and matches_low_stock
                and matches_out_of_stock
            )

            self.table.setRowHidden(row, not show_row)

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
