import 'package:flutter/material.dart';

import '../models/knowledge.dart';
import '../services/knowledge_service.dart';

class KnowledgeDetailScreen extends StatefulWidget {
  final int knowledgeId;

  const KnowledgeDetailScreen({super.key, required this.knowledgeId});

  @override
  State<KnowledgeDetailScreen> createState() => _KnowledgeDetailScreenState();
}

class _KnowledgeDetailScreenState extends State<KnowledgeDetailScreen> {
  Knowledge? _knowledge;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadDetail();
  }

  Future<void> _loadDetail() async {
    try {
      final knowledge = await fetchKnowledgeDetail(widget.knowledgeId);
      if (mounted) {
        setState(() {
          _knowledge = knowledge;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'ナレッジの取得に失敗しました';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ナレッジ詳細')),
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
    final k = _knowledge!;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (k.title != null) ...[
            Text(k.title!, style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 8),
          ],
          if (k.category != null)
            Chip(label: Text(k.category!)),
          if (k.keywords.isNotEmpty) ...[
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: k.keywords.map((kw) => Chip(label: Text(kw))).toList(),
            ),
          ],
          if (k.question != null) ...[
            const SizedBox(height: 16),
            _buildSection('疑問', k.question!),
          ],
          if (k.summary != null) ...[
            const SizedBox(height: 16),
            _buildSection('まとめ', k.summary!),
          ],
          if (k.answer != null) ...[
            const SizedBox(height: 16),
            _buildSection('回答', k.answer!),
          ],
        ],
      ),
    );
  }

  Widget _buildSection(String label, String content) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 4),
        Text(content),
      ],
    );
  }
}
