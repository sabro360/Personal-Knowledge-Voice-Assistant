import 'package:audioplayers/audioplayers.dart';

/// Service for playing audio output.
class AudioPlayerService {
  final AudioPlayer _player = AudioPlayer();

  /// Called when playback completes naturally.
  void Function()? onComplete;

  AudioPlayerService() {
    _player.onPlayerComplete.listen((_) {
      onComplete?.call();
    });
  }

  /// Plays the bundled test beep sound.
  Future<void> playTestBeep() async {
    await _player.play(AssetSource('test_beep.wav'));
  }

  /// Stops playback.
  Future<void> stop() async {
    await _player.stop();
  }

  /// Releases player resources.
  Future<void> dispose() async {
    await _player.dispose();
  }
}
