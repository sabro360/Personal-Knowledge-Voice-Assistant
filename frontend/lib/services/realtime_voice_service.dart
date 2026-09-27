import 'package:flutter/foundation.dart';

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

  /// Whether the microphone is currently recording.
  final ValueNotifier<bool> isRecording = ValueNotifier(false);

  /// Whether audio playback is active.
  final ValueNotifier<bool> isPlaying = ValueNotifier(false);

  /// Whether a WebRTC audio track has been acquired.
  final ValueNotifier<bool> hasTrack = ValueNotifier(false);

  RealtimeVoiceService({
    AudioRecorderService? recorder,
    AudioPlayerService? player,
    WebRtcService? webRtcService,
  })  : _recorder = recorder ?? AudioRecorderService(),
        _player = player ?? AudioPlayerService(),
        _webRtcService = webRtcService ?? WebRtcService() {
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

  /// Acquires a local WebRTC audio track and immediately releases it.
  ///
  /// Returns a description string (e.g. "audio / <id>") for display purposes.
  /// T1302 will replace this method with persistent PeerConnection logic.
  Future<String> acquireTrack() async {
    final track = await _webRtcService.getLocalAudioTrack();
    hasTrack.value = true;
    await _webRtcService.stop();
    hasTrack.value = false;
    return '${track.kind} / ${track.id}';
  }

  /// Releases all underlying service resources.
  void dispose() {
    _recorder.dispose();
    _player.dispose();
    _webRtcService.dispose();
    isRecording.dispose();
    isPlaying.dispose();
    hasTrack.dispose();
  }
}
