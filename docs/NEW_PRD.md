# 📝 Retail Management System – Product Requirements Document (PRD)

## 1. Executive Summary

The Retail Management System (RMS) is a comprehensive, offline-first desktop application for small and medium retail businesses. Built for Windows, it streamlines inventory, sales, supplier, and user management, supporting multi-role access and robust offline/online synchronization. The system is designed for reliability, ease of use, and extensibility, with a modern UI and secure, modular backend.

---

## 2. System Architecture

- **Frontend:** Flutter (Windows Desktop)
- **Backend:** Flask (Python REST API + WebSocket)
- **Database:** SQLite (local, per device)
- **Sync:** LAN-based, master-client model
- **Installer:** Bundled Windows executable (Inno Setup/NSIS)

### High-Level Architecture

```
[User Device]
  ├─ Flutter UI (Desktop App)
  ├─ Embedded Flask Backend (auto-starts)
  └─ SQLite DB (local)
      │
      └─ LAN Sync (WebSocket/REST) → [Master Node]
```

- On launch, the app checks/starts the backend, connects to the local DB, and syncs with the master node if available.
- All features work offline; sync resumes when LAN is available.

---

## 3. Feature List & Workflows

### 3.1 User & Role Management
- **Roles:** Admin, Manager, Assistant Manager, Inventory Assistant, Sales Assistant
- **Workflow:**
  1. Admin creates users and assigns roles.
  2. Users log in with username/password.
  3. Access is restricted by role (see permissions matrix).
  4. Device ID logic ensures only one primary device per user (except Admin).

### 3.2 Product & Inventory Management
- **Workflow:**
  1. User (with permission) adds/edits products (name, SKU, category, price, stock).
  2. Inventory Assistant logs new stock via supplier and invoice number.
  3. System prevents duplicate invoice numbers per supplier.
  4. Stock levels update in real time; reorder alerts trigger as needed.

### 3.3 Sales & POS
- **Workflow:**
  1. Sales Assistant logs in and opens POS screen.
  2. Products are added to cart via search/barcode.
  3. Discounts, split payments, and notes can be added.
  4. Order is completed, receipt generated, and stock updated.
  5. Orders can be held, resumed, or auto-expire after 1 hour.

### 3.4 Supplier Management
- **Workflow:**
  1. User adds/edits suppliers (name, contact, etc.).
  2. Supplies are tracked by supplier and invoice number.
  3. System validates uniqueness and links supplies to inventory.

### 3.5 Reporting & Analytics
- **Workflow:**
  1. User selects report type (sales, inventory, aging, etc.).
  2. Filters by date, product, or category.
  3. Exports data as CSV or PDF.

### 3.6 Sync & Offline Support
- **Workflow:**
  1. All actions are logged locally.
  2. When LAN is available, devices sync with the master node.
  3. Conflict resolution uses timestamps (last-writer-wins).

### 3.7 Packaging & Deployment
- **Workflow:**
  1. Installer bundles Flutter frontend, Flask backend, and SQLite DB.
  2. On install, all components are set up for auto-start.
  3. User launches a single executable; backend starts in background.

---

## 4. UI/UX Specification

### 4.1 High-Level Screen Descriptions
- **Login:** Username/password, role-based redirect.
- **Dashboard:** KPIs, quick actions, alerts, role-specific widgets.
- **POS:** Product search, cart, payment, receipt, order hold/cancel.
- **Product Management:** List, add/edit/delete, filter, barcode.
- **Inventory Intake:** Supplier selection, invoice, batch entry.
- **Orders:** List, filter, detail, status update.
- **Suppliers:** List, add/edit/delete, contact info.
- **Reports:** Sales, inventory, export options.
- **Settings:** Device ID, user profile, system settings.

### 4.2 Wireframes (Textual)
- **Navigation:** Persistent left sidebar (Dashboard, POS, Products, Inventory, Orders, Suppliers, Reports, Settings)
- **Top Bar:** User info, sync status, logout
- **Modals:** For add/edit actions, animated transitions
- **Responsive:** Minimum 1024x768, touch/mouse optimized

### 4.3 UX Notes
- Form validation, error states, light/dark mode, auto-lock after inactivity
- Real-time updates via WebSocket

---

## 5. Database & API Overview

### 5.1 Key Tables (SQLite)
- `users` (id, username, password_hash, role_id, ...)
- `roles` (id, name, ...)
- `products` (id, name, sku, category_id, ...)
- `suppliers` (id, name, contact, ...)
- `inventory` (id, product_id, quantity, ...)
- `orders` (id, status, total_amount, cashier_id, ...)
- `order_items` (id, order_id, product_id, quantity, price, ...)
- `activity_logs`, `device_logs`, etc.

### 5.2 Main API Endpoints (Sample)
- `POST /api/login` – Authenticate user
- `GET /api/products` – List products
- `POST /api/orders` – Create order
- `GET /api/orders` – List orders
- `POST /api/inventory` – Add inventory
- `GET /api/reports/sales` – Sales report
- `POST /api/suppliers` – Add supplier
- `GET /api/suppliers` – List suppliers
- `POST /api/sync` – Sync data with master

---

## 6. Packaging & Deployment

- **Installer:** Bundled using Inno Setup or NSIS
- **Contents:**
  - Flutter Windows executable
  - Flask backend (compiled with PyInstaller)
  - SQLite DB (with initial schema)
  - Auto-start script for backend
- **Behavior:**
  - Single-click install
  - On launch, backend starts automatically
  - LAN sync enabled by default
  - No internet required for core features

---

## 7. Appendix

### 7.1 Glossary
- **Master Node:** Primary device holding authoritative data
- **Sync Client:** Device syncing with master
- **POS:** Point-of-Sale
- **SKU:** Stock Keeping Unit

### 7.2 Future Enhancements
- Cloud backup & restore
- Mobile companion app
- Multi-store/branch support
- Loyalty program
- Advanced analytics & forecasting

---

*This PRD is intended for stakeholder review and as a foundation for design, development, and deployment of the Retail Management System.* 