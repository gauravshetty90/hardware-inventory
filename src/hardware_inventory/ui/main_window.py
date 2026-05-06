from PySide6.QtWidgets import QMainWindow, QTabWidget

from hardware_inventory.services.inventory_service import InventoryService
from hardware_inventory.services.export_service import ExportService
from hardware_inventory.storage.json_store import JsonStore
from hardware_inventory.utils.paths import PRODUCTS_FILE, SALES_FILE
from hardware_inventory.ui.inventory_tab import InventoryTab

from hardware_inventory.services.sales_service import SalesService
from hardware_inventory.storage.sales_store import SalesStore
from hardware_inventory.ui.sales_tab import SalesTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hardware Inventory")
        self.resize(1100, 750)

        self.inventory_service = InventoryService(JsonStore(PRODUCTS_FILE))
        self.export_service = ExportService()
        self.sales_service = SalesService(
            SalesStore(SALES_FILE),
            self.inventory_service,
        )

        self.tabs = QTabWidget()

        self.inventory_tab = InventoryTab(
            inventory_service=self.inventory_service,
            export_service=self.export_service,
        )

        self.sales_tab = SalesTab(
            sales_service=self.sales_service,
            inventory_service=self.inventory_service,
            on_sale_recorded=self.handle_sale_recorded,
        )

        self.tabs.addTab(self.inventory_tab, "Inventory")
        self.tabs.addTab(self.sales_tab, "Sales")

        self.setCentralWidget(self.tabs)

    def handle_sale_recorded(self) -> None:
        self.inventory_tab.refresh_table()
