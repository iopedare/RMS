# 👥 User Roles and Permissions Design – Retail Management System

## Overview

This document defines the user roles, permissions, and role-based access control (RBAC) architecture for the Retail Management System. The system will support multiple user roles with granular permissions to ensure security and operational efficiency.

---

## 1. User Roles Definition

### 1.1 Role Hierarchy

```
Admin (Super User)
├── Manager
│   ├── Assistant Manager
│   ├── Inventory Assistant
│   └── Sales Assistant
```

### 1.2 Role Descriptions

#### **Admin (Super User)**
- **Description**: Full system access with administrative privileges
- **Primary Responsibilities**: 
  - System configuration and maintenance
  - User management and role assignment
  - Security settings and audit review
  - Database management and backups
  - Override any system restrictions
- **Key Features**:
  - Can access all modules and functions
  - Can manage all users and roles
  - Can override single-device login restrictions
  - Can view and manage audit logs
  - Can perform system maintenance tasks

#### **Manager**
- **Description**: Store management with broad operational access
- **Primary Responsibilities**:
  - Store operations oversight
  - Staff management and scheduling
  - Financial reporting and analysis
  - Inventory management oversight
  - Customer service management
- **Key Features**:
  - Full access to POS, inventory, and reporting
  - Can manage staff accounts (except Admin)
  - Can approve discounts and refunds
  - Can access financial reports
  - Can manage suppliers and orders

#### **Assistant Manager**
- **Description**: Deputy manager with most operational permissions
- **Primary Responsibilities**:
  - Daily store operations
  - Staff supervision
  - Customer service
  - Inventory oversight
  - Sales management
- **Key Features**:
  - Full POS access
  - Inventory management (except bulk operations)
  - Customer management
  - Basic reporting access
  - Limited user management (view only)

#### **Inventory Assistant**
- **Description**: Specialized role for inventory management
- **Primary Responsibilities**:
  - Stock management and tracking
  - Receiving and processing orders
  - Inventory counts and adjustments
  - Supplier communication
  - Batch and expiry management
- **Key Features**:
  - Full inventory module access
  - Order management
  - Supplier management
  - Inventory reporting
  - Limited POS access (view only)

#### **Sales Assistant**
- **Description**: Point-of-sale focused role
- **Primary Responsibilities**:
  - Customer transactions
  - Product sales and returns
  - Customer service
  - Basic inventory queries
  - Cash handling
- **Key Features**:
  - Full POS access
  - Customer management
  - Basic inventory queries
  - Sales reporting
  - No administrative functions

---

## 2. Permission Matrix

### 2.1 Module Access Permissions

| Module | Admin | Manager | Assistant Manager | Inventory Assistant | Sales Assistant |
|--------|-------|---------|-------------------|-------------------|-----------------|
| **Authentication & Users** | Full | Manage (except Admin) | View Only | None | None |
| **POS Operations** | Full | Full | Full | View Only | Full |
| **Inventory Management** | Full | Full | Limited | Full | View Only |
| **Customer Management** | Full | Full | Full | View Only | Full |
| **Supplier Management** | Full | Full | Limited | Full | None |
| **Order Management** | Full | Full | Limited | Full | None |
| **Reporting & Analytics** | Full | Full | Limited | Limited | Limited |
| **System Settings** | Full | Limited | None | None | None |
| **Audit Logs** | Full | View | None | None | None |

### 2.2 CRUD Operation Permissions

#### **Create Permissions**
| Operation | Admin | Manager | Assistant Manager | Inventory Assistant | Sales Assistant |
|-----------|-------|---------|-------------------|-------------------|-----------------|
| Users | ✅ | ✅ (except Admin) | ❌ | ❌ | ❌ |
| Products | ✅ | ✅ | ✅ | ✅ | ❌ |
| Inventory | ✅ | ✅ | ✅ | ✅ | ❌ |
| Customers | ✅ | ✅ | ✅ | ❌ | ✅ |
| Suppliers | ✅ | ✅ | ❌ | ✅ | ❌ |
| Orders | ✅ | ✅ | ✅ | ✅ | ❌ |
| Sales | ✅ | ✅ | ✅ | ❌ | ✅ |
| Reports | ✅ | ✅ | ❌ | ❌ | ❌ |

#### **Read Permissions**
| Operation | Admin | Manager | Assistant Manager | Inventory Assistant | Sales Assistant |
|-----------|-------|---------|-------------------|-------------------|-----------------|
| Users | ✅ | ✅ | ✅ (limited) | ❌ | ❌ |
| Products | ✅ | ✅ | ✅ | ✅ | ✅ |
| Inventory | ✅ | ✅ | ✅ | ✅ | ✅ |
| Customers | ✅ | ✅ | ✅ | ✅ | ✅ |
| Suppliers | ✅ | ✅ | ✅ | ✅ | ❌ |
| Orders | ✅ | ✅ | ✅ | ✅ | ❌ |
| Sales | ✅ | ✅ | ✅ | ✅ | ✅ |
| Reports | ✅ | ✅ | ✅ (limited) | ✅ (limited) | ✅ (limited) |

#### **Update Permissions**
| Operation | Admin | Manager | Assistant Manager | Inventory Assistant | Sales Assistant |
|-----------|-------|---------|-------------------|-------------------|-----------------|
| Users | ✅ | ✅ (except Admin) | ❌ | ❌ | ❌ |
| Products | ✅ | ✅ | ✅ | ✅ | ❌ |
| Inventory | ✅ | ✅ | ✅ | ✅ | ❌ |
| Customers | ✅ | ✅ | ✅ | ❌ | ✅ |
| Suppliers | ✅ | ✅ | ❌ | ✅ | ❌ |
| Orders | ✅ | ✅ | ✅ | ✅ | ❌ |
| Sales | ✅ | ✅ | ✅ | ❌ | ✅ |
| System Settings | ✅ | ✅ (limited) | ❌ | ❌ | ❌ |

#### **Delete Permissions**
| Operation | Admin | Manager | Assistant Manager | Inventory Assistant | Sales Assistant |
|-----------|-------|---------|-------------------|-------------------|-----------------|
| Users | ✅ | ✅ (except Admin) | ❌ | ❌ | ❌ |
| Products | ✅ | ✅ | ❌ | ❌ | ❌ |
| Inventory | ✅ | ✅ | ❌ | ❌ | ❌ |
| Customers | ✅ | ✅ | ❌ | ❌ | ❌ |
| Suppliers | ✅ | ✅ | ❌ | ❌ | ❌ |
| Orders | ✅ | ✅ | ❌ | ❌ | ❌ |
| Sales | ✅ | ✅ | ❌ | ❌ | ❌ |
| System Data | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 3. Special Permissions and Restrictions

### 3.1 Financial Operations

| Operation | Admin | Manager | Assistant Manager | Inventory Assistant | Sales Assistant |
|-----------|-------|---------|-------------------|-------------------|-----------------|
| **Discount Approval** | ✅ | ✅ | ✅ (up to 15%) | ❌ | ❌ |
| **Refund Processing** | ✅ | ✅ | ✅ (up to $100) | ❌ | ✅ (up to $50) |
| **Void Transactions** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Cash Drawer Management** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Financial Reports** | ✅ | ✅ | ✅ (limited) | ❌ | ❌ |

### 3.2 System Operations

| Operation | Admin | Manager | Assistant Manager | Inventory Assistant | Sales Assistant |
|-----------|-------|---------|-------------------|-------------------|-----------------|
| **Device Management** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Sync Configuration** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Backup Operations** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Audit Log Access** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **System Maintenance** | ✅ | ❌ | ❌ | ❌ | ❌ |

### 3.3 Session Management

| Feature | Admin | Manager | Assistant Manager | Inventory Assistant | Sales Assistant |
|---------|-------|---------|-------------------|-------------------|-----------------|
| **Single Device Login** | ❌ (Override) | ✅ | ✅ | ✅ | ✅ |
| **Session Timeout** | 8 hours | 6 hours | 6 hours | 4 hours | 4 hours |
| **Concurrent Sessions** | Unlimited | 1 | 1 | 1 | 1 |
| **Remote Access** | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## 4. Role-Based Access Control (RBAC) Design

### 4.1 Permission Structure

```
Permission (Granular)
├── Resource (Module/Entity)
├── Action (CRUD Operation)
├── Condition (Business Rules)
└── Effect (Allow/Deny)
```

### 4.2 Permission Categories

#### **Authentication Permissions**
- `auth:login` - Can log into the system
- `auth:logout` - Can log out of the system
- `auth:change_password` - Can change own password
- `auth:reset_password` - Can reset other user passwords
- `auth:manage_sessions` - Can manage user sessions

#### **User Management Permissions**
- `users:create` - Can create new users
- `users:read` - Can view user information
- `users:update` - Can update user information
- `users:delete` - Can delete users
- `users:assign_roles` - Can assign roles to users

#### **Role Management Permissions**
- `roles:create` - Can create new roles
- `roles:read` - Can view role information
- `roles:update` - Can update role information
- `roles:delete` - Can delete roles
- `roles:assign_permissions` - Can assign permissions to roles

#### **POS Permissions**
- `pos:create_sale` - Can create sales transactions
- `pos:read_sale` - Can view sales transactions
- `pos:update_sale` - Can modify sales transactions
- `pos:delete_sale` - Can void sales transactions
- `pos:apply_discount` - Can apply discounts
- `pos:process_refund` - Can process refunds
- `pos:manage_cart` - Can manage shopping cart
- `pos:access_cash_drawer` - Can access cash drawer

#### **Inventory Permissions**
- `inventory:create_product` - Can create products
- `inventory:read_product` - Can view products
- `inventory:update_product` - Can update products
- `inventory:delete_product` - Can delete products
- `inventory:manage_stock` - Can manage stock levels
- `inventory:process_orders` - Can process inventory orders
- `inventory:view_reports` - Can view inventory reports

#### **Customer Permissions**
- `customers:create` - Can create customer records
- `customers:read` - Can view customer information
- `customers:update` - Can update customer information
- `customers:delete` - Can delete customer records
- `customers:manage_loyalty` - Can manage loyalty program

#### **Supplier Permissions**
- `suppliers:create` - Can create supplier records
- `suppliers:read` - Can view supplier information
- `suppliers:update` - Can update supplier information
- `suppliers:delete` - Can delete supplier records
- `suppliers:manage_orders` - Can manage supplier orders

#### **Reporting Permissions**
- `reports:view_sales` - Can view sales reports
- `reports:view_inventory` - Can view inventory reports
- `reports:view_financial` - Can view financial reports
- `reports:view_customer` - Can view customer reports
- `reports:export_data` - Can export report data

#### **System Permissions**
- `system:view_audit_logs` - Can view audit logs
- `system:manage_devices` - Can manage system devices
- `system:configure_sync` - Can configure sync settings
- `system:perform_backup` - Can perform system backups
- `system:maintenance` - Can perform system maintenance

### 4.3 Permission Assignment by Role

#### **Admin Permissions**
```python
admin_permissions = [
    # All permissions
    "*:*"  # Wildcard permission for all operations
]
```

#### **Manager Permissions**
```python
manager_permissions = [
    # User Management (except Admin)
    "users:create", "users:read", "users:update", "users:delete",
    "roles:read", "roles:update",
    
    # POS Operations
    "pos:*",
    
    # Inventory Management
    "inventory:*",
    
    # Customer Management
    "customers:*",
    
    # Supplier Management
    "suppliers:*",
    
    # Reporting
    "reports:*",
    
    # System (limited)
    "system:view_audit_logs", "system:manage_devices", "system:configure_sync"
]
```

#### **Assistant Manager Permissions**
```python
assistant_manager_permissions = [
    # POS Operations
    "pos:*",
    
    # Inventory (limited)
    "inventory:read_product", "inventory:update_product", "inventory:manage_stock",
    "inventory:view_reports",
    
    # Customer Management
    "customers:*",
    
    # Limited reporting
    "reports:view_sales", "reports:view_inventory", "reports:view_customer"
]
```

#### **Inventory Assistant Permissions**
```python
inventory_assistant_permissions = [
    # Inventory Management
    "inventory:*",
    
    # Supplier Management
    "suppliers:*",
    
    # Order Management
    "orders:*",
    
    # Limited reporting
    "reports:view_inventory", "reports:export_data"
]
```

#### **Sales Assistant Permissions**
```python
sales_assistant_permissions = [
    # POS Operations
    "pos:create_sale", "pos:read_sale", "pos:update_sale", "pos:manage_cart",
    "pos:apply_discount", "pos:process_refund", "pos:access_cash_drawer",
    
    # Customer Management
    "customers:create", "customers:read", "customers:update",
    
    # Limited inventory access
    "inventory:read_product",
    
    # Limited reporting
    "reports:view_sales"
]
```

---

## 5. Security Considerations

### 5.1 Authentication Security
- **Password Policy**: Minimum 8 characters, complexity requirements
- **Account Lockout**: 5 failed attempts, 30-minute lockout
- **Session Management**: Configurable timeouts by role
- **Single Device Login**: Enforced for all roles except Admin
- **Audit Logging**: All authentication events logged

### 5.2 Authorization Security
- **Principle of Least Privilege**: Users get minimum required permissions
- **Role-Based Access**: Permissions assigned through roles
- **Permission Inheritance**: Clear hierarchy for permission inheritance
- **Dynamic Permission Checking**: Real-time permission validation
- **Audit Trail**: All authorization decisions logged

### 5.3 Data Security
- **Encryption**: Sensitive data encrypted at rest and in transit
- **Access Control**: Database-level access control
- **Data Masking**: Sensitive data masked in logs
- **Backup Security**: Encrypted backups with access control

---

## 6. Implementation Guidelines

### 6.1 Authentication Flow Design

#### **Initial Setup (First Device)**
1. **First Device Registration**: When the app is installed on the first device, an admin user must register
2. **Admin Creation**: This creates the initial admin user with full system permissions
3. **Device Registration**: The first device becomes the "master" device for that network
4. **Network Discovery**: Device broadcasts its admin status on the local network

#### **Subsequent Devices (Same Router)**
1. **Auto-Discovery**: When other devices join the same router, they automatically discover the existing admin
2. **No Registration Needed**: Other devices should NOT require registration - they inherit the admin authentication
3. **Single Admin Per Network**: Only one admin registration per router/network segment
4. **Network-Based Authentication**: Authentication is tied to the local network

#### **Key Design Principles**
- ✅ **One Admin Per Network**: Only the first device needs admin registration
- ✅ **Auto-Discovery**: Other devices automatically find and connect to the existing admin
- ✅ **No Dummy Login**: No default credentials or dummy accounts
- ✅ **Network-Based Authentication**: Authentication is tied to the local network

### 6.2 Database Design
- **Users Table**: Store user information and authentication data
- **Roles Table**: Define available roles
- **Permissions Table**: Define available permissions
- **UserRoles Table**: Many-to-many relationship between users and roles
- **RolePermissions Table**: Many-to-many relationship between roles and permissions
- **AuditLog Table**: Track all security events

### 6.2 API Design
- **Authentication Endpoints**: Login, logout, refresh, verify
- **User Management Endpoints**: CRUD operations for users
- **Role Management Endpoints**: CRUD operations for roles
- **Permission Management Endpoints**: Assign permissions to roles
- **Session Management Endpoints**: Manage user sessions

### 6.3 Frontend Integration
- **Role-Based UI**: Show/hide UI elements based on permissions
- **Permission Guards**: Route-level permission checking
- **Dynamic Menus**: Generate navigation based on user permissions
- **Error Handling**: Graceful handling of permission denied errors

---

## 7. Testing Strategy

### 7.1 Unit Testing
- Test permission checking logic
- Test role assignment and inheritance
- Test authentication flows
- Test authorization middleware

### 7.2 Integration Testing
- Test complete authentication flows
- Test role-based access to APIs
- Test session management
- Test audit logging

### 7.3 Security Testing
- Test authentication bypass scenarios
- Test privilege escalation attempts
- Test session hijacking prevention
- Test input validation and sanitization

---

## 8. Documentation Requirements

### 8.1 Technical Documentation
- API reference for authentication endpoints
- Database schema documentation
- Permission matrix documentation
- Security configuration guide

### 8.2 User Documentation
- User role descriptions and responsibilities
- Permission guide for each role
- Security best practices guide
- Troubleshooting guide for common issues

---

## 9. Approval and Sign-off

This design document requires stakeholder approval before implementation:

- [ ] **Technical Review**: Architecture and security review
- [ ] **Business Review**: Role definitions and permission matrix
- [ ] **Security Review**: Security considerations and compliance
- [ ] **Stakeholder Approval**: Final approval from project stakeholders

**Next Steps:**
1. Review this design with stakeholders
2. Get approval for role definitions and permissions
3. Begin implementation of database models
4. Create authentication services
5. Implement REST endpoints
6. Add comprehensive testing
7. Conduct security testing
8. Create documentation
9. Conduct UAT
10. Prepare for frontend integration 