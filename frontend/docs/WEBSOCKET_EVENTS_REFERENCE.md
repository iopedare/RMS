# WebSocket Events Reference - Frontend Implementation

This document provides a comprehensive reference for all WebSocket events that the Flutter frontend needs to handle for advanced sync features.

## Event Categories

### 1. Device Management Events

#### `device_online`
**Purpose:** Handle device coming back online
**Payload:**
```json
{
  "device_id": "string",
  "current_master": "string|null",
  "role": "master|client"
}
```
**Frontend Action:** Update device role, sync with current master if needed

#### `device_offline_ack`
**Purpose:** Acknowledge device going offline
**Payload:**
```json
{
  "device_id": "string"
}
```
**Frontend Action:** Update device status, prepare for potential role changes

#### `device_shutdown`
**Purpose:** Handle master device shutdown and trigger master election
**Payload:**
```json
{
  "device_id": "string"
}
```
**Frontend Action:** If this device is master, trigger shutdown sequence; if client, prepare for master election

### 2. Master Election Events

#### `master_elected`
**Purpose:** Notify all devices of new master election
**Payload:**
```json
{
  "previous_master_id": "string|null",
  "new_master_id": "string",
  "election_reason": "shutdown|failure|manual",
  "election_timestamp": "ISO8601",
  "devices_participating": "number"
}
```
**Frontend Action:** Update device roles, show notification, sync with new master

#### `role_change_ack`
**Purpose:** Acknowledge device role change
**Payload:**
```json
{
  "device_id": "string",
  "new_role": "master|client",
  "reason": "string"
}
```
**Frontend Action:** Update UI to reflect new role, show notification

### 3. Sync Events

#### `sync_response`
**Purpose:** Response to sync request from master
**Payload:**
```json
{
  "sync_type": "full|incremental",
  "timestamp": "ISO8601",
  "changes": "array",
  "master_device_id": "string"
}
```
**Frontend Action:** Apply sync changes, update local database

#### `sync_complete_ack`
**Purpose:** Acknowledge sync completion
**Payload:**
```json
{
  "device_id": "string",
  "sync_timestamp": "ISO8601",
  "changes_count": "number"
}
```
**Frontend Action:** Update sync status, show completion notification

#### `sync_conflict_resolved`
**Purpose:** Notify of conflict resolution
**Payload:**
```json
{
  "table_name": "string",
  "record_id": "number",
  "resolution_method": "last_writer_wins",
  "resolved_data": "object",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Apply resolved data, show conflict resolution notification

#### `sync_error_ack`
**Purpose:** Notify of sync error
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
**Payload:**
```json
{
  "device_id": "string",
  "table_name": "string",
  "record_id": "number",
  "new_data": "object",
  "operation": "insert|update|delete",
  "timestamp": "ISO8601"
}
```
**Frontend Action:** Update local database, refresh relevant UI components

#### `data_response`
**Purpose:** Response to data request
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

#### `queue_status_response`
**Purpose:** Response to queue status request
**Payload:**
```json
{
  "device_id": "string",
  "queue_type": "sync|offline",
  "pending_count": "number",
  "last_processed": "ISO8601",
  "status": "idle|processing|error"
}
```
**Frontend Action:** Update queue status display, show progress indicators

### 6. Legacy Events (Backward Compatibility)

#### `critical_event`
**Purpose:** Broadcast critical sync events
**Payload:**
```json
{
  "event_type": "string",
  "payload": "object",
  "device_id": "string"
}
```
**Frontend Action:** Handle based on event_type, show critical notifications

#### `registered`
**Purpose:** Confirm device registration
**Payload:**
```json
{
  "device_id": "string",
  "role": "master|client"
}
```
**Frontend Action:** Update registration status, show success notification

#### `acknowledged`
**Purpose:** Confirm event acknowledgement
**Payload:**
```json
{
  "message": "string"
}
```
**Frontend Action:** Update event status, log acknowledgement

#### `heartbeat_ack`
**Purpose:** Confirm heartbeat received
**Payload:**
```json
{
  "device_id": "string"
}
```
**Frontend Action:** Update connection status, reset heartbeat timer

### 7. Error Events

#### `error`
**Purpose:** General error notification
**Payload:**
```json
{
  "error": "string"
}
```
**Frontend Action:** Show error notification, log error

## Frontend Implementation Notes

### Event Handler Structure
Each event should be handled with:
1. **Validation:** Check required fields
2. **State Update:** Update relevant app state
3. **UI Update:** Refresh UI components
4. **User Feedback:** Show notifications where appropriate
5. **Error Handling:** Handle malformed or unexpected payloads

### State Management
The following state should be tracked:
- Device role (master/client)
- Connection status
- Sync status and queue
- Last sync timestamp
- Error states and messages

### UI Updates Required
- Sync status bar with role indicator
- Connection status indicator
- Queue status display
- Error notifications
- Role change notifications
- Master election notifications

### Error Handling
- Network disconnection/reconnection
- Invalid payload handling
- Timeout handling
- Retry mechanisms for failed operations 