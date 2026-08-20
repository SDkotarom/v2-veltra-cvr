# GTM API 読み取り環境 セットアップ

Claude から GTM コンテナ設定（タグ・トリガー・変数）を API 経由で読めるようにする手順。
管理画面から手作業でエクスポートする運用をなくすことがゴール。

---

## 0. 前提：GA4 側は追加作業が不要

元手順書では GA4 の API 有効化と権限付与も含まれていたが、**GA4 は既に MCP 経由で接続済み**。

| 対象 | 状態 | 使うもの |
|---|---|---|
| GA4 レポートデータ | ✅ 接続済み | `mcp__*__run_report` / `run_realtime_report` |
| GA4 プロパティ設定 | ✅ 接続済み | `mcp__*__get_property_details` / `get_account_summaries` |
| GTM コンテナ設定 | ❌ 未接続 | 本手順で構築する |

MCP は GA4 アカウント `VELTRA Domain`（`21205104`）をアカウントレベルで参照できており、
元手順書で対象とされた 3 プロパティはすべて到達可能。

| プロパティ名 | ID | 到達 |
|---|---|---|
| VELTRA Main Site (All-Subdomain) | `318494528` | ✅ |
| Current Site Dev environment | `546403487` | ✅ |
| mobility.veltra.com（※未使用、削除予定） | `547515476` | ✅ |

→ **Google Analytics Admin API / Data API の有効化、GA4 へのサービスアカウント追加は実施しない。**
権限は増やさないほうが安全なので、必要のない付与は行わない。

---

## 1. コンソール作業（実施者：Kotarom）

`gcloud` は Claude の実行環境に入っていないため、以下は GCP コンソールで行う。
ローカルに `gcloud` がある場合は各節の CLI を使ってもよい。

### 1-1. プロジェクト選択

`console.cloud.google.com` で既存プロジェクトに相乗りする。以下の資産が動いているものを探す。

- `ai.veltra.dev` / `ai.veltra.com` の MCP サーバー群
- `mobility-dev-web-1018137694367.asia-northeast1.run.app`（Cloud Run）

見つからない場合は新規作成でも可（名前案 `veltra-analytics-api`）。**プロジェクトIDを控える。**

### 1-2. API の有効化（1つだけ）

`APIとサービス` → `ライブラリ` → **Tag Manager API** を有効化。

```bash
gcloud config set project <PROJECT_ID>
gcloud services enable tagmanager.googleapis.com
gcloud services list --enabled | grep tagmanager
```

### 1-3. サービスアカウントの作成

`IAMと管理` → `サービスアカウント` → `サービスアカウントを作成`

| 項目 | 値 |
|---|---|
| 名前 | `gtm-readonly` |
| 説明 | GTM コンテナの読み取り専用アクセス |
| GCP ロール | **付与しない**（空のまま次へ） |

GCP 側の IAM ロールは不要。権限は GTM 管理画面から個別に渡す。
**作成されたメールアドレスを控える**（`gtm-readonly@<PROJECT_ID>.iam.gserviceaccount.com`）。

### 1-4. JSON キーの発行・保管

`キー` タブ → `鍵を追加` → `新しい鍵を作成` → **JSON**

ダウンロードした鍵は**リポジトリ内に置かない**。

```bash
mkdir -p ~/.config/gcp && chmod 700 ~/.config/gcp
mv ~/Downloads/<ダウンロードしたファイル>.json ~/.config/gcp/gtm-readonly.json
chmod 600 ~/.config/gcp/gtm-readonly.json

echo 'export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcp/gtm-readonly.json' >> ~/.zshrc
source ~/.zshrc
```

鍵の取り扱い規約：

- Slack・メール・チャットに貼らない（貼ったら失効させて再発行する）
- リポジトリに置かない。`.gitignore` で `*-readonly*.json` 等を塞いであるが、それは最後の砦
- 社内で Secret Manager 運用の推奨があればそちらに従う
- 使わなくなったら GCP コンソールから鍵を削除する

### 1-5. GTM への権限付与（読み取りのみ）

`tagmanager.google.com` → コンテナ `www.veltra.com (v2)` → `管理` → `ユーザー管理` → `＋`

| 種別 | 設定 |
|---|---|
| アカウント権限 | **ユーザー**（管理者にしない） |
| コンテナ権限 | **読み取り**のみ |

編集・承認・公開は付与しない。書き込み権限がなければ、本番タグが変更される事故は原理的に起きない。

| 項目 | 値 |
|---|---|
| アカウントID | `173868083` |
| コンテナID | `8248186` |
| 公開ID | `GTM-5KFX5VX` |

---

## 2. 実行場所をどこにするか

| 方式 | 鍵の置き場所 | 評価 |
|---|---|---|
| **A. ローカルの Claude Code（推奨）** | `~/.config/gcp/gtm-readonly.json` | 鍵が自分のマシンから出ない。既定はこれ |
| B. リモートセッション | 環境変数 `GTM_SA_KEY_JSON` に JSON 文字列 | 鍵がホスト環境に載る。使い捨てコンテナは毎回消えるので再設定が必要 |

リモート（Claude Code on the web）のコンテナは一時的なので、鍵をファイルとして置いても
セッション終了で消える。恒久的に使いたい場合のみ、環境設定の環境変数に `GTM_SA_KEY_JSON`
を登録する。その場合も**鍵をチャットに貼り付けて渡すことはしない**。

---

## 3. 使い方

```bash
python3 -m pip install -r scripts/requirements-gtm.txt

# 疎通確認（まずこれ）
python3 scripts/fetch_gtm.py accounts

# ライブ版のタグ/トリガー/変数を要約
python3 scripts/fetch_gtm.py summary

# 特定の話題だけ絞る
python3 scripts/fetch_gtm.py summary --filter mobility

# dev ホスト名がトリガー条件に残っていないか検索
python3 scripts/fetch_gtm.py find dev.veltra.com

# 生 JSON（秘匿値はマスク済み）
python3 scripts/fetch_gtm.py live > ~/gtm-live.json
```

`accounts` でアカウント `173868083` が出れば疎通成功。`summary` の
`containerVersionId` がライブ版の番号（例 `750`）になる。

### スクリプト側の安全装置

| 装置 | 内容 |
|---|---|
| スコープ限定 | `tagmanager.readonly` のみ要求。書き込み系スコープは持たない |
| ホワイトリスト | `ACCOUNT_ID` / `ALLOWED_CONTAINERS` 外へはアクセスしない |
| 鍵位置チェック | 鍵がリポジトリ内にあると実行を拒否（コミット事故の防止） |
| パーミッション警告 | 鍵が group/other から読める場合に警告 |
| 秘匿値マスク | GTM 定数変数の `api_key` / `token` / `secret` 等は既定でマスク |
| 鍵内容の非出力 | エラー時も鍵の中身は一切出力しない |

`ALLOWED_CONTAINERS` のホワイトリストは外さない。権限設定によっては意図しないコンテナまで
読めてしまうため。別コンテナが必要になったら、スクリプトに明示追記してレビューを通す。

### 取得した JSON の扱い

`live` の出力にはタグ設定・測定ID・トリガー条件が含まれる。`.gitignore` で
`gtm-live*.json` / `live.json` を塞いであるが、**リポジトリ外（ホームなど）に出力するのが基本**。

---

## 4. うまくいかないとき

| 症状 | 対処 |
|---|---|
| 403 Forbidden | GTM の権限付与は反映まで数分。5分待って再実行 |
| 403 が続く | Tag Manager API が有効化されているか、対象プロジェクトが合っているか確認 |
| 401 Unauthorized | 鍵が失効・削除されている。再発行する |
| `アクセス可能なアカウントがありません` | GTM 側のユーザー追加が保存されていない |

---

## 5. エスカレーション（二木さんに相談）

- GCP プロジェクトの作成権限がない
- API 有効化で課金アカウントの紐付けを求められ、対象を選べない
- サービスアカウント作成が拒否される（`iam.serviceAccounts.create`）
- 組織ポリシーでキー作成が禁止（`iam.disableServiceAccountKeyCreation`）
- GTM のユーザー管理画面で追加ボタンが押せない

**キー作成が組織ポリシーで禁止されている場合**は、Workload Identity Federation か
キーなしの ADC 運用に切り替える。この場合は方式から相談する（鍵を作らない運用のほうが
本来は望ましいので、禁止されていること自体は問題ではない）。

---

## 6. 完了後にできること

- `Mobility - GA4 PageView (prod)` の測定ID確認（`summary --filter mobility`）
- `Mobility - PageView Trigger (prod)` の発火条件確認
- dev 環境のホスト名がトリガー条件に残っていないかの検出（`find dev.veltra.com`）
- タグ・トリガー・変数の全数と依存関係の把握

なお元手順書の直近目的（Mobility Hub の GA4 受信ゼロ）については、対象プロパティ
`547515476` が GA4 上で「mobility.veltra.com（※未使用、削除予定）」に改名されている。
調査を再開する前に、この計測自体がまだ生きている案件かを確認したほうがよい。
