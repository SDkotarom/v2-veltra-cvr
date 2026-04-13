#!/usr/bin/env python3
"""
audit-actions.py
================
打ち手（actions）の施策化レビュー監査スクリプト。

1. known-implementations.json とのキーワードマッチで重複検出
2. feasibility-constraints.json との制約マッチ
3. implementation_check / feasibility フィールドの記入状況チェック
4. Quick Wins 一覧の出力
5. 施策化レディネスサマリー

使用方法:
    python3 scripts/audit-actions.py --week 2026-w14
    python3 scripts/audit-actions.py --week 2026-w14 --auto-fill
    python3 scripts/audit-actions.py --week 2026-w14 --report-only
"""

import argparse
import json
import os
import sys
from typing import Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")
IMPLEMENTATIONS_PATH = os.path.join(REPO_ROOT, "known-implementations.json")
CONSTRAINTS_PATH = os.path.join(REPO_ROOT, "feasibility-constraints.json")


def load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"エラー: {path} が見つかりません", file=sys.stderr)
        return {}


def build_keyword_index(implementations: dict) -> list[dict]:
    """known-implementations.json からフラットなキーワードインデックスを構築"""
    index = []
    for category in implementations.get("categories", []):
        for impl in category.get("implementations", []):
            index.append({
                "category_id": category["id"],
                "category_label": category["label"],
                "title": impl["title"],
                "date": impl["date"],
                "keywords": [kw.lower() for kw in impl.get("keywords", [])],
                "detail": impl.get("detail", ""),
            })
    return index


def build_constraint_index(constraints_data: dict) -> list[dict]:
    """feasibility-constraints.json からフラットな制約インデックスを構築"""
    index = []
    for constraint in constraints_data.get("constraints", []):
        index.append({
            "id": constraint["id"],
            "label": constraint["label"],
            "trigger_keywords": [kw.lower() for kw in constraint.get("trigger_keywords", [])],
            "risk": constraint.get("risk", "low"),
            "issues": constraint.get("issues", []),
            "mitigation": constraint.get("mitigation", ""),
            "verification_questions": constraint.get("verification_questions", []),
        })
    return index


# 汎用キーワード: 1語だけのマッチでは偽陽性になりやすいため、
# score==1 かつ全マッチが汎用キーワードの場合は partial フラグを立てない
GENERIC_KEYWORDS = {
    "カレンダー", "検索", "口コミ", "トップページ", "フィルター", "cta",
    "フローティング", "確定", "エリアページ", "パフォーマンス", "お気に入り",
    "おすすめ", "bot", "レビュー", "リスト", "ヘッダー", "カテゴリ", "アプリ",
    "ネイティブ", "検索ui", "モバイル", "デスクトップ", "ai", "クロール",
    "クーポン", "補足", "サマリー",
    # 第2ラウンド追加: 単独では偽陽性になるキーワード
    "ナビゲーション", "表示速度", "評価", "気になる", "seo", "検索結果",
    "カルーセル", "api", "カラー", "レコメンド",
}


def match_implementation(action_title: str, action_desc: str, keyword_index: list[dict]) -> list[dict]:
    """施策タイトル・説明文とキーワードインデックスをマッチング"""
    text = (action_title + " " + action_desc).lower()
    matches = []
    for impl in keyword_index:
        matched_keywords = [kw for kw in impl["keywords"] if kw in text]
        if matched_keywords:
            # 汎用キーワードのみの1語マッチはスキップ（偽陽性防止）
            all_generic = all(kw in GENERIC_KEYWORDS for kw in matched_keywords)
            if len(matched_keywords) == 1 and all_generic:
                continue
            matches.append({
                **impl,
                "matched_keywords": matched_keywords,
                "score": len(matched_keywords),
            })
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches


def match_constraints(action_title: str, action_desc: str, action_spec: str,
                      constraint_index: list[dict]) -> list[dict]:
    """施策タイトル・説明・仕様と制約キーワードをマッチング"""
    text = (action_title + " " + action_desc + " " + action_spec).lower()
    matches = []
    for constraint in constraint_index:
        matched_keywords = [kw for kw in constraint["trigger_keywords"] if kw in text]
        if matched_keywords:
            matches.append({
                "id": constraint["id"],
                "label": constraint["label"],
                "risk": constraint["risk"],
                "matched_keywords": matched_keywords,
                "mitigation": constraint["mitigation"],
                "verification_questions": constraint["verification_questions"],
            })
    return matches


def estimate_effort(action_spec: str, constraints: list[dict]) -> str:
    """施策の工数レベルを推定"""
    spec_lower = action_spec.lower()
    has_high_risk = any(c["risk"] == "high" for c in constraints)
    backend_keywords = ["バックエンド", "api新設", "db", "サーバー", "インフラ", "bigquery"]
    needs_backend = any(kw in spec_lower for kw in backend_keywords)
    partner_keywords = ["globick", "linktivity", "fareharbor", "tiqets", "パートナーapi"]
    needs_partner = any(kw in spec_lower for kw in partner_keywords)

    if needs_partner:
        return "L"
    if needs_backend or has_high_risk:
        return "M"
    tracking_keywords = ["トラッキング", "計測", "rum", "モニタリング", "ga4設定"]
    if any(kw in spec_lower for kw in tracking_keywords):
        return "S"
    return "S"


def audit_week(week_id: str, auto_fill: bool = False, report_only: bool = False) -> int:
    """指定週のボトルネック分析を監査"""
    week_dir = os.path.join(REPORTS_DIR, week_id)
    if not os.path.isdir(week_dir):
        print(f"エラー: {week_dir} が見つかりません", file=sys.stderr)
        return 1

    implementations = load_json(IMPLEMENTATIONS_PATH)
    constraints_data = load_json(CONSTRAINTS_PATH)

    if not implementations or not constraints_data:
        return 1

    keyword_index = build_keyword_index(implementations)
    constraint_index = build_constraint_index(constraints_data)

    # 集計カウンタ
    total_actions = 0
    overlap_actions = []       # already_exists / superseded
    partial_actions = []       # partial
    high_risk_actions = []     # high risk constraints
    quick_win_actions = []     # effort=S, constraints=[]
    missing_check = []         # implementation_check 未記入
    missing_feasibility = []   # feasibility 未記入
    all_actions = []           # 全施策の詳細

    for bn_num in range(1, 11):
        content_path = os.path.join(week_dir, f"bottleneck-{bn_num}-content.json")
        if not os.path.exists(content_path):
            continue

        content = load_json(content_path)
        bn_title = content.get("title", f"Bottleneck {bn_num}")

        for hypo in content.get("hypotheses", []):
            for action in hypo.get("actions", []):
                total_actions += 1
                letter = action.get("letter", "?")
                title = action.get("title", "")
                desc = action.get("description", "")
                spec = action.get("spec_html", "")
                action_id = f"B{bn_num}-{letter}"

                # 自動マッチング
                impl_matches = match_implementation(title, desc, keyword_index)
                constraint_matches = match_constraints(title, desc, spec, constraint_index)
                effort = estimate_effort(spec, constraint_matches)

                action_info = {
                    "id": action_id,
                    "bn_num": bn_num,
                    "bn_title": bn_title,
                    "letter": letter,
                    "title": title,
                    "impl_matches": impl_matches,
                    "constraint_matches": constraint_matches,
                    "estimated_effort": effort,
                }
                all_actions.append(action_info)

                # 重複チェック（スコア2以上、またはキーワード完全一致）
                if impl_matches and impl_matches[0]["score"] >= 2:
                    overlap_actions.append(action_info)
                elif impl_matches and impl_matches[0]["score"] == 1:
                    partial_actions.append(action_info)

                # 高リスク制約
                if any(c["risk"] == "high" for c in constraint_matches):
                    high_risk_actions.append(action_info)

                # Quick Wins (重複ではない場合のみ)
                is_overlap = impl_matches and impl_matches[0]["score"] >= 2
                if effort == "S" and not constraint_matches and not is_overlap:
                    quick_win_actions.append(action_info)

                # フィールド記入チェック
                impl_check = action.get("implementation_check")
                if not impl_check or impl_check.get("status") is None:
                    missing_check.append(action_id)

                feasibility = action.get("feasibility")
                if not feasibility or feasibility.get("effort") is None:
                    missing_feasibility.append(action_id)

                # auto-fill モード
                if auto_fill and not report_only:
                    if "implementation_check" not in action:
                        if impl_matches and impl_matches[0]["score"] >= 2:
                            action["implementation_check"] = {
                                "status": "already_exists",
                                "matched_feature": impl_matches[0]["title"],
                                "note": f"キーワード一致: {', '.join(impl_matches[0]['matched_keywords'])}。{impl_matches[0]['detail']}"
                            }
                        elif impl_matches and impl_matches[0]["score"] == 1:
                            action["implementation_check"] = {
                                "status": "partial",
                                "matched_feature": impl_matches[0]["title"],
                                "note": f"類似機能あり（{impl_matches[0]['title']}）。差分を確認してください。"
                            }
                        else:
                            action["implementation_check"] = {
                                "status": "new",
                                "matched_feature": None,
                                "note": None
                            }

                    if "feasibility" not in action:
                        constraint_ids = [c["id"] for c in constraint_matches]
                        constraint_notes = "; ".join(c["mitigation"] for c in constraint_matches[:2]) if constraint_matches else ""
                        prereqs = []
                        for c in constraint_matches:
                            prereqs.extend(c.get("verification_questions", [])[:1])
                        action["feasibility"] = {
                            "effort": effort,
                            "constraints": constraint_ids,
                            "constraint_notes": constraint_notes[:200] if constraint_notes else "",
                            "prerequisites": prereqs[:3],
                            "quick_wins": effort == "S" and len(constraint_ids) == 0
                        }

        # auto-fill の場合はファイルを書き戻す
        if auto_fill and not report_only:
            with open(content_path, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
                f.write("\n")

    # ── レポート出力 ──

    print(f"\n{'='*70}")
    print(f"  施策化レビュー監査レポート: {week_id}")
    print(f"{'='*70}")

    print(f"\n📊 サマリー")
    print(f"  総施策数:         {total_actions}")
    print(f"  重複疑い:         {len(overlap_actions)} 件（要差し替え）")
    print(f"  部分重複:         {len(partial_actions)} 件（差分確認要）")
    print(f"  高リスク制約:     {len(high_risk_actions)} 件")
    print(f"  Quick Wins:       {len(quick_win_actions)} 件（即実装可能）")
    print(f"  check未記入:      {len(missing_check)} 件")
    print(f"  feasibility未記入: {len(missing_feasibility)} 件")

    if overlap_actions:
        print(f"\n{'─'*70}")
        print(f"❌ 重複疑い（already_exists 候補）— 代替施策への差し替え推奨")
        print(f"{'─'*70}")
        for a in overlap_actions:
            best = a["impl_matches"][0]
            print(f"  [{a['id']}] {a['title']}")
            print(f"    → 既存: {best['title']}（{best['date']}）")
            print(f"    → 一致KW: {', '.join(best['matched_keywords'])}")
            print()

    if partial_actions:
        print(f"\n{'─'*70}")
        print(f"⚠️  部分重複（partial 候補）— 差分の確認が必要")
        print(f"{'─'*70}")
        for a in partial_actions:
            best = a["impl_matches"][0]
            print(f"  [{a['id']}] {a['title']}")
            print(f"    → 類似: {best['title']}（{best['date']}）")
            print(f"    → 一致KW: {', '.join(best['matched_keywords'])}")
            print()

    if high_risk_actions:
        print(f"\n{'─'*70}")
        print(f"🔴 高リスク制約 — 施策化前に前提確認が必要")
        print(f"{'─'*70}")
        for a in high_risk_actions:
            high_constraints = [c for c in a["constraint_matches"] if c["risk"] == "high"]
            print(f"  [{a['id']}] {a['title']}")
            for c in high_constraints:
                print(f"    → 制約: {c['label']} (risk: {c['risk']})")
                print(f"    → KW: {', '.join(c['matched_keywords'])}")
                if c.get("verification_questions"):
                    print(f"    → 確認: {c['verification_questions'][0]}")
            print()

    if quick_win_actions:
        print(f"\n{'─'*70}")
        print(f"✅ Quick Wins（effort=S, 制約なし）— 即施策化候補")
        print(f"{'─'*70}")
        for a in quick_win_actions:
            print(f"  [{a['id']}] {a['title']}")
        print()

    # 施策化レディネス
    ready_count = total_actions - len(overlap_actions)
    ready_pct = (ready_count / total_actions * 100) if total_actions > 0 else 0
    print(f"\n{'='*70}")
    print(f"  施策化レディネス: {ready_count}/{total_actions} ({ready_pct:.0f}%)")
    print(f"  Quick Wins: {len(quick_win_actions)} 件 → すぐに着手可能")
    print(f"{'='*70}\n")

    # エラー判定
    errors = 0
    if missing_check and not auto_fill:
        print(f"[ERROR] implementation_check 未記入: {len(missing_check)} 件")
        errors += 1
    if missing_feasibility and not auto_fill:
        print(f"[ERROR] feasibility 未記入: {len(missing_feasibility)} 件")
        errors += 1

    return errors


def main():
    parser = argparse.ArgumentParser(description="打ち手の施策化レビュー監査")
    parser.add_argument("--week", required=True, help="対象週（例: 2026-w14）")
    parser.add_argument("--auto-fill", action="store_true",
                        help="implementation_check と feasibility を自動推定で記入")
    parser.add_argument("--report-only", action="store_true",
                        help="レポートのみ出力（ファイル変更なし）")
    args = parser.parse_args()

    errors = audit_week(args.week, auto_fill=args.auto_fill, report_only=args.report_only)
    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
