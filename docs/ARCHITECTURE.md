# ARCHITECTURE.md — ボトルネック分析レポート アーキテクチャ

> 最終更新: 2026-04-07（テンプレートリファクタリング + 週期間変更）

---

## 1. ディレクトリ構成

```
v2-veltra-cvr/
├── ドキュメント（ルート）
│   ├── CLAUDE.md                    AI セッション設定（Claude Code 自動読込）
│   └── README.md                    プロジェクト概要（GitHub表示）
│
├── docs/                            プロジェクトドキュメント
│   ├── ARCHITECTURE.md              ← このファイル（技術構成）
│   ├── playbook.md                  週次レポート運用マニュアル
│   ├── veltra-design-system.md      VELTRA デザインルール
│   ├── veltra-url-structure.md      VELTRA URL階層（エリア定義）
│   └── prd-template.md              PRDテンプレート（汎用）
│
├── 共通アセット（ルート）
│   ├── auth.js                      Google OAuth 認証
│   ├── nav.js                       サイドナビゲーション（全ページ共通）
│   ├── funnel-def.js                ファネル定義（ステップ名・イベント名）
│   ├── bottleneck.css               ボトルネック分析ページのCSS
│   ├── bottleneck.js                アコーディオン等のUI操作JS
│   └── bottleneck.html              ボトルネック分析テンプレート（動的描画）
│
├── ページ
│   ├── index.html                   ダッシュボード（トップページ）
│   ├── login.html                   ログインページ
│   ├── cycle.html                   CVR改善サイクル説明
│   └── analysis.html                分析ガイド
│
├── データ（ルート）
│   ├── reports-index.json           全週のインデックス（週ID・日付・パス）
│   ├── weekly-summary.json          週次サマリーデータ
│   ├── summary-data.json            ダッシュボード用サマリー
│   └── archive-meta.json            アーカイブメタデータ
│
├── reports/                         週次レポート格納
│   ├── index.html                   アーカイブ一覧ページ
│   ├── 2026-w13/
│   │   └── data.json                GA4分析データ
│   └── 2026-w14/
│       ├── index.html               週次サマリーページ
│       ├── data.json                GA4分析データ
│       └── bottleneck-{1-10}-content.json   ボトルネック分析コンテンツ
│
├── scripts/                         スクリプト
│   ├── generate-week.py             週次スキャフォールド生成
│   ├── validate-report.py           レポートバリデーション
│   ├── extract-content-from-html.py content.json スケルトン生成ユーティリティ
│   └── archive/                     過去の一時スクリプト
│
└── releasenote/                     VELTRAリリースノート（CSV）
```

---

## 2. ページ生成アーキテクチャ

### 2.1 ボトルネック分析ページ（動的テンプレート方式）

```
┌─────────────────────┐     fetch      ┌──────────────────────────────┐
│  /bottleneck.html   │ ──────────────→│ /reports/{week}/             │
│  （1テンプレート）    │                │   bottleneck-{N}-content.json│
│  URL: ?week=...&num=│                │   data.json (meta)           │
└─────────────────────┘                └──────────────────────────────┘
         │
         │ JS で DOM 構築
         ▼
┌─────────────────────┐
│  描画されたページ     │
│  CSS: /bottleneck.css│
│  JS:  /bottleneck.js │
│       /nav.js        │
│       /funnel-def.js │
└─────────────────────┘
```

**URL形式**: `/bottleneck.html?week=2026-w14&num=4`

- `week`: 週ID（例: `2026-w14`）
- `num`: ボトルネック番号（1〜10）
- テンプレートが `fetch()` で content.json と data.json を取得し、JS で DOM を構築
- ビルドステップ不要（Pythonスクリプトでの静的HTML生成は廃止）

### 2.2 その他のページ（静的HTML）

| ページ | ファイル | 説明 |
|--------|----------|------|
| ダッシュボード | `/index.html` | summary-data.json を読み込み表示 |
| 週次サマリー | `/reports/{week}/index.html` | data.json を読み込み表示 |
| アーカイブ | `/reports/index.html` | reports-index.json を読み込み表示 |
| CVR改善サイクル | `/cycle.html` | 静的コンテンツ |
| 分析ガイド | `/analysis.html` | 静的コンテンツ |

---

## 3. データフロー

### 3.1 週次レポート生成フロー

```
① generate-week.py --week 2026-w15
   │
   ├── reports/2026-w15/ ディレクトリ作成
   ├── reports/2026-w15/data.json（meta スケルトン）
   ├── reports/2026-w15/index.html（週次サマリー）
   └── reports-index.json 更新
   │
② GA4 MCP でデータ取得 → data.json に Q1-Q10 の結果を格納
   │
③ ボトルネック分析 → bottleneck-{1-10}-content.json を作成
   │
④ validate-report.py --week 2026-w15 で検証
   │
⑤ git push → Vercel 自動デプロイ
```

### 3.2 データファイル一覧

| ファイル | スコープ | 内容 |
|----------|----------|------|
| `data.json` | 週単位 | GA4分析データ（meta, baseline, funnel_7d, segments, bottlenecks） |
| `bottleneck-{N}-content.json` | ページ単位 | 仮説・施策・競合比較・検証チェックリスト |
| `reports-index.json` | 全体 | 全週のインデックス（週ID, 日付範囲, パス） |
| `weekly-summary.json` | 全体 | 週次サマリー（KPI推移） |
| `summary-data.json` | 全体 | ダッシュボード用集約データ |

---

## 4. content.json スキーマ

`bottleneck-{N}-content.json` の構造:

```jsonc
{
  "number": 1,                    // ボトルネック番号（1-10）
  "title": "Organic Search × Mobile — ③→④ 意向転換率の低さ",
  "tags": [
    {"label": "③→④ 検討→意向", "type": "red"},   // type: "red" | "default"
    {"label": "Organic Search", "type": "default"}
  ],
  "deviation": "-42%",            // 全体平均との乖離率
  "impact_sessions": "923K / 月", // 影響セッション数
  "description_html": "...",      // 説明文（HTML可）

  // ファネル全体比較（オプション）
  "funnel_overview": {
    "title": "ファネル全体比較（...）",
    "cells": [
      {"label": "①→② ...", "value": "22.04%", "sub": "ベースライン 26.10%", "alert": false}
    ]
  },

  // Tier 1 比較（4セル）
  "funnel_compare": [
    {"label": "全体平均", "stage": "③→④ 意向転換", "value": "86.62%", "sub": "ベースライン", "alert": false}
  ],

  // 深掘り分析（2カード）
  "drill_down": [
    {"title": "...", "body_html": "...", "note": "..."}
  ],

  // 特定結果コールアウト
  "callout": {"title": "特定結果", "body_html": "..."},

  // 仮説セクション（カスタムタイトル）
  "hypo_section_title": "原因仮説 × 3 &amp; 打ち手 × 9",
  "hypo_section_desc": "...",

  // 仮説 × 3（各仮説に施策 × 3 = 計9施策）
  "hypotheses": [
    {
      "level": "h1",              // h1（有力）/ h2 / h3
      "level_label": "仮説 1（有力）",
      "title": "...",
      "body": "...",
      "evidence": ["裏付け1", "裏付け2"],
      "actions": [
        {
          "letter": "A",          // A-I（9施策）
          "title": "...",
          "description": "...",
          "spec_html": "...",     // 開発仕様（HTML可）
          "impact": "③→④ +6pt",
          "prototype": {          // オプション
            "before_html": "<div>...</div>",
            "after_html": "<div>...</div>"
          }
        }
      ]
    }
  ],

  // 検証方法コールアウト
  "verification_method": "...",

  // 競合比較（6社）
  "competitive": [
    {
      "name": "Klook",
      "favicon_url": "https://...",
      "url": "https://...",
      "feature": "...",
      "detail": "..."
    }
  ],
  "competitive_insight": "...",   // 競合比較から得られる示唆

  // チームレビューチェックリスト
  "verification": ["確認項目1", "確認項目2"]
}
```

---

## 5. 週期間ルール

| 項目 | ルール |
|------|--------|
| 週の開始日 | **日曜日**（ISO週の月曜 - 1日） |
| 週の終了日 | **土曜日**（ISO週の月曜 + 5日） |
| 週ID | ISO週番号を使用（例: `2026-w14`） |
| ローリング期間 | 28日間（date_end - 27日 〜 date_end） |
| 生成タイミング | 毎週月曜 AM 4:00 JST（土曜データを1日寝かせて確定） |

**例（W15, 生成日 4/13 月曜）:**

| 期間 | 算出方法 | 値 |
|------|----------|-----|
| `date_start` | ISO週の月曜 - 1日 = 日曜 | `2026-04-05` |
| `date_end` | ISO週の月曜 + 5日 = 土曜 | `2026-04-11` |
| `rolling_start` | date_end - 27日 | `2026-03-15` |
| `rolling_end` | date_end | `2026-04-11` |

---

## 6. ナビゲーション（nav.js）

全ページに `nav.js` を読み込むことでサイドナビが自動構築される。

- **データソース**: `/reports-index.json` → 各週の `data.json` を fetch
- **ページ種別検出**: URLパスとクエリパラメータで判定
  - ボトルネック: `/bottleneck.html?week=...&num=...`
  - 週次サマリー: `/reports/2026-w14/`
  - トップ: `/`
- **リンク形式**: `/bottleneck.html?week={week_id}&num={rank}`

---

## 7. デプロイ

| 項目 | 値 |
|------|-----|
| ホスティング | Vercel |
| デプロイトリガー | `main` ブランチへの push |
| ビルドステップ | なし（静的ファイル配信） |
| URL | https://v2-veltra-cvr.vercel.app/ |

---

## 8. リファクタリング履歴

### 2026-04-07: テンプレートリファクタリング

**Before（旧アーキテクチャ）:**
```
content.json × 10
    ↓ generate-bottleneck.py（Python テンプレートエンジン）
静的 HTML × 10（各700〜1,300行、CSS/JS インライン）
```

**After（新アーキテクチャ）:**
```
content.json × 10
    ↓ bottleneck.html が JS で fetch & DOM 構築（ビルド不要）
1テンプレート × 動的描画
```

**変更理由:**
1. 静的HTML × 10 は CSS/JS が全ファイルに重複（66行CSS + 35行JS × 10）
2. AI生成時に700〜1,300行のフルHTMLを出力 → トークン消費大、タイムアウト頻発
3. デザイン変更時に全10ファイルを手動修正する必要があった
4. content.json だけ作成すれば自動的にページが描画される方が運用効率が高い

**削除されたファイル:**
- `reports/2026-w14/bottleneck-{1-10}.html`（静的HTML × 10）
- `scripts/generate-bottleneck.py`（静的HTML生成スクリプト）

**追加されたファイル:**
- `/bottleneck.html`（動的テンプレート）
- `/bottleneck.css`（共通CSS、インラインから抽出）
- `/bottleneck.js`（共通JS、インラインから抽出）

### 2026-04-07: 週期間変更（月〜日 → 日〜土）

- `scripts/generate-week.py`: `calc_week_meta()` を日〜土に変更
- `scripts/validate-report.py`: バリデーション条件を日曜始まりに更新
- `docs/playbook.md`: 日付範囲テーブルを更新
