# Personal Knowledge Voice Assistant

AIと普通に会話しているだけで、自分専用の知識体系が育つ。

日常で生じた疑問をAIと自然に音声会話するだけで、それが自分の知識として蓄積され、後から再利用できる Personal Knowledge Assistant。

---

## Requirements

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv)（Python パッケージマネージャー）
- Flutter SDK >= 3.1.5（Dart >= 3.1.5）
- Android SDK（実機または Android エミュレーター）

---

## Environment Variables

`.env.example` を `.env` にコピーして編集する:

```powershell
# PowerShell
Copy-Item backend\.env.example backend\.env
```

```bash
# bash / Git Bash
cp backend/.env.example backend/.env
```

`.env` を編集して以下を設定する:

| 変数 | 説明 | デフォルト |
|------|------|-----------|
| `DATABASE_URL` | SQLite ファイルパス | `sqlite:///./app.db` |
| `OPENAI_API_KEY` | OpenAI API キー（必須） | — |

> `.env` は `.gitignore` で除外済み。Git に追加しないこと。

---

## Backend

### セットアップ

```bash
cd backend

# 依存パッケージインストール
uv sync

# Database migration 適用
uv run alembic upgrade head
```

### 起動

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

起動確認:

```powershell
# PowerShell
Invoke-RestMethod http://localhost:8000/health
# status : ok
```

```bash
# bash / Git Bash
curl http://localhost:8000/health
# {"status":"ok"}
```

---

## Flutter

### baseUrl の設定

[frontend/lib/services/api_client.dart](frontend/lib/services/api_client.dart) の `baseUrl` を環境に合わせて変更する:

```dart
// エミュレーター使用時
static const String baseUrl = 'http://10.0.2.2:8000';

// 実機使用時（PC の LAN IP に合わせる）
static const String baseUrl = 'http://192.168.x.x:8000';
```

PC の LAN IP は `ipconfig`（Windows）または `ifconfig`（Mac/Linux）で確認する。

### セットアップ・起動

```bash
cd frontend

# パッケージ取得
flutter pub get

# 接続済みデバイスまたはエミュレーターで実行
flutter run
```

---

## Database Migration

```bash
cd backend

# migration 適用
uv run alembic upgrade head

# 現在のリビジョン確認
uv run alembic current

# 新しい migration 作成（開発時）
uv run alembic revision --autogenerate -m "description"
```

---

## Architecture

- Frontend: Flutter (Android)
- Backend: Python / FastAPI
- Database: SQLite (MVP)
- Voice AI: OpenAI Realtime API / WebRTC

詳細は [docs/architecture.md](docs/architecture.md) を参照。
