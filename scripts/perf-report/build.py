#!/usr/bin/env python3
"""表示速度モニタリング レポートビルダー

data.json を読み、固定テンプレートで report.html を書き出す。
テンプレートはこのファイルの中にあり、週ごとに揺れない。
差し替わるのは data.json だけ。

usage: python3 scripts/perf-report/build.py [data.json] [out.html]
"""
import json, sys, datetime
from pathlib import Path

BASE = Path(__file__).parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "data.json"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else BASE / "report.html"

D = json.loads(SRC.read_text(encoding="utf-8"))
defs, pages, weekly = D["defs"], D["pages"], D["weekly"]

COLORS = ["#1F6FB2", "#C2410C", "#6D28A8", "#0F766E", "#8A6D1F", "#9333EA"]
COLOR = {p["page_key"]: COLORS[i % len(COLORS)] for i, p in enumerate(pages)}
VCLASS = {"合格": "good", "要改善": "ni", "不良": "poor", "未計測": "nd"}
VEN = {"合格": "Pass", "要改善": "Needs work", "不良": "Poor", "未計測": "No data"}
STATUS_EN = {"ok": "ok", "欠測": "missing", "未収集": "not collected"}


def t(ja, en):
    return f'<span class="ja">{ja}</span><span class="en">{en}</span>'


def fm(v, unit="ms"):
    if v is None:
        return "—"
    if isinstance(v, float) and unit == "":
        return f"{v:.2f}"
    return f"{v:,}{' ' + unit if unit else ''}"


# ---------------------------------------------------------------- chart

def chart(keys, ymax, W=880, H=290, PL=56, PR=16, PT=20, PB=32):
    weeks = weekly["weeks"]
    d0 = datetime.date.fromisoformat(weeks[0])
    dend = datetime.date.fromisoformat(defs["chart_end"])
    span = (dend - d0).days

    def xf(ds):
        d = datetime.date.fromisoformat(ds)
        return PL + (d - d0).days / span * (W - PL - PR)

    def yf(v):
        return PT + (1 - v / ymax) * (H - PT - PB)

    o = []
    step = 1000 if ymax <= 4000 else 2000
    v = 0
    while v <= ymax:
        y = yf(v)
        o.append(f'<line class="grid" x1="{PL}" y1="{y:.1f}" x2="{W-PR}" y2="{y:.1f}"/>')
        o.append(f'<text class="ax" x="{PL-8}" y="{y+4:.1f}" text-anchor="end">{v:,}</text>')
        v += step

    ty = yf(defs["lcp_good"])
    o.append(f'<line class="target" x1="{PL}" y1="{ty:.1f}" x2="{W-PR}" y2="{ty:.1f}"/>')
    o.append(f'<text class="tgt ja" x="{W-PR}" y="{ty-7:.1f}" text-anchor="end">合格ライン {defs["lcp_good"]:,}ms</text>')
    o.append(f'<text class="tgt en" x="{W-PR}" y="{ty-7:.1f}" text-anchor="end">Target {defs["lcp_good"]:,}ms</text>')

    seen = set()
    for w in weeks:
        d = datetime.date.fromisoformat(w)
        if d.month in seen:
            continue
        seen.add(d.month)
        x = xf(w)
        o.append(f'<text class="ax ja" x="{x:.1f}" y="{H-12}" text-anchor="middle">{d.month}月</text>')
        o.append(f'<text class="ax en" x="{x:.1f}" y="{H-12}" text-anchor="middle">{d.strftime("%b")}</text>')

    for r in D["releases"]:
        rx = xf(r["date"])
        o.append(f'<line class="rel" x1="{rx:.1f}" y1="{PT}" x2="{rx:.1f}" y2="{H-PB}"/>')
    if D["releases"]:
        rx = xf(D["releases"][0]["date"])
        md = datetime.date.fromisoformat(D["releases"][0]["date"])
        o.append(f'<text class="rell ja" x="{rx-6:.1f}" y="{PT+12}" text-anchor="end">{md.month}/{md.day} リリース</text>')
        o.append(f'<text class="rell en" x="{rx-6:.1f}" y="{PT+12}" text-anchor="end">{md.strftime("%b %-d")} release</text>')

    for k in keys:
        vals = weekly["series"].get(k, [])
        segs, pts = [], []
        for i, v in enumerate(vals):
            if v is None:
                if pts:
                    segs.append(pts)
                pts = []
                continue
            pts.append((xf(weeks[i]), yf(v)))
        if pts:
            segs.append(pts)
        for s in segs:
            path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in s)
            o.append(f'<path class="ln" d="{path}" stroke="{COLOR[k]}" fill="none"/>')
        pts_with = [(i, v) for i, v in enumerate(vals) if v is not None]
        if pts_with:
            li = pts_with[-1]
            lx, ly = xf(weeks[li[0]]), yf(li[1])
            o.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="{COLOR[k]}" stroke="var(--panel)" stroke-width="2"/>')
            p = next(p for p in pages if p["page_key"] == k)
            o.append(f'<text class="dl ja" x="{lx-8:.1f}" y="{ly-10:.1f}" text-anchor="end" fill="{COLOR[k]}">{p["page_ja"]}</text>')
            o.append(f'<text class="dl en" x="{lx-8:.1f}" y="{ly-10:.1f}" text-anchor="end" fill="{COLOR[k]}">{p["page_en"]}</text>')
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="LCP p75 weekly trend">' + "".join(o) + "</svg>"


# チャートの分割は値域で自動。3,200ms に収まる系列と、そうでない系列
plotted = [k for k in weekly["series"] if any(v is not None for v in weekly["series"][k])]
low = [k for k in plotted if max(v for v in weekly["series"][k] if v is not None) <= 3200]
high = [k for k in plotted if k not in low]

# ---------------------------------------------------------------- blocks

counts = {}
for p in pages:
    counts[p["lcp_verdict"]] = counts.get(p["lcp_verdict"], 0) + 1
tally_ja = "・".join(f"{k} {v}" for k, v in
                     [(k, counts.get(k, 0)) for k in ["合格", "要改善", "不良", "未計測"]])
tally_en = " · ".join(f"{VEN[k]} {counts.get(k,0)}" for k in ["合格", "要改善", "不良", "未計測"])

tiles = ""
for p in pages:
    cl = VCLASS[p["lcp_verdict"]]
    d = p.get("lcp_delta_ms")
    dt = "—" if d is None else ("+" if d > 0 else "") + f"{d:,}ms"
    dc = "" if d is None else ("up" if d > 0 else "down")
    if p["data_status"] == "未収集":
        sj, se = "収集対象に入っていない", "not in collection"
    elif p["data_status"] == "欠測":
        sj = f'{p.get("first_missing_week","")} 以降 欠測'
        se = f'missing since {p.get("first_missing_week","")}'
    elif p.get("delta_from_best_ms"):
        sj = f'最速週 {p["best_period_end"]} 比 +{p["delta_from_best_ms"]:,}ms'
        se = f'+{p["delta_from_best_ms"]:,}ms vs best week ({p["best_period_end"]})'
    else:
        sj = se = ""
    tiles += f'''<div class="tile"><div class="tl-h"><span class="dot" style="background:{COLOR[p["page_key"]]}"></span>{t(p["page_ja"], p["page_en"])}</div>
<div class="tl-v">{"—" if p["lcp_p75_ms"] is None else f'{p["lcp_p75_ms"]:,}'}<span class="u">ms</span></div>
<div class="tl-s">{t(sj, se)}</div>
<div class="tl-f"><span class="badge {cl}">{t(p["lcp_verdict"], VEN[p["lcp_verdict"]])}</span><span class="diff {dc}">{t("前週", "vs prev")} {dt}</span></div></div>'''

def bad(v, key):
    return ' class="bad"' if v is not None and v > defs[key] else ""

drows = "".join(
    f'<tr><td>{t(p["page_ja"], p["page_en"])}</td>'
    f'<td{bad(p["lcp_p75_ms"],"lcp_good")}>{fm(p["lcp_p75_ms"])}</td>'
    f'<td{bad(p["inp_p75_ms"],"inp_good")}>{fm(p["inp_p75_ms"])}</td>'
    f'<td{bad(p["cls_p75"],"cls_good")}>{fm(p["cls_p75"],"")}</td>'
    f'<td{bad(p["ttfb_p75_ms"],"ttfb_good")}>{fm(p["ttfb_p75_ms"])}</td>'
    f'<td>{t(p["data_status"], STATUS_EN.get(p["data_status"], p["data_status"]))}</td></tr>'
    for p in pages)

prows = "".join(
    f'<tr><td>{t(p["page_ja"], p["page_en"])}</td><td>{fm(p.get("psi_score"),"")}</td><td>{fm(p.get("psi_lcp_ms"))}</td></tr>'
    for p in pages)

rrows = "".join(
    f'<tr><td>{r["date"]}</td><td><a href="https://app.clickup.com/t/31108037/{r["ticket"]}">{r["ticket"]}</a></td>'
    f'<td>{t(r["scope"]["ja"], r["scope"]["en"])}</td><td>{t(r["note"]["ja"], r["note"]["en"])}</td></tr>'
    for r in D["releases"])

leads = "".join(f'<p class="lead">{t(l["ja"], l["en"])}</p>' for l in D["lead"])
frows = "".join(
    f'<div class="find"><div class="fn">{i+1:02d}</div><div><h3>{t(f["h"]["ja"], f["h"]["en"])}</h3>'
    f'<p>{t(f["b"]["ja"], f["b"]["en"])}</p></div></div>' for i, f in enumerate(D["findings"]))

irows = ""
for i, s in enumerate(D["issues"]):
    li = "".join(f'<li>{t(x["ja"], x["en"])}</li>' for x in s["todo"])
    tk = (f'<a href="https://app.clickup.com/t/31108037/{s["ticket"]}">{s["ticket"]}</a>'
          if s.get("ticket") else f'<span class="nt">{t("未起票", "Not filed")}</span>')
    irows += (f'<div class="issue"><div class="ih">{t("課題", "Issue")} {i+1:02d}</div>'
              f'<h3>{t(s["h"]["ja"], s["h"]["en"])}</h3><p>{t(s["b"]["ja"], s["b"]["en"])}</p>'
              f'<div class="yl">{t("やること", "Next steps")}</div><ul>{li}</ul>'
              f'<div class="ifoot"><span class="chip">{t(s["tag"]["ja"], s["tag"]["en"])}</span>{tk}</div></div>')

wk = "<tr><th>" + t("週末日", "Week ending") + "</th>" + "".join(
    f'<th>{t(p["page_ja"], p["page_en"])}</th>' for p in pages if p["page_key"] in plotted) + "</tr>"
for i, w in enumerate(weekly["weeks"]):
    wk += f"<tr><td>{w}</td>" + "".join(
        f'<td>{fm(weekly["series"][k][i], "")}</td>' for k in plotted) + "</tr>"

defrows = "".join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in D["defs_table"])

CSS = (BASE / "report.css").read_text(encoding="utf-8")

html = f'''<title>表示速度モニタリング</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap">
<style>{CSS}</style>
<div class="wrap">
<div class="langbar"><button id="btn-ja" aria-pressed="true" onclick="setLang('ja')">日本語</button><button id="btn-en" aria-pressed="false" onclick="setLang('en')">English</button></div>
<p class="eyebrow">Veltra ／ {t("表示速度改善", "Web Performance")} ／ {defs["generated_at"][:10]}</p>
<h1>{t("表示速度モニタリング", "Web Performance Monitor")}</h1>
<p class="sub">www.veltra.com — {t(f'実ユーザー p75（CrUX・モバイル）・対象週 {defs["latest_period_end"]}', f'Real-user p75 (CrUX, mobile) · week ending {defs["latest_period_end"]}')}</p>
{leads}

<h2><span class="n">1</span>{t("いまの数字", "Where we stand")}</h2>
<p class="tally">{t(f'対象 {defs["denominator"]} ページ — {tally_ja}', f'{defs["denominator"]} pages — {tally_en}')}</p>
<div class="tiles">{tiles}</div>
<p class="note">{t(f'合格ラインは LCP {defs["lcp_good"]:,}ms 以下。URL単位の CrUX のみを採用し、サイト全体（origin）の値での代用はしていない。取れないページは未計測として分母に残している。', f'Target is LCP {defs["lcp_good"]:,}ms or under. Only URL-level CrUX is used — origin-level values are never substituted. Pages without data stay in the denominator as "no data".')}</p>

<div class="card"><h3>{t("合格ライン付近のページ", "Pages near the target")}</h3>{chart(low, 3200)}</div>
{f'<div class="card"><h3>{t("桁が違うページ", "Pages an order of magnitude slower")}</h3><p>{t("縦軸の上限が異なる", "Note the different y-axis")}</p>{chart(high, 10000)}</div>' if high else ''}
<p class="note">{t("破線はリリース日。CrUX は28日間のローリングのため、破線より右に効果が出るまで数週かかる。", "The dashed line marks a release. CrUX rolls over 28 days, so effects take several weeks to appear to the right of it.")}</p>

<div class="tw"><table><tr><th>{t("ページ","Page")}</th><th>LCP</th><th>INP</th><th>CLS</th><th>TTFB</th><th>{t("状態","Status")}</th></tr>{drows}</table></div>
<p class="note">{t(f'合格ライン：INP {defs["inp_good"]}ms 以下／CLS {defs["cls_good"]} 以下／TTFB {defs["ttfb_good"]}ms 以下。赤字は合格ラインを超えている値。LCP と TTFB はそれぞれ独立した p75 のため、差や比率は計算できない。', f'Targets: INP under {defs["inp_good"]}ms, CLS under {defs["cls_good"]}, TTFB under {defs["ttfb_good"]}ms. Red exceeds target. LCP and TTFB are independent p75 values — differences and ratios between them are not meaningful.')}</p>

<h2><span class="n">2</span>{t("分かったこと", "What we learned")}</h2>
{frows}

<h2><span class="n">3</span>{t("課題とやること", "Issues and next steps")}</h2>
{irows}

<h2><span class="n">4</span>{t("補足データ", "Supporting data")}</h2>
<div class="tw"><table><tr><th>{t("ページ","Page")}</th><th>{t("PSI スコア","PSI score")}</th><th>PSI LCP</th></tr>{prows}</table></div>
<p class="note">{t(f'PageSpeed Insights（ラボ・{defs["psi_date"]}）。日次でばらつきが大きく、実ユーザー値とは別物。傾向の確認にのみ使う。', f'PageSpeed Insights (lab, {defs["psi_date"]}). High daily variance, not real-user data — direction only.')}</p>
<div class="tw"><table><tr><th>{t("日付","Date")}</th><th>{t("チケット","Ticket")}</th><th>{t("対象","Scope")}</th><th>{t("内容","Change")}</th></tr>{rrows}</table></div>

<details><summary>{t("データの定義を見る", "View data definitions")}</summary><div class="tw"><table><tr><th>key</th><th>value</th></tr>{defrows}</table></div></details>
<details><summary>{t(f'週次データ（全{len(weekly["weeks"])}週）を表で見る', f'View the full {len(weekly["weeks"])}-week table')}</summary><div class="tw"><table>{wk}</table></div></details>

<a class="linkcard" href="{defs["sheet_url"]}"><div><b>{t("計測スプレッドシート","Measurement spreadsheet")}</b><span>{t("生データと集計タブ（_summary / _defs）","Raw data and the aggregation tabs (_summary / _defs)")}</span></div><span>{t("開く →","Open →")}</span></a>

<footer>
{t(f'集計期間：{defs["period_from"]}〜{defs["latest_period_end"]}（{defs["weeks_covered"]}週）。対象は www.veltra.com・日本語・モバイル。', f'Period: {defs["period_from"]} to {defs["latest_period_end"]} ({defs["weeks_covered"]} weeks). Scope: www.veltra.com, Japanese, mobile.')}<br>
{t(f'数値はすべて計測スプレッドシートの _summary タブから取得（CrUX 収集ブロック {defs["crux_collected_at"]}）。生データの解釈は集計タブ側で確定させており、本レポートでは行っていない。', f'All figures come from the _summary tab of the measurement spreadsheet (CrUX collection block {defs["crux_collected_at"]}). Raw data is interpreted in the aggregation layer, not in this report.')}<br>
{t('CrUX は直近28日間の実ユーザーデータの p75。掲載閾値に満たない URL は値が返らないため、欠測は 0 で埋めず空欄として扱う。判定は本番のみで行い、dev 環境の数値は使わない。', 'CrUX reports p75 over a rolling 28 days. URLs below the reporting threshold return nothing; gaps are left empty, never zero-filled. Judged on production only — dev numbers are not used.')}
</footer>
</div>
<script>
function setLang(l){{
  document.documentElement.setAttribute('data-lang', l);
  document.getElementById('btn-ja').setAttribute('aria-pressed', String(l==='ja'));
  document.getElementById('btn-en').setAttribute('aria-pressed', String(l==='en'));
  try{{ localStorage.setItem('perf-report-lang', l); }}catch(e){{}}
}}
try{{ var s = localStorage.getItem('perf-report-lang'); if(s) setLang(s); }}catch(e){{}}
</script>'''

OUT.write_text(html, encoding="utf-8")
print(f"built {OUT} ({len(html):,} bytes)")
