import 'dart:async';
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:voice_assistant/models/voice_connection_state.dart';
import 'package:voice_assistant/services/api_client.dart';
import 'package:voice_assistant/services/audio_player_service.dart';
import 'package:voice_assistant/services/audio_recorder_service.dart';
import 'package:voice_assistant/services/realtime_voice_service.dart';
import 'package:voice_assistant/services/webrtc_service.dart';

// ---------------------------------------------------------------------------
// Fakes
// ---------------------------------------------------------------------------

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

/// WebRtcService that injects events into the stream and records sent messages.
class CapturingWebRtcService extends WebRtcService {
  final _testController = StreamController<String>.broadcast();
  final List<String> sentMessages = [];

  @override
  Stream<String> get events => _testController.stream;

  void injectEvent(String json) => _testController.add(json);

  @override
  Future<void> sendMessage(String json) async => sentMessages.add(json);

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

/// ApiClient that records calls and returns appropriate dummy data per path.
class TrackingApiClient extends ApiClient {
  final List<String> calledPaths = [];
  final List<Map<String, dynamic>?> calledBodies = [];

  @override
  Future<dynamic> post(String path, {Map<String, dynamic>? body}) async {
    calledPaths.add(path);
    calledBodies.add(body);

    if (path == '/realtime/session') {
      return {
        'client_secret': 'fake_secret',
        'expires_at': '2099-01-01T00:00:00Z',
        'model': 'gpt-realtime-2.1',
      };
    }
    if (path == '/knowledge/search_tool') {
      return {
        'results': [
          {'title': 'CDの虹色', 'question': null, 'summary': '回折', 'answer': null, 'category': null}
        ],
        'count': 1,
      };
    }
    return {};
  }
}

// ---------------------------------------------------------------------------
// Helper
// ---------------------------------------------------------------------------

String _responseDoneWithFunctionCall({
  String callId = 'call_abc',
  String name = 'search_knowledge',
  String argsJson = '{"query":"CD"}',
}) {
  return jsonEncode({
    'type': 'response.done',
    'response': {
      'output': [
        {
          'type': 'function_call',
          'call_id': callId,
          'name': name,
          'arguments': argsJson,
        }
      ],
    },
  });
}

String _responseDoneNoFunctionCall() {
  return jsonEncode({
    'type': 'response.done',
    'response': {'output': []},
  });
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  group('RealtimeVoiceService tool calls', () {
    late CapturingWebRtcService fakeWebRtc;
    late TrackingApiClient trackingApiClient;
    late RealtimeVoiceService service;

    setUp(() {
      fakeWebRtc = CapturingWebRtcService();
      trackingApiClient = TrackingApiClient();
      service = RealtimeVoiceService(
        recorder: FakeRecorder(),
        player: FakePlayer(),
        webRtcService: fakeWebRtc,
        apiClient: trackingApiClient,
      );
    });

    tearDown(() => service.dispose());

    test('response.done with function_call calls POST /knowledge/search_tool',
        () async {
      await service.connect();

      fakeWebRtc.injectEvent(_responseDoneWithFunctionCall());

      // Allow async _handleFunctionCalls to run.
      await Future<void>.delayed(const Duration(milliseconds: 50));

      expect(trackingApiClient.calledPaths, contains('/knowledge/search_tool'));
      final idx = trackingApiClient.calledPaths.indexOf('/knowledge/search_tool');
      expect(trackingApiClient.calledBodies[idx], {'query': 'CD'});
    });

    test('response.done with function_call sends conversation.item.create',
        () async {
      await service.connect();
      fakeWebRtc.sentMessages.clear(); // clear session.update sent on connect

      fakeWebRtc.injectEvent(_responseDoneWithFunctionCall(callId: 'call_123'));

      await Future<void>.delayed(const Duration(milliseconds: 50));

      final itemCreateMsgs = fakeWebRtc.sentMessages
          .map((m) => jsonDecode(m) as Map<String, dynamic>)
          .where((m) => m['type'] == 'conversation.item.create')
          .toList();

      expect(itemCreateMsgs, isNotEmpty);
      final item = itemCreateMsgs.first['item'] as Map<String, dynamic>;
      expect(item['type'], 'function_call_output');
      expect(item['call_id'], 'call_123');
      expect(item['output'], isA<String>());
    });

    test('response.done with function_call sends response.create last',
        () async {
      await service.connect();
      fakeWebRtc.sentMessages.clear();

      fakeWebRtc.injectEvent(_responseDoneWithFunctionCall());

      await Future<void>.delayed(const Duration(milliseconds: 50));

      final types = fakeWebRtc.sentMessages
          .map((m) => (jsonDecode(m) as Map<String, dynamic>)['type'])
          .toList();
      expect(types.last, 'response.create');
    });

    test('response.done without function_call transitions to listening',
        () async {
      await service.connect();
      fakeWebRtc.injectEvent('{"type":"response.created"}'); // thinking
      await Future<void>.delayed(Duration.zero);

      fakeWebRtc.injectEvent(_responseDoneNoFunctionCall());
      await Future<void>.delayed(Duration.zero);

      expect(service.connectionState.value, VoiceConnectionState.listening);
    });
  });
}
