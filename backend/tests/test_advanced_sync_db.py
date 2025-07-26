"""
Integration tests for advanced sync database models and event integration.
"""
import pytest
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models import DeviceRole, SyncState, MasterElectionLog, SyncAuditLog

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session

def test_device_role_crud(session):
    device = DeviceRole(device_id='dev001', role='client', priority=2)
    session.add(device)
    session.commit()
    found = DeviceRole.get_device_by_id('dev001')
    assert found is not None
    assert found.role == 'client'
    found.change_role('master', reason='test')
    assert found.role == 'master'
    found.deactivate()
    assert found.is_active is False

def test_sync_state_crud(session):
    state = SyncState(device_id='dev002', sync_status='pending', pending_changes_count=3)
    session.add(state)
    session.commit()
    found = SyncState.get_device_sync_state('dev002')
    assert found is not None
    assert found.sync_status == 'pending'
    found.update_sync_status('error', error_message='Test error')
    assert found.sync_status == 'error'
    found.update_last_sync()
    assert found.sync_status == 'synced'
    found.increment_pending_changes(2)
    assert found.pending_changes_count == 5  # 3 + 2 = 5
    found.decrement_pending_changes(1)
    assert found.pending_changes_count == 4
    found.reset_pending_changes()
    assert found.pending_changes_count == 0

def test_master_election_log(session):
    log = MasterElectionLog(previous_master_id='dev001', new_master_id='dev002', election_reason='test', devices_participating=2)
    session.add(log)
    session.commit()
    found = MasterElectionLog.query.filter_by(new_master_id='dev002').first()
    assert found is not None
    assert found.election_reason == 'test'

def test_audit_log(session):
    audit = SyncAuditLog(event_type='sync', operation='request', status='pending', device_id='dev003', details='Test audit')
    session.add(audit)
    session.commit()
    found = SyncAuditLog.query.filter_by(device_id='dev003').first()
    assert found is not None
    assert found.operation == 'request' 