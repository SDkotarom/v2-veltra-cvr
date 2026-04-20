#!/usr/bin/env python3
"""
generate-week.py
================
週次レポートの生成を自動化するスクリプト。
機械的・決定論的な処理を担当し、AIによる分析は Claude が別途行う。

使用方法:
    python3 scripts/generate-week.py [--week 2026-w15] [--dry-run]
    python3 scripts/generate-week.py --skeleton --week 2026-w14

オプション:
    --week YYYY-wWW  生成対象の週を指定（省略時は次週を自動検出）
    --dry-run        実際にファイルを書き込まず、実行内容をプレビュー表示
    --skeleton       data.json の bottlenecks 配列から content.json スケルトンを生成
"""

import argparse
import json
import os
import shutil
import subprocess
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
            "week_label": meta["week_label"],
            "date_start": meta["date_start"],
            "date_end": meta["date_end"],
            "rolling_start": meta["rolling_start"],
            "rolling_end": meta["rolling_end"],
            "ga4_property": GA4_PROPERTY,
            "generated_at": meta["generated_at"],
            "note": f"Sun-Sat format. Rolling 28d: {meta['rolling_start']} to {meta['rolling_end']}",
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
# bottleneck content.json スケルトン生成
# ============================================================

# ファネルステージ定義
STAGE_LABELS = {
    "1→2": {"short": "①→②", "full": "①→② 流入→AC到達", "rate_key": "1_to_2"},
    "2→3": {"short": "②→③", "full": "②→③ AC到達→検討", "rate_key": "2_to_3"},
    "3→4": {"short": "③→④", "full": "③→④ 検討→意向", "rate_key": "3_to_4"},
    "4→5": {"short": "④→⑤", "full": "④→⑤ 意向→完了", "rate_key": "4_to_5"},
}

# セグメント表示名
SEGMENT_DISPLAY = {
    "Organic Search": "Organic Search",
    "Paid Search": "Paid Search",
    "Direct": "Direct",
    "Email": "Email",
    "Referral": "Referral",
    "Unassigned": "Unassigned",
    "Cross-network": "Cross-network",
    "Paid Other": "Paid Other",
    "Paid Social": "Paid Social",
    "Organic Social": "Organic Social",
    "Organic Video": "Organic Video",
    "Affiliates": "Affiliates",
    "Organic Shopping": "Organic Shopping",
    "mobile": "Mobile",
    "desktop": "Desktop",
    "tablet": "Tablet",
    "new": "新規ユーザー",
    "returning": "リピーター",
    "hawaii": "ハワイ",
    "bali": "バリ",
    "guam": "グアム",
    "okinawa": "沖縄",
    "europe": "ヨーロッパ",
    "kanto": "関東",
    "kyushu": "九州",
    "ishigaki": "石垣島・宮古島",
    "australia": "オーストラリア",
    "taipei": "台北",
    "singapore": "シンガポール",
}

# セグメントのカテゴリマッピング
SEGMENT_CATEGORY = {
    "Organic Search": "channel", "Paid Search": "channel", "Direct": "channel",
    "Email": "channel", "Referral": "channel", "Unassigned": "channel",
    "Cross-network": "channel", "Paid Other": "channel", "Paid Social": "channel",
    "Organic Social": "channel", "Organic Video": "channel",
    "Affiliates": "channel", "Organic Shopping": "channel",
    "mobile": "device", "desktop": "device", "tablet": "device",
    "new": "new_returning", "returning": "new_returning",
    "hawaii": "area", "bali": "area", "guam": "area", "okinawa": "area",
    "europe": "area", "kanto": "area", "kyushu": "area", "ishigaki": "area",
    "australia": "area", "taipei": "area", "singapore": "area",
}

# 競合6社テンプレート
COMPETITORS = [
    {"name": "Klook", "favicon_url": "https://res.klook.com/image/upload/fl_lossy.progressive,q_85/c_fill,w_32,h_32/v1643959325/blog/klook-favicon.png", "url": "https://www.klook.com/"},
    {"name": "GetYourGuide", "favicon_url": "https://cdn.getyourguide.com/tf/assets/static/favicon/favicon-32x32.png", "url": "https://www.getyourguide.com/"},
    {"name": "Viator", "favicon_url": "https://www.viator.com/favicon.ico", "url": "https://www.viator.com/"},
    {"name": "KKday", "favicon_url": "https://www.kkday.com/favicon.ico", "url": "https://www.kkday.com/"},
    {"name": "アクティビティジャパン", "favicon_url": "https://activityjapan.com/favicon.ico", "url": "https://activityjapan.com/"},
    {"name": "じゃらん", "favicon_url": "https://www.jalan.net/favicon.ico", "url": "https://www.jalan.net/"},
]


def fmt_pct(val: float | None) -> str:
    """0.8284 → "82.84%" 形式にフォーマット。None は "N/A"。"""
    if val is None:
        return "N/A"
    return f"{val * 100:.2f}%"


def fmt_gap(gap: float) -> str:
    """gap 値を "-42.25%" 形式にフォーマット。"""
    sign = "+" if gap > 0 else ""
    return f"{sign}{gap * 100:.1f}%"


def fmt_impact(sessions: int) -> str:
    """impact_sessions を "1,267K / 月" 形式にフォーマット。"""
    if sessions >= 1_000_000:
        return f"{sessions / 1_000:,.0f}K / 月"
    elif sessions >= 1_000:
        return f"{sessions / 1_000:,.0f}K / 月"
    return f"{sessions:,} / 月"


def find_segment_rates(data: dict, segment: str) -> dict | None:
    """data.json の segments からセグメントの rates を探す。"""
    for category in ["channel", "device", "new_returning", "area"]:
        cat_data = data.get("segments", {}).get(category, {})
        if segment in cat_data and "rates" in cat_data[segment]:
            return cat_data[segment]["rates"]
    return None


def find_related_segments(data: dict, segment: str, stage_key: str, limit: int = 3) -> list:
    """同カテゴリから関連セグメントを取得し、ステージレートで比較用リストを返す。"""
    category = SEGMENT_CATEGORY.get(segment)
    if not category:
        return []
    cat_data = data.get("segments", {}).get(category, {})
    results = []
    for seg_name, seg_data in cat_data.items():
        if seg_name == segment:
            continue
        rates = seg_data.get("rates", {})
        rate = rates.get(stage_key)
        if rate is not None:
            results.append((seg_name, rate))
    # レート降順でソート
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]


def make_content_skeleton(bn: dict, idx: int, data: dict) -> dict:
    """
    data.json の bottlenecks[i] から content.json スケルトンを生成する。
    機械的に埋められるフィールドを自動投入し、
    Claude が書くべき分析テキストは "TODO: ..." プレースホルダーにする。
    """
    rank = bn.get("rank", idx + 1)
    title = bn.get("title", "")
    segment = bn.get("segment", "")
    stage = bn.get("stage", "")
    gap = bn.get("gap", 0)
    impact = bn.get("impact_sessions", 0)
    summary = bn.get("summary", "")

    stage_info = STAGE_LABELS.get(stage, {})
    stage_full = stage_info.get("full", stage)
    rate_key = stage_info.get("rate_key", "")

    # tags を自動生成
    tags = [{"label": stage_full, "type": "red"}]
    # セグメント名をタグに追加（複合セグメントは | で分割）
    for seg_part in segment.replace("/", "|").split("|"):
        seg_part = seg_part.strip()
        display = SEGMENT_DISPLAY.get(seg_part, seg_part)
        if display:
            tags.append({"label": display, "type": "default"})

    # deviation, impact_sessions
    deviation = fmt_gap(gap)
    impact_str = fmt_impact(impact)

    # ベースラインレート取得
    baseline_rates = data.get("baseline", {}).get("conversion_rates", {})

    # funnel_overview: セグメントのレートがあれば自動生成
    funnel_overview = None
    seg_rates = find_segment_rates(data, segment)
    if seg_rates and stage != "all":
        display_name = SEGMENT_DISPLAY.get(segment, segment)
        cells = []
        for s_key, s_info in STAGE_LABELS.items():
            s_rate_key = s_info["rate_key"]
            seg_val = seg_rates.get(s_rate_key)
            bl_val = baseline_rates.get(s_rate_key)
            is_target = (s_key == stage)
            cell = {
                "label": s_info["full"],
                "value": fmt_pct(seg_val),
                "sub": f"ベースライン {fmt_pct(bl_val)}"
            }
            if is_target and seg_val is not None and bl_val is not None:
                diff_pp = (seg_val - bl_val) * 100
                cell["sub"] += f" | {diff_pp:+.1f}pp"
                cell["alert"] = True
            cells.append(cell)
        funnel_overview = {
            "title": f"ファネル全体比較（{display_name} vs ベースライン）",
            "cells": cells,
        }

    # funnel_compare: 関連セグメントとの比較
    funnel_compare = []
    bl_rate = baseline_rates.get(rate_key)
    if bl_rate is not None and stage_full:
        funnel_compare.append({
            "label": "全体平均",
            "stage": stage_full.split(" ", 1)[-1] if " " in stage_full else stage_full,
            "value": fmt_pct(bl_rate),
            "sub": "ベースライン",
        })
    if seg_rates and rate_key:
        seg_val = seg_rates.get(rate_key)
        display_name = SEGMENT_DISPLAY.get(segment, segment)
        fc_entry = {
            "label": display_name,
            "stage": stage_full.split(" ", 1)[-1] if " " in stage_full else stage_full,
            "value": fmt_pct(seg_val),
            "sub": f"{deviation} vs 全体",
            "alert": True,
        }
        funnel_compare.append(fc_entry)

    # 同カテゴリの関連セグメントを追加
    related = find_related_segments(data, segment, rate_key)
    for rel_name, rel_rate in related:
        rel_display = SEGMENT_DISPLAY.get(rel_name, rel_name)
        if bl_rate and bl_rate > 0:
            diff = (rel_rate - bl_rate) / bl_rate
            diff_str = f"{diff * 100:+.1f}% vs 全体"
        else:
            diff_str = ""
        funnel_compare.append({
            "label": rel_display,
            "stage": stage_full.split(" ", 1)[-1] if " " in stage_full else stage_full,
            "value": fmt_pct(rel_rate),
            "sub": diff_str,
        })

    # hypotheses テンプレート（3仮説 × 3施策）
    hypotheses = []
    for h_idx, (level, level_label) in enumerate([
        ("h1", "仮説 1（有力）"),
        ("h2", "仮説 2"),
        ("h3", "仮説 3"),
    ]):
        actions = []
        for a_idx in range(3):
            letter = chr(65 + h_idx * 3 + a_idx)  # A,B,C / D,E,F / G,H,I
            actions.append({
                "letter": letter,
                "title": "TODO: 施策タイトル",
                "description": "TODO: 施策の説明",
                "spec_html": "TODO: 開発仕様",
                "impact": f"TODO: {stage_full.split(' ')[0]} +Xpt",
                "prototype": {
                    "before_text": "TODO: 現状の簡潔な説明",
                    "after_text": "TODO: 改善後の簡潔な説明",
                },
                # implementation_check / feasibility は
                # audit-actions.py --auto-fill が自動記入するため省略
            })
        hypotheses.append({
            "level": level,
            "level_label": level_label,
            "title": "TODO: 仮説タイトル",
            "body": "TODO: 仮説の説明",
            "evidence": [
                f"{SEGMENT_DISPLAY.get(segment, segment)} {stage_full}: {fmt_pct(seg_rates.get(rate_key)) if seg_rates and rate_key else 'N/A'}（ベースライン {fmt_pct(bl_rate)}）" if seg_rates else "TODO: 裏付けデータ",
                "TODO: 裏付けデータ2",
                "TODO: 裏付けデータ3",
            ],
            "actions": actions,
        })

    # competitive テンプレート
    competitive = []
    for comp in COMPETITORS:
        competitive.append({
            **comp,
            "feature": "TODO: この競合の該当機能の特徴",
            "detail": "TODO: 注目点の詳細",
        })

    # 組み立て
    skeleton = {
        "number": rank,
        "title": title,
        "tags": tags,
        "deviation": deviation,
        "impact_sessions": impact_str,
        "description_html": f"TODO: {summary}",
    }

    if funnel_overview:
        skeleton["funnel_overview"] = funnel_overview

    skeleton["funnel_compare"] = funnel_compare

    skeleton["drill_down"] = [
        {
            "title": "TODO: ドリルダウン分析1のタイトル",
            "body_html": "TODO: 分析内容HTML",
            "note": "TODO: 要点メモ",
        }
    ]

    skeleton["callout"] = {
        "title": "TODO: 特定結果のタイトル",
        "body_html": "TODO: 特定結果の詳細HTML",
    }

    # behavior_context テンプレート（行動仮説レイヤー）
    bc_display = SEGMENT_DISPLAY.get(segment, segment)
    bc_bl_rate = baseline_rates.get(rate_key)
    skeleton["behavior_context"] = {
        "estimated_action": f"TODO: {bc_display} の {stage_full} でのユーザー推定行動",
        "evidence": [
            f"{bc_display} {stage_full}: {fmt_pct(seg_rates.get(rate_key)) if seg_rates and rate_key else 'N/A'}（ベースライン {fmt_pct(bc_bl_rate)}）" if seg_rates else "TODO: 裏付けデータ1",
            "TODO: 裏付けデータ2",
        ],
        "page_role_check": f"TODO: {stage_full} に該当するページの戦略ガイド上の役割チェック",
        "subtraction_check": "TODO: 情報の引き算で解決できるかチェック",
        "pattern_references": [],
    }

    skeleton["hypo_section_title"] = f"原因仮説 × 3 &amp; 打ち手 × 9"
    skeleton["hypo_section_desc"] = f"なぜ {bc_display} の {stage_full} が低いか？ 仮説をクリックして打ち手・プロトタイプを展開。"

    skeleton["hypotheses"] = hypotheses

    skeleton["competitive"] = competitive
    skeleton["competitive_insight"] = "TODO: 競合比較から得られる示唆"

    skeleton["verification"] = [
        "TODO: チェック項目1",
        "TODO: チェック項目2",
        "TODO: チェック項目3",
    ]
    skeleton["verification_method"] = f"TODO: GA4 で {SEGMENT_DISPLAY.get(segment, segment)} の {stage_full} を検証"

    return skeleton


def step_generate_skeletons(week_dir: str, dry_run: bool) -> None:
    """
    data.json の bottlenecks 配列から bottleneck-N-content.json スケルトンを生成する。
    既存ファイルは上書きしない。
    """
    data_path = os.path.join(week_dir, "data.json")
    print(f"\n[SKELETON] data.json から content.json スケルトン生成")

    data = read_json(data_path)
    if not data:
        print(f"  エラー: {data_path} が見つかりません。先に data.json を生成してください。")
        return

    bottlenecks = data.get("bottlenecks", [])
    if not bottlenecks:
        print(f"  エラー: data.json に bottlenecks 配列がないか空です。")
        return

    print(f"  bottlenecks: {len(bottlenecks)} 件検出")

    generated = 0
    skipped = 0
    for i, bn in enumerate(bottlenecks):
        rank = bn.get("rank", i + 1)
        content_path = os.path.join(week_dir, f"bottleneck-{rank}-content.json")

        if not dry_run and os.path.exists(content_path):
            print(f"  スキップ: bottleneck-{rank}-content.json（既に存在）")
            skipped += 1
            continue

        skeleton = make_content_skeleton(bn, i, data)
        write_json(content_path, skeleton, dry_run)
        generated += 1

        if not dry_run:
            # TODO カウント
            json_str = json.dumps(skeleton, ensure_ascii=False)
            todo_count = json_str.count("TODO:")
            print(f"  生成: bottleneck-{rank}-content.json（TODO: {todo_count} 箇所）")

    print(f"\n  結果: 生成 {generated} / スキップ {skipped} / 合計 {len(bottlenecks)}")


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


def step_generate_index_html(week_dir: str, meta: dict, dry_run: bool) -> None:
    """
    ステップ2.5: 週次サマリーページ index.html のスケルトンを生成する。
    結論 / 論拠 / やるべきこと の3セクション（TODO入り）+ 詳細自動描画プレースホルダ。

    既存の手書きサマリー（/summary.css を参照しているもの）は上書きしない。
    完成済みページの誤上書きを防ぐため。
    """
    index_path = os.path.join(week_dir, "index.html")
    print(f"\n[2.5] 週次サマリー index.html スケルトン生成: {index_path}")

    # Skip if a real summary page already exists (detected by summary.css import).
    if os.path.exists(index_path):
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                existing = f.read()
            if "summary.css" in existing:
                print(f"  スキップ: 既存のサマリーページを検出（summary.css 参照あり）")
                return
        except OSError:
            pass

    week_id = meta["week_id"]
    week_label = meta["week_label"]
    date_start = meta.get("date_start", "")
    date_end = meta.get("date_end", "")

    content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<script src="/auth.js"></script>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="/report.css">
<link rel="stylesheet" href="/summary.css">
<title>{week_label}サマリー | 週次ボトルネック分析</title>
</head>
<body>
<div id="app">
  <div class="card">
    <div class="header-band">
      <div class="logo">V2</div>
      <div class="right">週次サマリー<br><strong>{week_label}</strong></div>
    </div>
    <div style="padding:22px 44px;display:flex;gap:32px;flex-wrap:wrap;font-size:13px;line-height:1.8;color:var(--text2)">
      <div><span style="color:var(--text3);font-weight:700">分析対象</span><br>{week_label} 単週（{date_start} 〜 {date_end}）</div>
      <div><span style="color:var(--text3);font-weight:700">GA4 Property</span><br>347074845</div>
    </div>
  </div>

  <div class="card">
    <div class="sec-tag"><span class="sec-num red">01</span><span class="sec-main">Conclusion — 結論</span></div>
    <div class="summary-hero">
      <div class="summary-kicker">{week_id.upper()} SPOT ANALYSIS</div>
      <div class="summary-headline">
        <!-- TODO: ユーザー行動の観察を主語にした1〜3行ヘッドライン。<em>強調</em>で数字を挟む -->
      </div>
      <div class="summary-sub">
        <!-- TODO: 4〜6行のサブ説明。ユーザーが何を感じ、どこで止まっているかを数字で支える -->
      </div>
      <div class="summary-kpi-strip">
        <div class="skpi">
          <div class="skpi-label">セッション（{week_id.upper()}単週）</div>
          <div class="skpi-val"><!-- TODO --></div>
          <div class="skpi-wow"><!-- TODO: ▲/▼ ±X.X% WoW --></div>
        </div>
        <div class="skpi">
          <div class="skpi-label">予約完了（{week_id.upper()}単週）</div>
          <div class="skpi-val"><!-- TODO --></div>
          <div class="skpi-wow"><!-- TODO --></div>
        </div>
        <div class="skpi">
          <div class="skpi-label">CVR（{week_id.upper()}単週）</div>
          <div class="skpi-val"><!-- TODO --></div>
          <div class="skpi-wow"><!-- TODO --></div>
        </div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="sec-tag"><span class="sec-num">02</span><span class="sec-main">Evidence — 論拠</span></div>
    <div class="sec-big"><!-- TODO: 論拠全体のサマリー一文 --></div>
    <div class="sec-sub"><!-- TODO: 補足 --></div>
    <div class="evidence-grid">
      <!-- TODO: Evidence カード ×3（ユーザー行動 / 乖離 / ユーザー層 の3軸） -->
    </div>
  </div>

  <div class="card">
    <div class="sec-tag"><span class="sec-num">03</span><span class="sec-main">Action — やるべきこと</span></div>
    <div class="sec-big"><!-- TODO: アクション方針 --></div>
    <div class="sec-sub"><!-- TODO --></div>
    <div class="action-list">
      <!-- TODO: Action アイテム ×3（短期 NEW / 中期 既存BN Top3 / 継続監視） -->
    </div>
  </div>

  <div id="summary-detail" style="scroll-margin-top:24px"></div>

  <div class="card">
    <div class="footer">
      <span>VELTRA CVR改善チーム — UIUX Design Squad</span>
      <span><a href="https://analytics.google.com/analytics/web/#/p347074845/reports/reportinghub" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline">GA4: 347074845</a></span>
      <span><!-- TODO: 発行日 --></span>
    </div>
  </div>
</div>
<script src="/nav.js"></script>
<script src="/summary-detail.js"></script>
</body>
</html>
"""
    if dry_run:
        print(f"  [DRY-RUN] 書き込み: {index_path}")
    else:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  生成完了（TODO を Phase 2.9 で埋める）")


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
  python3 scripts/generate-week.py                     # 次週を自動検出して生成
  python3 scripts/generate-week.py --week 2026-w15     # 特定の週を指定して生成
  python3 scripts/generate-week.py --dry-run           # 実行内容をプレビュー
  python3 scripts/generate-week.py --skeleton --week 2026-w14  # content.json スケルトン生成
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
    parser.add_argument(
        "--skeleton",
        action="store_true",
        help="data.json の bottlenecks から bottleneck-N-content.json スケルトンを生成",
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
    # --skeleton モード: content.json スケルトン生成のみ
    # --------------------------------------------------------
    if args.skeleton:
        week_dir = os.path.join(REPORTS_DIR, meta["week_id"])
        step_generate_skeletons(week_dir, args.dry_run)

        # スケルトン生成後に audit-actions.py を自動実行
        if not args.dry_run:
            print(f"\n[AUDIT] implementation_check / feasibility を自動記入中...")
            audit_script = os.path.join(REPO_ROOT, "scripts", "audit-actions.py")
            result = subprocess.run(
                [sys.executable, audit_script, "--week", meta["week_id"], "--auto-fill"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                # サマリー行だけ抜粋して表示
                for line in result.stdout.splitlines():
                    if any(k in line for k in ["総施策数", "重複疑い", "Quick Wins", "高リスク", "施策化レディネス"]):
                        print(f"  {line.strip()}")
            else:
                print(f"  [WARN] audit-actions.py でエラー: {result.stderr[:200]}")

        print("\n" + "=" * 60)
        if args.dry_run:
            print("DRY-RUN 完了。--dry-run を外すと実際に書き込みます。")
        else:
            print("スケルトン生成 + 施策化レビュー自動記入 完了！")
            print(f"\n次のステップ:")
            print(f"  Claude が各ファイルの TODO: を埋める（2-3 ファイルずつ並列推奨）")
            print(f"  プロトタイプは before_text / after_text の短縮形式で記述可能")
            print(f"  ※ implementation_check / feasibility は自動記入済み")
            print(f"  ※ already_exists の施策は代替案に差し替えてください")
        print("=" * 60)
        return

    # --------------------------------------------------------
    # 通常モード: 各ステップを順に実行
    # --------------------------------------------------------
    week_dir = step_create_directory(meta["week_id"], args.dry_run)
    step_generate_data_json(week_dir, meta, args.dry_run)
    step_generate_index_html(week_dir, meta, args.dry_run)
    step_update_reports_index(meta, args.dry_run)
    step_update_archive_meta(args.dry_run)
    step_update_weekly_summary(meta, args.dry_run)

    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY-RUN 完了。--dry-run を外すと実際に書き込みます。")
    else:
        print(f"完了！ {meta['week_id']} のレポート雛形を生成しました。")
        print(f"\n次のステップ:")
        print(f"  1. GA4 MCP でデータをクエリし、data.json を埋める")
        print(f"  2. スケルトン生成: python3 scripts/generate-week.py --skeleton --week {meta['week_id']}")
        print(f"  3. Claude が各 bottleneck-N-content.json の TODO: を埋める（2-3 ファイルずつ並列推奨）")
        print(f"  4. 週次サマリーページ (Phase 2.9): reports/{meta['week_id']}/index.html の TODO を埋める")
        print(f"     - 結論/論拠/やるべきこと の3セクションを手書き（playbook.md Phase 2.9 参照）")
        print(f"     - 詳細部分（ファネル28日・進捗・BN10件）は summary-detail.js が自動描画")
    print("=" * 60)


if __name__ == "__main__":
    main()
