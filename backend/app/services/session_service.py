#!/usr/bin/env python3
"""
Session Management Service for Retail Management System.

This service handles user session management, device tracking, and single device
login enforcement based on user roles and permissions.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.models import User, AuditLog
import uuid


class SessionService:
    """
    Session management service for handling user sessions and device tracking.
    
    Provides functionality for session creation, validation, cleanup, and
    single device login enforcement based on user roles.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.session_timeout = {
            'Admin': 8 * 3600,      # 8 hours
            'Manager': 6 * 3600,     # 6 hours
            'Assistant Manager': 6 * 3600,  # 6 hours
            'Inventory Assistant': 4 * 3600,  # 4 hours
            'Sales Assistant': 4 * 3600      # 4 hours
        }
    
    def create_session(self, user_id: int, device_id: str = None, ip_address: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create a new session for a user.
        
        Args:
            user_id: User ID
            device_id: Device identifier
            ip_address: IP address for audit logging
            
        Returns:
            Tuple of (success, session_id, error_message)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.is_active:
                return False, None, "User not found or inactive"
            
            # Check single device login restriction
            if not self._can_have_multiple_sessions(user):
                # Check if user already has an active session
                if user.current_session_id:
                    return False, None, "User already has an active session on another device"
            
            # Generate new session ID
            session_id = str(uuid.uuid4())
            
            # Update user session info
            user.current_session_id = session_id
            user.device_id = device_id
            user.last_login = datetime.utcnow()
            
            self.db.commit()
            
            # Log session creation
            self._log_session_event(
                event_type="session_created",
                description=f"Session created for user '{user.username}'",
                is_success="success",
                user_id=user.id,
                session_id=session_id,
                device_id=device_id,
                ip_address=ip_address
            )
            
            return True, session_id, None
            
        except Exception as e:
            return False, None, f"Session creation error: {str(e)}"
    
    def validate_session(self, user_id: int, session_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a session is still active and valid.
        
        Args:
            user_id: User ID
            session_id: Session ID to validate
            
        Returns:
            Tuple of (valid, error_message)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.is_active:
                return False, "User not found or inactive"
            
            # Check if session ID matches
            if user.current_session_id != session_id:
                return False, "Session has been invalidated"
            
            # Check if session has expired
            if self._is_session_expired(user):
                self.invalidate_session(user_id, session_id)
                return False, "Session has expired"
            
            # Check if account is locked
            if user.is_account_locked():
                return False, "Account is locked"
            
            return True, None
            
        except Exception as e:
            return False, f"Session validation error: {str(e)}"
    
    def invalidate_session(self, user_id: int, session_id: str, ip_address: str = None) -> bool:
        """
        Invalidate a user session.
        
        Args:
            user_id: User ID
            session_id: Session ID to invalidate
            ip_address: IP address for audit logging
            
        Returns:
            True if session invalidated successfully, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            # Clear session info
            user.current_session_id = None
            user.last_logout = datetime.utcnow()
            
            self.db.commit()
            
            # Log session invalidation
            self._log_session_event(
                event_type="session_invalidated",
                description=f"Session invalidated for user '{user.username}'",
                is_success="success",
                user_id=user.id,
                session_id=session_id,
                ip_address=ip_address
            )
            
            return True
            
        except Exception as e:
            return False
    
    def refresh_session(self, user_id: int, session_id: str) -> Tuple[bool, Optional[str]]:
        """
        Refresh a user session by updating the last activity time.
        
        Args:
            user_id: User ID
            session_id: Session ID to refresh
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate session first
            is_valid, error = self.validate_session(user_id, session_id)
            if not is_valid:
                return False, error
            
            user = self.db.query(User).filter(User.id == user_id).first()
            
            # Update last login time to extend session
            user.last_login = datetime.utcnow()
            self.db.commit()
            
            return True, None
            
        except Exception as e:
            return False, f"Session refresh error: {str(e)}"
    
    def refresh_session(self, user_id: int, device_id: str = None) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Refresh user session by updating last activity.
        
        Args:
            user_id: User ID
            device_id: Device ID (optional)
            
        Returns:
            Tuple of (success, session_data, error_message)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, None, "User not found"
            
            # Update last login time
            user.last_login = datetime.utcnow()
            self.db.commit()
            
            # Get session timeout
            timeout_seconds = self._get_session_timeout(user)
            expires_at = datetime.utcnow() + timedelta(seconds=timeout_seconds)
            
            session_data = {
                'session_id': user.current_session_id,
                'expires_at': expires_at.isoformat(),
                'timeout_seconds': timeout_seconds
            }
            
            return True, session_data, None
            
        except Exception as e:
            logger.error(f"Session refresh error: {str(e)}")
            return False, None, f"Session refresh failed: {str(e)}"
    
    def get_active_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of session information dictionaries
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return []
            
            sessions = []
            
            # For single device login, only return current session
            if user.current_session_id:
                sessions.append({
                    'session_id': user.current_session_id,
                    'device_id': user.device_id,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'is_active': True
                })
            
            return sessions
            
        except Exception:
            return []
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions for all users.
        
        Returns:
            Number of sessions cleaned up
        """
        try:
            cleaned_count = 0
            users = self.db.query(User).filter(User.current_session_id.isnot(None)).all()
            
            for user in users:
                if self._is_session_expired(user):
                    user.current_session_id = None
                    cleaned_count += 1
                    
                    # Log session cleanup
                    self._log_session_event(
                        event_type="session_expired",
                        description=f"Session expired for user '{user.username}'",
                        is_success="success",
                        user_id=user.id,
                        session_id=user.current_session_id
                    )
            
            self.db.commit()
            return cleaned_count
            
        except Exception:
            return 0
    
    def get_all_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Get all active sessions (Admin only).
        
        Returns:
            List of active session data
        """
        try:
            from app.models import User
            
            # Get all users with active sessions
            users = self.db.query(User).filter(
                User.current_session_id.isnot(None),
                User.is_active == True
            ).all()
            
            sessions = []
            for user in users:
                if not self._is_session_expired(user):
                    sessions.append({
                        'session_id': user.current_session_id,
                        'user_id': user.id,
                        'username': user.username,
                        'device_id': user.device_id,
                        'ip_address': getattr(user, 'last_ip_address', None),
                        'created_at': user.last_login.isoformat() if user.last_login else None,
                        'expires_at': (user.last_login + timedelta(seconds=self._get_session_timeout(user))).isoformat() if user.last_login else None,
                        'is_active': True
                    })
            
            return sessions
            
        except Exception as e:
            logger.error(f"Get all sessions error: {str(e)}")
            return []
    
    def force_logout_user(self, user_id: int, reason: str = "Forced logout") -> bool:
        """
        Force logout a user from all devices.
        
        Args:
            user_id: User ID
            reason: Reason for forced logout
            
        Returns:
            True if logout successful, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            session_id = user.current_session_id
            
            # Clear session
            user.current_session_id = None
            user.last_logout = datetime.utcnow()
            
            self.db.commit()
            
            # Log forced logout
            self._log_session_event(
                event_type="forced_logout",
                description=f"Forced logout for user '{user.username}': {reason}",
                is_success="success",
                user_id=user.id,
                session_id=session_id
            )
            
            return True
            
        except Exception as e:
            return False
    
    def get_session_info(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive session information for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with session information
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {}
            
            return {
                'user_id': user.id,
                'username': user.username,
                'session_id': user.current_session_id,
                'device_id': user.device_id,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'last_logout': user.last_logout.isoformat() if user.last_logout else None,
                'is_session_active': user.current_session_id is not None,
                'can_override_single_device': user.can_override_single_device(),
                'session_timeout': self._get_session_timeout(user),
                'is_session_expired': self._is_session_expired(user) if user.current_session_id else False
            }
            
        except Exception:
            return {}
    
    def _can_have_multiple_sessions(self, user: User) -> bool:
        """
        Check if a user can have multiple concurrent sessions.
        
        Args:
            user: User object
            
        Returns:
            True if user can have multiple sessions, False otherwise
        """
        # Admin can have unlimited sessions
        if user.is_admin():
            return True
        
        # All other roles are limited to single device login
        return False
    
    def _get_session_timeout(self, user: User) -> int:
        """
        Get session timeout duration for a user based on their role.
        
        Args:
            user: User object
            
        Returns:
            Session timeout in seconds
        """
        # Get user's primary role
        primary_role = None
        for user_role in user.roles:
            if user_role.is_primary and user_role.role.is_active:
                primary_role = user_role.role
                break
        
        if not primary_role:
            # Default timeout if no primary role
            return 4 * 3600  # 4 hours
        
        return self.session_timeout.get(primary_role.name, 4 * 3600)
    
    def _is_session_expired(self, user: User) -> bool:
        """
        Check if a user's session has expired.
        
        Args:
            user: User object
            
        Returns:
            True if session expired, False otherwise
        """
        if not user.last_login:
            return True
        
        timeout_seconds = self._get_session_timeout(user)
        expiry_time = user.last_login + timedelta(seconds=timeout_seconds)
        
        return datetime.utcnow() > expiry_time
    
    def _log_session_event(self, event_type: str, description: str, is_success: str,
                          user_id: int = None, session_id: str = None, device_id: str = None,
                          ip_address: str = None) -> None:
        """
        Log session event to audit log.
        
        Args:
            event_type: Type of session event
            description: Event description
            is_success: Success status ('success' or 'failure')
            user_id: User ID (optional)
            session_id: Session ID (optional)
            device_id: Device ID (optional)
            ip_address: IP address (optional)
        """
        try:
            audit_log = AuditLog(
                event_type=event_type,
                event_category="session_management",
                severity="medium",
                description=description,
                is_success=is_success,
                user_id=user_id,
                session_id=session_id,
                device_id=device_id,
                ip_address=ip_address
            )
            
            self.db.add(audit_log)
            self.db.commit()
            
        except Exception:
            # Don't let audit logging errors break session management
            pass 