#!/usr/bin/env python3
"""Extract content.json skeleton from existing bottleneck HTML files.
Outputs a minimal but valid content.json for testing the dynamic template."""

import json, re, sys, os
from html.parser import HTMLParser

WEEK_DIR = "/home/user/v2-veltra-cvr/reports/2026-w14"

# Page metadata extracted from reading the HTML files
PAGES = [
    {
        "number": 1,
        "title": "Organic Search \u00d7 Mobile \u2014 \u2462\u2192\u2463 意向転換率の低さ",
        "tags": [
            {"label": "\u2462\u2192\u2463 検討\u2192意向", "type": "red"},
            {"label": "Organic Search", "type": "default"},
            {"label": "Mobile", "type": "default"},
            {"label": "channel_x_device", "type": "default"}
        ],
        "deviation": "-42%",
        "impact_sessions": "923K / 月",
        "description_html": "カレンダーは表示されるが、フォーム（予約開始）に進まない。<br>\u2462\u2192\u2463 意向転換率（form_start / calendar_view）: <strong style=\"color:var(--red)\">50.38%</strong> vs ベースライン <strong>86.62%</strong> \u2192 <strong style=\"color:var(--red)\">-41.8%（-36.24pp）</strong><br>CVR: 0.6314% vs 1.4568%",
        "funnel_overview": {
            "title": "ファネル全体比較（Organic Search \u00d7 Mobile vs ベースライン）",
            "cells": [
                {"label": "\u2460\u2192\u2461 流入\u2192AC到達", "value": "22.04%", "sub": "ベースライン 26.10%"},
                {"label": "\u2461\u2192\u2462 AC到達\u2192検討", "value": "57.21%", "sub": "ベースライン 75.01%"},
                {"label": "\u2462\u2192\u2463 検討\u2192意向", "value": "50.38%", "sub": "ベースライン 86.62% | -41.8%", "alert": True},
                {"label": "\u2463\u2192\u2464 意向\u2192完了", "value": "12.65%", "sub": "ベースライン 12.65%"}
            ]
        },
        "funnel_compare": [
            {"label": "全体平均", "stage": "\u2462\u2192\u2463 意向転換", "value": "86.62%", "sub": "ベースライン"},
            {"label": "Organic \u00d7 Mobile", "stage": "\u2462\u2192\u2463 意向転換", "value": "50.38%", "sub": "-41.8% vs 全体", "alert": True},
            {"label": "Paid Search \u00d7 Mobile", "stage": "\u2462\u2192\u2463 意向転換", "value": "60.12%", "sub": "-30.6% vs 全体"},
            {"label": "Organic \u00d7 Desktop", "stage": "\u2462\u2192\u2463 意向転換", "value": "83.40%", "sub": "-3.7% vs 全体"}
        ],
        "drill_down": [
            {
                "title": "Organic Search（チャネル全体）",
                "body_html": "Organic Search（全体）: \u2462\u2192\u2463 = <strong style=\"color:var(--red)\">60.22%</strong>（-30.5% vs ベースライン）",
                "note": "チャネル全体でも低いが、Mobileに絞ると50.4%とさらに深刻。"
            },
            {
                "title": "新規 vs リピーター（Organic Search）",
                "body_html": "Organic \u00d7 <strong style=\"color:var(--red)\">新規: \u2462\u2192\u2463 = 52.74%</strong>（723Kセッション）<br>Organic \u00d7 リピーター: \u2462\u2192\u2463 = 63.86%（451Kセッション）",
                "note": "新規もリピーターも低い。Mobileで特に深刻。"
            }
        ],
        "callout": {
            "title": "特定結果",
            "body_html": "<strong>Organic Search \u00d7 Mobile</strong> の \u2462\u2192\u2463 意向転換率が <strong>50.38%</strong>（全体平均 86.62% の <strong>-41.8%</strong>）。<br>月間 923Kセッション。カレンダーを表示した後にフォーム開始（予約開始）に進むユーザーが半数に満たない。<br>Desktop（83.4%）と比べて33pp低く、モバイルUI固有の問題が示唆される。ACページのプラン選択・予約CTAの視認性がモバイルで著しく低下している可能性が高い。"
        },
        "hypo_section_title": "原因仮説 \u00d7 3 &amp; 打ち手 \u00d7 9",
        "hypo_section_desc": "なぜ Organic Search \u00d7 Mobile の\u2462\u2192\u2463意向転換率が低いか？ 仮説をクリックして打ち手・プロトタイプを展開。",
    },
    {
        "number": 2,
        "title": "Organic Search \u00d7 新規 \u2014 \u2461\u2192\u2462 検討転換率の低さ",
        "tags": [
            {"label": "\u2461\u2192\u2462 AC到達\u2192検討", "type": "red"},
            {"label": "Organic Search", "type": "default"},
            {"label": "新規ユーザー", "type": "default"}
        ],
        "deviation": "-58%",
        "impact_sessions": "723K / 月",
    },
    {
        "number": 3,
        "title": "Paid Search \u00d7 新規 \u2014 \u2461\u2192\u2462 検討転換率の低さ",
        "tags": [
            {"label": "\u2461\u2192\u2462 AC到達\u2192検討", "type": "red"},
            {"label": "Paid Search", "type": "default"},
            {"label": "新規ユーザー", "type": "default"}
        ],
        "deviation": "-55%",
        "impact_sessions": "386K / 月",
    },
    {
        "number": 4,
        "title": "Paid Search \u00d7 Mobile \u2014 \u2462\u2192\u2463 意向転換率の低さ",
        "tags": [
            {"label": "\u2462\u2192\u2463 検討\u2192意向", "type": "red"},
            {"label": "Paid Search", "type": "default"},
            {"label": "Mobile", "type": "default"}
        ],
        "deviation": "-30.6%",
        "impact_sessions": "515,780 / 月",
    },
    {
        "number": 5,
        "title": "Organic Search \u00d7 リピーター \u2014 \u2462\u2192\u2463 意向転換率の低さ",
        "tags": [
            {"label": "\u2462\u2192\u2463 検討\u2192意向", "type": "red"},
            {"label": "Organic Search", "type": "default"},
            {"label": "リピーター", "type": "default"}
        ],
        "deviation": "-26.3%",
        "impact_sessions": "451,499 / 月",
    },
    {
        "number": 6,
        "title": "Organic Search \u00d7 新規 \u2014 \u2460\u2192\u2461 AC到達率の低さ",
        "tags": [
            {"label": "\u2460\u2192\u2461 流入\u2192AC到達", "type": "red"},
            {"label": "Organic Search", "type": "default"},
            {"label": "新規ユーザー", "type": "default"}
        ],
        "deviation": "-33.1%",
        "impact_sessions": "723,479 / 月",
    },
    {
        "number": 7,
        "title": "Direct \u00d7 新規 \u2014 \u2460\u2192\u2461 AC到達率の低さ",
        "tags": [
            {"label": "\u2460\u2192\u2461 流入\u2192AC到達", "type": "red"},
            {"label": "Direct", "type": "default"},
            {"label": "新規ユーザー", "type": "default"}
        ],
        "deviation": "-68%",
        "impact_sessions": "274,917 / 月",
    },
    {
        "number": 8,
        "title": "Direct \u00d7 Desktop \u2014 \u2460\u2192\u2461 AC到達率の低さ（異常値）",
        "tags": [
            {"label": "\u2460\u2192\u2461 流入\u2192AC到達", "type": "red"},
            {"label": "Direct", "type": "default"},
            {"label": "Desktop", "type": "default"}
        ],
        "deviation": "-86%",
        "impact_sessions": "180K / 月",
    },
    {
        "number": 9,
        "title": "Paid Search \u00d7 Returning \u2014 \u2462\u2192\u2463 意向転換率の低さ",
        "tags": [
            {"label": "\u2462\u2192\u2463 検討\u2192意向", "type": "red"},
            {"label": "Paid Search", "type": "default"},
            {"label": "Returning", "type": "default"}
        ],
        "deviation": "-13.9%",
        "impact_sessions": "273K / 月",
    },
    {
        "number": 10,
        "title": "Organic Search \u00d7 Desktop \u2014 \u2461\u2192\u2462 検討転換率の低さ",
        "tags": [
            {"label": "\u2461\u2192\u2462 AC到達\u2192検討", "type": "red"},
            {"label": "Organic Search", "type": "default"},
            {"label": "Desktop", "type": "default"}
        ],
        "deviation": "-9.1%",
        "impact_sessions": "301K / 月",
    },
]

# Write minimal content.json for each page (metadata + empty hypotheses structure)
for page in PAGES:
    n = page["number"]
    out_path = os.path.join(WEEK_DIR, f"bottleneck-{n}-content.json")
    
    # Only add hypotheses placeholder if not already present
    if "hypotheses" not in page:
        page["hypotheses"] = []
    if "competitive" not in page:
        page["competitive"] = []
    if "verification" not in page:
        page["verification"] = []
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(page, f, ensure_ascii=False, indent=2)
    print(f"Written: {out_path}")

print("Done. Now add hypotheses/actions content to each file.")
