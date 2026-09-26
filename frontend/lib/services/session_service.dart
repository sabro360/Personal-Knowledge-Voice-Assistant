import 'api_client.dart';

/// Calls POST /sessions and returns the new session ID.
Future<int> createSession() async {
  final client = ApiClient();
  final result = await client.post('/sessions') as Map<String, dynamic>;
  return result['id'] as int;
}
