import 'package:flutter/material.dart';

import '../models/knowledge.dart';
import '../services/knowledge_service.dart';
import 'knowledge_detail_screen.dart';

class KnowledgeSearchScreen extends StatefulWidget {
  const KnowledgeSearchScreen({super.key});

  @override
  State<KnowledgeSearchScreen> createState() => _KnowledgeSearchScreenState();
}

class _KnowledgeSearchScreenState extends State<KnowledgeSearchScreen> {
  final TextEditingController _queryController = TextEditingController();
  List<Knowledge>? _results; // null = 未検索、[] = 結果なし
  bool _isLoading = false;
  String? _error;

  @override
  void dispose() {
    _queryController.dispose();
    super.dispose();
  }

  Future<void> _search() async {
    final q = _queryController.text.trim();
    if (q.isEmpty) return;
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final results = await fetchKnowledgeSearch(q);
      if (mounted) {
        setState(() {
          _results = results;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = '検索に失敗しました';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ナレッジ検索')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _queryController,
                    decoration: const InputDecoration(
                      hintText: 'キーワードを入力',
                      border: OutlineInputBorder(),
                    ),
                    onSubmitted: (_) => _search(),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.search),
                  onPressed: _search,
                ),
              ],
            ),
          ),
          Expanded(child: _buildResults()),
        ],
      ),
    );
  }

  Widget _buildResults() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(child: Text(_error!));
    }
    if (_results == null) {
      return const Center(child: Text('キーワードを入力して検索してください'));
    }
    if (_results!.isEmpty) {
      return const Center(child: Text('検索結果がありません'));
    }
    return ListView.builder(
      itemCount: _results!.length,
      itemBuilder: (context, index) {
        final item = _results![index];
        return ListTile(
          title: Text(item.title ?? '（タイトルなし）'),
          subtitle: Text(item.category ?? '未分類'),
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => KnowledgeDetailScreen(knowledgeId: item.id),
              ),
            );
          },
        );
      },
    );
  }
}
