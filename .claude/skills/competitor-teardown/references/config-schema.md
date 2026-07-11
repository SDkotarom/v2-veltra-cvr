# teardown config スキーマ

`scripts/build-teardown.py --config <file>` が読む JSON。動くサンプルは `scripts/teardown/config.example.json`。

## トップレベル
| キー | 必須 | 内容 |
|------|------|------|
| `outfile` | ○ | 出力先（リポジトリ相対）例 `spot/2026-competitor-booking-teardown.html` |
| `title` | ○ | `<title>` |
| `hero` | ○ | `{badge, h1, lead}`（lead は HTML 可） |
| `sections` | ○ | ブロック配列（下記） |
| `footer` | | フッター HTML |

## sections ブロック（`type` で分岐）
- `slide_hi` … `{st, h, subs:[html...], callout?}` 強調スライド
- `pains` … `{st?, stt?, callout?}` ペイン5分類カード（固定内容）＋任意コールアウト
- `comparison` … `{st, axis_label?, sites:[{name,note?,veltra?}], rows:[{axis, cells:[{r,t}...]}], callout?}`
  - `r` は `g`(◎優秀)/`o`(○良)/`m`(△弱)/`b`(✕課題)。`cells` は `sites` と同順。
- `gallery` … `{st, assets_base?, lead?, groups:[{site, tag?, shots:[{img,cap}], note?}], note?}`
  - 画像は `assets_base`(既定 `/spot/assets/teardown`)+`img`。`shots` 空で `note` があれば注記ボックス。
- `matrix` … `{st, cols:[...], rows:[{phase, cells:[{t, focus?}]}], note?}`
  - `t:"—"` は空セル。`focus:true` で注力セル（オレンジ枠）。
- `steps` … `{st, steps:[{title, dur?, body}], callout?}` 番号付きステップ
- `html` … `{st?, wrap?("sec"|"slide"|"none"), html}` 任意 HTML の逃げ道（bespoke な節に）

## コールアウト（`callout`）
`{kind:"blue"|"amber"|"green", h, p}`。`p` は HTML 可（`<span class="pc e|a|w|c|b">` でペインタグを付けられる）。

## 注意
- 文字列は HTML として出力される（`slide-h` 等）。信頼できない入力を入れない。
- 画像は事前に `spot/assets/teardown/` へ配置しておく（PII 配慮のうえ）。
