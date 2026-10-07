# 表示速度モニタリング 引き継ぎ（2026-10-07 時点）

次のセッションは、まずこのファイルと `.claude/skills/veltra-web-perf-weekly-report/SKILL.md` を読むこと。

---

## 1. いまの状態

| 項目 | 値 |
|---|---|
| レポート | https://claude.ai/artifact/PdRrX84rA8hhBCxZ6Vq8WC （組織内公開・V41） |
| タブ | 「レポート」／「後半の方針」（URL 末尾 `#plan` で方針タブを直接開ける） |
| データの範囲 | PSI 日次 9/4〜9/30、CrUX 週次 〜9/26 締めの週（9月末で中締め） |
| 冒頭ブロック | 「9月の中締め」（実施内容／結果／要因／10月にやること） |
| 版数表示 | `defs.version` = 42（次に公開すると Artifact も Version 42 になり一致する） |
| ブランチ | `claude/charming-albattani-mc5puq`（push 済み・PR は未作成） |
| 計測スプレッドシート | fileId `1QPDTDPxCLqYQqCUAARHshpvYOJ4rcHvsF05X4AgWpLM` |
| Slack 投稿先の候補 | #proj-web-performance（C0BN961QQA1） |
| ClickUp | web-performance リスト `901820239496`、Suki さんの user id `66847429` |

## 2. 更新手順（確定版）

**別セッションも同じ Artifact に公開している。** 公開が拒否されたら、保存された最新版を全行読み、差分を data.json / build.py に移してから公開し直す（V39〜V41 で発生。中締めの「結果」の表は別セッション由来）

1. `mcp__Google_Drive__download_file_content` に `exportMimeType: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` を付けてシートを書き出す（結果はファイルに保存される。JSON の `content` を base64 デコードして .xlsx に）
2. `python3 scripts/perf-report/from_sheet.py <xlsx> [締め日]` で `psi` / `weekly` / `pages` を作り直す
   - from_sheet.py は data.json を丸ごと書き換えるので、`effect` `memos` `review` `strategy` `releases` `inventory` `react_measured` `tracks` は事前に退避して戻す
3. `effect`（前・直後・月末の比較）、`memos`（週次メモ）、`review`（冒頭）、`strategy`（方針タブ）は手で更新
4. `python3 scripts/perf-report/build.py` → playwright で確認（`executablePath: '/opt/pw-browsers/chromium'`）
5. 同じ URL に Artifact を publish → その直後に `defs.version` を +1 → sample-report.html にコピー → commit / push

**つまずきどころ**
- `read_file_content` はシートの先頭40行ほどで切れる。必ず xlsx 書き出しを使う
- build.py の f-string の中にバックスラッシュ（`\'` `’`）を書くと SyntaxError
- developers.google.com / developer.chrome.com / cloud.google.com はこの環境から接続拒否。Google の仕様を確かめるときは GitHub（GoogleChrome/lighthouse）のソースを見る
- ClickUp の添付画像（clickup-attachments.com）も接続拒否。画像はユーザーにスクリーンショットをもらう

## 3. 数値の扱い（ユーザーと決めたこと）

- **比較の期間**：リリース前 9/12〜9/16／直後 9/19〜9/24／月末 9/25〜9/30。いずれも6ページとも測れた5日の平均
- **結果の判定**：「前」と「月末」の差が、そのページの日次の標準偏差以内なら「変化なし」。表記は **速くなった／遅くなった／変化なし**（上がった・下がったは使わない）。数値には単位（点・ms）を付ける
- **PSI の判定帯**：90点以上「高」／50〜89点「普通」／49点以下「低」（Lighthouse の shared/util.js と ja.json で確認）
- **CrUX**：直近28日の p75。9/17 の効果を判定できるのは **10/17 締めの週** から。シートに入るのは締めの約1週間後なので **10/25 ごろ**
- **欠測**：最後の値が4週以上前のページは「欠測」とし、古い値を現在地として出さない
- **TBT**：ローディング中のリング回転（サーバー待ち）は TBT に出ない。②の効果は TBT では見えない
- **用語**：「くるくる」は使わない。「ローディング中のリング回転」と書く（英語は loading indicator）

## 4. 9月の結果（要点）

- リリース：9/17 UX_DESIGN-323・304・389、9/30 UX_DESIGN-309
- PSI 6ページ平均 33.7 → 38.5点。速くなった3（検索結果 +20.6、TOP +9.0、エリア +7.0）、変化なし2（地域・カテゴリー）、遅くなった1（AC詳細 −7.4）
- 絞り込みの応答 1.82秒 → 0.97秒（UX_DESIGN-309、Suki さんの手計測10回）
- 実ユーザー LCP（9/26 締め）：検索結果 6,895 → 6,112ms、TOP 2,755 → 2,942ms、エリア 2,642 → 2,805ms
- 実ユーザーのサーバー応答（TTFB）は TOP 1.6秒・エリア 1.8秒・検索結果 5.1秒。PSI 上は 2〜184ms。実ユーザーはキャッシュを外しているという見立て（推定）

## 5. 未完了・保留

| 順 | 内容 | 状態 | 次の一手 |
|---|---|---|---|
| A | Suki さんへの月次共有（Slack #proj-web-performance） | 文案あり（本文＋スレッド返信、EN→JA）。**未送信** | ユーザーの確認待ち。予算の具体値を入れるか、優先順（UX_DESIGN-404 は 416・417 と1組）を確認 |
| B | UX_DESIGN-307 の before/after 数字 | 10/5 に Suki さんへ依頼済み | 返信を待つ。来たらレポートの「本番で測った操作の応答」に追加 |
| C | UX_DESIGN-420 を閉じる | 307 の返信で「閉じます」と書いたが**未実施** | ユーザーの指示があれば閉じる |
| D | UX_DESIGN-395／396／397 のステータス | 9/17 に UX_DESIGN-304 として本番に出たのに「open」のまま | ユーザーの指示があれば直す |
| E | 週次の自動更新 | **未登録** | 曜日・時刻・投稿先が決まってから。登録前に内容を伝える |
| F | 収集スクリプトの正体 | 計測シートの「拡張機能 → Apps Script」をユーザーが確認する待ち | 見つかれば、地域・カテゴリー・AC詳細の計測 URL を差し替える。API キーは不要になった（URL を自前で取る場合だけ要る） |
| G | 9/17 の効果を実ユーザー値で判定 | 10/25 ごろ | 10/17 締めの週が入ったら更新 |
| H | 未返信の返信7件（BUR 発表分担、小林さんの報告事項・自動ログイン、Figma 社外共有、石井さんのシート確認、SYS-7288 打ち合わせ、JOBCAN） | 要約・判断事項・返信ドラフトを提示済み。**未送信** | ユーザーが番号と［　］の中身を決めたら送る |
| I | PR | 未作成 | 必要なら作成 |

## 6. このユーザーとの約束（守ること）

- **送信・投稿・ステータス変更は、必ずユーザーの「送って」「やって」の後**。下書きは「未送信」と明記する
- **定期実行・監視・購読は、明示の依頼まで登録しない**。登録前に、いつ・何を・どの頻度でやるかを伝える
- 見出しは名詞のラベル。比喩・造語を使わない。同じものは同じ言葉で（初出は「PageSpeed Insights（PSI）」、以降「PSI」）
- 数値には主語と単位を付ける。推定は「推定」と書く。確認できていないことは「未確認」と書く
- 回答の冒頭に [検索済:〜] か [未確認] を付ける。手順を書く前に一次情報を確認する
- 社内エンジニア向けコメントは EN → `---` → JA、短く、提案は問いの形で
- チケット番号は ClickUp リンク（`https://app.clickup.com/t/31108037/UX_DESIGN-NNN`）。裸の `#123` は書かない
- 絵文字・左罫線の太線・行頭アイコンを使わない
- ツールチップは用語ごとに初出だけ。ただし見出しの中の用語には必ず付ける
