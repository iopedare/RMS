#!/usr/bin/env python3
"""
Test validation fixes for device registration and sync operations.
This test file verifies that the validation improvements address the failed test scenario.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.validation import validate_device_registration_data


def test_validation_fixes():
    """Test the validation improvements."""
    print("🧪 Testing Validation Fixes")
    print("=" * 50)
    
    # Test cases from the failed UAT scenario
    test_cases = [
        # Valid cases
        ({'device_id': 'test_device', 'role': 'admin', 'priority': 50}, True, "Valid device registration"),
        ({'device_id': 'test_device', 'role': 'manager', 'priority': 75}, True, "Valid manager role"),
        ({'device_id': 'test_device', 'role': 'assistant_manager', 'priority': 25}, True, "Valid assistant manager role"),
        ({'device_id': 'test_device', 'role': 'sales_assistant', 'priority': 10}, True, "Valid sales assistant role"),
        ({'device_id': 'test_device', 'role': 'master', 'priority': 100}, True, "Valid master role"),
        ({'device_id': 'test_device', 'role': 'client', 'priority': 0}, True, "Valid client role"),
        
        # Invalid cases that should now be caught
        ({'device_id': None, 'role': 'admin', 'priority': 100}, False, "None device_id"),
        ({'device_id': 123, 'role': 'admin', 'priority': 100}, False, "Wrong device_id type"),
        ({'device_id': '', 'role': 'admin', 'priority': 100}, False, "Empty device_id"),
        ({'device_id': 'a' * 101, 'role': 'admin', 'priority': 100}, False, "Too long device_id"),
        ({'device_id': 'test', 'role': 'invalid_role', 'priority': 100}, False, "Invalid role"),
        ({'device_id': 'test', 'role': 'admin', 'priority': -1}, False, "Negative priority"),
        ({'device_id': 'test', 'role': 'admin', 'priority': 101}, False, "Priority > 100"),
        ({'device_id': 'test', 'role': 'admin', 'priority': 'high'}, False, "Wrong priority type"),
        ({'device_id': 'test<script>', 'role': 'admin', 'priority': 100}, False, "Dangerous characters"),
        ({'device_id': 'test', 'role': None, 'priority': 100}, False, "None role"),
        ({'device_id': 'test', 'role': 'admin'}, False, "Missing priority"),
        ({}, False, "Empty request body"),
    ]
    
    passed = 0
    failed = 0
    
    for data, expected_valid, description in test_cases:
        is_valid, error_msg, validated_data = validate_device_registration_data(data)
        
        if is_valid == expected_valid:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"{status} {description}")
        if not is_valid and expected_valid:
            print(f"   Expected valid but got: {error_msg}")
        elif is_valid and not expected_valid:
            print(f"   Expected invalid but got valid")
        elif not is_valid and not expected_valid:
            print(f"   Correctly rejected: {error_msg}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All validation tests passed!")
        return True
    else:
        print("⚠️  Some validation tests failed!")
        return False


if __name__ == '__main__':
    success = test_validation_fixes()
    sys.exit(0 if success else 1) 