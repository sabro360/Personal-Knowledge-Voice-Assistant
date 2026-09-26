import 'package:flutter/material.dart';

import 'services/health_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Voice Assistant',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const BackendStatusPage(),
    );
  }
}

class BackendStatusPage extends StatelessWidget {
  const BackendStatusPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice Assistant'),
      ),
      body: Center(
        child: FutureBuilder<String>(
          future: checkHealth(),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const CircularProgressIndicator();
            }
            if (snapshot.hasError) {
              return Text(healthErrorMessage(snapshot.error!));
            }
            return Text('Backend: ${snapshot.data}');
          },
        ),
      ),
    );
  }
}
