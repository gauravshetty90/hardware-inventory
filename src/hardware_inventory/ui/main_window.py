from pathlib import Path

from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
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
from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtGui import QColor, QBrush, QFont

from hardware_inventory.services.inventory_service import InventoryService
from hardware_inventory.services.export_service import ExportService
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
        self.export_service = ExportService()


    def apply_stock_highlighting_to_quantity_cell(
        self,
        item: QTableWidgetItem,
        quantity: int | float | None,
        min_quantity: int | float | None,
    ) -> None:
        if quantity is None:
            return

        if quantity == 0:
            item.setBackground(QBrush(QColor("#f8d7da")))
            item.setForeground(QBrush(QColor("#842029")))
        elif min_quantity is not None and quantity > 0 and quantity <= min_quantity:
            item.setBackground(QBrush(QColor("#fff3cd")))
            item.setForeground(QBrush(QColor("#997404")))

    def _build_ui(self) -> None:
        central = QWidget()

        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        filter_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Product")
        self.edit_button = QPushButton("Edit Product")
        self.delete_button = QPushButton("Delete Product")
        self.export_button = QPushButton("Export CSV")
        self.import_button = QPushButton("Import CSV")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.import_button)

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
        self.export_button.clicked.connect(self.export_products)
        self.import_button.clicked.connect(self.import_products)

        self.search_input.textChanged.connect(self.apply_filters)
        self.category_filter.currentTextChanged.connect(self.apply_filters)
        self.low_stock_checkbox.toggled.connect(self.on_low_stock_toggled)
        self.out_of_stock_checkbox.toggled.connect(
            self.on_out_of_stock_toggled)

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
            quantity = product_dict.get("quantity")
            min_quantity = product_dict.get("min_quantity")

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
                if column_name == "quantity":
                    self.apply_stock_highlighting_to_quantity_cell(
                        item,
                        quantity,
                        min_quantity,
                    )

                self.table.setItem(row_index, col_index, item)

        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)

        self.populate_category_filter()
        self.apply_filters()

    def apply_filters(self) -> None:
        query = self.normalize_text(self.search_input.text())
        selected_category = self.category_filter.currentText()
        low_stock_only = self.low_stock_checkbox.isChecked()
        out_of_stock_only = self.out_of_stock_checkbox.isChecked()

        self.table.clearSelection()

        category_col = self.columns.index(
            "category") if "category" in self.columns else None
        quantity_col = self.columns.index(
            "quantity") if "quantity" in self.columns else None
        min_quantity_col = self.columns.index(
            "min_quantity") if "min_quantity" in self.columns else None

        for row in range(self.table.rowCount()):
            row_values = []

            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_values.append(item.text() if item else "")

            normalized_row_text = self.normalize_text(" ".join(row_values))

            category = ""
            if category_col is not None:
                item = self.table.item(row, category_col)
                category = item.text() if item else ""

            quantity = 0
            if quantity_col is not None:
                item = self.table.item(row, quantity_col)
                try:
                    quantity = int(float(item.text())) if item else 0
                except ValueError:
                    quantity = 0

            min_quantity = 0
            if min_quantity_col is not None:
                item = self.table.item(row, min_quantity_col)
                try:
                    min_quantity = int(float(item.text())) if item else 0
                except ValueError:
                    min_quantity = 0

            matches_search = not query or query in normalized_row_text
            matches_category = (
                selected_category == "All"
                or not selected_category
                or category == selected_category
            )
            matches_low_stock = (
                not low_stock_only
                or (
                    quantity_col is not None
                    and min_quantity_col is not None
                    and quantity > 0
                    and quantity <= min_quantity
                )
            )
            matches_out_of_stock = (
                not out_of_stock_only
                or (quantity_col is not None and quantity == 0)
            )

            show_row = (
                matches_search
                and matches_category
                and matches_low_stock
                and matches_out_of_stock
            )

            self.table.setRowHidden(row, not show_row)

    def populate_category_filter(self) -> None:
        current_value = self.category_filter.currentText()

        products = self.inventory_service.get_all_products()
        product_dicts = [product.to_dict() for product in products]

        categories = sorted({
            str(product_dict.get("category", "")).strip()
            for product_dict in product_dicts
            if str(product_dict.get("category", "")).strip()
        })

        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem("All")
        self.category_filter.addItems(categories)

        index = self.category_filter.findText(current_value)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)
        else:
            self.category_filter.setCurrentIndex(0)

        self.category_filter.blockSignals(False)

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

    def on_low_stock_toggled(self, checked: bool) -> None:
        if checked:
            blocker = QSignalBlocker(self.out_of_stock_checkbox)
            self.out_of_stock_checkbox.setChecked(False)
            del blocker

        self.apply_filters()

    def on_out_of_stock_toggled(self, checked: bool) -> None:
        if checked:
            blocker = QSignalBlocker(self.low_stock_checkbox)
            self.low_stock_checkbox.setChecked(False)
            del blocker

        self.apply_filters()

    def export_products(self) -> None:
        products = self.inventory_service.get_all_products()
        product_dicts = [product.to_dict() for product in products]

        if not product_dicts:
            QMessageBox.information(
                self, "Export CSV", "There are no products to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Products to CSV",
            "inventory_export.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return
        
        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        try:
            self.export_service.export_products_to_csv(
                product_dicts, file_path)
            QMessageBox.information(
                self,
                "Export CSV",
                f"Products exported successfully to:\n{file_path}",
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Export CSV",
                f"Failed to export products:\n{exc}",
            )

    def import_products(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Products from CSV",
            "",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            imported_products = self.export_service.import_products_from_csv(
                file_path)

            if not imported_products:
                QMessageBox.warning(
                    self,
                    "Import CSV",
                    "The selected CSV file contains no product rows.",
                )
                return

            self.inventory_service.replace_all_products(imported_products)
            self.refresh_table()

            QMessageBox.information(
                self,
                "Import CSV",
                f"Imported {len(imported_products)} products successfully.",
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Import CSV",
                f"Failed to import products:\n{exc}",
            )
