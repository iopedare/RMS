# 🛍️ Retail Management System - Product Requirements Document (PRD)

## 📘 Overview

A comprehensive offline-first Retail Management System designed for Windows Desktop, built with **Flutter (frontend)** and **Flask (backend)**. The system supports advanced inventory control with batch tracking, enhanced POS operations with discounts and loyalty, comprehensive reporting with profit/loss analytics, supplier management, and administrative functionalities with embedded backend architecture.

---

## ⚙️ Technical Architecture

### 🧱 Tech Stack
- **Frontend**: Flutter Desktop (Windows)
- **Backend**: Flask + Flask-SocketIO (embedded)
- **Database**: SQLite (local per device, sync-capable)
- **Communication**: WebSocket + REST API over LAN
- **Deployment**: Windows Executable with embedded server
- **Installation**: Bundled installer using Inno Setup or similar

### 🔧 Embedded System Behavior
- On Windows app launch:
  - Starts Flask + Flask-SocketIO backend on `localhost:5000`
  - Launches Flutter frontend (desktop app)
  - WebSocket connects all terminals on LAN
  - Real-time sync initiated automatically

### 🖥️ Master-Client Architecture
- **Master Node**: Primary cashier PC (server)
- **Sync Clients**: All other devices connect to Master
- **Failover**: If Master PC shuts down, fallback client becomes new Master
- **Offline Mode**: Master handles data consistency and conflict resolution

---

## 🧠 User Roles & Access Control

### 👥 Role Definitions

| Role | Access Level | Permissions |
|------|--------------|-------------|
| **Admin** | Full Access | User management, device settings, inventory control, supplier management, all reports, discount management, customer loyalty management |
| **Manager** | High Access | Order approvals, cashier assignment, password resets, view reports, profit/loss analytics, customer analytics, apply discounts |
| **Assistant Manager** | Medium Access | Dashboard, POS, Inventory management, batch tracking, basic reporting |
| **Inventory Assistant** | Focused Access | Goods receiving, stock updates, batch management, expiry tracking, POS access, supplier management |
| **Sales Assistant** | Limited Access | POS operations, apply pre-configured discounts, customer lookup |

### 🔐 Authentication & Security
- **Username-based login** (no email required)
- Username is immutable
- **Single-device login** enforcement (except Admin)
- Admin can override multi-device login
- **Device ID logic** with primary/backup role switching
- Session timeout and logout tracking

---

## 🚀 Core Features (MVP)

### 1. 🏪 Enhanced Point of Sale (POS)
- **Product Search**: By name, barcode, or SKU with instant search
- **Barcode Scanning**: Integrated barcode scanner support for quick product addition
- **Cart Management**: Add/remove items, quantity adjustment with real-time calculations
- **Advanced Discount Engine**: 
  - Percentage and fixed amount discounts
  - Product-specific, category-wide, or cart-wide discounts
  - Manager approval required for discounts above threshold
  - Seasonal and promotional discount campaigns
- **Customer Loyalty Program**:
  - Customer database with phone/email lookup
  - Points accumulation based on purchase amount
  - Loyalty tier system (Bronze, Silver, Gold, Platinum)
  - Reward redemption and point balance tracking
- **Payment Processing**: 
  - Cash, ATM (POS terminal), Bank Transfer
  - **Split Payment Support**: Accept partial payments with remaining balance tracking
  - Loyalty points as partial payment option
- **Order Management**:
  - Hold order, resume order
  - Add products before payment at cashier
  - Cancel or auto-expire order after 1 hour
  - Order note field for comments
- **Real-time Sync**: Badge alerts when Admin/Manager pushes order to cashier
- **Enhanced Invoice Generation**: 
  - Show total, tax, discount details, loyalty points earned/redeemed
  - Customer information and loyalty status
  - Itemized discount breakdown
- **Stock Validation**: Prevent sale if product stock is 0 or expired

### 2. 📦 Advanced Inventory Management
- **Advanced Stock Operations**: 
  - Add new stock with supplier selection
  - **Batch Number Tracking**: Unique batch identifiers for traceability
  - **Expiry Date Management**: Track expiration dates with automated alerts
  - **FIFO/FEFO Logic**: First-In-First-Out or First-Expired-First-Out inventory rotation
- **Enhanced Pricing Logic**: 
  - Selling price based on most recent cost + markup %
  - Display average of last 2 purchase costs
  - Batch-specific cost tracking
  - Dynamic pricing based on expiry proximity
- **Stock Tracking**: 
  - Auto-group by product, category, batch, and expiry date
  - Batch-level stock movements and history
  - Expiry date monitoring with color-coded alerts
- **Advanced Alerts**: 
  - Low stock alerts with reorder level suggestions
  - Expiry warnings (30, 15, 7, 3 days before expiration)
  - Near-expiry stock reports for promotional pricing
  - Batch recall notifications
- **Batch Operations**: 
  - Multiple products per supplier entry with individual batch tracking
  - Bulk expiry date updates
  - Mass batch transfers between locations

### 3. 🏢 Supplier Management
- **Enhanced Supplier Fields**: Name, contact person, email, phone, address, notes, payment terms
- **Advanced Invoice Tracking**: 
  - Invoice number required per supply (manual input)
  - Uniqueness validation per supplier
  - Each supply has unique receipt/invoice with batch correlation
  - Invoice amount validation against received goods
- **Supplier Performance Analytics**:
  - Lead time tracking
  - Quality score based on returns/defects
  - Payment terms compliance monitoring
- **Supplier Validation**: No duplicate supplier names allowed
- **Inline Creation**: Add new supplier during stock entry

### 4. 📋 Order Management
- **Order Creation**: Admin/Manager can create orders for customers with loyalty lookup
- **Real-time Push**: Send orders to cashier devices via WebSocket
- **Order Flexibility**: Customers can add items at checkout before payment
- **Order Status**: Track pending, completed, expired, cancelled orders
- **Auto-expiry**: Orders expire after 1 hour if not completed
- **Loyalty Integration**: Apply customer loyalty benefits to orders

### 5. 📊 Advanced Dashboard & Analytics
- **Enhanced KPI Widgets**: 
  - Today's sales, monthly sales, profit margins
  - Stock alerts, expiry warnings, batch notifications
  - Customer loyalty metrics, top customers
- **Sales Overview**: 
  - Graphical representation (daily/weekly/monthly/yearly)
  - Profit vs revenue comparison charts
  - Category performance analysis
- **Advanced Performance Metrics**: 
  - Most sold products with profit analysis
  - Customer analytics and segmentation
  - Inventory turnover rates
  - Expiry loss tracking
- **Role-based Access**: Admin, Manager, Assistant Manager with customized views
- **User Profile**: Click username to access profile settings

### 6. 👤 User Profile Management
- **Editable Fields**: Email, password, phone number, address
- **Read-only Fields**: First name, last name, username
- **Profile Access**: Top-right username click opens settings panel
- **Notification Preferences**: Configure alert settings for discounts, expiry, etc.

### 7. 👥 Customer Loyalty Management
- **Customer Database**:
  - Customer registration with phone, email, name, address
  - Purchase history and preferences tracking
  - Birthday and anniversary date storage for targeted promotions
- **Loyalty Program Configuration**:
  - Points per currency unit spent (configurable)
  - Tier thresholds and benefits
  - Redemption rates and minimum points
- **Customer Analytics**:
  - Customer lifetime value calculations
  - Purchase frequency and patterns
  - Segmentation based on spending and loyalty tier
- **Promotional Tools**:
  - Targeted discount campaigns
  - Birthday/anniversary promotions
  - Loyalty tier-based exclusive offers

### 8. 📈 Advanced Reporting & Analytics
- **Profit/Loss Reports**:
  - Daily, weekly, monthly, quarterly P&L statements
  - Cost of goods sold (COGS) calculations
  - Gross and net profit margins
  - Expense tracking and categorization
- **Customer Analytics**:
  - Customer acquisition and retention rates
  - Average order value and frequency
  - Customer lifetime value analysis
  - Loyalty program performance metrics
- **Inventory Analytics**:
  - Stock turnover analysis by category and product
  - Expiry loss reports and cost impact
  - Batch traceability and recall reports
  - Supplier performance scorecards
- **Sales Forecasting**:
  - Demand prediction based on historical data
  - Seasonal trend analysis
  - Inventory optimization recommendations
  - Reorder point calculations
- **Financial Forecasting**:
  - Cash flow projections
  - Revenue trend analysis
  - Profit margin forecasting
  - Budget vs actual performance

---

## 🔄 Real-time Sync Features

### 📡 WebSocket Capabilities
- **Live Updates**: Cashier alerts, order sync, inventory broadcasts, loyalty updates
- **Offline Queue**: Log actions locally when disconnected
- **Client Discovery**: Automatic device detection on LAN
- **Heartbeat Monitor**: Connection status tracking
- **Master Election**: Automatic failover protocol

### 🔃 Sync Logic
- Master Node holds authoritative database
- Clients log unsynced actions locally
- WebSocket sends payloads with timestamps
- On reconnect, sync queue is flushed
- Last-writer-wins consistency model with conflict resolution

---

## 🗃️ Enhanced Database Schema

*All tables include `created_at` and `updated_at` timestamp fields*

### Core Tables

```sql
-- User Management
users: id, username, password_hash, role_id, device_id, phone, email, address
roles: id, name, description

-- Product & Inventory with Batch Tracking
categories: id, name, prefix (for SKU generation)
products: id, name, sku (auto-generated), category_id, price, barcode, status, reorder_level
suppliers: id, name, contact_person, email, phone, address, notes, payment_terms

-- Advanced Inventory Operations
invoices: id, invoice_number, supplier_id (unique per supplier), total_amount
invoice_items: id, invoice_id, product_id, quantity, cost_price, batch_number, expiry_date
inventory_logs: id, product_id, quantity, type, invoice_id, batch_number
batches: id, product_id, batch_number, expiry_date, quantity, cost_price, status

-- Customer & Loyalty Management
customers: id, phone, email, name, address, birthday, anniversary_date, registration_date
loyalty_tiers: id, name, min_points, benefits, discount_percentage
customer_loyalty: id, customer_id, tier_id, total_points, available_points, lifetime_spent
loyalty_transactions: id, customer_id, order_id, points_earned, points_redeemed, transaction_type

-- Enhanced Sales Operations
pos_orders: id, order_number, status, total_amount, discount_amount, cashier_id, customer_id, notes
pos_order_items: id, order_id, product_id, quantity, selling_price, discount_amount, batch_id
payments: id, order_id, payment_method, amount, loyalty_points_used

-- Discount Management
discount_campaigns: id, name, type, value, start_date, end_date, min_purchase, max_usage
discount_rules: id, campaign_id, product_id, category_id, customer_tier_id
discount_usage: id, campaign_id, order_id, customer_id, discount_amount

-- Advanced Reporting
expense_categories: id, name, description
expenses: id, category_id, amount, description, expense_date, invoice_reference
profit_loss_summaries: id, period_start, period_end, revenue, cogs, gross_profit, expenses, net_profit

-- System Tracking
device_logs: id, device_id, action, user_id, timestamp
activity_logs: id, user_id, activity, details, timestamp
sync_logs: id, device_id, action_type, payload_json, synced_at
```

### 🔑 Enhanced Features
- **Batch Tracking**: Complete traceability from supplier to customer
- **Expiry Management**: Automated alerts and FIFO/FEFO rotation
- **Customer Loyalty**: Comprehensive points and tier management
- **Discount Engine**: Flexible campaign and rule-based discounting
- **Advanced Analytics**: Detailed financial and operational reporting

---

## 🎨 Enhanced User Interface Specification

### 🧭 Navigation Layout
- **Left Sidebar**: Expanded navigation menu with role-based access
- **Main Content**: Dynamic content area with advanced widgets
- **Top Bar**: User info, sync status, notifications, logout button
- **Alert Panel**: Sliding panel for expiry alerts and batch notifications
- **Full Screen**: Optimized for desktop (minimum 1280x800)

### 📱 Key UI Components

#### 1. Login Screen
- Username and password fields
- Role-based redirect after authentication
- System health indicators

#### 2. Enhanced Dashboard
- **KPI Cards**: Sales, profit margins, inventory alerts, loyalty metrics
- **Alert Widgets**: Expiry warnings, low stock, batch recalls
- **Charts**: Sales trends, profit analysis, customer analytics
- **Quick Actions**: Fast access to critical functions

#### 3. Advanced POS Interface
- **Left Panel**: Product search with barcode scanning integration
- **Center Panel**: Shopping cart with discount applications
- **Right Panel**: Customer lookup and loyalty information
- **Bottom Panel**: Multiple payment processing options
- **Discount Controls**: Manager override for large discounts

#### 4. Enhanced Product Management
- **Table View**: Products with batch information and expiry dates
- **Batch Management**: Track individual batches per product
- **Expiry Alerts**: Color-coded expiration warnings
- **Barcode Generation**: Automatic barcode creation for new products

#### 5. Advanced Inventory Management
- **Batch Entry**: Individual batch tracking during stock receipt
- **Expiry Calendar**: Visual representation of upcoming expirations
- **Stock Rotation**: FIFO/FEFO management interface
- **Supplier Performance**: Visual scorecards and metrics

#### 6. Customer Management Interface
- **Customer Database**: Searchable customer records
- **Loyalty Dashboard**: Points, tier status, and transaction history
- **Campaign Management**: Create and manage promotional campaigns
- **Analytics Views**: Customer segmentation and behavior analysis

#### 7. Advanced Reporting Dashboard
- **Financial Reports**: P&L statements with drill-down capabilities
- **Interactive Charts**: Clickable analytics with filtering
- **Export Options**: PDF, Excel, CSV export functionality
- **Scheduled Reports**: Automated report generation and delivery

---

## 🔌 Enhanced API Endpoints

### Authentication & Users
```
POST /api/login              # User authentication
GET  /api/me                # Current user info
POST /api/logout            # Session termination
```

### Products & Advanced Inventory
```
GET  /api/products          # Fetch all products with batch info
POST /api/products          # Create new product
PUT  /api/products/<id>     # Update product
GET  /api/inventory         # Inventory levels with batch tracking
POST /api/inventory         # Add stock with batch information
GET  /api/batches           # Batch information and expiry dates
POST /api/batches           # Create new batch
PUT  /api/batches/<id>      # Update batch information
GET  /api/expiry-alerts     # Get products nearing expiration
```

### Enhanced Orders & Sales
```
GET  /api/orders            # Fetch orders with customer info
POST /api/orders            # Create new order
PUT  /api/orders/<id>       # Update order
POST /api/sales             # Complete sale with loyalty processing
GET  /api/discounts         # Available discount campaigns
POST /api/discounts/apply   # Apply discount to order
```

### Customer & Loyalty Management
```
GET  /api/customers         # Customer database
POST /api/customers         # Add new customer
PUT  /api/customers/<id>    # Update customer information
GET  /api/loyalty           # Loyalty program configuration
POST /api/loyalty/earn      # Process loyalty points earning
POST /api/loyalty/redeem    # Process loyalty points redemption
GET  /api/campaigns         # Marketing campaigns
POST /api/campaigns         # Create new campaign
```

### Advanced Reporting & Analytics
```
GET  /api/reports/pnl       # Profit and loss reports
GET  /api/reports/customer  # Customer analytics
GET  /api/reports/inventory # Inventory analysis
GET  /api/reports/forecast  # Sales and profit forecasting
POST /api/reports/export    # Export reports in various formats
GET  /api/analytics/dashboard # Dashboard KPI data
```

### Suppliers & Admin
```
GET  /api/suppliers         # List suppliers with performance data
POST /api/suppliers         # Add new supplier
POST /api/sync              # Push local changes to Master
GET  /api/system/health     # System status and diagnostics
```

---

## 🛠️ Device Management

### 📱 Device Settings
- **Device ID Assignment**: Under System Settings > Device Settings
- **Primary Device Logic**: Only primary device operates when router offline
- **Backup Device**: Automatic failover to designated backup
- **Router Status**: Warning display when network disconnected
- **Device Switching**: Admin logs for role changes
- **Hardware Integration**: Barcode scanner and receipt printer setup

### 🔄 Offline Behavior
- **Queue-based Sync**: Store actions locally when offline including loyalty transactions
- **Router Detection**: Automatic network status monitoring
- **Fallback Mode**: Primary device continues operation with full functionality
- **Conflict Resolution**: Advanced timestamp-based consistency with data integrity checks

---

## 📤 Export & Advanced Reporting

### 📊 Enhanced Export Features
- **Comprehensive CSV Export**: Sales, inventory, customer data, and financial reports
- **PDF Reports**: Professional formatted financial statements and analytics
- **Excel Integration**: Advanced spreadsheet exports with charts and pivot tables
- **Scheduled Exports**: Automated daily/weekly/monthly report generation
- **Custom Report Builder**: User-configurable report templates

### 📈 Advanced Analytics
- **Predictive Analytics**: Machine learning-based demand forecasting
- **Performance Benchmarking**: KPI tracking against industry standards
- **ROI Analysis**: Return on investment calculations for campaigns and inventory
- **Trend Analysis**: Advanced statistical analysis of sales and customer patterns

---

## 🚀 Installation & Deployment

### 📦 Enhanced Packaging Strategy
- **Backend Bundling**: PyInstaller with advanced dependencies (ML libraries, analytics)
- **Frontend Build**: Flutter Windows executable with enhanced UI components
- **Installer Creation**: Advanced Inno Setup with hardware driver integration
- **Database Migration**: Automatic schema updates for advanced features

### 🔧 Installation Process
- Single installer with all dependencies including analytics libraries
- Hardware integration setup (barcode scanners, receipt printers)
- Advanced SQLite database with analytics tables
- Sample data and demonstration mode
- Comprehensive user manual and training materials

---

## 🛡️ Security & Compliance

### 🔐 Enhanced Security Features
- Advanced password policies and multi-factor authentication options
- Role-based access with granular permissions
- Audit trail for all financial transactions
- Data encryption for sensitive customer information
- Secure offline operations with integrity verification

### 📋 Compliance & Data Protection
- PCI DSS compliance for payment processing
- GDPR compliance with customer data protection
- Financial audit trail requirements
- Customer loyalty data protection
- Batch tracking for product recalls and quality assurance

---

## 🔮 Future Enhancements (Version 2)

### Advanced Integration Features
- **Cloud Backup**: Secure cloud synchronization and backup
- **Multi-store Management**: Centralized control for multiple locations
- **E-commerce Integration**: Online store synchronization
- **ERP Integration**: Connect with existing business systems
- **Advanced AI**: Machine learning for customer behavior prediction

### Enterprise Features
- **Advanced Security**: Biometric authentication, advanced encryption
- **Mobile Apps**: iOS/Android companion applications
- **API Gateway**: External system integration capabilities
- **Advanced Workflow**: Approval processes and business rule engine

---

## ✅ Success Metrics

### 📈 Enhanced Key Performance Indicators
- **User Adoption**: Role-based usage with advanced feature utilization
- **System Reliability**: 99.9% uptime with advanced sync success rates
- **Performance**: Sub-second response times for all operations
- **Business Impact**: Measurable improvements in profit margins and customer retention
- **Advanced Analytics**: Accurate forecasting within 5% variance

### 🎯 Acceptance Criteria
- Complete offline functionality for all advanced features
- Real-time sync with <1 second latency for critical operations
- Support for minimum 10 concurrent devices
- 99.99% data consistency across all clients
- Advanced reporting with drill-down capabilities
- Customer loyalty program with full points tracking
- Batch tracking with complete traceability
- Discount engine with flexible rule configuration

---

This enhanced PRD now includes all the advanced features as core Version 1 functionality, providing a comprehensive retail management system with professional-grade capabilities for inventory tracking, customer loyalty, advanced POS operations, and detailed financial analytics.

---
*This document will be updated as requirements evolve.* 