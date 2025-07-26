import sys
import os

# Ensure the backend/app directory is in the Python path regardless of working directory
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app, db
from app.models.sync_audit_log import SyncAuditLog

def test_sync_audit_log_crud():
    app = create_app()
    with app.app_context():
        # Ensure tables are created
        db.create_all()

        # Create a new audit log entry
        log = SyncAuditLog(
            event_type='sync',
            operation='push',
            status='success',
            device_id='device123',
            user_id='user456',
            details='Test audit log entry'
        )
        db.session.add(log)
        db.session.commit()
        print(f"Created: {log}")

        # Query for audit logs
        logs = SyncAuditLog.query.filter_by(device_id='device123').all()
        print(f"Queried: {logs}")

        # Update log status
        log.status = 'error'
        db.session.commit()
        print(f"Updated: {log}")

        # Error handling example
        try:
            bad_log = SyncAuditLog()
            db.session.add(bad_log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error (expected): {e}")

        # Clean up (optional)
        db.session.delete(log)
        db.session.commit()
        print("Deleted log entry.")

if __name__ == '__main__':
    test_sync_audit_log_crud() 