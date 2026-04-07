#!/usr/bin/env python3
"""
generate-week.py
================
週次レポートの生成を自動化するスクリプト。
機械的・決定論的な処理を担当し、AIによる分析は Claude が別途行う。

使用方法:
    python3 scripts/generate-week.py [--week 2026-w15] [--dry-run]

オプション:
    --week YYYY-wWW  生成対象の週を指定（省略時は次週を自動検出）
    --dry-run        実際にファイルを書き込まず、実行内容をプレビュー表示
"""

import argparse
import json
import os
import shutil
import sys
from datetime import date, datetime, timedelta, timezone

# ============================================================
# 定数
# ============================================================

# リポジトリルート（このスクリプトの親ディレクトリ）
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# GA4 プロパティ ID（固定値）
GA4_PROPERTY = "347074845"

# レポート生成時刻のタイムゾーン（日本時間 UTC+9）
JST = timezone(timedelta(hours=9))

# 各種 JSON ファイルのパス
REPORTS_INDEX_PATH = os.path.join(REPO_ROOT, "reports-index.json")
ARCHIVE_META_PATH = os.path.join(REPO_ROOT, "archive-meta.json")
WEEKLY_SUMMARY_PATH = os.path.join(REPO_ROOT, "weekly-summary.json")
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")


# ============================================================
# 週メタデータの計算
# ============================================================

def parse_week_arg(week_str: str) -> tuple[int, int]:
    """
    "2026-w15" 形式の文字列を (year, week) のタプルに変換する。
    不正な形式の場合は SystemExit を送出する。
    """
    try:
        parts = week_str.lower().split("-w")
        if len(parts) != 2:
            raise ValueError
        year = int(parts[0])
        week = int(parts[1])
        if not (1 <= week <= 53):
            raise ValueError
        return year, week
    except (ValueError, IndexError):
        print(f"エラー: --week の形式が不正です: '{week_str}'（例: 2026-w15）", file=sys.stderr)
        sys.exit(1)


def get_next_week() -> tuple[int, int]:
    """
    既存の reports-index.json に記録されている最新週の「次の週」を返す。
    records が空の場合は今週を返す。
    """
    try:
        with open(REPORTS_INDEX_PATH, "r", encoding="utf-8") as f:
            index = json.load(f)
        weeks = index.get("weeks", [])
        if not weeks:
            # データが空の場合は今週を使用
            today = date.today()
            iso = today.isocalendar()
            return iso.year, iso.week
        # 最新エントリの week_id を取得
        latest_id = weeks[-1]["week_id"]  # 例: "2026-w14"
        year, week = parse_week_arg(latest_id)
        # 次の週を計算
        latest_monday = date.fromisocalendar(year, week, 1)
        next_monday = latest_monday + timedelta(weeks=1)
        iso = next_monday.isocalendar()
        return iso.year, iso.week
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        # ファイルが存在しない等の場合は今週を使用
        today = date.today()
        iso = today.isocalendar()
        return iso.year, iso.week


def calc_week_meta(year: int, week: int) -> dict:
    """
    ISO 週番号から週のメタデータを計算して辞書で返す。

    返却キー:
        week_id        : "2026-w15"
        week_label     : "W15（4/5〜4/11）"
        date_start     : ISO 8601 日付文字列（日曜日）
        date_end       : ISO 8601 日付文字列（土曜日）
        rolling_start  : date_end から 27 日前（28日間ローリング期間の開始日）
        rolling_end    : date_end と同じ
        generated_at   : 生成時刻（JST、ISO 8601）

    週期間: 日曜〜土曜（ISO週番号は期間内の月曜で採番）。
    生成タイミング: 毎週月曜 AM 4:00 JST。土曜データを1日寝かせて確定。
    """
    monday = date.fromisocalendar(year, week, 1)   # ISO week の月曜
    sunday = monday - timedelta(days=1)             # 前日 = 週の開始日（日曜）
    saturday = monday + timedelta(days=5)           # 週の終了日（土曜）

    # 28日間ローリング期間: 土曜を基準に過去28日
    rolling_end = saturday
    rolling_start = rolling_end - timedelta(days=27)

    # 生成時刻（JST）
    generated_at = datetime.now(JST).strftime("%Y-%m-%dT%H:%M:%S+09:00")

    # 週ラベル（例: "W15（4/5〜4/11）"）
    week_label = (
        f"W{week}（{sunday.month}/{sunday.day}〜{saturday.month}/{saturday.day}）"
    )

    return {
        "week_id": f"{year}-w{week}",
        "week_label": week_label,
        "date_start": sunday.isoformat(),      # 日曜（週の開始）
        "date_end": saturday.isoformat(),       # 土曜（週の終了）
        "rolling_start": rolling_start.isoformat(),
        "rolling_end": rolling_end.isoformat(),
        "generated_at": generated_at,
    }


# ============================================================
# data.json スケルトン生成
# ============================================================

def make_data_skeleton(meta: dict) -> dict:
    """
    data.json のスケルトン（空値つき）を生成して返す。
    数値フィールドはすべて null（Python では None）で初期化される。
    AI / GA4 クエリによる実データ投入は別途行う。
    """
    return {
        "meta": {
            "week_id": meta["week_id"],
            "date_start": meta["date_start"],
            "date_end": meta["date_end"],
            "rolling_start": meta["rolling_start"],
            "rolling_end": meta["rolling_end"],
            "ga4_property": GA4_PROPERTY,
            "generated_at": meta["generated_at"],
        },
        "baseline": {
            "sessions": None,
            "purchases": None,
            "cvr": None,
            "funnel": {
                "session_start_users": None,
                "ac_page_reach_users": None,
                "calendar_view": None,
                "form_start": None,
                "purchase": None,
            },
            "conversion_rates": {
                "1_to_2": None,
                "2_to_3": None,
                "3_to_4": None,
                "4_to_5": None,
                "wow_pp": {
                    "1_to_2": None,
                    "2_to_3": None,
                    "3_to_4": None,
                    "4_to_5": None,
                },
            },
        },
        "funnel_7d": None,
        "segments": {
            "channel": {},
            "device": {},
            "new_returning": {},
            "area": {},
        },
        "bottlenecks": [],
    }


# ============================================================
# ファイル操作ユーティリティ
# ============================================================

def write_json(path: str, data: dict, dry_run: bool) -> None:
    """JSON を整形して書き込む。dry_run 時はパスのみ表示。"""
    if dry_run:
        print(f"  [DRY-RUN] 書き込み: {path}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")  # ファイル末尾改行


def read_json(path: str) -> dict:
    """JSON ファイルを読み込んで返す。ファイルが存在しない場合は空辞書を返す。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# ============================================================
# 各ステップの実装
# ============================================================

def step_create_directory(week_id: str, dry_run: bool) -> str:
    """
    ステップ1: レポートディレクトリを作成する。
    例: reports/2026-w15/
    """
    week_dir = os.path.join(REPORTS_DIR, week_id)
    print(f"\n[1] ディレクトリ作成: {week_dir}")
    if dry_run:
        print(f"  [DRY-RUN] mkdir -p {week_dir}")
    else:
        os.makedirs(week_dir, exist_ok=True)
        print(f"  作成完了（既存の場合はスキップ）")
    return week_dir


def step_generate_data_json(week_dir: str, meta: dict, dry_run: bool) -> None:
    """
    ステップ2: data.json スケルトンを生成する。
    既に存在する場合は上書きしない（dry_run 時を除く）。
    """
    data_path = os.path.join(week_dir, "data.json")
    print(f"\n[2] data.json 生成: {data_path}")

    if not dry_run and os.path.exists(data_path):
        print(f"  スキップ（既に存在します）")
        return

    skeleton = make_data_skeleton(meta)
    write_json(data_path, skeleton, dry_run)
    if not dry_run:
        print(f"  生成完了")


def step_update_reports_index(meta: dict, dry_run: bool) -> None:
    """
    ステップ3: reports-index.json に新週エントリを追加する。
    同一 week_id が既に存在する場合はスキップ。
    """
    print(f"\n[3] reports-index.json 更新")
    index = read_json(REPORTS_INDEX_PATH)

    # weeks キーがなければ初期化
    if "weeks" not in index:
        index["weeks"] = []
    if "targets" not in index:
        index["targets"] = {"monthly_cvr": 0.018, "annual_cvr": 0.020}

    # 重複チェック
    existing_ids = [w["week_id"] for w in index["weeks"]]
    if meta["week_id"] in existing_ids:
        print(f"  スキップ（{meta['week_id']} は既に存在します）")
        return

    new_entry = {
        "week_id": meta["week_id"],
        "week_label": meta["week_label"],
        "date_start": meta["date_start"],
        "date_end": meta["date_end"],
        "path": f"/reports/{meta['week_id']}/",
        "data_path": f"/reports/{meta['week_id']}/data.json",
    }
    index["weeks"].append(new_entry)
    # 常に時系列順にソート（古い順 → 最新が末尾）
    index["weeks"].sort(key=lambda w: w["week_id"])

    write_json(REPORTS_INDEX_PATH, index, dry_run)
    if not dry_run:
        print(f"  追加完了: {new_entry}")


def step_update_archive_meta(dry_run: bool) -> None:
    """
    ステップ4: archive-meta.json の updatedAt を現在時刻（JST）に更新する。
    """
    print(f"\n[4] archive-meta.json 更新")
    meta = read_json(ARCHIVE_META_PATH)
    now_jst = datetime.now(JST).strftime("%Y-%m-%dT%H:%M:%S+09:00")
    meta["updatedAt"] = now_jst

    write_json(ARCHIVE_META_PATH, meta, dry_run)
    if not dry_run:
        print(f"  updatedAt = {now_jst}")


def step_update_weekly_summary(meta: dict, dry_run: bool) -> None:
    """
    ステップ5: weekly-summary.json に新週のエントリを追加する。
    "week" フィールドは ISO 週番号の YYYYWW 形式（例: "202615"）。
    sessions / purchases / cvr は null で初期化し、GA4 クエリ後に投入する。
    同一週が既に存在する場合はスキップ。
    """
    print(f"\n[5] weekly-summary.json 更新")
    summary = read_json(WEEKLY_SUMMARY_PATH)

    if "weekly" not in summary:
        summary["weekly"] = []

    # YYYYWW 形式の週キーを生成（例: "202615"）
    year_str, week_str = meta["week_id"].split("-w")
    week_key = f"{year_str}{int(week_str):02d}"  # ゼロ埋め2桁

    # 重複チェック
    existing_keys = [str(w.get("week", "")) for w in summary["weekly"]]
    if week_key in existing_keys:
        print(f"  スキップ（{week_key} は既に存在します）")
        return

    new_entry = {
        "week": week_key,
        "sessions": None,
        "purchases": None,
        "cvr": None,
    }
    summary["weekly"].append(new_entry)

    # generated_at も更新
    summary["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    write_json(WEEKLY_SUMMARY_PATH, summary, dry_run)
    if not dry_run:
        print(f"  追加完了: {new_entry}")


# ============================================================
# メインエントリポイント
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="週次レポートの雛形を生成するスクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 scripts/generate-week.py               # 次週を自動検出して生成
  python3 scripts/generate-week.py --week 2026-w15  # 特定の週を指定して生成
  python3 scripts/generate-week.py --dry-run     # 実行内容をプレビュー（書き込みなし）
        """,
    )
    parser.add_argument(
        "--week",
        metavar="YYYY-wWW",
        help="生成する週の指定（例: 2026-w15）。省略時は次週を自動検出",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="ファイルを実際には書き込まず、実行内容をプレビュー表示",
    )
    args = parser.parse_args()

    # --------------------------------------------------------
    # 対象週の決定
    # --------------------------------------------------------
    if args.week:
        year, week = parse_week_arg(args.week)
    else:
        year, week = get_next_week()

    meta = calc_week_meta(year, week)

    print("=" * 60)
    print(f"週次レポート生成{'（DRY-RUN）' if args.dry_run else ''}")
    print("=" * 60)
    print(f"  対象週    : {meta['week_id']}  {meta['week_label']}")
    print(f"  週期間    : {meta['date_start']} 〜 {meta['date_end']}")
    print(f"  28日期間  : {meta['rolling_start']} 〜 {meta['rolling_end']}")
    print(f"  生成時刻  : {meta['generated_at']}")
    print("=" * 60)

    # --------------------------------------------------------
    # 各ステップを順に実行
    # --------------------------------------------------------
    week_dir = step_create_directory(meta["week_id"], args.dry_run)
    step_generate_data_json(week_dir, meta, args.dry_run)
    step_update_reports_index(meta, args.dry_run)
    step_update_archive_meta(args.dry_run)
    step_update_weekly_summary(meta, args.dry_run)

    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY-RUN 完了。--dry-run を外すと実際に書き込みます。")
    else:
        print(f"完了！ {meta['week_id']} のレポート雛形を生成しました。")
        print(f"\n次のステップ:")
        print(f"  1. GA4 でデータをクエリし、data.json を埋める")
        print(f"  2. Claude に分析を依頼し、ボトルネックレポートを生成する")
    print("=" * 60)


if __name__ == "__main__":
    main()
