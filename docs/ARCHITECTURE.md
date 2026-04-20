# ARCHITECTURE.md — ボトルネック分析レポート アーキテクチャ

> 最終更新: 2026-04-20（ボトルネック分析進捗バー追加: data.json.progress）

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
│   ├── report.html                  週次サマリーテンプレート（動的描画）★NEW
│   ├── report.css                   週次サマリーCSS
│   ├── bottleneck.html              ボトルネック分析テンプレート（動的描画）
│   ├── bottleneck.css               ボトルネック分析ページのCSS
│   └── bottleneck.js                アコーディオン等のUI操作JS
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
│   ├── archive-meta.json            アーカイブメタデータ
│   ├── known-implementations.json   実装済み機能カタログ（重複チェック用）★NEW
│   └── feasibility-constraints.json 制約チェックリスト定義★NEW
│
├── reports/                         週次レポート格納
│   ├── index.html                   アーカイブ一覧ページ
│   └── {YYYY}-w{WW}/                週別ディレクトリ（例: 2026-w13 〜 2026-w16）
│       ├── index.html               リダイレクト → /report.html?week={YYYY}-w{WW}
│       ├── data.json                GA4分析データ（+bottleneck summary +progress）
│       └── bottleneck-{1-10}-content.json   ボトルネック分析コンテンツ
│
├── scripts/                         スクリプト
│   ├── generate-week.py             週次スキャフォールド生成 + content.json スケルトン生成
│   ├── validate-report.py           レポートバリデーション
│   ├── extract-content-from-html.py content.json スケルトン生成ユーティリティ
│   └── archive/                     過去の一時スクリプト
│
└── releasenote/                     VELTRAリリースノート（CSV）
```

---

## 2. ページ生成アーキテクチャ（動的テンプレート方式）

すべてのレポートページは **1テンプレート + N個のJSONデータ** 構成。
静的HTMLの生成は不要。JSONデータさえ作れば自動的にページが描画される。

### 2.1 週次サマリーページ

```
┌─────────────────────┐     fetch      ┌──────────────────────────────┐
│  /report.html       │ ──────────────→│ /reports/{week}/data.json    │
│  URL: ?week=2026-w14│                └──────────────────────────────┘
│  CSS: /report.css   │
└─────────────────────┘
```

**URL形式**: `/report.html?week=2026-w14`（または `/reports/2026-w14/` → リダイレクト）

- `data.json` からファネル転換率、WoW変化、KPI、ボトルネックリストを描画
- トピック（改善/悪化）は WoW データから自動生成
- 各週の `index.html` はリダイレクトのみ（`generate-week.py` で自動生成）

### 2.2 ボトルネック分析ページ

```
┌─────────────────────┐     fetch      ┌──────────────────────────────┐
│  /bottleneck.html   │ ──────────────→│ /reports/{week}/             │
│  URL: ?week=...&num=│                │   bottleneck-{N}-content.json│
│  CSS: /bottleneck.css│               │   data.json (meta)           │
└─────────────────────┘                └──────────────────────────────┘
```

**URL形式**: `/bottleneck.html?week=2026-w14&num=4`

- テンプレートが `fetch()` で content.json と data.json を取得し、JS で DOM を構築
- ビルドステップ不要

### 2.3 その他のページ（静的HTML）

| ページ | ファイル | 説明 |
|--------|----------|------|
| ダッシュボード | `/index.html` | summary-data.json を読み込み表示 |
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
   ├── reports/2026-w15/index.html（リダイレクト）
   └── reports-index.json 更新
   │
② GA4 MCP でデータ取得 → data.json に Q1-Q10 の結果を格納
   │
③ generate-week.py --skeleton --week 2026-w15
   │  └── bottleneck-{1-10}-content.json スケルトン自動生成（~77%の記述を自動化）
   │
④ Claude が各スケルトンの TODO: を埋める（2-3ファイルずつ並列推奨）
   │
⑤ validate-report.py --week 2026-w15 で検証
   │
⑥ git push → Vercel 自動デプロイ
```

### 3.2 データファイル一覧

| ファイル | スコープ | 内容 |
|----------|----------|------|
| `data.json` | 週単位 | GA4分析データ（meta, baseline, funnel_7d, segments, bottlenecks, progress） |
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

  // 分析軸 比較（4セル）
  "funnel_compare": [
    {"label": "全体平均", "stage": "③→④ 意向転換", "value": "86.62%", "sub": "ベースライン", "alert": false}
  ],

  // 掛け合わせ深掘り（2カード）
  "drill_down": [
    {"title": "...", "body_html": "...", "note": "..."}
  ],

  // 特定結果コールアウト
  "callout": {"title": "特定結果", "body_html": "..."},

  // 行動仮説レイヤー（ボトルネック → 仮説の橋渡し）
  "behavior_context": {
    "estimated_action": "ユーザーの推定行動（1文）",       // required
    "evidence": [                                          // required, 2-4件
      "裏付けデータ1（数値引用）",
      "裏付けデータ2"
    ],
    "page_role_check": "戦略ガイドのページ役割との照合",    // required
    "subtraction_check": "引き算で解決できるかのチェック",   // required
    "pattern_references": [                                // optional, 0-3件
      "✅ 勝ちパターン名 +X%",
      "❌ 負けパターン名"
    ]
  },

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
          "prototype": {          // オプション（2形式から選択）
            // 形式1: フルHTML（リッチなモックアップ）
            "before_html": "<div>...</div>",
            "after_html": "<div>...</div>",
            // 形式2: テキスト短縮形（トークン節約、bottleneck.html が自動ラップ）
            "before_text": "テキストリスト表示、カード型UIなし",
            "after_text": "写真+評価+価格のカード型UI、タップでAC直遷移"
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

### 4.1 action フィールド拡張（施策化レビューレイヤー）

各 `action` オブジェクトに以下のフィールドを追加。施策化前のレビュー工数を削減し、そのまま施策化できる品質を目指す。

```jsonc
{
  "letter": "A",
  "title": "...",
  "description": "...",
  "spec_html": "...",
  "impact": "③→④ +6pt",
  "prototype": { ... },

  // ── 施策化レビューレイヤー（Phase 2 で Claude が記入） ──

  // 実装済み機能との重複チェック
  "implementation_check": {
    "status": "new",           // "new" | "partial" | "already_exists" | "superseded"
    "matched_feature": null,   // 重複する既存機能名（なければ null）
    "note": null               // 差分の説明（partial の場合: 何が未実装か）
  },

  // 実現可能性レビュー
  "feasibility": {
    "effort": "S",             // "S" | "M" | "L" | "XL"（feasibility-constraints.json 参照）
    "constraints": [],         // 該当する制約ID（例: ["inventory_realtime", "partner_api_dependency"]）
    "constraint_notes": "",    // 制約の具体的影響と回避策（1-2文）
    "prerequisites": [],       // 前提条件（例: ["Globick API v3.1の在庫フィールド確認"]）
    "quick_wins": true         // フロントのみで即実装可能か（effort "S" かつ constraints 空なら true）
  }
}
```

**status の定義**:

| status | 意味 | 施策化可否 |
|--------|------|-----------|
| `new` | 未実装。新規施策として有効 | ✅ そのまま施策化 |
| `partial` | 類似機能が存在するが、この施策の核心部分は未実装 | ✅ 差分を明記して施策化 |
| `already_exists` | 既に実装済み。施策としては不要 | ❌ 除外 |
| `superseded` | より良い代替が既に実装されている | ❌ 除外 |

**effort の定義**:

| effort | 内容 | 目安期間 |
|--------|------|---------|
| `S` | フロントエンド CSS/JS のみ | 1-2週間 |
| `M` | フロントエンド＋既存APIの活用 | 2-4週間 |
| `L` | バックエンドAPI新設またはパートナーAPI連携 | 1-3ヶ月 |
| `XL` | データ基盤改修・インフラ変更 | 3ヶ月以上 |

**参照ファイル**:
- `known-implementations.json`: 実装済み機能カタログ（重複チェック用）
- `feasibility-constraints.json`: 制約チェックリスト定義

### 4.2 behavior_context フィールド定義

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `estimated_action` | string | ✅ | ユーザーの推定行動。1文、断定せず推量表現 |
| `evidence` | string[] | ✅ (2-4件) | 推定を裏付けるデータパターン。GA4数値を引用 |
| `page_role_check` | string | ✅ | 戦略ガイドSection 3のページ役割定義との照合 |
| `subtraction_check` | string | ✅ | 情報の引き算で改善可能かのチェック結果 |
| `pattern_references` | string[] | — (0-3件) | 2025年ABテスト勝ち/負けパターン。✅/❌ 付き |

**配置**: `callout` と `hypo_section_title` の間。青色ボーダーカードで描画。

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

### 2026-04-08: content.json スケルトン自動生成

**施策**: `generate-week.py --skeleton` で bottleneck content.json の雛形を自動生成

**効果**:
- Claude が書く量を **約77%削減**（300K chars → 69K chars / 10ファイル）
- `before_text/after_text` 短縮形式でプロトタイプ記述を **91%削減**
- 機械的フィールド（tags, deviation, impact_sessions, funnel_overview, funnel_compare, competitive骨格, verification骨格）を data.json から自動投入
- Claude は仮説・施策テキスト・プロトタイプ説明の **分析部分のみ** に集中

**自動生成されるフィールド**:
- `number`, `title`, `tags`, `deviation`, `impact_sessions`
- `funnel_overview`（セグメントのレート vs ベースライン）
- `funnel_compare`（同カテゴリ関連セグメント比較）
- `hypotheses` 構造（3仮説 × 3施策のテンプレート）
- `competitive`（6社テンプレート）
- `verification`（チェックリストテンプレート）

### 2026-04-13: 施策化レビューレイヤー追加

**施策**: 打ち手の施策化率を向上させるため、各 action に `implementation_check` と `feasibility` フィールドを追加。

**背景**:
1. 打ち手にVELTRA既存機能と重複する提案が含まれ、レビュー時に弾かれていた
2. 実務上の制約（在庫API、為替、パートナーAPI依存等）の考慮が不足し、施策化前の再考慮コストが高かった

**追加ファイル**:
- `known-implementations.json`: annotations.json + リリースノートから抽出した実装済み機能カタログ
- `feasibility-constraints.json`: 10カテゴリの制約チェックリスト（在庫、為替、時差、パーソナライズ、API依存等）
- `scripts/audit-actions.py`: 既存打ち手と実装済み機能のクロスチェックスクリプト

**スキーマ変更**:
- `action.implementation_check`: 重複ステータス（new/partial/already_exists/superseded）
- `action.feasibility`: 工数・制約・前提条件・クイックウィン判定

**効果**:
- Phase 2 でClaude が `known-implementations.json` を参照して重複を自動排除
- 各施策に制約と回避策が事前記載され、レビュアーの判断コスト削減
- `quick_wins: true` フィルターで即実装可能な施策を一覧化可能

### 2026-04-07: 週期間変更（月〜日 → 日〜土）

- `scripts/generate-week.py`: `calc_week_meta()` を日〜土に変更
- `scripts/validate-report.py`: バリデーション条件を日曜始まりに更新
- `docs/playbook.md`: 日付範囲テーブルを更新

### 2026-04-20: ボトルネック分析進捗バー追加 & pct 変数衝突修正

**施策**: `report.html` にボトルネック分析の進捗可視化UIを追加。

**追加内容**:
- プログレスバー + 「N/10 件完了（X%）」表示
- 各ボトルネック行に状態バッジ（○未着手 / ◔分析完了 / ◑打ち手完了 / ✓完了）
- `data.json` に `progress` オブジェクトを追加（`overall` + `bottlenecks[].status`）

**progress スキーマ**:
```jsonc
"progress": {
  "overall": { "completed": 0, "total": 10, "percentage": 0 },
  "bottlenecks": [
    {
      "rank": 1,
      "status": "pending",        // "pending" | "analysis_done" | "action_done" | "complete"
      "proto_done": 0,            // action_done 時の施策プロトタイプ完了数
      "proto_total": 9
    }
  ],
  "updated_at": "2026-04-20T07:30:00+09:00"
}
```

**バグ修正**:
- 進捗バー実装時に `var pct = Math.round(...)` を `render()` 内に宣言したところ、
  var hoisting によりファイル先頭の `pct()` 関数（パーセント整形）がシャドーイングされ、
  ファネルサマリー等の `pct(rate)` 呼び出しが `pct is not a function` で失敗していた。
- ローカル変数を `progPct` にリネームして衝突を解消（`report.html`）。

**教訓**: `report.html` 内では既存ヘルパー関数名（`pct`, `pp`, `fmtK`, `fmtNum`）を
ローカル `var` で再宣言しない。var hoisting により関数スコープ全体がシャドー化される。
