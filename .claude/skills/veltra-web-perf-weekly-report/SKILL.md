---
name: veltra-web-perf-weekly-report
description: >
  VELTRA「表示速度モニタリング」の週次レポートを生成するスキル。計測スプレッドシート
  （CrUX週次・PSI日次・リリース注釈）を読み、対象6ページの Core Web Vitals と週次推移に
  リリース注釈を重ねた自己完結HTMLを生成し、Google サイトの Full page embed に貼る。
  ユーザーが「速度レポート作って」「表示速度の週次」「web performance レポート」などと
  言ったら使用する。
---

# VELTRA 表示速度モニタリング 週次レポート生成スキル

## 何を作るか

対象6ページの Core Web Vitals（実ユーザー p75）と週次推移を、**リリース日の注釈つき**で
1枚のHTMLにして、Google サイトに貼る。リリース前後で何が変わったかを、線とラベルで
見て分かる状態にするのが目的。

レポートは週ごとに新しいページとして追加する。過去週のページはそのまま残す。

## データソース

### 計測スプレッドシート

- fileId: `1QPDTDPxCLqYQqCUAARHshpvYOJ4rcHvsF05X4AgWpLM`
- タイトル: `wip_表示速度改善 施策リスト（web-performance）`
- 読み方: `mcp__Google_Drive__read_file_content` に fileId を渡す

タブ構成（列はこの順）:

| タブ | 列 |
|---|---|
| CrUX 週次 | `collected_at / period_end / page / url / form_factor / lcp_p75_ms / inp_p75_ms / cls_p75 / ttfb_p75_ms / lcp_good_pct` |
| PSI 日次 | `collected_at / date / page / url / strategy / perf_score / lcp_ms / ttfb_ms / tbt_ms / cls / field_lcp_p75_ms` |
| リリース注釈 | `date / ticket / target / type / note` |
| 週次計測トラッカー | AsIs・合格ライン・目標・週次列 |

### 落とし穴（必ず守る）

**CrUX 週次タブは、収集を回すたびに全履歴が丸ごと再掲される。** 同じ `period_end` の行が
`collected_at` 違いで何本も並ぶ。**最新の `collected_at` のブロックだけを使うこと。**
全行をそのまま集計すると、同じ週を何度も数えて壊れる。

PSI 日次タブは追記型なので、そのまま時系列として使ってよい。

`#NUM!` が入っている行は、そのURLがCrUXの掲載閾値に届かずデータが返らなかった週。
欠測として扱い、0 で埋めない。線は途切れさせる。

## 対象6ページと合格ライン

| ページ | URL |
|---|---|
| TOP | `https://www.veltra.com/jp/` |
| エリア | `https://www.veltra.com/jp/japan/tokyo/` |
| 地域 | `https://www.veltra.com/jp/japan/kanto/` |
| カテゴリー | `https://www.veltra.com/jp/japan/tokyo/ctg/...` |
| AC詳細 | `https://www.veltra.com/jp/japan/tokyo/a/160690` |
| 検索結果 | `https://www.veltra.com/jp/search?kw=tokyo` |

合格ライン（実ユーザー p75）: LCP ≤2,500ms ／ INP ≤200ms ／ CLS ≤0.1 ／ TTFB ≤800ms
要改善: LCP ≤4,000ms ／ INP ≤500ms ／ CLS ≤0.25

判定は **本番 www.veltra.com のみ**。dev は設定が違い数値が乖離するため使わない。

## レポート構成

1. ヘッダー（タイトル・対象週・データ取得日・タイムゾーン）
2. サマリー（6ページの LCP を合格/要改善/不良のバッジつきで一覧。前週差も併記）
3. **週次推移チャート（このレポートの主役）**
   - 横軸は CrUX の `period_end`、縦軸は LCP p75
   - ページごとの折れ線。合格ライン 2,500ms に基準線
   - **リリース注釈タブの日付に縦線を引き、チケット番号のラベルを添える**
   - 縦線は淡いグレー、ラベルは縦書きにせず短く（例: `UX_DESIGN-304`）
4. 指標詳細表（LCP / INP / CLS / TTFB を6ページ×最新週で）
5. リリース記録（注釈タブの内容をそのまま表に。チケットは ClickUp へリンク）
6. フッター（データソース・CrUXは28日間の実ユーザーデータで効果が出るまで数週かかる旨・生成日）

### 効果を語るときの作法

- **リリース直後の週で「改善した」と書かない。** CrUX は28日間のローリングなので、
  リリースの効果が p75 に出始めるまで数週かかる。リリースは注釈として置くだけにして、
  判定は数週後に行う
- 悪化していたら悪化と書く。都合のいい週だけ切り取らない

## HTMLの作り方

- **自己完結1枚**。`<style>` でCSS、`<script>` でチャート描画まで含める
- **外部JSライブラリを読まない。** インラインSVG + 少量のスクリプトで描く。
  Sites 埋め込み時の CSP / CORS を避けるため
- VELTRAブランドガイドライン（`veltra-brand-guidelines` スキル）の色とフォントを使う
- グラフは `dataviz` スキルの手順に従う
- **本リポジトリの CLAUDE.md の禁止事項を必ず守る**
  - 絵文字を一切使わない
  - 左罫線だけ太くして色を付けるUIを使わない（均一の1pxボーダーとバッジで表現）
  - 見出し行頭のアイコン四角を使わない
  - チケット番号は必ず `https://app.clickup.com/t/31108037/UX_DESIGN-<番号>` へリンク

## Google サイトへの貼り方

対象サイトのURLは初回に確認する（速度モニタリング用のサイトを新設するか、既存サイトに
ページを足すか）。

1. サイトを編集モードで開く
2. 右パネルの「Pages」タブ
3. 右下の「+」→「Full page embed」
4. ページ名は週の命名規則 `YYMMDD~YYMMDD`（対象週の月曜〜日曜）
5. 「Done」→「Add embed」→「Embed code」タブ
6. textarea にHTML全文を貼る
   - Sites のネイティブブロックに直接入力すると日本語が文字化けする。**必ず Embed code を使う**
   - 1万文字を超えると type 操作がタイムアウトすることがあるが、実際には入力されている
     ことが多い。末尾に `</html>` があるかスクリーンショットで確認してから次へ進む
7. 「Next」→ プレビューが出たら「Insert」
8. 右上の「Preview」で表示を確認
9. **Publish は必ずユーザーの明示的な確認を得てから行う**

## 実行タイミング

- CrUX は週次更新なので、**週1回で足りる**。日次で回しても同じ数字が返る
- 対象週が完全に終わってから実行する
- 週が未完了のまま出す場合は「速報値」と明記し、推移チャートには載せない

## 注意点

- スプレッドシートに書き込む手段がない場合は、リリース注釈の行をユーザーに渡して
  貼ってもらう。勝手に別のシートを作らない
- 本番ページを直接書き換えない。新しいページを追加する形にする
- 数値の出典（どのタブの、いつの `collected_at` か）をフッターに必ず書く
- 確認していないことを断定で書かない。欠測は欠測と書く
