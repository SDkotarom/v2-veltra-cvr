# GTM API 読み取り環境 セットアップ

Claude から GTM コンテナ設定（タグ・トリガー・変数）を API 経由で読めるようにする手順。
管理画面から手作業でエクスポートする運用をなくすことがゴール。

## 方式（社内標準 / 2026-08 二木さん確認）

> 自社 Google Cloud プロジェクト内に作った「内部（Internal）」の OAuth クライアントを使い、
> 自分の Google アカウントで一度だけブラウザ承認する。サービスアカウント鍵は作らない。

| 項目 | 内容 |
|---|---|
| 認証 | OAuth インストール型アプリ（デスクトップアプリ）。本人の Google アカウントで承認 |
| 鍵 | サービスアカウント鍵は作らない。更新用トークンを本人のローカルに保管 |
| gcloud / ADC | 使わない（後述） |
| Workspace 管理者への申請 | 不要 |

### なぜ gcloud / ADC 方式ではないのか

`gcloud`（Google Cloud SDK）は当社 Workspace から見ると **社外製アプリ** の扱いになる。
社外アプリの利用が制限されているため、ADC 発行時に「このアプリはブロックされます」で止まる。

一方、**自社プロジェクト内に作り、OAuth 同意画面を「内部」にした** OAuth クライアントは
**社内アプリ扱い**になるので、この制限に当たらない。だから管理者の許可申請そのものが不要で、
Workspace 管理コンソールを触る必要もない。

### セキュリティ上の位置づけ

更新用トークンもファイルに置く以上は秘密情報。ただしサービスアカウント鍵と比べて扱いやすい。

- 本人に紐づくので、権限はその人が GTM に持つ範囲を超えない
- 本人の Google アカウント画面からいつでも失効できる（鍵回収に人手が要らない）
- 組織レベルの鍵が増えないので、流出時の影響範囲が限定される

「鍵は平文で置かない（＝誰でも見える状態に置かない）」方針に対しては、
トークンを本人のローカル（権限 600・本人だけ読める場所）に置き、リポジトリには入れない運用で満たす。

---

## 0. GA4 側は追加作業が不要

GA4 は既に MCP 経由で接続済み。GTM だけが本手順の対象。

| 対象 | 状態 | 使うもの |
|---|---|---|
| GA4 レポート・プロパティ設定 | ✅ 接続済み | MCP（`run_report` 等） |
| GTM コンテナ設定 | ❌ 未接続 | 本手順で構築 |

→ **Google Analytics Admin API / Data API の有効化は不要。** 有効化するのは Tag Manager API のみ。

---

## 1. 対象リソース

| 項目 | 値 |
|---|---|
| GCP プロジェクト | `veltra-analytics-api`（veltra.com 組織配下。既存の別プロジェクトでも可） |
| GTM アカウントID | `173868083` |
| GTM コンテナID | `8248186` |
| GTM 公開ID | `GTM-5KFX5VX` |

---

## 2. GCP コンソール作業（ブラウザ・15分ほど）

### 2-1. プロジェクトを用意

`console.cloud.google.com` で veltra.com 組織配下のプロジェクトを 1 つ選ぶ（`veltra-analytics-api` 流用可）。

### 2-2. Tag Manager API を有効化

`APIとサービス` → `ライブラリ` → **Tag Manager API** → 有効にする。

### 2-3. OAuth 同意画面を「内部」にする ← 要点

`APIとサービス` → `OAuth 同意画面` → **User Type = 内部（Internal）** を選択。

これで社外アプリ扱いを避けられる（＝ Workspace の外部アプリ制限に当たらない）。

### 2-4. OAuth クライアント ID を作成

`APIとサービス` → `認証情報` → `認証情報を作成` → `OAuth クライアント ID`

| 項目 | 値 |
|---|---|
| アプリケーションの種類 | **デスクトップアプリ** |
| 名前 | 任意（例 `gtm-reader-local`） |

作成後、**JSON をダウンロード**する。

### 2-5. client_secret を安全な場所に置く

ダウンロードした JSON を、リポジトリ外・本人だけが読める場所に置く。

```bash
mkdir -p ~/.config/gtm && chmod 700 ~/.config/gtm
mv ~/Downloads/client_secret_*.json ~/.config/gtm/client_secret.json
chmod 600 ~/.config/gtm/client_secret.json
```

- リポジトリ内には置かない（スクリプトが実行を拒否する。`.gitignore` でも二重に防いでいる）
- Slack・メールに貼らない

---

## 3. 使い方

```bash
python3 -m pip install -r scripts/requirements-gtm.txt

# 初回のみブラウザ承認が走る（自分の Google アカウントを選んで許可）
python3 scripts/fetch_gtm.py accounts

# 以降はトークンで自動的に通る
python3 scripts/fetch_gtm.py summary
python3 scripts/fetch_gtm.py summary --filter mobility
python3 scripts/fetch_gtm.py find dev.veltra.com
python3 scripts/fetch_gtm.py live > ~/gtm-live.json   # 秘匿値はマスク済み
```

初回 `accounts` でブラウザが開く。同意画面には **GTM の読み取り** に関する権限だけが出るはず。
承認後、アカウント `173868083` が一覧に出れば疎通成功。更新用トークンは
`~/.config/gtm/token.json`（権限 600）に保存され、次回以降は自動で使われる。

### ファイルの置き場所（環境変数で変更可）

| 用途 | 既定パス | 環境変数 |
|---|---|---|
| client_secret | `~/.config/gtm/client_secret.json` | `GTM_OAUTH_CLIENT` |
| 更新用トークン | `~/.config/gtm/token.json` | `GTM_OAUTH_TOKEN` |
| 両方の親ディレクトリ | `~/.config/gtm` | `GTM_CONFIG_DIR` |

### スクリプト側の安全装置

| 装置 | 内容 |
|---|---|
| スコープ限定 | `tagmanager.readonly` のみ。書き込み系は要求しない |
| ホワイトリスト | アカウント `173868083` / コンテナ `8248186` 以外へはアクセスしない |
| リポジトリ内ファイルの拒否 | client_secret / token がリポジトリ内にあると実行を拒否 |
| トークンの権限 | 保存時に `chmod 600`。緩い権限のファイルは警告 |
| 秘匿値マスク | GTM 定数変数の `api_key` / `token` / `secret` 等は既定でマスク（`measurementId` は保持）。`--no-redact` で解除 |

`ALLOWED_CONTAINERS` のホワイトリストは外さない。別コンテナが必要になったらスクリプトに明示追記してレビューを通す。

### トークンの失効・再承認

```bash
python3 scripts/fetch_gtm.py logout   # ローカルのトークンを削除
```

Google 側の承認自体を取り消すには、Google アカウント → セキュリティ →
サードパーティのアクセス から該当アプリを削除する。

---

## 4. うまくいかないとき

| 症状 | 対処 |
|---|---|
| `client_secret が見つかりません` | 2-5 の配置、または `GTM_OAUTH_CLIENT` の指定を確認 |
| ブラウザで「このアプリはブロックされます」 | OAuth 同意画面が「内部」になっていない（2-3 を確認） |
| `client_secret の形式が不正` | OAuth クライアントの種類が「デスクトップアプリ」か確認 |
| 403 Forbidden | Tag Manager API 有効化、自分の GTM 権限、スコープを確認 |
| 401 / リフレッシュ失敗 | `logout` してから再度 `accounts` で再承認 |

---

## 5. 書き込みについて（将来）

最終ゴールは読み書き両方だが、当面は読み取りで疎通確認・分析を行う。書き込みは必要になった時点で
スコープ（`tagmanager.edit.containers` 等）を足す。**GTM の編集はワークスペース内に留まり、
公開して初めて本番サイトに反映される。注意すべきは編集権限より公開権限なので、公開はコードから
行わず管理画面から手作業で最終承認する**（＝スクリプトに公開系スコープは付けない）。

---

## 6. 完了後にできること

- `Mobility - GA4 PageView (prod)` の測定ID確認（`summary --filter mobility`）
- `Mobility - PageView Trigger (prod)` の発火条件確認
- dev 環境のホスト名がトリガー条件に残っていないかの検出（`find dev.veltra.com`）
- タグ・トリガー・変数の全数と依存関係の把握

なお元手順書の直近目的（Mobility Hub の GA4 受信ゼロ）については、対象プロパティ
`547515476` が GA4 上で「mobility.veltra.com（※未使用、削除予定）」に改名されている。
調査を再開する前に、この計測がまだ生きている案件かを確認したほうがよい。
