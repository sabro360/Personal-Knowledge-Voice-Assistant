import 'package:flutter/foundation.dart';
import 'package:audioplayers/audioplayers.dart';

/// Service for playing audio output.
class AudioPlayerService {
  final AudioPlayer? _player;

  /// Called when playback completes naturally.
  void Function()? onComplete;

  AudioPlayerService() : _player = AudioPlayer() {
    _player!.onPlayerComplete.listen((_) {
      onComplete?.call();
    });
  }

  /// Named constructor for test subclasses that override all methods.
  /// Does not initialize [AudioPlayer] to avoid platform channel calls.
  @visibleForTesting
  AudioPlayerService.testing() : _player = null;

  /// Plays the bundled test beep sound.
  Future<void> playTestBeep() async {
    await _player!.play(AssetSource('test_beep.wav'));
  }

  /// Stops playback.
  Future<void> stop() async {
    await _player!.stop();
  }

  /// Releases player resources.
  Future<void> dispose() async {
    await _player?.dispose();
  }
}
