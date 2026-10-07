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

RV = D["review"]
def _cell(c):
    if isinstance(c, dict):
        txt = t(c["ja"], c["en"])
        return f'<span class="bdg {c["bdg"]}">{txt}</span>' if c.get("bdg") else txt
    return c


def _lead(x):
    body = ""
    if "table" in x:   # 表（スライド風のまとめ）
        tb = x["table"]
        head = "".join(f"<th>{_cell(c)}</th>" for c in tb["head"])
        rows = "".join("<tr>" + "".join(f"<td>{_cell(c)}</td>" for c in r) + "</tr>" for r in tb["rows"])
        body += f'<div class="tw"><table><tr>{head}</tr>{rows}</table></div>'
        if tb.get("note"):
            body += f'<p class="mut">{t(tb["note"]["ja"], tb["note"]["en"])}</p>'
    if "items" in x:   # 箇条書き
        li = lambda L: "<ul>" + "".join(f"<li>{expand(v)}</li>" for v in L) + "</ul>"
        body += f'<div class="rv-l"><span class="ja">{li(x["items"]["ja"])}</span><span class="en">{li(x["items"]["en"])}</span></div>'
    if "b" in x:
        body += f'<p>{t(x["b"]["ja"], x["b"]["en"])}</p>'
    return f'<div class="rv-p"><h3>{t(x["h"]["ja"], x["h"]["en"])}</h3>{body}</div>'
leads = "".join(_lead(x) for x in RV["parts"])
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


_RT = hint(GLOSSARY["判定"]["ja"], GLOSSARY["判定"]["en"])

EF = D["effect"]
_RD = "・".join(sorted({x["d"][5:].replace("-", "/").lstrip("0") for x in D["inventory"]["shipped"]}))
IV = D["inventory"]
N = {g["key"]: g["n"] for g in IV["groups"]}

# 1 何が起きたか — 4つの数字
HEAD = [
 (t("リリースした施策", "Changes released"), f'{len(IV["shipped"])}',
  t(f'件（{_RD}）', f'released {_RD}')),
 (t("未リリースの施策案", "Not yet released"), f'{N["backlog"]}',
  t(f'件（うち急ぎ {len(IV["urgent"])} 件）', f'items, {len(IV["urgent"])} urgent')),
]
headline = "".join(
    f'<div class="hl"><div class="hl-h">{h}</div><div class="hl-v">{v}</div>'
    f'<div class="hl-s">{sub}</div></div>' for h, v, sub in HEAD)

# 2 効果 — ページ別 before/after
def _band(v):
    return ("低", "Low") if v < 50 else (("普通", "Average") if v < 90 else ("高", "High"))
def _bk(v):
    return "slow" if v < 50 else ("mid" if v < 90 else "fast")
TB = EF["tbt"]
VD = {"fast": ("速くなった", "Faster", "up", "good"), "slow": ("遅くなった", "Slower", "down", "bad"),
      "same": ("変化なし", "No change", "flat", "")}
_ORD = {"fast": 0, "same": 1, "slow": 2}

def _md(a, b):
    return f'{a[5:].replace("-", "/").lstrip("0")}〜{b[5:].replace("-", "/").lstrip("0")}'
WIN = f'リリース前 {_md(*EF["pre"])}／直後 {_md(*EF["mid"])}／月末 {_md(*EF["post"])}'
WIN_EN = f'before {_md(*EF["pre"])}, just after {_md(*EF["mid"])}, month end {_md(*EF["post"])}'

def _row(r, unit, fmt, rating=""):
    ja, en, bc, dc = VD[r["verdict"]]
    diff = r["after"] - r["before"]
    return (f'<tr><td>{r["p"]}</td><td><span class="bdg {bc}">{t(ja, en)}</span></td>'
            f'<td class="{dc}">{fmt(diff, True)}{unit}</td>'
            f'<td>{fmt(r["before"])}{unit} → {fmt(r["mid"])}{unit} → <b>{fmt(r["after"])}{unit}</b></td>'
            f'<td>&plusmn;{fmt(r["sd"])}{unit}</td>{rating}</tr>')

_pt = lambda v, sign=False: f'{v:+.1f}' if sign else f'{v:.1f}'
_ms = lambda v, sign=False: f'{v:+,}' if sign else f'{v:,}'
_key = lambda x: (_ORD[x["verdict"]], -abs(x["after"] - x["before"]))
erows = "".join(_row(r, "点", _pt, f'<td><span class="bdg b-{_bk(r["after"])}">{t(*_band(r["after"]))}</span></td>')
                for r in sorted(EF["pages"], key=_key))
trows = "".join(_row(r, "ms", _ms) for r in sorted(TB["pages"], key=_key))
_cnt = lambda rs: {k: sum(1 for r in rs if r["verdict"] == k) for k in VD}
EC, TC = _cnt(EF["pages"]), _cnt(TB["pages"])

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



# 週次メモ。新しい週を開いた状態で置き、過去の週は畳む
def _ul(items):
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

def _memo_body(m, lang):
    L = {"ja": ("リリース", "数値", "考察", "次週"), "en": ("Released", "Figures", "Reading", "Next week")}[lang]
    _lk = lambda x: re.sub(r"(?<!\[\[)(UX_DESIGN-\d+)(?!\]\])", r"[[\1]]", x)  # チケットは全部 ClickUp へ
    return "".join(f'<div class="wm-r"><div class="wm-k">{k}</div><div class="wm-v">{_ul([expand(_lk(x)) for x in m[f][lang]])}</div></div>'
                   for k, f in zip(L, ("rel", "num", "obs", "nxt")))

memos = ""
for i, m in enumerate(D["memos"]):
    rng = f'{m["from"][5:].replace("-", "/")}〜{m["to"][5:].replace("-", "/")}'
    memos += (f'<details class="wm"{" open" if i == 0 else ""}><summary>'
              f'<span class="wm-w">{m["week"]}</span><span class="wm-d">{rng}</span>'
              f'<span class="wm-s">{t(m["obs"]["ja"][0], m["obs"]["en"][0])}</span></summary>'
              f'<div class="wm-b"><span class="ja">{_memo_body(m, "ja")}</span>'
              f'<span class="en">{_memo_body(m, "en")}</span></div></details>')

# 操作への反応：本番で測った値
import statistics as _st
rmrows = ""
for r in D.get("react_measured", []):
    b, a = _st.mean(r["before"]), _st.mean(r["after"])
    from decimal import Decimal, ROUND_HALF_UP
    _r = lambda v: Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    bm, am = _r(_st.median(r["before"])), _r(_st.median(r["after"]))
    rmrows += (f'<tr><td>{t(r["what"]["ja"], r["what"]["en"])}</td>'
               f'<td><a href="https://app.clickup.com/t/31108037/{r["t"]}">{r["t"]}</a><br><span class="mut">{r["date"][5:].replace("-", "/")}</span></td>'
               f'<td>{b:.2f}s → <b>{a:.2f}s</b></td><td>{bm:.2f}s → {am:.2f}s</td>'
               f'<td class="good">{a - b:+.2f}s</td></tr>')


# 後半の方針タブ
SG = D["strategy"]
def _li(items):
    return "<ul>" + "".join(f"<li>{expand(_lk2(x))}</li>" for x in items) + "</ul>"
import re as _re
_lk2 = lambda x: _re.sub(r"(?<!\[\[)(UX_DESIGN-\d+)(?!\]\])", r"[[\1]]", x)
def _bil(items):
    return f'<span class="ja">{_li(items["ja"])}</span><span class="en">{_li(items["en"])}</span>'
def _cell(c):
    return c if isinstance(c, str) else t(c["ja"], c["en"])
_views = ""
for b in SG["views"]["blocks"]:
    tb = ""
    if "table" in b:
        head, *body = b["table"]
        tb = ('<div class="tw"><table><tr>' + "".join(f"<th>{_cell(c)}</th>" for c in head) + "</tr>"
              + "".join("<tr>" + "".join(f"<td>{_cell(c)}</td>" for c in r) + "</tr>" for r in body) + "</table></div>")
    _views += f'<div class="pl-b"><h4>{t(b["h"]["ja"], b["h"]["en"])}</h4>{tb}<div class="rv-l">{_bil(b["items"])}</div></div>'
_crows = "".join(
    f'<tr><td>{i+1}</td><td><a href="https://app.clickup.com/t/31108037/{r["t"]}">{r["t"]}</a></td>'
    f'<td>{t(r["d"]["ja"], r["d"]["en"])}</td><td>{t(r["why"]["ja"], r["why"]["en"])}</td></tr>'
    for i, r in enumerate(SG["cands"]["rows"]))
def _sec(key):
    x = SG[key]
    return f'<div class="sec pl"><h3 class="sh">{t(x["h"]["ja"], x["h"]["en"])}</h3><div class="rv-l">{_bil(x["items"])}</div></div>'

def _classify():
    x = SG["classify"]
    head, *body = x["table"]
    tb = ('<div class="tw"><table class="cls"><tr>' + "".join(f"<th>{_cell(c)}</th>" for c in head) + "</tr>"
          + "".join("<tr>" + "".join(f"<td>{_cell(c)}</td>" for c in r) + "</tr>" for r in body) + "</table></div>")
    return (f'<div class="sec pl"><h3 class="sh">{t(x["h"]["ja"], x["h"]["en"])}</h3>'
            f'<div class="rv-l">{_bil(x["items"])}</div>{tb}'
            f'<h4 class="sh">{t(x["add"]["h"]["ja"], x["add"]["h"]["en"])}</h4>'
            f'<div class="rv-l">{_bil(x["add"]["items"])}</div></div>')

PLAN = f'''<div class="rv-h"><h2>{t(SG["title"]["ja"], SG["title"]["en"])}</h2><span class="rv-m">{t(SG["meta"]["ja"], SG["meta"]["en"])}</span></div>
{_sec("status")}
{_classify()}
<div class="sec pl"><h3 class="sh">{t(SG["views"]["h"]["ja"], SG["views"]["h"]["en"])}</h3>{_views}</div>
<div class="sec pl"><h3 class="sh">{t(SG["cands"]["h"]["ja"], SG["cands"]["h"]["en"])}</h3>
<div class="tw"><table><tr><th>{t("順","No.")}</th><th>{t("チケット","Ticket")}</th><th>{t("内容","What")}</th><th>{t("なぜ先か","Why first")}</th></tr>{_crows}</table></div>
<p class="note">{t(SG["cands"]["note"]["ja"], SG["cands"]["note"]["en"])}</p></div>
{_sec("extra")}
{_sec("ideas")}
{_sec("goals")}
{_sec("asks")}'''

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

<nav class="ptabs" role="tablist">
<button class="pt" data-tab="report" aria-selected="true">{t("レポート", "Report")}</button>
<button class="pt" data-tab="plan" aria-selected="false">{t("後半の方針", "Second-half plan")}</button>
</nav>
<div class="pane" data-pane="plan" hidden><div class="rv">{PLAN}</div></div>
<div class="pane" data-pane="report">
<div class="rv">
<div class="rv-h"><h2>{t(RV["h"]["ja"], RV["h"]["en"])}</h2>
<span class="rv-m">{t(f'対象期間 {RV["period"]["from"]} 〜 {RV["period"]["to"]} ／ 更新 {RV["updated"]}', f'Covering {RV["period"]["from"]} to {RV["period"]["to"]} · updated {RV["updated"]}')}</span></div>
{leads}</div>

<div class="wms"><div class="wms-h"><h2>{t("週次メモ", "Weekly notes")}</h2>
<span class="rv-m">{t("週ごとのリリース・数値・考察・次週。新しい週が上", "Releases, figures, reading and next steps by week, newest first")}</span></div>
{memos}</div>

<div class="sec"><h2><span class="n">1</span>{t("プロジェクト実績サマリー", "Project summary")}</h2>
<div class="hls">{headline}</div>
<h3 class="sh">{t("表示の速さ（PSI スコア）", "How fast it appears (PSI score)")}</h3>
<div class="tw"><table><tr><th>{t("ページ種別","Page type")}</th><th>{t("結果","Result")}</th><th>{t("差","Change")}</th><th>{t("リリース前 → 直後 → 月末","Before → just after → month end")}</th><th>{t("日ごとのばらつき","Daily spread")}</th><th><span class="ja"><span{_RT}>判定（月末）</span></span><span class="en"><span{_RT}>Rating (month end)</span></span></th></tr>{erows}</table></div>
<p class="note">{t(f'[[PageSpeed Insights]]（PSI）のスコア。0〜100点で、<b>点が高いほど速い</b>。{WIN}（いずれも6ページとも測れた5日の平均）。', f'PageSpeed Insights (PSI) score, 0 to 100, <b>higher is faster</b>. Five-day means: {WIN_EN}, counting only days when all six pages were measured.')}</p>
<p class="note">{t(f'結果は「リリース前」と「月末」の差で決めている。差が日ごとのばらつき（同じページの日ごとの標準偏差）以内なら変化なし。速くなった {EC["fast"]}ページ／変化なし {EC["same"]}ページ／遅くなった {EC["slow"]}ページ。', f'The result compares before with month end. A change inside the daily spread (standard deviation of that page across days) counts as no change. Faster {EC["fast"]}, no change {EC["same"]}, slower {EC["slow"]}.')}</p>
<p class="note">{t('判定は PSI がスコアを分ける3段階。<b>90点以上が「高」、50〜89点が「普通」、49点以下が「低」</b>。月末時点で6ページとも「低」。', 'The rating is the three bands PSI uses: <b>90 and above high, 50-89 average, 49 and below low</b>. At month end all six are low.')}</p>

<h3 class="sh">{t("操作への反応（[[TBT]]）", "Response to a tap ([[TBT]])")}</h3>
<div class="tw"><table><tr><th>{t("ページ種別","Page type")}</th><th>{t("結果","Result")}</th><th>{t("差","Change")}</th><th>{t("リリース前 → 直後 → 月末","Before → just after → month end")}</th><th>{t("日ごとのばらつき","Daily spread")}</th></tr>{trows}</table></div>
<p class="note">{t(f'ページを開いている間に、操作を受け付けられなかった時間の合計。<b>ミリ秒（ms）が小さいほど速い</b>。期間は表示の速さと同じ。6ページ平均は {TB["overall"]["before"]:,}ms → {TB["overall"]["mid"]:,}ms → {TB["overall"]["after"]:,}ms。', f'Total time the page could not accept a tap. <b>Fewer milliseconds is faster</b>. Same periods as above. Six-page mean {TB["overall"]["before"]:,}ms → {TB["overall"]["mid"]:,}ms → {TB["overall"]["after"]:,}ms.')}</p>
<p class="note">{t(f'結果の決め方も同じ。速くなった {TC["fast"]}ページ／変化なし {TC["same"]}ページ／遅くなった {TC["slow"]}ページ。TBT は日ごとの振れが大きく、ばらつきの幅が差と同じくらいある。', f'Same rule for the result. Faster {TC["fast"]}, no change {TC["same"]}, slower {TC["slow"]}. TBT swings hard day to day; the spread is about as wide as the changes.')}</p>
</div>

<div class="sec"><h2><span class="n">2</span>{t("PSI スコア推移", "PSI score")}</h2>
<p class="note">{t(f'太線は7日の[[移動平均]]、薄い線がその日の PSI スコア。日ごとの振れがページによって ±3〜11点あるので、太線のほうを見る。', 'The bold line is a 7-day mean; the faint line is the PSI score for that day. Daily swings run 3-11 points depending on the page, so read the bold line.')}</p>
<div class="card"><div class="ch-h"><h3>{t("PSI スコアの推移", "PSI score over time")}</h3>
<span class="ch-t">{t(f'{defs["psi_from"]} 〜 {defs["psi_to"]}', f'{defs["psi_from"]} to {defs["psi_to"]}')}</span></div>
<div class="legend" id="psi-legend"></div>
<div class="plot" id="plot-psi"></div></div>
</div>

<div class="sec"><h2><span class="n">3</span>{t("操作レスポンス速度（[[TBT]]）", "Response speed ([[TBT]])")}</h2>
<p class="note">{t('押してから画面が応えるまでの時間。いまは [[ラボ値]] の [[TBT]] で代用している。実ユーザーの数値はこれから取る。', 'The wait between a tap and a response. It is currently stood in for by the lab figure TBT; real-user numbers are on the way.')}</p>
<p class="note">{t('縦軸はミリ秒で、<b>線が下にあるほど速い</b>。太線は7日の[[移動平均]]、薄い線がその日の値。点線は 9/17 のリリース。<br>見るところは<b>点線の前後で太線に段が付いているか</b>。PSI スコア側には段が付いたが、こちらは付いていない。', 'The vertical axis is milliseconds, so <b>lower is faster</b>. The bold line is a 7-day mean, the faint one the value for that day, and the dotted line is the 9/17 release.<br>What to look for is <b>a step in the bold line either side of the dotted one</b>. The PSI score has one; this does not.')}</p>
<div class="card"><div class="ch-h"><h3>{t("TBT の推移（代理指標）", "TBT over time (stand-in)")}</h3>
<span class="ch-t">{t("短いほどよい", "Lower is better")}</span></div>
<div class="legend" id="tbt-legend"></div>
<div class="plot" id="plot-tbt"></div></div>
<h3 class="sh">{t("本番で測った操作の応答", "Response measured in production")}</h3>
<div class="tw"><table><tr><th>{t("操作","Action")}</th><th>{t("施策","Change")}</th><th>{t("平均（前 → 後）","Mean (before → after)")}</th><th>{t("中央値","Median")}</th><th>{t("差","Change")}</th></tr>{rmrows}</table></div>
<p class="note">{t(f'{D["react_measured"][0]["src"]["ja"]}。実際に使っている人の値ではないので、実ユーザー計測が始まったら置き換える。', f'{D["react_measured"][0]["src"]["en"]}. These are not real-user figures and will be replaced once real-user measurement starts.')}</p>
{setup_panel("web-vitals")}
{setup_panel("server-timing")}
</div>

<div class="sec"><h2><span class="n">4</span>{t("リリース実績", "Released")}</h2>
<div class="card strip"><div class="ch-h"><h3>{t("リリースした日", "Release days")}</h3></div>
<div class="plot" id="plot-releases"></div></div>
{setup_panel("release-log")}
<div class="tw"><table><tr><th>{t("日付","Date")}</th><th>{t("チケット","Ticket")}</th><th>{t("内容","Change")}</th><th>{t("対象","Scope")}</th><th>{t("削減","Saved")}</th></tr>{srows}</table></div>
<details><summary>{t(f'調査・改修で完了したもの（{len(IV["closed"])}件）', f'Investigations and fixes already closed ({len(IV["closed"])})')}</summary><div class="tw"><table><tr><th>{t("チケット","Ticket")}</th><th>{t("内容","Change")}</th></tr>{crows}</table></div></details>
</div>

<div class="sec"><h2><span class="n">5</span>{t("未リリースの施策案", "Not yet released")}</h2>
<p class="note">{t(f'調査で見つけて起票したまま、本番に出ていないものが {N["backlog"]} 件ある。うち急ぎが {len(IV["urgent"])} 件。', f'{N["backlog"]} items were found, written up, and have not reached production. {len(IV["urgent"])} of them are marked urgent.')}</p>
<div class="tw"><table><tr><th>{t("チケット","Ticket")}</th><th>{t("内容","Item")}</th><th>{t("削減見込み","Expected saving")}</th></tr>{urows}</table></div>
<details><summary>{t("全49件の内訳", "All 49 items by state")}</summary><div class="tw"><table><tr><th>{t("状態","State")}</th><th>{t("件数","Count")}</th></tr>{grows}</table></div></details>
</div>

<div class="sec"><h2><span class="n">6</span>{t("実ユーザー計測値", "Real-user measurements")}</h2>
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
<p class="note">{t(f'このグラフと表の起点は {defs["baseline_period_end"]} の週（計測トラッカーに最初の数値を記録した {defs["baseline_note"]} を含む週）。第2節の PSI は別の計測で、{defs["psi_from"]} から毎日取っている。', f'These charts start at the week ending {defs["baseline_period_end"]}, which contains {defs["baseline_note"]}, when the first figures were recorded. The PSI series in section 2 is a separate measurement, taken daily from {defs["psi_from"]}.')}</p>
<div class="tw" id="trend-table"></div>
</div>

<div class="sec"><h2><span class="n">7</span>{t("課題と次の打ち手", "Issues and next moves")}</h2>
{irows}
</div>

<div class="sec"><h2><span class="n">8</span>{t("計測基盤と更新サイクル", "Measurement pipeline and cadence")}</h2>
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
</div>
<script>window.__PERF={PAYLOAD};</script>
<script>{JS}</script>'''

# 同じ語に何度もツールチップを出さない。文書に現れた順で最初の1つだけ残す。
# ただし見出し（h1〜h3）の中は、本文に先に出ていても残す。見出しで初めて目にする人がいるため
HINT_RE = re.compile(r'(<span class="hint" tabindex="0" data-tip-ja="[^"]*" data-tip-en="[^"]*">)([^<]+)(</span>)')
HEAD_RE = re.compile(r'<h[123][ >].*?</h[123]>', re.S)
_heads = [m.span() for m in HEAD_RE.finditer(html)]

def _in_head(i):
    return any(a <= i < b for a, b in _heads)

_seen, _out, _last = set(), [], 0
for m in HINT_RE.finditer(html):
    term = m.group(2)
    keep = _in_head(m.start()) or term not in _seen
    _seen.add(term)
    _out.append(html[_last:m.start()])
    _out.append(m.group(0) if keep else f'<span>{term}</span>')
    _last = m.end()
_out.append(html[_last:])
html = "".join(_out)

OUT.write_text(html, encoding="utf-8")
print(f"built {OUT} ({len(html):,} bytes)")
