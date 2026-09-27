import 'package:flutter_test/flutter_test.dart';
import 'package:voice_assistant/services/api_client.dart';
import 'package:voice_assistant/services/audio_player_service.dart';
import 'package:voice_assistant/services/audio_recorder_service.dart';
import 'package:voice_assistant/services/realtime_voice_service.dart';
import 'package:voice_assistant/services/webrtc_service.dart';

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

class FakeWebRtcService extends WebRtcService {
  @override
  Future<void> connect(String clientSecret) async {}

  @override
  Future<void> disconnect() async {}

  @override
  Future<void> dispose() async {}
}

class FakeApiClient extends ApiClient {
  @override
  Future<dynamic> post(String path, {Map<String, dynamic>? body}) async {
    return {
      'client_secret': 'fake_secret',
      'expires_at': '2099-01-01T00:00:00Z',
      'model': 'gpt-4o-realtime-preview',
    };
  }
}

class FailingWebRtcService extends WebRtcService {
  @override
  Future<void> connect(String clientSecret) async {
    throw Exception('connection failed');
  }
}

void main() {
  group('RealtimeVoiceService connect/disconnect', () {
    late RealtimeVoiceService service;

    setUp(() {
      service = RealtimeVoiceService(
        recorder: FakeRecorder(),
        player: FakePlayer(),
        webRtcService: FakeWebRtcService(),
        apiClient: FakeApiClient(),
      );
    });

    tearDown(() => service.dispose());

    test('isConnected is false initially', () {
      expect(service.isConnected.value, false);
    });

    test('connect() sets isConnected to true', () async {
      await service.connect();
      expect(service.isConnected.value, true);
    });

    test('disconnect() sets isConnected to false', () async {
      await service.connect();
      await service.disconnect();
      expect(service.isConnected.value, false);
    });

    test('connect() failure leaves isConnected false', () async {
      final svc = RealtimeVoiceService(
        recorder: FakeRecorder(),
        player: FakePlayer(),
        webRtcService: FailingWebRtcService(),
        apiClient: FakeApiClient(),
      );
      await expectLater(svc.connect(), throwsException);
      expect(svc.isConnected.value, false);
      svc.dispose();
    });
  });
}
