# WEEKLY REPORT PLAYBOOK

## プロジェクト基礎知識（新規セッション向け）

### このリポジトリは何か
VELTRAのCVR改善プロジェクト「V2」の週次ボトルネック分析レポートを管理するリポジトリ。
GA4データからファネル×セグメントの転換率を分析し、ボトルネック10件を特定、各件に仮説・打ち手・プロトタイプを生成する。

### リポジトリ構成
```
v2-veltra-cvr/
├── WEEKLY_REPORT_PLAYBOOK.md   ← このファイル。全フェーズの手順書
├── auth.js                     ← 認証（ログインページへリダイレクト）
├── nav.js                      ← レポートページ共通ナビゲーション
├── funnel-def.js               ← ファネル定義
├── prototype-tabs.js           ← プロトタイプタブUI
├── archive-meta.json           ← 過去レポートのメタ情報
├── reports/
│   └── {YEAR}-w{WEEK}/
│       ├── data.json           ← GA4から取得した実データ
│       ├── index.html          ← サマリーページ（ベースライン + #1ハイライト + #2〜#10テーブル）
│       ├── bottleneck-1.html   ← #1フル分析（仮説×3 / 打ち手×3 / プロトタイプ / 競合比較）
│       ├── bottleneck-2.html   ← #2〜#3: プロトあり
│       ├── ...
│       ├── bottleneck-7.html   ← #4〜#7: 仮説+打ち手
│       ├── bottleneck-8.html   ← #8〜#10: プレースホルダー
│       └── bottleneck-10.html
```

### デプロイ
- **ホスティング**: Vercel（mainブランチへのpushで自動デプロイ）
- **URL**: https://v2-veltra-cvr.vercel.app/
- **認証**: auth.jsによるログイン必須（403が返る場合は認証が必要）
- **レポートURL例**: https://v2-veltra-cvr.vercel.app/reports/2026-w14/

### ファネル定義（5段階）
1. **①流入** — session_start（sessions）
2. **②AC到達** — ac_page_reach（商品詳細ページ到達）
3. **③検討** — GA4_vtjp_ex_yokka_view_booking_calendar（カレンダー表示）
4. **④意向** — form_start（予約フォーム開始）
5. **⑤完了** — purchase（購入完了）

### ボトルネック個別ページの分量ルール
- **#1**: フル分析（Tier比較 / 深掘り / 仮説×3 / 打ち手×3 / プロトタイプBefore/After / 競合比較6社 / 検証方法 / チームレビュー欄）
- **#2〜#3**: プロトあり（仮説×3カード / プロトタイプタブ / チームレビュー欄）
- **#4〜#7**: 仮説+打ち手（仮説×3カード / チームレビュー欄 / プロトタイプなし）
- **#8〜#10**: プレースホルダー（主要仮説callout1つのみ / ナビバー）

### CSS・デザイン
- 全ページ共通のCSS変数を各HTMLの`<style>`にインライン記述（外部CSSなし）
- フォント: Noto Sans JP + DM Sans
- カラー: --red:#E8423F / --bg:#f5f4f0 / --card:#fff
- 既存のデザイン・CSS・レイアウトは変更しない

### Git運用
- **メインブランチ**: main（デプロイ対象）
- **作業ブランチ**: claude/* で作業し、完了後mainにマージ
- **コミットメッセージ**: 英語、conventional commits形式（feat: / fix: / refactor:）

### 週次レポート生成の全体フロー
1. **Phase 1 — データ取得**: GA4 APIから8本のクエリを実行 → data.json生成
2. **Phase 2 — HTML生成**: data.jsonを元にindex.html + bottleneck-1〜10.htmlを生成
3. **Phase 3 — コミット・デプロイ**: git add → commit → push origin main（Vercel自動デプロイ）

---

## Phase 1 — データ取得

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

## Phase 2 — HTML生成

### 生成手順
1. `reports/{YEAR}-w{WEEK}/data.json` を読み込む
2. 既存の直近週のHTMLをテンプレートとして参照（CSS・レイアウトを踏襲）
3. index.html を生成（ベースライン + #1ハイライト + #2〜#10サマリーテーブル）
4. bottleneck-1.html を生成（#1フル分析）
5. bottleneck-2〜10.html を分量ルールに従い生成
6. 「仮想データ」等のプロトタイプ表記は使わない

### 大きなHTMLを書く際の注意
- 1回のレスポンスでタイムアウトしないよう、3分割で書く:
  - Part 1: CSS + ヘッダー + データセクション
  - Part 2: 仮説 + 打ち手
  - Part 3: プロトタイプ + 競合比較 + フッター
- Agentへの委任より分割書き込みの方がトークン効率が良い

## Phase 3 — コミット・デプロイ

### 完了後の作業
生成したreports/{YEAR}-w{WEEK}/data.json に加え、
以下のファイルもリポジトリに保存してください。

1. WEEKLY_REPORT_PLAYBOOK.md（このファイル全体）を
   リポジトリルートに保存

2. git add WEEKLY_REPORT_PLAYBOOK.md reports/{YEAR}-w{WEEK}/data.json
3. git commit -m "feat: add w{WEEK} data.json + update playbook"
4. git push origin main
