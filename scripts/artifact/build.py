#!/usr/bin/env python3
"""
repo -> dist/ : Artifact 公開用ビルド。

リポジトリが唯一の正。dist/ は毎回作り直す生成物なので手で編集しない。

  python3 scripts/artifact/build.py
  python3 scripts/artifact/build.py --check   # 書き出さず検証だけ

やっていること:
  1. /auth.js の読み込みを除去する。アクセス制御は Artifact の共有設定に移る
  2. ページごとに __SITE_PATH__ / __SITE_BASE__ を注入し site-shim.js を読ませる
  3. href/src のルート絶対パスを、そのページの深さに応じた相対パスへ書き換える
     ディレクトリ参照（/2026h1/）は index.html を明示する形に正規化する
  4. nav.js の href 文字列とページ判定を __SITE_BASE__ / __SITE_PATH__ 経由にする
  5. 週次の bottleneck-N-content.json を bottlenecks.json 1 本へ統合する
     Artifact のファイル数上限 255 に対する構造的な対策
  6. 生成後に全リンクの実体を突き合わせ、切れリンクを列挙する
  7. dist/_build/files.json に publish 対象の一覧を書き出す
"""

import argparse
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
SHIM_SRC = Path(__file__).resolve().parent / "site-shim.js"

# Artifact 側の上限。超えたら publish 前に落とす
MAX_FILES = 255
MAX_PAGE_BYTES = 16 * 1024 * 1024
MAX_VERSION_BYTES = 64 * 1024 * 1024

WEB_EXT = {".html", ".css", ".js", ".json", ".md", ".jpg", ".jpeg", ".png",
           ".svg", ".gif", ".webp", ".ico", ".woff", ".woff2"}
INCLUDE_TREES = ["2026h1", "2026h2"]
EXCLUDE_DIRS = {".git", ".claude", ".vercel", "docs", "scripts",
                "releasenote", "node_modules", "dist"}
# auth.js / login.html は Vercel 時代のクライアント側ゲート。Artifact では不要
# CLAUDE.md / README.md はリポジトリ内部の文書なので公開しない
EXCLUDE_FILES = {"auth.js", "login.html", "CLAUDE.md", "README.md"}

# 自分のサイトルートを別に持つサブツリー。
# staging の LP は src/ を自分のルートとして /common/img/... を書いている
SITE_ROOT_OVERRIDES = {
    "2026h1/planning/veltra-theme-lp-staging/src/": "2026h1/planning/veltra-theme-lp-staging/src/",
}

BOTTLENECK_CONTENT = re.compile(r"^bottleneck-(\d+)-content\.json$")
ATTR_ABS = re.compile(r'(\s(?:src|href|data-src|poster)=")(/[^"]*)(")')
CSS_URL_ABS = re.compile(r'(url\(\s*["\']?)(/[^"\')]+)(["\']?\s*\))')

stats = defaultdict(int)
problems = []
notes = []


def rel_base(dest_rel: str) -> str:
    """dist 内の dest_rel から見たサイトルートへの相対プレフィックス"""
    depth = dest_rel.count("/")
    return "../" * depth if depth else "./"


def abs_root_for(dest_rel: str) -> str:
    """そのページにとってルート絶対パス（/foo）が指す先。
    既定はサイトルート。SITE_ROOT_OVERRIDES に該当すればそのディレクトリ"""
    for prefix, root in SITE_ROOT_OVERRIDES.items():
        if dest_rel.startswith(prefix):
            return root
    return ""


def split_suffix(path: str):
    """パス本体と #fragment / ?query を分ける"""
    for sep in ("#", "?"):
        i = path.find(sep)
        if i != -1:
            return path[:i], path[i:]
    return path, ""


def normalize_abs(abs_path: str) -> str:
    """ルート絶対パスをサイトルート基準の実ファイルパスへ正規化。
    ディレクトリ参照には index.html を明示する（Artifact はディレクトリ索引を返さない）"""
    body, suffix = split_suffix(abs_path)
    body = body.lstrip("/")
    if body == "" or body.endswith("/"):
        body += "index.html"
    return body, suffix


def to_relative(abs_path: str, base: str, abs_root: str = "") -> str:
    body, suffix = normalize_abs(abs_path)
    return base + abs_root + body + suffix


def collect_sources():
    """publish 対象のソースファイルを (src_path, dest_rel) で返す"""
    out = []
    for p in sorted(ROOT.glob("*")):
        if p.is_file() and p.suffix.lower() in WEB_EXT and p.name not in EXCLUDE_FILES:
            out.append((p, p.name))
    for tree in INCLUDE_TREES:
        base = ROOT / tree
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            if any(part in EXCLUDE_DIRS for part in p.relative_to(ROOT).parts):
                continue
            if p.suffix.lower() not in WEB_EXT or p.name in EXCLUDE_FILES:
                continue
            out.append((p, p.relative_to(ROOT).as_posix()))
    return out


def merge_bottlenecks(sources):
    """同一ディレクトリの bottleneck-N-content.json を bottlenecks.json へ統合。
    統合後のソースリストと、書き出す統合データを返す"""
    by_dir = defaultdict(dict)
    for src, dest in sources:
        m = BOTTLENECK_CONTENT.match(Path(dest).name)
        if m:
            by_dir[str(Path(dest).parent)][m.group(1)] = src

    merged = {}
    for d, items in by_dir.items():
        if len(items) < 2:
            continue
        blob = {}
        for num, src in sorted(items.items(), key=lambda kv: int(kv[0])):
            blob[num] = json.loads(src.read_text(encoding="utf-8"))
        dest = (Path(d) / "bottlenecks.json").as_posix()
        merged[dest] = blob
        stats["bottleneck_merged_files"] += len(items)
        stats["bottleneck_merged_targets"] += 1

    consumed = {str(Path(dest).parent) for dest in
                (str(Path(d) / "x") for d in by_dir if len(by_dir[d]) >= 2)}
    kept = []
    for src, dest in sources:
        m = BOTTLENECK_CONTENT.match(Path(dest).name)
        if m and str(Path(dest).parent) in consumed:
            continue
        kept.append((src, dest))
    return kept, merged


def rewrite_html(text: str, dest_rel: str) -> str:
    base = rel_base(dest_rel)
    abs_root = abs_root_for(dest_rel)
    site_path = "/" + dest_rel

    before = text
    text = re.sub(r'[ \t]*<script src="/auth\.js"></script>\n?', "", text)
    if text != before:
        stats["auth_removed"] += 1

    inject = (
        f'<script>window.__SITE_PATH__="{site_path}";'
        f'window.__SITE_BASE__="{base}";</script>\n'
        f'<script src="{base}site-assets/site-shim.js"></script>\n'
    )
    m = re.search(r'<meta\s+charset=[^>]*>\s*\n?', text, re.I)
    if m:
        text = text[:m.end()] + inject + text[m.end():]
    else:
        m = re.search(r"<head[^>]*>\s*\n?", text, re.I)
        if m:
            text = text[:m.end()] + inject + text[m.end():]
        else:
            text = inject + text
            notes.append(f"{dest_rel}: <head> が見つからず先頭に shim を挿入")
    stats["shim_injected"] += 1

    def repl(m):
        stats["attr_rewritten"] += 1
        return m.group(1) + to_relative(m.group(2), base, abs_root) + m.group(3)

    text = ATTR_ABS.sub(lambda m: m.group(0) if m.group(2).startswith("//") else repl(m), text)
    return text


DOC_SHELL = [
    (re.compile(r"<!DOCTYPE[^>]*>\s*", re.I), ""),
    (re.compile(r"</?html[^>]*>\s*", re.I), ""),
    (re.compile(r"</?head[^>]*>\s*", re.I), ""),
    (re.compile(r"<body([^>]*)>", re.I), r'<div class="artifact-body"\1>'),
    (re.compile(r"</body>", re.I), "</div>"),
]


def strip_doc_shell(text: str) -> str:
    """Artifact のページ本体は publish 時に doctype/html/head/body で包まれる。
    二重構造を避けるため、ルートページだけ外殻を外す。
    サポートファイルとして配信される他ページは包まれないので完全な文書のままでよい。"""
    for pat, repl in DOC_SHELL:
        text = pat.sub(repl, text)
    return text


def rewrite_js(text: str, dest_rel: str) -> str:
    """nav.js など。JS はサイトルート直下に置かれ、複数の深さのページから読まれる。
    href は実行時に __SITE_BASE__ で組み立て、ページ判定は __SITE_PATH__ を見る"""
    def abs_to_expr(abs_path: str) -> str:
        body, suffix = normalize_abs(abs_path)
        stats["js_href_rewritten"] += 1
        return f"window.__SITE_BASE__ + '{body}{suffix}'"

    before = text
    text = text.replace(
        "var path = location.pathname;",
        "var path = (window.__SITE_PATH__ || location.pathname);",
    )
    if text != before:
        stats["js_path_patched"] += 1

    # href: '/x'  /  href = '/x'
    text = re.sub(r"(href\s*[:=]\s*)'(/[^']*)'",
                  lambda m: m.group(1) + abs_to_expr(m.group(2)), text)
    # mkA('label', '/x')
    text = re.sub(r"(mkA\(\s*[^,]*,\s*)'(/[^']*)'",
                  lambda m: m.group(1) + abs_to_expr(m.group(2)), text)
    return text


def rewrite_css(text: str, dest_rel: str) -> str:
    base = rel_base(dest_rel)

    def repl(m):
        if m.group(2).startswith("//"):
            return m.group(0)
        stats["css_url_rewritten"] += 1
        return m.group(1) + to_relative(m.group(2), base) + m.group(3)

    return CSS_URL_ABS.sub(repl, text)


def verify_links(published: set):
    """生成物のリンク先が実在するか突き合わせる。ここが毎回のズレの検出点"""
    broken = []
    for dest in sorted(published):
        if not dest.endswith(".html"):
            continue
        text = (DIST / dest).read_text(encoding="utf-8", errors="replace")
        page_dir = Path(dest).parent
        for m in re.finditer(r'\s(?:src|href)="([^"]+)"', text):
            target = m.group(1)
            if (re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I)
                    or target.startswith("//")
                    or target.startswith("#")
                    or target.startswith("data:")):
                continue
            # インラインスクリプトが実行時に組み立てる href は静的に追えない。
            # これらは site-shim.js が実行時に解決する
            if any(tok in target for tok in ("${", "' +", '" +', "+ '", '+ "')):
                stats["runtime_href_deferred"] += 1
                continue
            body, _ = split_suffix(target)
            if not body:
                continue
            if body.endswith("/"):
                body += "index.html"
            resolved = (page_dir / body) if not body.startswith("/") else Path(body.lstrip("/"))
            try:
                norm = Path(*resolved.parts).resolve().relative_to(Path().resolve())
            except Exception:
                norm = None
            key = str((page_dir / body)).replace("\\", "/")
            key = str(Path(key)).replace("\\", "/")
            # 正規化（.. を潰す）
            parts = []
            for part in key.split("/"):
                if part in ("", "."):
                    continue
                if part == "..":
                    if parts:
                        parts.pop()
                    continue
                parts.append(part)
            key = "/".join(parts)
            if key not in published:
                broken.append((dest, target, key))
    return broken


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="dist を残さず検証のみ")
    args = ap.parse_args()

    sources = collect_sources()
    sources, merged = merge_bottlenecks(sources)

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    published = set()

    for src, dest in sources:
        out = DIST / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        ext = src.suffix.lower()
        if ext == ".html":
            html = rewrite_html(src.read_text(encoding="utf-8"), dest)
            if dest == "index.html":
                html = strip_doc_shell(html)
                stats["page_shell_stripped"] += 1
            out.write_text(html, encoding="utf-8")
        elif ext == ".js":
            out.write_text(rewrite_js(src.read_text(encoding="utf-8"), dest), encoding="utf-8")
        elif ext == ".css":
            out.write_text(rewrite_css(src.read_text(encoding="utf-8"), dest), encoding="utf-8")
        else:
            shutil.copy2(src, out)
        published.add(dest)
        stats["files"] += 1

    for dest, blob in merged.items():
        out = DIST / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(blob, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        published.add(dest)
        stats["files"] += 1

    shim_dest = "site-assets/site-shim.js"
    (DIST / "site-assets").mkdir(parents=True, exist_ok=True)
    (DIST / shim_dest).write_text(SHIM_SRC.read_text(encoding="utf-8"), encoding="utf-8")
    published.add(shim_dest)
    stats["files"] += 1

    broken = verify_links(published)

    supporting = sorted(p for p in published if p != "index.html")
    (DIST / "_build").mkdir(parents=True, exist_ok=True)
    (DIST / "_build" / "files.json").write_text(
        json.dumps(supporting, ensure_ascii=False, indent=1), encoding="utf-8")

    total_bytes = sum((DIST / p).stat().st_size for p in published)
    page_bytes = (DIST / "index.html").stat().st_size if "index.html" in published else 0

    print("=== build ===")
    for k in sorted(stats):
        print(f"  {k}: {stats[k]}")
    print(f"  total_bytes: {total_bytes:,}")
    print(f"  page_bytes: {page_bytes:,}")

    print("\n=== Artifact 上限 ===")
    fail = False
    for label, value, limit in (
        ("files", len(published), MAX_FILES),
        ("page_bytes", page_bytes, MAX_PAGE_BYTES),
        ("version_bytes", total_bytes, MAX_VERSION_BYTES),
    ):
        mark = "OK " if value <= limit else "NG "
        if value > limit:
            fail = True
        print(f"  {mark}{label}: {value:,} / {limit:,}")

    if notes:
        print("\n=== 注記 ===")
        for n in notes:
            print(f"  {n}")

    if broken:
        print(f"\n=== 切れリンク {len(broken)} 件 ===")
        agg = defaultdict(list)
        for page, target, key in broken:
            agg[target].append(page)
        for target in sorted(agg):
            pages = agg[target]
            print(f"  {target}  <- {len(pages)} pages (例: {pages[0]})")

    meta_path = Path(__file__).resolve().parent / "artifact.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        print(f"\n=== publish 先 ===\n  {meta['url']}")
        print("  この url を指定して上書きする。指定しないと別の Artifact が増える")

    if args.check:
        shutil.rmtree(DIST)
        print("\n--check: dist を削除しました")

    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
