# Frontend Master-Client Sync Architecture

## Overview
This document describes how the Flutter frontend integrates with the backend for master-client sync, including device registration, REST and WebSocket communication, real-time event handling, and UI sync indicators.

## 1. Device Registration
- On app startup, generate or retrieve a unique device ID.
- Register the device with the backend via WebSocket (`register_device` event).
- Assign device role (master/client) as needed.
- Display registration status in the UI.

## 2. REST API Integration
- Use HTTP requests for:
  - `/sync/push`: Push local changes/events to backend
  - `/sync/pull`: Pull latest events/updates from backend
  - `/sync/status`: Get sync/health status
- Handle API errors and show status in the UI.

## 3. WebSocket Integration
- Connect to backend WebSocket endpoint on app startup.
- Listen for real-time events:
  - `critical_event`: Receive and process critical sync events
  - `acknowledge`: Send/receive acknowledgements for event delivery
  - `registered`: Confirm device registration
  - `error`: Handle and display errors
- Reconnect automatically if connection is lost.

## 4. Real-Time Event Handling
- On receiving a `critical_event`, update local state and UI immediately.
- Send `acknowledge` event back to backend after processing.
- Queue events for later sync if offline.

## 5. UI Sync Indicators
- Show sync status (connected, syncing, offline, error) in the app header or status bar.
- Display last sync time and pending changes count.
- Notify user of critical events or sync failures.

## 6. Offline/Online State Management
- Detect network status and update UI accordingly.
- Queue outgoing events when offline; push them when back online.
- Pull latest updates from backend when reconnecting.

## 7. Advanced Features (Planned)
- Conflict resolution UI (if two devices update same record)
- Master election and failover handling
- Device heartbeat and health monitoring
- Security/authentication for API/WebSocket

---

*Update this document as the frontend sync logic evolves or new features are added.* 