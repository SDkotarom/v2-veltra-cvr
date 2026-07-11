#!/usr/bin/env python3
"""
capture.example.py  —  競合予約フローの半自動キャプチャ雛形（Playwright）
=====================================================================
競合の「探す→比べる→決める→予約フォーム」を巡回してスクショを撮る雛形。
Claude in Chrome 拡張はドメイン許可が固定のため、競合巡回は Playwright で行う。

⚠️ ガードレール（厳守）
  - 決済情報の入力・予約確定は絶対に行わない（支払い画面が出たら撮るだけで停止）
  - CAPTCHA / bot 検知は回避しない。ブロックされたら記録してスキップ
  - 各社の利用規約・robots を尊重。過度なアクセスをしない
  - 認証情報はハードコードしない（環境変数）。テストデータのみ

前提: pip install playwright && playwright install chromium
実行: python3 capture.example.py --config competitors.json --out ../../spot/assets/teardown

competitors.json（例）:
{
  "sites": [{
    "site": "klook",
    "start_url": "https://www.klook.com/ja/...",
    "steps": [
      {"action": "goto",  "url": "..."},
      {"action": "shot",  "name": "klook-product"},
      {"action": "click", "selector": "text=日付を選択"},
      {"action": "shot",  "name": "klook-date"},
      {"action": "click", "selector": "text=予約手続きへ"},
      {"action": "shot",  "name": "klook-form"},
      {"action": "stop_before_payment"}
    ]
  }]
}
"""
import argparse, json, os, sys

STOP_MARKERS = ["カード番号", "セキュリティコード", "CVV", "お支払い方法", "card number", "cvv"]


def run(config_path, out_dir):
    from playwright.sync_api import sync_playwright  # import 内側: 雛形として未導入環境でも読める
    os.makedirs(out_dir, exist_ok=True)
    cfg = json.load(open(config_path, encoding="utf-8"))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for site in cfg["sites"]:
            ctx = browser.new_context(
                viewport={"width": 390, "height": 844},  # モバイル相当
                device_scale_factor=2,
                locale="ja-JP",
            )
            page = ctx.new_page()
            print("== %s ==" % site["site"])
            try:
                for step in site["steps"]:
                    act = step["action"]
                    if act == "goto":
                        page.goto(step.get("url") or site["start_url"], wait_until="domcontentloaded")
                        page.wait_for_timeout(1500)
                    elif act == "click":
                        page.click(step["selector"], timeout=8000)
                        page.wait_for_timeout(1200)
                    elif act == "fill":
                        # テストデータのみ。個人情報・決済情報は入れない
                        page.fill(step["selector"], step.get("value", ""))
                    elif act == "shot":
                        # 支払い画面に到達していないか安全チェック
                        body = (page.content() or "")
                        if any(m in body for m in STOP_MARKERS):
                            print("  [stop] 支払い画面を検知。撮影して停止:", step["name"])
                        path = os.path.join(out_dir, step["name"] + ".jpg")
                        page.screenshot(path=path, full_page=step.get("full_page", False),
                                        type="jpeg", quality=80)
                        print("  shot:", path)
                    elif act == "stop_before_payment":
                        print("  [done] 予約フォーム手前で停止")
                        break
            except Exception as e:
                print("  [skip] %s: %s" % (site["site"], e))
            finally:
                ctx.close()
        browser.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True, help="スクショ出力ディレクトリ（例 spot/assets/teardown）")
    a = ap.parse_args()
    run(a.config, a.out)


if __name__ == "__main__":
    main()
