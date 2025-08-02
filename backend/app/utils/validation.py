"""
Validation utilities for device registration and sync operations.
"""
from typing import Tuple, Dict, Any, Optional


def validate_device_registration_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Validate device registration data for both REST API and WebSocket handlers.
    
    Args:
        data: Dictionary containing device registration data
        
    Returns:
        Tuple of (is_valid, error_message, validated_data)
    """
    if not data:
        return False, "Missing request body", {}
    
    device_id = data.get('device_id')
    role = data.get('role')
    priority = data.get('priority')
    
    # Validate device_id
    if not device_id:
        return False, "Missing device_id field", {}
    
    if not isinstance(device_id, str):
        return False, "device_id must be a string", {}
    
    if len(device_id.strip()) == 0:
        return False, "device_id cannot be empty", {}
    
    if len(device_id) > 100:
        return False, "device_id too long (max 100 characters)", {}
    
    # Validate role
    if not role:
        return False, "Missing role field", {}
    
    if not isinstance(role, str):
        return False, "role must be a string", {}
    
    # Define valid roles for device registration
    valid_roles = ['admin', 'manager', 'assistant_manager', 'sales_assistant', 'master', 'client']
    if role not in valid_roles:
        return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}", {}
    
    # Validate priority
    if priority is None:
        return False, "Missing priority field", {}
    
    if not isinstance(priority, (int, float)):
        return False, "priority must be a number", {}
    
    if priority < 0 or priority > 100:
        return False, "priority must be between 0 and 100", {}
    
    # Validate device_id doesn't contain dangerous characters
    dangerous_chars = ['<', '>', '"', "'", ';', '--', '/*', '*/', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '=', '{', '}', '[', ']', '|', '\\', ':', ';', '"', "'", ',', '<', '>', '/', '?']
    for char in dangerous_chars:
        if char in device_id:
            return False, "device_id contains invalid characters", {}
    
    # Return validated data
    validated_data = {
        'device_id': device_id.strip(),
        'role': role,
        'priority': int(priority)  # Ensure it's an integer
    }
    
    return True, None, validated_data


def validate_sync_event_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Validate sync event data.
    
    Args:
        data: Dictionary containing sync event data
        
    Returns:
        Tuple of (is_valid, error_message, validated_data)
    """
    if not data:
        return False, "Missing request body", {}
    
    event_type = data.get('event_type')
    payload = data.get('payload', {})
    device_id = data.get('device_id')
    
    # Validate event_type
    if not event_type:
        return False, "Missing event_type field", {}
    
    if not isinstance(event_type, str):
        return False, "event_type must be a string", {}
    
    valid_event_types = [
        'critical_event', 'data_update', 'sync_request', 'sync_response',
        'device_online', 'device_offline', 'master_election', 'role_change'
    ]
    
    if event_type not in valid_event_types:
        return False, f"Invalid event_type. Must be one of: {', '.join(valid_event_types)}", {}
    
    # Validate device_id if present
    if device_id:
        if not isinstance(device_id, str):
            return False, "device_id must be a string", {}
        
        if len(device_id.strip()) == 0:
            return False, "device_id cannot be empty", {}
    
    # Validate payload is a dictionary
    if not isinstance(payload, dict):
        return False, "payload must be a dictionary", {}
    
    validated_data = {
        'event_type': event_type,
        'payload': payload,
        'device_id': device_id
    }
    
    return True, None, validated_data


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize a string value for safe database storage.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        raise ValueError("Value must be a string")
    
    # Remove leading/trailing whitespace
    sanitized = value.strip()
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized 