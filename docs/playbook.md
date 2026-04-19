# Weekly Report Playbook — VELTRA CVR Bottleneck Analysis

> **このファイルは週次レポート生成の唯一の運用マニュアルです。**
> 新しいセッションでは最初にこのファイルを読み込んでください。
> デザインルール: `veltra-design-system.md` / URL構造: `veltra-url-structure.md`

---

## 1. プロジェクト概要

- **目的**: VELTRAのCVR改善。ファネル×セグメントで転換率を分析し、ボトルネック10件を特定、各件に仮説・打ち手・プロトタイプを生成
- **ホスティング**: Vercel（mainブランチ push → 自動デプロイ）
- **URL**: https://v2-veltra-cvr.vercel.app/
- **認証**: auth.js による Google OAuth（sessionStorage `gauth_user`）
- **GA4 Property**: `347074845`

---

## 2. リポジトリ構成

```
v2-veltra-cvr/
├── CLAUDE.md                   ← AI セッション設定（ルート必須）
├── README.md                   ← プロジェクト概要（ルート必須）
├── docs/
│   ├── playbook.md             ← このファイル（運用マニュアル）
│   ├── ARCHITECTURE.md         ← 技術構成・スキーマ詳細
│   ├── veltra-design-system.md ← VELTRAサイトのデザインルール
│   ├── veltra-url-structure.md ← VELTRA URL階層（エリア定義）
│   └── prd-template.md         ← PRDテンプレート（汎用）
├── known-implementations.json   ← 実装済み機能カタログ（150+件、カテゴリ別）
├── feasibility-constraints.json ← 制約チェックリスト（10カテゴリ）
├── scripts/
│   ├── generate-week.py        ← 週次スキャフォールド生成
│   ├── validate-report.py      ← レポートバリデーション
│   ├── audit-actions.py        ← 施策化レビュー監査（重複+制約チェック）
│   ├── extract-content-from-html.py ← content.json スケルトン生成
│   └── archive/                ← 過去の一時スクリプト
├── auth.js / nav.js / funnel-def.js / bottleneck.js  ← 共通JS
├── bottleneck.html / bottleneck.css  ← ボトルネック分析テンプレート（動的描画）
├── index.html / login.html / cycle.html / analysis.html  ← ページ
├── summary-data.json / weekly-summary.json / reports-index.json / archive-meta.json  ← データ
└── reports/{YYYY}-w{WW}/
    ├── data.json               ← GA4実データ（ファネル・セグメント・ボトルネック）
    ├── index.html              ← 週次サマリー
    └── bottleneck-{1-10}-content.json  ← ボトルネック分析コンテンツ
```

---

## 3. ファネル定義（5段階）

| 段階 | ラベル | GA4イベント/条件 | 通過率 |
|------|--------|-----------------|--------|
| ① | 流入 | 全セッション数 | — |
| ② | AC到達 | pagePath に `/a/` を含むセッション | ①→② |
| ③ | 検討 | `GA4_vtjp_ex_yokka_view_booking_calendar` イベント | ②→③ |
| ④ | 意向 | pagePath に `/jp/booking` を含むセッション | ③→④ |
| ⑤ | 完了 | `purchase` イベント | ④→⑤ |

**通過率計算**: `rates.1_to_2 = funnel.ac_page_reach_users / funnel.session_start_users`（以下同様）
**CVR**: `purchase / session_start_users`

---

## 4. 週次サイクル（3フェーズ）

### Phase 1: データ取得（Sonnet + GA4 MCP）

```bash
# Step 0: スキャフォールド生成
python3 scripts/generate-week.py --week {YYYY}-w{WW}
```

#### 日付範囲の算出

| 期間 | 算出方法 | 例（W15, 生成日 4/13 月曜） |
|------|---------|---------------------------|
| `date_start` | ISO週の月曜 - 1日 = **日曜** | `2026-04-05` |
| `date_end` | ISO週の月曜 + 5日 = **土曜** | `2026-04-11` |
| `rolling_start` | `date_end - 27日` | `2026-03-15` |
| `rolling_end` | `date_end` | `2026-04-11` |
| Q10 今週 | `date_start` 〜 `date_end` | `2026-04-05 〜 2026-04-11` |
| Q10 先週 | `date_start - 7日` 〜 `date_start - 1日` | `2026-03-29 〜 2026-04-04` |

> 生成は毎週月曜 AM 4:00 JST。土曜のGA4データを1日寝かせて確定させるため。

> `scripts/generate-week.py` が `meta` に上記日付を自動計算して `data.json` に書き込みます。

#### ベルトラアカウント向け実行手順

```
1. playbook.md を読む
2. reports/{YYYY}-w{WW}/data.json の meta.rolling_start 〜 meta.rolling_end を確認
3. GA4 Property 347074845 に対して Q1〜Q10 を上記期間で実行
4. 結果を data.json のスキーマ（セクション5）に従って格納
5. 【最優先】data.json 完成後、真っ先にサマリーページを更新する
   - summary-data.json（月次KPI追記）
   - weekly-summary.json（週次KPI追記）
   - reports-index.json（新しい週のエントリ追加）
   - archive-meta.json（updatedAt 更新）
   - ローカル/Vercelで https://v2-veltra-cvr.vercel.app/ のサマリーが正しく描画されるか確認
6. サマリーページ更新分を先に commit & push（Phase 2 の前にデプロイ確定）
7. その後 Phase 2（ボトルネック分析）へ進む
```

> 📌 **重要**: ボトルネック分析（Phase 2）に入る前に、必ずサマリーページ関連JSONを先に更新・コミット・プッシュすること。サマリー描画不整合を早期検出するため。

#### クエリ一覧

以下のクエリを GA4 MCP で実行し、`data.json` に格納:

| Query | 内容 | dimensions | metrics | 格納先 |
|-------|------|-----------|---------|--------|
| Q1 | ベースラインファネル | — | sessions, 各ファネルイベント | `baseline` |
| Q2 | チャネル別 | sessionDefaultChannelGroup | 同上 | `segments.channel` |
| Q3 | デバイス別 | deviceCategory | 同上 | `segments.device` |
| Q4 | 新規/リピーター | newVsReturning | 同上 | `segments.new_returning` |
| Q5 | チャネル×デバイス | channel + device | 同上 | `segments.channel_device` |
| Q6 | チャネル×新規リピーター | channel + newVsReturning | 同上 | `segments.channel_new_returning` |
| Q7 | エリア別（20エリア） | landingPage フィルタ | 同上 | `segments.area` |
| Q8 | 「その他」内訳（上位5） | landingPage（Q7除外） | sessions, purchases | `segments.area.other.sub_areas` |
| Q9 | サマリー（月次/週次） | — | sessions, purchases, cvr | `summary-data.json`, `weekly-summary.json` |
| Q10 | 7日ファネル（WoW） | — | 今週+先週のファネル | `funnel_7d` |

**共通条件**:
- Property: `347074845`
- 期間: 直近28日間（Q10のみ7日）
- rates は小数（42.35% → `0.4235`）

#### Phase 1 完了時の更新ファイル一覧

**更新順序を厳守**（JSON作成 → サマリー更新を最優先 → その後ボトルネック分析）:

| 優先 | ファイル | 更新内容 |
|------|----------|---------|
| 1 | `reports/{W}/data.json` | Q1〜Q10 の全結果 |
| 2 ★最優先 | `summary-data.json` | 当月の月次KPI追記 |
| 2 ★最優先 | `weekly-summary.json` | 当週の週次KPI追記/更新 |
| 2 ★最優先 | `reports-index.json` | **新しい週のエントリ追加（week_label, date_start, date_end を正しい週日付で）** |
| 2 ★最優先 | `archive-meta.json` | updatedAt タイムスタンプ更新 |
| 3 | サマリーページ描画確認 | https://v2-veltra-cvr.vercel.app/ で当週の数値が正しく表示されているか確認 |
| 4 | Phase 2 開始 | ボトルネック分析（`bottleneck-{1-10}-content.json`）へ進む |

> ⚠️ `reports-index.json` の `date_start` / `date_end` は対象週の月〜日（例: 3/30〜4/5）。
> ローリング期間（28日）ではないので注意。

> ⚠️ **手順固定**: data.json が出来上がったら、**何よりも先に** 上記サマリー系4ファイル（summary-data / weekly-summary / reports-index / archive-meta）を更新する。ボトルネック分析は、サマリーページが正しく描画された状態を確認した後に着手すること。

### Phase 2: ボトルネック分析 & content.json 生成（Opus）

**前提条件**: Phase 1 で data.json 作成後、**サマリーページ更新（summary-data.json / weekly-summary.json / reports-index.json / archive-meta.json）が完了しコミット済み**であること。未完了の場合は Phase 2 に進まず Phase 1 に戻ること。

**重要**: 週次サマリーページは `report.html` が `data.json` から動的に描画するため、
HTML生成は不要。Phase 2 では `bottleneck-{1-10}-content.json` のみ生成する。

#### Step 1: スケルトン自動生成

```bash
python3 scripts/generate-week.py --skeleton --week {YYYY}-w{WW}
```

data.json の bottlenecks 配列から content.json の機械的フィールドを自動生成（**約77%の記述を自動化**）。
Claude が埋めるべき箇所は `TODO:` プレースホルダーで示される。

#### Step 1.5: behavior_context（行動仮説レイヤー）生成

スケルトン内の `behavior_context` TODO を埋める。**仮説・施策の前に行う**。

**生成ルール**:
1. **estimated_action**: ファネルドロップオフ地点でのユーザー行動を1文で推定（「〜した可能性が高い」等、断定しない）
2. **evidence**: data.json のセグメント比較から2〜4件の裏付けデータ。具体的数値を引用
3. **page_role_check**: 戦略ガイドSection 3 と照合（Area=大づかみ / Ctg=絞り込み / Ac=確信 / Form=完了）
4. **subtraction_check**: 情報追加でなく引き算で解決可能か検討
5. **pattern_references** (任意): 2025年ABテスト結果から類似パターンを引用（✅勝ち / ❌負け）

**ファネルステージ別テンプレート**:
- **①→②** (流入→AC到達): ランディングページの第一印象・信頼性・検索意図との合致
- **②→③** (AC到達→検討): ACページの情報量・プラン比較・カレンダー到達導線
- **③→④** (検討→意向): カレンダー→予約フォーム遷移障壁・CTA視認性
- **④→⑤** (意向→完了): 予約フォームの離脱要因（入力量・決済不安・エラー）

#### Step 2: Claude が TODO を埋める

1. **ボトルネック特定**: `data.json` のセグメント間比較から、インパクト順で10件ランキング（スケルトンに反映済み）
2. **各スケルトンの TODO: を埋める**（1ファイルずつ順番に）:
   - behavior_context（行動仮説）→ 仮説×3 → 打ち手×9（A-I）→ **HTMLモックアップ×9（必須）** → 競合比較6社

**⚠️ タイムアウト防止：必ずこの手順で実行すること**

```
# 前提: Opusセッションとして起動する（手動切替不要）
#   cd /home/user/v2-veltra-cvr && claude --model opus
# ↑ これだけ。セッション開始時からOpusが適用される。
# サブエージェント（Agent ツール）は使わない → stream idle timeout が発生する

# 1ファイルの作業順（Edit ツールで3〜5個ずつ置換）：
Step A: description_html / drill_down / callout
Step B: behavior_context（estimated_action, evidence, page_role_check, subtraction_check）
Step C: 仮説1（title, body, evidence）
Step D: 施策A（title, description, spec_html, impact）
Step E: 施策A prototype → before_html / after_html（HTMLモックアップ）
Step F: 施策B（title, description, spec_html, impact）
Step G: 施策B prototype → before_html / after_html
... 施策C〜I も同様に D+E のペアで繰り返す ...
Step X: 仮説2（title, body, evidence）→ 施策D/E/F ...
Step Y: 仮説3（title, body, evidence）→ 施策G/H/I ...
Step Z: competitive 6社 / competitive_insight / verification / verification_method

# 1ファイル完了後に必ず:
python3 -c "import json; json.load(open('reports/2026-w15/bottleneck-N-content.json'))" # JSON検証
git add reports/2026-w15/bottleneck-N-content.json
git commit -m "feat: W{WW} BN{N} bottleneck analysis content"
git push
```

**プロトタイプ形式：`before_html` / `after_html` を必ず使うこと**

```jsonc
// ✅ 正しい形式（必須）
"prototype": {
  "before_html": "<div style=\"border:1px solid #E0E0E0;border-radius:8px;overflow:hidden;max-width:375px;margin:0 auto;background:#F2F5F8\">...</div>",
  "after_html": "<div style=\"border:2px solid #2DAE6C;border-radius:8px;overflow:hidden;max-width:375px;margin:0 auto;background:#F2F5F8\">...</div>"
}

// ❌ 禁止（テキスト短縮形は使わない。CVR改善の提案としてワイヤーが読めないため）
"prototype": {
  "before_text": "...",
  "after_text": "..."
}
```

**HTMLモックアップ デザインルール**（W14準拠）:
- コンテナ: `max-width:375px; margin:0 auto;` （スマホ画面想定）
- Before: `border:1px solid #E0E0E0`（グレー枠）
- After: `border:2px solid #2DAE6C`（グリーン枠で改善を示す）
- VELTRAヘッダー: `<span style="font-size:15px;font-weight:900;color:#1B82C5">VELTRA</span>`
- CTAボタン: `background:#1B82C5; color:#fff;` または `background:#E8386E; color:#fff;`
- 最下部に改善ポイントを1文で: `color:var(--green)` または `color:#999`


**デザインルール**: `veltra-design-system.md` 参照
- プロトタイプのモックアップはVELTRAサイトデザイン準拠（`#1B82C5` blue CTA, `#F2F5F8` bg）
- レポートページは V2 テーマ（`--red:#E8423F`, `--bg:#f5f4f0`）

### Phase 3: デプロイ（Sonnet）

```bash
git add reports/{YYYY}-w{WW}/ summary-data.json weekly-summary.json reports-index.json archive-meta.json
git commit -m "feat: W{WW} bottleneck analysis report"
git push -u origin main
```

Vercel が自動デプロイ。

### Phase 2.5: 施策化レビュー（実装重複チェック + 実現可能性評価）

> **目的**: 打ち手の施策化率を高める。「レビューのみで施策化できる」品質を Phase 2 の時点で担保する。

#### Step 1: 既存実装の把握

Phase 2 開始前に以下を必ず読み込む:
- `known-implementations.json`: 実装済み機能カタログ（カテゴリ別、キーワード付き）
- `feasibility-constraints.json`: 10カテゴリの実務制約チェックリスト
- `annotations.json`: 直近のリリースイベント（新機能が追加されている可能性）

#### Step 2: 各 action の implementation_check 記入

各施策について `known-implementations.json` のキーワードと照合し、status を判定:

```
new           → 未実装。そのまま施策化可能
partial       → 類似機能あり。差分（未実装部分）を note に明記
already_exists → 実装済み。代替施策に差し替える
superseded    → より良い実装が存在。代替施策に差し替える
```

**差し替えルール**: `already_exists` / `superseded` の施策は削除せず、`note` に理由を書いた上で代替施策を同じ letter で提案する。

#### Step 3: 各 action の feasibility 記入

`feasibility-constraints.json` の `trigger_keywords` でマッチする制約を特定し:

1. `effort`: S/M/L/XL を判定
2. `constraints`: 該当する制約IDを列挙
3. `constraint_notes`: その施策固有の制約影響と回避策（1-2文）
4. `prerequisites`: 実装前に確認が必要な前提条件
5. `quick_wins`: `effort == "S"` かつ `constraints` が空なら `true`

#### Step 4: 実務考慮ポイント事前検証

以下の考慮ポイントを施策ごとに事前検証し、`constraint_notes` に反映:

| 考慮ポイント | チェック内容 | よくある問題 |
|-------------|-------------|-------------|
| **在庫リアルタイム性** | 在庫数表示を含む施策か？ | パートナーAPIごとに在庫取得が異なる。リクエスト制は在庫概念なし |
| **為替レート** | 価格比較・表示を含むか？ | JPYデフォルト化済みだがダイナミックプライシングと複合 |
| **時差** | 日時表示・締切を含むか？ | 現地時間vsJST。「明日」の定義が目的地で異なる |
| **パーソナライズ依存** | ログイン/Cookie依存か？ | 未ログインユーザーが大多数。3rd party Cookie廃止 |
| **パートナーAPI** | 外部API改修が必要か？ | リードタイム数ヶ月。VELTRA側でコントロール不可 |
| **ABテスト履歴** | 類似施策の過去テスト結果は？ | 情報追加系は負ける傾向（引き算の設計思想） |
| **マルチサイト** | JP以外への展開が必要か？ | JP優先、EN/HAは別フェーズ |
| **計測可能性** | 効果を既存GA4イベントで測れるか？ | 新規イベント追加はGTM変更が必要 |
| **モバイル/PC差異** | デバイス特化UIか？ | フローティングUIの画面占有率に注意 |
| **開発工数** | フロントのみか、バックエンド必要か？ | S=即実行、L/XL=プロジェクト化が必要 |

#### Step 5: 監査スクリプト実行

```bash
python3 scripts/audit-actions.py --week {YYYY}-w{WW}
```

出力:
- 重複検出一覧（already_exists / superseded）
- 制約該当一覧（high risk constraints）
- Quick Wins 一覧（effort=S, constraints=空）
- 施策化レディネスサマリー

### Phase 4: 検証 → 自動修正 → 指示書改善（Sonnet）

Phase 3 完了後に自動実行する。

```bash
python3 scripts/validate-report.py --week {YYYY}-w{WW}
```

#### 検証項目（スクリプトが自動チェック）
1. `reports-index.json` の日付・ラベルが正しいか
2. サマリーページのベースライン数値が data.json と一致するか
3. 日付範囲（ローリング期間）が正しいか
4. 用語統一（回遊段階→流入→AC到達 等）
5. 全10件の bottleneck HTML が存在するか
6. weekly-summary.json / archive-meta.json が更新されているか
7. ファビコンURL が正しいか
8. 「仮想データ」表記が残っていないか

#### エラー時の対応フロー

```
validate-report.py 実行
  ├─ ✅ エラー0件 → 完了
  └─ ❌ エラーあり
       ├─ 1. エラー内容を読んで該当HTMLを自動修正
       ├─ 2. git commit & push（再デプロイ）
       ├─ 3. validate-report.py を再実行（修正確認）
       └─ 4. 同じエラーが今後起きないよう playbook.md の
            品質チェックリストまたは Phase 1-3 の手順を更新
```

> ⚠️ Phase 4 は「修正して終わり」ではなく、**指示書（playbook.md）自体を改善**して再発防止する。

---

## 5. データスキーマ

### data.json

```json
{
  "meta": { "week_id", "date_start", "date_end", "rolling_start", "rolling_end", "ga4_property", "generated_at" },
  "baseline": {
    "sessions": number,
    "purchases": number,
    "cvr": number,
    "funnel": { "session_start_users", "ac_page_reach_users", "calendar_view", "form_start", "purchase" },
    "conversion_rates": { "1_to_2", "2_to_3", "3_to_4", "4_to_5", "wow_pp": { "1_to_2", ... } }
  },
  "funnel_7d": null | { "funnel": {...}, "conversion_rates": {...} },
  "segments": {
    "channel": { "Organic Search": { "sessions", "share", "purchases", "cvr", "funnel": {...}, "rates": {...} }, ... },
    "device": { "mobile": {...}, "desktop": {...}, ... },
    "new_returning": { "new": {...}, "returning": {...} },
    "area": {
      "hawaii": { "sessions", "share", "purchases", "cvr", "funnel": {...}, "rates": {...} },
      ... (20エリア),
      "other": { ..., "sub_areas": [{ "name", "key", "sessions", "purchases", "cvr" }] }
    }
  },
  "bottlenecks": [{ "rank", "title", "stage", "segment", "gap", "impact_sessions" }, ...]
}
```

### summary-data.json / weekly-summary.json

```json
{ "monthly": [{ "month": "2026-03", "sessions": N, "purchases": N, "cvr": 0.0N }], "targets": { "monthly_cvr": 0.018, "annual_cvr": 0.020 } }
{ "weekly": [{ "week": "202614", "sessions": N, "purchases": N, "cvr": 0.0N }] }
```

---

## 6. エリア定義（20セグメント）

| キー | 表示名 | VELTRAパス | GA4フィルタ |
|------|--------|-----------|------------|
| `hawaii` | ハワイ | `/jp/hawaii/` | `/hawaii/` |
| `bali` | バリ | `/jp/asia/indonesia/bali/` | `/bali/` |
| `guam` | グアム | `/jp/beach_resort/guam/` | `/guam/` |
| `cebu` | セブ | `/jp/asia/philippines/cebu/` | `/cebu/` |
| `singapore` | シンガポール | `/jp/asia/singapore/` | `/singapore/` |
| `taiwan` | 台湾 | `/jp/asia/taiwan/` | `/taiwan/` |
| `hongkong` | 香港・マカオ | `/jp/asia/hongkong/` | `/hongkong/` |
| `thailand` | タイ | `/jp/asia/thailand/` | `/thailand/` |
| `vietnam` | ベトナム | `/jp/asia/vietnam/` | `/vietnam/` |
| `europe` | ヨーロッパ | `/jp/europe/` | `/europe/` |
| `australia` | オーストラリア | `/jp/oceania/australia/` | `/australia/` |
| `okinawa` | 沖縄 | `/jp/japan/okinawa/` | `/okinawa/` |
| `tokyo` | 東京 | `/jp/japan/tokyo/` | `/tokyo/` |
| `osaka` | 大阪 | `/jp/japan/osaka/` | `/osaka/` |
| `kyoto` | 京都 | `/jp/japan/kyoto/` | `/kyoto/` |
| `hokkaido` | 北海道 | `/jp/japan/hokkaido/` | `/hokkaido/` |
| `kanto` | 関東 | `/jp/japan/kanto/` | `/kanto/` |
| `kyushu` | 九州 | `/jp/japan/kyushu/` | `/kyushu/` |
| `ishigaki_miyako` | 石垣島・宮古島 | `/jp/japan/okinawa/ishigaki_yaeyama/` | `/ishigaki/` or `/miyako/` |
| `other` | その他 | — | 上記以外 |

---

## 7. AIモデル使い分けガイド

| タスク | モデル | 理由 |
|--------|--------|------|
| スキャフォールド生成 | **Python スクリプト** | 定型処理、AIコスト不要 |
| content.json スケルトン生成 | **Python スクリプト** | `--skeleton` で自動生成、AIコスト不要 |
| GA4 クエリ実行 | **Sonnet** | MCP操作は定型、判断不要 |
| data.json 組み立て | **Sonnet** | クエリ結果の整形 |
| summary/weekly JSON 更新 | **Sonnet** | 追記のみ |
| ボトルネック分析（ランキング） | **Opus** | セグメント間の相対比較に判断力が必要 |
| スケルトンの TODO 埋め（仮説・施策・競合） | **Opus** | ドメイン知識 + 創造性（ただし記述量は約77%削減済み） |
| プロトタイプ設計 | **Opus** | UI/UX判断（`before_text/after_text` で記述量1/10） |
| CSS / レイアウト修正 | **Sonnet** | 定型作業 |
| git commit & push | **Sonnet** | 定型 |

**コスト最適化**: Phase 1 は全て Sonnet。Phase 2 のスケルトン生成は Python スクリプト、TODO 埋めのみ Opus。Phase 3 は Sonnet。

---

## 8. 品質チェックリスト

- [ ] data.json の `baseline.sessions` と KPI セクションの値が一致
- [ ] ファネル通過率の用語が統一（①→② 流入→AC到達 / ②→③ AC到達→検討 / ③→④ 検討→意向 / ④→⑤ 意向→完了）
- [ ] 「仮想データ」表記が残っていない
- [ ] 全エリア（20件）のファネルデータが入っている
- [ ] reports-index.json に新しい週が追加され、**date_start/date_end が対象週の月〜日**になっている（ローリング期間ではない）
- [ ] reports-index.json の week_label が正しい（例: `W14（3/30〜4/5）`）
- [ ] reports-index.json の weeks が **時系列順（古い→新しい）** に並んでいる（最新が末尾）
- [ ] `python3 scripts/validate-report.py` がエラー0件で通る
- [ ] weekly-summary.json に新しい週が追加されている
- [ ] archive-meta.json の updatedAt が更新されている
- [ ] w{XX}/index.html のベースライン数値が data.json と一致
- [ ] w{XX}/index.html の「分析対象データ」日付がローリング期間（例: 3/9〜4/5）と一致
- [ ] プロトタイプがVELTRAデザインシステム準拠（`#1B82C5` blue CTA）
- [ ] 競合分析のファビコンが正しい URL
- [ ] 全10件の content.json に `behavior_context` が存在（`estimated_action` 非空、`evidence` 2件以上、`page_role_check` 非空、`subtraction_check` 非空）
- [ ] 全90施策に `implementation_check` が記入されている（status が new/partial/already_exists/superseded のいずれか）
- [ ] `already_exists` / `superseded` の施策には代替案が提示されている
- [ ] 全90施策に `feasibility` が記入されている（effort, constraints, quick_wins）
- [ ] `python3 scripts/audit-actions.py --week {YYYY}-w{WW}` が重複0件で通る

---

## 9. 週次スケジュール

**毎週月曜 AM 4:00 JST に自動実行**（土曜データを1日寝かせて確定させるため）

```
Phase 1 (Sonnet): スキャフォールド → GA4 クエリ → data.json 生成    ~15分
Phase 2 (Opus):   ボトルネック分析 → content.json ×10 生成（並列）    ~20分
Phase 3 (Sonnet): commit & push → Vercel自動デプロイ                  ~5分
```

Claude Code の `schedule` スキルで設定:
```
毎週日曜 04:00 JST に playbook.md を読み、Phase 1→2→3 を順次実行
```

---

---

## 10. アカウント構成と実行テンプレート

### アカウント構成

| アカウント | 用途 | モデル | 特徴 |
|------------|------|--------|------|
| **アカウントA**（ベルトラ） | GA4 MCP接続・データ取得 | Sonnet | GA4 MCP に直接接続可 |
| **アカウントB**（分析） | 分析・コンテンツ生成・デプロイ | Opus / Sonnet 切替 | GA4 MCP 接続不可 |

### Phase別 指示テンプレート（コピペ用）

**Phase 1（アカウントA）**:
```
playbook.md を読んでください。
W{XX}（{date_start}〜{date_end}）のデータを取得してください。
Phase 1 の手順に従い、Q1〜Q10 を実行して data.json を生成し、
summary-data.json / weekly-summary.json / reports-index.json も更新して push してください。
```

**Phase 2（アカウントB）**:
```
playbook.md を読んでください。
git pull して最新の data.json を取得してください。
W{XX} の Phase 2 を実行してください。
ボトルネック10件の bottleneck-{1-10}-content.json 生成 → commit & push までお願いします。
※ report.html が data.json から週次サマリーを動的描画するため index.html 生成は不要です。
※ content.json は 2-3 ファイルずつ並列 Agent で生成してタイムアウトを回避してください。

【重要】施策化レビューレイヤー:
1. known-implementations.json を最初に読み、実装済み機能を把握してください
2. feasibility-constraints.json を読み、制約チェックリストを把握してください
3. 各 action に implementation_check と feasibility を記入してください
4. status が "already_exists" の施策は代替案に差し替えてください
5. 完了後 python3 scripts/audit-actions.py --week W{XX} で重複チェックを実行してください
```

**修正対応（アカウントB）**:
```
playbook.md を読んでください。
https://v2-veltra-cvr.vercel.app/reports/{YYYY}-w{WW}/ を確認して、
{具体的な修正内容} を対応してください。
```

### トラブルシューティング

| 問題 | 原因 | 対処 |
|------|------|------|
| アカウントAのAPI制限 | GA4クエリレート制限 | 数時間待って再試行 |
| GA4 MCP 接続エラー | Proxy/認証問題 | アカウントAのセッションを再起動 |
| git push rejected | リモートに先行コミット | `git pull --rebase` → push |
| Vercel デプロイ失敗 | HTML/JSON構文エラー | ブラウザコンソールで確認、修正して再push |
| 数値不整合 | data.json とHTML内ハードコードの乖離 | data.json を正とし、HTMLを修正 |
| 「仮想データ」表記残り | 古いHTML | grep で検索、置換 |
| content.json prototype不足 | 施策にprototype未設定 | `python3 -c "import json; ..."` で確認 |

---

## 11. データファイルのメンテナンス

### known-implementations.json の更新

VELTRAサイトに新機能がリリースされた場合、`known-implementations.json` に追記する。
これにより、次回以降のボトルネック分析で重複施策の自動検出が可能になる。

**更新タイミング**:
- サイトに新機能がリリースされたとき
- ABテストの結果が確定し、本番適用されたとき
- 月次で棚卸し（過去1ヶ月のリリースノートを確認）

**更新手順**:
1. `known-implementations.json` を開く
2. 該当カテゴリの `implementations` 配列に追加:
   ```json
   {
     "title": "機能名",
     "date": "YYYY-MM",
     "keywords": ["キーワード1", "キーワード2"],
     "detail": "実装詳細（省略可）"
   }
   ```
3. `keywords` は施策タイトル・説明文に出現しうる語を選ぶ（2語以上推奨）
4. 汎用的すぎるキーワード（`scripts/audit-actions.py` の `GENERIC_KEYWORDS` 参照）は避ける
5. 動作確認: `python3 scripts/audit-actions.py --week {最新週} --report-only`

### feasibility-constraints.json の更新

新たな制約パターンが判明した場合に追記する。

**更新時の注意**:
- `trigger_keywords` は具体的な複合語を使う（「空き状況」「パートナーAPI」等）
- 単独で偽陽性を起こす汎用語（「API」「連携」「空き」等）は避ける
- 新規追加後は `python3 scripts/audit-actions.py --week {最新週} --report-only` で影響確認

### audit-actions.py の実行タイミング

| タイミング | コマンド | 目的 |
|-----------|---------|------|
| Phase 2 完了後 | `python3 scripts/audit-actions.py --week {YYYY}-w{WW} --auto-fill` | 自動記入+レポート |
| 手動レビュー後 | `python3 scripts/audit-actions.py --week {YYYY}-w{WW} --report-only` | 最終確認 |
| known-implementations.json 更新後 | `python3 scripts/audit-actions.py --week {最新週} --report-only` | 回帰チェック |

---

*v2 / 2026年4月 / 統合版*
