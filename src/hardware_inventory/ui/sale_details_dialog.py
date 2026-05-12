from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from hardware_inventory.models.sale import Sale


class SaleDetailsDialog(QDialog):
    def __init__(self, sale: Sale, parent=None):
        super().__init__(parent)
        self.sale = sale

        self.setWindowTitle(f"Sale Details - {sale.sale_id}")
        self.resize(800, 500)

        self._build_ui()
        self._load_data()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout()
        summary_layout = QFormLayout()

        self.sale_id_label = QLabel()
        self.sale_date_label = QLabel()
        self.total_items_label = QLabel()
        self.grand_total_label = QLabel()

        summary_layout.addRow("Sale ID:", self.sale_id_label)
        summary_layout.addRow("Sale Date:", self.sale_date_label)
        summary_layout.addRow("Total Items:", self.total_items_label)
        summary_layout.addRow("Grand Total:", self.grand_total_label)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "SKU",
            "Product Name",
            "Quantity",
            "Unit Price",
            "Line Total",
        ])
        self.items_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        button_row = QHBoxLayout()
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)

        button_row.addStretch()
        button_row.addWidget(self.close_button)

        main_layout.addLayout(summary_layout)
        main_layout.addWidget(self.items_table)
        main_layout.addLayout(button_row)

        self.setLayout(main_layout)

    def _load_data(self) -> None:
        self.sale_id_label.setText(self.sale.sale_id)
        self.sale_date_label.setText(self.sale.sale_date)
        self.total_items_label.setText(str(self.sale.total_items))
        self.grand_total_label.setText(f"{self.sale.grand_total:.2f}")

        self.items_table.setRowCount(len(self.sale.items))

        for row, item in enumerate(self.sale.items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item.product_sku))
            self.items_table.setItem(row, 1, QTableWidgetItem(item.product_name))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item.quantity)))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item.unit_price:.2f}"))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"{item.line_total:.2f}"))

        self.items_table.resizeColumnsToContents()