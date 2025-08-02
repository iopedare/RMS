# 🧪 Frontend UAT Testing Guide – Advanced Sync Features

This document provides frontend-specific testing guidelines for Flutter applications during UAT.

---

## 📱 Frontend Test Environment Setup

### Multi-Device Flutter Setup
```bash
# Device 1: Master Device (Admin)
cd frontend
flutter run -d windows --dart-define=DEVICE_ID=master_device --dart-define=DEVICE_ROLE=master --dart-define=DEVICE_PRIORITY=100

# Device 2: Client Device 1 (Manager)
cd frontend
flutter run -d windows --dart-define=DEVICE_ID=client_device_1 --dart-define=DEVICE_ROLE=client --dart-define=DEVICE_PRIORITY=80

# Device 3: Client Device 2 (Assistant Manager)
cd frontend
flutter run -d windows --dart-define=DEVICE_ID=client_device_2 --dart-define=DEVICE_ROLE=client --dart-define=DEVICE_PRIORITY=60

# Device 4: Client Device 3 (Sales Assistant)
cd frontend
flutter run -d windows --dart-define=DEVICE_ID=client_device_3 --dart-define=DEVICE_ROLE=client --dart-define=DEVICE_PRIORITY=20
```

### Frontend Configuration
```dart
// lib/config/device_config.dart
class DeviceConfig {
  static const String deviceId = String.fromEnvironment('DEVICE_ID', defaultValue: 'unknown');
  static const String deviceRole = String.fromEnvironment('DEVICE_ROLE', defaultValue: 'client');
  static const int devicePriority = int.fromEnvironment('DEVICE_PRIORITY', defaultValue: 0);
  
  static const String backendUrl = 'http://localhost:5000';
  static const String websocketUrl = 'ws://localhost:5000';
}
```

---

## 🔄 Frontend Test Scenarios

### Scenario 1: Device Registration and UI Updates

#### 1.1 Device Registration Test
```dart
// Test device registration and UI updates
void testDeviceRegistration() async {
  print('🧪 Testing Device Registration');
  
  // Initialize device
  await deviceService.initialize();
  
  // Verify registration
  final deviceInfo = await deviceService.getDeviceInfo();
  assert(deviceInfo.deviceId == DeviceConfig.deviceId);
  assert(deviceInfo.role == DeviceConfig.deviceRole);
  assert(deviceInfo.priority == DeviceConfig.devicePriority);
  
  // Verify UI updates
  expect(find.text('Connected'), findsOneWidget);
  expect(find.text('Device: ${DeviceConfig.deviceId}'), findsOneWidget);
  expect(find.text('Role: ${DeviceConfig.deviceRole}'), findsOneWidget);
  
  print('✅ Device registration test passed');
}
```

#### 1.2 Master Election UI Test
```dart
// Test master election UI updates
void testMasterElectionUI() async {
  print('🧪 Testing Master Election UI');
  
  // Wait for master election
  await Future.delayed(Duration(seconds: 10));
  
  // Verify master election UI
  final currentMaster = await syncService.getCurrentMaster();
  if (DeviceConfig.deviceId == currentMaster) {
    expect(find.text('👑 Master Device'), findsOneWidget);
    expect(find.text('Admin Controls'), findsOneWidget);
  } else {
    expect(find.text('📱 Client Device'), findsOneWidget);
    expect(find.text('Connected to: $currentMaster'), findsOneWidget);
  }
  
  print('✅ Master election UI test passed');
}
```

### Scenario 2: Data Sync and UI Updates

#### 2.1 Product Creation Sync Test
```dart
// Test product creation and sync across devices
void testProductCreationSync() async {
  print('🧪 Testing Product Creation Sync');
  
  // Create product on master device
  if (DeviceConfig.deviceRole == 'master') {
    final product = Product(
      name: 'Test Product A',
      sku: 'TEST001',
      price: 99.99,
      stock: 50,
    );
    
    await productService.createProduct(product);
    
    // Verify local UI update
    expect(find.text('Test Product A'), findsOneWidget);
    expect(find.text('\$99.99'), findsOneWidget);
  }
  
  // Wait for sync
  await Future.delayed(Duration(seconds: 3));
  
  // Verify sync on all devices
  final products = await productService.getAllProducts();
  final testProduct = products.firstWhere((p) => p.sku == 'TEST001');
  expect(testProduct.name, 'Test Product A');
  expect(testProduct.price, 99.99);
  
  print('✅ Product creation sync test passed');
}
```

#### 2.2 Price Update Sync Test
```dart
// Test price update sync across devices
void testPriceUpdateSync() async {
  print('🧪 Testing Price Update Sync');
  
  // Update product price
  final productId = 1;
  final newPrice = 89.99;
  
  await productService.updateProductPrice(productId, newPrice);
  
  // Verify local UI update
  expect(find.text('\$89.99'), findsOneWidget);
  
  // Wait for sync
  await Future.delayed(Duration(seconds: 3));
  
  // Verify sync on all devices
  final product = await productService.getProduct(productId);
  expect(product.price, newPrice);
  
  print('✅ Price update sync test passed');
}
```

### Scenario 3: Conflict Resolution UI

#### 3.1 Conflict Detection UI Test
```dart
// Test conflict detection and UI notifications
void testConflictDetectionUI() async {
  print('🧪 Testing Conflict Detection UI');
  
  // Simulate concurrent price updates
  if (DeviceConfig.deviceId == 'master_device') {
    await productService.updateProductPrice(1, 85.99);
  } else if (DeviceConfig.deviceId == 'client_device_1') {
    await productService.updateProductPrice(1, 95.99);
  }
  
  // Wait for conflict detection
  await Future.delayed(Duration(seconds: 5));
  
  // Verify conflict notification
  expect(find.text('⚠️ Conflict Detected'), findsOneWidget);
  expect(find.text('Price update conflict resolved'), findsOneWidget);
  
  print('✅ Conflict detection UI test passed');
}
```

### Scenario 4: Error Handling UI

#### 4.1 Network Disconnection UI Test
```dart
// Test network disconnection UI
void testNetworkDisconnectionUI() async {
  print('🧪 Testing Network Disconnection UI');
  
  // Simulate network disconnection
  await networkService.simulateDisconnection();
  
  // Verify disconnection UI
  expect(find.text('🔌 Disconnected'), findsOneWidget);
  expect(find.text('Retrying connection...'), findsOneWidget);
  
  // Restore connection
  await networkService.restoreConnection();
  
  // Verify reconnection UI
  expect(find.text('✅ Connected'), findsOneWidget);
  
  print('✅ Network disconnection UI test passed');
}
```

#### 4.2 Error Message UI Test
```dart
// Test error message display
void testErrorMessageUI() async {
  print('🧪 Testing Error Message UI');
  
  // Trigger invalid operation
  try {
    await productService.updateProductPrice(-1, 100.0);
  } catch (e) {
    // Verify error message
    expect(find.text('❌ Invalid product ID'), findsOneWidget);
    expect(find.text('Please select a valid product'), findsOneWidget);
  }
  
  print('✅ Error message UI test passed');
}
```

---

## 🎨 UI Component Testing

### Sync Status Bar Test
```dart
// Test sync status bar component
void testSyncStatusBar() async {
  print('🧪 Testing Sync Status Bar');
  
  // Test different sync states
  await syncService.setSyncState(SyncState.syncing);
  expect(find.text('🔄 Syncing...'), findsOneWidget);
  
  await syncService.setSyncState(SyncState.synced);
  expect(find.text('✅ Synced'), findsOneWidget);
  
  await syncService.setSyncState(SyncState.error);
  expect(find.text('❌ Sync Error'), findsOneWidget);
  
  print('✅ Sync status bar test passed');
}
```

### Device Role Display Test
```dart
// Test device role display component
void testDeviceRoleDisplay() async {
  print('🧪 Testing Device Role Display');
  
  // Test master role display
  if (DeviceConfig.deviceRole == 'master') {
    expect(find.text('👑 Master Device'), findsOneWidget);
    expect(find.text('Admin Controls'), findsOneWidget);
    expect(find.byIcon(Icons.admin_panel_settings), findsOneWidget);
  } else {
    expect(find.text('📱 Client Device'), findsOneWidget);
    expect(find.text('Connected to Master'), findsOneWidget);
    expect(find.byIcon(Icons.device_hub), findsOneWidget);
  }
  
  print('✅ Device role display test passed');
}
```

---

## 📊 Performance Testing

### UI Responsiveness Test
```dart
// Test UI responsiveness during sync operations
void testUIResponsiveness() async {
  print('🧪 Testing UI Responsiveness');
  
  final stopwatch = Stopwatch()..start();
  
  // Perform sync operation
  await productService.syncAllProducts();
  
  stopwatch.stop();
  
  // Verify UI remains responsive
  expect(stopwatch.elapsedMilliseconds, lessThan(2000)); // < 2 seconds
  
  // Verify no UI freezing
  expect(find.text('Loading...'), findsNothing);
  
  print('✅ UI responsiveness test passed');
}
```

### Memory Usage Test
```dart
// Test memory usage during extended operations
void testMemoryUsage() async {
  print('🧪 Testing Memory Usage');
  
  final initialMemory = await getMemoryUsage();
  
  // Perform extended operations
  for (int i = 0; i < 100; i++) {
    await productService.createProduct(Product(
      name: 'Test Product $i',
      sku: 'TEST$i',
      price: 10.0 + i,
      stock: i,
    ));
  }
  
  final finalMemory = await getMemoryUsage();
  final memoryIncrease = finalMemory - initialMemory;
  
  // Verify memory usage is reasonable (< 50MB increase)
  expect(memoryIncrease, lessThan(50 * 1024 * 1024));
  
  print('✅ Memory usage test passed');
}
```

---

## 🔧 Test Automation

### Automated UI Test Runner
```dart
// Automated test runner for UI tests
class UATTestRunner {
  static Future<void> runAllTests() async {
    print('🚀 Starting Frontend UAT Tests');
    
    final tests = [
      testDeviceRegistration,
      testMasterElectionUI,
      testProductCreationSync,
      testPriceUpdateSync,
      testConflictDetectionUI,
      testNetworkDisconnectionUI,
      testErrorMessageUI,
      testSyncStatusBar,
      testDeviceRoleDisplay,
      testUIResponsiveness,
      testMemoryUsage,
    ];
    
    int passed = 0;
    int failed = 0;
    
    for (final test in tests) {
      try {
        await test();
        passed++;
        print('✅ Test passed: ${test.toString()}');
      } catch (e) {
        failed++;
        print('❌ Test failed: ${test.toString()} - $e');
      }
    }
    
    print('📊 Test Results: $passed passed, $failed failed');
  }
}
```

### Test Data Setup
```dart
// Test data setup for UI tests
class TestDataSetup {
  static Future<void> setupTestData() async {
    print('📊 Setting up test data');
    
    // Clear existing data
    await productService.clearAllProducts();
    await customerService.clearAllCustomers();
    
    // Add test products
    final testProducts = [
      Product(name: 'iPhone 15 Pro', sku: 'PHONE001', price: 999.99, stock: 50),
      Product(name: 'Samsung Galaxy S24', sku: 'PHONE002', price: 899.99, stock: 30),
      Product(name: 'MacBook Pro 16"', sku: 'LAPTOP001', price: 2499.99, stock: 15),
    ];
    
    for (final product in testProducts) {
      await productService.createProduct(product);
    }
    
    // Add test customers
    final testCustomers = [
      Customer(name: 'John Smith', email: 'john@test.com', loyaltyPoints: 1500),
      Customer(name: 'Sarah Johnson', email: 'sarah@test.com', loyaltyPoints: 750),
    ];
    
    for (final customer in testCustomers) {
      await customerService.createCustomer(customer);
    }
    
    print('✅ Test data setup complete');
  }
}
```

---

## 📱 Device-Specific Testing

### Master Device Tests
```dart
// Tests specific to master device
void runMasterDeviceTests() async {
  if (DeviceConfig.deviceRole != 'master') return;
  
  print('👑 Running Master Device Tests');
  
  // Test admin controls
  expect(find.byType(AdminControls), findsOneWidget);
  
  // Test master election controls
  expect(find.text('Initiate Election'), findsOneWidget);
  
  // Test device management
  expect(find.text('Manage Devices'), findsOneWidget);
  
  print('✅ Master device tests passed');
}
```

### Client Device Tests
```dart
// Tests specific to client devices
void runClientDeviceTests() async {
  if (DeviceConfig.deviceRole == 'master') return;
  
  print('📱 Running Client Device Tests');
  
  // Test client limitations
  expect(find.byType(AdminControls), findsNothing);
  
  // Test sync status
  expect(find.byType(SyncStatusBar), findsOneWidget);
  
  // Test data display
  expect(find.byType(ProductList), findsOneWidget);
  
  print('✅ Client device tests passed');
}
```

---

## 🎯 Success Criteria

### UI Responsiveness
- **Loading Times:** < 2 seconds for UI updates
- **Animation Smoothness:** 60 FPS during transitions
- **Error Recovery:** < 3 seconds for error state recovery

### User Experience
- **Error Messages:** 100% actionable and clear
- **Status Indicators:** Real-time sync status updates
- **Role-Based UI:** Correct UI elements for each role

### Data Consistency
- **Sync Accuracy:** 100% data consistency across devices
- **Conflict Resolution:** Clear conflict notifications
- **Recovery Time:** < 5 seconds for automatic recovery

---

*This document provides comprehensive frontend testing guidelines for UAT scenarios. Update as needed for specific testing requirements.* 