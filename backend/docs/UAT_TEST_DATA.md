# 📊 UAT Test Data Sets – Advanced Sync Features

This document provides comprehensive test data sets for User Acceptance Testing (UAT) scenarios.

---

## 🛍️ Retail Test Data Sets

### Product Catalog Data
```json
{
  "products": [
    {
      "id": 1,
      "name": "iPhone 15 Pro",
      "sku": "PHONE001",
      "category": "Electronics",
      "price": 999.99,
      "cost": 750.00,
      "stock": 50,
      "batch_number": "BATCH001",
      "expiry_date": "2026-12-31",
      "barcode": "1234567890123",
      "description": "Latest iPhone model with advanced features",
      "created_at": "2025-01-27T10:00:00Z",
      "updated_at": "2025-01-27T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Samsung Galaxy S24",
      "sku": "PHONE002",
      "category": "Electronics",
      "price": 899.99,
      "cost": 650.00,
      "stock": 30,
      "batch_number": "BATCH002",
      "expiry_date": "2026-12-31",
      "barcode": "1234567890124",
      "description": "Premium Android smartphone",
      "created_at": "2025-01-27T10:05:00Z",
      "updated_at": "2025-01-27T10:05:00Z"
    },
    {
      "id": 3,
      "name": "MacBook Pro 16\"",
      "sku": "LAPTOP001",
      "category": "Computers",
      "price": 2499.99,
      "cost": 1800.00,
      "stock": 15,
      "batch_number": "BATCH003",
      "expiry_date": "2026-12-31",
      "barcode": "1234567890125",
      "description": "Professional laptop for developers",
      "created_at": "2025-01-27T10:10:00Z",
      "updated_at": "2025-01-27T10:10:00Z"
    },
    {
      "id": 4,
      "name": "Dell XPS 13",
      "sku": "LAPTOP002",
      "category": "Computers",
      "price": 1299.99,
      "cost": 900.00,
      "stock": 25,
      "batch_number": "BATCH004",
      "expiry_date": "2026-12-31",
      "barcode": "1234567890126",
      "description": "Ultrabook for business users",
      "created_at": "2025-01-27T10:15:00Z",
      "updated_at": "2025-01-27T10:15:00Z"
    },
    {
      "id": 5,
      "name": "AirPods Pro",
      "sku": "AUDIO001",
      "category": "Audio",
      "price": 249.99,
      "cost": 150.00,
      "stock": 100,
      "batch_number": "BATCH005",
      "expiry_date": "2026-12-31",
      "barcode": "1234567890127",
      "description": "Wireless earbuds with noise cancellation",
      "created_at": "2025-01-27T10:20:00Z",
      "updated_at": "2025-01-27T10:20:00Z"
    }
  ]
}
```

### Customer Data
```json
{
  "customers": [
    {
      "id": 1,
      "name": "John Smith",
      "email": "john.smith@email.com",
      "phone": "+1-555-0123",
      "loyalty_points": 1500,
      "tier": "Gold",
      "created_at": "2025-01-27T10:00:00Z",
      "updated_at": "2025-01-27T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Sarah Johnson",
      "email": "sarah.johnson@email.com",
      "phone": "+1-555-0124",
      "loyalty_points": 750,
      "tier": "Silver",
      "created_at": "2025-01-27T10:05:00Z",
      "updated_at": "2025-01-27T10:05:00Z"
    },
    {
      "id": 3,
      "name": "Mike Davis",
      "email": "mike.davis@email.com",
      "phone": "+1-555-0125",
      "loyalty_points": 2500,
      "tier": "Platinum",
      "created_at": "2025-01-27T10:10:00Z",
      "updated_at": "2025-01-27T10:10:00Z"
    }
  ]
}
```

### Order Data
```json
{
  "orders": [
    {
      "id": 1,
      "customer_id": 1,
      "status": "completed",
      "total_amount": 1249.98,
      "payment_method": "credit_card",
      "items": [
        {
          "product_id": 1,
          "quantity": 1,
          "unit_price": 999.99,
          "total_price": 999.99
        },
        {
          "product_id": 5,
          "quantity": 1,
          "unit_price": 249.99,
          "total_price": 249.99
        }
      ],
      "created_at": "2025-01-27T11:00:00Z",
      "updated_at": "2025-01-27T11:30:00Z"
    },
    {
      "id": 2,
      "customer_id": 2,
      "status": "pending",
      "total_amount": 899.99,
      "payment_method": "cash",
      "items": [
        {
          "product_id": 2,
          "quantity": 1,
          "unit_price": 899.99,
          "total_price": 899.99
        }
      ],
      "created_at": "2025-01-27T12:00:00Z",
      "updated_at": "2025-01-27T12:00:00Z"
    }
  ]
}
```

---

## 🔄 Sync Conflict Test Data

### Concurrent Modification Scenarios
```json
{
  "conflict_scenarios": [
    {
      "scenario": "Price Update Conflict",
      "device_1_action": {
        "device_id": "master_device",
        "operation": "update_product_price",
        "product_id": 1,
        "new_price": 949.99,
        "timestamp": "2025-01-27T14:00:00Z"
      },
      "device_2_action": {
        "device_id": "client_device_1",
        "operation": "update_product_price",
        "product_id": 1,
        "new_price": 979.99,
        "timestamp": "2025-01-27T14:01:00Z"
      },
      "expected_resolution": "last_writer_wins",
      "expected_final_price": 979.99
    },
    {
      "scenario": "Inventory Update Conflict",
      "device_1_action": {
        "device_id": "master_device",
        "operation": "update_inventory",
        "product_id": 1,
        "quantity_change": -5,
        "timestamp": "2025-01-27T14:05:00Z"
      },
      "device_2_action": {
        "device_id": "client_device_2",
        "operation": "update_inventory",
        "product_id": 1,
        "quantity_change": -3,
        "timestamp": "2025-01-27T14:06:00Z"
      },
      "expected_resolution": "last_writer_wins",
      "expected_final_stock": 42
    },
    {
      "scenario": "Product Creation Conflict",
      "device_1_action": {
        "device_id": "master_device",
        "operation": "create_product",
        "product_data": {
          "name": "iPad Pro",
          "sku": "TABLET001",
          "price": 799.99
        },
        "timestamp": "2025-01-27T14:10:00Z"
      },
      "device_2_action": {
        "device_id": "client_device_1",
        "operation": "create_product",
        "product_data": {
          "name": "iPad Air",
          "sku": "TABLET002",
          "price": 599.99
        },
        "timestamp": "2025-01-27T14:11:00Z"
      },
      "expected_resolution": "both_products_created",
      "expected_result": "two_new_products"
    }
  ]
}
```

---

## ⚠️ Error Test Data

### Invalid WebSocket Events
```json
{
  "invalid_events": [
    {
      "event_name": "device_online",
      "invalid_payload": {
        "device_id": null,
        "role": "invalid_role"
      },
      "expected_error": "Missing device_id",
      "error_code": "4001"
    },
    {
      "event_name": "sync_request",
      "invalid_payload": {
        "device_id": "test_device",
        "sync_type": "invalid_type"
      },
      "expected_error": "Invalid sync_type",
      "error_code": "2001"
    },
    {
      "event_name": "data_update",
      "invalid_payload": {
        "device_id": "test_device",
        "table_name": "",
        "record_id": "not_a_number"
      },
      "expected_error": "Invalid record_id",
      "error_code": "2004"
    },
    {
      "event_name": "master_election",
      "invalid_payload": {
        "reason": ""
      },
      "expected_error": "Missing election reason",
      "error_code": "4003"
    }
  ]
}
```

### Malformed JSON Payloads
```json
{
  "malformed_payloads": [
    {
      "description": "Missing closing brace",
      "payload": "{\"device_id\": \"test_device\", \"role\": \"client\"",
      "expected_error": "Invalid JSON format",
      "error_code": "5001"
    },
    {
      "description": "Invalid data types",
      "payload": {
        "device_id": 123,
        "role": ["client"],
        "priority": "high"
      },
      "expected_error": "Invalid data types",
      "error_code": "2004"
    },
    {
      "description": "Extra fields",
      "payload": {
        "device_id": "test_device",
        "role": "client",
        "unknown_field": "value"
      },
      "expected_error": "Unknown field",
      "error_code": "2004"
    }
  ]
}
```

---

## 📊 Performance Test Data

### Large Data Sets
```json
{
  "large_datasets": {
    "products": {
      "count": 1000,
      "description": "Large product catalog for performance testing",
      "data_pattern": "Product {i} with SKU SKU{i:04d}"
    },
    "customers": {
      "count": 500,
      "description": "Large customer database for sync testing",
      "data_pattern": "Customer {i} with email customer{i}@test.com"
    },
    "orders": {
      "count": 200,
      "description": "Large order history for conflict testing",
      "data_pattern": "Order {i} with {random_items} items"
    }
  }
}
```

### Stress Test Scenarios
```json
{
  "stress_test_scenarios": [
    {
      "name": "High Frequency Sync",
      "description": "100 sync operations per minute",
      "duration": "30 minutes",
      "expected_performance": "Response time < 3 seconds"
    },
    {
      "name": "Concurrent Device Load",
      "description": "10 devices performing operations simultaneously",
      "duration": "15 minutes",
      "expected_performance": "No crashes, response time < 5 seconds"
    },
    {
      "name": "Large Data Transfer",
      "description": "Sync 1000 products simultaneously",
      "duration": "5 minutes",
      "expected_performance": "Complete within 60 seconds"
    },
    {
      "name": "Memory Leak Test",
      "description": "Continuous operations for 24 hours",
      "duration": "24 hours",
      "expected_performance": "Memory usage stable, no leaks"
    }
  ]
}
```

---

## 🔧 Test Automation Scripts

### Device Registration Test
```python
def test_device_registration():
    """Test device registration with different roles."""
    devices = [
        {"device_id": "master_device", "role": "master", "priority": 100},
        {"device_id": "client_device_1", "role": "client", "priority": 80},
        {"device_id": "client_device_2", "role": "client", "priority": 60},
        {"device_id": "client_device_3", "role": "client", "priority": 20}
    ]
    
    for device in devices:
        # Register device
        response = register_device(device)
        assert response.status_code == 200
        
        # Verify registration
        device_info = get_device_info(device["device_id"])
        assert device_info["role"] == device["role"]
        assert device_info["priority"] == device["priority"]
```

### Sync Conflict Test
```python
def test_sync_conflicts():
    """Test conflict resolution scenarios."""
    conflict_scenarios = load_conflict_test_data()
    
    for scenario in conflict_scenarios:
        # Perform concurrent modifications
        device1_result = perform_action(scenario["device_1_action"])
        device2_result = perform_action(scenario["device_2_action"])
        
        # Wait for sync
        time.sleep(5)
        
        # Verify resolution
        final_state = get_final_state(scenario)
        assert final_state == scenario["expected_resolution"]
```

### Performance Test
```python
def test_performance_metrics():
    """Test system performance under load."""
    # Start performance monitoring
    start_monitoring()
    
    # Perform operations
    for i in range(100):
        perform_sync_operation(i)
        time.sleep(0.1)  # 10 operations per second
    
    # Get metrics
    metrics = get_performance_metrics()
    
    # Verify performance
    assert metrics["average_response_time"] < 3.0
    assert metrics["error_rate"] < 0.01
    assert metrics["memory_usage"] < 0.8
```

---

## 📝 Test Data Generation Scripts

### Generate Test Products
```python
def generate_test_products(count=100):
    """Generate test product data."""
    products = []
    categories = ["Electronics", "Computers", "Audio", "Accessories", "Software"]
    
    for i in range(count):
        product = {
            "id": i + 1,
            "name": f"Test Product {i+1}",
            "sku": f"SKU{i+1:04d}",
            "category": categories[i % len(categories)],
            "price": round(random.uniform(10.0, 2000.0), 2),
            "cost": round(random.uniform(5.0, 1500.0), 2),
            "stock": random.randint(0, 100),
            "batch_number": f"BATCH{i+1:04d}",
            "expiry_date": "2026-12-31",
            "barcode": f"1234567890{i+1:03d}",
            "description": f"Test product description {i+1}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        products.append(product)
    
    return products
```

### Generate Test Customers
```python
def generate_test_customers(count=50):
    """Generate test customer data."""
    customers = []
    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    
    for i in range(count):
        customer = {
            "id": i + 1,
            "name": f"Test Customer {i+1}",
            "email": f"customer{i+1}@test.com",
            "phone": f"+1-555-{i+1:04d}",
            "loyalty_points": random.randint(0, 5000),
            "tier": tiers[random.randint(0, len(tiers)-1)],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        customers.append(customer)
    
    return customers
```

---

## 🎯 Test Data Validation

### Data Integrity Checks
```python
def validate_test_data():
    """Validate test data integrity."""
    # Check product data
    products = load_test_products()
    for product in products:
        assert product["id"] > 0
        assert product["price"] > 0
        assert product["cost"] > 0
        assert product["stock"] >= 0
        assert len(product["sku"]) > 0
    
    # Check customer data
    customers = load_test_customers()
    for customer in customers:
        assert customer["id"] > 0
        assert "@" in customer["email"]
        assert customer["loyalty_points"] >= 0
        assert customer["tier"] in ["Bronze", "Silver", "Gold", "Platinum"]
    
    print("✅ All test data validation passed")
```

---

*This document provides comprehensive test data sets for UAT scenarios. Update data as needed for specific testing requirements.* 