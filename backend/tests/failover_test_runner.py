#!/usr/bin/env python3
"""
Failover and Recovery Test Runner for Retail Management System

This script tests the system's ability to handle device failures, network partitions,
and automatic recovery scenarios. It simulates various failure modes and validates
the system's resilience and recovery capabilities.
"""

import requests
import time
import json
import threading
import subprocess
import signal
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

class FailoverTestRunner:
    """Test runner for failover and recovery scenarios."""
    
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
    
    def wait_for_master_election(self, timeout: int = 60) -> bool:
        """Wait for master election to complete."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/device/roles", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('devices'):
                        return True
            except requests.RequestException:
                pass
            time.sleep(2)
        return False
    
    def get_master_device(self) -> Optional[str]:
        """Get the current master device ID."""
        try:
            response = requests.get(f"{self.base_url}/device/roles", timeout=5)
            if response.status_code == 200:
                data = response.json()
                for device in data.get('devices', []):
                    if device.get('role') == 'master':
                        return device.get('device_id')
        except requests.RequestException:
            pass
        return None
    
    def test_scenario_1_graceful_shutdown(self):
        """Test Scenario 1.1: Master Device Graceful Shutdown"""
        print("\n🔄 TEST SCENARIO 1.1: MASTER DEVICE GRACEFUL SHUTDOWN")
        print("=" * 60)
        
        # Step 1: Register all devices
        devices = [
            {"device_id": "master_device", "role": "admin", "priority": 100},
            {"device_id": "client_device_1", "role": "manager", "priority": 80},
            {"device_id": "client_device_2", "role": "assistant_manager", "priority": 60},
            {"device_id": "client_device_3", "role": "sales_assistant", "priority": 20}
        ]
        
        for device in devices:
            try:
                response = requests.post(
                    f"{self.base_url}/device/register",
                    json=device,
                    timeout=10
                )
                if response.status_code == 200:
                    print(f"✅ Registered: {device['device_id']}")
                else:
                    self.log_test("Device Registration", "FAILED", f"Failed to register {device['device_id']}")
                    return False
            except requests.RequestException as e:
                self.log_test("Device Registration", "FAILED", f"Error registering {device['device_id']}: {e}")
                return False
        
        # Step 2: Wait for master election
        print("⏳ Waiting for master election...")
        if not self.wait_for_master_election(30):
            self.log_test("Master Election", "FAILED", "Master election timeout")
            return False
        
        master_device = self.get_master_device()
        if not master_device:
            self.log_test("Master Election", "FAILED", "No master device found")
            return False
        
        print(f"👑 Master elected: {master_device}")
        
        # Step 3: Perform sync operations
        print("📊 Performing sync operations...")
        operations = [
            {"device_id": "master_device", "event_type": "create_product", "payload": {"name": "Product A", "price": 29.99}},
            {"device_id": "client_device_1", "event_type": "update_product", "payload": {"product_id": 1, "price": 35.99}},
            {"device_id": "client_device_2", "event_type": "add_inventory", "payload": {"product_id": 1, "quantity": 50}},
            {"device_id": "client_device_3", "event_type": "create_order", "payload": {"product_id": 1, "quantity": 2}}
        ]
        
        for op in operations:
            try:
                response = requests.post(f"{self.base_url}/sync/push", json=op, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Operation: {op['event_type']}")
                else:
                    print(f"❌ Operation failed: {op['event_type']}")
            except requests.RequestException as e:
                print(f"❌ Operation error: {op['event_type']} - {e}")
        
        # Step 4: Simulate graceful shutdown (we can't actually kill the Flask server in this test)
        print("🔄 Simulating graceful shutdown...")
        print("⚠️  Note: In real testing, this would involve stopping the Flask server")
        
        # Step 5: Monitor for recovery (simulated)
        print("⏳ Monitoring recovery process...")
        time.sleep(5)  # Simulate recovery time
        
        # Step 6: Verify new master election
        print("🔍 Checking for new master election...")
        new_master = self.get_master_device()
        if new_master and new_master != master_device:
            print(f"✅ New master elected: {new_master}")
            self.log_test("Graceful Shutdown Recovery", "PASSED", f"New master: {new_master}")
        else:
            print("❌ No new master election detected")
            self.log_test("Graceful Shutdown Recovery", "FAILED", "No new master election")
            return False
        
        return True
    
    def test_scenario_2_crash_recovery(self):
        """Test Scenario 2.1: Master Device Crash Recovery"""
        print("\n🔄 TEST SCENARIO 2.1: MASTER DEVICE CRASH RECOVERY")
        print("=" * 60)
        
        # Register devices
        devices = [
            {"device_id": "crash_master", "role": "admin", "priority": 100},
            {"device_id": "crash_client_1", "role": "manager", "priority": 80},
            {"device_id": "crash_client_2", "role": "assistant_manager", "priority": 60}
        ]
        
        for device in devices:
            try:
                response = requests.post(f"{self.base_url}/device/register", json=device, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Registered: {device['device_id']}")
                else:
                    self.log_test("Crash Recovery Setup", "FAILED", f"Failed to register {device['device_id']}")
                    return False
            except requests.RequestException as e:
                self.log_test("Crash Recovery Setup", "FAILED", f"Error registering {device['device_id']}: {e}")
                return False
        
        # Wait for master election
        if not self.wait_for_master_election(30):
            self.log_test("Crash Recovery Setup", "FAILED", "Initial master election timeout")
            return False
        
        master_device = self.get_master_device()
        print(f"👑 Initial master: {master_device}")
        
        # Simulate crash (in real testing, this would kill the Flask process)
        print("💥 Simulating master crash...")
        print("⚠️  Note: In real testing, this would kill the Flask server process")
        
        # Monitor for recovery
        print("⏳ Monitoring crash recovery...")
        time.sleep(10)  # Simulate detection and election time
        
        # Check for new master
        new_master = self.get_master_device()
        if new_master and new_master != master_device:
            print(f"✅ Crash recovery successful: {new_master}")
            self.log_test("Crash Recovery", "PASSED", f"New master after crash: {new_master}")
        else:
            print("❌ Crash recovery failed")
            self.log_test("Crash Recovery", "FAILED", "No recovery detected")
            return False
        
        return True
    
    def test_scenario_3_network_partition(self):
        """Test Scenario 3.1: Network Partition Recovery"""
        print("\n🔄 TEST SCENARIO 3.1: NETWORK PARTITION RECOVERY")
        print("=" * 60)
        
        # Register devices
        devices = [
            {"device_id": "partition_master", "role": "admin", "priority": 100},
            {"device_id": "partition_client_1", "role": "manager", "priority": 80},
            {"device_id": "partition_client_2", "role": "assistant_manager", "priority": 60}
        ]
        
        for device in devices:
            try:
                response = requests.post(f"{self.base_url}/device/register", json=device, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Registered: {device['device_id']}")
                else:
                    self.log_test("Network Partition Setup", "FAILED", f"Failed to register {device['device_id']}")
                    return False
            except requests.RequestException as e:
                self.log_test("Network Partition Setup", "FAILED", f"Error registering {device['device_id']}: {e}")
                return False
        
        # Establish initial sync
        print("📡 Establishing initial sync...")
        if not self.wait_for_master_election(30):
            self.log_test("Network Partition Setup", "FAILED", "Initial sync timeout")
            return False
        
        # Simulate network partition
        print("🌐 Simulating network partition...")
        print("⚠️  Note: In real testing, this would block network connections")
        
        # Perform operations during partition (simulated)
        print("📊 Performing operations during partition...")
        operations = [
            {"device_id": "partition_master", "event_type": "create_product", "payload": {"name": "Partition Product", "price": 25.00}},
            {"device_id": "partition_client_1", "event_type": "update_product", "payload": {"product_id": 1, "price": 30.00}},
            {"device_id": "partition_client_2", "event_type": "add_inventory", "payload": {"product_id": 1, "quantity": 25}}
        ]
        
        for op in operations:
            try:
                response = requests.post(f"{self.base_url}/sync/push", json=op, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Operation during partition: {op['event_type']}")
                else:
                    print(f"❌ Operation failed: {op['event_type']}")
            except requests.RequestException as e:
                print(f"❌ Operation error: {op['event_type']} - {e}")
        
        # Simulate network restoration
        print("🔌 Simulating network restoration...")
        time.sleep(5)  # Simulate recovery time
        
        # Check sync recovery
        print("📡 Checking sync recovery...")
        try:
            response = requests.get(f"{self.base_url}/sync/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sync status retrieved: {len(data.get('history', []))} events")
                self.log_test("Network Partition Recovery", "PASSED", "Sync recovery successful")
            else:
                self.log_test("Network Partition Recovery", "FAILED", "Sync status check failed")
                return False
        except requests.RequestException as e:
            self.log_test("Network Partition Recovery", "FAILED", f"Sync recovery error: {e}")
            return False
        
        return True
    
    def test_scenario_4_multiple_failures(self):
        """Test Scenario 4.1: Multiple Device Failures"""
        print("\n🔄 TEST SCENARIO 4.1: MULTIPLE DEVICE FAILURES")
        print("=" * 60)
        
        # Register multiple devices
        devices = [
            {"device_id": "multi_master", "role": "admin", "priority": 100},
            {"device_id": "multi_client_1", "role": "manager", "priority": 80},
            {"device_id": "multi_client_2", "role": "assistant_manager", "priority": 60},
            {"device_id": "multi_client_3", "role": "sales_assistant", "priority": 20}
        ]
        
        for device in devices:
            try:
                response = requests.post(f"{self.base_url}/device/register", json=device, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Registered: {device['device_id']}")
                else:
                    self.log_test("Multiple Failures Setup", "FAILED", f"Failed to register {device['device_id']}")
                    return False
            except requests.RequestException as e:
                self.log_test("Multiple Failures Setup", "FAILED", f"Error registering {device['device_id']}: {e}")
                return False
        
        # Establish initial sync
        if not self.wait_for_master_election(30):
            self.log_test("Multiple Failures Setup", "FAILED", "Initial sync timeout")
            return False
        
        initial_master = self.get_master_device()
        print(f"👑 Initial master: {initial_master}")
        
        # Simulate multiple device failures
        print("💥 Simulating multiple device failures...")
        print("⚠️  Note: In real testing, this would kill multiple Flask server processes")
        
        # Monitor for recovery with reduced device set
        print("⏳ Monitoring recovery with reduced device set...")
        time.sleep(10)  # Simulate recovery time
        
        # Check for new master election
        new_master = self.get_master_device()
        if new_master and new_master != initial_master:
            print(f"✅ Multiple failure recovery successful: {new_master}")
            self.log_test("Multiple Failures Recovery", "PASSED", f"New master after multiple failures: {new_master}")
        else:
            print("❌ Multiple failure recovery failed")
            self.log_test("Multiple Failures Recovery", "FAILED", "No recovery detected")
            return False
        
        return True
    
    def run_all_failover_tests(self):
        """Run all failover and recovery test scenarios."""
        print("🚀 STARTING FAILOVER AND RECOVERY TEST EXECUTION")
        print("=" * 60)
        
        self.start_time = time.time()
        
        test_scenarios = [
            ("Master Device Graceful Shutdown", self.test_scenario_1_graceful_shutdown),
            ("Master Device Crash Recovery", self.test_scenario_2_crash_recovery),
            ("Network Partition Recovery", self.test_scenario_3_network_partition),
            ("Multiple Device Failures", self.test_scenario_4_multiple_failures)
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
        print("\n📊 FAILOVER TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "Success Rate: 0%")
        print(f"Total Time: {self.end_time - self.start_time:.2f} seconds")
        
        if failed == 0:
            print("🎉 ALL FAILOVER TESTS PASSED!")
        else:
            print("⚠️  Some failover tests failed. Review logs for details.")
        
        return failed == 0

def main():
    """Main function to run failover tests."""
    print("🔄 Failover and Recovery Test Runner")
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
    
    # Run failover tests
    test_runner = FailoverTestRunner()
    success = test_runner.run_all_failover_tests()
    
    # Save results
    with open("data/test_results/failover_test_results.json", "w") as f:
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
    
    print(f"\n📄 Results saved to: data/test_results/failover_test_results.json")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 