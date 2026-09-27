import 'package:flutter/foundation.dart';

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

  /// Whether the microphone is currently recording.
  final ValueNotifier<bool> isRecording = ValueNotifier(false);

  /// Whether audio playback is active.
  final ValueNotifier<bool> isPlaying = ValueNotifier(false);

  /// Whether a WebRTC connection to the Realtime API is active.
  final ValueNotifier<bool> isConnected = ValueNotifier(false);

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
    final data =
        await _apiClient.post('/realtime/session') as Map<String, dynamic>;
    final clientSecret = data['client_secret'] as String;
    await _webRtcService.connect(clientSecret);
    isConnected.value = true;
  }

  /// Closes the WebRTC connection.
  Future<void> disconnect() async {
    await _webRtcService.disconnect();
    isConnected.value = false;
  }

  /// Releases all underlying service resources.
  void dispose() {
    _recorder.dispose();
    _player.dispose();
    _webRtcService.dispose();
    isRecording.dispose();
    isPlaying.dispose();
    isConnected.dispose();
  }
}
