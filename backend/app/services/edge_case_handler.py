"""
Edge Case Handler Service for Advanced Sync Features

This service handles various edge cases and improves system robustness:
- Network partitions and split-brain scenarios
- Device clock drift and timestamp conflicts
- Data corruption and recovery
- Performance optimization and rate limiting
- Error recovery and graceful degradation
"""

import datetime
import logging
import time
from typing import Dict, List, Optional, Tuple
from flask import current_app
from app.extensions import db
from app.models.device_role import DeviceRole
from app.models.sync_state import SyncState
from app.models.master_election_log import MasterElectionLog
from app.models.sync_audit_log import SyncAuditLog

logger = logging.getLogger(__name__)

class EdgeCaseHandler:
    """Handles edge cases and improves system robustness"""
    
    def __init__(self):
        self.clock_drift_threshold = 300  # 5 minutes in seconds
        self.network_partition_timeout = 60  # 1 minute
        self.max_retry_attempts = 3
        self.rate_limit_window = 60  # 1 minute
        self.rate_limit_max_requests = 100
        
    def detect_clock_drift(self, device_id: str, client_timestamp: datetime.datetime) -> Tuple[bool, float]:
        """
        Detect clock drift between devices
        
        Args:
            device_id: The device ID
            client_timestamp: Timestamp from client device
            
        Returns:
            Tuple of (has_drift, drift_seconds)
        """
        server_time = datetime.datetime.utcnow()
        drift_seconds = abs((client_timestamp - server_time).total_seconds())
        has_drift = drift_seconds > self.clock_drift_threshold
        
        if has_drift:
            logger.warning(f"Clock drift detected for device {device_id}: {drift_seconds:.2f} seconds")
            self._log_clock_drift(device_id, drift_seconds, client_timestamp, server_time)
            
        return has_drift, drift_seconds
    
    def handle_network_partition(self, device_id: str) -> Dict:
        """
        Handle network partition scenarios
        
        Args:
            device_id: The device experiencing network issues
            
        Returns:
            Dict with partition status and recovery actions
        """
        device_role = DeviceRole.get_device_by_id(device_id)
        if not device_role:
            return {"status": "unknown_device", "actions": []}
            
        # Check if device is master and handle accordingly
        if device_role.role == 'master':
            return self._handle_master_partition(device_role)
        else:
            return self._handle_client_partition(device_role)
    
    def detect_split_brain(self) -> Tuple[bool, List[Dict]]:
        """
        Detect split-brain scenarios where multiple masters exist
        
        Returns:
            Tuple of (has_split_brain, list_of_masters)
        """
        masters = DeviceRole.query.filter_by(role='master', is_active=True).all()
        has_split_brain = len(masters) > 1
        
        if has_split_brain:
            logger.error(f"Split-brain detected: {len(masters)} active masters")
            master_info = [
                {
                    'device_id': master.device_id,
                    'priority': master.priority,
                    'last_seen': master.last_seen.isoformat() if master.last_seen else None
                }
                for master in masters
            ]
            self._log_split_brain(master_info)
            return True, master_info
            
        return False, []
    
    def resolve_split_brain(self, masters: List[Dict]) -> str:
        """
        Resolve split-brain by electing the highest priority master
        
        Args:
            masters: List of master devices
            
        Returns:
            Device ID of the elected master
        """
        if not masters:
            return None
            
        # Sort by priority (highest first), then by last_seen (most recent first)
        sorted_masters = sorted(
            masters,
            key=lambda x: (x['priority'], x['last_seen'] or datetime.datetime.min),
            reverse=True
        )
        
        elected_master = sorted_masters[0]['device_id']
        logger.info(f"Split-brain resolved: {elected_master} elected as master")
        
        # Demote other masters to clients
        for master_info in sorted_masters[1:]:
            device_role = DeviceRole.get_device_by_id(master_info['device_id'])
            if device_role:
                device_role.change_role('client', 'split_brain_resolution')
                logger.info(f"Demoted {master_info['device_id']} to client due to split-brain resolution")
        
        return elected_master
    
    def validate_data_integrity(self, device_id: str, data_hash: str, data_type: str) -> bool:
        """
        Validate data integrity for sync operations
        
        Args:
            device_id: The device sending data
            data_hash: Hash of the data for validation
            data_type: Type of data being validated
            
        Returns:
            True if data integrity is valid
        """
        # This is a simplified validation - in production, implement proper hash validation
        if not data_hash or len(data_hash) < 32:
            logger.warning(f"Invalid data hash from device {device_id} for {data_type}")
            return False
            
        # Log validation attempt
        audit_log = SyncAuditLog(
            event_type='data_validation',
            operation='integrity_check',
            status='success' if data_hash else 'failed',
            device_id=device_id,
            details=f"Data integrity check for {data_type}: {'valid' if data_hash else 'invalid'}"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return True
    
    def handle_sync_conflict(self, device_id: str, conflict_data: Dict) -> Dict:
        """
        Handle sync conflicts with intelligent resolution
        
        Args:
            device_id: The device reporting the conflict
            conflict_data: Conflict details
            
        Returns:
            Resolution strategy and actions
        """
        conflict_type = conflict_data.get('type', 'unknown')
        conflict_details = conflict_data.get('details', {})
        
        logger.info(f"Handling sync conflict for device {device_id}: {conflict_type}")
        
        resolution_strategy = self._determine_conflict_resolution(conflict_type, conflict_details)
        
        # Log conflict and resolution
        audit_log = SyncAuditLog(
            event_type='sync_conflict',
            operation='conflict_resolution',
            status='resolved',
            device_id=device_id,
            details=f"Conflict type: {conflict_type}, Resolution: {resolution_strategy['strategy']}"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return resolution_strategy
    
    def optimize_sync_performance(self, device_id: str, sync_data_size: int) -> Dict:
        """
        Optimize sync performance based on data size and device capabilities
        
        Args:
            device_id: The device performing sync
            sync_data_size: Size of data being synced in bytes
            
        Returns:
            Optimization recommendations
        """
        device_role = DeviceRole.get_device_by_id(device_id)
        if not device_role:
            return {"optimization": "none", "reason": "device_not_found"}
        
        # Simple optimization based on data size
        if sync_data_size > 1024 * 1024:  # 1MB
            optimization = {
                "optimization": "chunked_sync",
                "chunk_size": 256 * 1024,  # 256KB chunks
                "reason": "large_data_size"
            }
        elif sync_data_size > 100 * 1024:  # 100KB
            optimization = {
                "optimization": "compression",
                "compression_level": "medium",
                "reason": "medium_data_size"
            }
        else:
            optimization = {
                "optimization": "direct_sync",
                "reason": "small_data_size"
            }
        
        logger.info(f"Sync optimization for device {device_id}: {optimization['optimization']}")
        return optimization
    
    def implement_rate_limiting(self, device_id: str, operation: str) -> bool:
        """
        Implement rate limiting for sync operations
        
        Args:
            device_id: The device making the request
            operation: The operation being performed
            
        Returns:
            True if request is allowed, False if rate limited
        """
        # This is a simplified rate limiting - in production, use Redis or similar
        current_time = time.time()
        window_start = current_time - self.rate_limit_window
        
        # Count recent requests for this device
        recent_requests = SyncAuditLog.query.filter(
            SyncAuditLog.device_id == device_id,
            SyncAuditLog.created_at >= datetime.datetime.fromtimestamp(window_start)
        ).count()
        
        if recent_requests >= self.rate_limit_max_requests:
            logger.warning(f"Rate limit exceeded for device {device_id}: {recent_requests} requests")
            return False
            
        return True
    
    def graceful_degradation(self, device_id: str, error_type: str) -> Dict:
        """
        Implement graceful degradation for system failures
        
        Args:
            device_id: The device experiencing issues
            error_type: Type of error encountered
            
        Returns:
            Degradation strategy and fallback options
        """
        degradation_strategies = {
            'network_timeout': {
                'strategy': 'offline_mode',
                'fallback': 'local_operations_only',
                'recovery': 'automatic_reconnect'
            },
            'database_error': {
                'strategy': 'read_only_mode',
                'fallback': 'cache_operations',
                'recovery': 'manual_intervention_required'
            },
            'memory_overflow': {
                'strategy': 'reduced_functionality',
                'fallback': 'essential_operations_only',
                'recovery': 'restart_required'
            },
            'disk_full': {
                'strategy': 'emergency_mode',
                'fallback': 'critical_operations_only',
                'recovery': 'cleanup_required'
            }
        }
        
        strategy = degradation_strategies.get(error_type, {
            'strategy': 'unknown_error',
            'fallback': 'minimal_functionality',
            'recovery': 'manual_intervention_required'
        })
        
        logger.warning(f"Graceful degradation for device {device_id}: {error_type} -> {strategy['strategy']}")
        
        # Log degradation event
        audit_log = SyncAuditLog(
            event_type='system_degradation',
            operation='graceful_degradation',
            status='degraded',
            device_id=device_id,
            details=f"Error type: {error_type}, Strategy: {strategy['strategy']}"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return strategy
    
    def _handle_master_partition(self, device_role: DeviceRole) -> Dict:
        """Handle network partition for master device"""
        return {
            "status": "master_partition",
            "actions": [
                "trigger_master_election",
                "notify_clients_of_partition",
                "enable_offline_mode"
            ],
            "recovery_actions": [
                "wait_for_network_restoration",
                "validate_data_consistency",
                "resume_master_operations"
            ]
        }
    
    def _handle_client_partition(self, device_role: DeviceRole) -> Dict:
        """Handle network partition for client device"""
        return {
            "status": "client_partition",
            "actions": [
                "enable_offline_mode",
                "queue_local_operations",
                "attempt_reconnection"
            ],
            "recovery_actions": [
                "sync_pending_operations",
                "validate_data_consistency",
                "resume_normal_operations"
            ]
        }
    
    def _determine_conflict_resolution(self, conflict_type: str, conflict_details: Dict) -> Dict:
        """Determine the best conflict resolution strategy"""
        if conflict_type == 'timestamp_conflict':
            return {
                "strategy": "last_writer_wins",
                "resolution": "use_most_recent_timestamp",
                "priority": "high"
            }
        elif conflict_type == 'data_conflict':
            return {
                "strategy": "manual_resolution",
                "resolution": "require_user_intervention",
                "priority": "critical"
            }
        elif conflict_type == 'version_conflict':
            return {
                "strategy": "merge_attempt",
                "resolution": "attempt_automatic_merge",
                "priority": "medium"
            }
        else:
            return {
                "strategy": "default_resolution",
                "resolution": "use_device_priority",
                "priority": "low"
            }
    
    def _log_clock_drift(self, device_id: str, drift_seconds: float, 
                        client_time: datetime.datetime, server_time: datetime.datetime):
        """Log clock drift event"""
        audit_log = SyncAuditLog(
            event_type='clock_drift',
            operation='drift_detection',
            status='warning',
            device_id=device_id,
            details=f"Clock drift: {drift_seconds:.2f}s, Client: {client_time}, Server: {server_time}"
        )
        db.session.add(audit_log)
        db.session.commit()
    
    def _log_split_brain(self, master_info: List[Dict]):
        """Log split-brain detection"""
        audit_log = SyncAuditLog(
            event_type='split_brain',
            operation='detection',
            status='critical',
            device_id='system',
            details=f"Split-brain detected with {len(master_info)} masters: {master_info}"
        )
        db.session.add(audit_log)
        db.session.commit()

# Global instance
edge_case_handler = EdgeCaseHandler()
