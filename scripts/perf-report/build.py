#!/usr/bin/env python3
"""表示速度モニタリング レポートビルダー

data.json を読み、固定テンプレートで HTML を書き出す。
テンプレートはこのファイルの中にあり、週ごとに揺れない。差し替わるのは data.json だけ。

usage: python3 scripts/perf-report/build.py [data.json] [out.html]
"""
import json, re, sys, datetime
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


def hint(ja, en):
    """ホバーで出る小さな説明。日英は CSS の attr() で出し分ける"""
    esc = lambda x: x.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
    return f' class="hint" tabindex="0" data-tip-ja="{esc(ja)}" data-tip-en="{esc(en)}"'


GLOSSARY = defs.get("glossary", {})
GL_RE = re.compile(r"\[\[([^\]]+)\]\]")


def expand(x):
    """本文中の [[用語]] を、ホバーで説明が出る語に変える"""
    def rep(m):
        k = m.group(1)
        if k.startswith("UX_DESIGN-"):          # チケットは必ず ClickUp へ
            return f'<a href="https://app.clickup.com/t/31108037/{k}">{k}</a>'
        g = GLOSSARY.get(k)
        return f'<span{hint(g["ja"], g["en"])}>{k}</span>' if g else k
    return GL_RE.sub(rep, x)


def t(ja, en):
    return f'<span class="ja">{expand(ja)}</span><span class="en">{expand(en)}</span>'


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

# 判定に使うのは実ユーザー値が現に取れているページだけ。
# 欠測（AC詳細）と未収集（地域・カテゴリー）は、古い値を持っていても数えない。
LIVE = [p for p in pages if p["data_status"] == "ok"]

BASE_I = weekly["weeks"].index(defs["baseline_period_end"])


def base_value(mk, page_key):
    """起点の週の値。プロジェクト開始時点と比べるために使う"""
    return weekly["metrics"][mk][page_key][BASE_I]


def last_value(mk, page_key):
    """そのページで最後に取れている値。最新週が未収集でも前週の値を使う"""
    for v in reversed(weekly["metrics"][mk][page_key]):
        if v is not None:
            return v
    return None


kpi = ""
for m in metrics:
    vs = [last_value(m["key"], p["page_key"]) for p in LIVE]
    vs = [v for v in vs if v is not None]
    n_pass = sum(1 for v in vs if v <= m["good"])
    n_meas = len(vs)
    bs = [base_value(m["key"], p["page_key"]) for p in LIVE]
    bs = [v for v in bs if v is not None]
    n_base = sum(1 for v in bs if v <= m["good"])
    n_base_meas = len(bs)
    kpi += f'''<div class="kpi">
<div class="kpi-h"><span{hint(m["tip_ja"], m["tip_en"])}>{m["ja"]}</span><span class="kpi-sub">{t(m["sub_ja"], m["sub_en"])}</span></div>
<div class="kpi-v">{n_pass}<span class="kpi-d"> / {n_meas}</span></div>
<dl class="kpi-f">
<div><dt><span{hint("Google が Core Web Vitals で定めている基準値。ベルトラ内の平均でも、競合の平均でもない。", "The threshold Google sets for Core Web Vitals. It is not an average of Veltra pages, nor of competitors.")}>{t("合格ライン", "Target")}</span></dt><dd>{fm(m["good"], m["dec"], m["unit"])}</dd></div>
<div><dt>{t(f'{defs["baseline_period_end"]} 時点', f'As of {defs["baseline_period_end"]}')}</dt><dd>{n_base} / {n_base_meas}</dd></div>
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
    else:
        bv = base_value("lcp", p["page_key"])
        if bv is None or p["lcp_p75_ms"] is None:
            sj = se = ""
        else:
            dv = p["lcp_p75_ms"] - bv
            sign = "+" if dv > 0 else ""
            sj = f'{defs["baseline_period_end"]} 時点から {sign}{dv:,}ms'
            se = f'{sign}{dv:,}ms since {defs["baseline_period_end"]}'
    asof = ""
    if p.get("as_of") and p["as_of"] != defs["latest_period_end"]:
        aw = p["as_of"]
        asof = '<div class="tl-w">' + t(f"{aw} 時点。最新週は未収集", f"as of {aw} — latest week not collected") + "</div>"
    path = p["url"]
    tiles += f'''<div class="tile"><div class="tl-h"><span class="dot" style="background:{COLOR[p["page_key"]]}"></span>{t(p["page_ja"], p["page_en"])}</div>
<a class="tl-u" href="{p["url"]}" title="{p["url"]}" target="_blank" rel="noopener">{path}</a>
<div class="tl-v">{"—" if p["lcp_p75_ms"] is None else f'{p["lcp_p75_ms"]:,}'}<span class="u">ms</span></div>
<div class="tl-s">{t(sj, se)}</div>{asof}
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
    """「合格ページ数 / 実ユーザー値が取れているページ数」。値はページごとの最新の実測値"""
    vs = [last_value(m["key"], p["page_key"]) for p in LIVE]
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


ST = {"ok": ("稼働中", "running"), "warn": ("要確認", "check"), "todo": ("未設置", "not set up")}
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


# ---------------------------------------------------- 構築中パネル / 実績 / ストック

def setup_panel(key):
    """足りていないデータの「構築中」パネル。押すと手順が開く"""
    sp = next((x for x in D["setups"] if x["key"] == key), None)
    if not sp:
        return ""
    def body(lang):
        g = sp[lang]
        L = {"ja": ("なぜ必要か", "誰が何をするか", "いつ取れるか", "手順"),
             "en": ("Why it matters", "Who does what", "When it lands", "Steps")}[lang]
        steps = "".join(
            f'<li><a href="{x["u"]}" target="_blank" rel="noopener">{x["t"]}</a></li>' if x["u"]
            else f'<li>{x["t"]}</li>' for x in g["steps"])
        return (f'<dl class="su-f">'
                f'<div><dt>{L[0]}</dt><dd>{g["why"]}</dd></div>'
                f'<div><dt>{L[1]}</dt><dd>{g["who"]}</dd></div>'
                f'<div><dt>{L[2]}</dt><dd>{g["when"]}</dd></div>'
                f'</dl><div class="yl">{L[3]}</div><ol class="su-s">{steps}</ol>'
                f'<p class="su-n">{g["note"]}</p>')
    return (f'<details class="su"><summary>'
            f'<span class="su-b">{t("構築中", "Being set up")}</span>'
            f'<span class="su-t">{t(sp["ja"]["title"], sp["en"]["title"])}</span>'
            f'<span class="su-c">{t(sp["ja"]["cost"], sp["en"]["cost"])}</span></summary>'
            f'<div class="su-body"><span class="ja">{body("ja")}</span>'
            f'<span class="en">{body("en")}</span></div></details>')


EF = D["effect"]
IV = D["inventory"]
N = {g["key"]: g["n"] for g in IV["groups"]}

# 1 何が起きたか — 4つの数字
HEAD = [
 (t("打った施策", "Shipped"), f'{len(IV["shipped"])}',
  t(f'件（{EF["release_date"]} の1日）', f'changes (all on {EF["release_date"]})')),
 (t("PSI 6ページ平均", "PSI mean, 6 pages"), f'+{EF["overall"]["after"] - EF["overall"]["before"]:.1f}',
  t(f'{EF["overall"]["before"]} → {EF["overall"]["after"]}', f'{EF["overall"]["before"]} → {EF["overall"]["after"]}')),
 (t("手元にある弾", "Waiting in the backlog"), f'{N["backlog"]}',
  t(f'件（うち急ぎ {len(IV["urgent"])} 件）', f'items ({len(IV["urgent"])} urgent)')),
 (t("毎日測れているページ", "Pages measured daily"), f'{len(pages)} / {len(pages)}',
  t(f'{defs["psi_from"][5:]}〜{defs["psi_to"][5:]}', f'{defs["psi_from"][5:]}-{defs["psi_to"][5:]}')),
]
headline = "".join(
    f'<div class="hl"><div class="hl-h">{h}</div><div class="hl-v">{v}</div>'
    f'<div class="hl-s">{sub}</div></div>' for h, v, sub in HEAD)

# 2 効果 — ページ別 before/after
erows = "".join(
    f'<tr><td>{r["p"]}</td><td>{r["before"]:.1f}</td><td>{r["after"]:.1f}</td>'
    f'<td class="{"good" if r["after"] > r["before"] else "bad"}">'
    f'{r["after"] - r["before"]:+.1f}</td></tr>' for r in EF["pages"])

# 4 やったこと
srows = "".join(
    f'<tr><td>{r["d"][5:]}</td>'
    f'<td><a href="https://app.clickup.com/t/31108037/{r["t"]}">{r["t"]}</a></td>'
    f'<td>{t(r["ja"], r["en"])}</td><td>{r["scope"]}</td><td>{r["gain"] or "—"}</td></tr>'
    for r in IV["shipped"])
crows = "".join(
    f'<tr><td><a href="https://app.clickup.com/t/31108037/{r["t"]}">{r["t"]}</a></td>'
    f'<td>{t(r["ja"], r["en"])}</td></tr>' for r in IV["closed"])

# 5 ストック
urows = "".join(
    f'<tr><td><a href="https://app.clickup.com/t/31108037/{r["t"]}">{r["t"]}</a></td>'
    f'<td>{t(r["ja"], r["en"])}</td><td>{r["gain"] or "—"}</td></tr>' for r in IV["urgent"])
grows = "".join(
    f'<tr><td>{t(g["ja"], g["en"])}</td><td>{g["n"]}</td></tr>' for g in IV["groups"])


PAYLOAD = json.dumps({
    "weeks": weekly["weeks"], "metrics": weekly["metrics"],
    "meta": {m["key"]: m for m in metrics},
    "pages": [{"key": p["page_key"], "ja": p["page_ja"], "en": p["page_en"],
               "color": COLOR[p["page_key"]]} for p in pages],
    "releases": D["releases"],
    "psi": D["psi"],
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
<p class="eyebrow">Veltra ／ {t("表示速度改善", "Web Performance")} ／ {defs["generated_at"][:10]}<span class="ver">v{defs["version"]}</span></p>
<h1>{t("表示速度モニタリング", "Web Performance Monitor")}</h1>
<p class="sub">www.veltra.com — {t(f'モバイル・日本語 ／ PSI 日次 {defs["psi_from"][5:]}〜{defs["psi_to"][5:]} ／ 実ユーザー値 〜{defs["latest_period_end"][5:]}', f'Mobile, Japanese · PSI daily {defs["psi_from"][5:]}-{defs["psi_to"][5:]} · real-user through {defs["latest_period_end"][5:]}')}</p>
</div>

<div class="leads">{leads}</div>

<div class="sec"><h2><span class="n">1</span>{t("このプロジェクトで何が起きたか", "What has happened so far")}</h2>
<div class="hls">{headline}</div>
<p class="note">{t(f'起点は {defs["baseline_period_end"]} の週（計測トラッカーに最初の数値を記録した {defs["baseline_note"]} を含む週）。', f'The starting point is the week ending {defs["baseline_period_end"]}, which contains {defs["baseline_note"]} — when the first figures were recorded.')}</p>
</div>

<div class="sec"><h2><span class="n">2</span>{t("本番の数値は動いたか", "Did the production figures move")}</h2>
<p class="note">{t(f'[[PageSpeed Insights]] のスコア。6ページとも毎日測っている。太線は7日の[[移動平均]]、薄い線がその日の値。日ごとの振れが大きいので、太線のほうを見る。', 'PageSpeed Insights scores, measured daily on all six pages. The bold line is a 7-day mean; the faint line is the value for that day. Daily swings are large, so read the bold line.')}</p>
<div class="card"><div class="ch-h"><h3>{t("PSI スコアの推移", "PSI score over time")}</h3>
<span class="ch-t">{t(f'{defs["psi_from"]} 〜 {defs["psi_to"]}', f'{defs["psi_from"]} to {defs["psi_to"]}')}</span></div>
<div class="legend" id="psi-legend"></div>
<div class="plot" id="plot-psi"></div></div>
<div class="tw"><table><tr><th>{t("ページ","Page")}</th><th>{t("リリース前","Before")}</th><th>{t("リリース後","After")}</th><th>{t("差","Change")}</th></tr>{erows}</table></div>
<p class="note">{t(f'{EF["release_date"]} のリリース前5日と後5日の平均。6ページ全部が揃った日だけを使っている。', f'Mean of the five days before and the five days after the {EF["release_date"]} release, using only days where all six pages were measured.')}</p>
</div>

<div class="sec"><h2><span class="n">3</span>{t("触ってからの反応", "Response after you tap")}</h2>
<p class="note">{t('押してから画面が応えるまでの時間。いまは [[ラボ値]] の [[TBT]] で代用している。実ユーザーの数値はこれから取る。', 'The wait between a tap and a response. It is currently stood in for by the lab figure TBT; real-user numbers are on the way.')}</p>
<div class="card"><div class="ch-h"><h3>{t("TBT の推移（代理指標）", "TBT over time (stand-in)")}</h3>
<span class="ch-t">{t("短いほどよい", "Lower is better")}</span></div>
<div class="legend" id="tbt-legend"></div>
<div class="plot" id="plot-tbt"></div></div>
{setup_panel("web-vitals")}
{setup_panel("server-timing")}
</div>

<div class="sec"><h2><span class="n">4</span>{t("やったこと", "What shipped")}</h2>
<div class="card strip"><div class="ch-h"><h3>{t("リリースした日", "Release days")}</h3></div>
<div class="plot" id="plot-releases"></div></div>
{setup_panel("release-log")}
<div class="tw"><table><tr><th>{t("日付","Date")}</th><th>{t("チケット","Ticket")}</th><th>{t("内容","Change")}</th><th>{t("対象","Scope")}</th><th>{t("削減","Saved")}</th></tr>{srows}</table></div>
<details><summary>{t(f'調査・改修で完了したもの（{len(IV["closed"])}件）', f'Investigations and fixes already closed ({len(IV["closed"])})')}</summary><div class="tw"><table><tr><th>{t("チケット","Ticket")}</th><th>{t("内容","Change")}</th></tr>{crows}</table></div></details>
</div>

<div class="sec"><h2><span class="n">5</span>{t("まだ出していないもの", "Found but not shipped")}</h2>
<p class="note">{t(f'調査で見つけて起票したまま、本番に出ていないものが {N["backlog"]} 件ある。うち急ぎが {len(IV["urgent"])} 件。', f'{N["backlog"]} items were found, written up, and have not reached production. {len(IV["urgent"])} of them are marked urgent.')}</p>
<div class="tw"><table><tr><th>{t("チケット","Ticket")}</th><th>{t("内容","Item")}</th><th>{t("削減見込み","Expected saving")}</th></tr>{urows}</table></div>
<details><summary>{t("全49件の内訳", "All 49 items by state")}</summary><div class="tw"><table><tr><th>{t("状態","State")}</th><th>{t("件数","Count")}</th></tr>{grows}</table></div></details>
</div>

<div class="sec"><h2><span class="n">6</span>{t("分かったこと", "What we learned")}</h2>
<div class="finds">{frows}</div>
</div>

<div class="sec"><h2><span class="n">7</span>{t("実ユーザーの数値", "Real-user figures")}</h2>
<p class="note">{t('[[CrUX]] の週次。[[28日ローリング]]の [[p75]] なので、隣り合う週は27日ぶん同じデータを共有している。1週の増減だけを見ても意味がない。', 'Weekly CrUX. Because each figure covers a rolling 28 days, neighbouring weeks share 27 days of data, so one week of movement means little.')}</p>
<div class="tiles">{tiles}</div>
{setup_panel("crux-key")}
<div class="ctrl">
<div class="mtabs"><button class="mt gt" data-g="w" aria-pressed="true">{t("週次","Weekly")}</button><button class="mt gt" data-g="m" aria-pressed="false">{t("月次","Monthly")}</button></div>
<div class="range">
<button class="rg" data-move="-1" aria-label="前の期間 / Previous period">‹</button>
<span class="rg-lab" id="range-label"></span>
<button class="rg" data-move="1" aria-label="次の期間 / Next period">›</button>
<button class="rg rg-today">{t("今週","This week")}</button>
</div>
</div>
<div class="chart-grid">{charts}</div>
<div class="mtabs">{mtabs}</div>
<p class="note">{t('赤字は合格ラインを超えた値。— はその週の値が取れていないところ。', 'Red means the figure missed its target. A dash means there is no figure for that week.')}</p>
<div class="tw" id="trend-table"></div>
</div>

<div class="sec"><h2><span class="n">8</span>{t("課題とやること", "Issues and next steps")}</h2>
{irows}
</div>

<div class="sec"><h2><span class="n">9</span>{t("データの流れと更新", "How the data arrives, and when")}</h2>
<p class="note">{t(D["pipeline"]["note"]["ja"], D["pipeline"]["note"]["en"])}</p>
<div class="flow">{flow}</div>
{setup_panel("schedule")}
<details><summary>{t("データの定義を見る", "View data definitions")}</summary><div class="tw"><table><tr><th>key</th><th>value</th></tr>{defrows}</table></div>
<div class="tw"><table><tr><th>{t("ページ","Page")}</th><th>{t("PSI スコア","PSI score")}</th><th>PSI LCP</th></tr>{prows}</table></div></details>
</div>

<a class="linkcard" href="{defs["sheet_url"]}"><div><b>{t("計測スプレッドシート","Measurement spreadsheet")}</b><span>{t("生データと集計タブ（_summary / _defs）","Raw data and the aggregation tabs (_summary / _defs)")}</span></div><span>{t("開く →","Open →")}</span></a>

<footer>
{t(f'集計期間：{defs["period_from"]}〜{defs["latest_period_end"]}（{defs["weeks_covered"]}週）。対象は www.veltra.com・日本語・モバイル。', f'Period: {defs["period_from"]} to {defs["latest_period_end"]} ({defs["weeks_covered"]} weeks). Scope: www.veltra.com, Japanese, mobile.')}<br>
{t(f'数値はすべて計測スプレッドシートの _summary タブから取得（CrUX 収集ブロック {defs["crux_collected_at"]}）。生データの解釈は集計タブ側で確定させており、本レポートでは行っていない。', f'All figures come from the _summary tab of the measurement spreadsheet (CrUX collection block {defs["crux_collected_at"]}). Raw data is interpreted in the aggregation layer, not in this report.')}<br>
{t('[[CrUX]] は直近28日間の実ユーザーデータの [[p75]]。掲載閾値に満たない URL は値が返らないため、欠測は 0 で埋めず空欄として扱う。判定は本番のみで行い、dev 環境の数値は使わない。', 'CrUX reports p75 over a rolling 28 days. URLs below the reporting threshold return nothing; gaps are left empty, never zero-filled. Judged on production only — dev numbers are not used.')}
</footer>
</div>
<script>window.__PERF={PAYLOAD};</script>
<script>{JS}</script>'''

OUT.write_text(html, encoding="utf-8")
print(f"built {OUT} ({len(html):,} bytes)")
