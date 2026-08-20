#!/usr/bin/env bash
# gtm-key-store.sh
# ==================
# サービスアカウント鍵を macOS Keychain に保管し、ディスク上の平文を消す。
# キーレス（ADC）運用ができない場合のフォールバック。
#
#   scripts/gtm-key-store.sh store  ~/Downloads/xxx.json   # 登録して元ファイルを削除
#   scripts/gtm-key-store.sh check                          # 登録済みか確認（中身は出さない）
#   scripts/gtm-key-store.sh remove                         # Keychain から削除
#
# 注意: security コマンドの実行中は、同一ユーザーの他プロセスから ps で引数が
# 見えます。実行後は速やかに GCP コンソールで鍵をローテーションできる体制を保つこと。

set -euo pipefail

SERVICE="${GTM_KEYCHAIN_SERVICE:-gtm-readonly}"

die() { echo "ERROR: $*" >&2; exit 1; }

case "${1:-}" in
  store)
    KEY_PATH="${2:-}"
    [ -n "$KEY_PATH" ] || die "鍵ファイルのパスを指定してください"
    [ -f "$KEY_PATH" ] || die "ファイルが見つかりません: $KEY_PATH"

    # リポジトリ内の鍵は受け付けない
    REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
    case "$(cd "$(dirname "$KEY_PATH")" && pwd)" in
      "$REPO_ROOT"*) die "リポジトリ内の鍵は扱えません。リポジトリ外へ移動してください: $KEY_PATH" ;;
    esac

    # サービスアカウント鍵かを検証（内容は出力しない）
    python3 - "$KEY_PATH" <<'PY' || die "サービスアカウントJSONとして不正です"
import json, sys
d = json.load(open(sys.argv[1]))
assert d.get("type") == "service_account", "type が service_account ではありません"
for k in ("client_email", "private_key", "project_id"):
    assert d.get(k), f"{k} がありません"
print(f"  検証OK: {d['client_email']} (project={d['project_id']})")
PY

    # 履歴に残さずに Keychain へ登録（1行化して格納）
    set +o history 2>/dev/null || true
    security add-generic-password -U -s "$SERVICE" -a "$USER" \
      -l "GTM readonly service account key" \
      -w "$(python3 -c 'import json,sys; print(json.dumps(json.load(open(sys.argv[1]))))' "$KEY_PATH")"
    set -o history 2>/dev/null || true
    echo "  Keychain に登録しました（service=$SERVICE）"

    # ディスク上の平文を削除
    rm -P "$KEY_PATH" 2>/dev/null || rm -f "$KEY_PATH"
    echo "  元ファイルを削除しました: $KEY_PATH"
    echo
    echo "  ※ APFS では上書き削除が保証されません。鍵が漏れた懸念があれば"
    echo "     GCP コンソールで鍵を削除して再発行してください。"
    echo "  ※ GOOGLE_APPLICATION_CREDENTIALS を設定している場合は削除してください:"
    echo "     unset GOOGLE_APPLICATION_CREDENTIALS  # ~/.zshrc の行も消す"
    ;;

  check)
    if security find-generic-password -s "$SERVICE" >/dev/null 2>&1; then
      echo "  登録済み: service=$SERVICE"
    else
      echo "  未登録: service=$SERVICE"
      exit 1
    fi
    ;;

  remove)
    security delete-generic-password -s "$SERVICE" >/dev/null
    echo "  Keychain から削除しました（service=$SERVICE）"
    ;;

  *)
    sed -n '2,15p' "$0"
    exit 1
    ;;
esac
