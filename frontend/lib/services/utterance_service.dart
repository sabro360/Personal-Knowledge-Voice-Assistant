import '../models/utterance.dart';
import 'api_client.dart';

/// Calls POST /sessions/{sessionId}/utterances to save an utterance.
Future<void> addUtterance(int sessionId, String speaker, String text) async {
  final client = ApiClient();
  await client.post(
    '/sessions/$sessionId/utterances',
    body: {'speaker': speaker, 'text': text},
  );
}

/// Calls GET /sessions/{sessionId}/utterances and returns the list of utterances.
Future<List<Utterance>> fetchUtterances(int sessionId) async {
  final client = ApiClient();
  final result =
      await client.get('/sessions/$sessionId/utterances') as List<dynamic>;
  return result
      .cast<Map<String, dynamic>>()
      .map(Utterance.fromJson)
      .toList();
}
