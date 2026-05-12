from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QMessageBox,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from hardware_inventory.ui.sale_details_dialog import SaleDetailsDialog


class SalesTab(QWidget):
    def __init__(self, sales_service, inventory_service, on_sale_recorded=None):
        super().__init__()
        self.sales_service = sales_service
        self.inventory_service = inventory_service
        self.on_sale_recorded = on_sale_recorded

        self._build_ui()
        self._connect_signals()
        self.populate_products()
        self.refresh_sales_table()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.product_combo = QComboBox()

        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(100000)

        self.unit_price_input = QDoubleSpinBox()
        self.unit_price_input.setMinimum(0.0)
        self.unit_price_input.setMaximum(1000000.0)
        self.unit_price_input.setDecimals(2)

        self.sale_date_input = QDateEdit()
        self.sale_date_input.setCalendarPopup(True)
        self.sale_date_input.setDate(QDate.currentDate())

        self.add_item_button = QPushButton("Add Item")
        self.remove_item_button = QPushButton("Remove Selected Item")
        self.record_sale_button = QPushButton("Record Sale")
        self.view_sale_button = QPushButton("View Sale Details")
        self.total_label = QLabel("Grand Total: 0.00")

        form_layout.addRow("Product:", self.product_combo)
        form_layout.addRow("Quantity:", self.quantity_input)
        form_layout.addRow("Unit Price:", self.unit_price_input)
        form_layout.addRow("Sale Date:", self.sale_date_input)

        basket_buttons = QHBoxLayout()
        basket_buttons.addWidget(self.add_item_button)
        basket_buttons.addWidget(self.remove_item_button)
        basket_buttons.addStretch()
        basket_buttons.addWidget(self.total_label)
        basket_buttons.addWidget(self.record_sale_button)

        history_buttons = QHBoxLayout()
        history_buttons.addStretch()
        history_buttons.addWidget(self.view_sale_button)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels([
            "SKU",
            "Product Name",
            "Quantity",
            "Unit Price",
            "Line Total",
        ])

        self.cart_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.cart_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self.cart_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked)

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(4)
        self.sales_table.setHorizontalHeaderLabels([
            "Sale ID",
            "Date",
            "Total Items",
            "Grand Total",
        ])

        self.sales_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sales_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.sales_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(basket_buttons)
        main_layout.addWidget(QLabel("Current Basket"))
        main_layout.addWidget(self.cart_table)
        main_layout.addWidget(QLabel("Sale History"))
        main_layout.addWidget(self.sales_table)
        main_layout.addLayout(history_buttons)

        self.setLayout(main_layout)

    def _connect_signals(self) -> None:
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)
        self.add_item_button.clicked.connect(self.add_item_to_cart)
        self.remove_item_button.clicked.connect(self.remove_selected_item)
        self.record_sale_button.clicked.connect(self.record_sale)
        self.cart_table.itemChanged.connect(self.on_cart_item_changed)
        self.view_sale_button.clicked.connect(self.view_selected_sale)
        self.sales_table.itemDoubleClicked.connect(self.view_selected_sale)

    def populate_products(self) -> None:
        self.product_combo.clear()

        products = self.inventory_service.get_all_products()
        for product in products:
            self.product_combo.addItem(
                f"{product.sku} - {product.name}",
                product.sku,
            )

        self.on_product_changed()

    def on_product_changed(self) -> None:
        sku = self.product_combo.currentData()
        if not sku:
            return

        product = self.inventory_service.get_product_by_sku(sku)
        if product is not None:
            self.unit_price_input.setValue(product.sell_price)

    def add_item_to_cart(self) -> None:
        sku = self.product_combo.currentData()
        quantity = self.quantity_input.value()
        unit_price = self.unit_price_input.value()

        if not sku:
            QMessageBox.information(
                self, "Add Item", "Please select a product.")
            return

        product = self.inventory_service.get_product_by_sku(sku)
        if product is None:
            QMessageBox.warning(
                self, "Add Item", "Selected product was not found.")
            return

        for row in range(self.cart_table.rowCount()):
            sku_item = self.cart_table.item(row, 0)
            quantity_item = self.cart_table.item(row, 2)

            if sku_item is None or quantity_item is None:
                continue

            if sku_item.text().strip() == product.sku:
                current_quantity = int(float(quantity_item.text()))
                quantity_item.setText(str(current_quantity + quantity))
                return

        row = self.cart_table.rowCount()
        self.cart_table.insertRow(row)

        sku_item = QTableWidgetItem(product.sku)
        sku_item.setFlags(sku_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        name_item = QTableWidgetItem(product.name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        quantity_item = QTableWidgetItem(str(quantity))
        unit_price_item = QTableWidgetItem(f"{unit_price:.2f}")

        line_total = quantity * unit_price
        total_item = QTableWidgetItem(f"{line_total:.2f}")
        total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        self.cart_table.setItem(row, 0, sku_item)
        self.cart_table.setItem(row, 1, name_item)
        self.cart_table.setItem(row, 2, quantity_item)
        self.cart_table.setItem(row, 3, unit_price_item)
        self.cart_table.setItem(row, 4, total_item)

        self.update_cart_totals()

    def remove_selected_item(self) -> None:
        selected_rows = self.cart_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(
                self, "Remove Item", "Select a cart row first.")
            return

        row = selected_rows[0].row()
        self.cart_table.removeRow(row)
        self.update_cart_totals()

    def on_cart_item_changed(self, item: QTableWidgetItem) -> None:
        if item.column() not in (2, 3):
            return

        row = item.row()

        quantity_item = self.cart_table.item(row, 2)
        unit_price_item = self.cart_table.item(row, 3)
        total_item = self.cart_table.item(row, 4)

        if quantity_item is None or unit_price_item is None or total_item is None:
            return

        try:
            quantity = int(float(quantity_item.text()))
            unit_price = float(unit_price_item.text())

            if quantity <= 0:
                raise ValueError
            if unit_price < 0:
                raise ValueError

            line_total = quantity * unit_price
            total_item.setText(f"{line_total:.2f}")

            self.update_cart_totals()

        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Quantity must be greater than zero and price must be zero or more.",
            )

    def update_cart_totals(self) -> None:
        grand_total = 0.0

        for row in range(self.cart_table.rowCount()):
            item = self.cart_table.item(row, 4)
            if item is not None:
                try:
                    grand_total += float(item.text())
                except ValueError:
                    pass

        self.total_label.setText(f"Grand Total: {grand_total:.2f}")

    def collect_sale_lines(self) -> list[dict]:
        sale_lines = []

        for row in range(self.cart_table.rowCount()):
            sku_item = self.cart_table.item(row, 0)
            quantity_item = self.cart_table.item(row, 2)
            unit_price_item = self.cart_table.item(row, 3)

            if sku_item is None or quantity_item is None or unit_price_item is None:
                continue

            sale_lines.append({
                "sku": sku_item.text().strip(),
                "quantity": int(float(quantity_item.text())),
                "unit_price": float(unit_price_item.text()),
            })

        return sale_lines

    def record_sale(self) -> None:
        sale_lines = self.collect_sale_lines()
        if not sale_lines:
            QMessageBox.information(
                self, "Record Sale", "Add at least one item to the basket.")
            return

        sale_date = self.sale_date_input.date().toString("yyyy-MM-dd")

        try:
            sale = self.sales_service.record_sale(
                sale_lines=sale_lines,
                sale_date=sale_date,
            )

            QMessageBox.information(
                self,
                "Record Sale",
                f"Sale recorded successfully.\nSale ID: {sale.sale_id}",
            )

            self.cart_table.setRowCount(0)
            self.update_cart_totals()
            self.populate_products()
            self.refresh_sales_table()

            if self.on_sale_recorded is not None:
                self.on_sale_recorded()

        except Exception as exc:
            QMessageBox.critical(self, "Record Sale Failed", str(exc))

    def refresh_sales_table(self) -> None:
        sales = self.sales_service.get_all_sales()
        self.sales_table.setRowCount(len(sales))

        for row, sale in enumerate(sales):
            self.sales_table.setItem(row, 0, QTableWidgetItem(sale.sale_id))
            self.sales_table.setItem(row, 1, QTableWidgetItem(sale.sale_date))
            self.sales_table.setItem(
                row, 2, QTableWidgetItem(str(sale.total_items)))
            self.sales_table.setItem(
                row, 3, QTableWidgetItem(f"{sale.grand_total:.2f}"))

        self.sales_table.resizeColumnsToContents()

    def get_selected_sale_id(self) -> str | None:
        selected_rows = self.sales_table.selectionModel().selectedRows()
        if not selected_rows:
            return None

        row = selected_rows[0].row()
        sale_id_item = self.sales_table.item(row, 0)

        if sale_id_item is None:
            return None

        return sale_id_item.text().strip()

    def view_selected_sale(self) -> None:
        sale_id = self.get_selected_sale_id()
        if sale_id is None:
            QMessageBox.information(
                self, "Sale Details", "Please select a sale first.")
            return

        sale = self.sales_service.get_sale_by_id(sale_id)
        if sale is None:
            QMessageBox.warning(self, "Sale Details",
                                "Selected sale was not found.")
            return

        dialog = SaleDetailsDialog(sale, parent=self)
        dialog.exec()
