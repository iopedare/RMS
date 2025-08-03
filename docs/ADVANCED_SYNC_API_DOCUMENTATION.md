# 🔄 Advanced Sync API Documentation – Retail Management System

This document provides comprehensive documentation for all advanced sync features, including WebSocket events, REST endpoints, payload schemas, error codes, and implementation guidelines.

---

## 📋 Table of Contents

1. [WebSocket Events Reference](#websocket-events-reference)
2. [REST API Endpoints](#rest-api-endpoints)
3. [Device Role Transitions](#device-role-transitions)
4. [Master Election Protocol](#master-election-protocol)
5. [Database Schema Documentation](#database-schema-documentation)
6. [Error Codes and Recovery](#error-codes-and-recovery)
7. [Implementation Guidelines](#implementation-guidelines)
8. [Testing and Validation](#testing-and-validation)

---

## 🔌 WebSocket Events Reference

### Event Categories Overview

| Category | Events | Purpose |
|----------|--------|---------|
| **Device Management** | `device_online`, `device_offline`, `device_shutdown` | Handle device lifecycle |
| **Master Election** | `master_election`, `master_elected`, `role_change` | Manage device roles and leadership |
| **Sync Operations** | `sync_request`, `sync_response`, `sync_complete` | Handle data synchronization |
| **Data Events** | `data_update`, `data_request`, `data_response` | Manage data operations |
| **Queue Management** | `queue_status`, `queue_status_response` | Monitor sync queues |
| **Error Handling** | `sync_error`, `sync_conflict`, `error` | Handle errors and conflicts |
| **Legacy Support** | `critical_event`, `registered`, `heartbeat` | Backward compatibility |

---

## 🔌 WebSocket Events Reference

### Event Categories Overview

| Category | Events | Purpose |
|----------|--------|---------|
| **Device Management** | `device_online`, `device_offline`, `device_shutdown` | Handle device lifecycle |
| **Master Election** | `master_election`, `master_elected`, `role_change` | Manage device roles and leadership |
| **Sync Operations** | `sync_request`, `sync_response`, `sync_complete` | Handle data synchronization |
| **Data Events** | `data_update`, `data_request`, `data_response` | Manage data operations |
| **Queue Management** | `queue_status`, `queue_status_response` | Monitor sync queues |
| **Error Handling** | `sync_error`, `sync_conflict`, `error` | Handle errors and conflicts |
| **Legacy Support** | `critical_event`, `registered`, `heartbeat` | Backward compatibility |

### 1. Device Management Events

#### `device_online`
**Purpose:** Handle device coming back online and role assignment
**Direction:** Client → Server
**Payload:**
```json
{
  "device_id": "string (required)",
  "role": "master|client (optional, default: client)",
  "priority": "number (optional, default: 0)",
  "capabilities": ["array of strings (optional)"],
  "timestamp": "ISO8601 (optional)"
}
```
**Server Response:** `device_online_ack`
**Frontend Action:** Update device role, sync with current master if needed

#### `device_online_ack`
**Purpose:** Acknowledge device online registration
**Direction:** Server → Client
**Payload:**
```json
{
  "device_id": "string",
  "current_master": "string|null",
  "role": "master|client",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Update device status, prepare for role-based operations

#### `device_offline`
**Purpose:** Handle device going offline gracefully
**Direction:** Client → Server
**Payload:**
```json
{
  "device_id": "string (required)",
  "reason": "string (optional)",
  "timestamp": "ISO8601 (optional)"
}
```
**Server Response:** `device_offline_ack`
**Frontend Action:** Update device status, prepare for potential role changes

#### `device_offline_ack`
**Purpose:** Acknowledge device offline
**Direction:** Server → Client
**Payload:**
```json
{
  "device_id": "string",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Update device status, prepare for potential role changes

#### `device_shutdown`
**Purpose:** Handle master device shutdown and trigger master election
**Direction:** Client → Server
**Payload:**
```json
{
  "device_id": "string (required)",
  "reason": "string (optional)",
  "timestamp": "ISO8601 (optional)"
}
```
**Server Response:** `master_elected` (if master shutdown)
**Frontend Action:** If this device is master, trigger shutdown sequence; if client, prepare for master election

### 2. Master Election Events

#### `master_election`
**Purpose:** Trigger master election process
**Direction:** Client → Server
**Payload:**
```json
{
  "reason": "shutdown|failure|manual (required)",
  "initiated_by": "string (optional)",
  "timestamp": "ISO8601 (optional)"
}
```
**Server Response:** `master_elected`
**Frontend Action:** Prepare for election process

#### `master_elected`
**Purpose:** Notify all devices of new master election
**Direction:** Server → All Clients
**Payload:**
```json
{
  "previous_master_id": "string|null",
  "new_master_id": "string",
  "election_reason": "shutdown|failure|manual",
  "election_timestamp": "ISO8601",
  "devices_participating": "number",
  "election_method": "priority|manual|automatic"
}
```
**Frontend Action:** Update device roles, show notification, sync with new master

#### `role_change`
**Purpose:** Notify device role change
**Direction:** Server → All Clients
**Payload:**
```json
{
  "device_id": "string",
  "new_role": "master|client",
  "reason": "string",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Update UI to reflect new role, show notification

#### `role_change_ack`
**Purpose:** Acknowledge device role change
**Direction:** Server → Client
**Payload:**
```json
{
  "device_id": "string",
  "new_role": "master|client",
  "reason": "string",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Update UI to reflect new role, show notification

### 3. Sync Events

#### `sync_request`
**Purpose:** Request sync from master device
**Direction:** Client → Server
**Payload:**
```json
{
  "device_id": "string (required)",
  "sync_type": "full|incremental (optional, default: full)",
  "last_sync_timestamp": "ISO8601 (optional)",
  "requested_tables": ["array of strings (optional)"],
  "timestamp": "ISO8601 (optional)"
}
```
**Server Response:** `sync_response`
**Frontend Action:** Wait for sync response, show progress indicator

#### `sync_response`
**Purpose:** Response to sync request from master
**Direction:** Server → Client
**Payload:**
```json
{
  "sync_type": "full|incremental",
  "timestamp": "ISO8601",
  "changes": [
    {
      "table_name": "string",
      "record_id": "number",
      "operation": "insert|update|delete",
      "data": "object",
      "timestamp": "ISO8601"
    }
  ],
  "master_device_id": "string",
  "sync_id": "string"
}
```
**Frontend Action:** Apply sync changes, update local database

#### `sync_complete`
**Purpose:** Notify sync completion
**Direction:** Client → Server
**Payload:**
```json
{
  "device_id": "string (required)",
  "sync_timestamp": "ISO8601",
  "changes_count": "number",
  "sync_id": "string (optional)",
  "timestamp": "ISO8601 (optional)"
}
```
**Server Response:** `sync_complete_ack`
**Frontend Action:** Update sync status, show completion notification

#### `sync_complete_ack`
**Purpose:** Acknowledge sync completion
**Direction:** Server → All Clients
**Payload:**
```json
{
  "device_id": "string",
  "sync_timestamp": "ISO8601",
  "changes_count": "number",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Update sync status, show completion notification

#### `sync_conflict`
**Purpose:** Notify of sync conflict detection
**Direction:** Server → Client
**Payload:**
```json
{
  "device_id": "string",
  "table_name": "string",
  "record_id": "number",
  "conflict_type": "timestamp|data|version",
  "conflict_data": {
    "local_version": "object",
    "remote_version": "object",
    "timestamp": "ISO8601"
  },
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Show conflict resolution UI, apply resolution strategy

#### `sync_conflict_resolved`
**Purpose:** Notify of conflict resolution
**Direction:** Server → All Clients
**Payload:**
```json
{
  "table_name": "string",
  "record_id": "number",
  "resolution_method": "last_writer_wins|manual|automatic",
  "resolved_data": "object",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Apply resolved data, show conflict resolution notification

#### `sync_error`
**Purpose:** Notify of sync error
**Direction:** Server → Client
**Payload:**
```json
{
  "device_id": "string",
  "error_message": "string",
  "error_code": "string",
  "sync_type": "string (optional)",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Show error notification, update sync status, provide retry option

#### `sync_error_ack`
**Purpose:** Acknowledge sync error
**Direction:** Server → Client
**Payload:**
```json
{
  "device_id": "string",
  "error_message": "string",
  "error_code": "string",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Show error notification, update sync status, provide retry option

### 4. Data Events

#### `data_update`
**Purpose:** Broadcast data updates to all clients
**Direction:** Client → Server
**Payload:**
```json
{
  "device_id": "string (required)",
  "table_name": "string (required)",
  "record_id": "number (required)",
  "new_data": "object (required)",
  "operation": "insert|update|delete (optional, default: update)",
  "timestamp": "ISO8601 (optional)"
}
```
**Server Response:** Broadcasts to all clients
**Frontend Action:** Update local database, refresh relevant UI components

#### `data_request`
**Purpose:** Request specific data from master
**Direction:** Client → Server
**Payload:**
```json
{
  "device_id": "string (required)",
  "table_name": "string (required)",
  "record_id": "number (required)",
  "timestamp": "ISO8601 (optional)"
}
```
**Server Response:** `data_response`
**Frontend Action:** Wait for data response, update local data

#### `data_response`
**Purpose:** Response to data request
**Direction:** Server → Client
**Payload:**
```json
{
  "table_name": "string",
  "record_id": "number",
  "data": "object",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Update local data, refresh UI

### 5. Queue Status Events

#### `queue_status`
**Purpose:** Request queue status
**Direction:** Client → Server
**Payload:**
```json
{
  "device_id": "string (required)",
  "queue_type": "sync|offline (optional, default: sync)",
  "timestamp": "ISO8601 (optional)"
}
```
**Server Response:** `queue_status_response`
**Frontend Action:** Wait for queue status response

#### `queue_status_response`
**Purpose:** Response to queue status request
**Direction:** Server → Client
**Payload:**
```json
{
  "device_id": "string",
  "queue_type": "sync|offline",
  "pending_count": "number",
  "last_processed": "ISO8601",
  "status": "idle|processing|error",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Update queue status display, show progress indicators

### 6. Legacy Events (Backward Compatibility)

#### `critical_event`
**Purpose:** Broadcast critical sync events
**Direction:** Client → Server
**Payload:**
```json
{
  "event_type": "string (required)",
  "payload": "object (required)",
  "device_id": "string (required)",
  "timestamp": "ISO8601 (optional)"
}
```
**Server Response:** Broadcasts to all clients
**Frontend Action:** Handle based on event_type, show critical notifications

#### `registered`
**Purpose:** Confirm device registration
**Direction:** Server → Client
**Payload:**
```json
{
  "device_id": "string",
  "role": "master|client",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Update registration status, show success notification

#### `acknowledged`
**Purpose:** Confirm event acknowledgement
**Direction:** Server → Client
**Payload:**
```json
{
  "message": "string",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Update event status, log acknowledgement

#### `heartbeat`
**Purpose:** Send heartbeat to maintain connection
**Direction:** Client → Server
**Payload:**
```json
{
  "device_id": "string (required)",
  "timestamp": "ISO8601 (optional)"
}
```
**Server Response:** `heartbeat_ack`
**Frontend Action:** Maintain connection status

#### `heartbeat_ack`
**Purpose:** Confirm heartbeat received
**Direction:** Server → Client
**Payload:**
```json
{
  "device_id": "string",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Update connection status, reset heartbeat timer

### 7. Error Events

#### `error`
**Purpose:** General error notification
**Direction:** Server → Client
**Payload:**
```json
{
  "error": "string",
  "error_code": "string (optional)",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Show error notification, log error

---

## 🌐 REST API Endpoints

### Base URLs
- **Development**: `http://localhost:5000`
- **Production**: `http://[device-ip]:5000`

### Authentication
All endpoints require authentication unless specified otherwise.

### 1. Device Management Endpoints

#### Register Device
```http
POST /device/register
Content-Type: application/json

{
  "device_id": "string (required)",
  "role": "master|client (optional, default: client)",
  "priority": "number (optional, default: 0)",
  "capabilities": ["array of strings (optional)"]
}
```

**Response:**
```json
{
  "success": true,
  "device_id": "string",
  "role": "master|client",
  "master_device_id": "string|null",
  "sync_status": "connected|disconnected|error"
}
```

#### Get Device Roles
```http
GET /device/roles
```

**Response:**
```json
{
  "devices": [
    {
      "device_id": "string",
      "role": "master|client",
      "priority": "number",
      "last_seen": "ISO8601",
      "is_active": "boolean"
    }
  ]
}
```

#### Get Device Role
```http
GET /device/roles/{device_id}
```

**Response:**
```json
{
  "device_id": "string",
  "role": "master|client",
  "priority": "number",
  "last_seen": "ISO8601",
  "is_active": "boolean"
}
```

#### Update Device Role
```http
PUT /device/roles/{device_id}
Content-Type: application/json

{
  "role": "master|client (required)",
  "reason": "string (required)",
  "timestamp": "ISO8601 (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "device_id": "string",
  "new_role": "master|client",
  "reason": "string"
}
```

### 2. Sync State Management

#### Get Sync State
```http
GET /sync/state/{device_id}
```

**Response:**
```json
{
  "device_id": "string",
  "sync_status": "pending|syncing|synced|error",
  "pending_changes_count": "number",
  "last_sync_timestamp": "ISO8601",
  "last_error_message": "string|null",
  "updated_at": "ISO8601"
}
```

#### Update Sync State
```http
PUT /sync/state/{device_id}
Content-Type: application/json

{
  "sync_status": "pending|syncing|synced|error (optional)",
  "pending_changes_count": "number (optional)",
  "last_error_message": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "sync_state": {
    "device_id": "string",
    "sync_status": "string",
    "pending_changes_count": "number",
    "last_sync_timestamp": "ISO8601",
    "last_error_message": "string|null",
    "updated_at": "ISO8601"
  }
}
```

### 3. Master Election Logs

#### Get Master Election Logs
```http
GET /sync/master-election-logs?limit=10&offset=0
```

**Response:**
```json
{
  "logs": [
    {
      "id": "number",
      "previous_master_id": "string|null",
      "new_master_id": "string",
      "election_reason": "string",
      "election_timestamp": "ISO8601",
      "devices_participating": "number"
    }
  ],
  "pagination": {
    "limit": "number",
    "offset": "number",
    "total": "number"
  }
}
```

### 4. Sync Audit Logs

#### Get Sync Audit Logs
```http
GET /sync/audit-logs?device_id=string&event_type=string&start_date=ISO8601&end_date=ISO8601&limit=10&offset=0
```

**Response:**
```json
{
  "logs": [
    {
      "id": "number",
      "event_type": "string",
      "operation": "string",
      "status": "success|error",
      "device_id": "string",
      "details": "string",
      "timestamp": "ISO8601"
    }
  ],
  "pagination": {
    "limit": "number",
    "offset": "number",
    "total": "number"
  }
}
```

### 5. System Health

#### Get System Health
```http
GET /system/health
```

**Response:**
```json
{
  "status": "healthy|degraded|unhealthy",
  "master_device": "string|null",
  "active_devices": "number",
  "sync_status": "string",
  "last_check": "ISO8601"
}
```

#### Get Network Status
```http
GET /system/network
```

**Response:**
```json
{
  "network_status": "connected|disconnected|partitioned",
  "active_connections": "number",
  "last_heartbeat": "ISO8601",
  "network_latency": "number"
}
```

---

## 🔄 Device Role Transitions

### Role Transition State Diagram

```
[Client] ←→ [Master]
    ↑           ↑
    ↓           ↓
[Offline] ←→ [Shutdown]
```

### Transition Triggers

| From | To | Trigger | Conditions |
|------|----|---------|------------|
| Client | Master | Master Election | - Current master offline<br>- Manual election<br>- Priority-based selection |
| Master | Client | Master Election | - Another device elected<br>- Manual role change<br>- System failure |
| Any | Offline | Device Offline | - Network disconnect<br>- Device shutdown<br>- System failure |
| Offline | Client | Device Online | - Network reconnect<br>- Device restart<br>- Manual reconnection |

### Priority-Based Election Logic

1. **Device Priority Calculation:**
   - Admin devices: Priority 100
   - Manager devices: Priority 80
   - Assistant Manager devices: Priority 60
   - Inventory Assistant devices: Priority 40
   - Sales Assistant devices: Priority 20

2. **Election Process:**
   - Triggered by master shutdown, failure, or manual request
   - All active devices participate
   - Highest priority device becomes master
   - Ties resolved by device ID (alphabetical)

3. **Graceful Handover:**
   - Current master completes pending operations
   - New master assumes control
   - All clients notified of role change
   - Sync state transferred

---

## 👑 Master Election Protocol

### Election Triggers

1. **Automatic Triggers:**
   - Master device shutdown
   - Master device failure (heartbeat timeout)
   - Network partition detection
   - System restart

2. **Manual Triggers:**
   - Admin-initiated election
   - Device role change request
   - System maintenance

### Election Process Flow

```
1. Election Triggered
   ↓
2. Collect Active Devices
   ↓
3. Calculate Priorities
   ↓
4. Select New Master
   ↓
5. Notify All Devices
   ↓
6. Transfer Sync State
   ↓
7. Resume Operations
```

### Election Timeout and Retry

- **Initial Timeout:** 30 seconds
- **Retry Attempts:** 3 maximum
- **Backoff Strategy:** Exponential (1s, 2s, 4s)
- **Fallback:** Manual intervention required

### Election Validation

1. **Pre-election Checks:**
   - Verify device connectivity
   - Validate device capabilities
   - Check sync state consistency

2. **Post-election Validation:**
   - Confirm new master online
   - Verify role change completion
   - Test sync operations

---

## 🗄️ Database Schema Documentation

### DeviceRole Model

```sql
CREATE TABLE device_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'client',
    priority INTEGER DEFAULT 0,
    last_seen DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `device_id`: Unique device identifier
- `role`: Current role (master/client)
- `priority`: Election priority (0-100)
- `last_seen`: Last activity timestamp
- `is_active`: Device connectivity status

### SyncState Model

```sql
CREATE TABLE sync_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    sync_status VARCHAR(50) DEFAULT 'pending',
    pending_changes_count INTEGER DEFAULT 0,
    last_sync_timestamp DATETIME,
    last_error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `device_id`: Device identifier
- `sync_status`: Current sync status
- `pending_changes_count`: Number of pending changes
- `last_sync_timestamp`: Last successful sync
- `last_error_message`: Last error details

### MasterElectionLog Model

```sql
CREATE TABLE master_election_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    previous_master_id VARCHAR(255),
    new_master_id VARCHAR(255) NOT NULL,
    election_reason VARCHAR(100) NOT NULL,
    election_timestamp DATETIME NOT NULL,
    devices_participating INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `previous_master_id`: Previous master device
- `new_master_id`: Newly elected master
- `election_reason`: Reason for election
- `election_timestamp`: Election timestamp
- `devices_participating`: Number of participating devices

### SyncAuditLog Model

```sql
CREATE TABLE sync_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR(100) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    device_id VARCHAR(255),
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `event_type`: Type of sync event
- `operation`: Operation performed
- `status`: Success/error status
- `device_id`: Related device
- `details`: Additional information

### Database Migrations

#### Migration 1: Create Advanced Sync Tables
```sql
-- Create device_roles table
CREATE TABLE device_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'client',
    priority INTEGER DEFAULT 0,
    last_seen DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create sync_states table
CREATE TABLE sync_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    sync_status VARCHAR(50) DEFAULT 'pending',
    pending_changes_count INTEGER DEFAULT 0,
    last_sync_timestamp DATETIME,
    last_error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create master_election_logs table
CREATE TABLE master_election_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    previous_master_id VARCHAR(255),
    new_master_id VARCHAR(255) NOT NULL,
    election_reason VARCHAR(100) NOT NULL,
    election_timestamp DATETIME NOT NULL,
    devices_participating INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create sync_audit_logs table
CREATE TABLE sync_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR(100) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    device_id VARCHAR(255),
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_device_roles_device_id ON device_roles(device_id);
CREATE INDEX idx_device_roles_role ON device_roles(role);
CREATE INDEX idx_sync_states_device_id ON sync_states(device_id);
CREATE INDEX idx_sync_states_status ON sync_states(sync_status);
CREATE INDEX idx_master_election_logs_timestamp ON master_election_logs(election_timestamp);
CREATE INDEX idx_sync_audit_logs_device_id ON sync_audit_logs(device_id);
CREATE INDEX idx_sync_audit_logs_timestamp ON sync_audit_logs(timestamp);
```

---

## ⚠️ Error Codes and Recovery

### Error Code Categories

| Category | Code Range | Description |
|----------|------------|-------------|
| **Connection Errors** | 1000-1999 | Network and connectivity issues |
| **Sync Errors** | 2000-2999 | Data synchronization problems |
| **Authentication Errors** | 3000-3999 | Authentication and authorization |
| **Device Errors** | 4000-4999 | Device management issues |
| **System Errors** | 5000-5999 | System-level problems |

### Common Error Codes

#### Connection Errors (1000-1999)
- `1001`: Connection timeout
- `1002`: Network unreachable
- `1003`: WebSocket connection failed
- `1004`: Heartbeat timeout
- `1005`: Reconnection failed

#### Sync Errors (2000-2999)
- `2001`: Sync request failed
- `2002`: Data conflict detected
- `2003`: Sync timeout
- `2004`: Invalid sync data
- `2005`: Master unavailable

#### Authentication Errors (3000-3999)
- `3001`: Invalid credentials
- `3002`: Token expired
- `3003`: Insufficient permissions
- `3004`: Device not registered

#### Device Errors (4000-4999)
- `4001`: Device registration failed
- `4002`: Role change failed
- `4003`: Master election failed
- `4004`: Device offline

#### System Errors (5000-5999)
- `5001`: Database connection failed
- `5002`: Internal server error
- `5003`: Service unavailable
- `5004`: Configuration error

### Recovery Procedures

#### Automatic Recovery
1. **Connection Recovery:**
   - Exponential backoff retry
   - Automatic reconnection
   - Heartbeat monitoring

2. **Sync Recovery:**
   - Retry failed sync operations
   - Conflict resolution
   - State reconciliation

3. **Device Recovery:**
   - Automatic role reassignment
   - Master election retry
   - State restoration

#### Manual Recovery
1. **Network Issues:**
   - Check network connectivity
   - Restart network services
   - Verify firewall settings

2. **Device Issues:**
   - Restart device
   - Clear device cache
   - Re-register device

3. **System Issues:**
   - Restart backend service
   - Check database connectivity
   - Verify configuration

---

## 🛠️ Implementation Guidelines

### Frontend Implementation

#### Event Handler Structure
```dart
// Example: Device online handler
void _handleDeviceOnline(dynamic data) {
  // 1. Validation
  if (data is! Map<String, dynamic>) return;
  final deviceId = data['device_id'];
  final role = data['role'];
  if (deviceId == null) return;

  // 2. State Update
  setState(() {
    this.deviceId = deviceId;
    this.role = role;
    this.status = 'connected';
  });

  // 3. UI Update
  _updateSyncStatusBar();
  _showNotification('Device online as $role');

  // 4. Error Handling
  try {
    // Additional processing
  } catch (e) {
    _handleError('Device online error: $e');
  }
}
```

#### State Management
```dart
class SyncState {
  String deviceId;
  String role;
  String status;
  DateTime? lastSync;
  int pendingChanges;
  String? errorMessage;
  
  // State update methods
  void updateRole(String newRole) {
    role = newRole;
    notifyListeners();
  }
  
  void updateSyncStatus(String status) {
    this.status = status;
    if (status == 'synced') {
      lastSync = DateTime.now();
    }
    notifyListeners();
  }
}
```

#### Error Handling
```dart
void _handleError(String error, {String? errorCode}) {
  setState(() {
    this.errorMessage = error;
    this.status = 'error';
  });
  
  // Log error
  print('Sync error: $error (code: $errorCode)');
  
  // Show user notification
  _showErrorNotification(error);
  
  // Attempt recovery
  _attemptRecovery(errorCode);
}
```

### Backend Implementation

#### Event Handler Structure
```python
@socketio.on('device_online')
def handle_device_online(data):
    """Handle device coming back online."""
    try:
        # 1. Validation
        device_id = data.get('device_id')
        role = data.get('role', 'client')
        
        if not device_id:
            emit('error', {'error': 'Missing device_id'})
            return
            
        # 2. Database Update
        device = DeviceRole.get_device_by_id(device_id)
        if not device:
            device = DeviceRole(device_id=device_id, role=role)
            db.session.add(device)
        else:
            device.role = role
            device.last_seen = datetime.now()
            
        db.session.commit()
        
        # 3. Audit Logging
        audit = SyncAuditLog(
            event_type='device_online',
            operation='online',
            status='success',
            device_id=device_id,
            details=f"Device online as {role}"
        )
        db.session.add(audit)
        db.session.commit()
        
        # 4. Response
        emit('device_online_ack', {
            'device_id': device_id,
            'current_master': master_device_id,
            'role': device.role
        })
        
    except Exception as e:
        # 5. Error Handling
        emit('error', {'error': f'Device online failed: {str(e)}'})
        db.session.rollback()
```

#### Database Operations
```python
class DeviceRole(db.Model):
    __tablename__ = 'device_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False, default='client')
    priority = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_device_by_id(cls, device_id):
        return cls.query.filter_by(device_id=device_id).first()
    
    def change_role(self, new_role, reason='manual'):
        self.role = new_role
        self.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log role change
        audit = SyncAuditLog(
            event_type='role_change',
            operation='change_role',
            status='success',
            device_id=self.device_id,
            details=f"Role changed to {new_role} (reason: {reason})"
        )
        db.session.add(audit)
        db.session.commit()
```

### Performance Optimization

#### Frontend Optimizations
1. **Event Batching:**
   - Batch UI updates
   - Debounce frequent events
   - Use efficient state management

2. **Connection Management:**
   - Implement connection pooling
   - Use heartbeat for connection monitoring
   - Implement automatic reconnection

3. **Memory Management:**
   - Clean up event listeners
   - Dispose of unused resources
   - Monitor memory usage

#### Backend Optimizations
1. **Database Optimization:**
   - Use appropriate indexes
   - Implement connection pooling
   - Optimize queries

2. **Event Handling:**
   - Use async event processing
   - Implement event queuing
   - Monitor event throughput

3. **Resource Management:**
   - Implement proper cleanup
   - Monitor resource usage
   - Handle connection limits

---

## 🧪 Testing and Validation

### Unit Testing

#### Frontend Tests
```dart
test('Device online event handler', () {
  // Arrange
  final mockData = {
    'device_id': 'test_device',
    'role': 'client'
  };
  
  // Act
  syncService.handleDeviceOnline(mockData);
  
  // Assert
  expect(syncService.deviceId, 'test_device');
  expect(syncService.role, 'client');
  expect(syncService.status, 'connected');
});
```

#### Backend Tests
```python
def test_device_online_handler():
    """Test device online event handler."""
    # Arrange
    data = {
        'device_id': 'test_device',
        'role': 'client'
    }
    
    # Act
    with app.test_client() as client:
        response = client.post('/socket.io/', json={
            'event': 'device_online',
            'data': data
        })
    
    # Assert
    assert response.status_code == 200
    device = DeviceRole.get_device_by_id('test_device')
    assert device is not None
    assert device.role == 'client'
```

### Integration Testing

#### Multi-Device Sync Test
```python
def test_multi_device_sync():
    """Test sync between multiple devices."""
    # Setup devices
    device1 = create_test_device('device1', 'master')
    device2 = create_test_device('device2', 'client')
    
    # Perform sync operations
    sync_data = {'test': 'data'}
    device1.push_sync_event(sync_data)
    
    # Verify sync
    assert device2.has_synced_data(sync_data)
```

### Performance Testing

#### Load Testing
```python
def test_concurrent_devices():
    """Test system with multiple concurrent devices."""
    devices = []
    
    # Create multiple devices
    for i in range(10):
        device = create_test_device(f'device{i}')
        devices.append(device)
    
    # Perform concurrent operations
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(device.perform_sync)
            for device in devices
        ]
        
        # Wait for completion
        for future in futures:
            assert future.result() is not None
```

### User Acceptance Testing

#### Test Scenarios
1. **Device Registration:**
   - Register new device
   - Verify role assignment
   - Test priority-based election

2. **Master Election:**
   - Trigger master shutdown
   - Verify automatic election
   - Test role transitions

3. **Sync Operations:**
   - Perform data sync
   - Test conflict resolution
   - Verify data consistency

4. **Error Recovery:**
   - Simulate network failures
   - Test automatic recovery
   - Verify error handling

#### Test Results Documentation
```markdown
## UAT Results

### Test Scenario: Multi-Device Sync
- **Status:** ✅ PASSED
- **Devices Tested:** 3
- **Sync Operations:** 50
- **Conflicts Resolved:** 2
- **Performance:** < 2s average sync time

### Test Scenario: Master Election
- **Status:** ✅ PASSED
- **Elections Triggered:** 5
- **Role Transitions:** 10
- **Recovery Time:** < 5s average

### Test Scenario: Error Recovery
- **Status:** ✅ PASSED
- **Network Failures:** 10
- **Automatic Recovery:** 100%
- **Data Loss:** 0%
```

---

## 📚 Additional Resources

### Related Documentation
- [Frontend WebSocket Events Reference](../frontend/docs/WEBSOCKET_EVENTS_REFERENCE.md)
- [Backend Architecture Documentation](ARCHITECTURE.md)
- [API Reference](API_REFERENCE.md)
- [Implementation Plan](implementation_plan.md)

### Development Tools
- **WebSocket Testing:** [Socket.IO Tester](https://chrome.google.com/webstore/detail/socket-io-tester/cgmimdpepcncnjgclhnhghdooepgeggf)
- **API Testing:** [Postman](https://www.postman.com/)
- **Performance Monitoring:** [Flutter DevTools](https://docs.flutter.dev/tools/devtools)

### Support and Troubleshooting
- **Error Codes:** See [Error Codes and Recovery](#error-codes-and-recovery) section
- **Common Issues:** Check [Implementation Guidelines](#implementation-guidelines)
- **Performance Issues:** Review [Testing and Validation](#testing-and-validation)

---

*This documentation is maintained as part of the Retail Management System project. For updates and contributions, please refer to the project repository.* 