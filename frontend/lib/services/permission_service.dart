import 'package:permission_handler/permission_handler.dart';

/// Requests microphone permission from the user.
///
/// Returns true if the permission is granted, false otherwise.
Future<bool> requestMicrophonePermission() async {
  final status = await Permission.microphone.request();
  return status.isGranted;
}
