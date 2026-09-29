import 'dart:async';

import 'package:flutter/material.dart';

import '../models/voice_connection_state.dart';
import '../services/realtime_voice_service.dart';
import '../services/session_service.dart';
import '../services/utterance_service.dart';
import 'knowledge_list_screen.dart';

/// Voice-first main screen.
///
/// Shows a single "会話開始" button that connects to the Realtime API.
/// State display (Listening/Thinking/Speaking) and the finish button are
/// added in T1502–T1506.
class VoiceMainScreen extends StatefulWidget {
  const VoiceMainScreen({super.key});

  @override
  State<VoiceMainScreen> createState() => _VoiceMainScreenState();
}

class _VoiceMainScreenState extends State<VoiceMainScreen> {
  final RealtimeVoiceService _voiceService = RealtimeVoiceService();
  StreamSubscription<String>? _userTranscriptSubscription;
  StreamSubscription<String>? _assistantTranscriptSubscription;

  int? _sessionId;
  bool _isLoadingSession = true;
  String? _sessionError;
  bool _isFinished = false; // ignore: prefer_final_fields

  @override
  void initState() {
    super.initState();
    _voiceService.connectionState.addListener(_onVoiceStateChanged);
    _userTranscriptSubscription =
        _voiceService.userTranscripts.listen(_onUserTranscript);
    _assistantTranscriptSubscription =
        _voiceService.assistantTranscripts.listen(_onAssistantTranscript);
    _createSession();
  }

  void _onVoiceStateChanged() => setState(() {});

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

  Future<void> _onUserTranscript(String transcript) async {
    if (_sessionId == null || _isFinished) return;
    try {
      await addUtterance(_sessionId!, 'user', transcript);
    } catch (_) {
      // 保存失敗は会話を中断させない
    }
  }

  Future<void> _onAssistantTranscript(String transcript) async {
    if (_sessionId == null || _isFinished) return;
    try {
      await addUtterance(_sessionId!, 'assistant', transcript);
    } catch (_) {
      // 保存失敗は会話を中断させない
    }
  }

  Future<void> _startConversation() async {
    try {
      await _voiceService.connect();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('接続に失敗しました')),
        );
      }
    }
  }

  @override
  void dispose() {
    _voiceService.connectionState.removeListener(_onVoiceStateChanged);
    _userTranscriptSubscription?.cancel();
    _assistantTranscriptSubscription?.cancel();
    _voiceService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice Assistant'),
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
    final bool canStart = _sessionId != null &&
        !_isFinished &&
        _voiceService.connectionState.value == VoiceConnectionState.disconnected;
    return Center(
      child: ElevatedButton(
        onPressed: canStart ? _startConversation : null,
        child: const Text('会話開始'),
      ),
    );
  }
}
