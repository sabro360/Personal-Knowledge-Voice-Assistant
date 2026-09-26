# Personal Knowledge Voice Assistant - TASKS

## Task Status

* [ ] 未着手
* [>] 作業中
* [x] 完了
* [!] Blocked

原則として上から順番に実装する。

1 Task = 1つの明確な目的

可能な限り1 Task = 1 Commitとする。

---

# Phase 0 - Project Definition

## T0001 Repository初期化

* [x] Git repositoryを作成
* [x] README.mdを作成
* [x] CLAUDE.mdを配置
* [x] TASKS.mdを配置
* [x] .gitignoreを作成

完了条件:

* git statusが正常
* Secretが追跡されていない

---

## T0002 Root directory構成作成

作成:

* frontend/
* backend/
* docs/

完了条件:

以下の構成になっている。

project/
frontend/
backend/
docs/
CLAUDE.md
TASKS.md
README.md

---

# Phase 1 - Backend Foundation

## T0101 FastAPI project初期化

backendにFastAPIプロジェクトを作成する。

最低限:

* app/main.py
* tests/

---

## T0102 Health Check API作成

GET:

/health

Response:

{
"status": "ok"
}

---

## T0103 Backend設定管理追加

環境変数管理を実装する。

候補:

pydantic-settings

作成:

* app/core/config.py
* .env.example

---

## T0104 SQLAlchemy導入

SQLAlchemyを追加する。

Database URLを設定から取得する。

---

## T0105 SQLite接続

Development databaseとしてSQLiteを使用する。

例:

app.db

---

## T0106 Alembic導入

Database migrationを管理できる状態にする。

---

# Phase 2 - Conversation Database

## T0201 ConversationSession Model作成 [x]

Fields:

* id
* started_at
* ended_at
* title
* created_at

Migrationを作成する。

---

## T0202 Utterance Model作成 [x]

Fields:

* id
* session_id
* speaker
* text
* timestamp
* sequence_number

---

## T0203 ConversationSession Repository作成 [x]

実装:

* create
* get_by_id
* list
* finish

---

## T0204 Utterance Repository作成 [x]

実装:

* create
* list_by_session

---

## T0205 Repository Unit Test [x]

Session RepositoryとUtterance RepositoryのTestを書く。

---

# Phase 3 - Conversation API

## T0301 Session作成API [x]

POST:

/sessions

Sessionを作成する。

---

## T0302 Session取得API [x]

GET:

/sessions/{session_id}

---

## T0303 Session一覧API [x]

GET:

/sessions

---

## T0304 Utterance追加API [x]

POST:

/sessions/{session_id}/utterances

Request:

{
"speaker": "user",
"text": "..."
}

---

## T0305 Utterance一覧API [x]

GET:

/sessions/{session_id}/utterances

---

## T0306 Session終了API [x]

POST:

/sessions/{session_id}/finish

ended_atを設定する。

---

## T0307 Conversation API Integration Test [x]

以下をTestする。

1. Session作成
2. Utterance追加
3. Utterance取得
4. Session終了

---

# Phase 4 - Flutter Foundation

## T0401 Flutter project作成 [x]

frontend/にFlutter projectを作成する。

Androidを有効にする。

---

## T0402 Development環境確認

以下を確認する。

* flutter doctor
* Android build
* Emulatorまたは実機起動

---

## T0403 Flutter directory整理

作成:

lib/
screens/
widgets/
models/
services/
repositories/
state/

---

## T0404 Backend API Client作成

FastAPIと通信するAPI Clientを作成する。

---

## T0405 Health Check呼び出し

Flutterから:

GET /health

を呼び出す。

---

## T0406 API接続エラー表示

Backend停止時にCrashせずエラー表示する。

---

# Phase 5 - Text Conversation Prototype

音声実装前に会話データフローを完成させる。

---

## T0501 Conversation Screen作成

最低限:

* Message list
* Text input
* Send button
* Finish button

---

## T0502 Session開始処理

画面開始時またはButton押下時にSessionを作る。

---

## T0503 User Utterance保存

Text input内容をBackendへ保存する。

---

## T0504 Assistant Utterance表示

まずはDummy responseでよい。

例:

"You said: ..."

---

## T0505 Assistant Utterance保存

Dummy Assistant responseもDBへ保存する。

---

## T0506 Conversation終了処理

Finish buttonでSessionを終了する。

---

## T0507 Conversation履歴確認

DBに以下が正しい順番で保存されることを確認する。

user

assistant

user

assistant

---

# Phase 6 - Knowledge Database

## T0601 Knowledge Model作成

Fields:

* id
* session_id
* title
* question
* summary
* answer
* category
* created_at
* updated_at

---

## T0602 Keyword Model作成

Fields:

* id
* name

---

## T0603 KnowledgeKeyword Model作成

Many-to-Many relationを実装する。

---

## T0604 Knowledge Repository作成

実装:

* create
* get_by_id
* list
* update

---

## T0605 Keyword Repository作成

実装:

* get_or_create
* list_for_knowledge

---

## T0606 Knowledge Repository Test

Knowledge保存・取得をTestする。

---

# Phase 7 - AI Provider Foundation

## T0701 KnowledgeModel interface定義

InterfaceまたはProtocolを定義する。

責務:

* summarize_conversation
* extract_questions
* extract_keywords
* classify_category
* generate_title

---

## T0702 DummyKnowledgeModel作成

APIを使わず固定結果を返すFake Providerを作る。

目的:

Business Logicを外部AIなしでTest可能にする。

---

## T0703 Knowledge Extraction Service作成

Input:

ConversationSession + Utterances

Output:

Knowledge候補

AI Providerを直接API層から呼ばない。

---

## T0704 Knowledge Extraction Test

DummyKnowledgeModelを使用してTestする。

---

# Phase 8 - Real LLM Integration

## T0801 AI API設定追加

API Keyを環境変数から読み込む。

---

## T0802 OpenAI Knowledge Provider作成

KnowledgeModel interfaceを実装する。

まず対象:

* title
* question
* summary
* answer
* category
* keywords

---

## T0803 Structured Output定義

LLM出力をJSON schema等で構造化する。

期待例:

{
"knowledge": [
{
"title": "...",
"question": "...",
"summary": "...",
"answer": "...",
"category": "...",
"keywords": []
}
]
}

---

## T0804 Invalid Response処理

LLMが不正JSON等を返した場合のエラー処理を実装する。

---

## T0805 Knowledge生成API

POST:

/sessions/{session_id}/knowledge

ConversationからKnowledgeを生成する。

---

## T0806 Session終了との連携

Session終了後にKnowledge生成処理を実行できるようにする。

最初は同期処理でよい。

---

# Phase 9 - Knowledge UI

## T0901 Knowledge一覧API

GET:

/knowledge

---

## T0902 Knowledge詳細API

GET:

/knowledge/{knowledge_id}

---

## T0903 Flutter Knowledge一覧画面

表示:

* title
* category
* created_at

---

## T0904 Flutter Knowledge詳細画面

表示:

* title
* question
* summary
* answer
* keywords
* category

---

## T0905 元Conversationへのリンク

Knowledgeから元Sessionを開けるようにする。

---

# Phase 10 - Search

## T1001 Simple text search実装

まずLIKE等の単純検索でよい。

検索対象:

* title
* question
* summary
* answer

---

## T1002 Search API作成

GET:

/knowledge/search?q=...

---

## T1003 Flutter Search UI作成

Search fieldと結果一覧を作る。

---

## T1004 SQLite FTS5調査

現在の検索実装と比較する。

ここでは実装判断のみでもよい。

---

## T1005 SQLite FTS5導入

有効と判断した場合のみ実装する。

---

# Phase 11 - Voice Foundation

ここからVoice First機能を開始する。

---

## T1101 Flutter microphone permission

AndroidのMicrophone permissionを設定する。

---

## T1102 Audio input確認

マイクから音声を取得できることを確認する。

まだAI接続は行わない。

---

## T1103 Audio output確認

Flutterから音声を再生できることを確認する。

---

## T1104 flutter_webrtc導入

WebRTC dependencyを追加する。

---

## T1105 WebRTC microphone track確認

Local audio trackを取得する。

---

# Phase 12 - Realtime Backend Authentication

## T1201 Realtime Credential API設計

FlutterにPermanent API Keyを渡さない構成にする。

---

## T1202 Ephemeral credential endpoint作成

例:

POST /realtime/session

---

## T1203 Credential error handling

API Key不足

Provider error

Network error

を処理する。

---

# Phase 13 - Realtime Voice Connection

## T1301 Flutter Realtime Service作成

Voice関連コードをUIから分離する。

例:

RealtimeVoiceService

---

## T1302 WebRTC PeerConnection作成

Realtime APIとのPeerConnectionを確立する。

---

## T1303 Microphone track送信

User audioをRealtime APIへ送る。

---

## T1304 AI audio受信

AI response audioを再生する。

---

## T1305 DataChannel作成

Realtime eventを受信する。

---

## T1306 Connection State管理

State:

* disconnected
* connecting
* listening
* thinking
* speaking
* error

---

# Phase 14 - Voice Conversation Persistence

## T1401 User transcript取得

Realtime APIからUser transcriptを取得する。

---

## T1402 User transcript保存

UtteranceとしてBackendへ保存する。

---

## T1403 Assistant transcript取得

Assistant audio responseのTranscriptを取得する。

---

## T1404 Assistant transcript保存

Assistant Utteranceとして保存する。

---

## T1405 Voice sessionとDB session紐付け

Voice Session開始時にConversationSessionを作成する。

---

## T1406 Voice session終了処理

Voice終了時:

1. WebRTC切断
2. Session終了
3. Knowledge生成

を実行する。

---

# Phase 15 - Voice UI

## T1501 Voice Main Screen作成

メイン操作を極端にシンプルにする。

Button:

会話開始

---

## T1502 Listening表示

ユーザー発話待ち状態を表示する。

---

## T1503 Thinking表示

AI処理中状態を表示する。

---

## T1504 Speaking表示

AI発話中状態を表示する。

---

## T1505 Voice error表示

接続失敗等を表示する。

---

## T1506 Conversation終了操作

明示的な終了ボタンを用意する。

---

# Phase 16 - Voice UX Improvement

## T1601 VAD挙動確認

Realtime API標準VADの挙動を確認する。

---

## T1602 Silence threshold調整

必要に応じてTurn Detection設定を調整する。

---

## T1603 Barge-in確認

AI発話途中にUserが発話した場合の動作を確認する。

---

## T1604 Barge-in UI対応

AI音声停止とUser発話開始を正しくUIへ反映する。

---

## T1605 Network disconnect recovery

ネットワーク切断時に適切にSessionを終了または再接続する。

---

# Phase 17 - Knowledge from Voice

## T1701 Voice conversationからKnowledge生成

実際の音声ConversationをKnowledgeへ変換する。

---

## T1702 複数Question抽出

1 Sessionに複数疑問が含まれる場合、複数Knowledgeを作れるようにする。

---

## T1703 派生Question抽出

Conversation途中の追加質問を抽出する。

---

## T1704 Knowledge生成結果確認

10件以上の実会話で品質確認する。

---

# Phase 18 - Retrieval in Conversation

## T1801 Knowledge Search Service整理

AIから呼び出せるSearch Interfaceを定義する。

---

## T1802 Search Tool API作成

AI ToolとしてKnowledge検索を実行できるようにする。

---

## T1803 Realtime AI Tool連携

User:

「前にもこれ聞いた？」

にKnowledge検索を実行する。

---

## T1804 Search resultをAI Contextへ追加

過去KnowledgeをRealtime conversationへ渡す。

---

## T1805 Voice Retrieval E2E Test

例:

過去:
「CDが虹色なのはなぜ？」

今回:
「前に虹色について何か聞いた？」

期待:

過去Knowledgeを検索して音声回答する。

---

# Phase 19 - MVP Stabilization

## T1901 Error logging整理

BackendとFlutter両方に適切なLoggingを追加する。

---

## T1902 API timeout handling

Timeout時の処理を追加する。

---

## T1903 Empty conversation handling

Utteranceなしで終了されたSessionを処理する。

---

## T1904 Knowledge extraction failure handling

Knowledge生成失敗時もConversationを失わない。

---

## T1905 Duplicate Knowledge対策

同一SessionからKnowledge生成APIを複数回呼んでも重複しにくくする。

---

## T1906 Android実機テスト

実機で確認:

* microphone
* speaker
* network
* session保存
* knowledge生成

---

## T1907 30分連続使用テスト

長時間Conversationの問題を確認する。

---

## T1908 20 Session実使用テスト

実際の日常の疑問で20回以上使用する。

---

# Phase 20 - MVP Release

## T2001 README更新

以下を書く。

* Setup
* Backend起動
* Flutter起動
* Environment variables
* Database migration

---

## T2002 Architecture document作成

docs/architecture.md

---

## T2003 Database document作成

docs/database.md

---

## T2004 MVP Build作成

Android buildを生成する。

---

## T2005 MVP Definition of Done確認

以下が可能であればMVP完成。

1. Androidでアプリを開く
2. 会話開始
3. 音声で質問
4. AIが音声回答
5. 複数ターン会話
6. 会話終了
7. Conversation保存
8. Knowledge自動生成
9. Knowledge一覧表示
10. 過去Knowledge検索

---

# Post-MVP

以下はMVP完成後まで実装しない。

## Phase 21

* Embedding
* Semantic Search

## Phase 22

* PostgreSQL
* pgvector

## Phase 23

* Knowledge Relation
* Knowledge Graph

## Phase 24

* Bluetooth headset optimization

## Phase 25

* Background / Screen Off operation

## Phase 26

* iOS

## Phase 27

* Gemini Live Provider

## Phase 28

* Claude Knowledge Provider

## Phase 29

* Knowledge analytics

例:

* 最近よく質問しているカテゴリ
* 繰り返し質問している概念
* 理解が浅い可能性のある分野
* 新しく学んだテーマ
* 関連Knowledge推薦
