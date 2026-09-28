import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:voice_assistant/models/voice_connection_state.dart';
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

/// A [WebRtcService] subclass that allows injecting events into the stream
/// without actually establishing a WebRTC connection.
class ControllableWebRtcService extends WebRtcService {
  final _testController = StreamController<String>.broadcast();

  @override
  Stream<String> get events => _testController.stream;

  void injectEvent(String json) => _testController.add(json);

  @override
  Future<void> connect(String clientSecret) async {}

  @override
  Future<void> disconnect() async {}

  @override
  Future<void> dispose() async {
    await _testController.close();
    await super.dispose();
  }
}

class FailingWebRtcService extends WebRtcService {
  @override
  Future<void> connect(String clientSecret) async {
    throw Exception('connection failed');
  }
}

class FakeApiClient extends ApiClient {
  @override
  Future<dynamic> post(String path, {Map<String, dynamic>? body}) async {
    return {
      'client_secret': 'fake_secret',
      'expires_at': '2099-01-01T00:00:00Z',
      'model': 'gpt-realtime-2.1',
    };
  }
}

void main() {
  group('RealtimeVoiceService connectionState', () {
    late ControllableWebRtcService fakeWebRtc;
    late RealtimeVoiceService service;

    setUp(() {
      fakeWebRtc = ControllableWebRtcService();
      service = RealtimeVoiceService(
        recorder: FakeRecorder(),
        player: FakePlayer(),
        webRtcService: fakeWebRtc,
        apiClient: FakeApiClient(),
      );
    });

    tearDown(() => service.dispose());

    test('initial state is disconnected', () {
      expect(service.connectionState.value, VoiceConnectionState.disconnected);
    });

    test('connect() transitions connecting -> listening', () async {
      final states = <VoiceConnectionState>[];
      service.connectionState.addListener(() {
        states.add(service.connectionState.value);
      });

      await service.connect();

      expect(states, [
        VoiceConnectionState.connecting,
        VoiceConnectionState.listening,
      ]);
    });

    test('connect() sets final state to listening', () async {
      await service.connect();
      expect(service.connectionState.value, VoiceConnectionState.listening);
    });

    test('connect() failure sets state to error', () async {
      final failSvc = RealtimeVoiceService(
        recorder: FakeRecorder(),
        player: FakePlayer(),
        webRtcService: FailingWebRtcService(),
        apiClient: FakeApiClient(),
      );
      await expectLater(failSvc.connect(), throwsException);
      expect(failSvc.connectionState.value, VoiceConnectionState.error);
      failSvc.dispose();
    });

    test('disconnect() sets state to disconnected', () async {
      await service.connect();
      await service.disconnect();
      expect(service.connectionState.value, VoiceConnectionState.disconnected);
    });

    test('response.created event -> thinking', () async {
      await service.connect();
      fakeWebRtc.injectEvent('{"type":"response.created"}');
      await Future<void>.delayed(Duration.zero);
      expect(service.connectionState.value, VoiceConnectionState.thinking);
    });

    test('output_audio_buffer.started event -> speaking', () async {
      await service.connect();
      fakeWebRtc.injectEvent('{"type":"output_audio_buffer.started"}');
      await Future<void>.delayed(Duration.zero);
      expect(service.connectionState.value, VoiceConnectionState.speaking);
    });

    test('output_audio_buffer.stopped event -> listening', () async {
      await service.connect();
      fakeWebRtc.injectEvent('{"type":"response.created"}');
      fakeWebRtc.injectEvent('{"type":"output_audio_buffer.started"}');
      fakeWebRtc.injectEvent('{"type":"output_audio_buffer.stopped"}');
      await Future<void>.delayed(Duration.zero);
      expect(service.connectionState.value, VoiceConnectionState.listening);
    });

    test('response.done fallback -> listening when thinking', () async {
      await service.connect();
      fakeWebRtc.injectEvent('{"type":"response.created"}');
      fakeWebRtc.injectEvent('{"type":"response.done"}');
      await Future<void>.delayed(Duration.zero);
      expect(service.connectionState.value, VoiceConnectionState.listening);
    });

    test('error event -> error state', () async {
      await service.connect();
      fakeWebRtc.injectEvent('{"type":"error","error":{"message":"test"}}');
      await Future<void>.delayed(Duration.zero);
      expect(service.connectionState.value, VoiceConnectionState.error);
    });

    test('malformed JSON is ignored', () async {
      await service.connect();
      fakeWebRtc.injectEvent('not valid json {{{{');
      await Future<void>.delayed(Duration.zero);
      // State should remain listening, not crash.
      expect(service.connectionState.value, VoiceConnectionState.listening);
    });
  });

  group('RealtimeVoiceService userTranscripts', () {
    late ControllableWebRtcService fakeWebRtc;
    late RealtimeVoiceService service;

    setUp(() {
      fakeWebRtc = ControllableWebRtcService();
      service = RealtimeVoiceService(
        recorder: FakeRecorder(),
        player: FakePlayer(),
        webRtcService: fakeWebRtc,
        apiClient: FakeApiClient(),
      );
    });

    tearDown(() => service.dispose());

    test('input_audio_transcription.completed emits transcript', () async {
      await service.connect();
      final transcripts = <String>[];
      service.userTranscripts.listen(transcripts.add);

      fakeWebRtc.injectEvent('{'
          '"type":"conversation.item.input_audio_transcription.completed",'
          '"item_id":"item_123",'
          '"content_index":0,'
          '"transcript":"こんにちは"'
          '}');
      await Future<void>.delayed(Duration.zero);

      expect(transcripts, ['こんにちは']);
    });

    test('input_audio_transcription.completed with empty transcript is ignored',
        () async {
      await service.connect();
      final transcripts = <String>[];
      service.userTranscripts.listen(transcripts.add);

      fakeWebRtc.injectEvent('{'
          '"type":"conversation.item.input_audio_transcription.completed",'
          '"item_id":"item_123",'
          '"content_index":0,'
          '"transcript":""'
          '}');
      await Future<void>.delayed(Duration.zero);

      expect(transcripts, isEmpty);
    });

    test('input_audio_transcription.completed with null transcript is ignored',
        () async {
      await service.connect();
      final transcripts = <String>[];
      service.userTranscripts.listen(transcripts.add);

      fakeWebRtc.injectEvent('{'
          '"type":"conversation.item.input_audio_transcription.completed",'
          '"item_id":"item_123",'
          '"content_index":0,'
          '"transcript":null'
          '}');
      await Future<void>.delayed(Duration.zero);

      expect(transcripts, isEmpty);
    });

    test('conversation.item.done does not emit transcript (transcript is null)',
        () async {
      await service.connect();
      final transcripts = <String>[];
      service.userTranscripts.listen(transcripts.add);

      fakeWebRtc.injectEvent('{'
          '"type":"conversation.item.done",'
          '"item":{"role":"user","content":[{"type":"input_audio","transcript":null}]}'
          '}');
      await Future<void>.delayed(Duration.zero);

      expect(transcripts, isEmpty);
    });
  });
}
