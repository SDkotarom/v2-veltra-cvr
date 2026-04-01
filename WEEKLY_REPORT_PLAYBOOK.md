# WEEKLY REPORT PLAYBOOK

対象週: 2026-w15 として以下を実行してください。

## ルール
- 確認不要。出力はファイルのみ。説明文不要。
- Property ID: 347074845
- date_range: start_date="28daysAgo", end_date="yesterday"
- エラーが出たクエリはスキップし、該当フィールドをnullにする

## week_idとラベルの計算ルール
- week_idは「28daysAgo〜yesterdayが実際にカバーする期間」に対応する週番号
- date_startは28daysAgoの実際の日付、date_endはyesterdayの実際の日付
- 例：実行日が4/1なら date_start=2026-03-03、date_end=2026-03-31、week_id=2026-w14
- 「対象週」として渡されたweek_idをそのまま使わない。必ず実際のデータ期間から計算すること

## 取得するクエリ（8本）

### Query 1: ベースライン
dimensions: []
metrics: [sessions, totalUsers, eventCount]
dimensionFilter: eventName IN [session_start, ac_page_reach, GA4_vtjp_ex_yokka_view_booking_calendar, form_start, purchase]

### Query 2: チャネル別ファネル
dimensions: [sessionDefaultChannelGroup, eventName]
metrics: [eventCount, totalUsers]
dimensionFilter: eventName IN [session_start, ac_page_reach, GA4_vtjp_ex_yokka_view_booking_calendar, form_start, purchase]

### Query 3: デバイス別ファネル
dimensions: [deviceCategory, eventName]
metrics: [eventCount, totalUsers]
dimensionFilter: eventName IN [session_start, ac_page_reach, GA4_vtjp_ex_yokka_view_booking_calendar, form_start, purchase]

### Query 4: 新規/リピーター別
dimensions: [newVsReturning, eventName]
metrics: [eventCount, totalUsers]
dimensionFilter: eventName IN [session_start, ac_page_reach, GA4_vtjp_ex_yokka_view_booking_calendar, form_start, purchase]

### Query 5: エリア別（sessionsとpurchasesは別クエリで取得）
5a: dimensions: [landingPage], metrics: [sessions]
5b: dimensions: [landingPage], metrics: [ecommercePurchases]
※ sessionsとlandingPageを同一クエリに入れると不正確なため必ず分離
※ 注意: landingPagePath は無効。正しいディメンション名は landingPage

### Query 6: チャネル × デバイス
dimensions: [sessionDefaultChannelGroup, deviceCategory, eventName]
metrics: [eventCount, totalUsers]
dimensionFilter: eventName IN [session_start, ac_page_reach, GA4_vtjp_ex_yokka_view_booking_calendar, form_start, purchase]

### Query 7: チャネル × 新規/リピーター
dimensions: [sessionDefaultChannelGroup, newVsReturning, eventName]
metrics: [eventCount, totalUsers]
dimensionFilter: eventName IN [session_start, ac_page_reach, GA4_vtjp_ex_yokka_view_booking_calendar, form_start, purchase]

### Query 8: エリア × デバイス（sessionsのみ）
dimensions: [landingPage, deviceCategory]
metrics: [sessions]
※ 注意: landingPagePath は無効。正しいディメンション名は landingPage

## data.jsonの出力スキーマ

reports/{YEAR}-w{WEEK}/data.json に保存してください。

```json
{
  "meta": {
    "week_id": "2026-w15",
    "week_label": "26年4月 Week2（4/6〜4/12）",
    "date_start": "2026-04-06",
    "date_end": "2026-04-12",
    "data_period": "28daysAgo ~ yesterday",
    "generated_at": "<ISO8601>",
    "property_id": "347074845"
  },
  "baseline": {
    "sessions": "<number>",
    "purchases": "<number>",
    "cvr": "<purchases/sessions>",
    "funnel": {
      "session_start_users": "<totalUsers of session_start>",
      "ac_page_reach_users": "<totalUsers of ac_page_reach>",
      "calendar_view": "<eventCount of GA4_vtjp_ex_yokka_view_booking_calendar>",
      "form_start": "<eventCount of form_start>",
      "purchase": "<eventCount of purchase>"
    },
    "conversion_rates": {
      "1_to_2": "<ac_page_reach_users / session_start_users>",
      "2_to_3": "<calendar_view / ac_page_reach_users>",
      "3_to_4": "<form_start / calendar_view>",
      "4_to_5": "<purchase / form_start>"
    }
  },
  "segments": {
    "channel": {
      "<channel_name>": {
        "sessions": "<number>",
        "share": "<sessions/total_sessions>",
        "funnel": { "ac_page_reach_users": "N", "calendar_view": "N", "form_start": "N", "purchase": "N" },
        "rates": { "1_to_2": "N", "2_to_3": "N", "3_to_4": "N", "4_to_5": "N", "cvr": "N" }
      }
    },
    "device": {},
    "new_returning": {},
    "area": {
      "<area_slug>": {
        "sessions": "<number>",
        "share": "<number>",
        "purchases": "<number>",
        "cvr": "<number>"
      }
    },
    "channel_x_device": {
      "<channel>_<device>": {
        "sessions": "<number>",
        "funnel": { "ac_page_reach_users": "N", "calendar_view": "N", "form_start": "N", "purchase": "N" },
        "rates": { "1_to_2": "N", "2_to_3": "N", "3_to_4": "N", "4_to_5": "N", "cvr": "N" }
      }
    },
    "channel_x_new_returning": {}
  },
  "bottlenecks": []
}
```

## エリアの判定ルール
- /hawaii/ /oahu/ /maui/ 含む → "hawaii"
- /bali/ 含む → "bali"
- /europe/ /paris/ /rome/ /barcelona/ 等含む → "europe"
- /japan/ /tokyo/ /osaka/ 含む → "japan"
- それ以外 → "other"

## 完了後の作業
生成したreports/{YEAR}-w{WEEK}/data.json に加え、
以下のファイルもリポジトリに保存してください。

1. WEEKLY_REPORT_PLAYBOOK.md（このファイル全体）を
   リポジトリルートに保存

2. git add WEEKLY_REPORT_PLAYBOOK.md reports/{YEAR}-w{WEEK}/data.json
3. git commit -m "feat: add w{WEEK} data.json + update playbook"
4. git push origin main
