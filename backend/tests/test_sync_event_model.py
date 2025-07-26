import sys
import os

# Ensure the backend/app directory is in the Python path regardless of working directory
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app, db
from app.models.sync_event import SyncEvent

def test_sync_event_crud():
    app = create_app()
    with app.app_context():
        # Ensure tables are created
        db.create_all()

        # Create a new sync event
        event = SyncEvent(
            event_type='stock_update',
            payload={'product_id': 1, 'new_stock': 0},
            device_id='device123',
            user_id='user456'
        )
        db.session.add(event)
        db.session.commit()
        print(f"Created: {event}")

        # Query for sync events
        events = SyncEvent.query.filter_by(device_id='device123').all()
        print(f"Queried: {events}")

        # Update event status
        event.status = 'synced'
        db.session.commit()
        print(f"Updated: {event}")

        # Error handling example
        try:
            bad_event = SyncEvent()
            db.session.add(bad_event)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error (expected): {e}")

        # Clean up (optional)
        db.session.delete(event)
        db.session.commit()
        print("Deleted event.")

if __name__ == '__main__':
    test_sync_event_crud() 