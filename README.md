# v2-veltra-cvr

VELTRA CVR改善プロジェクトの週次ボトルネック分析レポート。

- **ダッシュボード**: https://v2-veltra-cvr.vercel.app/
- **運用マニュアル**: [playbook.md](playbook.md)
- **技術構成**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **デザインルール**: [docs/veltra-design-system.md](docs/veltra-design-system.md)

## 技術スタック

- 静的HTML + Vanilla JS（ビルド不要）
- ボトルネック分析: `/bottleneck.html` が `content.json` を動的に描画（静的HTML生成なし）
- Vercel（main push → 自動デプロイ）
- GA4 MCP でデータ取得 → Claude で分析 → content.json 生成

## 週次サイクル

```
毎週月曜 AM 4:00 JST（土曜データを1日寝かせて確定）
  Phase 1 (Sonnet): scripts/generate-week.py → GA4 クエリ → data.json
  Phase 2 (Opus):   ボトルネック分析 → bottleneck-{1-10}-content.json 生成
  Phase 3 (Sonnet): git push → Vercel デプロイ
```

詳細は [playbook.md](playbook.md) を参照。
