---
name: veltra-web-perf-weekly-report
description: >
  VELTRA「表示速度モニタリング」レポートを更新するスキル。計測スプレッドシートの
  _summary / _defs タブ（集計済み）を読んで data.json を更新し、ビルダーで HTML を
  生成して、既存のアーティファクトを同じURLに再publishする。ユーザーが「速度レポート
  更新して」「表示速度の週次」「web performance レポート」などと言ったら使用する。
---

# 表示速度モニタリング レポート更新

## 構成（3層）

| 層 | 実体 | 役割 |
|---|---|---|
| 1. 取得 | Apps Script（既存・要特定） | CrUX 週次 / PSI 日次をスプレッドシートに追記 |
| 2. 集計 | `scripts/gas/perf-aggregate.gs` | 生データの解釈を確定し `_summary` / `_defs` に書き出す |
| 3. 生成 | `scripts/perf-report/build.py` | `data.json` から HTML を生成。テンプレートはコード側に固定 |

**このスキルがやるのは 3 だけ。** 数値の解釈は 2 で終わっているので、レポート側で
生データを読み直さない。読むのは `_summary` と `_defs` のみ。

## 更新手順

1. `mcp__Google_Drive__read_file_content` で計測スプレッドシート
   （fileId `1QPDTDPxCLqYQqCUAARHshpvYOJ4rcHvsF05X4AgWpLM`）を読む
2. **`_summary` と `_defs` の内容だけ**を `scripts/perf-report/data.json` の
   `pages` / `defs` に転記する。crux_weekly や psi_daily を直接解釈しない
3. `weekly`（週次推移）は crux_weekly の**最新 collected_at のブロック**から作る。
   ここだけは生データを触るが、最新ブロック以外は使わない
4. `lead` / `findings` / `issues` を今週の内容に書き換える（後述）
4.5 `tracks`（2つの系統）と `pipeline`（データの流れ）の状態を見直す。
   - `tracks[].rows` はサーバ計測の値。再測されたら差し替え、出典を書き換える
   - `tracks[].auto` は指標キー。合格ページ数はビルダーが最新週から計算するので触らない
   - `pipeline[].items[].st` は `ok`（稼働中）/ `todo`（未設置）。層が動き出したら切り替える
5. `python3 scripts/perf-report/build.py` で HTML を生成
6. Artifact ツールで同じファイルパスを再publish。**URLは変わらない**

## 数値を書くときの規則

`_defs` に入っている規則がすべて。迷ったら `_defs` を見る。

- **分母は6ページ固定。** 測れないページも「未計測」として分母に残す
- **URL単位の CrUX のみ。** origin（サイト全体）の値で代用しない。代用すると
  そのページの施策効果が判定できなくなる
- **欠測は 0 で埋めない。** 線は途切れさせる
- **LCP と TTFB の差や比率を計算しない。** それぞれ独立した p75 なので、
  「LCP のうち何%が TTFB」は成立しない
- **「◯月比」と書かない。** `best_period_end` を使って「最速週 YYYY-MM-DD 比」と書く
- **リリース直後の週で「改善した」と書かない。** CrUX は28日ローリング

## lead / findings / issues の書き方

数値は `_summary` から引く。書くのは解釈だけ。

- **lead** — 3〜4段。結論が先。数字を `<b>` で埋め込んだ散文にする
- **findings** — 見出しは断定文（「半年かけて悪化している」）。データから言えることだけ。
  推測を書くときは本文に「これは推定だが」と明示する
- **issues** — ClickUp チケットに紐づける。紐づくものが無ければ `ticket` を空にする
  （ビルダーが「未起票」と出す）。やることは具体的な次の一手にする
- 日英とも書く。英語は直訳にせず、英語として読める文にする

## 出力先

- アーティファクト（組織内公開）。同じURLに再publishするので、リンクは変わらない
- Google サイトから見せる場合は、そのURLへリンクを1本置くだけでよい

## 注意点

- スプレッドシートへの書き込み手段はこのセッションにない。`_summary` の再生成が必要な
  場合は、Apps Script の `aggregate()` を実行してもらう
- 取得層（CrUX / PSI の収集）を何が動かしているかは未特定。止まっていないかは
  `_defs` の `crux_collected_at` と `psi_date` が更新されているかで判断する
- 本リポジトリの CLAUDE.md の禁止事項に従う（絵文字・左罫線・行頭アイコンを使わない、
  チケットは ClickUp へリンク）
