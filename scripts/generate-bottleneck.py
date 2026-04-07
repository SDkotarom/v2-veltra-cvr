#!/usr/bin/env python3
"""
generate-bottleneck.py
======================
content JSON からボトルネック分析 HTML を生成するテンプレートエンジン。

使用方法:
    python3 scripts/generate-bottleneck.py --week 2026-w14 --all
    python3 scripts/generate-bottleneck.py --week 2026-w14 --num 4
    python3 scripts/generate-bottleneck.py --week 2026-w14 --all --dry-run
"""

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")
TOTAL_PAGES = 10

# Action letter colors: h1=red, h2=amber, h3=text3
HYPO_COLORS = {"h1": "var(--red)", "h2": "var(--amber)", "h3": "var(--text3)"}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_tags(tags):
    parts = []
    for t in tags:
        cls = "bn-tag red" if t.get("type") == "red" else "bn-tag"
        parts.append(f'<span class="{cls}">{t["label"]}</span>')
    return "\n          ".join(parts)


def render_funnel_overview(funnel_overview):
    """Render the funnel overview 4-cell grid (full funnel comparison)."""
    if not funnel_overview:
        return ""
    cells = []
    for cell in funnel_overview:
        alert = cell.get("alert", False)
        cls = 'fc-cell alert' if alert else 'fc-cell'
        label_style = ' style="color:var(--red)"' if alert else ''
        val_style = ' style="font-size:28px;margin-top:8px;color:var(--red)"' if alert else ' style="font-size:24px;margin-top:8px"'
        val_label_style = ' style="color:var(--red)"' if alert else ''
        cells.append(f'''    <div class="{cls}">
      <div class="fc-label"{label_style}>{cell["label"]}</div>
      <div class="fc-val"{val_style}>{cell["value"]}</div>
      <div class="fc-val-label"{val_label_style}>{cell.get("sub", "")}</div>
    </div>''')
    return "\n".join(cells)


def render_funnel_compare(fc):
    cells = []
    for cell in fc:
        alert = cell.get("alert", False)
        cls = 'fc-cell alert' if alert else 'fc-cell'
        label_style = ' style="color:var(--red)"' if alert else ''
        val_style = ' style="font-size:28px;margin-top:8px;color:var(--red)"' if alert else ' style="font-size:28px;margin-top:8px"'
        val_label_style = ' style="color:var(--red)"' if alert else ''
        cells.append(f'''    <div class="{cls}">
      <div class="fc-label"{label_style}>{cell["label"]}</div>
      <div class="fc-stage">{cell["stage"]}</div>
      <div class="fc-val"{val_style}>{cell["value"]}</div>
      <div class="fc-val-label"{val_label_style}>{cell.get("sub", "")}</div>
    </div>''')
    return "\n".join(cells)


def render_drill_down(dd):
    if not dd:
        return ""
    cards = []
    for item in dd:
        note = f'<div style="font-size:13px;color:var(--text3);margin-top:8px">&rarr; {item.get("note", "")}</div>' if item.get("note") else ""
        cards.append(f'''      <div style="border:1px solid var(--border);border-radius:8px;padding:16px 20px">
        <div style="font-size:14px;font-weight:700;margin-bottom:8px">{item["title"]}</div>
        <div style="font-size:15px;color:var(--text2);line-height:1.7">
          {item["body_html"]}
        </div>
        {note}
      </div>''')
    cols = "1fr " * len(cards)
    return f'''  <div style="padding:0 44px 20px">
    <div style="font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px">Step 4-5 &mdash; Tier 2-3 深掘り</div>
    <div style="display:grid;grid-template-columns:{cols.strip()};gap:16px">
{chr(10).join(cards)}
    </div>
  </div>'''


def render_action(action, hypo_level, letter_idx):
    """Render a single action card with prototype."""
    letter = action["letter"]
    letter_lower = letter.lower()
    color = HYPO_COLORS.get(hypo_level, "var(--text3)")
    # First action per hypothesis gets h1 color, second gets amber, third gets text3
    action_colors = ["var(--red)", "var(--amber)", "var(--text3)"]
    action_color = action_colors[letter_idx % 3]

    proto_html = ""
    if action.get("prototype"):
        proto = action["prototype"]
        proto_html = f'''
        <!-- Prototype (hidden by default) -->
        <div id="proto-{letter_lower}" style="display:none;padding:16px;background:var(--bg);border-top:1px solid var(--border)">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">
        <!-- Before -->
        <div>
          <div style="font-size:11px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;text-align:center">Before（現状）</div>
          {proto["before_html"]}
        </div>
        <!-- After -->
        <div>
          <div style="font-size:11px;font-weight:700;color:var(--green);text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;text-align:center">After（施策{letter}適用）</div>
          {proto["after_html"]}
        </div>
      </div>
        </div>'''

    proto_toggle = ""
    if action.get("prototype"):
        proto_toggle = f'''
          <div style="text-align:center;margin-top:12px">
            <span id="proto-toggle-{letter_lower}" style="font-size:12px;color:var(--text2);cursor:pointer;font-weight:600" onclick="event.stopPropagation();toggleProto('proto-{letter_lower}')">&#x1F4D0; プロトタイプを見る &#x25B8;</span>
          </div>'''

    spec_html = ""
    if action.get("spec_html"):
        spec_html = f'''
          <div style="margin-top:8px;padding:10px 12px;background:var(--bg);border-radius:6px;font-size:12px;line-height:1.6">
            <strong>開発仕様</strong>
          {action["spec_html"]}
          </div>'''

    return f'''      <!-- Action {letter} -->
      <div style="margin-top:16px;border:1px solid var(--border);border-radius:8px;overflow:hidden;background:#fff">
        <div style="padding:14px 16px;cursor:pointer;display:flex;justify-content:space-between;align-items:center" onclick="toggleProto('proto-{letter_lower}')">
          <div>
            <span style="font-size:13px;font-weight:700;color:{action_color}">施策 {letter}</span>
            <span style="font-size:14px;font-weight:700;margin-left:8px">{action["title"]}</span>
          </div>
          <span style="font-size:13px;font-weight:700;color:var(--green);padding:3px 10px;background:var(--green-light);border-radius:20px;flex-shrink:0;margin-left:12px">{action.get("impact", "")}</span>
        </div>
        <div style="padding:0 16px 14px">
          <div style="font-size:13px;color:var(--text2);line-height:1.6">{action.get("description", "")}</div>{spec_html}{proto_toggle}
        </div>{proto_html}
      </div>'''


def render_hypothesis(hypo, idx):
    """Render a hypothesis accordion with its actions."""
    level = hypo["level"]
    level_label = hypo["level_label"]
    num = idx + 1

    evidence_items = ""
    if hypo.get("evidence"):
        items = "\n    ".join(f"<li>{e}</li>" for e in hypo["evidence"])
        evidence_items = f'''
  <ul style="margin:6px 0 0;padding-left:18px;list-style:disc">
    {items}
  </ul>'''

    actions_html = []
    for li, action in enumerate(hypo.get("actions", [])):
        actions_html.append(render_action(action, level, li))

    return f'''  <!-- HYPOTHESIS {num} ACCORDION -->
  <div class="hypo-accordion" style="margin-bottom:16px">
    <div class="hypo-card {level}" style="cursor:pointer" onclick="toggleHypoActions('hypo-actions-{num}')">
      <div class="hypo-num">{level_label}</div>
      <div class="hypo-title">{hypo["title"]}</div>
      <div class="hypo-body">{hypo.get("body", "")}</div>
      <div class="hypo-evidence">
        <strong>裏付けデータ:</strong>{evidence_items}
</div>
      <div style="padding-top:12px;text-align:center">
        <span class="hypo-toggle" id="hypo-toggle-{num}" style="font-size:13px;color:var(--red);font-weight:700;cursor:pointer">&#x1F53B; 打ち手を見る</span>
      </div>
    </div>

    <div id="hypo-actions-{num}" style="display:none;padding:0 20px 16px;background:#fafaf8;border:1px solid var(--border);border-top:none;border-radius:0 0 12px 12px;margin-top:-12px">
{chr(10).join(actions_html)}
    </div>
  </div>'''


def render_competitive(comp):
    if not comp:
        return ""
    cards = []
    for c in comp:
        favicon = ""
        if c.get("favicon_url"):
            favicon = f'<img src="{c["favicon_url"]}" width="20" height="20" style="border-radius:4px" onerror="this.style.display=\'none\'">'
        ref_link = ""
        if c.get("url"):
            ref_link = f' <a href="{c["url"]}" target="_blank" style="font-size:12px;color:var(--text3);text-decoration:none;border-bottom:1px dashed var(--border-dash)">参照 &rarr;</a>'
        cards.append(f'''      <div style="border:1px solid var(--border);border-radius:10px;padding:18px 20px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
          <div style="font-size:16px;font-weight:700;display:flex;align-items:center;gap:8px">{favicon}{c["name"]}</div>
         {ref_link}
        </div>
        <div style="font-size:14px;color:var(--text2);line-height:1.7;margin-bottom:10px">
          {c.get("feature", "")}
        </div>
        <div style="font-size:12px;color:var(--text3)">{c.get("detail", "")}</div>
      </div>''')

    return f'''  <div style="padding:24px 44px 16px">
    <div style="font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">競合比較 <span style="background:var(--red-light);color:var(--red);padding:2px 8px;border-radius:4px;font-size:11px;margin-left:6px">予約開始フロー視点</span></div>
  </div>

  <div style="padding:0 44px 32px">
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px">
{chr(10).join(cards)}
    </div>
  </div>'''


def render_verification(verif):
    if not verif:
        return ""
    items = []
    for v in verif:
        items.append(f'        <label style="display:flex;align-items:center;gap:8px;cursor:pointer"><input type="checkbox"> {v}</label>')
    return f'''  <div style="padding:24px 44px 16px">
    <div style="font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">チームレビュー</div>
  </div>
  <div style="padding:0 44px 28px">
    <div style="border:1px solid var(--border);border-radius:8px;padding:20px 24px">
      <div style="font-size:14px;font-weight:700;margin-bottom:12px">レビューチェックリスト</div>
      <div style="font-size:14px;color:var(--text2);line-height:2">
{chr(10).join(items)}
      </div>
      <div style="margin-top:16px;padding:12px 16px;background:var(--bg);border-radius:6px">
        <div style="font-size:12px;font-weight:700;margin-bottom:4px">コメント欄</div>
        <textarea style="width:100%;border:1px solid var(--border);border-radius:4px;padding:8px;font-size:13px;font-family:inherit;min-height:60px;resize:vertical" placeholder="レビューコメントをここに記入..."></textarea>
      </div>
    </div>
  </div>'''


def render_nav(number, total):
    left = f'<a href="./">&larr; サマリーに戻る</a>'
    center = f'<a href="./">サマリーに戻る</a>'
    if number > 1:
        right_or_left = f'<a href="bottleneck-{number - 1}.html">&larr; #{number - 1}</a>'
    else:
        right_or_left = f'<a href="./">&larr; サマリーに戻る</a>'
    if number < total:
        right = f'<a href="bottleneck-{number + 1}.html">#{number + 1} へ進む &rarr;</a>'
    else:
        right = f'<a href="./">サマリーに戻る</a>'
    return f'''  <div class="nav-bar">
    {right_or_left}
    {center}
    {right}
  </div>'''


def generate_html(content, meta):
    """Generate full HTML from content JSON and week meta."""
    number = content["number"]
    title = content["title"]
    tags_html = render_tags(content.get("tags", []))
    deviation = content.get("deviation", "")
    impact = content.get("impact_sessions", "")

    # Description text
    desc_html = content.get("description_html", "")

    # Funnel overview (full funnel comparison)
    funnel_overview_html = ""
    if content.get("funnel_overview"):
        fo = content["funnel_overview"]
        fo_title = fo.get("title", "ファネル全体比較")
        fo_cells = render_funnel_overview(fo.get("cells", []))
        funnel_overview_html = f'''
  <hr class="divider">

  <!-- ファネル概要 -->
  <div style="padding:24px 44px 12px">
    <div style="font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px">{fo_title}</div>
  </div>
  <div class="funnel-compare">
{fo_cells}
  </div>'''

    # Tier 1 comparison
    fc_html = render_funnel_compare(content.get("funnel_compare", []))

    # Drill down
    dd_html = render_drill_down(content.get("drill_down", []))

    # Callout
    callout_html = ""
    if content.get("callout"):
        co = content["callout"]
        callout_html = f'''  <div class="callout" style="margin-top:0">
    <div class="ct">{co.get("title", "特定結果")}</div>
    <div class="cb">{co["body_html"]}</div>
  </div>'''

    # Hypotheses
    hypo_html_parts = []
    for i, hypo in enumerate(content.get("hypotheses", [])):
        hypo_html_parts.append(render_hypothesis(hypo, i))
    total_actions = sum(len(h.get("actions", [])) for h in content.get("hypotheses", []))
    hypo_section_title = content.get("hypo_section_title", f"原因仮説 &times; {len(content.get('hypotheses', []))} &amp; 打ち手 &times; {total_actions}")
    hypo_section_desc = content.get("hypo_section_desc", f"なぜこのボトルネックが発生しているか？ 仮説をクリックして打ち手・プロトタイプを展開。")

    # Verification callout
    verif_callout_html = ""
    if content.get("verification_method"):
        verif_callout_html = f'''  <div class="callout-amber callout">
    <div class="ct">検証方法</div>
    <div class="cb">{content["verification_method"]}</div>
  </div>'''

    # Competitive
    competitive_html = render_competitive(content.get("competitive", []))

    # Competitive insight callout
    comp_insight_html = ""
    if content.get("competitive_insight"):
        comp_insight_html = f'''
    <div class="callout" style="margin:20px 0 0">
      <div class="ct">競合比較から得られる示唆</div>
      <div class="cb">{content["competitive_insight"]}</div>
    </div>'''

    # Verification checklist
    verification_html = render_verification(content.get("verification", []))

    # Nav
    nav_html = render_nav(number, TOTAL_PAGES)

    # Footer date
    generated_date = meta.get("generated_at", "")[:10] if meta.get("generated_at") else ""

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<script src="/auth.js"></script>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="/bottleneck.css">
</head>
<body>

<div class="card">
  <div class="header-band">
    <div class="logo">V2</div>
    <a href="./" style="color:rgba(255,255,255,.85);font-size:14px;text-decoration:none;font-weight:500">&larr; サマリーに戻る</a>
    <div class="right">ボトルネック #{number} / {TOTAL_PAGES}</div>
  </div>

  <div style="padding:32px 44px">
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:12px">
      <div style="font-family:'DM Sans';font-size:56px;font-weight:900;color:var(--red);line-height:1">#{number}</div>
      <div>
        <div style="font-size:22px;font-weight:900;margin-bottom:8px">{title}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          {tags_html}
        </div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:16px;margin-top:16px">
      <div style="font-size:12px;color:var(--text3);font-weight:700;text-transform:uppercase">全体平均との乖離</div>
      <div style="font-family:'DM Sans';font-size:36px;font-weight:900;color:var(--red)">{deviation}</div>
      <div style="font-size:14px;color:var(--text3)">影響セッション: {impact}</div>
    </div>
    <div style="margin-top:12px;font-size:14px;color:var(--text2);line-height:1.6">
      {desc_html}
    </div>
  </div>
{funnel_overview_html}
  <hr class="divider">

  <!-- Tier 1 comparison -->
  <div style="padding:24px 44px 12px">
    <div style="font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px">Tier 1 比較</div>
  </div>
  <div class="funnel-compare">
{fc_html}
  </div>

{dd_html}

  {callout_html}

  <hr class="divider">

  <!-- Hypotheses + Actions + Prototypes -->
  <div style="padding:24px 44px 16px">
    <div style="font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">Step 6 &mdash; {hypo_section_title}</div>
    <div style="font-size:15px;color:var(--text2)">{hypo_section_desc}</div>
  </div>

  <div style="padding:0 44px 28px">
{chr(10).join(hypo_html_parts)}
  </div>
  <hr class="divider">

  {verif_callout_html}

{competitive_html}
{comp_insight_html}

{verification_html}

{nav_html}

</div>

<div class="card">
  <div class="footer">
    <span>VELTRA CVR改善チーム</span>
    <span><a href="https://analytics.google.com/analytics/web/#/p347074845/reports/reportinghub" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline">GA4: 347074845</a></span>
    <span>{generated_date}</span>
  </div>
</div>

<script src="/bottleneck.js"></script>
<script src="/nav.js"></script>
<script src="/funnel-def.js"></script>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description="Generate bottleneck HTML from content JSON")
    parser.add_argument("--week", required=True, help="Week ID (e.g. 2026-w14)")
    parser.add_argument("--num", type=int, help="Page number to generate (1-10)")
    parser.add_argument("--all", action="store_true", help="Generate all 10 pages")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    week_dir = os.path.join(REPORTS_DIR, args.week)
    if not os.path.isdir(week_dir):
        print(f"エラー: {week_dir} が存在しません", file=sys.stderr)
        sys.exit(1)

    # Load meta from data.json
    data_path = os.path.join(week_dir, "data.json")
    meta = {}
    if os.path.exists(data_path):
        data = load_json(data_path)
        meta = data.get("meta", {})

    if args.all:
        nums = list(range(1, TOTAL_PAGES + 1))
    elif args.num:
        nums = [args.num]
    else:
        print("エラー: --all または --num を指定してください", file=sys.stderr)
        sys.exit(1)

    for n in nums:
        content_path = os.path.join(week_dir, f"bottleneck-{n}-content.json")
        if not os.path.exists(content_path):
            print(f"スキップ: {content_path} が存在しません")
            continue

        content = load_json(content_path)
        html = generate_html(content, meta)
        out_path = os.path.join(week_dir, f"bottleneck-{n}.html")

        if args.dry_run:
            print(f"[dry-run] {out_path} ({len(html)} bytes)")
        else:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"生成: {out_path} ({len(html)} bytes)")

    print("完了")


if __name__ == "__main__":
    main()
