# Retail Management System – Backend

This is the backend service for the Retail Management System, built with Flask and Flask-SocketIO. It provides REST and WebSocket APIs, handles business logic, and manages data storage and synchronization for offline-first retail operations.

## Features
- User authentication and role management
- Inventory and batch tracking
- POS and order processing
- Real-time sync and offline support
- Reporting and analytics

## Project Structure
- `app/` – Main application code (models, routes, services, utils, config)
- `tests/` – Unit and integration tests
- `requirements.txt` – Python dependencies
- `.gitignore` – Git ignore rules
- `README.md` – Project documentation
- `run.py` – Application entry point

## Setup
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On macOS/Linux
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the backend server:
   ```bash
   python run.py
   ```

## Error Handling & Audit Trail
- All sync operations (REST, WebSocket, conflict resolution, failover, etc.) are wrapped in robust error handling.
- All operations and errors are logged to the SyncAuditLog model for traceability, compliance, and troubleshooting.
- See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## Sync Logic Summary
- Periodic sync (every 30s) for all devices
- Immediate sync for critical events (real-time broadcast)
- Conflict resolution (first-come, first-served)
- Failover and device reconnection logic
- Full audit trail for all sync operations

## Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md): Backend architecture, sync protocol, error handling, audit trail
- [API_REFERENCE.md](API_REFERENCE.md): REST and WebSocket API endpoints

## API Reference
- See `API_REFERENCE.md` (to be created) for details on REST and WebSocket endpoints, parameters, and examples.

## Architecture
- See `ARCHITECTURE.md` (to be created) for backend architecture, master-client sync, and data flow.

## Progress
- [x] SyncEvent model and database integration complete (CRUD tested)
- [ ] REST and WebSocket API endpoints for sync (in progress)

## Testing the SyncEvent Model
You can run the test script from any directory:

```bash
python backend/tests/test_sync_event_model.py
```

or

```bash
python -m tests.test_sync_event_model
```

---

For more details, see the main project documentation and PRD.
