#!/usr/bin/env python3
"""
Veltra商品レビューページから rating(10点満点) / reviews(整数) を取得し
JSON出力するスクレイパー。

【実行方法（ベルトラ社内環境で）】
    python3 scrape_ratings.py > ratings.json

【出力フォーマット】
    [{"id": "183789", "rating": 8.4, "reviews": 21}, ...]

【利用ポリシー】
- User-Agent を明示
- リクエスト間隔 1.5s（穏当）
- 1日1回までの想定
- robots.txt は事前に確認すること: https://www.veltra.com/robots.txt
"""
import json, re, sys, time, urllib.request, urllib.error

# baseball/index.html の ACS 44商品ID（順序維持）
PRODUCT_IDS = [
    "183789","201111","186386","182662","193884","202305","202801","108997",
    "192599","192640","202524","203432","202804","177648","202644","202802",
    "202515","204024","203447","202806","202799","202796","202793","202652",
    "202649","202646","202643","202640","202638","202637","202632","202629",
    "202628","202627","202624","202534","202532","202530","202526","202525",
    "202520","202442","200028","184887",
]

# 商品IDから国/エリアパスへのマッピング（カテゴリページHTMLから抽出済）
URL_PATH = {
    "183789":"north_america/los_angeles","201111":"north_america/los_angeles",
    "186386":"north_america/los_angeles","182662":"north_america/los_angeles",
    "193884":"north_america/los_angeles","202305":"north_america/los_angeles",
    "202801":"north_america/canada/toronto","108997":"north_america/new_york",
    "192599":"north_america/new_york","192640":"north_america/new_york",
    "202524":"north_america/chicago","203432":"north_america/los_angeles",
    "202804":"north_america/new_york","177648":"north_america/new_york",
    "202644":"north_america/san_francisco","202802":"north_america/new_york",
    "202515":"north_america/los_angeles","204024":"north_america/los_angeles",
    "203447":"north_america/philadelphia","202806":"north_america/america_Other",
    "202799":"north_america/america_Other","202796":"north_america/america_Other",
    "202793":"north_america/phoenix_scottsdale","202652":"north_america/philadelphia",
    "202649":"north_america/denver","202646":"north_america/atlanta",
    "202643":"north_america/america_Other","202640":"north_america/seattle",
    "202638":"north_america/america_Other","202637":"north_america/chicago",
    "202632":"north_america/miami","202629":"north_america/america_Other",
    "202628":"north_america/america_Other","202627":"north_america/houston",
    "202624":"north_america/america_Other","202534":"north_america/america_Other",
    "202532":"north_america/boston","202530":"north_america/america_Other",
    "202526":"north_america/washington_dc","202525":"north_america/america_Other",
    "202520":"north_america/san_diego","202442":"north_america/boston",
    "200028":"north_america/canada/toronto","184887":"asia/taiwan/taipei",
}

UA = "Mozilla/5.0 (compatible; VeltraInternalRatingFetcher/1.0; +https://www.veltra.com)"
INTERVAL_SEC = 1.5

# Veltraの商品トップは "average rating: X.XX" を JSON-LD AggregateRating か
# 専用要素で出力している。reviewsトップページ末尾の "averageRating" を最優先で拾い、
# 取れない場合は score 表記をフォールバック。
RE_AGG = re.compile(r'"ratingValue"\s*:\s*"?([0-9.]+)"?\s*,\s*"reviewCount"\s*:\s*"?(\d+)"?')
RE_SCORE = re.compile(r'<span[^>]*class="score"[^>]*>\s*([0-9.]+)\s*</span>')
RE_COUNT = re.compile(r'体験談を読む（全(\d+)件')


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja"})
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read()
        # Veltraページは UTF-8
        return raw.decode("utf-8", errors="replace")


def parse(html: str):
    """rating(decimal), reviews(int) を返す。取れなければNone。"""
    m = RE_AGG.search(html)
    if m:
        return float(m.group(1)), int(m.group(2))
    rating = None
    reviews = None
    m = RE_SCORE.search(html)
    if m:
        rating = float(m.group(1))
    m = RE_COUNT.search(html)
    if m:
        reviews = int(m.group(1))
    return rating, reviews


def main():
    results = []
    for i, pid in enumerate(PRODUCT_IDS, 1):
        path = URL_PATH.get(pid, "")
        url = f"https://www.veltra.com/jp/{path}/a/{pid}/reviews/"
        try:
            html = fetch(url)
            rating, reviews = parse(html)
        except urllib.error.HTTPError as e:
            print(f"[{i}/44] {pid} HTTP {e.code}", file=sys.stderr)
            rating, reviews = None, None
        except Exception as e:
            print(f"[{i}/44] {pid} ERROR: {e}", file=sys.stderr)
            rating, reviews = None, None
        results.append({"id": pid, "rating": rating, "reviews": reviews})
        print(f"[{i}/44] {pid}: rating={rating} reviews={reviews}", file=sys.stderr)
        if i < len(PRODUCT_IDS):
            time.sleep(INTERVAL_SEC)
    json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
    print(file=sys.stdout)


if __name__ == "__main__":
    main()
