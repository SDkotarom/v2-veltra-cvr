# 種別ごとの構成と実例

どの既存ページを実例として見るかを機械的に確認した結果を置いてある。
「最新のページを見る」は危険。新しいページのほうが崩れている場合がある（実際そうだった）。

## 実例の選び方の根拠

週次サマリーのクラス語彙を実測した結果。

| 週 | インライン CSS | 共有 CSS の語彙 | 独自語彙 |
|---|---|---|---|
| W13 | 0 行 | 25 箇所 | 0 箇所 |
| W16 | 0 行 | 27 箇所 | 0 箇所 |
| W20 | 96 行 | 9 箇所 | 9 箇所 |
| W25 | 125 行 | 9 箇所 | 11 箇所 |

**実例として見るのは W16 と W13。W20 以降は見ない。**
W25 を `check.py` に通すと NG 3 件（インライン `<style>`、共有 CSS に無いクラス 52 個、
UI 規則違反 15 件）が出る。新しいから正しいわけではない。

## 週次サマリー

- 置き場所 `2026h1/reports/{YYYY}-{h1|h2}/{YYYY}-w{WW}/index.html`（W1〜W26 は `h1`、W27〜 は `h2`）
- 雛形 `assets/weekly-summary.html`
- 実例 `2026h1/reports/2026-h1/2026-w16/index.html`
- 手順の本体は `docs/playbook.md` Phase 2.9

固定 3 セクション + 自動描画。

| セクション | 中身 |
|---|---|
| 01 Conclusion | ヘッドライン + サブ + KPI 3 枚（セッション / 予約数 / CVR、前週比つき） |
| 02 Evidence | 証拠カード 3 枚。既定の軸は「ユーザー行動 / 流入と反応の乖離 / ユーザー層」 |
| 03 Action | 短期（今週の急性問題） / 中期（既存 BN Top3） / 継続監視 |
| 詳細 | `<div id="summary-detail"></div>` に `summary-detail.js` が `./data.json` から描画。触らない |

書く前に `docs/playbook.md` Phase 2.9 の Step 0（データ品質チェック）を通す。
Sessions の WoW が ±20% を超える週などは、ユーザー行動の物語ではなく
「データ品質インシデント」として書く。bot を見逃したまま行動物語を書くと
サマリー全体が成立しなくなる。実例は W16（bot 希釈インシデント）。

Action 2 の BN タイトルは `data.json` の `bottlenecks[].title` と一字一句合わせる。
`new-report.py` が埋めるので手で書かない。ずれると `validate-report.py` が落ちる。

## スポット分析・単発レポート

- 置き場所 `2026h1/spot/*.html`
- 雛形 `assets/analysis-report.html`
- 実例 `2026h1/spot/2026-h1-cvr-wrap.html`（共有 CSS を読んでいる）

週次と同じ語彙（`sec-tag` / `summary-hero` / `evidence-grid` / `action-item`）を使う。
種別が変わっても読み手の見方が変わらないほうがいい。

節数は論点の数で決める。3 枚に無理に揃えない。ただし枚数を決める前に
「何と何が並列か」を確定させる。並列でないものを同じ枠に並べると関係が読めなくなる。

年次比較を含むなら CLAUDE.md「YoY/前年比較の作法」の 3 原則を必ず守る。
matched 同期で比べる / ピーク月は 7-8月と 12-1月 / まだ来ていない月を考慮する。

## プロジェクトブリーフ

- 置き場所 `2026h2/projects/*.html`
- 雛形 `assets/analysis-report.html`

現状の 9 ページは互いに揃っているが、配色は `report.css` ではなく独自トークン
（`--blue:#7CA0BF` / `--offwhite:#FEFCF3`）を持っている。`lint.py` は
`local-palette` として警告に出す。

H2 で意図的に配色を変えたのか、ドリフトなのかは未確定。**新規ページは
`report.css` に寄せる**。既存 9 ページを寄せ直すかは別途の判断。

## 施策ドキュメント

- 置き場所 `2026h1/planning/*.html`
- 雛形 `assets/analysis-report.html`

CLAUDE.md「施策ドキュメント執筆ルール」がこのスキルより優先される。
特に以下は `check.py` では見きれないので自分で確認する。

- やり取りの痕跡を残さない（会話由来の造語、改善ボースト、版数追跡）
- 「マーケが」「担当が」など人に責任を投げる表現を使わない。仕組みで書く
- 抽象ラベルだけで終わらせない。発火条件と意味を書く
- サービス名は Veltra、ユーザー主語は Traveler
- 擬似レコメンドを扱うなら How の具体（データソース / クエリ / 環境 / 投入経路 / 属性 / テンプレ）を全部書く

## モックページは対象外

`2026h1/planning/sports-mock/**` と `veltra-theme-lp-staging/**` は
実サイト（veltra.com）の UI を再現するものなので、独自配色と 13px 未満のフォントが正当。
`lint.py` も `check.py` もこれらを除外している。
これらを作るときは `docs/veltra-design-system.md` と CLAUDE.md「Figma実装ルール」に従う。
