#!/usr/bin/env python3
"""
build-teardown.py
=================
競合予約フロー teardown レポート（spot/）を「設定ファイル駆動」で生成する。
機械的・決定論的な生成のみを担当し、分析（ペイン分類・所見）は Claude が別途 config に落とす。

デザインは spot/traveler-pain-framework.html を継承（CSS は scripts/teardown/style.css に vendoring 済み）。

使用方法:
    python3 scripts/build-teardown.py --config scripts/teardown/config.example.json
    python3 scripts/build-teardown.py --config <path> --dry-run   # 生成せず概要のみ表示

config スキーマ: scripts/teardown/README.md を参照。
対応ブロック: slide_hi / pains / comparison / gallery / matrix / steps / html
"""

import argparse
import html as _html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
STYLE_PATH = os.path.join(HERE, "teardown", "style.css")

RATE = {"g": ("g", ""), "o": ("o", ""), "m": ("m", ""), "b": ("b", "")}  # class map (see style.css .rc)


def esc(s):
    return _html.escape(s, quote=True)


def rc(cell):
    """comparison セル: {'r':'g|o|m|b','t':'表示文字'} → <span class="rc g">…</span>"""
    r = cell.get("r", "o")
    return '<span class="rc %s">%s</span>' % (r, cell.get("t", ""))


def callout(c):
    if not c:
        return ""
    kind = c.get("kind", "blue")
    h = c.get("h", "")
    p = c.get("p", "")
    return ('<div class="cout %s"><h4>%s</h4><p>%s</p></div>' % (kind, h, p))


# ---- block renderers -------------------------------------------------------

def b_slide_hi(b):
    subs = "".join("<p>%s</p>" % s for s in b.get("subs", []))
    return ('<h2 class="st">%s</h2>\n<div class="slide hi">'
            '<div class="slide-h">%s</div>'
            '<div class="slide-sub">%s</div>%s</div>'
            % (b.get("st", ""), b.get("h", ""), subs, callout(b.get("callout"))))


PAINS_HTML = (
    '<div class="pains">'
    '<div class="pain effort"><div class="pn">手間</div><div class="pe">Effort</div><div class="pq">入力・操作・ステップが多くないか</div></div>'
    '<div class="pain anxiety"><div class="pn">不安</div><div class="pe">Anxiety</div><div class="pq">「予約できてる？」「当日どこへ？」が残らないか</div></div>'
    '<div class="pain wait"><div class="pn">待ち</div><div class="pe">Waiting</div><div class="pq">回答・確定・返信を待たされないか</div></div>'
    '<div class="pain confusion"><div class="pn">分からない</div><div class="pe">Confusion</div><div class="pq">情報が見つからない・意味不明がないか</div></div>'
    '<div class="pain broken"><div class="pn">裏切り</div><div class="pe">Broken promise</div><div class="pq">期待と違った（在庫なし・即確定でない）がないか</div></div>'
    '</div>')


def b_pains(b):
    stt = b.get("stt", "各フェーズで「何が辛いのか」を5種類で点検する")
    return ('<h2 class="st">%s</h2>\n<div class="sec"><div class="stt">%s</div>%s%s</div>'
            % (b.get("st", "課題出しのレンズ：ペインの5分類"), stt, PAINS_HTML, callout(b.get("callout"))))


def b_comparison(b):
    sites = b["sites"]
    th = ['<th>%s</th>' % b.get("axis_label", "観点")]
    for s in sites:
        cls = ' class="veltra-col"' if s.get("veltra") else ''
        note = ('<br><small>%s</small>' % s["note"]) if s.get("note") else ''
        th.append('<th%s>%s%s</th>' % (cls, esc(s["name"]), note))
    rows = []
    for r in b["rows"]:
        tds = ['<th>%s</th>' % r["axis"]]
        for i, cell in enumerate(r["cells"]):
            cls = ' class="veltra-col"' if sites[i].get("veltra") else ''
            tds.append('<td%s>%s</td>' % (cls, rc(cell)))
        rows.append('<tr>%s</tr>' % "".join(tds))
    return ('<h2 class="st">%s</h2>\n<div class="slide"><div class="cmp-wrap">'
            '<table class="cmp"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>%s</div>'
            % (b.get("st", ""), "".join(th), "".join(rows), callout(b.get("callout"))))


def b_gallery(b):
    groups = []
    for g in b["groups"]:
        shots = []
        for sh in g.get("shots", []):
            src = "%s/%s" % (b.get("assets_base", "/spot/assets/teardown"), sh["img"])
            cap = esc(sh.get("cap", ""))
            shots.append('<figure class="shot" tabindex="0" data-src="%s" data-cap="%s">'
                         '<img src="%s" alt="%s" loading="lazy">'
                         '<figcaption class="cap">%s</figcaption></figure>'
                         % (src, cap, src, cap, cap))
        if not shots and g.get("note"):
            shots.append('<div class="gnote">%s</div>' % g["note"])
        tag = ('<span class="tagm">%s</span>' % esc(g["tag"])) if g.get("tag") else ''
        groups.append('<div class="gsite">%s %s</div><div class="gallery">%s</div>'
                      % (esc(g["site"]), tag, "".join(shots)))
    lead = ('<div class="lede">%s</div>' % b["lead"]) if b.get("lead") else ''
    note = ('<div class="note">%s</div>' % b["note"]) if b.get("note") else ''
    return ('<h2 class="st">%s</h2>\n<div class="sec">%s%s%s</div>'
            % (b.get("st", ""), lead, "".join(groups), note))


def b_matrix(b):
    cols = "".join("<th>%s</th>" % c for c in b["cols"])
    rows = []
    for r in b["rows"]:
        cells = []
        for c in r["cells"]:
            if c.get("t", "—") == "—" or c.get("t") is None:
                cells.append("<td>—</td>")
            else:
                fc = " focus" if c.get("focus") else ""
                cells.append('<td class="%s"><span class="cell-note">%s</span></td>'
                             % (("mxcell" + fc).strip(), c["t"]))
        rows.append('<tr><th>%s</th>%s</tr>' % (r["phase"], "".join(cells)))
    note = ('<div class="note">%s</div>' % b["note"]) if b.get("note") else ''
    return ('<h2 class="st">%s</h2>\n<div class="slide"><div class="mx-wrap">'
            '<table class="mx"><thead><tr><th>フェーズ＼ペイン</th>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>%s</div>'
            % (b.get("st", ""), cols, "".join(rows), note))


def b_steps(b):
    items = []
    for i, s in enumerate(b["steps"], 1):
        dur = ('<div class="sdur">%s</div>' % s["dur"]) if s.get("dur") else ''
        items.append('<div class="step"><div class="sn">%d</div>'
                     '<div class="stitle">%s</div>%s<div class="sbody">%s</div></div>'
                     % (i, s.get("title", ""), dur, s.get("body", "")))
    return ('<h2 class="st">%s</h2>\n<div class="slide"><div class="steps">%s</div>%s</div>'
            % (b.get("st", ""), "".join(items), callout(b.get("callout"))))


def b_html(b):
    st = ('<h2 class="st">%s</h2>\n' % b["st"]) if b.get("st") else ''
    wrap = b.get("wrap", "sec")  # sec | slide | none
    body = b["html"]
    if wrap == "none":
        return st + body
    return '%s<div class="%s">%s</div>' % (st, wrap, body)


RENDER = {
    "slide_hi": b_slide_hi, "pains": b_pains, "comparison": b_comparison,
    "gallery": b_gallery, "matrix": b_matrix, "steps": b_steps, "html": b_html,
}

LB_JS = """
<script>
(function(){
  var lb=document.getElementById('lb');if(!lb)return;
  var img=lb.querySelector('img'),cap=lb.querySelector('.cap2');
  function open(s,c){img.src=s;img.alt=c||'';cap.textContent=c||'';lb.classList.add('on');}
  function close(){lb.classList.remove('on');img.src='';}
  document.querySelectorAll('.shot').forEach(function(f){
    f.addEventListener('click',function(){open(f.getAttribute('data-src'),f.getAttribute('data-cap'));});
    f.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();open(f.getAttribute('data-src'),f.getAttribute('data-cap'));}});
  });
  lb.addEventListener('click',close);
  document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
})();
</script>
"""


def build(cfg):
    style = open(STYLE_PATH, encoding="utf-8").read()
    hero = cfg["hero"]
    parts = [RENDER[b["type"]](b) for b in cfg["sections"]]
    footer = '<div class="footer">%s</div>' % cfg.get("footer", "")
    lightbox = ('<div id="lb" role="dialog" aria-modal="true" aria-label="拡大表示">'
                '<span class="cl" aria-label="閉じる">&times;</span><img alt=""><div class="cap2"></div></div>')
    return (
        "<!DOCTYPE html>\n<html lang=\"ja\">\n<head>\n<meta charset=\"UTF-8\">\n"
        "<script src=\"/auth.js\"></script>\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        "<title>%s</title>\n"
        "<link href=\"https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;600;700;800&display=swap\" rel=\"stylesheet\">\n"
        "<style>\n%s</style>\n</head>\n<body>\n<div class=\"page\">\n"
        "<div class=\"hero\"><div class=\"hero-badge\">%s</div><h1>%s</h1><p>%s</p></div>\n"
        "%s\n%s\n</div>\n%s%s<script src=\"/nav.js\"></script>\n</body>\n</html>\n"
        % (esc(cfg.get("title", "競合予約フロー teardown")), style,
           hero.get("badge", ""), hero.get("h1", ""), hero.get("lead", ""),
           "\n".join(parts), footer, lightbox, LB_JS)
    )


def main():
    ap = argparse.ArgumentParser(description="競合 teardown レポートを config から生成")
    ap.add_argument("--config", required=True, help="レポート定義 JSON のパス")
    ap.add_argument("--out", help="出力先（省略時は config.outfile をリポジトリ相対で使用）")
    ap.add_argument("--dry-run", action="store_true", help="書き込まず概要のみ表示")
    a = ap.parse_args()

    cfg = json.load(open(a.config, encoding="utf-8"))
    out = a.out or os.path.join(REPO, cfg["outfile"])
    n_shots = sum(len(g.get("shots", [])) for b in cfg["sections"]
                  if b["type"] == "gallery" for g in b["groups"])
    print("config: %s" % a.config)
    print("sections: %s" % ", ".join(b["type"] for b in cfg["sections"]))
    print("gallery shots: %d" % n_shots)
    print("out: %s" % out)
    if a.dry_run:
        print("[dry-run] 書き込みなし")
        return
    html_out = build(cfg)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html_out)
    print("wrote %d bytes" % len(html_out))


if __name__ == "__main__":
    main()
