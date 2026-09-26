import 'api_client.dart';

/// Calls GET /health and returns the status string (e.g. "ok").
Future<String> checkHealth() async {
  final client = ApiClient();
  final result = await client.get('/health') as Map<String, dynamic>;
  return result['status'] as String;
}
