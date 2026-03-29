# VELTRA CVR 週次ボトルネック分析 — 生成指示書

## このドキュメントの目的

GA4 MCPに接続されたClaude（別アカウント）が、週次でボトルネック分析レポートを自動生成するための完全な指示書。
このドキュメントを渡すだけで、レポートHTMLとデータJSONを生成できる状態にする。

---

## 1. アーキテクチャ

```
[毎週の生成フロー]

Claude (GA4 MCP接続)
  ↓ run_report × 複数クエリ
GA4 Property 347074845
  ↓ 集計・分析
JSON ファイル生成 (reports/YYYY-wWW/data.json)
  ↓ テンプレートHTML に埋め込み
HTML ファイル生成 (reports/YYYY-wWW/index.html + bottleneck-N.html)
  ↓ git commit & push
Vercel 自動デプロイ → https://v2.veltra-cvr.vercel.app/
```

**リアルタイムではない。** 週に1回、JSONスナップショットを生成してgit commitする。
過去週のデータは `reports/YYYY-wWW/data.json` として蓄積される。

---

## 2. ディレクトリ構成

```
v2-veltra-cvr/
├── index.html                          ← フレームワーク（トップ・不変）
├── reports/
│   ├── 2026-w14/                       ← Week 14 (3/30〜4/5)
│   │   ├── data.json                   ← GA4から取得した生データ
│   │   ├── index.html                  ← #1 詳細 + サマリーテーブル
│   │   ├── bottleneck-2.html
│   │   ├── ...
│   │   └── bottleneck-10.html
│   ├── 2026-w15/                       ← Week 15 (4/6〜4/12)
│   │   ├── data.json
│   │   ├── index.html
│   │   └── ...
│   └── ...
├── templates/                          ← HTMLテンプレート（後述）
│   ├── report-main.html
│   └── bottleneck-detail.html
└── README.md
```

---

## 3. 固定値（変わらないもの）

| 項目 | 値 |
|------|-----|
| GA4 Property ID | `347074845` |
| GA4 Property名 | VELTRA Japanese excl. Yokka - GA4 |
| MCP Server | `https://ai.veltra.dev/ga/mcp` |
| ファネル段階数 | 5段階 |
| セグメントTier数 | 3 Tier（Tier 1: チャネル×デバイス / Tier 2: 新規リピーター×エリア / Tier 3: 掛け合わせ） |
| ボトルネック件数 | 10件 |
| 原因仮説数 | 各ボトルネックに3件 |
| 打ち手数 | 各仮説に3件 |
| 競合リスト | Klook, KKday, GetYourGuide, Viator, asoview!, NEWT |
| デプロイ先 | `https://v2.veltra-cvr.vercel.app/` |
| リポジトリ | `github.com/SDkotarom/v2-veltra-cvr` |

---

## 4. 可変値（毎週変わるもの）

### 4-1. 週の定義

| 変数 | 例（W14） | 算出方法 |
|------|-----------|----------|
| `WEEK_ID` | `2026-w14` | ISO週番号 |
| `WEEK_LABEL` | `26年4月 Week1（3/30〜4/5）` | 表示用ラベル |
| `DATE_START` | `2026-03-30` | 月曜日 |
| `DATE_END` | `2026-04-05` | 日曜日 |
| `DATA_PERIOD` | `28daysAgo` ~ `yesterday` | GA4クエリの対象期間（直近28日固定） |

### 4-2. GA4から取得するデータ（クエリ定義）

以下のクエリを順番に実行し、結果をJSONに格納する。

#### クエリ1: ベースライン（全体ファネル）
```
property_id: 347074845
date_ranges: [{start_date: '28daysAgo', end_date: 'yesterday'}]
dimensions: []
metrics: [sessions, ecommercePurchases]
→ 全体セッション数、全体CV数、全体CVR を算出
```

#### クエリ2: ファネル各段階のイベント数
```
dimensions: [eventName]
metrics: [eventCount]
dimension_filter: eventName in [
  'session_start',
  'view_item',
  'GA4_vtjp_ex_yokka_view_booking_calendar',
  'form_start',
  'purchase'
]
→ 各段階の絶対数を取得
```

#### クエリ3: Tier 1-A チャネル別ファネル
```
dimensions: [sessionDefaultChannelGroup, eventName]
metrics: [eventCount]
dimension_filter: eventName in [上記5イベント]
→ チャネル × ファネル段階のマトリクス
```

#### クエリ4: Tier 1-B デバイス別ファネル
```
dimensions: [deviceCategory, eventName]
metrics: [eventCount]
dimension_filter: eventName in [上記5イベント]
→ デバイス × ファネル段階のマトリクス
```

#### クエリ5: Tier 2-A 新規/リピーター別
```
dimensions: [newVsReturning, eventName]
metrics: [eventCount]
dimension_filter: eventName in [上記5イベント]
→ 新規/リピーター × ファネル段階のマトリクス
```

#### クエリ6: Tier 2-B エリア別（landingPagePath推定）
```
dimensions: [landingPagePath]
metrics: [sessions, ecommercePurchases]
dimension_filter: landingPagePath contains '/jp/hawaii/' OR '/jp/asia/bali/' OR '/jp/europe/' ...
→ エリア推定 × セッション数 × CV数
```

#### クエリ7: Tier 3 掛け合わせ（チャネル×デバイス）
```
dimensions: [sessionDefaultChannelGroup, deviceCategory, eventName]
metrics: [eventCount]
→ チャネル × デバイス × ファネル段階
```

#### クエリ8: Tier 3 掛け合わせ（チャネル×新規リピーター）
```
dimensions: [sessionDefaultChannelGroup, newVsReturning, eventName]
metrics: [eventCount]
→ チャネル × 新規リピーター × ファネル段階
```

### 4-3. data.json のスキーマ

```json
{
  "meta": {
    "week_id": "2026-w14",
    "week_label": "26年4月 Week1（3/30〜4/5）",
    "date_start": "2026-03-30",
    "date_end": "2026-04-05",
    "data_period": "28daysAgo ~ yesterday",
    "generated_at": "2026-03-30T09:00:00+09:00",
    "property_id": "347074845"
  },
  "baseline": {
    "sessions": 3017970,
    "purchases": 43760,
    "cvr": 0.0145,
    "funnel": {
      "session_start": 3017970,
      "view_item": 1364122,
      "calendar_view": 401052,
      "form_start": 36095,
      "purchase": 43760
    },
    "conversion_rates": {
      "1_to_2": 0.452,
      "2_to_3": 0.294,
      "3_to_4": 0.090,
      "4_to_5": 1.213
    }
  },
  "segments": {
    "channel": { ... },
    "device": { ... },
    "new_returning": { ... },
    "area": { ... },
    "channel_device": { ... },
    "channel_new_returning": { ... }
  },
  "bottlenecks": [
    {
      "rank": 1,
      "title": "Mobile × Organic — カレンダー表示率の低さ",
      "funnel_stage": "2_to_3",
      "segments": ["Mobile", "Organic Search", "新規"],
      "current_rate": 0.182,
      "baseline_rate": 0.294,
      "gap_pct": -0.38,
      "impact_sessions": 840000,
      "hypotheses": [
        {
          "id": "h1",
          "title": "カレンダーの読み込みが遅く、スクロール前に離脱",
          "confidence": "high",
          "evidence": "Mobile TTFB: 3.2s / Desktop: 0.8s",
          "actions": [
            {
              "id": "a1",
              "title": "カレンダーの遅延ロード + スケルトンUI",
              "expected_impact": "+8pt",
              "spec": "IntersectionObserverでlazy loading..."
            }
          ]
        }
      ]
    }
  ]
}
```

### 4-4. HTMLの可変部分

テンプレートHTML内の以下のプレースホルダーを `data.json` の値で置換する：

| プレースホルダー | data.jsonのパス | 例 |
|------------------|----------------|-----|
| `{{WEEK_LABEL}}` | `meta.week_label` | 26年4月 Week1（3/30〜4/5） |
| `{{TOTAL_SESSIONS}}` | `baseline.sessions` | 3,017,970 |
| `{{TOTAL_CVR}}` | `baseline.cvr` | 1.45% |
| `{{FUNNEL_1_TO_2}}` | `baseline.conversion_rates.1_to_2` | 45.2% |
| ボトルネック#N全体 | `bottlenecks[N-1]` | オブジェクト全体 |

---

## 5. ボトルネック特定のロジック

```
1. 全体ファネル転換率をベースラインとして算出
2. Tier 1（チャネル×デバイス）で同じファネル段階の転換率を算出
3. 全体平均との乖離率を計算: gap = (segment_rate - baseline_rate) / baseline_rate
4. gap が -20% 以上 かつ セッション数 10,000以上 のセグメントを抽出
5. インパクト順にソート: impact = abs(gap) × segment_sessions
6. 上位10件をボトルネックとして採用
7. 各ボトルネックに対しTier 2-3で深掘り
8. 原因仮説を3件生成（Web検索・競合調査を活用）
9. 各仮説に打ち手3件 + 開発仕様 + プロトタイプを生成
```

---

## 6. 競合調査の条件

| 競合 | ファビコンURL | 調査対象 |
|------|-------------|----------|
| Klook | `https://cdn.klook.com/s/dist_web/favicons/favicon-32x32.png` | 該当エリアの類似商品ACページ（Mobile） |
| KKday | `https://www.kkday.com/favicon.png` | 同上 |
| GetYourGuide | `https://cdn.getyourguide.com/tf/assets/static/favicons/2026/favicon-32.png` | 同上 |
| Viator | `https://cache.vtrcdn.com/orion/images/favicon.ico` | 同上 |
| asoview! | `https://image.asoview-media.com/image/production/fundamentals/logo/favicon.ico` | 国内レジャーの類似ACページ（Mobile） |
| NEWT | `https://newt.net/favicon.ico` | パッケージツアーの類似ページ（参考程度） |

**調査観点：** ボトルネックの該当ファネル段階に関連するUIを、**Mobile視点**で比較。Desktop差分がある場合は併記。

---

## 7. 生成ステップ（実行手順）

```
Step 1: 今週の WEEK_ID / DATE_START / DATE_END を決定
Step 2: GA4 MCPでクエリ1〜8を実行
Step 3: 結果をdata.jsonスキーマに整形
Step 4: ボトルネック特定ロジック（Section 5）を実行
Step 5: 上位10件に対し原因仮説・打ち手・プロトタイプを生成
Step 6: #1のボトルネックに対し競合調査を実行
Step 7: HTMLを生成（テンプレート + data.json）
Step 8: reports/YYYY-wWW/ ディレクトリに出力
Step 9: index.htmlのアーカイブセクションに新エントリ追加
Step 10: git commit & push
```

---

## 8. 出力ファイル一覧（毎週生成）

| ファイル | 内容 |
|---------|------|
| `reports/YYYY-wWW/data.json` | GA4生データ + 分析結果 |
| `reports/YYYY-wWW/index.html` | #1詳細分析 + #2〜#10サマリー |
| `reports/YYYY-wWW/bottleneck-2.html` 〜 `bottleneck-10.html` | 各ボトルネック詳細 |
| `index.html` | トップページのアーカイブに新週追加（差分更新） |

---

## 9. Opus 4.6 向け効率化ガイド

### 原則
- **コンテキストの前半に固定情報、後半に可変情報を配置**する。固定情報（このドキュメント全体）は1回渡せば良い。
- **1ターンで複数のGA4クエリを実行**しない。1ターン1クエリで結果を確認してから次へ。APIエラー時の手戻りが減る。
- **HTMLテンプレートを先に確定**してからデータを流し込む。テンプレートの修正とデータ生成を混ぜない。

### プロンプト構成（推奨）

```
[ターン1] ← 初回のみ
このドキュメント（生成指示書）を全文渡す。
「この指示書に基づいて、今週（W14, 3/30〜4/5）のレポートを生成してください。
まずStep 1-2（GA4クエリ実行）から始めてください。」

[ターン2]
「クエリ結果を確認しました。Step 3-4（JSON整形 + ボトルネック特定）を実行してください。
data.jsonを出力してください。」

[ターン3]
「data.jsonを確認しました。Step 5-6（仮説・打ち手・競合調査）を実行してください。
#1のボトルネックの詳細分析を出力してください。」

[ターン4]
「#1を確認しました。#2〜#10のHTMLを生成してください。」

[ターン5]
「全ファイルを確認しました。index.htmlのアーカイブセクションを更新してください。」
```

### トークン節約テクニック

1. **繰り返し指示をしない**: このドキュメントに書いてある内容を会話中に再説明しない。「指示書のSection 5に従って」と参照する。

2. **出力フォーマットを指定する**: 「JSON形式で出力」「HTMLファイルとして出力」を明示し、説明文を付けないよう指示。
   - NG: 「以下のJSONを生成しました。これは〜を表しています…」
   - OK: JSONだけ出力

3. **差分更新を活用する**: index.htmlの更新は全文再生成ではなく、アーカイブセクションの差分のみ指示。

4. **テンプレート化**: #2〜#10のHTMLは共通テンプレートにデータを流し込む形にし、10ファイル分のHTML全文を毎回生成しない。

5. **data.jsonを中間成果物として保存**: GA4クエリの結果を毎ターン保持する代わりに、早い段階でdata.jsonとして確定し、以降はそこを参照する。

6. **「確認不要、出力のみ」と指定**: 分析の途中経過説明や確認質問を省略させる。
   ```
   確認不要。指示書Section 5のロジックに従い、data.jsonのbottlenecksを生成してください。
   出力はJSONのみ。説明文不要。
   ```

7. **プロトタイプのHTMLは#1のみフル生成**: #2〜#4は仮説カード+プレースホルダー、#5〜#10はプレースホルダーのみ。全件フル生成しない。

### GA4 MCP クエリの注意事項

| 注意点 | 対処 |
|--------|------|
| `sessions` × `pagePath` の組み合わせは不正確な値を返す | 別々のクエリで取得 |
| カスタムディメンション（エリア、商品特性）はAPIエラー | `landingPagePath` で推定 |
| YoY比較で明示的日付指定するとエラー | `NdaysAgo` 形式を使用 |
| `addToCarts` / `checkouts` はゼロ | `form_start` / `purchase` で代替 |
| `bounceRate` / `averageSessionDuration` はエラー | 使用しない |
| Property ID に `properties/` プレフィックス不要 | `347074845` のみ指定 |

---

## 10. 品質チェックリスト（生成後）

- [ ] data.json の sessions / purchases が GA4 UI の数値と概ね一致するか（±10%以内）
- [ ] ファネルの各段階が単調減少しているか（session > view_item > calendar > form > purchase）
- [ ] ボトルネック10件が全て gap -20%以上かつ10,000セッション以上か
- [ ] #1のプロトタイプのBeforeがVELTRAの実際のACページ構造と一致しているか
- [ ] 競合調査がMobile視点で記述されているか
- [ ] 全HTMLのリンク（前後ページ、サマリーへの戻り）が正しく機能するか
- [ ] index.html のアーカイブに新週が追加されているか
