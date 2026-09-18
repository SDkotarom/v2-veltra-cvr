#!/usr/bin/env python3
"""
レポート提出前チェック。機械で見られるものを 1 コマンドに束ねる。

  python3 .claude/skills/report/scripts/check.py 2026h1/reports/2026-h1/2026-w26/index.html
  python3 .claude/skills/report/scripts/check.py --week 2026-w26
  python3 .claude/skills/report/scripts/check.py 2026h1/spot/my-report.html

見るもの:
  1. 未置換のプレースホルダ {{...}} が残っていないか
     → 埋め忘れが「そのまま公開」にならないための最後の砦
  2. インライン <style> を持っていないか
     → 持つとページごとに語彙が分裂する。足りないなら summary.css に 1 度足す
  3. 使っているクラスが共有 CSS に実在するか
     → 存在しないクラス名は無言で効かない。見た目が崩れて初めて気づく
  4. 結論が最初のセクションに来ているか
     → 後ろに置くと読まれない場所に結論が埋まる
  5. 出典（GA4 Property ID と集計期間）が書かれているか
  6. CLAUDE.md の UI 規則（scripts/artifact/lint.py に委譲）
  7. 週次なら data.json との数値整合（scripts/validate-report.py に委譲）

人が見るものは機械では代われない。何を人が見るかは SKILL.md に書いてある。
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SHARED_CSS = ["report.css", "summary.css"]

COMMENT = re.compile(r"<!--.*?-->", re.S)
PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")
STYLE_EL = re.compile(r"<style\b", re.I)
CLASS_ATTR = re.compile(r'class="([^"]+)"')
GA4_SOURCE = re.compile(r"347074845")
PERIOD = re.compile(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}")
SEC_TAG = re.compile(r'class="sec-tag"')

results = []


def add(sev, msg):
    results.append((sev, msg))


def week_reldir(week_id):
    m = re.match(r"^(\d{4})-w(\d+)$", week_id)
    if not m:
        return week_id
    half = "h1" if int(m.group(2)) <= 26 else "h2"
    return f"{m.group(1)}-{half}/{week_id}"


def shared_classes():
    defined = set()
    for name in SHARED_CSS:
        p = ROOT / name
        if p.exists():
            defined |= set(re.findall(r"\.([a-zA-Z][\w-]*)", p.read_text(encoding="utf-8")))
    return defined


def check_page(path: Path):
    raw = path.read_text(encoding="utf-8")
    body = COMMENT.sub(" ", raw)
    rel = path.relative_to(ROOT).as_posix()

    left = sorted(set(PLACEHOLDER.findall(body)))
    if left:
        shown = ", ".join(left[:8]) + (f" 他 {len(left) - 8} 個" if len(left) > 8 else "")
        add("NG", f"未置換のプレースホルダが残っている: {shown}")

    if STYLE_EL.search(body):
        n = len(STYLE_EL.findall(body))
        add("NG", f"インライン <style> が {n} 個ある。足りないコンポーネントは summary.css に追加する")

    linked = {c for c in SHARED_CSS if re.search(rf'href="[^"]*{re.escape(c)}"', body)}
    if "report.css" not in linked:
        add("NG", "report.css を読み込んでいない。配色トークンの正は report.css の :root")

    defined = shared_classes()
    used = {c for m in CLASS_ATTR.finditer(body) for c in m.group(1).split() if "{" not in c}
    missing = sorted(used - defined)
    if missing:
        add("NG", f"共有 CSS に存在しないクラス: {', '.join(missing[:10])}"
                  + (f" 他 {len(missing) - 10} 個" if len(missing) > 10 else ""))

    first = SEC_TAG.search(body)
    if first:
        head = body[first.start():first.start() + 260]
        if not re.search(r"Conclusion|結論|Summary|サマリー|全体像", head):
            add("WARN", "最初のセクションが結論になっていない。冒頭で全体像を出す")
    else:
        add("WARN", "sec-tag のセクション見出しが無い。情報の階層が読み取れない")

    if not GA4_SOURCE.search(body):
        add("WARN", "GA4 Property ID (347074845) の出典表記が無い")
    if not PERIOD.search(body):
        add("WARN", "集計期間の表記が見つからない")

    return rel


def run(label, cmd):
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    except FileNotFoundError:
        add("WARN", f"{label}: スクリプトが見つからず実行できなかった")
        return
    tail = [l for l in r.stdout.splitlines() if l.strip()][-6:]
    if r.returncode == 0:
        add("OK", f"{label}: 通過")
    else:
        add("NG", f"{label}: 未通過")
    for l in tail:
        print(f"    | {l}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page", nargs="?", help="対象 HTML のリポジトリ相対パス")
    ap.add_argument("--week", help="週 ID（例 2026-w26）。指定すると週次サマリーを対象にする")
    args = ap.parse_args()

    if args.week:
        target = ROOT / "2026h1/reports" / week_reldir(args.week) / "index.html"
    elif args.page:
        target = ROOT / args.page
    else:
        ap.error("対象ページか --week を指定してください")

    if not target.exists():
        print(f"NG  対象が見つかりません: {target}")
        return 1

    rel = check_page(target)
    print(f"=== check: {rel} ===\n")

    print("--- 委譲したチェック ---")
    run("UI 規則 (lint.py)",
        [sys.executable, "scripts/artifact/lint.py", str(target.relative_to(ROOT))])
    if args.week:
        run("数値整合 (validate-report.py)",
            [sys.executable, "scripts/validate-report.py", "--week", args.week])

    print("\n--- このページ自体 ---")
    ng = warn = 0
    for sev, msg in results:
        if sev == "NG":
            ng += 1
        elif sev == "WARN":
            warn += 1
        print(f"  {sev:4} {msg}")

    print(f"\n=== NG {ng} 件 / WARN {warn} 件 ===")
    if ng == 0 and warn == 0:
        print("機械で見られる範囲は通過。人が見る項目は SKILL.md の提出前チェックを参照")
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())
