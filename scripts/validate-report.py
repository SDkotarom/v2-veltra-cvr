#!/usr/bin/env python3
"""
週次レポート検証スクリプト
Phase 3（デプロイ）後に実行し、ページ上の数値とdata.jsonの整合性を検証する。

使い方:
  python3 scripts/validate-report.py --week 2026-w14
  python3 scripts/validate-report.py  # 最新週を自動検出
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ERRORS = []
WARNINGS = []

def error(msg):
    ERRORS.append(msg)
    print(f"  ❌ {msg}")

def warn(msg):
    WARNINGS.append(msg)
    print(f"  ⚠️ {msg}")

def ok(msg):
    print(f"  ✅ {msg}")

def detect_latest_week():
    idx_path = ROOT / "reports-index.json"
    if not idx_path.exists():
        return None
    with open(idx_path) as f:
        idx = json.load(f)
    weeks = idx.get("weeks", [])
    return weeks[-1]["week_id"] if weeks else None

def load_data_json(week_id):
    path = ROOT / "reports" / week_id / "data.json"
    if not path.exists():
        error(f"data.json が見つかりません: {path}")
        return None
    with open(path) as f:
        return json.load(f)

def read_html(path):
    if not path.exists():
        error(f"HTML ファイルが見つかりません: {path}")
        return None
    with open(path) as f:
        return f.read()

# ── 検証1: reports-index.json ──────────────────────
def check_reports_index(week_id, data):
    print("\n[1] reports-index.json")
    idx_path = ROOT / "reports-index.json"
    with open(idx_path) as f:
        idx = json.load(f)
    
    week_entry = None
    for w in idx.get("weeks", []):
        if w["week_id"] == week_id:
            week_entry = w
            break
    
    if not week_entry:
        error(f"reports-index.json に {week_id} のエントリがありません")
        return
    
    ok(f"エントリ存在: {week_id}")
    
    # date_start/date_end がローリング期間ではなく週日付であること
    meta = data.get("meta", {})
    if meta.get("date_start") and week_entry.get("date_start"):
        if week_entry["date_start"] == meta.get("rolling_start"):
            error(f"date_start がローリング開始日と同じ（{week_entry['date_start']}）。対象週の日曜日であるべき")
        elif week_entry["date_start"] == meta.get("date_start"):
            ok(f"date_start 一致: {week_entry['date_start']}")
        else:
            warn(f"date_start: index={week_entry['date_start']} vs meta={meta.get('date_start')}")
    
    # week_label に正しい日付が含まれているか
    label = week_entry.get("week_label", "")
    if label:
        ok(f"week_label: {label}")
    else:
        error("week_label が空です")

# ── 検証2: サマリーページのベースライン数値 ──────────
def check_summary_page(week_id, data):
    print(f"\n[2] reports/{week_id}/index.html ベースライン数値")
    html = read_html(ROOT / "reports" / week_id / "index.html")
    if not html:
        return
    
    bl = data["baseline"]
    
    # セッション数
    sessions = bl["sessions"]
    sessions_m = f"{sessions/1e6:.2f}M"
    sessions_comma = f"{sessions:,}"
    if sessions_comma in html or sessions_m in html:
        ok(f"セッション数: {sessions:,}")
    else:
        error(f"セッション数 {sessions:,} がHTML内に見つかりません")
    
    # CVR
    cvr_pct = f"{bl['cvr']*100:.2f}%"
    if cvr_pct in html:
        ok(f"CVR: {cvr_pct}")
    else:
        # 小数点1桁も許容
        cvr_pct1 = f"{bl['cvr']*100:.1f}%"
        if cvr_pct1 in html:
            ok(f"CVR: {cvr_pct1}")
        else:
            error(f"CVR {cvr_pct} がHTML内に見つかりません")
    
    # 通過率（④→⑤はサマリーページではCVRとして表示されるためスキップ）
    rates = bl["conversion_rates"]
    for key, label in [("1_to_2", "①→②"), ("2_to_3", "②→③"), ("3_to_4", "③→④")]:
        rate = rates.get(key)
        if rate is None:
            continue
        rate_pct = f"{rate*100:.1f}%"
        if rate_pct in html:
            ok(f"{label}: {rate_pct}")
        else:
            error(f"{label} {rate_pct} がHTML内に見つかりません")
    
    # 日付範囲
    meta = data.get("meta", {})
    rolling_start = meta.get("rolling_start", "")
    rolling_end = meta.get("rolling_end", "")
    if rolling_start and rolling_end:
        # 月/日形式に変換（例: 2026-03-09 → 3/9）
        rs = rolling_start.split("-")
        re_ = rolling_end.split("-")
        date_str = f"{int(rs[1])}/{int(rs[2])}〜{int(re_[1])}/{int(re_[2])}"
        if date_str in html:
            ok(f"日付範囲: {date_str}")
        else:
            error(f"日付範囲 '{date_str}' がHTML内に見つかりません")
    
    # 「仮想データ」チェック
    if "仮想データ" in html:
        error("「仮想データ」表記が残っています")
    else:
        ok("「仮想データ」表記なし")

# ── 検証3: 用語統一 ──────────────────────────────
def check_terminology(week_id):
    print(f"\n[3] 用語統一チェック")
    report_dir = ROOT / "reports" / week_id
    bad_terms = {
        "回遊段階": "①→② 流入→AC到達",
        "検討段階": "②→③ AC到達→検討",
        "意向段階": "③→④ 検討→意向",
        "完了段階": "④→⑤ 意向→完了",
    }
    
    found_any = False
    for html_file in sorted(report_dir.glob("*.html")):
        content = html_file.read_text()
        for bad, good in bad_terms.items():
            if bad in content:
                error(f"{html_file.name}: 「{bad}」→「{good}」に統一すべき")
                found_any = True
    
    if not found_any:
        ok("全ファイルで用語統一済み")

# ── 検証4: ボトルネック詳細ページの存在 ──────────────
def check_bottleneck_pages(week_id):
    print(f"\n[4] ボトルネック詳細ページ")
    report_dir = ROOT / "reports" / week_id
    
    for i in range(1, 11):
        path = report_dir / f"bottleneck-{i}.html"
        if path.exists():
            ok(f"bottleneck-{i}.html 存在")
        else:
            error(f"bottleneck-{i}.html が見つかりません")

# ── 検証5: summary-data.json / weekly-summary.json ──
def check_summary_files(week_id, data):
    print(f"\n[5] サマリーJSON")
    
    # weekly-summary.json
    ws_path = ROOT / "weekly-summary.json"
    if ws_path.exists():
        with open(ws_path) as f:
            ws = json.load(f)
        weekly = ws.get("weekly", [])
        # W14 → "202614"
        week_num = week_id.replace("-w", "").replace("-W", "").replace("20", "", 1)
        # Actually format as YYYYWW
        parts = week_id.split("-w")
        if len(parts) == 2:
            expected_key = parts[0] + parts[1]
        else:
            expected_key = week_id
        
        found = any(w.get("week") == expected_key for w in weekly)
        if found:
            ok(f"weekly-summary.json に {expected_key} あり")
        else:
            error(f"weekly-summary.json に {expected_key} がありません")
    else:
        error("weekly-summary.json が見つかりません")
    
    # archive-meta.json
    am_path = ROOT / "archive-meta.json"
    if am_path.exists():
        with open(am_path) as f:
            am = json.load(f)
        if am.get("updatedAt"):
            ok(f"archive-meta.json updatedAt: {am['updatedAt']}")
        else:
            error("archive-meta.json の updatedAt が空")
    else:
        error("archive-meta.json が見つかりません")

# ── 検証6: ファビコンURL ──────────────────────────
def check_favicons(week_id):
    print(f"\n[6] ファビコンURL")
    correct_favicons = {
        "Viator": "cache.vtrcdn.com",
        "アソビュー": "asoview-media.com",
    }
    report_dir = ROOT / "reports" / week_id
    
    for html_file in sorted(report_dir.glob("bottleneck-*.html")):
        content = html_file.read_text()
        for name, domain in correct_favicons.items():
            if name in content and domain not in content:
                warn(f"{html_file.name}: {name} のファビコンURLに {domain} が含まれていません")
    
    ok("ファビコンチェック完了")

# ── 検証7: behavior_context チェック（content.json） ──
def check_behavior_context(week_id):
    print(f"\n[7] behavior_context チェック")
    report_dir = ROOT / "reports" / week_id
    checked = 0
    for i in range(1, 11):
        path = report_dir / f"bottleneck-{i}-content.json"
        if not path.exists():
            continue
        with open(path) as f:
            d = json.load(f)
        bc = d.get('behavior_context')
        if bc is None:
            continue  # 後方互換: なくてもOK
        checked += 1
        if not bc.get('estimated_action'):
            error(f'#{i}: behavior_context.estimated_action が空')
        if len(bc.get('evidence', [])) < 2:
            error(f'#{i}: behavior_context.evidence が2件未満')
        if not bc.get('page_role_check'):
            error(f'#{i}: behavior_context.page_role_check が空')
        if not bc.get('subtraction_check'):
            error(f'#{i}: behavior_context.subtraction_check が空')
    if checked > 0:
        ok(f"behavior_context チェック完了（{checked}件）")
    else:
        ok("behavior_context なし（スキップ）")

# ── メイン ────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="週次レポート検証")
    parser.add_argument("--week", help="検証対象の週（例: 2026-w14）")
    args = parser.parse_args()
    
    week_id = args.week or detect_latest_week()
    if not week_id:
        print("❌ 検証対象の週が特定できません。--week オプションで指定してください。")
        sys.exit(1)
    
    print(f"{'='*60}")
    print(f"  週次レポート検証: {week_id}")
    print(f"{'='*60}")
    
    data = load_data_json(week_id)
    if not data:
        sys.exit(1)
    
    check_reports_index(week_id, data)
    check_summary_page(week_id, data)
    check_terminology(week_id)
    check_bottleneck_pages(week_id)
    check_summary_files(week_id, data)
    check_favicons(week_id)
    check_behavior_context(week_id)
    
    print(f"\n{'='*60}")
    print(f"  結果: ❌ エラー {len(ERRORS)}件 / ⚠️ 警告 {len(WARNINGS)}件")
    print(f"{'='*60}")
    
    if ERRORS:
        print("\n修正が必要な項目:")
        for e in ERRORS:
            print(f"  - {e}")
    
    # 終了コード: エラーがあれば1
    sys.exit(1 if ERRORS else 0)

if __name__ == "__main__":
    main()
