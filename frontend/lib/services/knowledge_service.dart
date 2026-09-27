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

/// Calls GET /knowledge/{id} and returns a single knowledge item with keywords.
Future<Knowledge> fetchKnowledgeDetail(int id) async {
  final client = ApiClient();
  final result = await client.get('/knowledge/$id') as Map<String, dynamic>;
  return Knowledge.fromJson(result);
}
