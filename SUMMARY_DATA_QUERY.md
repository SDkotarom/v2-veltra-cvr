# サマリーデータ取得指示書

Property ID: `347074845`
実行日: 2026年4月2日

---

## クエリ1: 月次データ追加（2024年4月〜12月の9ヶ月分）

summary-data.jsonに追加する月次sessions/purchases。

### 実行内容

以下9ヶ月分それぞれでGA4クエリを実行:

```
dimensions: []
metrics: [sessions, ecommercePurchases]
```

| # | startDate | endDate |
|---|-----------|---------|
| 1 | 2024-04-01 | 2024-04-30 |
| 2 | 2024-05-01 | 2024-05-31 |
| 3 | 2024-06-01 | 2024-06-30 |
| 4 | 2024-07-01 | 2024-07-31 |
| 5 | 2024-08-01 | 2024-08-31 |
| 6 | 2024-09-01 | 2024-09-30 |
| 7 | 2024-10-01 | 2024-10-31 |
| 8 | 2024-11-01 | 2024-11-30 |
| 9 | 2024-12-01 | 2024-12-31 |

### 出力

取得したデータを `/summary-data.json` の `monthly` 配列の**先頭**に追加してください。

フォーマット:
```json
{"month": "2024-04", "sessions": <sessions>, "purchases": <ecommercePurchases>, "cvr": <ecommercePurchases / sessions>}
```

既存の2025-01〜2026-03のデータはそのまま残す。結果として2024-04〜2026-03の24ヶ月分になる。

---

## クエリ2: 週次サマリーデータ（2025年1月〜2026年3月）

週次グラフ用の軽量データ。1クエリで全週分取得。

### 実行内容

```
dimensions: [isoYearIsoWeek]
metrics: [sessions, ecommercePurchases]
dateRanges: [{ startDate: "2025-01-01", endDate: "2026-03-31" }]
orderBys: [{ dimension: { dimensionName: "isoYearIsoWeek" }, desc: false }]
```

### 出力

`/weekly-summary.json` を新規作成:

```json
{
  "generated_at": "<ISO8601>",
  "property_id": "347074845",
  "weekly": [
    {"week": "202501", "sessions": <sessions>, "purchases": <ecommercePurchases>, "cvr": <ecommercePurchases / sessions>},
    {"week": "202502", "sessions": ..., "purchases": ..., "cvr": ...},
    ...
  ]
}
```

- `week` はGA4が返す `isoYearIsoWeek` の値をそのまま使用（例: "202501", "202602"）
- `cvr` = `ecommercePurchases / sessions`
- 全行を `week` 昇順で並べる

---

## 完了後

```bash
git add summary-data.json weekly-summary.json
git commit -m "feat: add monthly data 2024-04~12 + weekly summary 2025-2026"
git push origin main
```
