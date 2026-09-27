import '../models/knowledge.dart';
import 'api_client.dart';

/// Calls GET /knowledge and returns the list of knowledge items.
Future<List<Knowledge>> fetchKnowledgeList() async {
  final client = ApiClient();
  final result = await client.get('/knowledge') as List<dynamic>;
  return result
      .cast<Map<String, dynamic>>()
      .map(Knowledge.fromJson)
      .toList();
}
