/// A single utterance in a conversation.
class Message {
  final String speaker; // 'user' or 'assistant'
  final String text;

  const Message({required this.speaker, required this.text});
}
