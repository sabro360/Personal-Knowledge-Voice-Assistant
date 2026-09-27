/// A knowledge item extracted from a conversation session.
class Knowledge {
  final int id;
  final int sessionId;
  final String? title;
  final String? category;
  final DateTime createdAt;

  const Knowledge({
    required this.id,
    required this.sessionId,
    this.title,
    this.category,
    required this.createdAt,
  });

  factory Knowledge.fromJson(Map<String, dynamic> json) {
    return Knowledge(
      id: json['id'] as int,
      sessionId: json['session_id'] as int,
      title: json['title'] as String?,
      category: json['category'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
