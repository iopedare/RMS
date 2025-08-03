#!/usr/bin/env python3
"""
Error Handling and Edge Cases Test Runner for Retail Management System

This script tests the system's ability to handle various error conditions, high load,
extended operations, and edge cases. It validates error handling, performance under
stress, and system stability.
"""

import requests
import time
import json
import threading
import concurrent.futures
import random
import string
import sys
from datetime import datetime
from typing import Dict, List, Optional

class ErrorHandlingTestRunner:
    """Test runner for error handling and edge cases."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    def log_test(self, scenario: str, status: str, details: str = ""):
        """Log test results with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "timestamp": timestamp,
            "scenario": scenario,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        print(f"[{timestamp}] {status}: {scenario}")
        if details:
            print(f"    Details: {details}")
    
    def test_scenario_1_invalid_data_handling(self):
        """Test Scenario 1: Invalid Data Handling"""
        print("\n🚨 TEST SCENARIO 1: INVALID DATA HANDLING")
        print("=" * 60)
        
        test_cases = [
            # Malformed JSON payloads
            {"name": "Missing Device ID", "payload": {"role": "admin", "priority": 100}},
            {"name": "Invalid JSON", "payload": '{"device_id": "test", "role": "admin", priority: 100}'},
            {"name": "Wrong Data Type", "payload": {"device_id": 123, "role": "admin", "priority": "high"}},
            {"name": "Null Values", "payload": {"device_id": None, "role": "admin", "priority": 100}},
            
            # Invalid device IDs and parameters
            {"name": "Empty Device ID", "payload": {"device_id": "", "role": "admin", "priority": 100}},
            {"name": "Special Characters", "payload": {"device_id": "device@#$%^&*()", "role": "admin", "priority": 100}},
            {"name": "Very Long ID", "payload": {"device_id": "a" * 1000, "role": "admin", "priority": 100}},
            {"name": "Invalid Role", "payload": {"device_id": "test", "role": "invalid_role", "priority": 100}},
            {"name": "Negative Priority", "payload": {"device_id": "test", "role": "admin", "priority": -1}},
            
            # Missing required fields
            {"name": "No Payload", "payload": {}},
            {"name": "Missing Role", "payload": {"device_id": "test", "priority": 100}},
            {"name": "Missing Priority", "payload": {"device_id": "test", "role": "admin"}},
            {"name": "All Null", "payload": {"device_id": None, "role": None, "priority": None}},
            {"name": "Empty Strings", "payload": {"device_id": "", "role": "", "priority": 0}},
        ]
        
        passed = 0
        failed = 0
        
        for test_case in test_cases:
            try:
                if isinstance(test_case["payload"], str):
                    # Invalid JSON string
                    response = requests.post(
                        f"{self.base_url}/device/register",
                        data=test_case["payload"],
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                else:
                    # Invalid payload object
                    response = requests.post(
                        f"{self.base_url}/device/register",
                        json=test_case["payload"],
                        timeout=10
                    )
                
                # Check if we got a proper error response
                if response.status_code in [400, 422, 500]:
                    print(f"✅ {test_case['name']}: Proper error response ({response.status_code})")
                    passed += 1
                else:
                    print(f"❌ {test_case['name']}: Unexpected response ({response.status_code})")
                    failed += 1
                    
            except requests.RequestException as e:
                print(f"✅ {test_case['name']}: Request failed as expected ({e})")
                passed += 1
        
        print(f"\n📊 Invalid Data Handling Results:")
        print(f"Passed: {passed}, Failed: {failed}")
        
        if failed == 0:
            self.log_test("Invalid Data Handling", "PASSED", f"All {passed} test cases handled properly")
            return True
        else:
            self.log_test("Invalid Data Handling", "FAILED", f"{failed} test cases failed")
            return False
    
    def test_scenario_2_high_load_testing(self):
        """Test Scenario 2: High Load Testing"""
        print("\n🚨 TEST SCENARIO 2: HIGH LOAD TESTING")
        print("=" * 60)
        
        # Test concurrent device registration
        print("📊 Testing concurrent device registration...")
        
        def register_device(device_id):
            try:
                payload = {
                    "device_id": f"load_test_{device_id}",
                    "role": "manager",
                    "priority": random.randint(1, 100)
                }
                response = requests.post(f"{self.base_url}/device/register", json=payload, timeout=10)
                return response.status_code == 200
            except:
                return False
        
        # Test with 20 concurrent devices
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(register_device, i) for i in range(20)]
            results = [future.result() for future in futures]
        
        successful_registrations = sum(results)
        print(f"✅ Concurrent Registration: {successful_registrations}/20 devices registered")
        
        # Test rapid sync operations
        print("📊 Testing rapid sync operations...")
        
        def perform_sync_operation(operation_id):
            try:
                payload = {
                    "device_id": f"load_test_{operation_id % 5}",
                    "event_type": "create_product",
                    "payload": {
                        "name": f"Load Test Product {operation_id}",
                        "price": random.uniform(10.0, 100.0),
                        "category": "Load Test"
                    }
                }
                response = requests.post(f"{self.base_url}/sync/push", json=payload, timeout=10)
                return response.status_code == 200
            except:
                return False
        
        # Test with 50 rapid operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(perform_sync_operation, i) for i in range(50)]
            results = [future.result() for future in futures]
        
        successful_operations = sum(results)
        print(f"✅ Rapid Sync Operations: {successful_operations}/50 operations completed")
        
        # Test large payloads
        print("📊 Testing large payloads...")
        
        large_payload = {
            "device_id": "large_payload_test",
            "event_type": "create_product",
            "payload": {
                "name": "Large Product",
                "description": "A" * 10000,  # 10KB description
                "price": 99.99,
                "category": "Large Test"
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/sync/push", json=large_payload, timeout=30)
            if response.status_code == 200:
                print("✅ Large Payload: Successfully handled large payload")
                large_payload_success = True
            else:
                print(f"❌ Large Payload: Failed with status {response.status_code}")
                large_payload_success = False
        except requests.RequestException as e:
            print(f"❌ Large Payload: Request failed ({e})")
            large_payload_success = False
        
        # Overall assessment
        if successful_registrations >= 15 and successful_operations >= 40 and large_payload_success:
            self.log_test("High Load Testing", "PASSED", 
                         f"Registration: {successful_registrations}/20, Operations: {successful_operations}/50, Large Payload: OK")
            return True
        else:
            self.log_test("High Load Testing", "FAILED", 
                         f"Registration: {successful_registrations}/20, Operations: {successful_operations}/50, Large Payload: {'OK' if large_payload_success else 'FAIL'}")
            return False
    
    def test_scenario_3_extended_operation_testing(self):
        """Test Scenario 3: Extended Operation Testing"""
        print("\n🚨 TEST SCENARIO 3: EXTENDED OPERATION TESTING")
        print("=" * 60)
        
        print("⏳ Running extended operation test (5 minutes)...")
        
        start_time = time.time()
        operation_count = 0
        successful_operations = 0
        
        # Run operations for 5 minutes
        while time.time() - start_time < 300:  # 5 minutes
            try:
                # Perform a sync operation
                payload = {
                    "device_id": f"extended_test_{operation_count % 10}",
                    "event_type": "create_product",
                    "payload": {
                        "name": f"Extended Test Product {operation_count}",
                        "price": random.uniform(10.0, 100.0),
                        "category": "Extended Test"
                    }
                }
                
                response = requests.post(f"{self.base_url}/sync/push", json=payload, timeout=10)
                if response.status_code == 200:
                    successful_operations += 1
                
                operation_count += 1
                
                # Progress indicator
                if operation_count % 10 == 0:
                    elapsed = time.time() - start_time
                    print(f"⏳ Progress: {operation_count} operations, {elapsed:.1f}s elapsed")
                
                time.sleep(1)  # 1 second between operations
                
            except requests.RequestException as e:
                print(f"⚠️  Operation {operation_count} failed: {e}")
                operation_count += 1
                time.sleep(1)
        
        elapsed_time = time.time() - start_time
        success_rate = (successful_operations / operation_count * 100) if operation_count > 0 else 0
        
        print(f"\n📊 Extended Operation Results:")
        print(f"Total Operations: {operation_count}")
        print(f"Successful Operations: {successful_operations}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Time: {elapsed_time:.1f} seconds")
        
        if success_rate >= 90 and operation_count >= 50:
            self.log_test("Extended Operation Testing", "PASSED", 
                         f"Success rate: {success_rate:.1f}%, Operations: {operation_count}")
            return True
        else:
            self.log_test("Extended Operation Testing", "FAILED", 
                         f"Success rate: {success_rate:.1f}%, Operations: {operation_count}")
            return False
    
    def test_scenario_4_edge_case_testing(self):
        """Test Scenario 4: Edge Case Testing"""
        print("\n🚨 TEST SCENARIO 4: EDGE CASE TESTING")
        print("=" * 60)
        
        edge_cases = [
            # Empty and null values
            {"name": "Empty Strings", "payload": {"device_id": "", "role": "", "priority": 0}},
            {"name": "Null Values", "payload": {"device_id": None, "role": None, "priority": None}},
            {"name": "Whitespace Only", "payload": {"device_id": "   ", "role": "admin", "priority": 100}},
            {"name": "Zero Values", "payload": {"device_id": "test", "role": "admin", "priority": 0}},
            
            # Special characters and unicode
            {"name": "Special Characters", "payload": {"device_id": "device@#$%^&*()", "role": "admin", "priority": 100}},
            {"name": "Unicode Characters", "payload": {"device_id": "设备_123", "role": "admin", "priority": 100}},
            {"name": "Emoji", "payload": {"device_id": "device🚀", "role": "admin", "priority": 100}},
            {"name": "SQL Injection Attempt", "payload": {"device_id": "'; DROP TABLE users; --", "role": "admin", "priority": 100}},
            {"name": "XSS Attempt", "payload": {"device_id": "<script>alert('xss')</script>", "role": "admin", "priority": 100}},
            
            # Boundary values
            {"name": "Maximum Integer", "payload": {"device_id": "test", "role": "admin", "priority": 2147483647}},
            {"name": "Negative Values", "payload": {"device_id": "test", "role": "admin", "priority": -1}},
            {"name": "Floating Point", "payload": {"device_id": "test", "role": "admin", "priority": 100.5}},
            {"name": "Very Large String", "payload": {"device_id": "a" * 1000, "role": "admin", "priority": 100}},
        ]
        
        passed = 0
        failed = 0
        
        for test_case in edge_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/device/register",
                    json=test_case["payload"],
                    timeout=10
                )
                
                # Check if we got a proper response (either success or error)
                if response.status_code in [200, 400, 422]:
                    print(f"✅ {test_case['name']}: Proper response ({response.status_code})")
                    passed += 1
                else:
                    print(f"❌ {test_case['name']}: Unexpected response ({response.status_code})")
                    failed += 1
                    
            except requests.RequestException as e:
                print(f"✅ {test_case['name']}: Request handled ({e})")
                passed += 1
        
        print(f"\n📊 Edge Case Testing Results:")
        print(f"Passed: {passed}, Failed: {failed}")
        
        if failed == 0:
            self.log_test("Edge Case Testing", "PASSED", f"All {passed} edge cases handled properly")
            return True
        else:
            self.log_test("Edge Case Testing", "FAILED", f"{failed} edge cases failed")
            return False
    
    def run_all_error_handling_tests(self):
        """Run all error handling and edge case test scenarios."""
        print("🚀 STARTING ERROR HANDLING AND EDGE CASE TEST EXECUTION")
        print("=" * 60)
        
        self.start_time = time.time()
        
        test_scenarios = [
            ("Invalid Data Handling", self.test_scenario_1_invalid_data_handling),
            ("High Load Testing", self.test_scenario_2_high_load_testing),
            ("Extended Operation Testing", self.test_scenario_3_extended_operation_testing),
            ("Edge Case Testing", self.test_scenario_4_edge_case_testing)
        ]
        
        passed = 0
        failed = 0
        
        for scenario_name, test_func in test_scenarios:
            try:
                if test_func():
                    passed += 1
                    self.log_test(scenario_name, "PASSED", "Test completed successfully")
                else:
                    failed += 1
                    self.log_test(scenario_name, "FAILED", "Test failed")
            except Exception as e:
                failed += 1
                self.log_test(scenario_name, "ERROR", f"Test error: {e}")
        
        self.end_time = time.time()
        
        # Print summary
        print("\n📊 ERROR HANDLING TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "Success Rate: 0%")
        print(f"Total Time: {self.end_time - self.start_time:.2f} seconds")
        
        if failed == 0:
            print("🎉 ALL ERROR HANDLING TESTS PASSED!")
        else:
            print("⚠️  Some error handling tests failed. Review logs for details.")
        
        return failed == 0

def main():
    """Main function to run error handling tests."""
    print("🚨 Error Handling and Edge Cases Test Runner")
    print("=" * 50)
    
    # Check if Flask server is running
    try:
        response = requests.get("http://localhost:5000/device/roles", timeout=5)
        if response.status_code != 200:
            print("❌ Flask server not responding properly")
            return False
    except requests.RequestException:
        print("❌ Flask server not running. Please start the server first:")
        print("   cd backend && flask run")
        return False
    
    # Run error handling tests
    test_runner = ErrorHandlingTestRunner()
    success = test_runner.run_all_error_handling_tests()
    
    # Save results
    with open("data/test_results/error_handling_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": test_runner.test_results,
            "summary": {
                "total_tests": len(test_runner.test_results),
                "passed": len([r for r in test_runner.test_results if r["status"] == "PASSED"]),
                "failed": len([r for r in test_runner.test_results if r["status"] in ["FAILED", "ERROR"]]),
                "duration": test_runner.end_time - test_runner.start_time if test_runner.end_time else 0
            }
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: data/test_results/error_handling_test_results.json")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 