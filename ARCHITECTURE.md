# ARCHITECTURE.md — ボトルネック分析レポート アーキテクチャ

> 最終更新: 2026-04-07（テンプレートリファクタリング + 週期間変更）

---

## 1. ディレクトリ構成

```
v2-veltra-cvr/
├── ドキュメント
│   ├── CLAUDE.md                    AI セッション設定
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
└── scripts/
    ├── generate-week.py             週次スキャフォールド生成
    ├── validate-report.py           レポートバリデーション
    └── extract-content-from-html.py content.json スケルトン生成ユーティリティ
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
          "prototype": {          // ★必須 — 全施策に Before/After モックアップが必要
            "before_html": "<div>...</div>",  // 現状のUI（問題を可視化）
            "after_html": "<div>...</div>"    // 施策適用後のUI（改善を可視化）
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

## 6. content.json 品質チェックルール（必須）

content.json を作成・更新する際は、以下のチェックを**全て通過**させること。

### 6.1 構造チェック（全10ファイル共通）

| チェック項目 | 必須値 |
|-------------|--------|
| `number` | 1〜10（ファイル名と一致） |
| `title` | 空でないこと |
| `tags` | 1件以上 |
| `deviation` | 空でないこと |
| `impact_sessions` | 空でないこと |
| `funnel_compare` | 4セル |
| `callout` | `title` + `body_html` |
| `hypotheses` | **3件**（h1, h2, h3） |
| 各仮説の `actions` | **3件**（計9施策 A-I） |
| 各施策の `prototype` | **必須** — `before_html` + `after_html` |
| `competitive` | **6社** |
| `verification` | **1件以上** |

### 6.2 プロトタイプ品質チェック

各施策の `prototype` は以下を満たすこと:

- `before_html`: 現状のUI問題を可視化するVELTRAモバイルモックアップ
- `after_html`: 施策適用後の改善UIを可視化するVELTRAモバイルモックアップ
- Before/After で**施策の効果が視覚的に明確**であること
- HTMLはインラインスタイルで記述（外部CSS依存なし、CSS変数は使用可）

### 6.3 自動チェックコマンド

```bash
# 全10ファイルの構造チェック
python3 -c "
import json, os, sys
ok = True
for i in range(1, 11):
    f = f'reports/2026-wXX/bottleneck-{i}-content.json'  # wXX を実際の週に置換
    d = json.load(open(f))
    h = d.get('hypotheses', [])
    actions = [a for hyp in h for a in hyp.get('actions', [])]
    protos = [a for a in actions if a.get('prototype')]
    comp = d.get('competitive', [])
    if len(h) != 3:
        print(f'#{i}: hypotheses={len(h)} (want 3)'); ok = False
    if len(actions) != 9:
        print(f'#{i}: actions={len(actions)} (want 9)'); ok = False
    if len(protos) != 9:
        print(f'#{i}: prototypes={len(protos)}/9 ★MISSING★'); ok = False
    if len(comp) < 6:
        print(f'#{i}: competitive={len(comp)} (want 6)'); ok = False
if ok: print('ALL CHECKS PASSED')
else: sys.exit(1)
"
```

---

## 7. 週次レポート生成時の更新ファイル一覧（MECE）

新しい週（例: W15）を作成する際に更新が必要な全ファイルを網羅する。

### 7.1 新規作成ファイル（週ディレクトリ内）

| ファイル | 内容 | 生成方法 |
|----------|------|----------|
| `reports/{week}/data.json` | GA4分析データ（meta, baseline, funnel_7d, segments, bottlenecks） | `generate-week.py` でスケルトン → GA4 MCP でデータ投入 |
| `reports/{week}/index.html` | 週次サマリーページ | 前週の `index.html` をテンプレートとしてデータ差し替え |
| `reports/{week}/bottleneck-{1-10}-content.json` × 10 | ボトルネック分析データ | AI生成（ARCHITECTURE.md §4 スキーマ、§6 品質チェック準拠） |

### 7.2 更新ファイル（ルート）

| ファイル | 更新内容 | 注意事項 |
|----------|----------|----------|
| `reports-index.json` | 新しい週のエントリ追加 | `rolling_start`/`rolling_end` を含める。weeks は時系列順（古い→新しい） |
| `weekly-summary.json` | 週次サマリーデータ追加 | |
| `summary-data.json` | ダッシュボード用集約データ更新 | 最新週のデータで上書き |
| `archive-meta.json` | `updatedAt` 更新 | |

### 7.3 週次サマリーページ（`reports/{week}/index.html`）のデータバインド箇所

前週をテンプレートとして新週のデータに差し替える箇所の一覧:

| セクション | 差し替え対象 | データソース | 表示ルール |
|-----------|-------------|-------------|-----------|
| ヘッダーバンド | 週ID + 期間 | meta | `W{N}（{yyyy/m/d}〜{yyyy/m/d}）` ※ローリング28日間 |
| 分析対象データ | GA4 Property + 期間 | meta | `直近28日間（{yyyy/m/d}〜{yyyy/m/d}）` ※年付き |
| レポート発行週 | 週ラベル | meta | `W{N}（{yyyy/m/d}〜{yyyy/m/d}）` ※「2026年」不要 |
| 生成日時 | タイムスタンプ | meta.generated_at | `YYYY-MM-DD HH:MM JST` |
| ファネルサマリー | 4カラム通過率 + WoWバッジ + バー | baseline.conversion_rates, funnel_7d.wow_pp | ダッシュボードと同じUI（バー + WoWバッジ） |
| KPI ストリップ | セッション数 → CV数 → CVR | baseline | 順番: **セッション数 → CV数（予約完了） → CVR**（ダッシュボードと統一） |
| 今週のトピック | 4つのcalloutカード | baseline.conversion_rates, funnel_7d.wow_pp | **28日ローリングベース**で統一。文章は箇条書き（`<ul><li>`）。単週データは使わない |
| ボトルネックリスト | #1〜#10 リスト | data.json の bottlenecks + content.json | トグル不要（常時展開）。各アイテムは `→` 付きのリンク。リンク先: `/bottleneck.html?week={week}&num={N}` |

### 7.4 日付表示フォーマット統一ルール

全ページ共通:

| 場所 | フォーマット | 例 |
|------|-------------|-----|
| ヘッダー・セクションタイトル | `{yyyy/m/d}〜{yyyy/m/d}` （開始は年付き、終了は年なし） | `2026/3/8〜4/4` |
| 分析対象データ・レポート発行週 | 両方年付き | `2026/3/8〜2026/4/4` |
| 左ナビ（nav.js） | 開始のみ年付き | `2026/3/8〜4/4` |
| reports-index.json の week_label | 両方年付き | `W14（2026/3/8〜2026/4/4）` |
| 全ての期間 | **ローリング28日間**を表示 | 週次期間（date_start〜date_end）は表示しない |

### 7.5 UI統一ルール

週次サマリーページはダッシュボード（`index.html`）と以下を統一する:

| 要素 | ルール |
|------|--------|
| ファネル通過率 | 4カラム（①→②、②→③、③→④、④→⑤）+ バー + WoWバッジ |
| KPI 並び順 | セッション数 → CV数（予約完了） → CVR |
| WoW の基準 | **28日ローリング**で統一（単週データは使わない） |
| トピックカード | callout形式（green/red/amber）、本文は箇条書き |
| ボトルネックリスト | トグルなし、常時展開、`→` リンク付き |
| 最小フォントサイズ | **12px**（10px, 11px は使わない。funnel-def.js のコード表記は13px） |
| ホバー | 背景色変更ではなく左ボーダー（`border-left: 3px solid var(--red)`） |

---

## 8. ナビゲーション（nav.js）

全ページに `nav.js` を読み込むことでサイドナビが自動構築される。

- **データソース**: `/reports-index.json` → 各週の `data.json` を fetch
- **ページ種別検出**: URLパスとクエリパラメータで判定
  - ボトルネック: `/bottleneck.html?week=...&num=...`
  - 週次サマリー: `/reports/2026-w14/`
  - トップ: `/`
- **リンク形式**: `/bottleneck.html?week={week_id}&num={rank}`
- **期間表示**: ローリング28日間（`rolling_start`〜`rolling_end`）、開始のみ年付き

---

## 9. デプロイ

| 項目 | 値 |
|------|-----|
| ホスティング | Vercel |
| デプロイトリガー | `main` ブランチへの push |
| ビルドステップ | なし（静的ファイル配信） |
| URL | https://v2-veltra-cvr.vercel.app/ |

---

## 10. リファクタリング履歴

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
- `playbook.md`: 日付範囲テーブルを更新
