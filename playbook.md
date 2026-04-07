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
├── playbook.md                 ← このファイル（運用マニュアル）
├── veltra-design-system.md     ← VELTRAサイトのデザインルール
├── veltra-url-structure.md     ← VELTRA URL階層（エリア定義）
├── prd-template.md             ← PRDテンプレート（汎用）
├── scripts/
│   └── generate-week.py        ← 週次スキャフォールド（ディレクトリ・JSONスケルトン生成）
├── auth.js / nav.js / funnel-def.js  ← 共通JS
├── index.html                  ← ダッシュボード
├── summary-data.json           ← 月次KPI（24ヶ月）
├── weekly-summary.json         ← 週次KPI（66週〜）
├── reports-index.json          ← レポート一覧メタデータ
├── archive-meta.json           ← 最終更新タイムスタンプ
└── reports/{YYYY}-w{WW}/
    ├── data.json               ← GA4実データ（ファネル・セグメント・ボトルネック）
    ├── index.html              ← 週次サマリー
    └── bottleneck-{1-10}.html  ← ボトルネック詳細
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
5. summary-data.json / weekly-summary.json も更新
6. git commit & push to main
```

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

| ファイル | 更新内容 |
|----------|---------|
| `reports/{W}/data.json` | Q1〜Q10 の全結果 |
| `summary-data.json` | 当月の月次KPI追記 |
| `weekly-summary.json` | 当週の週次KPI追記/更新 |
| `reports-index.json` | **新しい週のエントリ追加（week_label, date_start, date_end を正しい週日付で）** |
| `archive-meta.json` | updatedAt タイムスタンプ更新 |

> ⚠️ `reports-index.json` の `date_start` / `date_end` は対象週の月〜日（例: 3/30〜4/5）。
> ローリング期間（28日）ではないので注意。

### Phase 2: 分析 & HTML生成（Opus）

1. **ボトルネック特定**: `data.json` のセグメント間比較から、インパクト順（sessions × 乖離率）で10件ランキング
2. **#1 フル分析**: 仮説×3 → 打ち手×3（仮説ごと）→ プロトタイプ Before/After → 競合比較6社
3. **#2〜#10**: 仮説×3 + 打ち手×3 + 競合比較
4. **HTML生成**: アコーディオン型ドリルダウンUI（仮説 → 打ち手 → プロトタイプ）

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
| GA4 クエリ実行 | **Sonnet** | MCP操作は定型、判断不要 |
| data.json 組み立て | **Sonnet** | クエリ結果の整形 |
| summary/weekly JSON 更新 | **Sonnet** | 追記のみ |
| ボトルネック分析（ランキング） | **Opus** | セグメント間の相対比較に判断力が必要 |
| 仮説生成 | **Opus** | ドメイン知識 + 創造性 |
| 施策立案 | **Opus** | デザインシステム理解 + 実装提案 |
| プロトタイプ設計 | **Opus** | UI/UX判断 |
| 競合比較 | **Opus** | 市場理解 |
| HTML テンプレート生成 | **Sonnet** | 定型HTML、Opusは過剰 |
| CSS / レイアウト修正 | **Sonnet** | 定型作業 |
| git commit & push | **Sonnet** | 定型 |

**コスト最適化**: Phase 1 は全て Sonnet。Phase 2 の分析部分のみ Opus。Phase 3 は Sonnet。

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

---

## 9. 週次スケジュール

**毎週日曜 AM 4:00 JST に自動実行**

```
Phase 1 (Sonnet): スキャフォールド → GA4 クエリ → data.json 生成    ~15分
Phase 2 (Opus):   ボトルネック分析 → HTML生成                        ~30分
Phase 3 (Sonnet): commit & push → Vercel自動デプロイ                  ~5分
```

Claude Code の `schedule` スキルで設定:
```
毎週日曜 04:00 JST に playbook.md を読み、Phase 1→2→3 を順次実行
```

---

*v2 / 2026年4月 / 統合版*
