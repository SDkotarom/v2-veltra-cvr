# エリア別ファネルデータ取得指示書

## 概要

`reports/2026-w14/data.json` の `segments.area` にファネル段階データを追加する。
現状はCVRのみ（5エリア）→ **20エリア × 全ファネル段階** に拡充。

---

## GA4 クエリ条件

- **Property ID:** `347074845`
- **期間:** `2026-03-03` ～ `2026-03-31`（28日間）
- **対象:** 全ユーザー（セグメントなし）

---

## 対象エリア（20件）

各エリアは **セッションの landingPage（または pagePath）** でフィルタする。
実際のURL構造に合わせて調整すること。

| # | エリアキー | 表示名 | page_path フィルタ例 |
|---|-----------|--------|---------------------|
| 1 | `hawaii` | ハワイ | `/hawaii/` を含む |
| 2 | `bali` | バリ | `/bali/` を含む |
| 3 | `guam` | グアム | `/guam/` を含む |
| 4 | `cebu` | セブ | `/cebu/` を含む |
| 5 | `singapore` | シンガポール | `/singapore/` を含む |
| 6 | `taiwan` | 台湾 | `/taipei/` or `/taiwan/` を含む |
| 7 | `hongkong` | 香港・マカオ | `/hongkong/` or `/macau/` を含む |
| 8 | `thailand` | タイ | `/bangkok/` or `/thailand/` or `/phuket/` を含む |
| 9 | `vietnam` | ベトナム | `/vietnam/` or `/danang/` or `/hochiminh/` を含む |
| 10 | `europe` | ヨーロッパ | `/paris/` or `/london/` or `/rome/` or `/barcelona/` を含む |
| 11 | `australia` | オーストラリア | `/australia/` or `/cairns/` or `/goldcoast/` を含む |
| 12 | `okinawa` | 沖縄 | `/okinawa/` を含む |
| 13 | `tokyo` | 東京 | `/tokyo/` を含む |
| 14 | `osaka` | 大阪 | `/osaka/` を含む |
| 15 | `kyoto` | 京都 | `/kyoto/` を含む |
| 16 | `hokkaido` | 北海道 | `/hokkaido/` を含む |
| 17 | `kanto` | 関東（東京除く） | `/kanto/` を含む（`/tokyo/` は除外） |
| 18 | `kyushu` | 九州 | `/kyushu/` or `/fukuoka/` を含む |
| 19 | `ishigaki_miyako` | 石垣島・宮古島 | `/ishigaki/` or `/miyako/` を含む |
| 20 | `other` | その他 | 上記いずれにも該当しないセッション |

---

## 各エリアで取得するファネルイベント（5指標）

| # | フィールド名 | 定義 |
|---|-------------|------|
| ① | `session_start_users` | そのエリアの全セッション数 |
| ② | `ac_page_reach_users` | pagePath に `/a/` を含むページへ到達したセッション数 |
| ③ | `calendar_view` | イベント `GA4_vtjp_ex_yokka_view_booking_calendar` の発生セッション数 |
| ④ | `form_start` | pagePath に `/jp/booking` を含むページへ到達したセッション数 |
| ⑤ | `purchase` | イベント `purchase` の発生セッション数 |

---

## 出力 JSON フォーマット

以下の形式で **20エリア分** を出力し、`data.json` の `segments.area` を丸ごと差し替える。

```json
{
  "hawaii": {
    "sessions": 67306,
    "share": 0.0341,
    "purchases": 1706,
    "cvr": 0.025347,
    "funnel": {
      "session_start_users": 67306,
      "ac_page_reach_users": 28500,
      "calendar_view": 21000,
      "form_start": 18200,
      "purchase": 1706
    },
    "rates": {
      "1_to_2": 0.4235,
      "2_to_3": 0.7368,
      "3_to_4": 0.8667,
      "4_to_5": 0.0938,
      "cvr": 0.025347
    }
  },
  "bali": {
    "sessions": 2072,
    "share": 0.00105,
    "purchases": 40,
    "cvr": 0.019305,
    "funnel": {
      "session_start_users": 2072,
      "ac_page_reach_users": null,
      "calendar_view": null,
      "form_start": null,
      "purchase": 40
    },
    "rates": {
      "1_to_2": null,
      "2_to_3": null,
      "3_to_4": null,
      "4_to_5": null,
      "cvr": 0.019305
    }
  }
}
```

### rates の計算式

```
rates.1_to_2 = funnel.ac_page_reach_users / funnel.session_start_users
rates.2_to_3 = funnel.calendar_view / funnel.ac_page_reach_users
rates.3_to_4 = funnel.form_start / funnel.calendar_view
rates.4_to_5 = funnel.purchase / funnel.form_start
rates.cvr    = funnel.purchase / funnel.session_start_users
share        = sessions / 全体セッション数(1,971,836)
```

### 注意事項

- ファネル値が取得できないエリアは `null` を入れる（0ではなく）
- `share` = そのエリアのセッション / 全体セッション数（`baseline.funnel.session_start_users` = 1,971,836）
- rates は小数（%ではない）。例: 42.35% → `0.4235`
- エリアキーは **小文字英数+アンダースコア** で統一

---

## 差し替え手順

1. 上記 JSON を生成
2. `reports/2026-w14/data.json` を開く
3. `"segments"` → `"area"` の中身を丸ごと差し替え
4. git commit & push to main

差し替え後、ダッシュボード（index.html）の「セグメント別 ファネル通過率 > エリア」タブが自動的にファネル全段階表示に切り替わる。

---

## 参考: 現在の全体ベースライン（比較基準）

```
①流入:    1,971,836 sessions
②AC到達:  514,567   (①→② 26.1%)
③検討:    385,959   (②→③ 75.0%)
④意向:    334,312   (③→④ 86.6%)
⑤完了:    42,292    (④→⑤ 12.7%)
全体CVR:  2.14%
```
