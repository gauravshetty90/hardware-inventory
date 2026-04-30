# Hardware Inventory

A desktop inventory management application built with PySide6. The current implementation focuses on product inventory management, CSV import/export, filtering, and stock-aware table views, and the project structure has already been prepared for a future sales module based on a second tab in the UI.

## What the project does

The application manages a catalog of hardware products with fields such as SKU, name, category, quantity, cost price, sell price, minimum quantity, and optional extra attributes that can appear dynamically in the table.

At the moment, the app supports:

- Adding a new product through a dialog-driven form.
- Editing an existing product.
- Deleting one or more products from the table.
- Searching and filtering inventory records by text, category, low stock, and out-of-stock status.
- Importing product data from CSV files.
- Exporting the current inventory to CSV files.
- Highlighting low-stock and out-of-stock quantities in the table for faster visual review.

## Current scope

The project currently centers on the **Inventory** area of the application. A **Sales** area has been planned and some supporting files have been added, but sales logic and transaction workflows are not implemented yet.

The intended direction is a tab-based desktop application where inventory and sales live in separate UI sections. `QTabWidget` is designed for this style of multi-page desktop interface, where each tab hosts a different widget and only the active page is shown at a time.

## How the app works

### Inventory workflow

The current inventory workflow is centered on CRUD-style product management:

1. Products are loaded from persistent storage through the inventory service.
2. The main table is rebuilt from product data whenever records change.
3. Filters are applied on top of the current table contents.
4. CSV import can replace the current inventory dataset.
5. CSV export writes the visible inventory data to a user-chosen file path.

This design separates UI actions from business logic and persistence, which makes the code easier to extend as the project grows.

### Filtering and display

The main table uses a `QTableWidget` and supports row-based selection, sorting, dynamic columns, and multiple filters. `QTableWidget` is appropriate when the application directly creates and manages table items in code rather than using a full custom model/view layer.

The table refresh logic converts product objects into dictionaries, determines any additional non-core fields dynamically, rebuilds the headers, repopulates all rows, reapplies visual formatting, and then reapplies active filters. This allows the table to adapt if products contain additional attributes beyond the base schema.

### Import and export

CSV import and export are user-driven through file dialogs. In PySide6, `QFileDialog.getOpenFileName()` is the standard way to ask the user for a source file, while `QFileDialog.getSaveFileName()` is used to ask the user where to save an exported file.

The current flow is:

- **Import CSV**: choose a source file, parse product rows, replace the existing inventory, refresh the table.
- **Export CSV**: choose a destination file, serialize the current inventory, and write it as a CSV file.

## Project structure

The project follows a `src/` layout, which is a good fit for larger Python applications because it keeps importable application code under `src/` and helps avoid accidental import-path issues during development.

A likely structure for the project is:

```text
hardware-inventory/
├── src/
│   └── hardware_inventory/
│       ├── main.py
│       ├── models/
│       │   └── product.py
│       ├── services/
│       │   ├── inventory_service.py
│       │   └── export_service.py
│       ├── storage/
│       │   └── json_store.py
│       ├── ui/
│       │   ├── main_window.py
│       │   └── product_dialog.py
│       └── utils/
│           └── paths.py
├── data/
├── tests/
└── README.md
```

If new sales-related files have already been added, they will naturally fit under the same `models/`, `services/`, `storage/`, and `ui/` folders.

## Architecture

The application is organized around a layered structure:

| Layer       | Responsibility                                                                             |
| ----------- | ------------------------------------------------------------------------------------------ |
| `ui/`       | Windows, dialogs, buttons, tables, filters, and user interaction                           |
| `services/` | Business rules such as add, update, delete, import replacement, and future sales recording |
| `storage/`  | Reading and writing persisted data                                                         |
| `models/`   | Domain objects such as `Product` and the planned `Sale`                                    |
| `utils/`    | Shared paths and helper utilities                                                          |

This separation is useful because inventory systems often grow from a simple CRUD app into a broader operations tool, and clean boundaries make that evolution safer.

## Main components

### `main.py`

Application entry point. This file starts the Qt application and opens the main window.

### `ui/main_window.py`

The central desktop UI. Right now it contains the inventory table, toolbar buttons, search input, category filter, stock filters, and CSV import/export actions. As the project evolves, this file can either remain the top-level shell or become the host for a tab widget that contains dedicated inventory and sales pages.

### `ui/product_dialog.py`

Handles product entry and editing through a modal dialog, keeping data-entry logic separate from the table page.

### `services/inventory_service.py`

Encapsulates product-related business logic such as loading all products, retrieving a product by SKU, adding products, updating products, deleting products, and replacing the full inventory after a CSV import.

### `services/export_service.py`

Owns CSV-specific import/export logic so that file-format handling stays outside the main window code. This keeps the UI thinner and makes the CSV workflow easier to test and extend.

### `storage/json_store.py`

Handles persistent storage of the application’s internal product dataset. Even though the user-facing import/export feature uses CSV, internal persistence can still remain JSON; these concerns do not need to use the same format.

### `utils/paths.py`

Central place for file path constants such as the persistent products data file.

## Data model

The current core entity is the product. The important fields in the current inventory workflow are:

- `sku`
- `name`
- `category`
- `quantity`
- `cost_price`
- `sell_price`
- `min_quantity`

The table also supports extra fields beyond the core schema by detecting additional keys found in product dictionaries and appending them as dynamic columns.

## Planned sales module

The project is being prepared for a second tab focused on **sales transactions** rather than inventory master data. This is the right direction architecturally because a sale should be treated as a separate transaction record instead of just another product attribute.

A good first sales record would include:

- sale ID
- product SKU
- product name snapshot
- quantity sold
- unit sale price
- sale date
- total amount

This approach preserves transaction history even if product names or prices change later, which is a standard design recommendation in inventory and point-of-sale systems.

### Proposed sales architecture

The next phase of the project can introduce:

- `ui/inventory_tab.py`
- `ui/sales_tab.py`
- `models/sale.py`
- `services/sales_service.py`
- `storage/sales_store.py`

The top-level main window can then host both pages inside a `QTabWidget`, with one tab for inventory management and one tab for sales operations.

## Typical user flow

### Inventory management

1. Start the application.
2. Review inventory in the main table.
3. Add, edit, or delete products.
4. Search by free text or filter by category and stock state.
5. Export current product data to CSV when needed.
6. Import a CSV file to replace the current dataset.

### Future sales flow

1. Open the Sales tab.
2. Select a product.
3. Enter quantity, date, and sale amount.
4. Record the sale.
5. Reduce inventory automatically.
6. View sales history and totals.

## Running the project

Because the project uses a `src/` layout and the package lives under `src/hardware_inventory`, it is typically run from the repository root using a module path such as `hardware_inventory.main`.

Example:

```bash
cd /path/to/hardware-inventory
source .venv/bin/activate
PYTHONPATH=src python -m hardware_inventory.main
```

Using the package module path is appropriate when `main.py` is inside the `hardware_inventory` package rather than directly under `src/`.

## Design notes

A few design choices in the current codebase are especially helpful:

- **Service-based logic** keeps the UI layer smaller.
- **CSV import/export isolated in a dedicated service** avoids file-format logic spreading across the app.
- **Dynamic columns** make the inventory table more flexible.
- **`src/` layout** supports cleaner imports and better project organization for growth.
