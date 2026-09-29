import 'dart:async';

import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:http/http.dart' as http;

/// Service for low-level WebRTC operations.
///
/// Handles local audio track acquisition and PeerConnection lifecycle,
/// including SDP negotiation with the OpenAI Realtime API.
class WebRtcService {
  MediaStream? _localStream;
  RTCPeerConnection? _peerConnection;
  RTCDataChannel? _dataChannel;
  final _eventsController = StreamController<String>.broadcast();

  /// Called when the PeerConnection transitions to a failed or disconnected state.
  void Function()? onDisconnected;

  /// Stream of raw JSON event strings received from the OpenAI Realtime API
  /// via the 'oai-events' DataChannel.
  Stream<String> get events => _eventsController.stream;

  // OpenAI Realtime API SDP endpoint (WebRTC offer/answer exchange)
  static const _sdpEndpoint = 'https://api.openai.com/v1/realtime/calls';

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

  /// Establishes a WebRTC PeerConnection with the OpenAI Realtime API.
  ///
  /// Steps:
  /// 1. Acquires the microphone track via [getLocalAudioTrack].
  /// 2. Creates an [RTCPeerConnection] with the track in a sendrecv transceiver.
  /// 3. Creates an SDP offer and waits for ICE gathering to complete.
  /// 4. POSTs the SDP offer to OpenAI using [clientSecret].
  /// 5. Sets the SDP answer as the remote description.
  Future<void> connect(String clientSecret) async {
    // Release any existing local stream before starting a new connection.
    await stop();

    // Acquire the microphone track before creating the offer so the SDP
    // reflects the actual track rather than an empty transceiver.
    final track = await getLocalAudioTrack();

    final pc = await createPeerConnection({
      'iceServers': <Map<String, dynamic>>[],
      'sdpSemantics': 'unified-plan',
    });
    _peerConnection = pc;

    pc.onConnectionState = (RTCPeerConnectionState state) {
      if (state == RTCPeerConnectionState.RTCPeerConnectionStateFailed ||
          state == RTCPeerConnectionState.RTCPeerConnectionStateDisconnected) {
        onDisconnected?.call();
      }
    };

    // Create DataChannel for Realtime events before createOffer so it
    // is included in the SDP offer sent to OpenAI.
    _dataChannel = await pc.createDataChannel(
      'oai-events',
      RTCDataChannelInit(),
    );
    _dataChannel!.onMessage = (RTCDataChannelMessage message) {
      if (!message.isBinary) _eventsController.add(message.text);
    };

    // Add the microphone track with sendrecv direction.
    await pc.addTransceiver(
      track: track,
      init: RTCRtpTransceiverInit(direction: TransceiverDirection.SendRecv),
    );

    final offer = await pc.createOffer({});
    await pc.setLocalDescription(offer);

    await _waitForIceGathering(pc);

    final localDesc = await pc.getLocalDescription();
    final sdpAnswer = await _exchangeSdp(
      clientSecret: clientSecret,
      sdpOffer: localDesc!.sdp!,
    );

    await pc.setRemoteDescription(RTCSessionDescription(sdpAnswer, 'answer'));

    // Route audio to speakerphone rather than earpiece.
    await Helper.setSpeakerphoneOn(true);
  }

  /// Sends a JSON string message via the 'oai-events' DataChannel.
  ///
  /// No-op if the DataChannel is not available.
  Future<void> sendMessage(String json) async {
    final dc = _dataChannel;
    if (dc == null) return;
    await dc.send(RTCDataChannelMessage(json));
  }

  /// Closes the PeerConnection.
  Future<void> disconnect() async {
    _dataChannel?.close();
    _dataChannel = null;
    await _peerConnection?.close();
    _peerConnection = null;
  }

  /// Releases all resources.
  Future<void> dispose() async {
    await disconnect();
    await stop();
    await _eventsController.close();
  }

  Future<void> _waitForIceGathering(RTCPeerConnection pc) async {
    if (pc.iceGatheringState ==
        RTCIceGatheringState.RTCIceGatheringStateComplete) {
      return;
    }
    final completer = Completer<void>();
    pc.onIceGatheringState = (state) {
      if (state == RTCIceGatheringState.RTCIceGatheringStateComplete) {
        if (!completer.isCompleted) completer.complete();
      }
    };
    await completer.future;
  }

  Future<String> _exchangeSdp({
    required String clientSecret,
    required String sdpOffer,
  }) async {
    final response = await http.post(
      Uri.parse(_sdpEndpoint),
      headers: {
        'Authorization': 'Bearer $clientSecret',
        'Content-Type': 'application/sdp',
      },
      body: sdpOffer,
    );
    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception('OpenAI SDP exchange failed: ${response.statusCode}');
    }
    return response.body;
  }
}
