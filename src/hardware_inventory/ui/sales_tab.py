from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


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

        self.record_button = QPushButton("Record Sale")

        form_layout.addRow("Product:", self.product_combo)
        form_layout.addRow("Quantity:", self.quantity_input)
        form_layout.addRow("Unit Price:", self.unit_price_input)
        form_layout.addRow("Sale Date:", self.sale_date_input)

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7)
        self.sales_table.setHorizontalHeaderLabels([
            "Sale ID",
            "Date",
            "SKU",
            "Product Name",
            "Quantity",
            "Unit Price",
            "Total Amount",
        ])

        button_row = QHBoxLayout()
        button_row.addWidget(self.record_button)
        button_row.addStretch()

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_row)
        main_layout.addWidget(self.sales_table)

        self.setLayout(main_layout)

    def _connect_signals(self) -> None:
        self.record_button.clicked.connect(self.record_sale)
        self.product_combo.currentIndexChanged.connect(self.on_product_changed)

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

    def record_sale(self) -> None:
        sku = self.product_combo.currentData()
        quantity = self.quantity_input.value()
        unit_price = self.unit_price_input.value()
        sale_date = self.sale_date_input.date().toString("yyyy-MM-dd")

        if not sku:
            QMessageBox.information(self, "Record Sale", "Please select a product.")
            return

        try:
            self.sales_service.record_sale(
                product_sku=sku,
                quantity=quantity,
                unit_price=unit_price,
                sale_date=sale_date,
            )

            QMessageBox.information(self, "Record Sale", "Sale recorded successfully.")
            self.refresh_sales_table()
            self.populate_products()

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
            self.sales_table.setItem(row, 2, QTableWidgetItem(sale.product_sku))
            self.sales_table.setItem(row, 3, QTableWidgetItem(sale.product_name))
            self.sales_table.setItem(row, 4, QTableWidgetItem(str(sale.quantity)))
            self.sales_table.setItem(row, 5, QTableWidgetItem(f"{sale.unit_price:.2f}"))
            self.sales_table.setItem(row, 6, QTableWidgetItem(f"{sale.total_amount:.2f}"))

        self.sales_table.resizeColumnsToContents()