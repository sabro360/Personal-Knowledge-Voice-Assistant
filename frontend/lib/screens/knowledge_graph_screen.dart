import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../models/knowledge_graph.dart';
import '../services/knowledge_service.dart';
import 'knowledge_detail_screen.dart';

class KnowledgeGraphScreen extends StatefulWidget {
  const KnowledgeGraphScreen({super.key});

  @override
  State<KnowledgeGraphScreen> createState() => _KnowledgeGraphScreenState();
}

class _KnowledgeGraphScreenState extends State<KnowledgeGraphScreen> {
  KnowledgeGraph? _graph;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadGraph();
  }

  Future<void> _loadGraph() async {
    try {
      final graph = await fetchKnowledgeGraph();
      if (mounted) {
        setState(() {
          _graph = graph;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'グラフの取得に失敗しました';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ナレッジグラフ')),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(child: Text(_error!));
    }
    final graph = _graph!;
    if (graph.nodes.isEmpty) {
      return const Center(child: Text('ナレッジがありません'));
    }
    return InteractiveViewer(
      boundaryMargin: const EdgeInsets.all(200),
      minScale: 0.3,
      maxScale: 3.0,
      child: SizedBox(
        width: 800,
        height: 800,
        child: _GraphWidget(
          graph: graph,
          onNodeTap: (id) {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => KnowledgeDetailScreen(knowledgeId: id),
              ),
            );
          },
        ),
      ),
    );
  }
}

class _GraphWidget extends StatelessWidget {
  final KnowledgeGraph graph;
  final void Function(int knowledgeId) onNodeTap;

  const _GraphWidget({required this.graph, required this.onNodeTap});

  @override
  Widget build(BuildContext context) {
    final n = graph.nodes.length;
    const centerX = 400.0;
    const centerY = 400.0;
    const radius = 280.0;
    const nodeRadius = 40.0;

    // Compute circular layout positions
    final positions = List.generate(n, (i) {
      final angle = 2 * math.pi * i / n - math.pi / 2;
      return Offset(
        centerX + radius * math.cos(angle),
        centerY + radius * math.sin(angle),
      );
    });

    final nodeIndex = {
      for (var i = 0; i < n; i++) graph.nodes[i].id: i,
    };

    return Stack(
      children: [
        // Edge layer
        CustomPaint(
          size: const Size(800, 800),
          painter: _EdgePainter(
            graph: graph,
            positions: positions,
            nodeIndex: nodeIndex,
          ),
        ),
        // Node layer
        for (var i = 0; i < n; i++)
          Positioned(
            left: positions[i].dx - nodeRadius,
            top: positions[i].dy - nodeRadius,
            child: GestureDetector(
              onTap: () => onNodeTap(graph.nodes[i].id),
              child: _NodeWidget(
                label: graph.nodes[i].title ?? '(no title)',
                radius: nodeRadius,
              ),
            ),
          ),
      ],
    );
  }
}

class _NodeWidget extends StatelessWidget {
  final String label;
  final double radius;

  const _NodeWidget({required this.label, required this.radius});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: radius * 2,
      height: radius * 2,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.primary,
        shape: BoxShape.circle,
      ),
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(6),
          child: Text(
            label.length > 20 ? '${label.substring(0, 18)}…' : label,
            style: TextStyle(
              color: Theme.of(context).colorScheme.onPrimary,
              fontSize: 10,
            ),
            textAlign: TextAlign.center,
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ),
    );
  }
}

class _EdgePainter extends CustomPainter {
  final KnowledgeGraph graph;
  final List<Offset> positions;
  final Map<int, int> nodeIndex;

  const _EdgePainter({
    required this.graph,
    required this.positions,
    required this.nodeIndex,
  });

  @override
  void paint(Canvas canvas, Size size) {
    for (final edge in graph.edges) {
      final srcIdx = nodeIndex[edge.sourceKnowledgeId];
      final tgtIdx = nodeIndex[edge.targetKnowledgeId];
      if (srcIdx == null || tgtIdx == null) continue;

      final paint = Paint()
        ..color = Colors.grey.withOpacity(edge.score.clamp(0.2, 1.0))
        ..strokeWidth = 1.5 + edge.score * 2
        ..style = PaintingStyle.stroke;

      canvas.drawLine(positions[srcIdx], positions[tgtIdx], paint);
    }
  }

  @override
  bool shouldRepaint(_EdgePainter old) =>
      old.graph != graph || old.positions != positions;
}
