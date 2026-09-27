/// A knowledge item extracted from a conversation session.
class Knowledge {
  final int id;
  final int sessionId;
  final String? title;
  final String? question;
  final String? summary;
  final String? answer;
  final String? category;
  final List<String> keywords;
  final DateTime createdAt;

  const Knowledge({
    required this.id,
    required this.sessionId,
    this.title,
    this.question,
    this.summary,
    this.answer,
    this.category,
    this.keywords = const [],
    required this.createdAt,
  });

  factory Knowledge.fromJson(Map<String, dynamic> json) {
    return Knowledge(
      id: json['id'] as int,
      sessionId: json['session_id'] as int,
      title: json['title'] as String?,
      question: json['question'] as String?,
      summary: json['summary'] as String?,
      answer: json['answer'] as String?,
      category: json['category'] as String?,
      keywords:
          (json['keywords'] as List<dynamic>?)?.cast<String>() ?? const [],
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
