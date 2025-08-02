#!/usr/bin/env python3
"""
UAT Test Runner for Advanced Sync Features
Executes real User Acceptance Testing scenarios for the Retail Management System.
"""

import requests
import socketio
import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Any

class UATTestRunner:
    """Comprehensive UAT test runner for advanced sync features."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        self.devices = []
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": timestamp,
            "details": details
        }
        self.test_results.append(result)
        print(f"[{timestamp}] {status.upper()}: {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def test_device_registration(self):
        """Test Scenario 1.1: Basic Device Registration and Role Assignment"""
        print("\n" + "="*60)
        print("🧪 TEST SCENARIO 1.1: DEVICE REGISTRATION AND ROLE ASSIGNMENT")
        print("="*60)
        
        try:
            # Test device registration via REST API
            devices = [
                {"device_id": "master_device", "role": "admin"},
                {"device_id": "client_device_1", "role": "manager"},
                {"device_id": "client_device_2", "role": "assistant_manager"},
                {"device_id": "client_device_3", "role": "sales_assistant"}
            ]
            
            registered_devices = []
            
            for device in devices:
                print(f"📱 Registering device: {device['device_id']}")
                
                # Register device using the correct endpoint
                response = requests.post(
                    f"{self.base_url}/device/register",
                    json=device,
                    timeout=10
                )
                
                if response.status_code == 200:
                    device_info = response.json()
                    registered_devices.append(device_info)
                    print(f"    ✅ Registered: {device_info}")
                else:
                    self.log_test(f"Device Registration - {device['device_id']}", "FAILED", 
                                f"Status: {response.status_code}, Response: {response.text}")
                    return False
            
            # Test device roles endpoint
            roles_response = requests.get(f"{self.base_url}/device/roles")
            if roles_response.status_code == 200:
                roles_data = roles_response.json()
                print(f"📋 Device Roles: {roles_data}")
                
                if 'devices' in roles_data:
                    self.log_test("Device Roles API", "PASSED", f"Retrieved {len(roles_data['devices'])} devices")
                else:
                    self.log_test("Device Roles API", "FAILED", "No devices found in response")
                    return False
            else:
                self.log_test("Device Roles API", "FAILED", f"Status: {roles_response.status_code}")
                return False
            
            # Test sync status endpoint
            status_response = requests.get(f"{self.base_url}/sync/status?device_id=master_device")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"📊 Sync Status: {status_data}")
                self.log_test("Sync Status API", "PASSED", "Sync status retrieved successfully")
            else:
                self.log_test("Sync Status API", "FAILED", f"Status: {status_response.status_code}")
                return False
            
            self.log_test("Device Registration and Role Assignment", "PASSED", 
                         f"Successfully registered {len(registered_devices)} devices")
            return True
            
        except Exception as e:
            self.log_test("Device Registration and Role Assignment", "FAILED", str(e))
            return False
    
    def test_concurrent_data_operations(self):
        """Test Scenario 1.2: Concurrent Data Operations"""
        print("\n" + "="*60)
        print("🧪 TEST SCENARIO 1.2: CONCURRENT DATA OPERATIONS")
        print("="*60)
        
        try:
            # Simulate concurrent data operations from different devices
            operations = [
                {
                    "device_id": "master_device",
                    "event_type": "create_product",
                    "payload": {"name": "Product A", "price": 29.99, "category": "Electronics"}
                },
                {
                    "device_id": "client_device_1", 
                    "event_type": "update_price",
                    "payload": {"product_id": 1, "new_price": 34.99}
                },
                {
                    "device_id": "client_device_2",
                    "event_type": "add_inventory",
                    "payload": {"product_id": 1, "quantity": 50}
                },
                {
                    "device_id": "client_device_3",
                    "event_type": "create_order",
                    "payload": {"product_id": 1, "quantity": 2, "customer": "John Doe"}
                }
            ]
            
            # Execute operations concurrently
            threads = []
            results = []
            
            def execute_operation(op):
                try:
                    response = requests.post(
                        f"{self.base_url}/sync/push",
                        json=op,
                        timeout=10
                    )
                    results.append({
                        "operation": op["event_type"],
                        "device": op["device_id"],
                        "status": response.status_code,
                        "response": response.json() if response.status_code == 200 else response.text
                    })
                except Exception as e:
                    results.append({
                        "operation": op["event_type"],
                        "device": op["device_id"],
                        "status": "ERROR",
                        "response": str(e)
                    })
            
            # Start concurrent operations
            for op in operations:
                thread = threading.Thread(target=execute_operation, args=(op,))
                threads.append(thread)
                thread.start()
            
            # Wait for all operations to complete
            for thread in threads:
                thread.join()
            
            # Analyze results
            successful_ops = [r for r in results if r["status"] == 200]
            failed_ops = [r for r in results if r["status"] != 200]
            
            print(f"📊 Operation Results:")
            for result in results:
                status_icon = "✅" if result["status"] == 200 else "❌"
                print(f"    {status_icon} {result['device']} - {result['operation']}: {result['status']}")
            
            if len(successful_ops) >= 3:  # At least 3 out of 4 operations should succeed
                self.log_test("Concurrent Data Operations", "PASSED", 
                             f"{len(successful_ops)}/{len(results)} operations successful")
                return True
            else:
                self.log_test("Concurrent Data Operations", "FAILED", 
                             f"Only {len(successful_ops)}/{len(results)} operations successful")
                return False
                
        except Exception as e:
            self.log_test("Concurrent Data Operations", "FAILED", str(e))
            return False
    
    def test_conflict_resolution(self):
        """Test Scenario 1.3: Conflict Resolution Testing"""
        print("\n" + "="*60)
        print("🧪 TEST SCENARIO 1.3: CONFLICT RESOLUTION TESTING")
        print("="*60)
        
        try:
            # Create a test product first
            test_product = {
                "device_id": "master_device",
                "event_type": "create_product",
                "payload": {"name": "Test Product", "price": 25.00, "category": "Test"}
            }
            
            create_response = requests.post(
                f"{self.base_url}/sync/push",
                json=test_product,
                timeout=10
            )
            
            if create_response.status_code != 200:
                self.log_test("Conflict Resolution Setup", "FAILED", "Could not create test product")
                return False
            
            # Simulate conflicting updates
            conflicts = [
                {
                    "device_id": "master_device",
                    "event_type": "update_product",
                    "payload": {"product_id": 1, "price": 30.00, "timestamp": time.time()}
                },
                {
                    "device_id": "client_device_1", 
                    "event_type": "update_product",
                    "payload": {"product_id": 1, "price": 35.00, "timestamp": time.time() + 0.1}
                }
            ]
            
            # Execute conflicting operations
            conflict_results = []
            for conflict in conflicts:
                response = requests.post(
                    f"{self.base_url}/sync/push",
                    json=conflict,
                    timeout=10
                )
                conflict_results.append({
                    "device": conflict["device_id"],
                    "status": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text
                })
            
            # Check conflict resolution
            print(f"🔀 Conflict Resolution Results:")
            for result in conflict_results:
                status_icon = "✅" if result["status"] == 200 else "❌"
                print(f"    {status_icon} {result['device']}: {result['status']}")
            
            # Test sync pull to verify events are queued
            pull_response = requests.get(f"{self.base_url}/sync/pull?device_id=client_device_2")
            if pull_response.status_code == 200:
                pull_data = pull_response.json()
                print(f"📋 Pulled Events: {len(pull_data.get('events', []))} events")
                
                if len(pull_data.get('events', [])) > 0:
                    self.log_test("Conflict Resolution", "PASSED", 
                                 f"Events queued and available for sync")
                    return True
                else:
                    self.log_test("Conflict Resolution", "FAILED", 
                                 "No events available for sync")
                    return False
            else:
                self.log_test("Conflict Resolution", "FAILED", 
                             f"Could not pull events: {pull_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Conflict Resolution", "FAILED", str(e))
            return False
    
    def test_audit_logs(self):
        """Test Scenario 1.4: Audit Logs and Monitoring"""
        print("\n" + "="*60)
        print("🧪 TEST SCENARIO 1.4: AUDIT LOGS AND MONITORING")
        print("="*60)
        
        try:
            # Test audit logs endpoint
            audit_response = requests.get(f"{self.base_url}/sync/audit-logs")
            if audit_response.status_code == 200:
                audit_data = audit_response.json()
                print(f"📋 Audit Logs: {len(audit_data.get('logs', []))} entries")
                
                if 'logs' in audit_data:
                    self.log_test("Audit Logs API", "PASSED", 
                                 f"Retrieved {len(audit_data['logs'])} audit entries")
                else:
                    self.log_test("Audit Logs API", "FAILED", "No audit logs found")
                    return False
            else:
                self.log_test("Audit Logs API", "FAILED", f"Status: {audit_response.status_code}")
                return False
            
            # Test master election logs
            election_response = requests.get(f"{self.base_url}/sync/master-election-logs")
            if election_response.status_code == 200:
                election_data = election_response.json()
                print(f"👑 Master Election Logs: {len(election_data.get('logs', []))} entries")
                self.log_test("Master Election Logs API", "PASSED", "Election logs retrieved successfully")
            else:
                self.log_test("Master Election Logs API", "FAILED", f"Status: {election_response.status_code}")
                return False
            
            self.log_test("Audit Logs and Monitoring", "PASSED", "All monitoring endpoints working")
            return True
            
        except Exception as e:
            self.log_test("Audit Logs and Monitoring", "FAILED", str(e))
            return False
    
    def run_all_tests(self):
        """Run all UAT test scenarios."""
        print("🚀 STARTING UAT TEST EXECUTION")
        print("="*60)
        
        test_scenarios = [
            ("Device Registration and Role Assignment", self.test_device_registration),
            ("Concurrent Data Operations", self.test_concurrent_data_operations),
            ("Conflict Resolution", self.test_conflict_resolution),
            ("Audit Logs and Monitoring", self.test_audit_logs)
        ]
        
        passed_tests = 0
        total_tests = len(test_scenarios)
        
        for test_name, test_func in test_scenarios:
            try:
                if test_func():
                    passed_tests += 1
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                self.log_test(test_name, "ERROR", str(e))
                print(f"❌ {test_name} ERROR: {e}")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 UAT TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  SOME TESTS FAILED")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    # Initialize test runner
    test_runner = UATTestRunner()
    
    # Run all tests
    success = test_runner.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1) 