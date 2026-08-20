# GTM API 読み取り環境 セットアップ

Claude から GTM コンテナ設定（タグ・トリガー・変数）を API 経由で読めるようにする手順。
管理画面から手作業でエクスポートする運用をなくすことがゴール。

## 前提となる方針

> **鍵は平文でおかない。**（管理者指示 / 2026-08-20）

GCP のサービスアカウント鍵は、失効期限がなく、持ち出されれば誰でもその権限で動かせる。
ファイルパーミッション（`chmod 600`）は他ユーザーから守るだけで、ディスク上は平文のまま。
そのため本手順では次の優先順位を取る。

| 優先 | 方式 | 鍵の状態 |
|---|---|---|
| **1（推奨）** | ADC / キーレス — サービスアカウント鍵を作らない | 鍵が存在しない |
| 2 | サービスアカウント鍵 + macOS Keychain | 暗号化保管。実行時のみメモリ |
| 3 | 環境変数 `GTM_SA_KEY_JSON`（CI / Secret Manager 経由） | ディスクに書かない |
| ✗ | 平文の鍵ファイル | **スクリプトが既定で拒否** |

---

## 0. GA4 側は追加作業が不要

元手順書には GA4 の API 有効化と権限付与も含まれていたが、**GA4 は既に MCP 経由で接続済み**。

| 対象 | 状態 | 使うもの |
|---|---|---|
| GA4 レポートデータ | ✅ 接続済み | `mcp__*__run_report` / `run_realtime_report` |
| GA4 プロパティ設定 | ✅ 接続済み | `mcp__*__get_property_details` / `get_account_summaries` |
| GTM コンテナ設定 | ❌ 未接続 | 本手順で構築する |

MCP は GA4 アカウント `VELTRA Domain`（`21205104`）をアカウントレベルで参照でき、元手順書で
対象とされた 3 プロパティ（`318494528` / `546403487` / `547515476`）はすべて到達可能。

→ **Google Analytics Admin API / Data API の有効化、GA4 へのサービスアカウント追加は実施しない。**
必要のない権限は付与しない。有効化するのは Tag Manager API のみ。

---

## 1. 対象リソース

| 項目 | 値 |
|---|---|
| GCP プロジェクト | `veltra-analytics-api`（プロジェクト番号 `1039372110822`） |
| GTM アカウントID | `173868083` |
| GTM コンテナID | `8248186` |
| GTM 公開ID | `GTM-5KFX5VX` |

---

## 2. 手順A：キーレス（推奨）

サービスアカウント鍵を作らないので、平文で置く鍵がそもそも発生しない。
GTM を自分の権限で読む方式なので、GTM 管理画面でのユーザー追加も不要。

### 2-1. Tag Manager API を有効化

`APIとサービス` → `ライブラリ` → **Tag Manager API** → 有効にする。

```bash
gcloud config set project veltra-analytics-api
gcloud services enable tagmanager.googleapis.com
gcloud services list --enabled | grep tagmanager
```

GA4 の 2 つの API は有効化しない。

### 2-2. ADC を発行（スコープを GTM 読み取りだけに絞る）

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/tagmanager.readonly

export GOOGLE_CLOUD_PROJECT=veltra-analytics-api
echo 'export GOOGLE_CLOUD_PROJECT=veltra-analytics-api' >> ~/.zshrc
```

スコープを `tagmanager.readonly` だけにするのが要点。これで発行される資格情報は
**GTM の読み取り以外には何もできない**。`cloud-platform` は付けない（付けると自分の
GCP 権限すべてを持つ資格情報になり、「GCPは極めて強力」という懸念がそのまま当たる）。

`invalid_scope` で弾かれた場合のみ、必要最小の追加として次を試す。

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/tagmanager.readonly,openid,https://www.googleapis.com/auth/userinfo.email
```

### 2-3. 古い平文鍵が残っていたら消す

過去に鍵をダウンロードしている場合は、この時点で始末する。

```bash
unset GOOGLE_APPLICATION_CREDENTIALS          # ~/.zshrc に書いた行も削除
rm -P ~/.config/gcp/*.json 2>/dev/null        # 平文鍵の削除
```

GCP コンソール（`IAMと管理` → `サービスアカウント` → 該当SA → `キー`）でも
**鍵自体を削除**する。ローカルのファイルを消しても、鍵が有効なままなら意味がない。

### 2-4. ADC 資格情報の性質を理解しておく

`~/.config/gcloud/application_default_credentials.json` にリフレッシュトークンが残る。
これは平文だが、サービスアカウント鍵とは性質が違う。

| | サービスアカウント鍵 | ADC（ユーザー資格情報） |
|---|---|---|
| 有効期限 | 事実上無期限 | Google のセッションポリシーに従う |
| 失効 | 鍵を消すまで有効 | `gcloud auth application-default revoke` で即失効 |
| 権限範囲 | SA に付与された全権限 | 発行時に指定したスコープのみ |
| 帰属 | 人に紐づかない | 本人に紐づく（監査ログで追跡可能） |

作業が終わったら失効させておく。

```bash
gcloud auth application-default revoke
```

---

## 3. 手順B：鍵が必要な場合（CI・非属人運用）

CI から動かす、または人に紐づかない ID が必要な場合のみ。鍵は Keychain に入れて平文を残さない。

### 3-1. サービスアカウントを作る

`IAMと管理` → `サービスアカウント` → `サービスアカウントを作成`

| 項目 | 値 |
|---|---|
| 名前 | `gtm-readonly` |
| 説明 | GTM コンテナの読み取り専用アクセス |
| GCP ロール | **付与しない**（空のまま次へ） |

GCP 側の IAM ロールは不要。権限は GTM 管理画面から個別に渡す。

### 3-2. GTM に読み取り権限だけ付与

`tagmanager.google.com` → コンテナ `www.veltra.com (v2)` → `管理` → `ユーザー管理` → `＋`

| 種別 | 設定 |
|---|---|
| アカウント権限 | **ユーザー**（管理者にしない） |
| コンテナ権限 | **読み取り**のみ |

編集・承認・公開は付与しない。書き込み権限がなければ、本番タグが変更される事故は原理的に起きない。

### 3-3. 鍵を Keychain に入れて平文を消す

JSON キーを発行したら、**ダウンロードしたまま放置せず**すぐに移す。

```bash
scripts/gtm-key-store.sh store ~/Downloads/veltra-analytics-api-xxxxx.json
```

このスクリプトが行うこと：

1. サービスアカウント JSON として妥当か検証（内容は表示しない）
2. リポジトリ内のファイルなら拒否
3. macOS Keychain に登録（シェル履歴に残さない）
4. ダウンロードした平文ファイルを削除

```bash
scripts/gtm-key-store.sh check    # 登録済みか確認（中身は出さない）
scripts/gtm-key-store.sh remove   # Keychain から削除
```

残存リスクは正直に把握しておく。`security` コマンド実行中は同一ユーザーの他プロセスから
`ps` で引数が見える。また APFS では `rm -P` の上書き削除が保証されない。どちらも
「鍵を即座にローテーションできる」ことが最終的な担保になる。懸念があれば GCP コンソールで
鍵を削除して再発行する。

### 3-4. CI で使う場合

鍵を Secret Manager（または GitHub Actions の Secrets）に置き、実行時に環境変数へ展開する。

```bash
export GTM_SA_KEY_JSON="$(gcloud secrets versions access latest --secret=gtm-readonly-key)"
python3 scripts/fetch_gtm.py summary
```

スクリプトはこの値をメモリ上でのみ扱い、ディスクに書き出さない。

---

## 4. 使い方

```bash
python3 -m pip install -r scripts/requirements-gtm.txt

# 疎通確認（まずこれ）
python3 scripts/fetch_gtm.py accounts

# ライブ版のタグ/トリガー/変数を要約
python3 scripts/fetch_gtm.py summary
python3 scripts/fetch_gtm.py summary --filter mobility

# dev ホスト名がトリガー条件に残っていないか検索
python3 scripts/fetch_gtm.py find dev.veltra.com

# 生 JSON（秘匿値はマスク済み）。リポジトリ外に出力する
python3 scripts/fetch_gtm.py live > ~/gtm-live.json
```

`accounts` でアカウント `173868083` が出れば疎通成功。
どの認証方式が使われたかは `GTM_VERBOSE=1` で確認できる。`--auth adc` 等で固定もできる。

### スクリプト側の安全装置

| 装置 | 内容 |
|---|---|
| スコープ限定 | `tagmanager.readonly` のみ要求。書き込み系スコープは持たない |
| ホワイトリスト | アカウント `173868083` / コンテナ `8248186` 以外へはアクセスしない |
| 平文鍵の拒否 | 平文の鍵ファイルは既定で拒否し、移行先を案内する |
| リポジトリ内鍵の拒否 | 許可フラグの有無にかかわらず無条件で拒否 |
| 秘匿値マスク | GTM 定数変数の `api_key` / `token` / `secret` 等は既定でマスク（`measurementId` は保持） |
| 鍵内容の非出力 | エラー時も鍵の中身・トークンは一切出力しない |

`ALLOWED_CONTAINERS` のホワイトリストは外さない。権限設定によっては意図しないコンテナまで
読めてしまうため。別コンテナが必要になったらスクリプトに明示追記してレビューを通す。

### 取得した JSON の扱い

`live` の出力にはタグ設定・測定ID・トリガー条件が含まれる。`.gitignore` で
`gtm-live*.json` / `live.json` を塞いであるが、**リポジトリ外（ホームなど）に出力するのが基本**。

---

## 5. うまくいかないとき

| 症状 | 対処 |
|---|---|
| `利用できる認証情報がありません` | 手順2-2 の ADC 発行が済んでいない |
| `quota project が未設定です` | `export GOOGLE_CLOUD_PROJECT=veltra-analytics-api` |
| 403 Forbidden | Tag Manager API の有効化を確認。手順B の場合は GTM 権限が反映されるまで5分待つ |
| 401 / リフレッシュ失敗 | `gcloud auth application-default login` をやり直す |
| `平文の鍵ファイルは使用できません` | 仕様どおりの挙動。手順A か Keychain に移行する |
| `invalid_scope` | 手順2-2 の追加スコープ版を試す |

---

## 6. エスカレーション（二木さんに相談）

- API 有効化で課金アカウントの紐付けを求められ、対象を選べない
- サービスアカウント作成が拒否される（`iam.serviceAccounts.create`）
- 組織ポリシーでキー作成が禁止（`iam.disableServiceAccountKeyCreation`）
  → 手順A（キーレス）で進められるので、この禁止は障害ではない
- GTM のユーザー管理画面で追加ボタンが押せない（手順B のみ該当）

---

## 7. 完了後にできること

- `Mobility - GA4 PageView (prod)` の測定ID確認（`summary --filter mobility`）
- `Mobility - PageView Trigger (prod)` の発火条件確認
- dev 環境のホスト名がトリガー条件に残っていないかの検出（`find dev.veltra.com`）
- タグ・トリガー・変数の全数と依存関係の把握

なお元手順書の直近目的（Mobility Hub の GA4 受信ゼロ）については、対象プロパティ
`547515476` が GA4 上で「mobility.veltra.com（※未使用、削除予定）」に改名されている。
調査を再開する前に、この計測がまだ生きている案件かを確認したほうがよい。
