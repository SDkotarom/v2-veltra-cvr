# CLAUDE.md — このプロジェクトでのAIアシスタント設定

> **新しいセッション開始時に必ずこのファイルを読むこと。**
> 運用マニュアル全体は `docs/playbook.md` を参照。

---

## GA4 MCP 接続について

このプロジェクトでは **GA4 MCP ツールが自動的に利用可能**です。

**セッション開始時の手順（必須）:**

```
ToolSearch で "run_report" を検索 → mcp__*__run_report ツールを取得
```

- 認証情報（サービスアカウントJSON、gcloud ADC、API Key）は**不要**
- Python SDK、curl、gcloud コマンドは**使わない**
- MCP ツール名は `mcp__<UUID>__run_report` 形式（UUIDはセッションごとに変わる場合がある）

**正しい呼び出し例:**

```json
{
  "property_id": "347074845",
  "date_ranges": [{"start_date": "2026-03-09", "end_date": "2026-04-05"}],
  "dimensions": [],
  "metrics": ["sessions", "activeUsers"]
}
```

**よくある失敗パターン（やってはいけないこと）:**

- `python3 -c "from google.analytics.data_v1beta import ..."` → SDK未認証でエラー
- `gcloud auth application-default login` → gcloudは未インストール
- 「認証情報を貼り付けてください」とユーザーに聞く → 不要、MCPで直接接続可能

---

## 基本情報

- **GA4 Property ID**: `347074845`
- **Vercel URL**: https://v2-veltra-cvr.vercel.app/
- **開発ブランチ規則**: `claude/<task>-<hash>` 形式で作業し、完了後 push

---

## よく使うクエリパターン

### ベースラインファネル（28日間）
```python
# dimensions=[], metrics=["sessions","activeUsers","purchaseRevenue"]
# dimension_filter で pagePath/eventName を切り替えて各ステップ取得
```

### エリア別（landingPage ディメンション）
```python
# dimensions=["landingPage"], limit=10000
# Python で area_key に集計後 data.json に格納
```

詳細な手順は `docs/playbook.md` のセクション4「Phase 1: データ取得」を参照。

---

## KPIダッシュボード（/kpi.html）更新漏れ防止

週次更新時にまず `summary-data.json` の `monthly` 配列を当月値で上書きする（他ファイルと同じ Phase 1 ステップ）。加えて **KPI ダッシュボード固有の更新**は以下：

| 頻度 | ファイル | 対象 |
|------|---------|------|
| 週次 | `summary-data.json` | `monthly[].{sessions,purchases,cvr}` — 当月速報 |
| **月次確定時** | `summary-data.json` | `monthly_notes["YYYY-MM"].{summary,good,bad}` — 前月の分析コメント |
| **四半期確定時** | `summary-data.json` | `targets.{baseline_cvr, monthly_cvr, annual_cvr, stretch_cvr, stretch_revenue*}` を再計算 |
| **四半期確定時** | `kpi.html` | arrow-row の 3 つのハードコード CVR 表示値（`biz-cvr-current / target / stretch`）+ 進捗ラベル + stretch-note |

完全な手順・分析コメントのテンプレート・計算式は `docs/playbook.md` セクション11「KPIダッシュボード（/kpi.html）の更新」を参照。

---

## ボトルネックのタイトル作成ルール（Phase 1 / Phase 2 共通）

`data.json` と `bottleneck-N-content.json` のタイトルは **「誰が・どこで・どう困っているか」を1文で描く課題目線**で書く。数値（%・pp）は `tags` / `deviation` / `description_html` が担当するのでタイトル枠では繰り返さない。

❌ NG: `新規ユーザーの意向→完了率が 51.1%（全体 76.9% から -25.9pp）`
✅ OK: `新規ユーザーが『長いフォーム＋最終価格の不意打ち』で決済直前に諦めている`

タイトル書き換えは **Step 1.5（behavior_context）完了後に Step 1.6 として必ず実施**し、以下3箇所を同時に更新する：
- `reports/{W}/data.json` の `bottlenecks[].title`
- `reports/{W}/bottleneck-N-content.json` の `title`
- `reports/{W}/index.html`（Phase 2.9 の週次サマリー）の Action 2 Top3 `.asl-title` ハードコード箇所

詳細ルールは `docs/playbook.md` Phase 2 Step 1.6 を参照。

---

## YoY/前年比較の作法（過小評価・誤読を防ぐ）

CVR / セッション等の年次比較を書くときに**必ず守る 3 原則**:

### 1. matched 同期で比較する（通年平均は使わない）

❌ NG: `2026 通年平均 1.27%` ← 2026 が Jan-May しかない場合、7-8月（高 CVR 月）が含まれないため過小評価される
✅ OK: `2026 Jan-May 1.331% vs 2025 Jan-May 1.542%`（同期同月数の volume-weighted CVR で比較）

### 2. ベルトラの本当のピーク月は 7-8月 と 12-1月

| 区分 | 月 | 特性 |
|------|-----|------|
| 夏休み・お盆 | **7-8月** | 年間最重要繁忙期、CVR 1.48〜1.54%（2024-25 実績） |
| 年末年始 | **12-1月** | 第二繁忙期、CVR 1.40〜1.61%（2024 12 月が 1.614% で年間最高） |
| 中位需要 | 4-6月、9-10月 | 通常水準、CVR 1.40〜1.55% |
| 谷 | 2-3月、11月 | やや低め、CVR 1.35〜1.50% |
| 最弱 | 5月（GW 後半は実質予約閑散） | 1.10〜1.20% 帯（2024 1.177%） |

通年平均で「2025 が peak year」と言いがちだが、<strong>繁忙期で見ると 2025-12 で既に -0.20pp 崩壊が始まっていた</strong>。「平均が良い年」 ≠ 「全部良い年」。

### 3. 「2026 はまだ来ていない月」を考慮する

- 2026 5月時点で「2026 全体が 2024 水準まで後退」と断じるのは早すぎる
- 残り 7-12月（うち 7-8月は最重要繁忙期）で挽回可能か / さらに崩れるかが運命の分岐点
- 結論は「(matched) 同期で見ると -0.XXpp、繁忙期の test はまだ来ていない」とニュアンス付き

### 適用先

スポット分析（`spot/2026-gw-cvr-decline.html` 等）、W サマリー（`reports/{W}/index.html`）、KPI ダッシュボード（`kpi.html`）、月次 notes（`summary-data.json` の `monthly_notes`）すべてでこの 3 原則を守る。
