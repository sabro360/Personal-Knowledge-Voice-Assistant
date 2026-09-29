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
  bool _isFinished = false;
  bool _isFinishing = false;

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

  Future<void> _finishSession() async {
    setState(() { _isFinishing = true; });
    // 1. WebRTC切断（接続中のみ、失敗しても続行する）
    if (_voiceService.isConnected.value) {
      try {
        await _voiceService.disconnect();
      } catch (_) {
        // 切断失敗はSession終了を止めない
      }
    }
    // 2. Session終了（バックエンドがKnowledge生成を自動実行）
    try {
      await finishSession(_sessionId!);
      if (mounted) {
        setState(() {
          _isFinished = true;
          _isFinishing = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('会話を終了しました')),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() { _isFinishing = false; });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('会話の終了に失敗しました')),
        );
      }
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
          TextButton(
            onPressed: (_sessionId == null || _isFinished || _isFinishing) ? null : _finishSession,
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

    final state = _voiceService.connectionState.value;

    if (state == VoiceConnectionState.listening) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.mic, size: 64, color: Colors.green),
            SizedBox(height: 16),
            Text('Listening', style: TextStyle(fontSize: 20, color: Colors.green)),
          ],
        ),
      );
    }

    if (state == VoiceConnectionState.thinking) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(color: Colors.amber),
            SizedBox(height: 16),
            Text('Thinking', style: TextStyle(fontSize: 20, color: Colors.amber)),
          ],
        ),
      );
    }

    if (state == VoiceConnectionState.speaking) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.volume_up, size: 64, color: Colors.blue),
            SizedBox(height: 16),
            Text('Speaking', style: TextStyle(fontSize: 20, color: Colors.blue)),
          ],
        ),
      );
    }

    if (state == VoiceConnectionState.error) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            const Text('エラーが発生しました', style: TextStyle(fontSize: 20, color: Colors.red)),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: (!_isFinished && !_isFinishing) ? _startConversation : null,
              child: const Text('再接続'),
            ),
          ],
        ),
      );
    }

    final bool canStart = _sessionId != null &&
        !_isFinished &&
        !_isFinishing &&
        state == VoiceConnectionState.disconnected;
    return Center(
      child: ElevatedButton(
        onPressed: canStart ? _startConversation : null,
        child: const Text('会話開始'),
      ),
    );
  }
}
