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

## 🔄 引き継ぎ：CVR目標設定タスク（2026-04-08時点）

### 背景
現在のダッシュボード（`reports-index.json` / `summary-data.json`）に記載されている目標CVR値：
- `monthly_cvr: 0.018`（1.8%）
- `annual_cvr: 0.020`（2.0%）

→ **根拠なしのプレースホルダー**。実際の事業目標から逆算した値に置き換える作業中。

### 確認済み実績データ（GA4）

| 期間 | セッション | 購入件数 | GMV |
|---|---|---|---|
| 2025 Q1（Jan–Mar） | 8,868,607 | 140,862 | 未取得 |
| 2026-01 | 3,086,509 | 41,717 | ¥284M |
| 2026-02 | 3,069,036 | 43,339 | ¥289M |
| 2026-03 | 3,239,652 | 47,903 | ¥303M |
| 2026-04（1–7日） | 739,867 | 10,851 | ¥68M |

- **現状CVR（2026-03）**: 1.48%
- **GA4 purchaseRevenue = GMV**（ユーザー確認済み）
- **平均単価**: ¥6,590/件（Q1平均）

### 事業目標（社内資料より）

- **Div TOTAL Revenue Base G5**: ¥4,080M（YoY +11%）
- **Div TOTAL Revenue Minimum G3**: ¥3,930M（YoY +7%）
- **2025年実績**: ¥3,665M

### 逆算した目標CVR（暫定）

| シナリオ | CVR | 現状比 |
|---|---|---|
| G3 Minimum達成 | 1.84% | +0.37pp |
| G5 Base達成 | 1.90% | +0.43pp |
| 現実的5月末目標（+0.5pp） | 1.97% | +0.50pp |

### 次セッションでやること

1. **GA4 MCP で2025年フル年の月次データを取得**
   ```json
   {
     "property_id": "347074845",
     "date_ranges": [{"start_date": "2025-01-01", "end_date": "2025-12-31"}],
     "dimensions": ["month"],
     "metrics": ["sessions", "transactions", "purchaseRevenue"]
   }
   ```
2. 2025年の月別セッション × 季節係数で2026年フル年セッションを予測
3. 目標CVRを確定し、以下のファイルを更新：
   - `reports-index.json` の `targets`
   - `summary-data.json` の `targets`
   - `docs/playbook.md` に目標根拠セクションを追加
   - `index.html` のラベル（「月次目標CVR」→「目標CVR（5月末）」など）

### 目標値の方向性（ユーザーと合意中）
- **ムーンショット（年間）**: 事業目標（G5）達成に必要なCVR ≈ **1.9–2.0%**
- **現実的目標（5月末）**: 現状+0.5pp ≈ **2.0%**
- ※両者が近い数値になるため、ムーンショットをより高い水準（例：2.5%）にするか検討中
