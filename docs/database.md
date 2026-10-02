# Database

## Overview

本番環境は PostgreSQL（Railway managed）を使用する。Alembic でマイグレーションを管理する。
ローカル開発は SQLite を使用する（`DATABASE_URL=sqlite:///./app.db`）。
pgvector extension は有効化済み。`knowledge` テーブルに `embedding` カラム（Vector(1536)）を追加し、セマンティック検索を実現している（Phase 22）。

---

## Tables

### conversation_sessions

会話セッションを管理する。

| カラム | 型 | 制約 | 説明 |
|-------|----|------|------|
| id | INTEGER | PK, autoincrement | セッション ID |
| started_at | DATETIME | NOT NULL | 会話開始日時（TZ-aware） |
| ended_at | DATETIME | NULL | 会話終了日時（終了前は NULL） |
| title | VARCHAR | NULL | セッションタイトル（未使用: NULL） |
| created_at | DATETIME | NOT NULL | レコード作成日時 |

---

### utterances

セッション内の個別発話を管理する。

| カラム | 型 | 制約 | 説明 |
|-------|----|------|------|
| id | INTEGER | PK, autoincrement | 発話 ID |
| session_id | INTEGER | FK → conversation_sessions.id | 所属セッション |
| speaker | VARCHAR | NOT NULL | 発話者（user / assistant / system） |
| text | TEXT | NOT NULL | 発話テキスト |
| timestamp | DATETIME | NOT NULL | 発話日時（TZ-aware） |
| sequence_number | INTEGER | NOT NULL | セッション内の発話順序（1始まり） |

`speaker` の値:

| 値 | 意味 |
|----|------|
| `user` | ユーザーの発話 |
| `assistant` | AI の発話 |
| `system` | システムメッセージ |

---

### knowledge

セッションから抽出した知識を管理する。

| カラム | 型 | 制約 | 説明 |
|-------|----|------|------|
| id | INTEGER | PK, autoincrement | Knowledge ID |
| session_id | INTEGER | FK → conversation_sessions.id | 元セッション |
| title | VARCHAR | NULL | 知識のタイトル |
| question | TEXT | NULL | 疑問・問い |
| summary | TEXT | NULL | 要約 |
| answer | TEXT | NULL | 回答 |
| category | VARCHAR | NULL | カテゴリ（1〜3 語） |
| related_questions | TEXT | NULL | 派生質問リスト（JSON 配列） |
| embedding | VECTOR(1536) | NULL | テキスト埋め込みベクトル（text-embedding-3-small）。PostgreSQL のみ。NULL = 未生成 |
| created_at | DATETIME | NOT NULL | 抽出日時 |
| updated_at | DATETIME | NOT NULL | 更新日時 |

---

### keywords

Knowledge に付与するキーワードを管理する。重複なし（unique）。

| カラム | 型 | 制約 | 説明 |
|-------|----|------|------|
| id | INTEGER | PK, autoincrement | キーワード ID |
| name | VARCHAR | NOT NULL, UNIQUE | キーワード文字列 |

---

### knowledge_keywords

Knowledge と Keyword の多対多関係を管理する。

| カラム | 型 | 制約 | 説明 |
|-------|----|------|------|
| knowledge_id | INTEGER | FK → knowledge.id | Knowledge |
| keyword_id | INTEGER | FK → keywords.id | Keyword |

Primary Key は (knowledge_id, keyword_id) の複合キー。

---

## Entity Relationship

```
conversation_sessions
  │  id (PK)
  │
  ├─── utterances (1:N)
  │      session_id (FK)
  │
  └─── knowledge (1:N)
         session_id (FK)
           │
           └─── knowledge_keywords (N:M)
                  knowledge_id (FK)
                  keyword_id   (FK)
                    │
                    └─── keywords
                           id (PK)
                           name (UNIQUE)
```

---

## Migration

Alembic でマイグレーションを管理する。

```bash
cd backend

# 現在の状態を確認
uv run alembic current

# 最新に適用
uv run alembic upgrade head

# 新しい migration を作成（開発時）
uv run alembic revision --autogenerate -m "description"

# 1つ前に戻す
uv run alembic downgrade -1
```

マイグレーションファイルの場所: `backend/alembic/versions/`

---

## Design Decisions

| 決定 | 理由 |
|------|------|
| 生の会話ログ（utterances）と Knowledge を分離 | LLM モデル変更時に utterances から Knowledge を再生成できる |
| utterances を Knowledge 生成後も削除しない | 会話履歴の保全・再抽出に対応するため |
| related_questions を JSON カラムで管理 | MVP では正規化コストが見合わない |
| keywords を正規化（separate table + M:M） | 同一キーワードを複数 Knowledge で共有し、将来の集計に備える |
| PostgreSQL を本番 DB として採用（Railway） | スケーラビリティ確保、pgvector 対応 |
| SQLite をローカル開発 DB として継続使用 | セットアップ不要、テストでも使用 |

---

## Future Extensions (Post-MVP)

- **KnowledgeRelation テーブル**: Knowledge 間の関連（関連概念・前提知識等）を管理（Phase 23）
