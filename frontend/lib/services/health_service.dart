import 'dart:io';

import 'api_client.dart';

/// Calls GET /health and returns the status string (e.g. "ok").
Future<String> checkHealth() async {
  final client = ApiClient();
  final result = await client.get('/health') as Map<String, dynamic>;
  return result['status'] as String;
}

/// Converts an exception from [checkHealth] into a user-readable message.
String healthErrorMessage(Object error) {
  if (error is SocketException) {
    return 'バックエンドに接続できません';
  }
  if (error is ApiException) {
    return 'サーバーエラーが発生しました (${error.statusCode})';
  }
  return 'エラーが発生しました';
}
