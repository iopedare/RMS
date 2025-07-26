import 'dart:convert';
import 'package:http/http.dart' as http;

class SyncApiService {
  final String baseUrl;

  SyncApiService(this.baseUrl);

  // Basic sync endpoints
  Future<http.Response> pushSyncEvent(Map<String, dynamic> event) async {
    return await http.post(
      Uri.parse('$baseUrl/sync/push'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(event),
    );
  }

  Future<http.Response> pullSyncEvents() async {
    return await http.get(Uri.parse('$baseUrl/sync/pull'));
  }

  Future<http.Response> getSyncStatus() async {
    return await http.get(Uri.parse('$baseUrl/sync/status'));
  }

  // Device registration
  Future<http.Response> registerDevice(String deviceId, String role) async {
    return await http.post(
      Uri.parse('$baseUrl/device/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'device_id': deviceId, 'role': role}),
    );
  }

  // Advanced sync endpoints
  Future<http.Response> getDeviceRoles() async {
    return await http.get(Uri.parse('$baseUrl/device/roles'));
  }

  Future<http.Response> getDeviceRole(String deviceId) async {
    return await http.get(Uri.parse('$baseUrl/device/roles/$deviceId'));
  }

  Future<http.Response> updateDeviceRole(
      String deviceId, String newRole, String reason) async {
    return await http.put(
      Uri.parse('$baseUrl/device/roles/$deviceId'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'role': newRole,
        'reason': reason,
        'timestamp': DateTime.now().toIso8601String(),
      }),
    );
  }

  Future<http.Response> getSyncState(String deviceId) async {
    return await http.get(Uri.parse('$baseUrl/sync/state/$deviceId'));
  }

  Future<http.Response> updateSyncState(
      String deviceId, Map<String, dynamic> state) async {
    return await http.put(
      Uri.parse('$baseUrl/sync/state/$deviceId'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(state),
    );
  }

  Future<http.Response> getMasterElectionLogs({int? limit, int? offset}) async {
    final queryParams = <String, String>{};
    if (limit != null) queryParams['limit'] = limit.toString();
    if (offset != null) queryParams['offset'] = offset.toString();

    final uri = Uri.parse('$baseUrl/sync/master-election-logs')
        .replace(queryParameters: queryParams);
    return await http.get(uri);
  }

  Future<http.Response> getSyncAuditLogs({
    String? deviceId,
    String? eventType,
    String? startDate,
    String? endDate,
    int? limit,
    int? offset,
  }) async {
    final queryParams = <String, String>{};
    if (deviceId != null) queryParams['device_id'] = deviceId;
    if (eventType != null) queryParams['event_type'] = eventType;
    if (startDate != null) queryParams['start_date'] = startDate;
    if (endDate != null) queryParams['end_date'] = endDate;
    if (limit != null) queryParams['limit'] = limit.toString();
    if (offset != null) queryParams['offset'] = offset.toString();

    final uri = Uri.parse('$baseUrl/sync/audit-logs')
        .replace(queryParameters: queryParams);
    return await http.get(uri);
  }

  Future<http.Response> triggerMasterElection(String reason) async {
    return await http.post(
      Uri.parse('$baseUrl/sync/master-election'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'reason': reason,
        'timestamp': DateTime.now().toIso8601String(),
      }),
    );
  }

  Future<http.Response> getActiveDevices() async {
    return await http.get(Uri.parse('$baseUrl/device/active'));
  }

  Future<http.Response> getMasterDevice() async {
    return await http.get(Uri.parse('$baseUrl/device/master'));
  }

  Future<http.Response> getSyncQueueStatus(String deviceId) async {
    return await http.get(Uri.parse('$baseUrl/sync/queue/$deviceId'));
  }

  Future<http.Response> clearSyncQueue(String deviceId) async {
    return await http.delete(Uri.parse('$baseUrl/sync/queue/$deviceId'));
  }

  Future<http.Response> getSyncConflicts(String deviceId) async {
    return await http.get(Uri.parse('$baseUrl/sync/conflicts/$deviceId'));
  }

  Future<http.Response> resolveSyncConflict(String deviceId, String conflictId,
      Map<String, dynamic> resolution) async {
    return await http.post(
      Uri.parse('$baseUrl/sync/conflicts/$deviceId/$conflictId/resolve'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(resolution),
    );
  }

  Future<http.Response> getSystemHealth() async {
    return await http.get(Uri.parse('$baseUrl/system/health'));
  }

  Future<http.Response> getNetworkStatus() async {
    return await http.get(Uri.parse('$baseUrl/system/network'));
  }

  // Data sync endpoints
  Future<http.Response> syncData(
      String targetDevice, String dataType, Map<String, dynamic> data) async {
    return await http.post(
      Uri.parse('$baseUrl/sync/data'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'target_device': targetDevice,
        'data_type': dataType,
        'data': data,
        'timestamp': DateTime.now().toIso8601String(),
      }),
    );
  }

  Future<http.Response> getPendingData(String deviceId) async {
    return await http.get(Uri.parse('$baseUrl/sync/data/pending/$deviceId'));
  }

  Future<http.Response> acknowledgeData(String deviceId, String dataId) async {
    return await http.post(
      Uri.parse('$baseUrl/sync/data/acknowledge'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'device_id': deviceId,
        'data_id': dataId,
        'timestamp': DateTime.now().toIso8601String(),
      }),
    );
  }

  // Error handling and recovery
  Future<http.Response> reportError(String deviceId, String errorType,
      String errorMessage, Map<String, dynamic>? details) async {
    return await http.post(
      Uri.parse('$baseUrl/system/error'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'device_id': deviceId,
        'error_type': errorType,
        'error_message': errorMessage,
        'details': details,
        'timestamp': DateTime.now().toIso8601String(),
      }),
    );
  }

  Future<http.Response> getErrorLogs(String deviceId, {int? limit}) async {
    final queryParams = <String, String>{};
    if (limit != null) queryParams['limit'] = limit.toString();

    final uri = Uri.parse('$baseUrl/system/errors/$deviceId')
        .replace(queryParameters: queryParams);
    return await http.get(uri);
  }

  // Utility methods
  bool isSuccessResponse(http.Response response) {
    return response.statusCode >= 200 && response.statusCode < 300;
  }

  Map<String, dynamic>? parseJsonResponse(http.Response response) {
    try {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } catch (e) {
      print('Error parsing JSON response: $e');
      return null;
    }
  }

  String getErrorMessage(http.Response response) {
    try {
      final json = jsonDecode(response.body);
      return json['error'] ?? json['message'] ?? 'Unknown error';
    } catch (e) {
      return 'HTTP ${response.statusCode}: ${response.reasonPhrase}';
    }
  }
}
