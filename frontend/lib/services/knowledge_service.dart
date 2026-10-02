import '../models/knowledge.dart';
import '../models/knowledge_graph.dart';
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

/// Calls GET /knowledge/search?q={q} and returns matching knowledge items.
Future<List<Knowledge>> fetchKnowledgeSearch(String q) async {
  final client = ApiClient();
  final result = await client.get(
        '/knowledge/search?q=${Uri.encodeQueryComponent(q)}',
      ) as List<dynamic>;
  return result
      .cast<Map<String, dynamic>>()
      .map(Knowledge.fromJson)
      .toList();
}

/// Calls GET /knowledge/graph and returns the Knowledge graph (nodes + edges).
Future<KnowledgeGraph> fetchKnowledgeGraph() async {
  final client = ApiClient();
  final result = await client.get('/knowledge/graph') as Map<String, dynamic>;
  return KnowledgeGraph.fromJson(result);
}
