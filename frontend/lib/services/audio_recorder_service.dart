import 'package:record/record.dart';

/// Service for capturing audio from the microphone.
class AudioRecorderService {
  final AudioRecorder _recorder = AudioRecorder();

  /// Starts capturing audio as a PCM stream.
  ///
  /// The stream is consumed without processing (T1102: confirm capture works).
  Future<void> start() async {
    final stream = await _recorder.startStream(
      const RecordConfig(
        encoder: AudioEncoder.pcm16bits,
        sampleRate: 16000,
        numChannels: 1,
      ),
    );
    stream.listen((_) {});
  }

  /// Stops audio capture.
  Future<void> stop() async {
    await _recorder.stop();
  }

  /// Releases recorder resources.
  Future<void> dispose() async {
    await _recorder.dispose();
  }
}
