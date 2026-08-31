#!/usr/bin/env python3
"""
fetch_gtm.py
============
GTM（Google Tag Manager）コンテナ設定の読み取り専用フェッチャ。
管理画面から手作業でエクスポートする運用をなくすためのスクリプト。

認証方式（社内標準 / 2026-08 二木さん確認）:
  自社 Google Cloud プロジェクト内に作った「内部（Internal）」の OAuth クライアントを使い、
  自分の Google アカウントで一度だけブラウザ承認する（インストール型アプリのフロー）。
  承認後に返る更新用トークンをローカルに保管して使い回す。

  - サービスアカウント鍵は作らない（平文の鍵をディスクに置かない）
  - gcloud / ADC は使わない（Google Cloud SDK は社外アプリ扱いでブロックされるため）
  - OAuth 同意画面を「内部」にすることで社内アプリ扱いになり、Workspace の
    外部アプリ制限に当たらない（管理者の許可申請が不要）

前提:
  - veltra.com 組織配下の GCP プロジェクトで Tag Manager API を有効化済み
  - OAuth 同意画面 = 内部（Internal）、OAuth クライアント = デスクトップアプリ
  - client_secret JSON をダウンロード済み（Git 管理下に置かない）
  - 依存: pip install -r scripts/requirements-gtm.txt

ファイルの置き場所（既定。環境変数で変更可）:
  - client_secret: ~/.config/gtm/client_secret.json   （GTM_OAUTH_CLIENT で変更可）
  - token（更新用）: ~/.config/gtm/token.json          （GTM_OAUTH_TOKEN で変更可）
  どちらも権限 600 を推奨。リポジトリ内に置くと実行を拒否する（コミット事故の防止）。

使い方:
    # 初回のみブラウザ承認が走る。以降はトークンで自動的に通る。
    python3 scripts/fetch_gtm.py accounts            # アクセス可能なアカウント確認（疎通テスト）
    python3 scripts/fetch_gtm.py containers          # 許可コンテナの一覧
    python3 scripts/fetch_gtm.py summary             # ライブ版のタグ/トリガー/変数を要約表示
    python3 scripts/fetch_gtm.py summary --filter mobility
    python3 scripts/fetch_gtm.py live                # ライブ版の生 JSON（秘匿値はマスク）
    python3 scripts/fetch_gtm.py find dev.veltra.com # ライブ版をキーワード検索
    python3 scripts/fetch_gtm.py logout              # 保管中のトークンを削除（失効は Google アカウント画面から）

セキュリティ上の設計:
  - スコープは tagmanager.readonly のみ（書き込みは必要になった時点で足す。公開権限は付けない）
  - ACCOUNT_ID / ALLOWED_CONTAINERS のホワイトリスト外はアクセスしない
  - client_secret / token がリポジトリ内にある場合は実行を拒否
  - token は保存時に chmod 600。緩い権限のファイルは警告
  - GTM の定数変数に third-party の API キーが入っていることがあるため、
    出力時に秘匿キーらしき値はデフォルトでマスクする（--no-redact で解除）
"""

import argparse
import json
import os
import stat
import sys
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import AuthorizedSession, Request
    from google.auth.exceptions import RefreshError
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    sys.exit(
        "依存パッケージが未インストールです。\n"
        "  python3 -m pip install -r scripts/requirements-gtm.txt"
    )

ROOT = Path(__file__).resolve().parent.parent

# --- ホワイトリスト（外さない）------------------------------------------------
ACCOUNT_ID = "173868083"                    # VELTRA GTM アカウント
ALLOWED_CONTAINERS = {
    "8248186": "www.veltra.com (v2) / GTM-5KFX5VX",
}
DEFAULT_CONTAINER = "8248186"

# 読み取り専用。書き込みが必要になったらここに edit 系スコープを足す（公開系は足さない）。
SCOPES = ["https://www.googleapis.com/auth/tagmanager.readonly"]

BASE = "https://tagmanager.googleapis.com/tagmanager/v2"
TIMEOUT = 30

# 認証情報の既定パス（環境変数で上書き可）
CONFIG_DIR = Path(os.environ.get("GTM_CONFIG_DIR", "~/.config/gtm")).expanduser()
CLIENT_SECRET_PATH = Path(
    os.environ.get("GTM_OAUTH_CLIENT", str(CONFIG_DIR / "client_secret.json"))
).expanduser()
TOKEN_PATH = Path(
    os.environ.get("GTM_OAUTH_TOKEN", str(CONFIG_DIR / "token.json"))
).expanduser()

# 値をマスクするパラメータキー / 変数名のパターン（measurementId 等は対象外）
import re  # noqa: E402  (依存チェックの後に置きたいので遅延 import)
SECRET_RE = re.compile(
    r"(api[_-]?key|secret|token|password|passwd|credential|private[_-]?key|auth)",
    re.IGNORECASE,
)
MASK = "***REDACTED***"


def die(msg):
    sys.exit(f"ERROR: {msg}")


# --- 認証（OAuth インストール型アプリ）--------------------------------------
def _reject_if_in_repo(path, label):
    """認証ファイルがリポジトリ内にあれば拒否（コミット事故の防止）。"""
    try:
        resolved = path.resolve()
    except OSError:
        return
    if ROOT == resolved or ROOT in resolved.parents:
        die(
            f"{label} がリポジトリ内にあります: {resolved}\n"
            f"  リポジトリ外（例 {CONFIG_DIR}）へ移動してから再実行してください。"
        )


def _warn_if_loose_perms(path, label):
    try:
        mode = path.stat().st_mode
    except OSError:
        return
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        print(
            f"⚠️  {label} が他ユーザーからも読めます（{oct(stat.S_IMODE(mode))}）。"
            f"chmod 600 {path} を推奨します。",
            file=sys.stderr,
        )


def _save_token(creds):
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    # 先に 0600 で空ファイルを作ってから書く（中身が一瞬でも緩い権限で出ないように）
    fd = os.open(str(TOKEN_PATH), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(creds.to_json())
    os.chmod(str(TOKEN_PATH), 0o600)


def load_credentials():
    """OAuth 認証情報を用意する。トークンがあれば再利用、なければブラウザ承認。"""
    _reject_if_in_repo(CLIENT_SECRET_PATH, "client_secret")
    _reject_if_in_repo(TOKEN_PATH, "token")

    creds = None
    if TOKEN_PATH.is_file():
        _warn_if_loose_perms(TOKEN_PATH, "token")
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        except (ValueError, KeyError):
            die(
                f"token ファイルが壊れています: {TOKEN_PATH}\n"
                "  削除して再度承認してください: python3 scripts/fetch_gtm.py logout"
            )

    if creds and creds.valid:
        return creds

    # 期限切れならリフレッシュを試みる
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds)
            return creds
        except RefreshError:
            # リフレッシュ不能（失効・取り消し等）→ 再承認に落とす
            creds = None

    # ここまで来たら新規ブラウザ承認が必要
    if not CLIENT_SECRET_PATH.is_file():
        die(
            f"OAuth クライアントの client_secret が見つかりません: {CLIENT_SECRET_PATH}\n"
            "  GCP コンソールで作成した JSON を上記パスに置くか、環境変数 GTM_OAUTH_CLIENT で指定してください。\n"
            "  手順は docs/gtm-api-setup.md を参照。"
        )
    _warn_if_loose_perms(CLIENT_SECRET_PATH, "client_secret")

    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
    except (ValueError, KeyError):
        die(
            f"client_secret の形式が不正です: {CLIENT_SECRET_PATH}\n"
            "  OAuth クライアントの種類が『デスクトップアプリ』であることを確認してください。"
        )

    print("ブラウザで承認を求めます（初回のみ）。開かない場合は表示される URL を手で開いてください。",
          file=sys.stderr)
    creds = flow.run_local_server(port=0)
    _save_token(creds)
    print(f"承認済み。トークンを保存しました: {TOKEN_PATH}", file=sys.stderr)
    return creds


_session = None


def session():
    global _session
    if _session is None:
        _session = AuthorizedSession(load_credentials())
    return _session


def get(path, **params):
    try:
        r = session().get(f"{BASE}/{path}", params=params or None, timeout=TIMEOUT)
    except RefreshError:
        die(
            "認証情報のリフレッシュに失敗しました。トークンが失効または取り消された可能性があります。\n"
            "  再承認してください: python3 scripts/fetch_gtm.py logout && python3 scripts/fetch_gtm.py accounts"
        )
    if r.status_code == 403:
        die(
            "403 Forbidden。次を確認してください:\n"
            "  - あなたの Google アカウントが GTM コンテナを読める権限を持っているか\n"
            "  - Tag Manager API（tagmanager.googleapis.com）が有効化されているか\n"
            "  - OAuth 同意画面が『内部』、スコープに tagmanager.readonly が含まれているか"
        )
    if r.status_code == 401:
        die(
            "401 Unauthorized。トークンが失効しています。\n"
            "  再承認してください: python3 scripts/fetch_gtm.py logout && python3 scripts/fetch_gtm.py accounts"
        )
    if not r.ok:
        die(f"{r.status_code} {r.reason}: {r.text[:500]}")
    return r.json()


def check_container(container_id):
    if container_id not in ALLOWED_CONTAINERS:
        die(
            f"許可されていないコンテナです: {container_id}\n"
            f"  許可済み: {', '.join(ALLOWED_CONTAINERS)}"
        )
    return container_id


# --- 出力の秘匿化 ------------------------------------------------------------
def redact(node, parent_key=None):
    """GTM パラメータ（{'key':..., 'value':...}）のうち秘匿キーらしき値をマスクする。"""
    if isinstance(node, dict):
        key_name = node.get("key")
        if isinstance(key_name, str) and SECRET_RE.search(key_name) and "value" in node:
            return {**{k: redact(v, k) for k, v in node.items() if k != "value"}, "value": MASK}
        return {k: redact(v, k) for k, v in node.items()}
    if isinstance(node, list):
        return [redact(v, parent_key) for v in node]
    return node


# --- API 呼び出し ------------------------------------------------------------
def live_version(container_id):
    return get(f"accounts/{ACCOUNT_ID}/containers/{container_id}/versions:live")


def param(entity, key):
    for p in entity.get("parameter", []):
        if p.get("key") == key:
            return p.get("value")
    return None


# --- サブコマンド ------------------------------------------------------------
def cmd_accounts(args):
    data = get("accounts")
    accounts = data.get("account", [])
    if not accounts:
        print("アクセス可能なアカウントがありません（権限未反映の可能性あり）")
        return
    for a in accounts:
        mark = "←対象" if a.get("accountId") == ACCOUNT_ID else ""
        print(f"{a.get('accountId'):>12}  {a.get('name')} {mark}")


def cmd_containers(args):
    data = get(f"accounts/{ACCOUNT_ID}/containers")
    for c in data.get("container", []):
        cid = c.get("containerId")
        if cid not in ALLOWED_CONTAINERS:
            continue
        print(f"{cid:>10}  {c.get('publicId'):<14} {c.get('name')}")


def cmd_live(args):
    data = live_version(check_container(args.container))
    if not args.no_redact:
        data = redact(data)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_summary(args):
    cid = check_container(args.container)
    v = live_version(cid)
    tags, triggers, variables = (v.get("tag", []), v.get("trigger", []), v.get("variable", []))
    trigger_names = {t.get("triggerId"): t.get("name") for t in triggers}

    print(f"# コンテナ {cid} ({ALLOWED_CONTAINERS[cid]})")
    print(f"  containerVersionId: {v.get('containerVersionId')}")
    print(f"  name: {v.get('name')}  / fingerprint: {v.get('fingerprint')}")
    print(f"  tags={len(tags)} triggers={len(triggers)} variables={len(variables)}")

    kw = args.filter.lower() if args.filter else None

    print("\n## タグ")
    for t in sorted(tags, key=lambda x: x.get("name", "")):
        name = t.get("name", "")
        if kw and kw not in name.lower() and kw not in t.get("type", "").lower():
            continue
        fires = ", ".join(trigger_names.get(i, i) for i in t.get("firingTriggerId", [])) or "-"
        mid = param(t, "measurementId") or param(t, "measurementIdOverride") or ""
        paused = " [PAUSED]" if t.get("paused") else ""
        print(f"  - {name}{paused}")
        print(f"      type={t.get('type')}" + (f"  measurementId={mid}" if mid else ""))
        print(f"      firing: {fires}")

    print("\n## トリガー")
    for t in sorted(triggers, key=lambda x: x.get("name", "")):
        name = t.get("name", "")
        if kw and kw not in name.lower() and kw not in t.get("type", "").lower():
            continue
        print(f"  - {name}  (type={t.get('type')})")
        for f in t.get("filter", []) + t.get("customEventFilter", []):
            arg0 = param(f, "arg0") or ""
            arg1 = param(f, "arg1") or ""
            print(f"      {arg0} {f.get('type')} {arg1}")

    print("\n## 変数")
    for var in sorted(variables, key=lambda x: x.get("name", "")):
        name = var.get("name", "")
        if kw and kw not in name.lower() and kw not in var.get("type", "").lower():
            continue
        print(f"  - {name}  (type={var.get('type')})")


def cmd_find(args):
    data = live_version(check_container(args.container))
    if not args.no_redact:
        data = redact(data)
    needle = args.keyword.lower()
    hits = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, val in node.items():
                walk(val, f"{path}.{k}")
        elif isinstance(node, list):
            for i, val in enumerate(node):
                walk(val, f"{path}[{i}]")
        elif isinstance(node, str) and needle in node.lower():
            hits.append((path, node))

    walk(data, "$")
    if not hits:
        print(f"'{args.keyword}' に一致する箇所はありません（version {data.get('containerVersionId')}）")
        return
    print(f"# '{args.keyword}' の一致箇所: {len(hits)} 件（version {data.get('containerVersionId')}）")
    for path, value in hits:
        print(f"  {path}\n    {value}")


def cmd_logout(args):
    if TOKEN_PATH.is_file():
        TOKEN_PATH.unlink()
        print(f"トークンを削除しました: {TOKEN_PATH}")
        print("※ Google 側の承認自体を取り消すには、Google アカウント →")
        print("   セキュリティ → サードパーティのアクセス から該当アプリを削除してください。")
    else:
        print(f"トークンはありません: {TOKEN_PATH}")


def main():
    p = argparse.ArgumentParser(description="GTM 読み取り専用フェッチャ（OAuth インストール型アプリ方式）")
    p.add_argument("--container", default=DEFAULT_CONTAINER, help="コンテナID（ホワイトリスト内のみ）")
    p.add_argument("--no-redact", action="store_true", help="秘匿値のマスクを解除（取り扱い注意）")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("accounts", help="アクセス可能なアカウント一覧（疎通確認）").set_defaults(func=cmd_accounts)
    sub.add_parser("containers", help="許可コンテナ一覧").set_defaults(func=cmd_containers)
    sub.add_parser("live", help="ライブ版の生JSON").set_defaults(func=cmd_live)
    sub.add_parser("logout", help="保管中のトークンを削除").set_defaults(func=cmd_logout)

    s = sub.add_parser("summary", help="ライブ版のタグ/トリガー/変数を要約")
    s.add_argument("--filter", help="名前・タイプの部分一致で絞り込み")
    s.set_defaults(func=cmd_summary)

    f = sub.add_parser("find", help="ライブ版をキーワード検索")
    f.add_argument("keyword")
    f.set_defaults(func=cmd_find)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
