# CLAUDE.md — このプロジェクトでのAIアシスタント設定

> **新しいセッション開始時に必ずこのファイルを読むこと。**
> 運用マニュアル全体は `playbook.md` を参照。

---

## GA4 MCP 接続について

このプロジェクトでは **GA4 MCP ツールが自動的に利用可能**です。

**セッション開始時の手順（必須）:**

```
ToolSearch で "run_report" を検索 → mcp__*__run_report ツールを取得
```

- 認証情報（サービスアカウントJSON、gcloud ADC、API Key）は**不要**
- Python SDK、curl、gcloud コマンドは**使わない**
- MCP ツール名は `mcp__<UUID>__run_report` 形式（UUIDはセッションごとに変わる場合がある）

**正しい呼び出し例:**

```json
{
  "property_id": "347074845",
  "date_ranges": [{"start_date": "2026-03-09", "end_date": "2026-04-05"}],
  "dimensions": [],
  "metrics": ["sessions", "activeUsers"]
}
```

**よくある失敗パターン（やってはいけないこと）:**

- `python3 -c "from google.analytics.data_v1beta import ..."` → SDK未認証でエラー
- `gcloud auth application-default login` → gcloudは未インストール
- 「認証情報を貼り付けてください」とユーザーに聞く → 不要、MCPで直接接続可能

---

## 基本情報

- **GA4 Property ID**: `347074845`
- **Vercel URL**: https://v2-veltra-cvr.vercel.app/
- **開発ブランチ規則**: `claude/<task>-<hash>` 形式で作業し、完了後 push

---

## よく使うクエリパターン

### ベースラインファネル（28日間）
```python
# dimensions=[], metrics=["sessions","activeUsers","purchaseRevenue"]
# dimension_filter で pagePath/eventName を切り替えて各ステップ取得
```

### エリア別（landingPage ディメンション）
```python
# dimensions=["landingPage"], limit=10000
# Python で area_key に集計後 data.json に格納
```

詳細な手順は `playbook.md` のセクション4「Phase 1: データ取得」を参照。
