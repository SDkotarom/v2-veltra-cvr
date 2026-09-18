#!/usr/bin/env python3
"""表示速度モニタリング レポートビルダー

data.json を読み、固定テンプレートで HTML を書き出す。
テンプレートはこのファイルの中にあり、週ごとに揺れない。差し替わるのは data.json だけ。

usage: python3 scripts/perf-report/build.py [data.json] [out.html]
"""
import json, sys, datetime
from pathlib import Path

BASE = Path(__file__).parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "data.json"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else BASE / "report.html"

D = json.loads(SRC.read_text(encoding="utf-8"))
defs, pages, weekly, metrics = D["defs"], D["pages"], D["weekly"], D["metrics"]

COLORS = ["#1F6FB2", "#C2410C", "#6D28A8", "#0F766E", "#8A6D1F", "#B3246B"]
COLOR = {p["page_key"]: COLORS[i % len(COLORS)] for i, p in enumerate(pages)}
VCLASS = {"合格": "good", "要改善": "ni", "不良": "poor", "未計測": "nd"}
VEN = {"合格": "Pass", "要改善": "Needs work", "不良": "Poor", "未計測": "No data"}
STATUS_EN = {"ok": "ok", "欠測": "missing", "未収集": "not collected"}


def t(ja, en):
    return f'<span class="ja">{ja}</span><span class="en">{en}</span>'


def fm(v, dec=0, unit="ms"):
    if v is None:
        return "—"
    s = f"{v:,.{dec}f}" if dec else f"{v:,.0f}"
    return s + (f" {unit}" if unit else "")


def verdict(m, v):
    if v is None:
        return "未計測"
    if v <= m["good"]:
        return "合格"
    if v <= m["ni"]:
        return "要改善"
    return "不良"


# ---------------------------------------------------- サマリー: KPI 一瞥

kpi = ""
for m in metrics:
    latest = {p["page_key"]: weekly["metrics"][m["key"]][p["page_key"]][-1] for p in pages}
    vs = [v for v in latest.values() if v is not None]
    n_pass = sum(1 for v in vs if v <= m["good"])
    n_meas = len(vs)
    worst = max(vs) if vs else None
    kpi += f'''<div class="kpi">
<div class="kpi-h">{m["ja"]}<span class="kpi-sub">{t(m["sub_ja"], m["sub_en"])}</span></div>
<div class="kpi-v">{n_pass}<span class="kpi-d"> / {n_meas}</span></div>
<dl class="kpi-f">
<div><dt>{t("合格ライン", "Target")}</dt><dd>{fm(m["good"], m["dec"], m["unit"])}</dd></div>
<div><dt>{t("最も悪い", "Worst")}</dt><dd>{fm(worst, m["dec"], m["unit"])}</dd></div>
</dl></div>'''

tiles = ""
for p in pages:
    cl = VCLASS[p["lcp_verdict"]]
    d = p.get("lcp_delta_ms")
    dt = "—" if d is None else ("+" if d > 0 else "") + f"{d:,}ms"
    dc = "" if d is None else ("up" if d > 0 else "down")
    if p["data_status"] == "未収集":
        sj, se = "収集対象に入っていない", "not in collection"
    elif p["data_status"] == "欠測":
        sj, se = f'{p.get("first_missing_week","")} 以降 欠測', f'missing since {p.get("first_missing_week","")}'
    elif p.get("delta_from_best_ms"):
        sj = f'最速週 {p["best_period_end"]} 比 +{p["delta_from_best_ms"]:,}ms'
        se = f'+{p["delta_from_best_ms"]:,}ms vs best ({p["best_period_end"]})'
    else:
        sj = se = ""
    path = p["url"].replace("https://www.veltra.com", "") or "/"
    tiles += f'''<div class="tile"><div class="tl-h"><span class="dot" style="background:{COLOR[p["page_key"]]}"></span>{t(p["page_ja"], p["page_en"])}</div>
<a class="tl-u" href="{p["url"]}" title="{p["url"]}">{path}</a>
<div class="tl-v">{"—" if p["lcp_p75_ms"] is None else f'{p["lcp_p75_ms"]:,}'}<span class="u">ms</span></div>
<div class="tl-s">{t(sj, se)}</div>
<div class="tl-f"><span class="badge {cl}">{t(p["lcp_verdict"], VEN[p["lcp_verdict"]])}</span><span class="diff {dc}">{t("前週", "vs prev")} {dt}</span></div></div>'''

# 指標ごとのグラフ枠（中身はブラウザ側で描く）
charts = ""
for m in metrics:
    legend = "".join(
        f'<button class="lg" data-metric="{m["key"]}" data-page="{p["page_key"]}" aria-pressed="true">'
        f'<span class="dot" style="background:{COLOR[p["page_key"]]}"></span>{t(p["page_ja"], p["page_en"])}</button>'
        for p in pages if any(v is not None for v in weekly["metrics"][m["key"]][p["page_key"]]))
    charts += f'''<div class="card chart" data-metric="{m["key"]}">
<div class="ch-h"><h3>{m["ja"]} <span class="ch-sub">{t(m["sub_ja"], m["sub_en"])}</span></h3>
<span class="ch-t">{t(f'合格ライン {fm(m["good"], m["dec"], m["unit"])} 以下', f'Target {fm(m["good"], m["dec"], m["unit"])} or under')}</span></div>
<div class="legend">{legend}</div>
<div class="plot" id="plot-{m["key"]}"></div></div>'''

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

prows = "".join(
    f'<tr><td>{t(p["page_ja"], p["page_en"])}</td><td>{fm(p.get("psi_score"),0,"")}</td><td>{fm(p.get("psi_lcp_ms"))}</td></tr>'
    for p in pages)
defrows = "".join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in D["defs_table"])

MET = {m["key"]: m for m in metrics}


def pass_count(m):
    """最新週の「合格ページ数 / 実ユーザー値が取れているページ数」"""
    vs = [weekly["metrics"][m["key"]][p["page_key"]][-1] for p in pages]
    vs = [v for v in vs if v is not None]
    return sum(1 for v in vs if v <= m["good"]), len(vs)


_ps = [p["psi_score"] for p in pages if p.get("psi_score") is not None]
PSI_AVG = round(sum(_ps) / len(_ps)) if _ps else None


def track_row(key):
    if key == "psi_avg":
        return (t(f'PSI Performance 平均（{len(_ps)}ページ）', f'PSI Performance, mean of {len(_ps)} pages'),
                f'{PSI_AVG} / 100' if PSI_AVG is not None else "—",
                t(f'ラボ・{defs["psi_date"]}', f'lab, {defs["psi_date"]}'))
    m = MET[key]
    n, tot = pass_count(m)
    return (t(f'実ユーザー {m["ja"]} 合格ページ', f'Pages passing {m["en"]} (real user)'),
            f'{n} / {tot}',
            t(f'合格ライン {fm(m["good"], m["dec"], m["unit"])} 以下', f'target {fm(m["good"], m["dec"], m["unit"])} or under'))


tracks = ""
for tr in D["tracks"]:
    rows = ""
    for k in tr["auto"]:
        lab, val, src = track_row(k)
        rows += f'<div><dt>{lab}</dt><dd>{val}<span class="trk-s">{src}</span></dd></div>'
    for r in tr["rows"]:
        rows += (f'<div><dt>{t(r["l"]["ja"], r["l"]["en"])}</dt>'
                 f'<dd>{r["v"]}<span class="trk-s">{t(r["s"]["ja"], r["s"]["en"])}</span></dd></div>')
    tk = "".join(f'<a class="chip" href="https://app.clickup.com/t/31108037/{x}">{x}</a>' for x in tr["tickets"])
    gap = (f'<p class="trk-g">{t(tr["gap"]["ja"], tr["gap"]["en"])}</p>' if tr["gap"]["ja"] else "")
    tracks += (f'<div class="trk"><h3>{t(tr["h"]["ja"], tr["h"]["en"])}</h3>'
               f'<p class="trk-b">{t(tr["b"]["ja"], tr["b"]["en"])}</p>'
               f'<dl class="trk-f">{rows}</dl>{gap}'
               f'<div class="yl">{t("出しているもの", "What has shipped")}</div>'
               f'<div class="ifoot">{tk}</div></div>')


def _bi(v, en_key=None):
    """文字列ならそのまま、辞書なら日英に展開する"""
    return v if isinstance(v, str) else t(v["ja"], v["en"])


ST = {"ok": ("稼働中", "running"), "todo": ("未設置", "not set up")}
flow = ""
for i, st in enumerate(D["pipeline"]["stages"]):
    if i:
        flow += '<div class="fa" aria-hidden="true">→</div>'
    boxes = ""
    for it in st["items"]:
        sj, se = ST[it["st"]]
        boxes += (f'<div class="fitem"><b>{_bi(it["n"])}</b>'
                  f'<span class="fbox-d">{_bi(it["d"])}</span>'
                  f'<span class="fbox-f">{_bi(it["f"])}<span class="fbadge {it["st"]}">{t(sj, se)}</span></span></div>')
    flow += (f'<div class="fs"><div class="fs-h">{i+1} {t(st["h"]["ja"], st["h"]["en"])}'
             f'<span class="fs-s">{t(st["sub"]["ja"], st["sub"]["en"])}</span></div>'
             f'<div class="fbox">{boxes}</div></div>')

mtabs = "".join(
    f'<button class="mt" data-m="{m["key"]}" aria-pressed="{"true" if i==0 else "false"}">{m["ja"]}</button>'
    for i, m in enumerate(metrics))

PAYLOAD = json.dumps({
    "weeks": weekly["weeks"], "metrics": weekly["metrics"],
    "meta": {m["key"]: m for m in metrics},
    "pages": [{"key": p["page_key"], "ja": p["page_ja"], "en": p["page_en"],
               "color": COLOR[p["page_key"]]} for p in pages],
    "releases": D["releases"],
}, ensure_ascii=False)

CSS = (BASE / "report.css").read_text(encoding="utf-8")
JS = (BASE / "report.js").read_text(encoding="utf-8")

html = f'''<title>表示速度モニタリング</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap">
<style>{CSS}</style>
<div class="wrap">
<div class="topbar">
<div class="langbar"><button id="btn-ja" aria-pressed="true" onclick="setLang('ja')">日本語</button><button id="btn-en" aria-pressed="false" onclick="setLang('en')">English</button></div>
</div>

<div class="head">
<p class="eyebrow">Veltra ／ {t("表示速度改善", "Web Performance")} ／ {defs["generated_at"][:10]}</p>
<h1>{t("表示速度モニタリング", "Web Performance Monitor")}</h1>
<p class="sub">www.veltra.com — {t(f'実ユーザー p75（CrUX・モバイル）・対象週 {defs["latest_period_end"]}', f'Real-user p75 (CrUX, mobile) · week ending {defs["latest_period_end"]}')}</p>
</div>

<div class="leads">{leads}</div>

<div class="sec"><h2><span class="n">1</span>{t("KPI の現在地", "KPI status")}</h2>
<p class="note">{t(f'分子は合格しているページ数、分母は実ユーザー値が取れているページ数。対象は {defs["denominator"]} ページで、取れていないページは分母にも入らない。', f'Numerator is pages passing; denominator is pages with real-user data. {defs["denominator"]} pages are in scope — those without data are not counted in either.')}</p>
<div class="kpis">{kpi}</div>
<div class="tiles">{tiles}</div>
<p class="note">{t('タイルの数値は LCP。URL単位の CrUX のみを採用し、サイト全体（origin）の値での代用はしていない。', 'Tile figures are LCP. Only URL-level CrUX is used — origin-level values are never substituted.')}</p>
</div>

<div class="sec"><h2><span class="n">2</span>{t("2つの系統で見る", "Two tracks")}</h2>
<p class="note">{t('直し方が違うので分けている。左は読み込みの中身と順番、右は押してから返ってくるまでの待ち時間。数値は最新週。', 'The two need different fixes, so they are tracked apart: what gets loaded and in what order, versus the wait between a tap and a result. Figures are from the latest week.')}</p>
<div class="trks">{tracks}</div>
</div>

<div class="sec"><h2><span class="n">3</span>{t("指標ごとの推移", "Trend by metric")}</h2>
<p class="note">{t('指標ごとに単位が違うため、グラフを分けている。リリースは上の帯にまとめ、各グラフには同じ位置に細い縦線だけ引いている。凡例をクリックするとそのページを外せる（縦軸も引き直す）。', 'Each metric has its own chart because the units differ. Releases are collected in the strip above; the charts carry only a thin vertical line at the same position. Click a legend item to remove that page — the y-axis rescales.')}</p>
<div class="card strip"><div class="ch-h"><h3>{t("リリース", "Releases")}</h3></div>
<div class="plot" id="plot-releases"></div></div>
<div class="chart-grid">{charts}</div>
</div>

<div class="sec"><h2><span class="n">4</span>{t("週ごとの数値とリリース", "Weekly figures and releases")}</h2>
<div class="mtabs">{mtabs}</div>
<p class="note">{t('行は週。リリースがあった週は、その週の行のすぐ下に開閉行が入る。開くとチケットと変更内容が出る。赤字は合格ラインを超えている値、— は欠測。', 'One row per week. A week with releases gets a collapsible row right under it — open it for the tickets and what changed. Red exceeds the target; — means no data.')}</p>
<div class="tw" id="trend-table"></div>
</div>

<div class="sec"><h2><span class="n">5</span>{t("分かったこと", "What we learned")}</h2>
{frows}
</div>

<div class="sec"><h2><span class="n">6</span>{t("課題とやること", "Issues and next steps")}</h2>
{irows}
</div>

<div class="sec"><h2><span class="n">7</span>{t("補足データ", "Supporting data")}</h2>
<div class="tw"><table><tr><th>{t("ページ","Page")}</th><th>{t("PSI スコア","PSI score")}</th><th>PSI LCP</th></tr>{prows}</table></div>
<p class="note">{t(f'PageSpeed Insights（ラボ・{defs["psi_date"]}）。日次でばらつきが大きく、実ユーザー値とは別物。傾向の確認にのみ使う。', f'PageSpeed Insights (lab, {defs["psi_date"]}). High daily variance, not real-user data — direction only.')}</p>
<details><summary>{t("データの定義を見る", "View data definitions")}</summary><div class="tw"><table><tr><th>key</th><th>value</th></tr>{defrows}</table></div></details>
</div>

<div class="sec"><h2><span class="n">8</span>{t("データの流れ", "How the data gets here")}</h2>
<p class="note">{t(D["pipeline"]["note"]["ja"], D["pipeline"]["note"]["en"])}</p>
<div class="flow">{flow}</div>
<p class="note">{t('解釈は集計の段で確定させ、生成の段では触らない。週ごとに数値の読み方が変わらないようにするため。', 'Interpretation is settled in the aggregation step and never revisited when the page is built, so the reading of a figure does not drift week to week.')}</p>
</div>

<a class="linkcard" href="{defs["sheet_url"]}"><div><b>{t("計測スプレッドシート","Measurement spreadsheet")}</b><span>{t("生データと集計タブ（_summary / _defs）","Raw data and the aggregation tabs (_summary / _defs)")}</span></div><span>{t("開く →","Open →")}</span></a>

<footer>
{t(f'集計期間：{defs["period_from"]}〜{defs["latest_period_end"]}（{defs["weeks_covered"]}週）。対象は www.veltra.com・日本語・モバイル。', f'Period: {defs["period_from"]} to {defs["latest_period_end"]} ({defs["weeks_covered"]} weeks). Scope: www.veltra.com, Japanese, mobile.')}<br>
{t(f'数値はすべて計測スプレッドシートの _summary タブから取得（CrUX 収集ブロック {defs["crux_collected_at"]}）。生データの解釈は集計タブ側で確定させており、本レポートでは行っていない。', f'All figures come from the _summary tab of the measurement spreadsheet (CrUX collection block {defs["crux_collected_at"]}). Raw data is interpreted in the aggregation layer, not in this report.')}<br>
{t('CrUX は直近28日間の実ユーザーデータの p75。掲載閾値に満たない URL は値が返らないため、欠測は 0 で埋めず空欄として扱う。判定は本番のみで行い、dev 環境の数値は使わない。', 'CrUX reports p75 over a rolling 28 days. URLs below the reporting threshold return nothing; gaps are left empty, never zero-filled. Judged on production only — dev numbers are not used.')}
</footer>
</div>
<script>window.__PERF={PAYLOAD};</script>
<script>{JS}</script>'''

OUT.write_text(html, encoding="utf-8")
print(f"built {OUT} ({len(html):,} bytes)")
