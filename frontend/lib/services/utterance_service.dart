import 'api_client.dart';

/// Calls POST /sessions/{sessionId}/utterances to save an utterance.
Future<void> addUtterance(int sessionId, String speaker, String text) async {
  final client = ApiClient();
  await client.post(
    '/sessions/$sessionId/utterances',
    body: {'speaker': speaker, 'text': text},
  );
}
