# W14 データ再取得指示（日付範囲修正）

## 変更理由
W14 の正しい日付範囲は `2026-03-09 〜 2026-04-05`（4/5を含む直近28日間）。
現在のデータは `2026-03-03 〜 2026-03-31` で取得されているため、再取得が必要。

## GA4 クエリ共通条件

- **Property ID**: `347074845`
- **期間**: `2026-03-09` 〜 `2026-04-05`（28日間）
- **Q10のみ**: 今週 `2026-03-30 〜 2026-04-05`（7日）+ 先週 `2026-03-23 〜 2026-03-29`（7日）

## 実行するクエリ（10本）

### Q1: ベースラインファネル
- dimensions: なし
- metrics: sessions, 各ファネルイベント（session_start_users, ac_page_reach_users, calendar_view, form_start, purchase）
- → `data.json` の `baseline` に格納

### Q2: チャネル別セグメント
- dimensions: `sessionDefaultChannelGroup`
- metrics: 同上
- → `segments.channel`

### Q3: デバイス別セグメント
- dimensions: `deviceCategory`
- metrics: 同上
- → `segments.device`

### Q4: 新規/リピーター
- dimensions: `newVsReturning`
- metrics: 同上
- → `segments.new_returning`

### Q5: チャネル×デバイス
- dimensions: `sessionDefaultChannelGroup` + `deviceCategory`
- metrics: 同上
- → `segments.channel_device`

### Q6: チャネル×新規リピーター
- dimensions: `sessionDefaultChannelGroup` + `newVsReturning`
- metrics: 同上
- → `segments.channel_new_returning`

### Q7: エリア別ファネル（20エリア）
- landingPage フィルタで20エリアに分割（エリア定義は `playbook.md` セクション6参照）
- metrics: sessions, 各ファネルイベント
- → `segments.area`（各エリアに `funnel` + `rates` を含める）

### Q8: 「その他」内訳（上位5）
- Q7の19エリアに該当しないセッションの中から、landingPage上位5を特定
- → `segments.area.other.sub_areas`

### Q9: サマリーデータ
- 2026年3月分の月次データ（sessions, purchases, cvr）を `summary-data.json` に追記
- 2026-W14 の週次データを `weekly-summary.json` に追記/更新

### Q10: 7日ファネル（WoW比較用）
- 今週（3/30〜4/5）と先週（3/23〜3/29）のファネルをそれぞれ取得
- → `data.json` の `funnel_7d` に格納
- `conversion_rates.wow_pp` に差分（pp）を計算して格納

## data.json の meta 更新

```json
"meta": {
  "week_id": "2026-w14",
  "date_start": "2026-03-30",
  "date_end": "2026-04-05",
  "rolling_start": "2026-03-09",
  "rolling_end": "2026-04-05",
  "ga4_property": "347074845",
  "generated_at": "2026-04-06T..."
}
```

## 出力

`playbook.md` セクション5 のスキーマに従って `data.json` を丸ごと再生成してください。
`summary-data.json` と `weekly-summary.json` も更新してください。

完了したら git push to main。
