# Personal Knowledge Voice Assistant

## 1. Project Overview

このプロジェクトは、日常生活で生じた疑問をAIとの音声会話によって深掘りし、その会話から得られた知識を自動的に構造化・保存・検索・再利用できるPersonal Knowledge Assistantを構築することを目的とする。

ユーザーは可能な限り画面を見ずにAIと会話する。

アプリの中心はKnowledge Baseではなく、Voice FirstなAI Assistantである。

基本フロー:

1. ユーザーがスマートフォンで会話を開始する
2. ユーザーが音声で疑問を話す
3. AIが音声で回答する
4. ユーザーが追加質問する
5. 会話を繰り返す
6. 会話終了後に会話ログを保存する
7. 会話から疑問・結論・キーワード等を抽出する
8. Personal Knowledge Databaseへ保存する
9. 後日、音声またはテキストで過去の知識を検索する
10. 過去の知識を新しい会話のコンテキストとして再利用する

---

# 2. Product Principles

以下を優先順位順に重視する。

1. Voice UX
2. Mobile UX
3. 会話ログを確実に保存すること
4. 知識を自動的に構造化すること
5. 過去知識を簡単に検索できること
6. 過去知識をAIとの会話で再利用できること
7. 高度な意味検索
8. 分析・可視化

ユーザーにタグ付けや整理作業を極力要求しない。

基本思想:

「AIと普通に会話しているだけで、自分専用の知識体系が育つ」

---

# 3. Target Platform

MVPではAndroidを第一ターゲットとする。

将来的には以下を検討する。

* iOS
* Web
* Windows
* macOS

Flutterによるクロスプラットフォーム化を前提とする。

---

# 4. Technology Stack

## Mobile

* Flutter
* Dart

主な責務:

* Voice UI
* マイク入力
* 音声再生
* WebRTC
* 会話状態表示
* Knowledge一覧表示
* Knowledge詳細表示
* 検索画面

---

## Voice AI

第一候補:

* OpenAI Realtime API
* GPT-Live系Realtime Model
* WebRTC

Voice AIへの通信は可能な限りFlutterから直接WebRTCで行う。

FastAPIを音声ストリームの単純な中継サーバーとして使用しない。

バックエンドは必要に応じてRealtime接続用の認証情報や一時トークンを発行する。

将来的にVoice Providerを交換できる設計にする。

候補:

* OpenAI Realtime
* Gemini Live
* その他Realtime Voice API

---

# 5. Backend

使用技術:

* Python
* FastAPI
* SQLAlchemy
* Alembic
* Pydantic

MVP Database:

* SQLite

将来的なDatabase:

* PostgreSQL
* pgvector

Backendの責務:

* Session管理
* Utterance保存
* Knowledge保存
* Knowledge抽出
* Keyword管理
* Search
* AI Tool呼び出し
* 認証
* Realtime API用トークン発行

---

# 6. Architecture

基本構成:

Flutter
|
| WebRTC
v
Realtime Voice AI

Flutter
|
| HTTPS / WebSocket
v
FastAPI
|
+-- Conversation Service
+-- Knowledge Service
+-- Search Service
+-- AI Provider
+-- Database
|
+-- SQLite

音声経路とKnowledge管理経路は可能な限り分離する。

---

# 7. AI Provider Abstraction

AIサービスをコード全体から直接呼び出してはならない。

Provider層を設ける。

例:

VoiceProvider

KnowledgeModel

EmbeddingProvider

SearchProvider

想定インターフェース:

KnowledgeModel:

* summarize_conversation()
* extract_questions()
* extract_knowledge()
* extract_keywords()
* classify_category()
* generate_title()

EmbeddingProvider:

* embed_text()
* embed_query()

VoiceProvider:

* create_session()
* close_session()
* create_realtime_credentials()

特定ベンダーへの依存をService層へ漏らさない。

---

# 8. Database Design

最低限以下のEntityを持つ。

## ConversationSession

* id
* started_at
* ended_at
* title
* created_at

## Utterance

* id
* session_id
* speaker
* text
* timestamp
* sequence_number

speaker:

* user
* assistant
* system

## Knowledge

* id
* session_id
* title
* question
* summary
* answer
* category
* created_at
* updated_at

## Keyword

* id
* name

## KnowledgeKeyword

* knowledge_id
* keyword_id

## KnowledgeRelation

* id
* source_knowledge_id
* target_knowledge_id
* relation_type

RelationはMVP後半まで必須ではない。

---

# 9. Conversation Data Policy

生の会話ログと構造化Knowledgeを分離する。

ConversationSession
|
+-- Utterance
+-- Utterance
+-- Utterance
|
+-- Knowledge
+-- Knowledge

会話ログをKnowledge生成後に削除してはならない。

Knowledge生成ロジックを将来変更した場合、過去のUtteranceからKnowledgeを再生成できる設計にする。

---

# 10. MVP Scope

MVPで必須:

* Androidアプリ起動
* 会話開始
* マイク入力
* AI音声回答
* 複数ターン会話
* ConversationSession作成
* Utterance保存
* 会話終了
* Knowledge自動抽出
* Knowledge保存
* Knowledge一覧
* Knowledge詳細
* テキスト検索

MVPでは必須ではない:

* Vector Search
* pgvector
* 複雑なKnowledge Graph
* SNS機能
* 複数ユーザー
* PC版
* iOS最適化
* 高度な統計Dashboard

---

# 11. Voice UX Requirements

最終目標は画面を見ずに使用できることである。

理想的な状態:

User:
「なぜCDって虹色なの？」

AI:
音声回答

User:
「水滴の場合とは違う？」

AI:
音声回答

User:
「今日は終わり」

AI:
会話終了

バックグラウンドでKnowledgeを生成する。

将来的に対応する:

* VAD
* Barge-in
* AI発話途中のユーザー割り込み
* Bluetooth Headset
* Background Audio
* Screen Off
* Wake Word

これらは段階的に実装する。

---

# 12. UI Philosophy

UIは可能な限り単純にする。

メイン画面で最も重要な操作:

「会話開始」

会話中は以下のみを明確に表示する。

* Listening
* Thinking
* Speaking
* Error

画面操作を必要以上に増やさない。

Knowledge管理画面はVoice UIとは分離する。

---

# 13. API Design Rules

REST APIを基本とする。

例:

POST /sessions

GET /sessions

GET /sessions/{id}

POST /sessions/{id}/utterances

POST /sessions/{id}/finish

GET /knowledge

GET /knowledge/{id}

GET /knowledge/search

必要になるまでWebSocketを追加しない。

Realtime Voice通信についてはRealtime API / WebRTCを使用する。

---

# 14. Coding Rules

## Python

* Python 3.12以降を想定
* type hint必須
* public functionにはdocstringを付ける
* PydanticをAPI schemaに使用
* ORM ModelとAPI Schemaを分離する
* Service層からHTTP依存を排除する
* global stateを極力使用しない

## Dart / Flutter

* Widget内にBusiness Logicを書きすぎない
* UI / State / Serviceを分離する
* API Clientを画面から直接呼び出さない
* 非同期処理のerror stateを必ず考慮する

---

# 15. Directory Structure

Backend:

backend/
app/
main.py
api/
models/
schemas/
services/
repositories/
providers/
db/
core/
tests/

Frontend:

frontend/
lib/
main.dart
screens/
widgets/
models/
services/
repositories/
providers/
state/

構造を変更する場合は実装前に理由を提示する。

---

# 16. Testing Policy

新しいBusiness Logicには原則テストを書く。

特に以下を優先する。

* Knowledge extraction
* Database操作
* Session lifecycle
* Search
* API endpoint

テストなしで大規模な変更を行わない。

---

# 17. Git Policy

1 Task = 原則1 Commitとする。

Commit例:

feat: add conversation session model

feat: add utterance persistence

feat: add knowledge extraction service

fix: handle realtime disconnect

refactor: separate knowledge provider

大量の機能を1 Commitにまとめない。

---

# 18. Claude Development Workflow

Claudeは実装依頼を受けた場合、原則以下の手順を取る。

1. TASKS.mdを確認する
2. 対象Taskを確認する
3. 関連コードを読む
4. 実装計画を提示する
5. 変更予定ファイルを提示する
6. 実装する
7. Test / Lintを実行する
8. 結果を確認する
9. TASKS.mdを更新する
10. 実装結果を報告する

---

# 19. Important Claude Rules

Claudeは以下を守ること。

## Do

* 既存コードを読んでから変更する
* 小さい変更単位で実装する
* 型を明確にする
* エラー処理を書く
* テスト可能な設計にする
* APIの責務を明確にする
* Provider abstractionを維持する

## Do Not

* 一度に複数Phaseを実装しない
* 指示されていない大規模Refactoringを行わない
* AI ProviderをBusiness Logicへ直接埋め込まない
* API Keyをコードへ書かない
* SQLiteに特化したロジックをService層へ書かない
* UI Widgetへ大量のBusiness Logicを書かない
* Vector DBをMVP初期から導入しない
* 将来機能を先回りして大量実装しない

---

# 20. Security

秘密情報は環境変数で管理する。

Git管理禁止:

* API Key
* Secret
* Token
* .env

`.env.example`のみGitへ登録する。

Mobileアプリへ長期間有効なServer API Keyを埋め込まない。

Realtime API接続にはBackendから取得した短時間有効なCredentialを利用する。

---

# 21. Definition of Done

Task完了条件:

* 要求を満たしている
* Build成功
* Test成功
* Lintで重大な問題なし
* Error pathを考慮している
* 不要なDebug codeがない
* Secretが含まれていない
* TASKS.md更新済み

---

# 22. Development Priority

迷った場合は以下の優先順位で判断する。

1. Voice conversation works
2. Conversation is not lost
3. Knowledge is generated correctly
4. Knowledge can be retrieved
5. Architecture remains maintainable
6. UX improvement
7. Performance optimization
8. Advanced features

---

# 23. Core Principle

このプロジェクトの価値は、

「高度なKnowledge Databaseを作ること」

ではない。

価値は、

「日常で生じた疑問をAIと自然に会話するだけで、それが自分の知識として蓄積され、後から再利用できること」

にある。

技術的判断では常にこの原則を優先する。
