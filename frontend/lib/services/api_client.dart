import 'dart:convert';

import 'package:http/http.dart' as http;

class ApiClient {
  // エミュレーター: http://10.0.2.2:8000
  // 実機: PC の LAN IP アドレスを使う
  static const String baseUrl = 'http://192.168.11.4:8000';

  Future<dynamic> get(String path) async {
    final response = await http.get(Uri.parse('$baseUrl$path'));
    _checkResponse(response);
    return json.decode(utf8.decode(response.bodyBytes));
  }

  Future<dynamic> post(String path, {Map<String, dynamic>? body}) async {
    final response = await http.post(
      Uri.parse('$baseUrl$path'),
      headers: {'Content-Type': 'application/json'},
      body: body != null ? json.encode(body) : null,
    );
    _checkResponse(response);
    return json.decode(utf8.decode(response.bodyBytes));
  }

  void _checkResponse(http.Response response) {
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(response.statusCode, response.body);
    }
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String body;

  const ApiException(this.statusCode, this.body);

  @override
  String toString() => 'ApiException($statusCode): $body';
}
