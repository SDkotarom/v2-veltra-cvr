# web-vitals GTM タグ (UX_DESIGN-300)

実ユーザーの LCP / INP / CLS / FCP / TTFB を、全ページで GA4 に送る。CrUX で値が出ない地域・カテゴリー・AC詳細も取れる。

## 公開手順 (GTM-5KFX5VX、ブラウザ作業)
1. タグ: 種類「カスタムHTML」。`web-vitals-gtm.html` の全文を貼る。トリガー All Pages。
2. トリガー: 種類「カスタムイベント」、イベント名 `web_vitals`。
3. 変数 (データレイヤー変数): `metric_name` `metric_value` `metric_rating` `page_type` `device` `nav_type`。
4. タグ: 種類「GA4 イベント」、イベント名 `web_vitals`、上の変数を同名のパラメータで渡す。トリガーは手順2。
5. プレビューで、各ページに `web_vitals` が出ることを確認してから公開する。

## GA4 のカスタム定義 (管理 → カスタム定義)
| 種類 | 名前 | イベント パラメータ |
|---|---|---|
| ディメンション (イベント) | metric_name | metric_name |
| ディメンション (イベント) | metric_rating | metric_rating |
| ディメンション (イベント) | page_type | page_type |
| ディメンション (イベント) | device | device |
| 指標 (標準) | metric_value | metric_value |

分析: metric_name ごとに metric_value の平均ではなく p75 が要る。GA4 画面では p75 が出ないため、BigQuery エクスポート、または `rating` (good/needs-improvement/poor) の割合で見る。

## 安全面
- 外部CDNを読まない (ライブラリは本文に埋め込み)。
- 送る値は指標名・数値・判定・ページ種別・端末のみ。URL・ユーザーIDなし。
- 例外は握りつぶし、ページ表示に影響させない。
- GTM の公開権限は最小限の人に限る。
