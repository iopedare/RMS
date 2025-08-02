#!/usr/bin/env python3
"""
Enhanced Failover and Recovery Test Runner for Retail Management System

This script tests the system's ability to handle device failures, network partitions,
and automatic recovery scenarios by actually stopping and restarting the Flask server.
"""

import requests
import time
import json
import subprocess
import signal
import os
import sys
import threading
from datetime import datetime
from typing import Dict, List, Optional

class EnhancedFailoverTestRunner:
    """Enhanced test runner for failover and recovery scenarios."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        self.start_time = None
        self.end_time = None
        self.flask_process = None
        
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
    
    def start_flask_server(self):
        """Start Flask server in background."""
        print("🚀 Starting Flask server...")
        try:
            # Start Flask server in background
            self.flask_process = subprocess.Popen(
                ["flask", "run"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Wait for server to start
            time.sleep(5)
            
            # Check if server is responding
            for i in range(10):
                try:
                    response = requests.get(f"{self.base_url}/device/roles", timeout=5)
                    if response.status_code == 200:
                        print("✅ Flask server started successfully")
                        return True
                except requests.RequestException:
                    pass
                time.sleep(2)
            
            print("❌ Flask server failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Error starting Flask server: {e}")
            return False
    
    def stop_flask_server(self):
        """Stop Flask server."""
        print("🛑 Stopping Flask server...")
        if self.flask_process:
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=10)
                print("✅ Flask server stopped successfully")
                return True
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing Flask server...")
                self.flask_process.kill()
                return True
            except Exception as e:
                print(f"❌ Error stopping Flask server: {e}")
                return False
        return True
    
    def wait_for_server_ready(self, timeout: int = 30) -> bool:
        """Wait for server to be ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/device/roles", timeout=5)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            time.sleep(2)
        return False
    
    def register_devices(self, devices: List[Dict]) -> bool:
        """Register multiple devices."""
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
                    print(f"❌ Failed to register {device['device_id']}")
                    return False
            except requests.RequestException as e:
                print(f"❌ Error registering {device['device_id']}: {e}")
                return False
        return True
    
    def perform_sync_operations(self, operations: List[Dict]) -> bool:
        """Perform sync operations."""
        for op in operations:
            try:
                response = requests.post(f"{self.base_url}/sync/push", json=op, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Operation: {op['event_type']}")
                else:
                    print(f"❌ Operation failed: {op['event_type']}")
            except requests.RequestException as e:
                print(f"❌ Operation error: {op['event_type']} - {e}")
        return True
    
    def test_scenario_1_graceful_shutdown(self):
        """Test Scenario 1.1: Master Device Graceful Shutdown"""
        print("\n🔄 TEST SCENARIO 1.1: MASTER DEVICE GRACEFUL SHUTDOWN")
        print("=" * 60)
        
        # Step 1: Start Flask server
        if not self.start_flask_server():
            self.log_test("Graceful Shutdown Setup", "FAILED", "Failed to start Flask server")
            return False
        
        # Step 2: Register devices
        devices = [
            {"device_id": "graceful_master", "role": "admin", "priority": 100},
            {"device_id": "graceful_client_1", "role": "manager", "priority": 80},
            {"device_id": "graceful_client_2", "role": "assistant_manager", "priority": 60}
        ]
        
        if not self.register_devices(devices):
            self.log_test("Graceful Shutdown Setup", "FAILED", "Failed to register devices")
            return False
        
        # Step 3: Perform sync operations
        operations = [
            {"device_id": "graceful_master", "event_type": "create_product", "payload": {"name": "Graceful Product", "price": 29.99}},
            {"device_id": "graceful_client_1", "event_type": "update_product", "payload": {"product_id": 1, "price": 35.99}},
            {"device_id": "graceful_client_2", "event_type": "add_inventory", "payload": {"product_id": 1, "quantity": 50}}
        ]
        
        self.perform_sync_operations(operations)
        
        # Step 4: Gracefully shutdown Flask server
        print("🔄 Gracefully shutting down Flask server...")
        if not self.stop_flask_server():
            self.log_test("Graceful Shutdown", "FAILED", "Failed to stop Flask server")
            return False
        
        # Step 5: Wait for shutdown to complete
        time.sleep(3)
        
        # Step 6: Restart Flask server
        print("🔄 Restarting Flask server...")
        if not self.start_flask_server():
            self.log_test("Graceful Shutdown Recovery", "FAILED", "Failed to restart Flask server")
            return False
        
        # Step 7: Verify system recovery
        print("🔍 Verifying system recovery...")
        if self.wait_for_server_ready(30):
            print("✅ System recovered successfully")
            self.log_test("Graceful Shutdown Recovery", "PASSED", "System recovered after graceful shutdown")
            return True
        else:
            print("❌ System recovery failed")
            self.log_test("Graceful Shutdown Recovery", "FAILED", "System did not recover")
            return False
    
    def test_scenario_2_crash_recovery(self):
        """Test Scenario 2.1: Master Device Crash Recovery"""
        print("\n🔄 TEST SCENARIO 2.1: MASTER DEVICE CRASH RECOVERY")
        print("=" * 60)
        
        # Step 1: Start Flask server
        if not self.start_flask_server():
            self.log_test("Crash Recovery Setup", "FAILED", "Failed to start Flask server")
            return False
        
        # Step 2: Register devices
        devices = [
            {"device_id": "crash_master", "role": "admin", "priority": 100},
            {"device_id": "crash_client_1", "role": "manager", "priority": 80},
            {"device_id": "crash_client_2", "role": "assistant_manager", "priority": 60}
        ]
        
        if not self.register_devices(devices):
            self.log_test("Crash Recovery Setup", "FAILED", "Failed to register devices")
            return False
        
        # Step 3: Perform sync operations
        operations = [
            {"device_id": "crash_master", "event_type": "create_product", "payload": {"name": "Crash Product", "price": 25.00}},
            {"device_id": "crash_client_1", "event_type": "update_product", "payload": {"product_id": 1, "price": 30.00}},
            {"device_id": "crash_client_2", "event_type": "add_inventory", "payload": {"product_id": 1, "quantity": 25}}
        ]
        
        self.perform_sync_operations(operations)
        
        # Step 4: Simulate crash (force kill)
        print("💥 Simulating crash (force killing Flask server)...")
        if self.flask_process:
            try:
                self.flask_process.kill()  # Force kill
                print("✅ Flask server crashed")
            except Exception as e:
                print(f"❌ Error crashing Flask server: {e}")
                return False
        
        # Step 5: Wait for crash to complete
        time.sleep(2)
        
        # Step 6: Restart Flask server
        print("🔄 Restarting Flask server after crash...")
        if not self.start_flask_server():
            self.log_test("Crash Recovery", "FAILED", "Failed to restart Flask server after crash")
            return False
        
        # Step 7: Verify system recovery
        print("🔍 Verifying crash recovery...")
        if self.wait_for_server_ready(30):
            print("✅ Crash recovery successful")
            self.log_test("Crash Recovery", "PASSED", "System recovered after crash")
            return True
        else:
            print("❌ Crash recovery failed")
            self.log_test("Crash Recovery", "FAILED", "System did not recover after crash")
            return False
    
    def test_scenario_3_network_partition_simulation(self):
        """Test Scenario 3.1: Network Partition Recovery (Simulated)"""
        print("\n🔄 TEST SCENARIO 3.1: NETWORK PARTITION RECOVERY (SIMULATED)")
        print("=" * 60)
        
        # Step 1: Start Flask server
        if not self.start_flask_server():
            self.log_test("Network Partition Setup", "FAILED", "Failed to start Flask server")
            return False
        
        # Step 2: Register devices
        devices = [
            {"device_id": "partition_master", "role": "admin", "priority": 100},
            {"device_id": "partition_client_1", "role": "manager", "priority": 80},
            {"device_id": "partition_client_2", "role": "assistant_manager", "priority": 60}
        ]
        
        if not self.register_devices(devices):
            self.log_test("Network Partition Setup", "FAILED", "Failed to register devices")
            return False
        
        # Step 3: Perform initial operations
        operations = [
            {"device_id": "partition_master", "event_type": "create_product", "payload": {"name": "Partition Product", "price": 25.00}},
            {"device_id": "partition_client_1", "event_type": "update_product", "payload": {"product_id": 1, "price": 30.00}},
            {"device_id": "partition_client_2", "event_type": "add_inventory", "payload": {"product_id": 1, "quantity": 25}}
        ]
        
        self.perform_sync_operations(operations)
        
        # Step 4: Simulate network partition (stop server)
        print("🌐 Simulating network partition (stopping server)...")
        if not self.stop_flask_server():
            self.log_test("Network Partition", "FAILED", "Failed to simulate network partition")
            return False
        
        # Step 5: Wait during partition
        print("⏳ Waiting during network partition...")
        time.sleep(5)
        
        # Step 6: Restore network (restart server)
        print("🔌 Restoring network (restarting server)...")
        if not self.start_flask_server():
            self.log_test("Network Partition Recovery", "FAILED", "Failed to restore network")
            return False
        
        # Step 7: Verify recovery
        print("🔍 Verifying network partition recovery...")
        if self.wait_for_server_ready(30):
            print("✅ Network partition recovery successful")
            self.log_test("Network Partition Recovery", "PASSED", "System recovered from network partition")
            return True
        else:
            print("❌ Network partition recovery failed")
            self.log_test("Network Partition Recovery", "FAILED", "System did not recover from network partition")
            return False
    
    def test_scenario_4_multiple_failures(self):
        """Test Scenario 4.1: Multiple Device Failures (Simulated)"""
        print("\n🔄 TEST SCENARIO 4.1: MULTIPLE DEVICE FAILURES (SIMULATED)")
        print("=" * 60)
        
        # Step 1: Start Flask server
        if not self.start_flask_server():
            self.log_test("Multiple Failures Setup", "FAILED", "Failed to start Flask server")
            return False
        
        # Step 2: Register multiple devices
        devices = [
            {"device_id": "multi_master", "role": "admin", "priority": 100},
            {"device_id": "multi_client_1", "role": "manager", "priority": 80},
            {"device_id": "multi_client_2", "role": "assistant_manager", "priority": 60},
            {"device_id": "multi_client_3", "role": "sales_assistant", "priority": 20}
        ]
        
        if not self.register_devices(devices):
            self.log_test("Multiple Failures Setup", "FAILED", "Failed to register devices")
            return False
        
        # Step 3: Perform operations
        operations = [
            {"device_id": "multi_master", "event_type": "create_product", "payload": {"name": "Multi Product", "price": 40.00}},
            {"device_id": "multi_client_1", "event_type": "update_product", "payload": {"product_id": 1, "price": 45.00}},
            {"device_id": "multi_client_2", "event_type": "add_inventory", "payload": {"product_id": 1, "quantity": 100}},
            {"device_id": "multi_client_3", "event_type": "create_order", "payload": {"product_id": 1, "quantity": 5}}
        ]
        
        self.perform_sync_operations(operations)
        
        # Step 4: Simulate multiple failures (restart server multiple times)
        print("💥 Simulating multiple failures (multiple restarts)...")
        
        for i in range(3):
            print(f"🔄 Restart {i+1}/3...")
            
            # Stop server
            if not self.stop_flask_server():
                print(f"❌ Failed to stop server on restart {i+1}")
                return False
            
            time.sleep(2)
            
            # Start server
            if not self.start_flask_server():
                print(f"❌ Failed to start server on restart {i+1}")
                return False
            
            # Wait for recovery
            if not self.wait_for_server_ready(20):
                print(f"❌ Failed to recover on restart {i+1}")
                return False
            
            print(f"✅ Restart {i+1} successful")
        
        print("✅ Multiple failures simulation successful")
        self.log_test("Multiple Failures Recovery", "PASSED", "System handled multiple failures successfully")
        return True
    
    def run_all_enhanced_failover_tests(self):
        """Run all enhanced failover and recovery test scenarios."""
        print("🚀 STARTING ENHANCED FAILOVER AND RECOVERY TEST EXECUTION")
        print("=" * 60)
        
        self.start_time = time.time()
        
        test_scenarios = [
            ("Master Device Graceful Shutdown", self.test_scenario_1_graceful_shutdown),
            ("Master Device Crash Recovery", self.test_scenario_2_crash_recovery),
            ("Network Partition Recovery", self.test_scenario_3_network_partition_simulation),
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
        
        # Ensure Flask server is stopped
        self.stop_flask_server()
        
        # Print summary
        print("\n📊 ENHANCED FAILOVER TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "Success Rate: 0%")
        print(f"Total Time: {self.end_time - self.start_time:.2f} seconds")
        
        if failed == 0:
            print("🎉 ALL ENHANCED FAILOVER TESTS PASSED!")
        else:
            print("⚠️  Some enhanced failover tests failed. Review logs for details.")
        
        return failed == 0

def main():
    """Main function to run enhanced failover tests."""
    print("🔄 Enhanced Failover and Recovery Test Runner")
    print("=" * 50)
    
    # Run enhanced failover tests
    test_runner = EnhancedFailoverTestRunner()
    success = test_runner.run_all_enhanced_failover_tests()
    
    # Save results
    with open("data/test_results/enhanced_failover_test_results.json", "w") as f:
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
    
    print(f"\n📄 Results saved to: data/test_results/enhanced_failover_test_results.json")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 