# v2-veltra-cvr

**UX Design Squad ｜ Northstar** — Squad の指針・プロジェクト管理・CVR分析のポータル。

- `/`（Northstar hub）から 2026 H2（Mission & 管理ボード）と 2026 H1（CVR Report 群）へ振り分け。
- ドメイン変更（プロジェクト名／カスタムドメイン）は Vercel ダッシュボード側で実施する（リポジトリからは不可）。

- **ポータル**: https://v2-veltra-cvr.vercel.app/
- **H2 Mission & 管理ボード**: `/2026h2/`（ファイル実体は `2026h2/index.html`）
- **H1 入口（CVR サマリー）**: `/2026h1/`（実体 `2026h1/index.html`）／ **KPI**: `/2026h1/kpi.html` ／ **週次レポート**: `/2026h1/reports/`
- H1（これまでの CVR レポート・分析・施策ページ）は `2026h1/` 配下、H2 は `2026h2/` 配下。振り分けは `/`（index.html）。
- **アクセス制御**: [docs/ACCESS.md](docs/ACCESS.md) — パスコードゲートの仕組み・環境変数・共有リンクの配り方
- **運用マニュアル**: [docs/playbook.md](docs/playbook.md) — 週次レポート生成手順・品質チェックリスト
- **技術構成**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — スキーマ・データフロー・デプロイ
- **デザインルール**: [docs/veltra-design-system.md](docs/veltra-design-system.md) — VELTRAサイトのUI仕様
- **AI セッション設定**: [CLAUDE.md](CLAUDE.md) — GA4 MCP接続・クエリパターン

## 技術スタック

- 静的HTML + Vanilla JS（ビルド不要）
- アクセス制御: `middleware.js`（Vercel Edge Middleware）が全パスをパスコードで保護。環境変数 `ACCESS_PASSCODE` / `ACCESS_SECRET` が必須（→ [docs/ACCESS.md](docs/ACCESS.md)）
- ボトルネック分析: `/bottleneck.html` が `bottleneck-{N}-content.json` を動的に描画
- Vercel（main push → 自動デプロイ）
- GA4 MCP でデータ取得 → Claude で分析 → content.json 生成

## 週次サイクル

```
毎週月曜 AM 4:00 JST（土曜データを1日寝かせて確定）
  Phase 1 (Sonnet): scripts/generate-week.py → GA4 クエリ → data.json
  Phase 2 (Opus):   ボトルネック分析 → bottleneck-{1-10}-content.json 生成
  Phase 3 (Sonnet): git push → Vercel デプロイ
```

詳細は [docs/playbook.md](docs/playbook.md) を参照。

## ドキュメント構成

| ファイル | 役割 | 対象読者 |
|---------|------|---------|
| `CLAUDE.md` | AIセッション設定（GA4 MCP接続） | Claude Code |
| `docs/playbook.md` | 週次運用マニュアル（手順・チェックリスト） | 運用者 |
| `docs/ARCHITECTURE.md` | 技術仕様（スキーマ・UI・デプロイ） | 開発者 |
| `docs/veltra-design-system.md` | VELTRAサイトのデザインルール | プロトタイプ作成時 |
| `docs/veltra-url-structure.md` | VELTRA URL階層・エリア定義 | GA4クエリ設計時 |
| `docs/prd-template.md` | PRDテンプレート（汎用） | 施策提案時 |
