import 'package:flutter_webrtc/flutter_webrtc.dart';

class WebRtcService {
  MediaStream? _localStream;

  /// Requests a local audio track via WebRTC getUserMedia.
  Future<MediaStreamTrack> getLocalAudioTrack() async {
    _localStream = await navigator.mediaDevices.getUserMedia({
      'audio': true,
      'video': false,
    });
    final audioTracks = _localStream!.getAudioTracks();
    if (audioTracks.isEmpty) {
      throw Exception('No audio track available');
    }
    return audioTracks.first;
  }

  /// Stops all tracks and disposes the local stream.
  Future<void> stop() async {
    if (_localStream != null) {
      for (final track in _localStream!.getTracks()) {
        await track.stop();
      }
      await _localStream!.dispose();
      _localStream = null;
    }
  }

  Future<void> dispose() async {
    await stop();
  }
}
