# v2-veltra-cvr

VELTRA CVR改善プロジェクトの週次ボトルネック分析レポート。

- **ダッシュボード**: https://v2-veltra-cvr.vercel.app/
- **運用マニュアル**: [docs/playbook.md](docs/playbook.md) — 週次レポート生成手順・品質チェックリスト
- **技術構成**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — スキーマ・データフロー・デプロイ
- **デザインルール**: [docs/veltra-design-system.md](docs/veltra-design-system.md) — VELTRAサイトのUI仕様
- **AI セッション設定**: [CLAUDE.md](CLAUDE.md) — GA4 MCP接続・クエリパターン

## 技術スタック

- 静的HTML + Vanilla JS（ビルド不要）
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
