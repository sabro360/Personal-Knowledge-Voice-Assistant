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

  // OpenAI Realtime API SDP endpoint (WebRTC offer/answer exchange)
  static const _sdpEndpoint =
      'https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview';

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
  /// 1. Creates an [RTCPeerConnection] with a sendrecv audio transceiver.
  /// 2. Creates an SDP offer and waits for ICE gathering to complete.
  /// 3. POSTs the SDP offer to OpenAI using [clientSecret].
  /// 4. Sets the SDP answer as the remote description.
  ///
  /// T1303 will add the actual microphone track after connection is established.
  Future<void> connect(String clientSecret) async {
    final pc = await createPeerConnection({
      'iceServers': <Map<String, dynamic>>[],
      'sdpSemantics': 'unified-plan',
    });
    _peerConnection = pc;

    // Declare audio capability (sendrecv). T1303 adds the actual mic track.
    await pc.addTransceiver(
      kind: RTCRtpMediaType.RTCRtpMediaTypeAudio,
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
  }

  /// Closes the PeerConnection.
  Future<void> disconnect() async {
    await _peerConnection?.close();
    _peerConnection = null;
  }

  /// Releases all resources.
  Future<void> dispose() async {
    await disconnect();
    await stop();
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
    if (response.statusCode != 201) {
      throw Exception('OpenAI SDP exchange failed: ${response.statusCode}');
    }
    return response.body;
  }
}
