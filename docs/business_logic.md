# 🧠 Business Logic Specification – Retail Management System

This document details the business logic flow for the offline-first Retail Management System. Update this file as business rules evolve or new features are added.

---

## 👤 User Roles & Permissions

### Admin
- Create product entries, manage users, assign roles.
- Initiate order requests (internal shopping carts) to be processed by subordinates.
- Full access to reporting, analytics, and accounting.

### Manager
- Similar to Admin but limited to their store/branch.
- Can initiate order requests.
- Can approve purchases or sales if permission granted.

### Assistant Manager
- Process assigned order requests into actual sales.
- View inventory, assist in purchases, handle expenses.

### Inventory Assistant
- Handle inventory updates, restocks, reorder alerts, same task with Sales Assistant.

### Sales Assistant
- Register walk-in sales and scan products.
- Cannot modify inventory or view reports.

---

## 🧾 Order Request to Sale Workflow

1. **Order Request Creation**
   - Admin or Manager creates an order request:
     - Selects customer or walk-in
     - Adds items with quantity
     - Assigns to staff (Assistant Manager or Sales Assistant)
     - Optionally sets discount or notes
2. **Request Processing**
   - Assigned staff sees pending request
   - Can approve, modify (quantity/discount), or reject
   - Once approved, processed as a Sale:
     - Generates receipt
     - Updates product quantities
3. **Audit Trail**
   - All processed requests are linked to the originating Admin/Manager for audit

---

## 🔄 Offline-First & Sync Logic
- Each device maintains its own SQLite DB.
- Every write operation is time-stamped and queued for sync.
- On LAN availability:
  - Devices push unsynced records to the Master Node
  - Master aggregates updates and broadcasts critical deltas (e.g., updated stock levels)
- Sync conflict resolution based on latest timestamp or Master priority.

---

## 💳 Accounting Flow
- Expenses tracked by any role with access (Admin, Manager, Assistant Manager)
- Revenue automatically logged per sale
- Daily financial summary auto-calculated:
  - Opening stock value
  - Sales revenue
  - Expenses
  - Closing balance

---

## 📋 Additional Logic Modules

### Inventory Reordering
- When stock < reorder threshold, system suggests reorder
- Can generate a "Reorder Request" sent to Manager for confirmation

### Barcode Handling
- System generates barcodes for each product (based on SKU)
- Can be printed or scanned via camera

### Customer Loyalty
- Points awarded based on sale amount
- Configurable threshold (e.g., 1 point per ₦1000 spent)

### Reporting
- Sales by day/month
- Best-selling products
- Stock aging
- Sales by staff
- Pending order requests

---

*Update this file as business logic evolves or new modules are added.* 