import 'package:flutter/material.dart';

import '../models/message.dart';
import '../services/audio_player_service.dart';
import '../services/audio_recorder_service.dart';
import '../services/permission_service.dart';
import '../services/session_service.dart';
import '../services/utterance_service.dart';
import 'knowledge_list_screen.dart';

class ConversationScreen extends StatefulWidget {
  const ConversationScreen({super.key});

  @override
  State<ConversationScreen> createState() => _ConversationScreenState();
}

class _ConversationScreenState extends State<ConversationScreen> {
  final List<Message> _messages = [];
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  final AudioRecorderService _audioRecorderService = AudioRecorderService();
  bool _isRecording = false;

  final AudioPlayerService _audioPlayerService = AudioPlayerService();
  bool _isPlaying = false;

  int? _sessionId;
  bool _isLoadingSession = true;
  String? _sessionError;
  bool _isFinished = false;

  @override
  void initState() {
    super.initState();
    _requestPermissions();
    _createSession();
  }

  Future<void> _requestPermissions() async {
    await requestMicrophonePermission();
  }

  Future<void> _createSession() async {
    try {
      final id = await createSession();
      setState(() {
        _sessionId = id;
        _isLoadingSession = false;
      });
    } catch (e) {
      setState(() {
        _sessionError = 'セッションを開始できませんでした';
        _isLoadingSession = false;
      });
    }
  }

  @override
  void dispose() {
    _audioRecorderService.dispose();
    _audioPlayerService.dispose();
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _togglePlayback() async {
    if (_isPlaying) {
      await _audioPlayerService.stop();
      if (mounted) setState(() => _isPlaying = false);
    } else {
      try {
        await _audioPlayerService.playTestBeep();
        if (mounted) setState(() => _isPlaying = true);
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('音声を再生できませんでした')),
          );
        }
      }
    }
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      await _audioRecorderService.stop();
      if (mounted) setState(() => _isRecording = false);
    } else {
      try {
        await _audioRecorderService.start();
        if (mounted) setState(() => _isRecording = true);
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('マイクを開始できませんでした')),
          );
        }
      }
    }
  }

  Future<void> _sendMessage() async {
    final text = _textController.text.trim();
    if (text.isEmpty) return;
    setState(() {
      _messages.add(Message(speaker: 'user', text: text));
    });
    _textController.clear();
    _scrollToBottom();
    try {
      await addUtterance(_sessionId!, 'user', text);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('メッセージの保存に失敗しました')),
        );
      }
    }
    if (mounted) {
      final dummyText = 'You said: $text';
      setState(() {
        _messages.add(Message(speaker: 'assistant', text: dummyText));
      });
      _scrollToBottom();
      try {
        await addUtterance(_sessionId!, 'assistant', dummyText);
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('メッセージの保存に失敗しました')),
          );
        }
      }
    }
  }

  Future<void> _finishSession() async {
    try {
      await finishSession(_sessionId!);
      if (mounted) {
        setState(() {
          _isFinished = true;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('会話を終了しました')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('会話の終了に失敗しました')),
        );
      }
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('会話'),
        actions: [
          IconButton(
            icon: const Icon(Icons.library_books),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const KnowledgeListScreen(),
                ),
              );
            },
          ),
          TextButton(
            onPressed: (_sessionId == null || _isFinished) ? null : _finishSession,
            child: const Text('終了'),
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoadingSession) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_sessionError != null) {
      return Center(child: Text(_sessionError!));
    }
    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            controller: _scrollController,
            itemCount: _messages.length,
            itemBuilder: (context, index) {
              final message = _messages[index];
              final isUser = message.speaker == 'user';
              return Align(
                alignment:
                    isUser ? Alignment.centerRight : Alignment.centerLeft,
                child: Container(
                  margin: const EdgeInsets.symmetric(
                      horizontal: 8, vertical: 4),
                  padding: const EdgeInsets.symmetric(
                      horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: isUser
                        ? Theme.of(context).colorScheme.primaryContainer
                        : Theme.of(context).colorScheme.surfaceVariant,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(message.text),
                ),
              );
            },
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(8),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _textController,
                  decoration: const InputDecoration(
                    hintText: 'メッセージを入力',
                    border: OutlineInputBorder(),
                  ),
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: Icon(_isPlaying ? Icons.stop_circle : Icons.volume_up),
                color: _isPlaying ? Colors.blue : null,
                onPressed: (_sessionId == null || _isFinished)
                    ? null
                    : _togglePlayback,
              ),
              IconButton(
                icon: Icon(_isRecording ? Icons.stop_circle : Icons.mic),
                color: _isRecording ? Colors.red : null,
                onPressed: (_sessionId == null || _isFinished)
                    ? null
                    : _toggleRecording,
              ),
              IconButton(
                onPressed: _sendMessage,
                icon: const Icon(Icons.send),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
