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

認証情報の渡し方（平文の鍵ファイルは使わない）:

  A. ADC / キーレス（推奨）— サービスアカウント鍵を一切作らない
       gcloud auth application-default login \
         --scopes=https://www.googleapis.com/auth/tagmanager.readonly

  B. macOS Keychain — サービスアカウント鍵を暗号化保管し、実行時のみメモリへ
       scripts/gtm-key-store.sh store ~/Downloads/<key>.json

  C. 環境変数に JSON 文字列（CI / Secret Manager 経由）
       export GTM_SA_KEY_JSON="$(<Secret Manager 等から取得>)"

  平文の鍵ファイル（GOOGLE_APPLICATION_CREDENTIALS）は既定で拒否する。
  tmpfs マウント等の正当な理由がある場合のみ GTM_ALLOW_PLAINTEXT_KEY=1 で明示的に許可。

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
  - 平文の鍵ファイルは既定で拒否（管理者方針: 鍵を平文でおかない）
  - 鍵ファイルがリポジトリ内にある場合は無条件で拒否（コミット事故の防止）
  - GTM の定数変数に third-party の API キーが入っていることがあるため、
    出力時に秘匿キーらしき値はデフォルトでマスクする（--no-redact で解除）
"""

import argparse
import json
import os
import platform
import re
import stat
import subprocess
import sys
from pathlib import Path

try:
    import google.auth
    from google.auth.exceptions import RefreshError
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
KEYCHAIN_SERVICE = os.environ.get("GTM_KEYCHAIN_SERVICE", "gtm-readonly")
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
def _build_sa_credentials(info=None, path=None, origin=""):
    """サービスアカウント資格情報を構築する。失敗しても鍵の内容は出力しない。"""
    try:
        if info is not None:
            return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        return service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
    except (ValueError, KeyError) as e:
        die(
            f"サービスアカウント鍵を読み込めませんでした（{origin}）。\n"
            "  鍵が破損・切り詰められている可能性があります。GCP コンソールで再発行してください。\n"
            f"  原因: {type(e).__name__}"
        )


def _from_inline_env():
    """環境変数の JSON 文字列から。CI や Secret Manager 経由の受け渡し用。"""
    inline = os.environ.get("GTM_SA_KEY_JSON")
    if not inline:
        return None
    try:
        info = json.loads(inline)
    except json.JSONDecodeError:
        die("GTM_SA_KEY_JSON が正しい JSON ではありません（鍵の内容は表示しません）")
    return _build_sa_credentials(info=info, origin="環境変数 GTM_SA_KEY_JSON")


def _from_keychain():
    """macOS Keychain から鍵を取り出す。ディスク上に平文を残さない。"""
    if platform.system() != "Darwin":
        return None
    try:
        r = subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True, text=True, timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None  # 項目未登録。次の方式へフォールバック
    try:
        info = json.loads(r.stdout.strip())
    except json.JSONDecodeError:
        die(
            f"Keychain 項目 '{KEYCHAIN_SERVICE}' の中身が JSON ではありません。"
            " scripts/gtm-key-store.sh store で再登録してください。"
        )
    return _build_sa_credentials(info=info, origin=f"Keychain '{KEYCHAIN_SERVICE}'")


def _from_adc():
    """ADC（キーレス）。gcloud auth application-default login で発行した資格情報。"""
    # GOOGLE_APPLICATION_CREDENTIALS が指す平文鍵を google.auth が黙って拾わないよう退避する
    saved = os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    try:
        creds, _ = google.auth.default(scopes=SCOPES)
    except Exception:
        return None
    finally:
        if saved is not None:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = saved

    quota_project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if quota_project and hasattr(creds, "with_quota_project"):
        creds = creds.with_quota_project(quota_project)
    return creds


def _from_plaintext_file():
    """平文の鍵ファイル。管理者方針により既定で拒否。"""
    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not key_path:
        return None

    path = Path(os.path.expanduser(key_path)).resolve()

    # リポジトリ内の鍵は許可フラグの有無にかかわらず拒否（コミット事故の防止）
    if ROOT in path.parents or path.parent == ROOT:
        die(
            f"鍵ファイルがリポジトリ内にあります: {path}\n"
            "  リポジトリ外へ移動し、Keychain へ登録してください:\n"
            "    scripts/gtm-key-store.sh store <鍵のパス>"
        )

    if os.environ.get("GTM_ALLOW_PLAINTEXT_KEY") != "1":
        die(
            f"平文の鍵ファイルは使用できません: {path}\n"
            "  管理者方針: サービスアカウント鍵を平文でディスクに置かないこと。\n"
            "  次のいずれかに移行してください:\n"
            "    1. キーレス（推奨）: gcloud auth application-default login \\\n"
            "         --scopes=https://www.googleapis.com/auth/tagmanager.readonly\n"
            "       ＋ GCP コンソールで当該サービスアカウント鍵を削除\n"
            "    2. Keychain 保管: scripts/gtm-key-store.sh store " + str(path) + "\n"
            "  tmpfs 等に置いていて意図的に許可する場合のみ GTM_ALLOW_PLAINTEXT_KEY=1"
        )

    if not path.is_file():
        die(f"鍵ファイルが見つかりません: {path}")

    mode = path.stat().st_mode
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        print(
            f"⚠️  鍵ファイルが他ユーザーから読めます（{oct(stat.S_IMODE(mode))}）。"
            f"chmod 600 {path}",
            file=sys.stderr,
        )
    print(
        "⚠️  平文の鍵ファイルを使用中（GTM_ALLOW_PLAINTEXT_KEY=1）。"
        "恒久運用にはしないでください。",
        file=sys.stderr,
    )
    return _build_sa_credentials(path=str(path), origin=str(path))


SOURCES = {
    "env": ("環境変数 GTM_SA_KEY_JSON", _from_inline_env),
    "keychain": ("macOS Keychain", _from_keychain),
    "adc": ("ADC（キーレス）", _from_adc),
    "file": ("平文の鍵ファイル", _from_plaintext_file),
}
SOURCE_ORDER = ["env", "keychain", "adc", "file"]


def load_credentials(prefer="auto"):
    """優先順に認証情報を探す。鍵の内容・トークンは一切出力しない。"""
    order = SOURCE_ORDER if prefer == "auto" else [prefer]
    for name in order:
        label, fn = SOURCES[name]
        creds = fn()
        if creds is not None:
            if os.environ.get("GTM_VERBOSE") == "1":
                print(f"認証方式: {label}", file=sys.stderr)
            return creds

    die(
        "利用できる認証情報がありません。次のいずれかを設定してください:\n"
        "  1. キーレス（推奨）:\n"
        "       gcloud auth application-default login \\\n"
        "         --scopes=https://www.googleapis.com/auth/tagmanager.readonly\n"
        "       export GOOGLE_CLOUD_PROJECT=<PROJECT_ID>\n"
        "  2. Keychain 保管:\n"
        "       scripts/gtm-key-store.sh store <サービスアカウント鍵のパス>\n"
        "  詳細: docs/gtm-api-setup.md"
    )


_session = None


AUTH_PREFER = "auto"


def session():
    global _session
    if _session is None:
        _session = AuthorizedSession(load_credentials(AUTH_PREFER))
    return _session


def get(path, **params):
    try:
        r = session().get(f"{BASE}/{path}", params=params or None, timeout=TIMEOUT)
    except RefreshError as e:
        die(
            "認証情報のリフレッシュに失敗しました。次を確認してください:\n"
            "  - ADC 利用時: gcloud auth application-default login をやり直す\n"
            "  - 鍵利用時: GCP コンソールで鍵が削除・無効化されていないか\n"
            "  - スコープが tagmanager.readonly を含んでいるか\n"
            f"  原因: {type(e).__name__}"
        )
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
        body = r.text[:500]
        if "quota" in body.lower() and "project" in body.lower():
            die(
                "quota project が未設定です（ADC 利用時によく出ます）。\n"
                "  export GOOGLE_CLOUD_PROJECT=<Tag Manager API を有効化したプロジェクトID>\n"
                f"  原文: {body}"
            )
        die(f"{r.status_code} {r.reason}: {body}")
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
    p.add_argument(
        "--auth", default="auto", choices=["auto"] + SOURCE_ORDER,
        help="認証方式を固定（既定 auto: env → keychain → adc の順に探す）",
    )
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
    global AUTH_PREFER
    AUTH_PREFER = args.auth
    args.func(args)


if __name__ == "__main__":
    main()
