#!/usr/bin/env python3
"""
雛形から新しいレポートを起こす。機械で決まる値はここで埋め、
判断が必要な箇所は {{...}} のまま残す。

  # 週次サマリー（data.json から KPI と BN タイトルを機械的に埋める）
  python3 .claude/skills/report/scripts/new-report.py --week 2026-w26

  # 単発の分析レポート
  python3 .claude/skills/report/scripts/new-report.py \
      --type analysis --out 2026h1/spot/my-report.html --title "タイトル"

残した {{...}} は check.py が未置換として検出する。
埋め忘れが「そのまま公開」にならないのが、この置き方の目的。
"""

import argparse
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]


def week_reldir(week_id):
    m = re.match(r"^(\d{4})-w(\d+)$", week_id)
    if not m:
        return week_id
    half = "h1" if int(m.group(2)) <= 26 else "h2"
    return f"{m.group(1)}-{half}/{week_id}"


def show(path: Path) -> str:
    """表示用パス。リポジトリ外を指されても落ちないようにする"""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def fmt_int(n):
    return f"{n:,}"


def fmt_pct(x, digits=2):
    return f"{x * 100:.{digits}f}%"


def wow(cur, prev, unit="%"):
    """前週比。増減の向き（up / down）も返す。色の出方を人が決めないための処理"""
    if not prev:
        return "—", ""
    d = (cur - prev) / prev
    arrow = "▲" if d >= 0 else "▼"
    return f"{arrow} {d * 100:+.1f}% WoW", ("up" if d >= 0 else "down")


def weekly_fills(week_id):
    data_path = ROOT / "2026h1/reports" / week_reldir(week_id) / "data.json"
    if not data_path.exists():
        print(f"NG  data.json がありません: {data_path}")
        print("    先に scripts/generate-week.py で Phase 1 のデータ取得を済ませてください")
        sys.exit(1)

    d = json.loads(data_path.read_text(encoding="utf-8"))
    meta = d["meta"]
    cur = d["funnel_7d"]["current_week"]
    prev = d["funnel_7d"].get("prev_week", {})

    def leg(side, key):
        return side.get("funnel", {}).get(key, 0)

    c_sess, p_sess = leg(cur, "session_start_users"), leg(prev, "session_start_users")
    c_pur, p_pur = leg(cur, "purchase"), leg(prev, "purchase")
    c_cvr = (c_pur / c_sess) if c_sess else 0
    p_cvr = (p_pur / p_sess) if p_sess else 0

    s_wow, s_dir = wow(c_sess, p_sess)
    p_wow, p_dir = wow(c_pur, p_pur)
    cvr_delta = (c_cvr - p_cvr) * 100
    cvr_wow = f"{'▲' if cvr_delta >= 0 else '▼'} {cvr_delta:+.2f}pt" if p_cvr else "—"
    cvr_dir = "up" if cvr_delta >= 0 else "down"

    bns = d.get("bottlenecks", [])

    fills = {
        "WEEK_LABEL": meta["week_label"],
        "WEEK_ID": meta["week_id"],
        "WEEK_ID_SHORT": meta["week_id"].split("-")[-1].upper(),
        "PERIOD": f'{meta["date_start"]} 〜 {meta["date_end"]}',
        "KPI1_LABEL": "セッション", "KPI1_VAL": fmt_int(c_sess),
        "KPI1_WOW": s_wow, "KPI1_DIR": s_dir,
        "KPI2_LABEL": "予約数", "KPI2_VAL": fmt_int(c_pur),
        "KPI2_WOW": p_wow, "KPI2_DIR": p_dir,
        "KPI3_LABEL": "CVR", "KPI3_VAL": fmt_pct(c_cvr),
        "KPI3_WOW": cvr_wow, "KPI3_DIR": cvr_dir,
    }
    for i in range(3):
        fills[f"BN{i + 1}_TITLE"] = bns[i]["title"] if i < len(bns) else "{{BN%d_TITLE}}" % (i + 1)

    out = ROOT / "2026h1/reports" / week_reldir(week_id) / "index.html"
    return "weekly-summary.html", out, fills


def analysis_fills(out_rel, title, kicker, period):
    return "analysis-report.html", ROOT / out_rel, {
        "TITLE": title,
        "KICKER": kicker or "スポット分析",
        "PERIOD": period or "{{PERIOD}}",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", choices=["weekly", "analysis"], default="weekly")
    ap.add_argument("--week", help="週 ID（例 2026-w26）")
    ap.add_argument("--out", help="出力先のリポジトリ相対パス（analysis 用）")
    ap.add_argument("--title", help="レポートのタイトル（analysis 用）")
    ap.add_argument("--kicker", help="ヘッダ右上の小見出し（analysis 用）")
    ap.add_argument("--period", help="集計期間（analysis 用）")
    ap.add_argument("--force", action="store_true", help="既存ファイルを上書きする")
    args = ap.parse_args()

    if args.type == "weekly":
        if not args.week:
            ap.error("--week を指定してください")
        tpl_name, out, fills = weekly_fills(args.week)
    else:
        if not (args.out and args.title):
            ap.error("--out と --title を指定してください")
        tpl_name, out, fills = analysis_fills(args.out, args.title, args.kicker, args.period)

    if out.exists() and not args.force:
        print(f"NG  既に存在します: {show(out)}")
        print("    上書きするなら --force。既存レポートの修正は直接編集してください")
        return 1

    text = (SKILL / "assets" / tpl_name).read_text(encoding="utf-8")
    for k, v in fills.items():
        text = text.replace("{{%s}}" % k, str(v))

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")

    left = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text)))
    print(f"作成: {show(out)}  （雛形 {tpl_name}）")
    print(f"\n機械が埋めた値 {len(fills)} 個:")
    for k, v in fills.items():
        s = str(v)
        print(f"  {k:16} {s[:58]}{'…' if len(s) > 58 else ''}")
    print(f"\nここから先は判断が要る箇所 {len(left)} 個:")
    for k in left:
        print(f"  {k}")
    print("\n書き終えたら:")
    print(f"  python3 .claude/skills/report/scripts/check.py {show(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
