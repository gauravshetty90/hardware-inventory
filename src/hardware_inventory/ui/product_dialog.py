from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from hardware_inventory.models.product import Product


class ProductDialog(QDialog):
    def __init__(self, product: Product | None = None, parent=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle(
            "Add Product" if product is None else "Edit Product")

        self.sku_input = QLineEdit()
        self.name_input = QLineEdit()

        self.category_input = QComboBox()
        self.category_input.addItems([
            "Hand Tools",
            "Power Tools",
            "Fasteners",
            "Measuring Tools",
            "Paint",
            "Safety",
            "Electrical",
            "Plumbing",
            "Other",
        ])
        self.category_input.setEditable(True)

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 100000)

        self.cost_price_input = QDoubleSpinBox()
        self.cost_price_input.setRange(0, 1000000)
        self.cost_price_input.setDecimals(2)

        self.sell_price_input = QDoubleSpinBox()
        self.sell_price_input.setRange(0, 1000000)
        self.sell_price_input.setDecimals(2)

        self.min_quantity_input = QSpinBox()
        self.min_quantity_input.setRange(0, 100000)

        form_layout = QFormLayout()
        form_layout.addRow("SKU:", self.sku_input)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Category:", self.category_input)
        form_layout.addRow("Quantity:", self.quantity_input)
        form_layout.addRow("Cost Price:", self.cost_price_input)
        form_layout.addRow("Sell Price:", self.sell_price_input)
        form_layout.addRow("Min Quantity:", self.min_quantity_input)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self._handle_accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        if self.product is not None:
            self._load_product_data()

    def _load_product_data(self) -> None:
        product = self.product
        if product is None:
            return

        self.sku_input.setText(product.sku)
        self.name_input.setText(product.name)
        self.category_input.setCurrentText(product.category)
        self.quantity_input.setValue(product.quantity)
        self.cost_price_input.setValue(product.cost_price)
        self.sell_price_input.setValue(product.sell_price)
        self.min_quantity_input.setValue(product.min_quantity)

    def _handle_accept(self) -> None:
        if not self.sku_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "SKU is required.")
            return

        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            return

        self.accept()

    def get_product(self) -> Product:
        return Product(
            sku=self.sku_input.text().strip(),
            name=self.name_input.text().strip(),
            category=self.category_input.currentText().strip(),
            quantity=self.quantity_input.value(),
            cost_price=self.cost_price_input.value(),
            sell_price=self.sell_price_input.value(),
            min_quantity=self.min_quantity_input.value(),
        )
