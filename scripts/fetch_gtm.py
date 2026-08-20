#!/usr/bin/env python3
"""
fetch_gtm.py
============
GTM（Google Tag Manager）コンテナ設定の読み取り専用フェッチャ。
管理画面から手作業でエクスポートする運用をなくすためのスクリプト。

前提:
  - サービスアカウントに GTM コンテナ「読み取り」権限のみを付与してあること
  - Tag Manager API（tagmanager.googleapis.com）が有効化されていること
  - 依存: pip install -r scripts/requirements-gtm.txt

認証情報の渡し方（どちらか）:
  1. ファイル経由（ローカル実行の推奨形）
       export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcp/gtm-readonly.json
  2. 環境変数に JSON 文字列を直接（リモート/CI 実行時のみ）
       export GTM_SA_KEY_JSON='{"type":"service_account",...}'
     ※ この場合、鍵はメモリ上のみで扱いディスクに書き出さない

使い方:
    python3 scripts/fetch_gtm.py accounts            # アクセス可能なアカウント確認（疎通テスト）
    python3 scripts/fetch_gtm.py containers          # 許可コンテナの一覧
    python3 scripts/fetch_gtm.py summary             # ライブ版のタグ/トリガー/変数を要約表示
    python3 scripts/fetch_gtm.py live                # ライブ版の生 JSON（秘匿値はマスク）
    python3 scripts/fetch_gtm.py find mobility       # ライブ版をキーワード検索
    python3 scripts/fetch_gtm.py summary --container 8248186

セキュリティ上の設計:
  - スコープは tagmanager.readonly のみ。書き込み系スコープは要求しない
  - ACCOUNT_ID / ALLOWED_CONTAINERS のホワイトリスト外はアクセスしない
  - 鍵ファイルがリポジトリ内にある場合は実行を拒否（コミット事故の防止）
  - 鍵ファイルのパーミッションが緩い場合は警告
  - GTM の定数変数に third-party の API キーが入っていることがあるため、
    出力時に秘匿キーらしき値はデフォルトでマスクする（--no-redact で解除）
"""

import argparse
import json
import os
import re
import stat
import sys
from pathlib import Path

try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
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

SCOPES = ["https://www.googleapis.com/auth/tagmanager.readonly"]
BASE = "https://tagmanager.googleapis.com/tagmanager/v2"
TIMEOUT = 30

# 値をマスクするパラメータキー / 変数名のパターン（measurementId 等は対象外）
SECRET_RE = re.compile(
    r"(api[_-]?key|secret|token|password|passwd|credential|private[_-]?key|auth)",
    re.IGNORECASE,
)
MASK = "***REDACTED***"


def die(msg):
    sys.exit(f"ERROR: {msg}")


# --- 認証 --------------------------------------------------------------------
def load_credentials():
    """環境変数から読み取り専用スコープの資格情報を作る。鍵の内容は一切出力しない。"""
    inline = os.environ.get("GTM_SA_KEY_JSON")
    if inline:
        try:
            info = json.loads(inline)
        except json.JSONDecodeError:
            die("GTM_SA_KEY_JSON が正しい JSON ではありません（鍵の内容は表示しません）")
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not key_path:
        die(
            "認証情報が未設定です。次のいずれかを設定してください:\n"
            "  export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcp/gtm-readonly.json\n"
            "  export GTM_SA_KEY_JSON='<サービスアカウントJSONの中身>'"
        )

    path = Path(os.path.expanduser(key_path)).resolve()
    if not path.is_file():
        die(f"鍵ファイルが見つかりません: {path}")

    # リポジトリ内に鍵を置いた状態での実行は拒否する（コミット事故の防止）
    if ROOT in path.parents or path.parent == ROOT:
        die(
            f"鍵ファイルがリポジトリ内にあります: {path}\n"
            "  ~/.config/gcp/ 配下へ移動してから再実行してください。"
        )

    mode = path.stat().st_mode
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        print(
            f"⚠️  鍵ファイルのパーミッションが緩いです（{oct(stat.S_IMODE(mode))}）。"
            f"chmod 600 {path} を推奨します。",
            file=sys.stderr,
        )

    return service_account.Credentials.from_service_account_file(str(path), scopes=SCOPES)


_session = None


def session():
    global _session
    if _session is None:
        _session = AuthorizedSession(load_credentials())
    return _session


def get(path, **params):
    r = session().get(f"{BASE}/{path}", params=params or None, timeout=TIMEOUT)
    if r.status_code == 403:
        die(
            "403 Forbidden。次を確認してください:\n"
            "  - GTM 管理画面でサービスアカウントに『読み取り』権限を付与済みか\n"
            "  - 権限付与は反映まで数分かかります。5分ほど待って再実行\n"
            "  - Tag Manager API（tagmanager.googleapis.com）が有効化されているか"
        )
    if r.status_code == 401:
        die("401 Unauthorized。鍵が失効しているか、スコープ設定が不正です。")
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


def main():
    p = argparse.ArgumentParser(description="GTM 読み取り専用フェッチャ")
    p.add_argument("--container", default=DEFAULT_CONTAINER, help="コンテナID（ホワイトリスト内のみ）")
    p.add_argument("--no-redact", action="store_true", help="秘匿値のマスクを解除（取り扱い注意）")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("accounts", help="アクセス可能なアカウント一覧（疎通確認）").set_defaults(func=cmd_accounts)
    sub.add_parser("containers", help="許可コンテナ一覧").set_defaults(func=cmd_containers)
    sub.add_parser("live", help="ライブ版の生JSON").set_defaults(func=cmd_live)

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
