import 'dart:async';
import 'dart:convert';
import 'dart:developer' show log;

import 'package:flutter/foundation.dart';

import '../models/voice_connection_state.dart';
import 'api_client.dart';
import 'audio_player_service.dart';
import 'audio_recorder_service.dart';
import 'webrtc_service.dart';

/// Service that encapsulates all voice-related logic and exposes observable state.
///
/// Wraps [AudioRecorderService], [AudioPlayerService], and [WebRtcService]
/// so that [ConversationScreen] does not depend on them directly.
/// State changes are published via [ValueNotifier] so the UI can rebuild efficiently.
class RealtimeVoiceService {
  final AudioRecorderService _recorder;
  final AudioPlayerService _player;
  final WebRtcService _webRtcService;
  final ApiClient _apiClient;

  StreamSubscription<String>? _eventsSubscription;
  final _userTranscriptController = StreamController<String>.broadcast();
  final _assistantTranscriptController = StreamController<String>.broadcast();

  /// Whether the microphone is currently recording.
  final ValueNotifier<bool> isRecording = ValueNotifier(false);

  /// Whether audio playback is active.
  final ValueNotifier<bool> isPlaying = ValueNotifier(false);

  /// Whether a WebRTC connection to the Realtime API is active.
  final ValueNotifier<bool> isConnected = ValueNotifier(false);

  /// Current state of the Realtime API connection.
  final ValueNotifier<VoiceConnectionState> connectionState =
      ValueNotifier(VoiceConnectionState.disconnected);

  /// Stream of user speech transcripts received from the Realtime API.
  Stream<String> get userTranscripts => _userTranscriptController.stream;

  /// Stream of assistant speech transcripts received from the Realtime API.
  Stream<String> get assistantTranscripts => _assistantTranscriptController.stream;

  RealtimeVoiceService({
    AudioRecorderService? recorder,
    AudioPlayerService? player,
    WebRtcService? webRtcService,
    ApiClient? apiClient,
  })  : _recorder = recorder ?? AudioRecorderService(),
        _player = player ?? AudioPlayerService(),
        _webRtcService = webRtcService ?? WebRtcService(),
        _apiClient = apiClient ?? ApiClient() {
    _player.onComplete = () => isPlaying.value = false;
  }

  /// Starts microphone recording.
  Future<void> startRecording() async {
    await _recorder.start();
    isRecording.value = true;
  }

  /// Stops microphone recording.
  Future<void> stopRecording() async {
    await _recorder.stop();
    isRecording.value = false;
  }

  /// Starts audio playback (test beep).
  Future<void> startPlayback() async {
    await _player.playTestBeep();
    isPlaying.value = true;
  }

  /// Stops audio playback.
  Future<void> stopPlayback() async {
    await _player.stop();
    isPlaying.value = false;
  }

  /// Fetches ephemeral credentials from the backend and establishes
  /// a WebRTC connection to the OpenAI Realtime API.
  Future<void> connect() async {
    connectionState.value = VoiceConnectionState.connecting;
    try {
      final data =
          await _apiClient.post('/realtime/session') as Map<String, dynamic>;
      final clientSecret = data['client_secret'] as String;

      // Subscribe before connecting so no early events are missed.
      _eventsSubscription?.cancel();
      _eventsSubscription =
          _webRtcService.events.listen(_handleRealtimeEvent);

      _webRtcService.onDisconnected = () {
        connectionState.value = VoiceConnectionState.error;
        isConnected.value = false;
      };

      await _webRtcService.connect(clientSecret);
      connectionState.value = VoiceConnectionState.listening;
      isConnected.value = true;
    } catch (e, stack) {
      log(
        'connect() failed: $e',
        name: 'RealtimeVoiceService',
        error: e,
        stackTrace: stack,
      );
      _eventsSubscription?.cancel();
      _eventsSubscription = null;
      connectionState.value = VoiceConnectionState.error;
      rethrow;
    }
  }

  /// Closes the WebRTC connection.
  Future<void> disconnect() async {
    _eventsSubscription?.cancel();
    _eventsSubscription = null;
    _webRtcService.onDisconnected = null;
    await _webRtcService.disconnect();
    connectionState.value = VoiceConnectionState.disconnected;
    isConnected.value = false;
  }

  /// Releases all underlying service resources.
  void dispose() {
    _eventsSubscription?.cancel();
    _userTranscriptController.close();
    _assistantTranscriptController.close();
    _recorder.dispose();
    _player.dispose();
    _webRtcService.dispose();
    isRecording.dispose();
    isPlaying.dispose();
    isConnected.dispose();
    connectionState.dispose();
  }

  void _handleRealtimeEvent(String json) {
    try {
      final event = jsonDecode(json) as Map<String, dynamic>;
      final type = event['type'] as String? ?? '';
      switch (type) {
        case 'session.created':
          // Enable user speech transcription and register the search_knowledge
          // tool so the AI can query past knowledge when asked.
          // In the GA Realtime API (gpt-realtime-2.1), transcription is configured
          // under session.audio.input.transcription (not input_audio_transcription).
          _webRtcService.sendMessage(jsonEncode({
            'type': 'session.update',
            'session': {
              'type': 'realtime',
              'audio': {
                'input': {
                  'transcription': {
                    'model': 'gpt-4o-transcribe',
                    'language': 'ja',
                  },
                },
              },
              'tools': [
                {
                  'type': 'function',
                  'name': 'search_knowledge',
                  'description':
                      '過去の会話から蓄積されたナレッジを検索します。'
                      'ユーザーが「前にもこれ聞いた？」「前回〇〇について話したことを教えて」'
                      'などと尋ねたときに呼び出してください。',
                  'parameters': {
                    'type': 'object',
                    'properties': {
                      'query': {
                        'type': 'string',
                        'description':
                            '検索する短いキーワード（1〜3語）。'
                            '長い文や説明文ではなく、トピックの核心語を使ってください。'
                            '例: 「CD」「光の回折」「水と虹」',
                      },
                    },
                    'required': ['query'],
                  },
                }
              ],
              'tool_choice': 'auto',
            },
          }));
        case 'response.created':
          connectionState.value = VoiceConnectionState.thinking;
        case 'output_audio_buffer.started':
          connectionState.value = VoiceConnectionState.speaking;
        case 'input_audio_buffer.speech_started':
          // Barge-in: ユーザーが AI 発話中に話し始めた。
          // speaking 中のみ即座に listening へ遷移し、割り込みを UI へ反映する。
          // listening / thinking 中は no-op（通常の発話開始なので状態変更不要）。
          if (connectionState.value == VoiceConnectionState.speaking) {
            connectionState.value = VoiceConnectionState.listening;
          }
        case 'output_audio_buffer.stopped':
          connectionState.value = VoiceConnectionState.listening;
        case 'response.done':
          // Check for AI tool calls before falling back to listening.
          final response = event['response'] as Map<String, dynamic>?;
          final output = (response?['output'] as List<dynamic>?) ?? [];
          final functionCalls = output
              .whereType<Map<String, dynamic>>()
              .where((item) => item['type'] == 'function_call')
              .toList();
          if (functionCalls.isNotEmpty) {
            // Execute tool calls; do not transition to listening yet.
            unawaited(_handleFunctionCalls(functionCalls));
          } else {
            // Fallback: transition to listening when no audio was generated
            // (e.g. text-only response). No-op if already listening.
            if (connectionState.value != VoiceConnectionState.listening) {
              connectionState.value = VoiceConnectionState.listening;
            }
          }
        case 'error':
          connectionState.value = VoiceConnectionState.error;
        case 'conversation.item.input_audio_transcription.completed':
          // User speech transcription arrives here (asynchronously after
          // conversation.item.done, which always has transcript=null).
          final transcript = event['transcript'] as String?;
          if (transcript == null || transcript.isEmpty) break;
          _userTranscriptController.add(transcript);
        case 'response.output_audio_transcript.done':
          // Assistant speech transcript is complete.
          final assistantTranscript = event['transcript'] as String?;
          if (assistantTranscript == null || assistantTranscript.isEmpty) break;
          _assistantTranscriptController.add(assistantTranscript);
      }
    } catch (e) {
      log('Malformed Realtime event: $e', name: 'RealtimeVoiceService');
    }
  }

  /// Executes AI function calls received in a [response.done] event.
  ///
  /// For each call, queries the backend and returns the result via
  /// [conversation.item.create]. Sends [response.create] once all calls
  /// are done to trigger the next AI turn.
  Future<void> _handleFunctionCalls(
    List<Map<String, dynamic>> functionCalls,
  ) async {
    for (final call in functionCalls) {
      final callId = call['call_id'] as String? ?? '';
      final name = call['name'] as String? ?? '';
      final argsJson = call['arguments'] as String? ?? '{}';

      String output;
      try {
        if (name == 'search_knowledge') {
          final args = jsonDecode(argsJson) as Map<String, dynamic>;
          final query = args['query'] as String? ?? '';
          final result = await _apiClient.post(
            '/knowledge/search_tool',
            body: {'query': query},
          ) as Map<String, dynamic>;
          output = jsonEncode(result);

          // T1804: inject results into session context so the AI can
          // reference the knowledge throughout the rest of this session.
          final results =
              (result['results'] as List<dynamic>?)?.whereType<Map<String, dynamic>>().toList() ?? [];
          if (results.isNotEmpty) {
            _webRtcService.sendMessage(jsonEncode({
              'type': 'session.update',
              'session': {
                'instructions': _buildKnowledgeInstructions(results),
              },
            }));
          }
        } else {
          output = jsonEncode({'error': 'Unknown tool: $name'});
        }
      } catch (e) {
        output = jsonEncode({'error': e.toString()});
      }

      _webRtcService.sendMessage(jsonEncode({
        'type': 'conversation.item.create',
        'item': {
          'type': 'function_call_output',
          'call_id': callId,
          'output': output,
        },
      }));
    }

    _webRtcService.sendMessage(jsonEncode({'type': 'response.create'}));
  }

  /// Formats [results] from [search_knowledge] into a readable instructions
  /// string for [session.update].
  String _buildKnowledgeInstructions(List<Map<String, dynamic>> results) {
    final buffer = StringBuffer()
      ..writeln('あなたはパーソナル知識アシスタントです。')
      ..writeln('ユーザーとの過去の会話から、関連する以下のナレッジが見つかりました。')
      ..writeln('回答の参考にしてください。')
      ..writeln()
      ..writeln('## 関連ナレッジ (${results.length}件)');

    for (final item in results) {
      final title = item['title'] as String? ?? '';
      final question = item['question'] as String? ?? '';
      final summary = item['summary'] as String? ?? '';
      final answer = item['answer'] as String? ?? '';

      buffer.writeln();
      if (title.isNotEmpty) buffer.writeln('### $title');
      if (question.isNotEmpty) buffer.writeln('質問: $question');
      if (summary.isNotEmpty) buffer.writeln('要約: $summary');
      if (answer.isNotEmpty) buffer.writeln('回答: $answer');
    }

    return buffer.toString();
  }
}
