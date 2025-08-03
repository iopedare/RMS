# 📚 API Reference – Retail Management System

This document provides comprehensive API documentation for the Retail Management System backend, including REST endpoints, WebSocket events, error codes, and integration examples.

---

## 🔗 Base URLs

- **Development**: `http://localhost:5000`
- **Production**: `http://[device-ip]:5000`

---

## 🔐 Authentication

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "device_id": "device_001"
  }
}
```

### Logout
```http
POST /api/auth/logout
Authorization: Bearer <token>
```

---

## 👤 User Management

### List Users
```http
GET /api/users?page=1&per_page=20&search=admin&role=Admin&status=active&sort_by=created_at&sort_order=desc
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20, max: 100)
- `search` (str): Search term for username, email, or name
- `role` (str): Filter by role name
- `status` (str): Filter by status (active, inactive, locked)
- `sort_by` (str): Sort field (username, email, created_at, last_login)
- `sort_order` (str): Sort order (asc, desc)

**Response:**
```json
{
  "success": true,
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "first_name": "Admin",
      "last_name": "User",
      "is_active": true,
      "is_locked": false,
      "roles": ["Admin"],
      "created_at": "2024-12-19T10:00:00Z",
      "last_login": "2024-12-19T15:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 50,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

### Get User
```http
GET /api/users/{id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "phone": "+1234567890",
    "is_active": true,
    "is_locked": false,
    "failed_login_attempts": 0,
    "locked_until": null,
    "roles": [
      {
        "id": 1,
        "name": "Admin",
        "description": "System Administrator",
        "is_primary": true
      }
    ],
    "permissions": ["users:create", "users:read", "users:update", "users:delete"],
    "created_at": "2024-12-19T10:00:00Z",
    "updated_at": "2024-12-19T15:30:00Z",
    "last_login": "2024-12-19T15:30:00Z",
    "password_changed_at": "2024-12-19T10:00:00Z"
  }
}
```

### Create User
```http
POST /api/users
Authorization: Bearer <token>
Content-Type: application/json

{
  "username": "manager",
  "email": "manager@example.com",
  "password": "Manager123!",
  "first_name": "Store",
  "last_name": "Manager",
  "phone": "+1234567890",
  "roles": [1, 2],
  "is_active": true
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 2,
    "username": "manager",
    "email": "manager@example.com",
    "first_name": "Store",
    "last_name": "Manager",
    "is_active": true,
    "roles": ["Manager"],
    "created_at": "2024-12-19T16:00:00Z"
  }
}
```

### Update User
```http
PUT /api/users/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "updated@example.com",
  "first_name": "Updated",
  "last_name": "Manager",
  "phone": "+9876543210",
  "is_active": true
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 2,
    "username": "manager",
    "email": "updated@example.com",
    "first_name": "Updated",
    "last_name": "Manager",
    "phone": "+9876543210",
    "is_active": true,
    "updated_at": "2024-12-19T16:30:00Z"
  }
}
```

### Delete User
```http
DELETE /api/users/{id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

**Error Responses:**

**400 Bad Request - Password Validation:**
```json
{
  "success": false,
  "error": "Password must be at least 8 characters long"
}
```

**409 Conflict - Duplicate Username/Email:**
```json
{
  "success": false,
  "error": "Username or email already exists"
}
```

**401 Unauthorized:**
```json
{
  "success": false,
  "error": "Authorization token required"
}
```

**403 Forbidden:**
```json
{
  "success": false,
  "error": "Insufficient permissions"
}
```

---

## 🔄 Sync Endpoints

### Device Registration
```http
POST /api/device/register
Content-Type: application/json

{
  "device_id": "device_001",
  "role": "client",
  "priority": 1,
  "capabilities": ["pos", "inventory", "reports"]
}
```

**Response:**
```json
{
  "success": true,
  "device_id": "device_001",
  "role": "client",
  "master_device_id": "device_002",
  "sync_status": "connected"
}
```

### Push Sync Event
```http
POST /api/sync/push
Content-Type: application/json
Authorization: Bearer <token>

{
  "event_type": "stock_update",
  "payload": {
    "product_id": 123,
    "quantity": 50,
    "batch_number": "BATCH001"
  },
  "device_id": "device_001",
  "user_id": 1,
  "timestamp": "2025-01-27T10:30:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "event_id": 456,
  "status": "queued",
  "sync_timestamp": "2025-01-27T10:30:05Z"
}
```

### Pull Sync Events
```http
GET /api/sync/pull?device_id=device_001&since=2025-01-27T10:00:00Z
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "events": [
    {
      "id": 456,
      "event_type": "stock_update",
      "payload": {
        "product_id": 123,
        "quantity": 50,
        "batch_number": "BATCH001"
      },
      "timestamp": "2025-01-27T10:30:00Z",
      "status": "pending",
      "device_id": "device_002",
      "user_id": 2
    }
  ],
  "last_sync": "2025-01-27T10:30:05Z"
}
```

### Sync Status
```http
GET /api/sync/status?device_id=device_001
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "device_id": "device_001",
  "role": "client",
  "master_device_id": "device_002",
  "sync_status": "connected",
  "last_sync": "2025-01-27T10:30:05Z",
  "pending_events": 5,
  "connection_health": "good",
  "clock_offset": 2.5
}
```

---

## 📡 WebSocket Events

### Connection
```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Register device after connection
socket.emit('register_device', {
  device_id: 'device_001',
  role: 'client',
  priority: 1
});
```

### Device Management Events

#### Device Online
```javascript
// Emit when device comes online
socket.emit('device_online', {
  device_id: 'device_001',
  role: 'client',
  priority: 1
});

// Listen for online acknowledgment
socket.on('device_online_ack', (data) => {
  console.log('Device online acknowledged:', data);
  // data: { device_id, current_master, role }
});
```

#### Device Offline
```javascript
// Emit when device goes offline gracefully
socket.emit('device_offline', {
  device_id: 'device_001'
});

// Listen for offline acknowledgment
socket.on('device_offline_ack', (data) => {
  console.log('Device offline acknowledged:', data);
  // data: { device_id }
});
```

#### Device Shutdown
```javascript
// Emit when master device is shutting down
socket.emit('device_shutdown', {
  device_id: 'device_001'
});
```

#### Master Election
```javascript
// Listen for master election events
socket.on('master_elected', (data) => {
  console.log('New master elected:', data);
  // data: { previous_master_id, new_master_id, election_reason, election_timestamp, devices_participating }
});

// Trigger manual master election
socket.emit('master_election', {
  reason: 'manual'
});
```

#### Role Change
```javascript
// Listen for role change notifications
socket.on('role_change', (data) => {
  console.log('Role changed:', data);
  // data: { device_id, new_role, reason }
});

// Listen for role change acknowledgment
socket.on('role_change_ack', (data) => {
  console.log('Role change acknowledged:', data);
  // data: { device_id, new_role, reason }
});
```

### Sync Events

#### Sync Request
```javascript
// Request sync from master
socket.emit('sync_request', {
  device_id: 'device_001',
  sync_type: 'full', // 'full' or 'incremental'
  last_sync_timestamp: '2025-01-27T10:00:00Z'
});

// Listen for sync response
socket.on('sync_response', (data) => {
  console.log('Sync response received:', data);
  // data: { sync_type, timestamp, changes, master_device_id }
});
```

#### Sync Complete
```javascript
// Notify sync completion
socket.emit('sync_complete', {
  device_id: 'device_001',
  sync_type: 'full',
  sync_timestamp: '2025-01-27T10:30:05Z',
  changes_processed: 10
});
```

#### Sync Conflict
```javascript
// Listen for sync conflicts
socket.on('sync_conflict', (data) => {
  console.log('Sync conflict detected:', data);
  // data: { device_id, table_name, record_id, conflict_type, resolution_method }
});
```

#### Sync Error
```javascript
// Listen for sync errors
socket.on('sync_error', (data) => {
  console.log('Sync error:', data);
  // data: { error, device_id, sync_type }
});
```

### Data Events

#### Data Update
```javascript
// Broadcast data update to all clients
socket.emit('data_update', {
  device_id: 'device_001',
  table_name: 'products',
  record_id: 123,
  operation: 'update',
  timestamp: '2025-01-27T10:30:00Z'
});

// Listen for data updates
socket.on('data_update', (data) => {
  console.log('Data update received:', data);
  // data: { device_id, table_name, record_id, operation, timestamp }
});
```

#### Data Request
```javascript
// Request specific data from master
socket.emit('data_request', {
  device_id: 'device_001',
  table_name: 'products',
  record_id: 123
});

// Listen for data response
socket.on('data_response', (data) => {
  console.log('Data response received:', data);
  // data: { table_name, record_id, data, timestamp }
});
```

#### Queue Status
```javascript
// Request queue status
socket.emit('queue_status', {
  device_id: 'device_001',
  queue_type: 'sync' // 'sync' or 'offline'
});

// Listen for queue status response
socket.on('queue_status_response', (data) => {
  console.log('Queue status:', data);
  // data: { device_id, queue_type, pending_count, last_processed, status }
});
```

---

## 🛠️ Product Management

### Get Products
```http
GET /api/products?page=1&limit=20&search=phone
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "products": [
    {
      "id": 1,
      "name": "iPhone 15",
      "sku": "PHONE001",
      "category": "Electronics",
      "price": 999.99,
      "stock": 50,
      "batch_number": "BATCH001",
      "expiry_date": "2026-01-27",
      "created_at": "2025-01-27T10:00:00Z",
      "updated_at": "2025-01-27T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

### Create Product
```http
POST /api/products
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "iPhone 15",
  "category_id": 1,
  "price": 999.99,
  "barcode": "1234567890123",
  "reorder_level": 10
}
```

### Update Product
```http
PUT /api/products/1
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "iPhone 15 Pro",
  "price": 1099.99
}
```

### Delete Product
```http
DELETE /api/products/1
Authorization: Bearer <token>
```

---

## 📦 Inventory Management

### Add Stock
```http
POST /api/inventory/add
Content-Type: application/json
Authorization: Bearer <token>

{
  "product_id": 1,
  "quantity": 50,
  "batch_number": "BATCH001",
  "expiry_date": "2026-01-27",
  "cost_price": 800.00,
  "supplier_id": 1,
  "invoice_number": "INV001"
}
```

### Get Inventory
```http
GET /api/inventory?product_id=1&batch_number=BATCH001
Authorization: Bearer <token>
```

### Update Stock
```http
PUT /api/inventory/1
Content-Type: application/json
Authorization: Bearer <token>

{
  "quantity": 45,
  "expiry_date": "2026-01-27"
}
```

---

## 🛒 POS Operations

### Create Order
```http
POST /api/pos/orders
Content-Type: application/json
Authorization: Bearer <token>

{
  "customer_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "price": 999.99
    }
  ],
  "payment_method": "cash",
  "discount_amount": 50.00,
  "notes": "Customer request"
}
```

### Get Orders
```http
GET /api/pos/orders?status=pending&page=1&limit=20
Authorization: Bearer <token>
```

### Update Order Status
```http
PUT /api/pos/orders/1/status
Content-Type: application/json
Authorization: Bearer <token>

{
  "status": "completed"
}
```

---

## 👥 Customer Management

### Get Customers
```http
GET /api/customers?search=john&page=1&limit=20
Authorization: Bearer <token>
```

### Create Customer
```http
POST /api/customers
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "John Doe",
  "phone": "+1234567890",
  "email": "john@example.com",
  "address": "123 Main St"
}
```

### Update Customer
```http
PUT /api/customers/1
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "John Smith",
  "phone": "+1234567890"
}
```

---

## 📊 Reports

### Sales Report
```http
GET /api/reports/sales?start_date=2025-01-01&end_date=2025-01-31&format=json
Authorization: Bearer <token>
```

### Inventory Report
```http
GET /api/reports/inventory?category_id=1&format=csv
Authorization: Bearer <token>
```

### Profit/Loss Report
```http
GET /api/reports/pnl?period=monthly&year=2025&month=1
Authorization: Bearer <token>
```

---

## ⚠️ Error Codes

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Unprocessable Entity
- `500` - Internal Server Error

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "price",
      "issue": "Price must be greater than 0"
    }
  }
}
```

### Common Error Codes
- `DEVICE_NOT_FOUND` - Device not registered
- `INVALID_ROLE` - Invalid device role
- `SYNC_CONFLICT` - Data sync conflict detected
- `MASTER_ELECTION_FAILED` - Master election failed
- `NETWORK_PARTITION` - Network partition detected
- `CLOCK_DRIFT` - Device clock drift detected
- `HIGH_LOAD` - System under high load
- `DATA_CORRUPTION` - Data integrity issue detected

---

## 🔧 Integration Examples

### Flutter Integration
```dart
// REST API Service
class ApiService {
  static const String baseUrl = 'http://localhost:5000';
  
  Future<Map<String, dynamic>> registerDevice(String deviceId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/device/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'device_id': deviceId,
        'role': 'client',
        'priority': 1
      })
    );
    
    return jsonDecode(response.body);
  }
}

// WebSocket Service
class SocketService {
  late Socket socket;
  
  void connect() {
    socket = io('http://localhost:5000');
    
    socket.on('connect', (data) {
      print('Connected to server');
      registerDevice();
    });
    
    socket.on('master_elected', (data) {
      print('New master elected: ${data['new_master_id']}');
    });
  }
  
  void registerDevice() {
    socket.emit('register_device', {
      'device_id': 'device_001',
      'role': 'client'
    });
  }
}
```

### JavaScript Integration
```javascript
// REST API calls
const api = {
  async registerDevice(deviceId) {
    const response = await fetch('/api/device/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        device_id: deviceId,
        role: 'client',
        priority: 1
      })
    });
    
    return response.json();
  },
  
  async getProducts(page = 1, limit = 20) {
    const response = await fetch(`/api/products?page=${page}&limit=${limit}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    return response.json();
  }
};

// WebSocket integration
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to server');
  socket.emit('register_device', {
    device_id: 'device_001',
    role: 'client'
  });
});

socket.on('data_update', (data) => {
  console.log('Data updated:', data);
  // Update UI based on data change
});
```

---

## 📋 Testing

### Test Environment
- **Base URL**: `http://localhost:5000`
- **Test Database**: `test_retail_system.db`
- **Test Token**: Use login endpoint to get valid token

### Test Scenarios
1. **Device Registration**: Test device registration and role assignment
2. **Sync Operations**: Test push/pull sync events
3. **Master Election**: Test master election and failover
4. **Network Partition**: Test network partition detection and recovery
5. **Clock Drift**: Test clock drift detection and compensation
6. **High Load**: Test system performance under high load
7. **Error Handling**: Test error responses and recovery

### Test Data
```json
{
  "test_device": {
    "device_id": "test_device_001",
    "role": "client",
    "priority": 1
  },
  "test_user": {
    "username": "testuser",
    "password": "testpass123",
    "role": "admin"
  },
  "test_product": {
    "name": "Test Product",
    "category_id": 1,
    "price": 99.99,
    "barcode": "1234567890123"
  }
}
```

---

## 🔄 Version History

### v1.0.0 (Current)
- Initial API implementation
- Basic sync functionality
- Device management
- Product and inventory management
- POS operations
- Customer management
- Reporting endpoints

### Planned Features
- Advanced analytics endpoints
- Real-time notifications
- Bulk operations
- Advanced search and filtering
- Export functionality
- Audit trail endpoints

---

*This API reference is maintained by the development team. For questions or clarifications, please refer to the implementation documentation or contact the development team.* 