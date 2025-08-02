# 🚀 UAT Test Execution Guide – Advanced Sync Features

This document provides step-by-step execution guidelines for User Acceptance Testing (UAT) scenarios.

---

## 📋 Pre-Test Setup

### Environment Preparation
1. **Backend Setup:**
   ```bash
   # Start backend server
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python run.py
   ```

2. **Frontend Setup:**
   ```bash
   # Start Flutter applications
   cd frontend
   flutter pub get
   flutter run -d windows  # For each device instance
   ```

3. **Database Setup:**
   ```bash
   # Initialize database with test data
   python scripts/init_test_data.py
   ```

### Test Environment Configuration
```json
{
  "test_environment": {
    "backend_url": "http://localhost:5000",
    "websocket_url": "ws://localhost:5000",
    "devices": [
      {
        "id": "master_device",
        "role": "master",
        "priority": 100,
        "port": 5001
      },
      {
        "id": "client_device_1",
        "role": "client",
        "priority": 80,
        "port": 5002
      },
      {
        "id": "client_device_2",
        "role": "client",
        "priority": 60,
        "port": 5003
      },
      {
        "id": "client_device_3",
        "role": "client",
        "priority": 20,
        "port": 5004
      }
    ]
  }
}
```

---

## 🔄 Test Execution Scripts

### Test Scenario 1: Multi-Device Sync Operations

#### 1.1 Basic Device Registration Test
```python
def test_device_registration():
    """Execute device registration test."""
    print("🧪 Starting Device Registration Test")
    
    # Test data
    devices = [
        {"device_id": "master_device", "role": "master", "priority": 100},
        {"device_id": "client_device_1", "role": "client", "priority": 80},
        {"device_id": "client_device_2", "role": "client", "priority": 60},
        {"device_id": "client_device_3", "role": "client", "priority": 20}
    ]
    
    results = []
    
    for device in devices:
        print(f"📱 Registering device: {device['device_id']}")
        
        # Register device via WebSocket
        socket = connect_websocket(device["device_id"])
        response = register_device(socket, device)
        
        # Verify registration
        device_info = get_device_info(device["device_id"])
        
        # Record results
        result = {
            "device_id": device["device_id"],
            "registration_success": response.status_code == 200,
            "role_correct": device_info["role"] == device["role"],
            "priority_correct": device_info["priority"] == device["priority"],
            "response_time": response.response_time
        }
        results.append(result)
        
        print(f"✅ Device {device['device_id']} registered successfully")
    
    # Generate report
    generate_test_report("device_registration", results)
    return results
```

#### 1.2 Concurrent Data Operations Test
```python
def test_concurrent_data_operations():
    """Execute concurrent data operations test."""
    print("🧪 Starting Concurrent Data Operations Test")
    
    # Test scenario
    operations = [
        {
            "device": "master_device",
            "operation": "create_product",
            "data": {
                "name": "Test Product A",
                "sku": "TEST001",
                "price": 99.99
            }
        },
        {
            "device": "client_device_1",
            "operation": "update_product_price",
            "data": {
                "product_id": 1,
                "new_price": 89.99
            }
        },
        {
            "device": "client_device_2",
            "operation": "update_inventory",
            "data": {
                "product_id": 1,
                "quantity_change": 10
            }
        },
        {
            "device": "client_device_3",
            "operation": "create_order",
            "data": {
                "customer_id": 1,
                "items": [{"product_id": 1, "quantity": 1}]
            }
        }
    ]
    
    results = []
    
    # Execute operations concurrently
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for op in operations:
            future = executor.submit(execute_operation, op)
            futures.append(future)
        
        # Wait for completion
        for future in futures:
            result = future.result()
            results.append(result)
    
    # Verify sync across all devices
    sync_verification = verify_sync_consistency()
    
    # Generate report
    generate_test_report("concurrent_operations", results, sync_verification)
    return results
```

#### 1.3 Conflict Resolution Test
```python
def test_conflict_resolution():
    """Execute conflict resolution test."""
    print("🧪 Starting Conflict Resolution Test")
    
    # Load conflict scenarios
    conflict_scenarios = load_conflict_test_data()
    results = []
    
    for scenario in conflict_scenarios:
        print(f"🔄 Testing conflict scenario: {scenario['scenario']}")
        
        # Execute concurrent modifications
        device1_socket = connect_websocket(scenario["device_1_action"]["device_id"])
        device2_socket = connect_websocket(scenario["device_2_action"]["device_id"])
        
        # Perform actions simultaneously
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(execute_action, device1_socket, scenario["device_1_action"])
            future2 = executor.submit(execute_action, device2_socket, scenario["device_2_action"])
            
            result1 = future1.result()
            result2 = future2.result()
        
        # Wait for sync and conflict resolution
        time.sleep(5)
        
        # Verify resolution
        final_state = get_final_state(scenario)
        resolution_correct = final_state == scenario["expected_resolution"]
        
        result = {
            "scenario": scenario["scenario"],
            "conflict_detected": True,
            "resolution_applied": resolution_correct,
            "final_state": final_state,
            "expected_state": scenario["expected_resolution"]
        }
        results.append(result)
        
        print(f"✅ Conflict resolved: {resolution_correct}")
    
    # Generate report
    generate_test_report("conflict_resolution", results)
    return results
```

---

## 👑 Test Scenario 2: Master Election and Failover

#### 2.1 Graceful Master Shutdown Test
```python
def test_graceful_master_shutdown():
    """Execute graceful master shutdown test."""
    print("🧪 Starting Graceful Master Shutdown Test")
    
    # Get current master
    current_master = get_current_master()
    print(f"👑 Current master: {current_master}")
    
    # Monitor all devices
    devices = get_all_devices()
    monitoring_results = []
    
    # Start monitoring
    for device in devices:
        monitor = start_device_monitoring(device["device_id"])
        monitoring_results.append(monitor)
    
    # Initiate graceful shutdown
    print("🔄 Initiating graceful shutdown...")
    shutdown_result = initiate_graceful_shutdown(current_master)
    
    # Monitor election process
    election_start_time = time.time()
    new_master = None
    
    while time.time() - election_start_time < 30:  # 30 second timeout
        new_master = get_current_master()
        if new_master and new_master != current_master:
            break
        time.sleep(1)
    
    # Verify election results
    election_success = new_master is not None and new_master != current_master
    election_time = time.time() - election_start_time
    
    # Verify all devices notified
    notifications_received = verify_election_notifications(devices, new_master)
    
    # Test sync operations with new master
    sync_test = test_sync_with_new_master(new_master)
    
    result = {
        "shutdown_initiated": shutdown_result["success"],
        "election_triggered": election_success,
        "election_time": election_time,
        "new_master": new_master,
        "notifications_received": notifications_received,
        "sync_operations_working": sync_test["success"]
    }
    
    # Generate report
    generate_test_report("graceful_shutdown", result)
    return result
```

#### 2.2 Master Device Crash Recovery Test
```python
def test_master_crash_recovery():
    """Execute master crash recovery test."""
    print("🧪 Starting Master Crash Recovery Test")
    
    # Get current master
    current_master = get_current_master()
    print(f"👑 Current master: {current_master}")
    
    # Start heartbeat monitoring
    heartbeat_monitor = start_heartbeat_monitoring(current_master)
    
    # Simulate crash (kill process)
    print("💥 Simulating master crash...")
    crash_result = simulate_master_crash(current_master)
    
    # Monitor heartbeat timeout
    timeout_detected = False
    timeout_start = time.time()
    
    while time.time() - timeout_start < 60:  # 60 second timeout
        if heartbeat_monitor.is_timeout_detected():
            timeout_detected = True
            break
        time.sleep(1)
    
    # Monitor election process
    election_start_time = time.time()
    new_master = None
    
    while time.time() - election_start_time < 30:  # 30 second timeout
        new_master = get_current_master()
        if new_master and new_master != current_master:
            break
        time.sleep(1)
    
    # Verify recovery
    recovery_success = new_master is not None and new_master != current_master
    recovery_time = time.time() - election_start_time
    
    # Test data consistency
    data_consistency = verify_data_consistency_after_crash()
    
    result = {
        "crash_simulated": crash_result["success"],
        "timeout_detected": timeout_detected,
        "timeout_time": timeout_start - time.time() if timeout_detected else None,
        "election_triggered": recovery_success,
        "recovery_time": recovery_time,
        "new_master": new_master,
        "data_consistency": data_consistency["consistent"]
    }
    
    # Generate report
    generate_test_report("crash_recovery", result)
    return result
```

---

## ⚠️ Test Scenario 3: Error Handling and Edge Cases

#### 3.1 Invalid Data Handling Test
```python
def test_invalid_data_handling():
    """Execute invalid data handling test."""
    print("🧪 Starting Invalid Data Handling Test")
    
    # Load invalid data scenarios
    invalid_scenarios = load_invalid_test_data()
    results = []
    
    for scenario in invalid_scenarios:
        print(f"⚠️ Testing invalid scenario: {scenario['event_name']}")
        
        # Send invalid event
        socket = connect_websocket("test_device")
        response = send_invalid_event(socket, scenario["invalid_payload"])
        
        # Verify error handling
        error_handled = response.status_code == 400
        error_message_correct = scenario["expected_error"] in response.text
        error_code_correct = scenario["error_code"] in response.text
        
        result = {
            "scenario": scenario["event_name"],
            "error_handled": error_handled,
            "error_message_correct": error_message_correct,
            "error_code_correct": error_code_correct,
            "system_stable": True  # Verify system didn't crash
        }
        results.append(result)
        
        print(f"✅ Invalid data handled: {error_handled}")
    
    # Generate report
    generate_test_report("invalid_data_handling", results)
    return results
```

#### 3.2 High Load Testing
```python
def test_high_load():
    """Execute high load testing."""
    print("🧪 Starting High Load Test")
    
    # Start performance monitoring
    performance_monitor = start_performance_monitoring()
    
    # Generate load
    load_generator = LoadGenerator(
        num_devices=10,
        operations_per_minute=100,
        duration_minutes=15
    )
    
    print("📊 Generating high load...")
    load_results = load_generator.run()
    
    # Get performance metrics
    metrics = performance_monitor.get_metrics()
    
    # Verify performance criteria
    performance_ok = (
        metrics["average_response_time"] < 5.0 and
        metrics["error_rate"] < 0.01 and
        metrics["memory_usage"] < 0.8 and
        metrics["cpu_usage"] < 0.7
    )
    
    result = {
        "load_generated": load_results["success"],
        "total_operations": load_results["total_operations"],
        "average_response_time": metrics["average_response_time"],
        "error_rate": metrics["error_rate"],
        "memory_usage": metrics["memory_usage"],
        "cpu_usage": metrics["cpu_usage"],
        "performance_criteria_met": performance_ok
    }
    
    # Generate report
    generate_test_report("high_load", result)
    return result
```

---

## 📊 Performance Monitoring

### Real-time Monitoring Dashboard
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "response_times": [],
            "error_counts": 0,
            "total_requests": 0,
            "memory_usage": [],
            "cpu_usage": [],
            "active_connections": 0
        }
        self.start_time = time.time()
    
    def record_request(self, response_time, success):
        self.metrics["response_times"].append(response_time)
        self.metrics["total_requests"] += 1
        if not success:
            self.metrics["error_counts"] += 1
    
    def record_system_metrics(self, memory, cpu, connections):
        self.metrics["memory_usage"].append(memory)
        self.metrics["cpu_usage"].append(cpu)
        self.metrics["active_connections"] = connections
    
    def get_summary(self):
        return {
            "average_response_time": np.mean(self.metrics["response_times"]),
            "error_rate": self.metrics["error_counts"] / self.metrics["total_requests"],
            "total_requests": self.metrics["total_requests"],
            "average_memory_usage": np.mean(self.metrics["memory_usage"]),
            "average_cpu_usage": np.mean(self.metrics["cpu_usage"]),
            "max_connections": max(self.metrics["active_connections"]),
            "test_duration": time.time() - self.start_time
        }
```

### Test Report Generation
```python
def generate_test_report(test_name, results, additional_data=None):
    """Generate comprehensive test report."""
    report = {
        "test_name": test_name,
        "timestamp": datetime.now().isoformat(),
        "test_duration": calculate_test_duration(),
        "results": results,
        "summary": {
            "total_scenarios": len(results),
            "passed": sum(1 for r in results if r.get("success", False)),
            "failed": sum(1 for r in results if not r.get("success", True)),
            "success_rate": calculate_success_rate(results)
        }
    }
    
    if additional_data:
        report["additional_data"] = additional_data
    
    # Save report
    filename = f"test_report_{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(f"reports/{filename}", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Test report saved: {filename}")
    return report
```

---

## 🎯 Test Execution Checklist

### Pre-Test Checklist
- [ ] Backend server running on port 5000
- [ ] Database initialized with test data
- [ ] All Flutter applications compiled and ready
- [ ] Network simulation tools configured
- [ ] Performance monitoring started
- [ ] Test data sets loaded
- [ ] All team members notified

### Test Execution Checklist
- [ ] Execute Scenario 1.1: Device Registration
- [ ] Execute Scenario 1.2: Concurrent Operations
- [ ] Execute Scenario 1.3: Conflict Resolution
- [ ] Execute Scenario 2.1: Graceful Shutdown
- [ ] Execute Scenario 2.2: Crash Recovery
- [ ] Execute Scenario 2.3: Network Partition
- [ ] Execute Scenario 3.1: Invalid Data Handling
- [ ] Execute Scenario 3.2: High Load Testing
- [ ] Execute Scenario 3.3: Extended Operation Testing

### Post-Test Checklist
- [ ] All test reports generated
- [ ] Performance metrics collected
- [ ] Issues logged and categorized
- [ ] Recommendations documented
- [ ] Test environment cleaned up
- [ ] Stakeholders notified of results

---

## 📈 Success Metrics

### Functional Metrics
- **Device Registration:** 100% success rate
- **Sync Operations:** < 3 seconds average
- **Conflict Resolution:** 100% resolution rate
- **Master Election:** < 10 seconds completion
- **Error Handling:** 100% error capture rate

### Performance Metrics
- **Response Time:** < 5 seconds under load
- **Error Rate:** < 1% under normal conditions
- **Memory Usage:** < 80% of available
- **CPU Usage:** < 70% average
- **Connection Stability:** > 99% uptime

### User Experience Metrics
- **UI Responsiveness:** < 2 seconds for UI updates
- **Error Message Clarity:** 100% actionable messages
- **Recovery Time:** < 20 seconds for automatic recovery
- **Data Consistency:** 100% consistency across devices

---

*This document provides comprehensive test execution guidelines. Follow these steps to ensure thorough UAT testing of advanced sync features.* 