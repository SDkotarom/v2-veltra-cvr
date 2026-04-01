# 引き継ぎメモ: エリア別ファネルデータ取得

作成: 2026-04-01  
対応者: VELTRAアカウント（GA4 MCP接続可能な環境）  
優先度: 中（次回 data.json 更新時に対応）

---

## 背景・現状の問題

`reports/2026-w14/data.json` の `segments.area` に  
ファネル段階データ（`funnel` / `rates`）が含まれていない。

現状:
```json
"area": {
  "bali":   { "sessions": 2072,   "purchases": 40,   "cvr": 0.019305 },
  "europe": { "sessions": 34164,  "purchases": 757,  "cvr": 0.022158 },
  "hawaii": { "sessions": 67306,  "purchases": 1706, "cvr": 0.025347 },
  "japan":  { "sessions": 368182, "purchases": 5466, "cvr": 0.014846 },
  "other":  { "sessions": 810249, "purchases": 21265,"cvr": 0.026245 }
}
```

---

## 必要な対応

### GA4クエリ方針
device/channel と同様に、エリアを **page_path フィルタ** で絞り込み、  
ファネルイベントをカウントする。

想定フィルタ条件（実際のURL構造に合わせて確認・修正すること）:

| エリア | page_path フィルタ例 |
|--------|----------------------|
| bali   | `page_path contains "/bali/"` |
| hawaii | `page_path contains "/hawaii/"` |
| europe | `page_path contains "/europe/"` または `/paris/` `/london/` etc. |
| japan  | `page_path contains "/japan/"` |
| other  | 上記以外のセッション |

> ⚠️ 実際のVELTRA URL構造（`/asia/bali/`, `/tours/bali/` 等）を確認の上、  
> フィルタ条件を調整すること。

### 取得すべきファネルイベント（device と同じ）

各エリアについて以下を取得:

| フィールド | GA4イベント |
|------------|-------------|
| `session_start_users` | session_start（ユーザー数） |
| `ac_page_reach_users` | view_item_list または 商品詳細ページ到達 |
| `calendar_view` | select_item または カレンダーUI表示 |
| `form_start` | begin_checkout |
| `purchase` | purchase |

---

## data.json の更新後の目標構造

```json
"area": {
  "bali": {
    "sessions": 2072,
    "share": 0.001616,
    "purchases": 40,
    "cvr": 0.019305,
    "funnel": {
      "session_start_users": 2072,
      "ac_page_reach_users": <GA4から取得>,
      "calendar_view": <GA4から取得>,
      "form_start": <GA4から取得>,
      "purchase": 40
    },
    "rates": {
      "1_to_2": <ac_page_reach_users / session_start_users>,
      "2_to_3": <calendar_view / ac_page_reach_users>,
      "3_to_4": <form_start / calendar_view>,
      "4_to_5": <purchase / form_start>,
      "cvr": 0.019305
    }
  },
  "europe": { ... 同構造 ... },
  "hawaii": { ... 同構造 ... },
  "japan":  { ... 同構造 ... },
  "other":  { ... 同構造 ... }
}
```

---

## 更新後のUI反映

data.json に `funnel` / `rates` が追加された時点で、  
表示コード（index.html `renderSegmentPanels`）は自動的に  
「全ファネル段階表示」に切り替わる実装済み。  
→ 追加のフロント対応は不要。

---

## 確認事項（VELTRAアカウント側で要確認）

1. VELTRAサイトの実際のエリアURLパス構造
2. GA4 でエリア絞り込みに使う dimension（page_path? landing_page?）
3. `ac_page_reach_users` の定義（商品ページ到達イベント名）

---

## 対応ファイル

- `reports/2026-w14/data.json` → segments.area を更新
- （次週以降） 週次生成スクリプトにエリア別ファネル取得を組み込む

