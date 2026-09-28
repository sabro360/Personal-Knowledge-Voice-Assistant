import 'dart:async';
import 'dart:convert';

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

      await _webRtcService.connect(clientSecret);
      connectionState.value = VoiceConnectionState.listening;
      isConnected.value = true;
    } catch (_) {
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
    await _webRtcService.disconnect();
    connectionState.value = VoiceConnectionState.disconnected;
    isConnected.value = false;
  }

  /// Releases all underlying service resources.
  void dispose() {
    _eventsSubscription?.cancel();
    _userTranscriptController.close();
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
          // Enable user speech transcription as soon as the session is ready.
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
            },
          }));
        case 'response.created':
          connectionState.value = VoiceConnectionState.thinking;
        case 'output_audio_buffer.started':
          connectionState.value = VoiceConnectionState.speaking;
        case 'output_audio_buffer.stopped':
          connectionState.value = VoiceConnectionState.listening;
        case 'response.done':
          // Fallback: transition to listening when no audio was generated
          // (e.g. text-only response). No-op if already listening.
          if (connectionState.value != VoiceConnectionState.listening) {
            connectionState.value = VoiceConnectionState.listening;
          }
        case 'error':
          connectionState.value = VoiceConnectionState.error;
        case 'conversation.item.input_audio_transcription.completed':
          // User speech transcription arrives here (asynchronously after
          // conversation.item.done, which always has transcript=null).
          final transcript = event['transcript'] as String?;
          if (transcript == null || transcript.isEmpty) break;
          _userTranscriptController.add(transcript);
      }
    } catch (_) {
      // Ignore malformed events.
    }
  }
}
