# API Reference – Retail Management System Backend

This document describes the REST and WebSocket API endpoints provided by the backend service.

> **Note:** All sync operations (REST, WebSocket, conflict resolution, failover, etc.) are logged to the SyncAuditLog model for audit trail and error handling. See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

---

## REST API Endpoints

| Method | Path         | Description                | Parameters         | Auth Required | Example Request/Response |
|--------|--------------|----------------------------|--------------------|---------------|-------------------------|
| GET    | /api/ping    | Health check               | None               | No            | ...                     |
| POST   | /api/login   | User login                 | username, password | No            | ...                     |
| POST   | /sync/push    | Push a new sync event to the master node | event_type (str, required), payload (JSON, required), device_id (str, required), user_id (str, optional), timestamp (ISO, optional) | No | Example Request: {"event_type": "stock_update", "payload": {"product_id": 1, "qty": 5}, "device_id": "dev123"} <br> Example Response: {"message": "Event queued", "event_id": 1} |
| GET    | /sync/pull    | Pull pending sync events for a device    | device_id (str, required), since (ISO timestamp, optional) | No | Example: /sync/pull?device_id=dev123&since=2025-07-25T12:00:00 <br> Response: {"events": [{...}]} |
| GET    | /sync/status  | Query sync status/history for device/user| device_id (str, optional), user_id (str, optional), limit (int, optional) | No | Example: /sync/status?device_id=dev123 <br> Response: {"summary": {"total": 10, ...}, "history": [{...}]} |

<!-- Add more endpoints as implemented -->

---

## WebSocket API Endpoints

| Event Name      | Description                | Payload/Parameters | Auth Required | Example Payload |
|-----------------|----------------------------|--------------------|---------------|----------------|
| connect         | Establish connection (optionally authenticate/register device) | None               | No            | {"message": "Connected to sync server"} |
| disconnect      | Disconnect from sync server                                    | None               | No            | N/A            |
| critical_event  | Broadcast a critical sync event to all clients (real-time)    | event_type (str, required), payload (JSON, required), device_id (str, required) | No | {"event_type": "stock_update", "payload": {"product_id": 1, "qty": 0}, "device_id": "dev123"} |
| acknowledge     | Client acknowledges receipt of a critical event                | event_id (int, required), device_id (str, required) | No | {"event_id": 1, "device_id": "dev123"} |
| sync_update     | Sync data update           | data, timestamp    | Yes           | ...            |
| ...             | ...                        | ...                | ...           | ...            |

<!-- Add more events as implemented -->

---

*Update this file as new endpoints and events are added to the backend.* 