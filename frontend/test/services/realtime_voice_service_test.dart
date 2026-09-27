import 'package:flutter_test/flutter_test.dart';
import 'package:voice_assistant/services/audio_player_service.dart';
import 'package:voice_assistant/services/audio_recorder_service.dart';
import 'package:voice_assistant/services/realtime_voice_service.dart';

class FakeRecorder extends AudioRecorderService {
  @override
  Future<void> start() async {}

  @override
  Future<void> stop() async {}

  @override
  Future<void> dispose() async {}
}

class FakePlayer extends AudioPlayerService {
  FakePlayer() : super.testing();

  @override
  Future<void> playTestBeep() async {}

  @override
  Future<void> stop() async {}

  @override
  Future<void> dispose() async {}
}

void main() {
  group('RealtimeVoiceService', () {
    late RealtimeVoiceService service;

    setUp(() {
      service = RealtimeVoiceService(
        recorder: FakeRecorder(),
        player: FakePlayer(),
      );
    });

    tearDown(() => service.dispose());

    test('isRecording is false initially', () {
      expect(service.isRecording.value, false);
    });

    test('startRecording sets isRecording to true', () async {
      await service.startRecording();
      expect(service.isRecording.value, true);
    });

    test('stopRecording sets isRecording to false', () async {
      await service.startRecording();
      await service.stopRecording();
      expect(service.isRecording.value, false);
    });

    test('isPlaying is false initially', () {
      expect(service.isPlaying.value, false);
    });

    test('startPlayback sets isPlaying to true', () async {
      await service.startPlayback();
      expect(service.isPlaying.value, true);
    });

    test('stopPlayback sets isPlaying to false', () async {
      await service.startPlayback();
      await service.stopPlayback();
      expect(service.isPlaying.value, false);
    });

    test('onComplete callback sets isPlaying to false', () async {
      final fakePlayer = FakePlayer();
      final svc = RealtimeVoiceService(
        recorder: FakeRecorder(),
        player: fakePlayer,
      );
      await svc.startPlayback();
      fakePlayer.onComplete?.call();
      expect(svc.isPlaying.value, false);
      svc.dispose();
    });
  });
}
