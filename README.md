# v2-veltra-cvr

VELTRA CVR改善プロジェクトの週次ボトルネック分析レポート。

- **ダッシュボード**: https://v2-veltra-cvr.vercel.app/
- **運用マニュアル**: [playbook.md](playbook.md)
- **デザインルール**: [veltra-design-system.md](veltra-design-system.md)

## 技術スタック

- 静的HTML + Vanilla JS（ビルド不要）
- Vercel（main push → 自動デプロイ）
- GA4 MCP でデータ取得 → Claude で分析 → HTML生成

## 週次サイクル

```
日曜 AM 4:00 JST
  Phase 1 (Sonnet): scripts/generate-week.py → GA4 クエリ → data.json
  Phase 2 (Opus):   ボトルネック分析 → HTML生成
  Phase 3 (Sonnet): git push → Vercel デプロイ
```

詳細は [playbook.md](playbook.md) を参照。
