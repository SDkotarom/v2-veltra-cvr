# 「その他」エリア内訳データ取得指示書

## 概要

`reports/2026-w14/data.json` の `segments.area.other` に `sub_areas` 配列を追加する。
「その他」（703,686 sessions / CVR 3.50%）の内訳上位5エリアを特定してダッシュボードに表示する。

---

## GA4 クエリ条件

- **Property ID:** `347074845`
- **期間:** `2026-03-03` ～ `2026-03-31`（28日間、他エリアと同一期間）

---

## クエリ方針

### Step 1: 「その他」に含まれるセッションの定義

以下の19エリアに**該当しない**セッションが「その他」:

| 除外エリア | page_path フィルタ |
|---|---|
| hawaii | `/hawaii/` |
| bali | `/bali/` |
| guam | `/guam/` |
| cebu | `/cebu/` |
| singapore | `/singapore/` |
| taiwan | `/taipei/` or `/taiwan/` |
| hongkong | `/hongkong/` or `/macau/` |
| thailand | `/bangkok/` or `/thailand/` or `/phuket/` |
| vietnam | `/vietnam/` or `/danang/` or `/hochiminh/` |
| europe | `/paris/` or `/london/` or `/rome/` or `/barcelona/` |
| australia | `/australia/` or `/cairns/` or `/goldcoast/` |
| okinawa | `/okinawa/` |
| tokyo | `/tokyo/` |
| osaka | `/osaka/` |
| kyoto | `/kyoto/` |
| hokkaido | `/hokkaido/` |
| kanto | `/kanto/` |
| kyushu | `/kyushu/` or `/fukuoka/` |
| ishigaki_miyako | `/ishigaki/` or `/miyako/` |

### Step 2: 「その他」内のセッションをエリア別に集計

「その他」に分類されたセッションの中で、**landingPage（または pagePath）の上位ディレクトリ**でグルーピングし、sessions 数の多い順に上位5つを取得する。

例えば `/cancun/`, `/maldives/`, `/korea/` などが候補。

### Step 3: 各サブエリアの指標取得

上位5サブエリアそれぞれについて:

| フィールド | 定義 |
|---|---|
| `name` | エリア表示名（日本語） |
| `key` | エリアキー（英数小文字） |
| `sessions` | セッション数 |
| `purchases` | purchase イベント数 |
| `cvr` | purchases / sessions |

---

## 出力 JSON フォーマット

`data.json` の `segments.area.other` に `sub_areas` 配列を追加:

```json
{
  "other": {
    "sessions": 703686,
    "share": 0.3568,
    "purchases": 24601,
    "cvr": 0.03496,
    "funnel": { ... },
    "rates": { ... },
    "sub_areas": [
      {
        "name": "カンクン",
        "key": "cancun",
        "sessions": 45000,
        "purchases": 1200,
        "cvr": 0.02667
      },
      {
        "name": "モルディブ",
        "key": "maldives",
        "sessions": 38000,
        "purchases": 950,
        "cvr": 0.025
      },
      {
        "name": "韓国",
        "key": "korea",
        "sessions": 35000,
        "purchases": 800,
        "cvr": 0.02286
      },
      {
        "name": "ドバイ",
        "key": "dubai",
        "sessions": 28000,
        "purchases": 700,
        "cvr": 0.025
      },
      {
        "name": "ニューヨーク",
        "key": "newyork",
        "sessions": 25000,
        "purchases": 600,
        "cvr": 0.024
      }
    ]
  }
}
```

※ 上記の name/key/数値は例です。実際のGA4データに基づいて差し替えてください。

---

## 差し替え手順

1. 上記クエリを実行して `sub_areas` 配列を生成
2. `reports/2026-w14/data.json` を開く
3. `segments.area.other` に `sub_areas` フィールドを追加
4. git commit & push to main

差し替え後、ダッシュボードのエリアタブで「その他」行の「▶ 内訳」をクリックすると上位5件が展開表示されます。

---

## 参考: 全体ベースライン

```
全体CVR: 1.46% (0.014568)
```

sub_areas の CVR をこの値と比較して、ダッシュボード上で ±X% が自動表示されます。
