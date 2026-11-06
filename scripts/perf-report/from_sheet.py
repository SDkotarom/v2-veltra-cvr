"""計測スプレッドシート（xlsx に書き出したもの）から data.json の psi / weekly / pages を作り直す。

  python3 from_sheet.py <sheet.xlsx> [締め日 YYYY-MM-DD]

- psi は締め日までの日次を、日付×ページに並べ直す
- weekly は (page, period_end) ごとに最新の collected_at の値を採る（SKILL.md の規則どおり）
- 締め日より後の期間の値は使わない（中締めで数字を固定するため）。収集日は問わない
  （CrUX は1週遅れで出るので、9/26 締めの週は 10/4 の収集回に入っている）
"""
import json
import sys
import datetime as dt
from collections import defaultdict
from pathlib import Path

import openpyxl

BASE = Path(__file__).parent
SRC, CUT = Path(sys.argv[1]), (sys.argv[2] if len(sys.argv) > 2 else "9999-12-31")

wb = openpyxl.load_workbook(SRC, data_only=True)


def rows(name):
    it = wb[name].iter_rows(values_only=True)
    head = [str(x) for x in next(it)]
    return [dict(zip(head, r)) for r in it if any(v not in (None, "") for v in r)]


def day(v):
    return v.strftime("%Y-%m-%d") if isinstance(v, (dt.date, dt.datetime)) else str(v).replace("/", "-")


def num(v):
    return None if v in (None, "") else float(v)


D = json.loads((BASE / "data.json").read_text(encoding="utf-8"))
KEYS = [p["page_key"] for p in D["pages"]]

# ---- PSI 日次 ----
psi = [r for r in rows("psi_daily") if day(r["date"]) <= CUT]
dates = sorted({day(r["date"]) for r in psi})
cols = {"score": "perf_score", "lcp": "lcp_ms", "ttfb": "ttfb_ms", "tbt": "tbt_ms",
        "cls": "cls", "field_lcp": "field_lcp_p75_ms"}
out = {"dates": dates}
for k, c in cols.items():
    grid = {p: [None] * len(dates) for p in KEYS}
    for r in psi:
        if r["page"] in grid:
            v = num(r[c])
            if v is not None and k != "cls":
                v = round(v)
            grid[r["page"]][dates.index(day(r["date"]))] = v
    out[k] = grid
D["psi"] = out

# ---- CrUX 週次 ----
crux = [r for r in rows("crux_weekly") if day(r["period_end"]) <= CUT]  # 収集日ではなく、値の期間で切る
latest = {}
for r in crux:
    k = (r["page"], day(r["period_end"]))
    if k not in latest or day(r["collected_at"]) >= day(latest[k]["collected_at"]):
        latest[k] = r
weeks = sorted({w for _, w in latest})
mcol = {"lcp": "lcp_p75_ms", "inp": "inp_p75_ms", "cls": "cls_p75", "ttfb": "ttfb_p75_ms"}
metrics = {}
for m, c in mcol.items():
    cast = (lambda v: v) if m == "cls" else (lambda v: None if v is None else round(v))
    metrics[m] = {p: [cast(num(latest[(p, w)][c])) if (p, w) in latest else None for w in weeks] for p in KEYS}
D["weekly"] = {"weeks": weeks, "metrics": metrics}

# ---- ページごとの最新値 ----
good, ni = D["defs"]["lcp_good"], 4000
for p in D["pages"]:
    k = p["page_key"]
    s = metrics["lcp"][k]
    idx = [i for i, v in enumerate(s) if v is not None]
    if idx and len(weeks) - 1 - idx[-1] >= 4:
        # 最後の値が4週以上前なら「欠測」。古い値を現在地として出さない
        p.update(data_status="欠測", lcp_verdict="未計測", as_of=None,
                 first_missing_week=weeks[idx[-1] + 1],
                 lcp_p75_ms=None, inp_p75_ms=None, cls_p75=None, ttfb_p75_ms=None,
                 lcp_prev_ms=None, lcp_delta_ms=None)
    elif idx:
        i = idx[-1]
        p.update(period_end=weeks[i], as_of=weeks[i], data_status="ok",
                 lcp_p75_ms=s[i], inp_p75_ms=metrics["inp"][k][i],
                 cls_p75=metrics["cls"][k][i], ttfb_p75_ms=metrics["ttfb"][k][i])
        prev = s[idx[-2]] if len(idx) > 1 else None
        p["lcp_prev_ms"] = prev
        p["lcp_delta_ms"] = (s[i] - prev) if prev is not None else None
        p["lcp_verdict"] = "合格" if s[i] <= good else ("要改善" if s[i] <= ni else "不良")
        gaps = [weeks[j] for j in range(idx[0], i) if s[j] is None]
        p["first_missing_week"] = gaps[0] if gaps else ""
    ps = out["score"][k]
    last = [i for i, v in enumerate(ps) if v is not None]
    if last:
        p["psi_score"] = ps[last[-1]]
        p["psi_lcp_ms"] = out["lcp"][k][last[-1]]

D["defs"].update(
    psi_from=dates[0], psi_to=dates[-1], psi_date=dates[-1],
    latest_period_end=weeks[-1], period_from=weeks[0], weeks_covered=len(weeks),
    crux_collected_at=max(day(r["collected_at"]) for r in crux)[:10],
    chart_end=weeks[-1])

(BASE / "data.json").write_text(json.dumps(D, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"psi {dates[0]}〜{dates[-1]}（{len(dates)}日） / crux {weeks[0]}〜{weeks[-1]}（{len(weeks)}週）")
