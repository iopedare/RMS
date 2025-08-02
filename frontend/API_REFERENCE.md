# API Reference – Retail Management System Frontend

This document describes how the frontend communicates with the backend, including REST and WebSocket integration, data models, and key integration points.

---

## 🔗 Backend Communication

### REST API Endpoints

#### Device Registration
```http
POST /sync/device/register
Content-Type: application/json

{
  "device_id": "string (required)",
  "role": "admin|manager|assistant_manager|sales_assistant|master|client",
  "priority": "integer (0-100)"
}
```

**Response:**
```json
{
  "status": "registered",
  "device_id": "string",
  "role": "string",
  "priority": "integer"
}
```

#### Sync Operations
```http
POST /sync/push
Content-Type: application/json

{
  "event_type": "string (required)",
  "payload": "object (required)",
  "device_id": "string (required)",
  "user_id": "string (optional)",
  "timestamp": "ISO timestamp (optional)"
}
```

```http
GET /sync/pull?device_id={device_id}&since={timestamp}
GET /sync/status?device_id={device_id}&user_id={user_id}&limit={limit}
```

### WebSocket Events

#### Connection Events
```json
// Device Online
{
  "event": "device_online",
  "data": {
    "device_id": "string",
    "role": "string",
    "priority": "integer"
  }
}

// Device Offline
{
  "event": "device_offline",
  "data": {
    "device_id": "string"
  }
}
```

#### Sync Events
```json
// Critical Event
{
  "event": "critical_event",
  "data": {
    "event_type": "string",
    "payload": "object",
    "device_id": "string"
  }
}

// Master Election
{
  "event": "master_election",
  "data": {
    "master_device_id": "string",
    "master_role": "string",
    "election_reason": "string"
  }
}

// Sync Request/Response
{
  "event": "sync_request",
  "data": {
    "requesting_device_id": "string",
    "sync_type": "string"
  }
}
```

### Error Handling

#### Standard Error Response
```json
{
  "error": "string",
  "error_code": "string",
  "timestamp": "ISO timestamp"
}
```

#### Validation Error Response
```json
{
  "error": "Validation failed",
  "details": {
    "field": "error_message"
  },
  "error_code": "VALIDATION_ERROR"
}
```

---

## 📊 Data Models

### Device Registration Model
```dart
class DeviceRegistration {
  final String deviceId;
  final String role;
  final int priority;
  final DateTime timestamp;
  
  DeviceRegistration({
    required this.deviceId,
    required this.role,
    required this.priority,
    required this.timestamp,
  });
}
```

### Sync Event Model
```dart
class SyncEvent {
  final String eventType;
  final Map<String, dynamic> payload;
  final String deviceId;
  final String? userId;
  final DateTime timestamp;
  
  SyncEvent({
    required this.eventType,
    required this.payload,
    required this.deviceId,
    this.userId,
    required this.timestamp,
  });
}
```

### Sync Status Model
```dart
class SyncStatus {
  final String status; // connected, disconnected, reconnecting, error
  final String? masterDeviceId;
  final String currentRole;
  final DateTime lastSync;
  final int pendingOperations;
  
  SyncStatus({
    required this.status,
    this.masterDeviceId,
    required this.currentRole,
    required this.lastSync,
    required this.pendingOperations,
  });
}
```

---

## 🔧 Integration Points

### Authentication Flow
1. **Device Registration**: Register device with backend on app startup
2. **Role Assignment**: Backend assigns role based on device priority
3. **Session Management**: Maintain WebSocket connection for real-time sync
4. **Reconnection**: Automatic reconnection on network disconnection

### Real-time Sync Logic
1. **WebSocket Connection**: Establish persistent connection
2. **Event Listening**: Listen for sync events from backend
3. **Event Processing**: Handle different event types (critical, master election, etc.)
4. **State Updates**: Update UI based on sync events
5. **Error Recovery**: Handle connection errors and retry logic

### Error Handling and Offline Support
1. **Network Detection**: Monitor network connectivity
2. **Offline Queue**: Queue operations when offline
3. **Retry Logic**: Retry failed operations when back online
4. **Error Notifications**: Show user-friendly error messages
5. **Graceful Degradation**: Continue basic functionality when offline

---

## 🎨 UI Integration Guidelines

### Sync Status Display
- **Connected**: Green indicator with checkmark
- **Disconnected**: Red indicator with X
- **Reconnecting**: Yellow indicator with spinner
- **Error**: Red indicator with exclamation

### Role Badge Design
- **Admin**: Purple badge with crown icon
- **Manager**: Blue badge with star icon
- **Assistant Manager**: Green badge with shield icon
- **Sales Assistant**: Orange badge with user icon
- **Master**: Gold badge with crown and star

### Error Notifications
- **Toast Messages**: Show temporary error notifications
- **Retry Buttons**: Allow users to retry failed operations
- **Error Details**: Show detailed error information when needed
- **Offline Indicators**: Clear indication when offline

---

## 🧪 Testing Guidelines

### Unit Testing
- Test all API service methods
- Mock WebSocket connections
- Test error handling scenarios
- Validate data models

### Integration Testing
- Test with real backend API
- Validate WebSocket event handling
- Test multi-device scenarios
- Verify data consistency

### User Acceptance Testing
- Test with different user roles
- Validate UI/UX design
- Test error recovery flows
- Collect user feedback

---

*This document should be updated as new integration points and data models are added to the frontend.* 