import 'package:flutter/material.dart';

import '../models/utterance.dart';
import '../services/utterance_service.dart';

class ConversationHistoryScreen extends StatefulWidget {
  final int sessionId;

  const ConversationHistoryScreen({super.key, required this.sessionId});

  @override
  State<ConversationHistoryScreen> createState() =>
      _ConversationHistoryScreenState();
}

class _ConversationHistoryScreenState
    extends State<ConversationHistoryScreen> {
  List<Utterance> _utterances = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadUtterances();
  }

  Future<void> _loadUtterances() async {
    try {
      final utterances = await fetchUtterances(widget.sessionId);
      if (mounted) {
        setState(() {
          _utterances = utterances;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = '会話ログの取得に失敗しました';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('会話ログ')),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(child: Text(_error!));
    }
    if (_utterances.isEmpty) {
      return const Center(child: Text('会話ログがありません'));
    }
    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: _utterances.length,
      itemBuilder: (context, index) {
        final utterance = _utterances[index];
        final isUser = utterance.speaker == 'user';
        return Align(
          alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
          child: Container(
            margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: isUser
                  ? Theme.of(context).colorScheme.primaryContainer
                  : Theme.of(context).colorScheme.surfaceVariant,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(utterance.text),
          ),
        );
      },
    );
  }
}
