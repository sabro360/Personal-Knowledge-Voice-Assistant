import 'package:voice_assistant/models/knowledge.dart';

/// A similarity-based relation between two Knowledge items.
class KnowledgeRelation {
  final int id;
  final int sourceKnowledgeId;
  final int targetKnowledgeId;
  final String relationType;
  final double score;
  final DateTime createdAt;

  const KnowledgeRelation({
    required this.id,
    required this.sourceKnowledgeId,
    required this.targetKnowledgeId,
    required this.relationType,
    required this.score,
    required this.createdAt,
  });

  factory KnowledgeRelation.fromJson(Map<String, dynamic> json) {
    return KnowledgeRelation(
      id: json['id'] as int,
      sourceKnowledgeId: json['source_knowledge_id'] as int,
      targetKnowledgeId: json['target_knowledge_id'] as int,
      relationType: json['relation_type'] as String,
      score: (json['score'] as num).toDouble(),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

/// The full Knowledge graph: nodes (Knowledge items) and edges (relations).
class KnowledgeGraph {
  final List<Knowledge> nodes;
  final List<KnowledgeRelation> edges;

  const KnowledgeGraph({required this.nodes, required this.edges});

  factory KnowledgeGraph.fromJson(Map<String, dynamic> json) {
    final nodes = (json['nodes'] as List<dynamic>)
        .map((e) => Knowledge.fromJson(e as Map<String, dynamic>))
        .toList();
    final edges = (json['edges'] as List<dynamic>)
        .map((e) => KnowledgeRelation.fromJson(e as Map<String, dynamic>))
        .toList();
    return KnowledgeGraph(nodes: nodes, edges: edges);
  }
}
