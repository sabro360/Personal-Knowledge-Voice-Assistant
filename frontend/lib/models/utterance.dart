/// A single utterance in a conversation session.
class Utterance {
  final int id;
  final String speaker; // 'user', 'assistant', or 'system'
  final String text;
  final int sequenceNumber;

  const Utterance({
    required this.id,
    required this.speaker,
    required this.text,
    required this.sequenceNumber,
  });

  factory Utterance.fromJson(Map<String, dynamic> json) {
    return Utterance(
      id: json['id'] as int,
      speaker: json['speaker'] as String,
      text: json['text'] as String,
      sequenceNumber: json['sequence_number'] as int,
    );
  }
}
