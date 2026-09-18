#!/usr/bin/env python3
"""
CLAUDE.md の UI 規則を機械チェックする。

「AI が毎回同じテンプレートで作れるか」を人の目視に頼らないための仕組み。
規則が文章のままだと守られたか確認できないので、判定できる形に落としてある。

  python3 scripts/artifact/lint.py                # 全ページ
  python3 scripts/artifact/lint.py 2026h2         # パス指定
  python3 scripts/artifact/lint.py --warn-only    # 警告でも終了コード 0

チェック内容（出典は CLAUDE.md）:
  NG   左罫線だけ太くして色を付ける UI
       border-left 3px 以上 / border-left-color / ::before を縦棒にする書き方
  NG   絵文字（文字・HTML 数値参照の両方）
  NG   見出し行頭のアイコン四角（.no バッジ）
  NG   裸のチケット番号（#418 形式。ClickUp リンクにすること）
  WARN 13px 未満のフォントサイズ（planning 配下。モック内の UI 再現は対象外）
  WARN planning 配下の VELTRA 表記（Veltra に統一）
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", ".claude", ".vercel", "docs", "scripts", "node_modules", "dist", "releasenote"}

EMOJI_CHAR = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U0001F000-\U0001F2FF"
    "☀-➿"
    "⬀-⯿"
    "️"
    "←-⇿"  # 矢印は装飾記号として使われるため別枠で扱う
    "]"
)
# 矢印や幾何記号は CLAUDE.md が挙げる絵文字（📌🔗🔍等）ではないので除外する。
# U+FE0F は直前の文字と対で出るため単体では数えない
EMOJI_ALLOW = set("←→↑↓↔↗↘↖↙⇒⇔⇄▸▾▴◂▲▼▶◀◆◇■□●○★☆•·−–—×✓✔※")
EMOJI_ENTITY = re.compile(r"&#x(1F[0-9A-Fa-f]{3}|2[6-7][0-9A-Fa-f]{2}|FE0F);", re.I)

BORDER_LEFT = re.compile(r"border-left\s*:\s*([0-9.]+)px\s+\w+\s+(?!transparent)", re.I)
BORDER_LEFT_COLOR = re.compile(r"border-left-color\s*:", re.I)
BORDER_LEFT_WIDTH = re.compile(r"border-left-width\s*:\s*([0-9.]+)px", re.I)
# border-left を使わず ::before を縦棒にする書き方も同じ禁止事項に当たる
ACCENT_BAR = re.compile(
    r"::(?:before|after)\s*\{[^}]*?left\s*:\s*0[^}]*?width\s*:\s*([0-9.]+)px[^}]*?\}", re.I | re.S)
# class="no" 単体、もしくは空白区切りで no を含むものだけ。nk-no / lyr-no は別物
ICON_BADGE = re.compile(r'class="(?:[^"]*\s)?no(?:\s[^"]*)?"|(?<![\w-])\.no(?![\w-])\s*[{,]')
FONT_SIZE = re.compile(r"font-size\s*:\s*([0-9.]+)px", re.I)
BARE_TICKET = re.compile(r"(?<![\w&#])#(\d{3,4})(?!\d)")
VELTRA_UPPER = re.compile(r"\bVELTRA\b")

STRIP_BLOCKS = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
STRIP_STYLE_ATTR = re.compile(r'\sstyle="[^"]*"', re.I)
STRIP_TAGS = re.compile(r"<[^>]+>")
CLICKUP_LINK = re.compile(r"app\.clickup\.com/t/\d+/[A-Z_]+-\d+")


def iter_targets(arg):
    base = ROOT / arg if arg else ROOT
    if base.is_file():
        yield base
        return
    for p in sorted(base.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        yield p
    for p in sorted(base.rglob("*.js")):
        rel = p.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        yield p


def text_only(html: str) -> str:
    """CSS / JS / style 属性 / タグを落として、読み手が見る文字だけ残す"""
    s = STRIP_BLOCKS.sub(" ", html)
    s = STRIP_STYLE_ATTR.sub(" ", s)
    s = STRIP_TAGS.sub(" ", s)
    return s


def lint_file(path: Path):
    findings = []
    raw = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(ROOT).as_posix()
    lines = raw.splitlines()

    for m in ACCENT_BAR.finditer(raw):
        if float(m.group(1)) >= 3:
            line_no = raw[:m.start()].count("\n") + 1
            findings.append(("NG", rel, line_no, "border-left",
                             f"::before を幅 {m.group(1)}px の左アクセントバーにしている"))

    for i, line in enumerate(lines, 1):
        m = BORDER_LEFT.search(line)
        if m and float(m.group(1)) >= 3:
            findings.append(("NG", rel, i, "border-left", f"border-left {m.group(1)}px（均一の 1px ボーダー＋バッジにする）"))
        if BORDER_LEFT_COLOR.search(line):
            findings.append(("NG", rel, i, "border-left", "border-left-color でステータスを表現している"))
        m = BORDER_LEFT_WIDTH.search(line)
        if m and float(m.group(1)) >= 3:
            findings.append(("NG", rel, i, "border-left", f"border-left-width {m.group(1)}px"))

        for m in EMOJI_ENTITY.finditer(line):
            findings.append(("NG", rel, i, "emoji", f"絵文字の数値参照 &#x{m.group(1)};"))

        if ICON_BADGE.search(line):
            findings.append(("NG", rel, i, "icon-badge", "見出し行頭のアイコン四角（.no）"))

        # 13px 下限は施策ドキュメントの規則。モックアップ内の UI 再現は対象外
        if "planning/" in rel and "-mock" not in rel and "staging" not in rel:
            m = FONT_SIZE.search(line)
            if m and float(m.group(1)) < 13:
                findings.append(("WARN", rel, i, "font-size", f"font-size {m.group(1)}px（13px 以上）"))

    # 絵文字（文字そのもの）とチケット番号は、読み手が見る文字だけを対象にする
    body = text_only(raw) if path.suffix == ".html" else raw
    for i, line in enumerate(body.splitlines(), 1):
        for m in EMOJI_CHAR.finditer(line):
            if m.group(0) in EMOJI_ALLOW or m.group(0) == "\uFE0F":
                continue
            findings.append(("NG", rel, 0, "emoji", f"絵文字 {m.group(0)!r}"))

    stripped = CLICKUP_LINK.sub(" ", body)
    seen = set()
    for m in BARE_TICKET.finditer(stripped):
        if m.group(1) in seen:
            continue
        seen.add(m.group(1))
        findings.append(("NG", rel, 0, "bare-ticket", f"裸のチケット番号 #{m.group(1)}（UX_DESIGN-{m.group(1)} とし ClickUp へリンク）"))

    if "planning/" in rel and VELTRA_UPPER.search(body):
        findings.append(("WARN", rel, 0, "naming", "VELTRA 表記（施策ドキュメントは Veltra に統一）"))

    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default="")
    ap.add_argument("--warn-only", action="store_true")
    ap.add_argument("--by-rule", action="store_true", help="ルール別の件数だけ出す")
    args = ap.parse_args()

    all_findings = []
    files = 0
    for p in iter_targets(args.path):
        files += 1
        all_findings.extend(lint_file(p))

    by_rule = defaultdict(list)
    for f in all_findings:
        by_rule[(f[0], f[3])].append(f)

    print(f"=== lint: {files} files ===")
    ng = sum(1 for f in all_findings if f[0] == "NG")
    warn = sum(1 for f in all_findings if f[0] == "WARN")

    print("\n--- ルール別 ---")
    for (sev, rule) in sorted(by_rule, key=lambda k: (k[0], -len(by_rule[k]))):
        items = by_rule[(sev, rule)]
        pages = len({i[1] for i in items})
        print(f"  {sev:4} {rule:13} {len(items):4} 件 / {pages} files")

    if not args.by_rule:
        print("\n--- 詳細（ファイル別 上位）---")
        by_file = defaultdict(list)
        for f in all_findings:
            by_file[f[1]].append(f)
        for rel in sorted(by_file, key=lambda r: -len(by_file[r]))[:15]:
            items = by_file[rel]
            print(f"\n  {rel}  ({len(items)} 件)")
            for sev, _, line, rule, msg in items[:6]:
                loc = f":{line}" if line else ""
                print(f"    {sev:4} {rule:13}{loc:>6}  {msg}")
            if len(items) > 6:
                print(f"    ... 他 {len(items) - 6} 件")

    print(f"\n=== NG {ng} 件 / WARN {warn} 件 ===")
    if args.warn_only:
        return 0
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())
