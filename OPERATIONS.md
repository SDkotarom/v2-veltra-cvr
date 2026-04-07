# 週次レポート運用マニュアル（内部用）

> **対象**: 運用担当者（自分用メモ）
> **更新**: 2026年4月

---

## 1. アカウント構成

| 名称 | 用途 | モデル | 制約 |
|------|------|--------|------|
| **アカウントA**（ベルトラ） | GA4 MCP 接続、データ取得 | Sonnet | GA4 MCP に直接接続可 |
| **アカウントB**（分析） | 分析、HTML生成、デプロイ | Opus / Sonnet 切替 | GA4 MCP 接続不可 |

**使い分けの理由**: GA4 MCP はアカウントAからのみ接続可能。分析・生成はアカウントBの方がモデル切替（Opus/Sonnet）が柔軟。

---

## 2. 週次サイクル（毎週日曜）

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: データ取得                    アカウントA (Sonnet)  │
│  ─────────────────────────────────────────────────────────  │
│  1. 新セッション開始                                         │
│  2. 「PLAYBOOK.md を読んで W{XX} のデータを取得して」         │
│  3. GA4 クエリ Q1〜Q10 実行                                  │
│  4. data.json / summary-data.json / weekly-summary.json 更新 │
│  5. git push to main                                         │
│                          ↓                                   │
│  Phase 2: 分析 & HTML生成               アカウントB (Opus)   │
│  ─────────────────────────────────────────────────────────  │
│  1. git pull で最新データ取得                                 │
│  2. 「PLAYBOOK.md を読んで W{XX} の分析とHTML生成をして」     │
│  3. ボトルネック10件分析 → HTML生成                           │
│  4. git push to main → Vercel 自動デプロイ                   │
│                          ↓                                   │
│  Phase 3: 確認                          ブラウザ             │
│  ─────────────────────────────────────────────────────────  │
│  1. https://v2-veltra-cvr.vercel.app/ を確認                 │
│  2. 数値の整合性、用語統一、デザインをチェック                │
│  3. 修正があればアカウントBで対応                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. ファイル更新マトリクス

### 毎週更新するファイル

| ファイル | 更新者 | Phase | 内容 |
|----------|--------|-------|------|
| `reports/{W}/data.json` | A | 1 | GA4 全クエリ結果 |
| `summary-data.json` | A | 1 | 月次KPI追記 |
| `weekly-summary.json` | A | 1 | 週次KPI追記 |
| `reports-index.json` | A | 1 | 新しい週のエントリ追加 |
| `archive-meta.json` | A | 1 | updatedAt タイムスタンプ |
| `reports/{W}/index.html` | B | 2 | 週次サマリーページ |
| `reports/{W}/bottleneck-{1-10}.html` | B | 2 | ボトルネック詳細ページ |

### 変更時のみ更新するファイル

| ファイル | 更新者 | トリガー |
|----------|--------|---------|
| `PLAYBOOK.md` | B | 運用プロセス変更時 |
| `veltra-design-system.md` | B | VELTRAサイトのデザイン変更時 |
| `veltra-url-structure.md` | B | VELTRAのURL構造変更時 |
| `index.html` | B | ダッシュボードUI改善時 |
| `nav.js` | B | ナビゲーション構造変更時 |
| `funnel-def.js` | B | ファネル定義変更時 |
| `scripts/generate-week.py` | B | スキャフォールド処理変更時 |

### 触らないファイル

| ファイル | 理由 |
|----------|------|
| `auth.js` | 認証ロジック確定済み |
| `login.html` | ログインUI確定済み |
| `.gitignore` | 設定済み |

---

## 4. 各アカウントへの指示テンプレート

### アカウントA（Phase 1）

```
PLAYBOOK.md を読んでください。
W{XX}（{日付範囲}）のデータを取得してください。
Phase 1 の手順に従い、Q1〜Q10 を実行して data.json を生成し、
summary-data.json と weekly-summary.json も更新して push してください。
```

### アカウントB（Phase 2）

```
PLAYBOOK.md を読んでください。
git pull して最新の data.json を取得してください。
W{XX} の Phase 2 を実行してください。
ボトルネック10件の分析 → HTML生成 → デプロイまでお願いします。
```

### アカウントB（修正対応）

```
PLAYBOOK.md を読んでください。
https://v2-veltra-cvr.vercel.app/reports/{YYYY}-w{WW}/ を確認して、
{具体的な修正内容} を対応してください。
```

---

## 5. モデル使い分け

### アカウントB での切替タイミング

| 作業 | モデル | 切替コマンド |
|------|--------|-------------|
| 分析開始（ボトルネック特定、仮説生成） | **Opus** | `/model claude-opus-4-6` |
| HTML テンプレート生成 | **Sonnet** | `/model claude-sonnet-4-6` |
| CSS / レイアウト微調整 | **Sonnet** | — |
| プロトタイプ設計 | **Opus** | `/model claude-opus-4-6` |
| 競合比較分析 | **Opus** | — |
| git 操作、デプロイ | **Sonnet** | `/model claude-sonnet-4-6` |

**原則**: 判断・創造性が必要 → Opus、定型作業 → Sonnet

---

## 6. トラブルシューティング

| 問題 | 原因 | 対処 |
|------|------|------|
| アカウントAのリミット | API制限 | 数時間待って再試行 |
| GA4 MCP 接続エラー | Proxy制限 | アカウントAのセッションを再起動 |
| git push rejected | リモートに先行コミット | `git pull --rebase` → push |
| Vercel デプロイ失敗 | HTML構文エラー | ブラウザコンソールで確認、修正して再push |
| 数値不整合 | data.json とHTML内ハードコードの乖離 | data.json を正とし、HTMLを修正 |
| 「仮想データ」表記残り | 古いHTML | grep で検索、置換 |

---

## 7. リポジトリ構成（最新）

```
v2-veltra-cvr/
├── PLAYBOOK.md                 ← 運用マニュアル（公開用）
├── OPERATIONS.md               ← このファイル（内部用）
├── veltra-design-system.md     ← デザインルール
├── veltra-url-structure.md     ← URL構造
├── prd-template.md             ← PRDテンプレート
├── scripts/generate-week.py    ← 週次スキャフォールド
├── auth.js / nav.js / funnel-def.js  ← 共通JS
├── index.html                  ← ダッシュボード
├── cycle.html                  ← 分析プロセス説明ページ
├── login.html                  ← ログイン
├── summary-data.json           ← 月次KPI
├── weekly-summary.json         ← 週次KPI
├── reports-index.json          ← レポート一覧
├── archive-meta.json           ← 最終更新時刻
└── reports/2026-w14/           ← 週次レポート
    ├── data.json
    ├── index.html
    └── bottleneck-{1-10}.html
```

---

*内部運用メモ / 2026年4月作成*
