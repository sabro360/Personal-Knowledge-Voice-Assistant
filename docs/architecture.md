# Architecture

## System Overview

```
Flutter (Android)
    │
    ├─ WebRTC ────────────────────────────── OpenAI Realtime API
    │   (音声ストリーム / DataChannel)         (gpt-realtime-2.1)
    │
    └─ HTTPS ─────────────────────────────── FastAPI Backend
        (REST API)                              │
                                                ├─ SQLite (MVP)
                                                └─ OpenAI API
                                                   (gpt-4o-mini / Knowledge 抽出)
```

音声経路（WebRTC）とデータ経路（REST API）を分離している。
Backend は音声ストリームを中継しない。Ephemeral Token 発行と Knowledge 管理のみを担当する。

---

## Backend Layer Structure

```
app/api/            HTTP リクエスト受付・バリデーション（FastAPI router）
app/services/       Business Logic（Knowledge 抽出・検索）
app/repositories/   DB アクセス抽象化（SQLAlchemy）
app/providers/      外部 AI サービス抽象化（Protocol + 実装）
app/models/         ORM エンティティ（SQLAlchemy）
app/schemas/        API スキーマ（Pydantic）
app/core/           設定・環境変数管理
app/db/             DB エンジン・セッション管理
```

---

## API Endpoints

| Method | Path | 説明 |
|--------|------|------|
| GET | /health | ヘルスチェック |
| POST | /sessions | セッション作成 |
| GET | /sessions | セッション一覧 |
| GET | /sessions/{id} | セッション取得 |
| POST | /sessions/{id}/utterances | 発話追加 |
| GET | /sessions/{id}/utterances | 発話一覧 |
| POST | /sessions/{id}/finish | セッション終了 + Knowledge 自動生成 |
| POST | /sessions/{id}/knowledge | Knowledge 手動生成 |
| GET | /knowledge | Knowledge 一覧 |
| GET | /knowledge/{id} | Knowledge 詳細（keywords 付き） |
| GET | /knowledge/search | テキスト検索 |
| POST | /knowledge/search_tool | AI Tool Call 用検索 |
| POST | /realtime/session | Ephemeral クレデンシャル発行 |

---

## Database Schema

```
ConversationSession
  id, started_at, ended_at, title, created_at
    │
    ├─ Utterance (1:N)
    │    id, session_id, speaker (user|assistant|system),
    │    text, timestamp, sequence_number
    │
    └─ Knowledge (1:N)
         id, session_id, title, question, summary,
         answer, category, related_questions (JSON),
         created_at, updated_at
           │
           └─ KnowledgeKeyword (N:M)
                knowledge_id, keyword_id
                  │
                  └─ Keyword
                       id, name (unique)
```

---

## Provider Abstraction

将来ベンダーを切り替えられるよう Provider 層で抽象化している。

```
VoiceProvider (Protocol)
  └─ OpenAIVoiceProvider   → OpenAI Realtime API (gpt-realtime-2.1)
  └─ DummyVoiceProvider    → テスト用

KnowledgeModel (Protocol)
  └─ OpenAIKnowledgeModel  → OpenAI API (gpt-4o-mini, structured output)
  └─ DummyKnowledgeModel   → テスト用
```

Service 層は Provider の具体的な実装に依存しない。
FastAPI の `Depends()` で実行時に注入する。

---

## Voice Connection Flow

```
Flutter
  │
  ├─ POST /realtime/session
  │     └─ Backend → OpenAI POST /v1/realtime/client_secrets
  │     ← client_secret (ek_...), expires_at, model
  │
  └─ POST https://api.openai.com/v1/realtime/calls
        Content-Type: application/sdp  (SDP offer)
        Authorization: Bearer {client_secret}
        ← SDP answer (200 or 201)

WebRTC 接続確立
  ├─ AudioTrack → AI 音声受信・再生
  └─ DataChannel → Realtime イベント送受信
```

### DataChannel イベント（主要）

| イベント | 意味 |
|---------|------|
| `session.created` | 接続完了 → `session.update` で設定送信 |
| `response.created` | AI 処理開始（thinking 状態） |
| `output_audio_buffer.started` | AI 音声出力開始（speaking 状態） |
| `response.done` | AI ターン完了（listening 状態へ） |
| `conversation.item.input_audio_transcription.completed` | ユーザー発話テキスト |
| `response.output_audio_transcript.done` | AI 発話テキスト |
| `input_audio_buffer.speech_started` | ユーザー発話開始（Barge-in 検出） |

---

## Knowledge Extraction Flow

```
POST /sessions/{id}/finish
  │
  ├─ ConversationSessionRepository.finish()     セッション終了マーク
  ├─ UtteranceRepository.list_by_session()      発話取得
  │
  └─ KnowledgeExtractionService.extract()
       ├─ utterances が空 → スキップ（return []）
       ├─ KnowledgeRepository.list_by_session() → 既存あり → 重複スキップ
       ├─ OpenAIKnowledgeModel.extract_knowledge()  ← LLM 呼び出し（1回）
       │    └─ gpt-4o-mini + structured output → list[KnowledgeExtraction]
       └─ 各 KnowledgeExtraction に対して:
            ├─ KnowledgeRepository.create()
            └─ KeywordRepository.get_or_create() + KnowledgeKeyword 登録
```

Knowledge 抽出失敗は非ブロッキング。失敗しても Session 終了は成功する。

---

## Flutter Layer Structure

```
lib/
  main.dart                  エントリーポイント（VoiceMainScreen を起動）
  screens/                   画面 Widget
  services/                  外部通信・デバイス操作
  models/                    データモデル（Dart）
```

### 画面遷移

```
VoiceMainScreen（デフォルト）
  └─ 会話開始 → WebRTC 接続 → Listening/Thinking/Speaking
  └─ 終了ボタン → セッション終了 → KnowledgeListScreen

KnowledgeListScreen
  └─ タップ → KnowledgeDetailScreen

KnowledgeSearchScreen
  └─ テキスト検索 → 結果一覧
```

### State Management

```
RealtimeVoiceService
  ├─ ValueNotifier<VoiceConnectionState>  UI 状態（6種）
  ├─ ValueNotifier<bool> isConnected
  ├─ Stream<String> userTranscripts       ユーザー発話テキスト
  └─ Stream<String> assistantTranscripts  AI 発話テキスト
```

`VoiceConnectionState`: `disconnected / connecting / listening / thinking / speaking / error`

---

## Key Design Decisions

| 決定 | 理由 |
|------|------|
| 音声は Flutter → OpenAI 直接（Backend 中継なし） | レイテンシ最小化、Backend の負荷軽減 |
| Backend は Ephemeral Token 発行のみ | 長期 API Key をモバイルに渡さない（セキュリティ） |
| Knowledge 抽出は Session finish 時に同期実行 | MVP では非同期キューは過剰 |
| SQLite を MVP DB として採用 | セットアップ不要、スケールは将来課題 |
| ORM Model と API Schema を分離 | DB 変更と API 変更を独立して行える |
| Provider Protocol で AI を抽象化 | 将来のベンダー切り替えに対応 |

---

## Future Extensions (Post-MVP)

- **Vector Search**: pgvector による意味検索
- **PostgreSQL 移行**: スケーラビリティ対応
- **iOS / Web**: Flutter クロスプラットフォーム展開
- **Gemini Live Provider**: VoiceProvider の実装追加
- **Knowledge Graph**: KnowledgeRelation テーブルによる関連可視化
- **Background Audio / Wake Word**: Screen Off での音声操作
