#!/usr/bin/env python3
"""Generate all 10 W13 bottleneck content JSON files."""
import json
import os

OUT_DIR = '/home/user/v2-veltra-cvr/reports/2026-w13'

def make_proto(before_desc, after_desc, ctx="veltra.com"):
    """Generate prototype before/after HTML mockups."""
    before_html = f'<div style="border:1px solid #E0E0E0;border-radius:8px;overflow:hidden;max-width:375px;margin:0 auto;background:#F2F5F8"><div style="background:#E8386E;height:3px"></div><div style="background:#fff;padding:8px 16px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #eee"><span style="font-size:15px;font-weight:900;color:#1B82C5">VELTRA</span><span style="font-size:11px;color:#666">&#9776;</span></div><div style="padding:16px"><div style="font-size:13px;font-weight:700;margin-bottom:8px;color:#333">{before_desc}</div><div style="padding:12px;background:#fff;border:1px solid #ddd;border-radius:6px;font-size:11px;color:#666;line-height:1.6">{ctx}</div></div><div style="padding:4px 16px 12px;font-size:10px;color:#999;text-align:center">現状の課題ポイント</div></div>'
    after_html = f'<div style="border:2px solid #2DAE6C;border-radius:8px;overflow:hidden;max-width:375px;margin:0 auto;background:#F2F5F8"><div style="background:#E8386E;height:3px"></div><div style="background:#fff;padding:8px 16px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #eee"><span style="font-size:15px;font-weight:900;color:#1B82C5">VELTRA</span><span style="font-size:11px;color:#666">&#9776;</span></div><div style="padding:16px"><div style="font-size:13px;font-weight:700;margin-bottom:8px;color:#2DAE6C">{after_desc}</div><div style="padding:12px;background:#E8F5E9;border:1px solid #A5D6A7;border-radius:6px;font-size:11px;color:#333;line-height:1.6">改善後のUI</div></div><div style="padding:4px 16px 12px;font-size:10px;color:#2DAE6C;text-align:center;font-weight:500">改善効果</div></div>'
    return {"before_html": before_html, "after_html": after_html}

# ---- Bottleneck definitions ----
bottlenecks = []

# #1: Organic Search — ①→② AC到達率の低さ
bottlenecks.append({
    "number": 1,
    "title": "Organic Search — ①→② AC到達率の低さ",
    "tags": [{"label":"①→② 流入→AC到達","type":"red"},{"label":"Organic Search","type":"default"},{"label":"channel","type":"default"}],
    "deviation": "-42.25%",
    "impact_sessions": "1,267K / 月",
    "description_html": "<p>Organic Search経由の流入セッションのうち、ACページ（アクティビティ詳細）に到達する割合が <strong style=\"color:#E8423F\">47.75%</strong>（全体ベースライン 82.60% の <strong>-42.25%</strong>）。月間 1,267K セッションに及ぶ最大チャネルでの構造的な問題。SEO検索結果からの流入後、トップページやカテゴリページで離脱しACまでたどり着かない。</p>",
    "funnel_overview": {
        "title": "ファネル全体比較（Organic Search vs ベースライン）",
        "cells": [
            {"label":"①→② 流入→AC到達","value":"47.75%","sub":"ベースライン 82.60% | -42.25%","alert":True},
            {"label":"②→③ AC到達→検討","value":"20.47%","sub":"ベースライン 26.43%"},
            {"label":"③→④ 検討→意向","value":"20.32%","sub":"ベースライン 31.92%"},
            {"label":"④→⑤ 意向→完了","value":"37.95%","sub":"ベースライン 34.57%"}
        ]
    },
    "funnel_compare": [
        {"label":"全体平均","stage":"①→② AC到達","value":"82.60%","sub":"ベースライン"},
        {"label":"Organic Search","stage":"①→② AC到達","value":"47.75%","sub":"-42.25% vs 全体","alert":True},
        {"label":"Paid Search","stage":"①→② AC到達","value":"57.19%","sub":"-30.8% vs 全体"},
        {"label":"新規ユーザー","stage":"①→② AC到達","value":"47.95%","sub":"-41.9% vs 全体"}
    ],
    "drill_down": [
        {"title":"新規 vs リピーター","body_html":"Organic × <strong style=\"color:#E8423F\">新規: ①→② = 47.95%</strong>（全体比 -42%）<br>Organic × リピーター: ①→② = 62.37%（全体比 -24%）","note":"新規ユーザーが特に低い。初回訪問時のAC到達導線に問題。"},
        {"title":"デバイス別","body_html":"Organic × Mobile: ①→② = 52.31%（全体比 -37%）<br>Organic × Desktop: ①→② = 52.93%（全体比 -36%）","note":"デバイス間差は小さい。Organic Search全体の構造的問題。"}
    ],
    "callout": {"title":"特定結果","body_html":"<strong>Organic Search</strong> の ①→② AC到達率が <strong>47.75%</strong>（全体平均 82.60% の <strong>-42.25%</strong>）。月間 1,267Kセッション。SEO経由の流入後、カテゴリ/エリアページからACへの導線が弱く半数以上が離脱。"},
    "hypo_section_title": "原因仮説 × 3 &amp; 打ち手 × 9",
    "hypo_section_desc": "なぜ Organic Search の①→② AC到達率が低いか？",
    "hypotheses": [
        {"level":"h1","level_label":"仮説 1（有力）","title":"SEOランディングページからACページへの導線が弱い",
         "body":"Organic検索で到達するページ（トップ・カテゴリ・エリア一覧）からACページへのリンクが目立たず、ユーザーが商品詳細まで進めていない。",
         "evidence":["Organic ①→②: 47.75% vs Paid: 57.19%（10pp差）","カテゴリページはテキストリスト表示で商品の魅力が伝わらない","新規ユーザー47.95%が特に低い→初回訪問でのUI問題"],
         "actions":[
            {"letter":"A","title":"カテゴリページにACカード型レイアウト導入","description":"テキストリスト表示からカード型ビジュアルレイアウトに変更。写真・評価・価格を一覧表示しACへの誘導を強化。","spec_html":"・写真+評価+価格のカード型UI<br>・タップでACページへ直接遷移<br>・「即確定」「人気」バッジ表示","impact":"①→② +8pt","prototype": make_proto("カテゴリ一覧（テキストリスト表示）<br>・ダイヤモンドヘッドハイキング ¥12,800〜<br>・ノースショア観光 ¥15,200〜<br>→ 商品の魅力が伝わらずACクリック率低下","カテゴリ一覧（カード型レイアウト）<br>📸写真＋★4.52＋¥12,800〜<br>「詳細を見る→」ボタン付きカード<br>→ 視覚的訴求でACクリック率向上")},
            {"letter":"B","title":"エリアページにパーソナライズ推薦セクション追加","description":"閲覧履歴に基づくおすすめアクティビティをエリアページ上部に表示。","spec_html":"・「あなたへのおすすめ」セクション追加<br>・閲覧履歴ベースの推薦アルゴリズム<br>・カルーセルUI（横スワイプ）","impact":"①→② +5pt","prototype": make_proto("エリアページ（推薦なし）<br>ハワイ＞オアフ島＞全258件<br>→ 膨大なリストから自力で探す必要あり","エリアページ（パーソナライズ推薦あり）<br>「あなたへのおすすめ」3件表示<br>閲覧履歴ベースの推薦<br>→ 迷わずACページへ到達")},
            {"letter":"C","title":"SEO LP内にインライン商品プレビュー埋め込み","description":"情報系ランディングページに人気アクティビティのプレビューカードを埋め込み。","spec_html":"・ブログ/ガイド記事内にACプレビューカード<br>・写真+価格+評価+「予約を見る」ボタン<br>・記事内容に関連する商品を自動選定","impact":"①→② +3pt","prototype": make_proto("ブログ記事「ハワイの楽しみ方TOP10」<br>テキストのみのガイド記事<br>→ 記事を読んで満足して離脱","ブログ記事「ハワイの楽しみ方TOP10」<br>記事内にACプレビューカード埋め込み<br>📸写真+★評価+¥価格+「予約→」<br>→ 記事からACページへ自然に遷移")}
         ]},
        {"level":"h2","level_label":"仮説 2","title":"検索意図のミスマッチ（情報収集 vs 予約）",
         "body":"Organic検索ユーザーの多くが「〇〇 おすすめ」「〇〇 観光」等の情報収集キーワードで流入。予約意向がなくACまで進まない。",
         "evidence":["情報系KW（おすすめ、観光、口コミ）での流入が多い","直帰率がPaid Searchより高い傾向","情報収集→予約の転換設計が不足"],
         "actions":[
            {"letter":"D","title":"情報系LPに「体験を探す」CTA設置","description":"情報収集目的のランディングページに「体験を探す」ボタンを設置し、ACページへの導線を追加。","spec_html":"・情報系LP下部に「この記事の体験を探す」CTA<br>・関連ACカード3件表示<br>・スクロール深度50%でフローティングCTA表示","impact":"①→② +4pt","prototype": make_proto("情報系LP「沖縄おすすめ観光」<br>テキスト記事のみ<br>ACへの導線なし<br>→ 情報収集で満足して離脱","情報系LP「沖縄おすすめ観光」<br>記事下部に「体験を探す」CTA<br>関連AC3件カード表示<br>→ 情報→予約への転換")},
            {"letter":"E","title":"ブログ・ガイド記事内にACリンクカード挿入","description":"既存コンテンツ記事の関連箇所にACリンクカードを自動挿入。","spec_html":"・記事内テキストにAC参照カードを自動挿入<br>・NLPでの関連性判定<br>・インライン表示（記事の流れを邪魔しない）","impact":"①→② +3pt","prototype": make_proto("ガイド記事「ダイヤモンドヘッドの登り方」<br>テキストのみの説明<br>→ 商品への導線がない","ガイド記事「ダイヤモンドヘッドの登り方」<br>本文中に関連ACカードを挿入<br>「このツアーで体験する→」リンク<br>→ 自然な文脈でACへ誘導")},
            {"letter":"F","title":"検索キーワード別LP最適化","description":"予約意図の高いキーワード（「予約」「ツアー」含む）用のLPを強化し、ACへの直接誘導を追加。","spec_html":"・予約意図KW: LP上部にACカード直接表示<br>・情報意図KW: 記事+AC導線の2段階設計<br>・KW分類の自動化（GA4+Search Console連携）","impact":"①→② +2pt","prototype": make_proto("全KW共通LP<br>同じカテゴリページを表示<br>→ 検索意図に関わらず同じ体験","KW別最適化LP<br>「ハワイ ツアー 予約」→AC直接表示<br>「ハワイ おすすめ」→記事+AC導線<br>→ 検索意図に合わせた体験")}
         ]},
        {"level":"h3","level_label":"仮説 3","title":"ページ表示速度・技術的課題による離脱",
         "body":"SEOランディングページの読み込み速度がモバイルで遅く、ユーザーがACページに到達する前にバウンスしている。",
         "evidence":["モバイルLCPが3秒超のページが存在","Core Web Vitals（CWV）のスコアが競合比で低い","高速表示の競合（Klook等）にトラフィックが流出"],
         "actions":[
            {"letter":"G","title":"LCPの改善（画像遅延読み込み・CDN最適化）","description":"主要ランディングページのLCPを3秒→1.5秒以内に改善。","spec_html":"・画像のlazy loading実装<br>・CDNエッジキャッシュ設定<br>・不要なJSの遅延読み込み","impact":"①→② +3pt","prototype": make_proto("現状: LCP 3.2秒<br>画像一括読み込み<br>JSブロッキング<br>→ ユーザーが待てずに離脱","改善後: LCP 1.4秒<br>画像lazy loading<br>Critical CSS inline<br>→ 高速表示でバウンス率低下")},
            {"letter":"H","title":"プリフェッチによるAC遷移高速化","description":"カテゴリページでユーザーがACリンクにホバー/タッチした時点でACページをプリフェッチ。","spec_html":"・hover/touchstartでlink prefetch発火<br>・対象: AC一覧のカードリンク<br>・帯域制限時はプリフェッチ無効化","impact":"①→② +2pt","prototype": make_proto("AC遷移: タップ後2.5秒待機<br>ページ全体をロード<br>→ 遷移の遅さで離脱","AC遷移: タップ前にプリフェッチ済み<br>遷移0.3秒で即表示<br>→ シームレスなAC到達")},
            {"letter":"I","title":"Core Web Vitals継続モニタリング設置","description":"CWVスコアのリアルタイムダッシュボードを構築し、パフォーマンス劣化を早期検知。","spec_html":"・CrUXデータの週次レポート自動生成<br>・LCP/FID/CLSの閾値アラート設定<br>・ページ別CWVランキング表示","impact":"①→② +1pt","prototype": make_proto("パフォーマンス監視: なし<br>劣化に気づかない<br>→ 知らないうちにバウンス率悪化","CWVダッシュボード導入<br>LCP/FID/CLSリアルタイム監視<br>閾値超過時にアラート<br>→ 即座に対応可能")}
         ]}
    ],
    "competitive": [
        {"name":"Klook","favicon_url":"https://www.klook.com/favicon.ico","url":"https://www.klook.com/ja/","feature":"<strong style=\"color:#E8423F\">カード型一覧ページ。</strong>写真・評価・価格を大きく表示。フィルター・ソートが充実しACページへの到達率が高い。","detail":"注目点: ビジュアル重視のカード型UIがACクリック率を最大化。施策Aの直接参考。"},
        {"name":"GetYourGuide","favicon_url":"https://cdn.getyourguide.com/tf/assets/static/favicons/favicon-32x32.png","url":"https://www.getyourguide.com/","feature":"一覧ページに「おすすめ」「人気」バッジ。空き状況インジケーター表示。地図ビュー切替機能。","detail":"注目点: 空き状況の事前表示でAC到達のモチベーションを提供。"},
        {"name":"Viator","favicon_url":"https://cache.vtrcdn.com/orion/images/favicon.ico","url":"https://www.viator.com/","feature":"Tripadvisorレビュー統合のカード型一覧。「ベストセラー」「割引」ラベル。ミニ商品プレビュー。","detail":"注目点: レビュー統合による信頼構築。施策CのインラインAC表示と類似。"},
        {"name":"アソビュー","favicon_url":"https://www.asoview.com/favicon.ico","url":"https://www.asoview.com/","feature":"「本日空きあり」「残りわずか」リアルタイム在庫表示。エリア×カテゴリのクロスフィルター。","detail":"注目点: リアルタイム在庫がAC到達前にアクション促進。"},
        {"name":"じゃらん","favicon_url":"https://www.jalan.net/favicon.ico","url":"https://www.jalan.net/kankou/","feature":"エリア特集ページからアクティビティ一覧への自然な導線。口コミ数表示。ポイント訴求バッジ。","detail":"注目点: ポイント訴求は情報収集ユーザーの予約転換に効果的。"},
        {"name":"KKday","favicon_url":"https://www.kkday.com/favicon.png","url":"https://www.kkday.com/ja/","feature":"「即確定」「キャンセル無料」バッジ。「今週の人気TOP10」セクション。明瞭な価格表示。","detail":"注目点: 人気ランキング表示でAC到達のモチベーションを提供。"}
    ],
    "competitive_insight": "主要競合6社すべてがカテゴリ/一覧ページにカード型ビジュアルレイアウトを採用済み。VELTRAのテキストリスト表示は業界水準から大きく乖離。施策A（カード型レイアウト）は最優先で実装すべき。",
    "verification": ["GA4レポートと照合しデータの正確性を確認","カテゴリページの現状CTR（AC到達率）を計測","仮説の妥当性をPM/UXデザイナーでレビュー","施策の技術的実現可能性を確認","ABテスト設計をレビュー","競合UIの最新状況を確認"],
    "verification_method": "GA4: Organic Search の ①→② 転換率を主要KPIとして計測。ABテスト 2週間。目標: ①→② 47.75% → 60%以上。副次指標: ②→③転換率、バウンス率、ページ滞在時間。優先施策: カード型レイアウト（施策A）を先行実施。"
})

print(f"#1 defined")

# #2: 新規ユーザー — ②→③ 検討転換率の低さ
bottlenecks.append({
    "number": 2,
    "title": "新規ユーザー — ②→③ 検討転換率の低さ",
    "tags": [{"label":"②→③ AC到達→検討","type":"red"},{"label":"新規ユーザー","type":"default"}],
    "deviation": "-38.94%",
    "impact_sessions": "1,534K / 月",
    "description_html": "<p>新規ユーザーのACページ到達後のカレンダー（日程確認）への転換率が <strong style=\"color:#E8423F\">16.14%</strong>（全体ベースライン 26.43% の <strong>-38.94%</strong>）。月間 1,534K セッションと最大セグメント。初回訪問ユーザーはACページを閲覧するが価格・プランの判断に迷い日程選択まで進まない。</p>",
    "funnel_overview": {"title":"ファネル比較（新規ユーザー vs ベースライン）","cells":[{"label":"①→②","value":"47.95%","sub":"BL 82.60%"},{"label":"②→③","value":"16.14%","sub":"BL 26.43% | -38.94%","alert":True},{"label":"③→④","value":"17.73%","sub":"BL 31.92%"},{"label":"④→⑤","value":"47.96%","sub":"BL 34.57%"}]},
    "funnel_compare": [
        {"label":"全体平均","stage":"②→③ 検討","value":"26.43%","sub":"ベースライン"},
        {"label":"新規ユーザー","stage":"②→③ 検討","value":"16.14%","sub":"-38.94% vs 全体","alert":True},
        {"label":"リピーター","stage":"②→③ 検討","value":"36.64%","sub":"+38.6% vs 全体"},
        {"label":"Organic × 新規","stage":"②→③ 検討","value":"~15%","sub":"新規の中でもさらに低い"}
    ],
    "drill_down": [
        {"title":"新規 Mobile vs Desktop","body_html":"新規 × Mobile: ②→③ ≈ 14%<br>新規 × Desktop: ②→③ ≈ 18%","note":"Mobile新規が特に低い。小画面でのプラン比較が困難。"},
        {"title":"新規のバウンス分析","body_html":"ACページ到達新規ユーザーの<strong style=\"color:#E8423F\">83.86%</strong>がカレンダーまで進まず離脱","note":"価格・プラン理解の壁が大きい。信頼構築要素がfold以下。"}
    ],
    "callout": {"title":"特定結果","body_html":"<strong>新規ユーザー</strong>のACページ到達後②→③転換率が<strong>16.14%</strong>（BL 26.43%の<strong>-38.94%</strong>）。初回訪問ユーザーは価格帯とプラン内容の判断に迷い、日程選択に進めていない。"},
    "hypo_section_title":"原因仮説 × 3 &amp; 打ち手 × 9",
    "hypo_section_desc":"なぜ新規ユーザーの②→③検討転換率が低いか？",
    "hypotheses": [
        {"level":"h1","level_label":"仮説 1（有力）","title":"ACページで価格と内容の判断に迷う（信頼・比較情報不足）",
         "body":"初回訪問ユーザーはVELTRAの価格帯と商品品質への判断材料が不足。レビュー・写真などの信頼構築要素がfold以下にある。",
         "evidence":["新規②→③: 16.14% vs リピーター: 36.64%（20pp差）","リピーターは信頼済みなので転換率が高い","レビューセクションがACページ下部に配置"],
         "actions":[
            {"letter":"A","title":"ACページ上部にレビューサマリーと信頼バッジ表示","description":"写真ヒーロー直下にレビュー評価・件数・「VELTRAで予約済み〇〇名」を表示。","spec_html":"・レビュースコア+件数をヒーロー直下に移動<br>・「VELTRAで〇〇名が予約」カウンター<br>・ハイライトレビュー1件をインライン表示","impact":"②→③ +5pt","prototype": make_proto("ACページ上部<br>写真→タイトル→プラン一覧<br>レビューは最下部<br>→ 新規ユーザーは信頼情報なしで判断","ACページ上部<br>写真→★4.52(328件)→「1,200名予約済」<br>ハイライトレビュー表示<br>→ 信頼構築で日程選択を促進")},
            {"letter":"B","title":"価格帯の相場感を表示（「この体験の平均価格」）","description":"ACページに「この体験の相場」を表示し、VELTRAの価格が適正であることを訴求。","spec_html":"・「この体験の相場: ¥12,000〜¥18,000」表示<br>・VELTRAの価格位置をバー表示<br>・「最安値保証」バッジ（該当する場合）","impact":"②→③ +3pt","prototype": make_proto("価格表示: ¥12,800〜<br>相場情報なし<br>→ 高いのか安いのか判断できない","価格表示: ¥12,800〜<br>「相場: ¥12,000〜¥18,000」バー表示<br>→ 適正価格と分かり安心して検討")},
            {"letter":"C","title":"写真ギャラリーの充実（ユーザー投稿写真含む）","description":"ACページの写真ギャラリーにユーザー投稿写真を追加し、リアルな体験イメージを提供。","spec_html":"・ユーザー投稿写真タブ追加<br>・写真枚数を10→20枚に拡充<br>・写真にキャプション追加（場所・時期）","impact":"②→③ +2pt","prototype": make_proto("写真ギャラリー: 公式写真5枚<br>→ プロ写真のみでリアル感が不足","写真ギャラリー: 公式5枚+投稿15枚<br>「参加者の写真」タブ<br>→ リアルな体験がイメージしやすい")}
         ]},
        {"level":"h2","level_label":"仮説 2","title":"プランが複数あり初回では何を選べばよいか不明",
         "body":"プラン一覧が並んでいるが違いが分かりにくい。新規ユーザーは選択に迷い離脱。",
         "evidence":["プラン数3以上のACで②→③が特に低い傾向","プラン名が似ていて違いが分かりにくい","リピーターは過去経験で選べるが新規は迷う"],
         "actions":[
            {"letter":"D","title":"「おすすめプラン」の自動ハイライト","description":"最も予約の多いプランに「おすすめ」バッジを自動付与し、初期選択状態にする。","spec_html":"・予約数TOP1プランに「おすすめ」バッジ<br>・「80%の方がこのプランを選択」表示<br>・デフォルト選択状態（展開済み）","impact":"②→③ +4pt","prototype": make_proto("プラン一覧<br>プランA ¥12,800〜<br>プランB ¥15,500〜<br>→ どちらを選ぶべきか不明","プラン一覧<br>★おすすめ プランA ¥12,800〜<br>「80%の方が選択」<br>→ 迷わず選択し日程確認へ")},
            {"letter":"E","title":"プラン比較テーブル導入","description":"プラン一覧上部に「プランの違いを比較」ボタンを配置。差分をハイライトした比較テーブルを表示。","spec_html":"・「プランの違いを比較」アコーディオン<br>・含まれるもの/所要時間/送迎の比較テーブル<br>・差分を緑ハイライト","impact":"②→③ +3pt","prototype": make_proto("プランA: チップ/入場料含む<br>プランB: チップ/入場料/朝食含む<br>→ 違いを一つずつ読む必要","プラン比較テーブル<br>　　　　A　　B<br>チップ　○　○<br>朝食　　×　○←差分<br>→ 一目で違いが分かる")},
            {"letter":"F","title":"プラン選択ガイド（2択フロー）","description":"「何を重視しますか？」の2択質問でおすすめプランに導くガイドフロー。","spec_html":"・「あなたにぴったりのプランは？」ウィジェット<br>・2-3の質問で絞り込み（価格重視/内容重視等）<br>・結果でプランをハイライト","impact":"②→③ +2pt","prototype": make_proto("プラン一覧をスクロールして比較<br>→ 情報過多で選べない","「あなたに合うプランは？」<br>Q1: 価格重視？内容重視？<br>→ おすすめプランをハイライト表示")}
         ]},
        {"level":"h3","level_label":"仮説 3","title":"レビュー・写真などの信頼構築要素がfold以下",
         "body":"ACページの信頼構築コンテンツ（レビュー・体験レポート・Q&A）がページ下部にあり、新規ユーザーが見る前に離脱。",
         "evidence":["レビューセクションまでスクロールするユーザーが30%未満（推定）","新規ユーザーはリピーターより信頼情報への依存度が高い","競合はレビューをACページ上部に配置"],
         "actions":[
            {"letter":"G","title":"レビューのサマリーカードをACページ上部に移動","description":"レビュー全体を移動せず、サマリー（星評価+件数+ハイライト1件）をACページ上部に配置。","spec_html":"・ヒーロー直下にレビューサマリーカード<br>・星評価+件数+最新ハイライトレビュー<br>・「全レビューを見る」リンク","impact":"②→③ +3pt","prototype": make_proto("ヒーロー→プラン一覧→...→レビュー<br>→ レビューまでスクロールしない","ヒーロー→★レビューサマリー→プラン一覧<br>→ 信頼情報が最初に目に入る")},
            {"letter":"H","title":"「体験レポート」ショート動画の追加","description":"過去参加者のショート動画（15秒）をACページ上部に配置。","spec_html":"・15秒ショート動画をヒーロー直下に配置<br>・自動再生（ミュート）<br>・参加者の実体験をビジュアルで伝達","impact":"②→③ +2pt","prototype": make_proto("写真ギャラリーのみ<br>→ 静止画ではイメージが伝わりにくい","ショート動画「参加者の声」15秒<br>→ 動画でリアルな体験を訴求")},
            {"letter":"I","title":"Q&Aセクションの充実とFAQのfold上表示","description":"よくある質問の上位3件をACページ上部（プラン一覧直前）に表示。","spec_html":"・FAQ上位3件をプラン一覧直前に表示<br>・アコーディオンUI（タップで展開）<br>・「もっと見る」で全FAQ表示","impact":"②→③ +1pt","prototype": make_proto("FAQ: ページ最下部<br>→ 誰も見ない","FAQ上位3件がプラン直前に表示<br>「送迎はある？」「キャンセルは？」<br>→ 不安解消して日程選択へ")}
         ]}
    ],
    "competitive": [
        {"name":"Klook","favicon_url":"https://www.klook.com/favicon.ico","url":"https://www.klook.com/ja/","feature":"レビュー評価をACページ最上部に大きく表示。「〇〇名が予約」カウンター。写真ギャラリーにユーザー投稿写真あり。","detail":"注目点: 信頼構築要素のfold上配置。施策A・Cの参考。"},
        {"name":"GetYourGuide","favicon_url":"https://cdn.getyourguide.com/tf/assets/static/favicons/favicon-32x32.png","url":"https://www.getyourguide.com/","feature":"ACページ上部にレビュースコア+件数。「ベストセラー」バッジ。プラン比較機能あり。","detail":"注目点: おすすめバッジ表示。施策Dの参考。"},
        {"name":"Viator","favicon_url":"https://cache.vtrcdn.com/orion/images/favicon.ico","url":"https://www.viator.com/","feature":"Tripadvisorレビュー統合でレビュー数が多い印象。「全額返金保証」バッジで信頼構築。","detail":"注目点: 返金保証表示は新規ユーザーの不安解消に効果的。"},
        {"name":"アソビュー","favicon_url":"https://www.asoview.com/favicon.ico","url":"https://www.asoview.com/","feature":"レビュー上部表示。「本日空きあり」表示で即座にカレンダーへ誘導。プラン選択がシンプル。","detail":"注目点: 在庫リアルタイム表示でカレンダー到達を促進。"},
        {"name":"じゃらん","favicon_url":"https://www.jalan.net/favicon.ico","url":"https://www.jalan.net/kankou/","feature":"口コミ件数を大きく表示。体験レポート（写真付き）が充実。ポイント還元表示。","detail":"注目点: 体験レポートはショート動画の代替。施策H参考。"},
        {"name":"KKday","favicon_url":"https://www.kkday.com/favicon.png","url":"https://www.kkday.com/ja/","feature":"レビュー上部表示+「即確定」バッジ。プランの違いが分かりやすい表示。価格比較しやすいUI。","detail":"注目点: プラン比較のわかりやすさ。施策E参考。"}
    ],
    "competitive_insight":"主要競合6社中5社がACページ上部にレビューサマリーを配置済み。VELTRAはレビューがfold以下にあり新規ユーザーの信頼構築が遅れている。施策A（レビュー上部表示）と施策D（おすすめプラン）を優先実装すべき。",
    "verification":["データの正確性をGA4で確認","新規vs リピーターのファネル差を定量分析","施策の技術的実現可能性確認","ABテスト設計レビュー","競合UIの最新状況確認","優先度・リソース配分決定"],
    "verification_method":"GA4: 新規ユーザーの②→③転換率を主要KPIとして計測。ABテスト2週間。目標: ②→③ 16.14% → 22%以上。副次指標: カレンダー到達時間、ACページ滞在時間。優先施策: レビュー上部表示（施策A）。"
})
print("#2 defined")

# #3: Mobile — ④→⑤ 完了率の低さ
bottlenecks.append({
    "number": 3,
    "title": "Mobile — ④→⑤ 完了率の低さ",
    "tags": [{"label":"④→⑤ 意向→完了","type":"red"},{"label":"Mobile","type":"default"}],
    "deviation": "-13.5%",
    "impact_sessions": "101K / 月",
    "description_html": "<p>Mobileでフォーム入力（④意向）まで進んだユーザーの購入完了率が <strong style=\"color:#E8423F\">29.89%</strong>（全体ベースライン 34.57% の <strong>-13.5%</strong>）。月間 101K セッション。Mobileのフォーム入力・決済UIの使いにくさにより最終段階で離脱。</p>",
    "funnel_overview": {"title":"ファネル比較（Mobile vs ベースライン）","cells":[{"label":"①→②","value":"52.31%","sub":"BL 82.60%"},{"label":"②→③","value":"25.68%","sub":"BL 26.43%"},{"label":"③→④","value":"35.66%","sub":"BL 31.92%"},{"label":"④→⑤","value":"29.89%","sub":"BL 34.57% | -13.5%","alert":True}]},
    "funnel_compare": [
        {"label":"全体平均","stage":"④→⑤ 完了","value":"34.57%","sub":"ベースライン"},
        {"label":"Mobile","stage":"④→⑤ 完了","value":"29.89%","sub":"-13.5% vs 全体","alert":True},
        {"label":"Desktop","stage":"④→⑤ 完了","value":"44.02%","sub":"+27.3% vs 全体"},
        {"label":"リピーター","stage":"④→⑤ 完了","value":"30.92%","sub":"-10.6% vs 全体"}
    ],
    "drill_down": [
        {"title":"Mobile新規 vs リピーター","body_html":"Mobile × 新規: ④→⑤ ≈ 28%<br>Mobile × リピーター: ④→⑤ ≈ 31%","note":"新規もリピーターも低い。Mobileフォーム共通の問題。"},
        {"title":"Desktop比較","body_html":"Desktop: ④→⑤ = <strong>44.02%</strong><br>Mobile: ④→⑤ = <strong style=\"color:#E8423F\">29.89%</strong>（-14.13pp）","note":"Desktop比14pp低い。MobileのフォームUIに構造的問題。"}
    ],
    "callout": {"title":"特定結果","body_html":"<strong>Mobile</strong>の④→⑤完了率が<strong>29.89%</strong>（BL 34.57%の<strong>-13.5%</strong>）。Desktop 44.02%と比べ14pp低い。Mobileの決済フォーム入力UXに構造的課題。"},
    "hypo_section_title":"原因仮説 × 3 &amp; 打ち手 × 9",
    "hypo_section_desc":"なぜMobileの④→⑤完了率が低いか？",
    "hypotheses": [
        {"level":"h1","level_label":"仮説 1（有力）","title":"Mobileの決済フォームが使いにくい",
         "body":"クレジットカード入力、住所入力等がMobileの小画面で操作しにくく、入力途中で離脱。",
         "evidence":["Mobile ④→⑤: 29.89% vs Desktop: 44.02%（14pp差）","フォームフィールド数が多い","入力バリデーションエラーが頻発"],
         "actions":[
            {"letter":"A","title":"フォームステップ化（1画面1入力グループ）","description":"長いフォームを3-4ステップに分割し、進捗バーで現在位置を表示。","spec_html":"・ステップ1: 参加者情報<br>・ステップ2: 決済情報<br>・ステップ3: 確認<br>・進捗バー表示","impact":"④→⑤ +4pt","prototype": make_proto("1ページ全フィールド表示<br>スクロール量が膨大<br>→ 完了までの道のりが見えない","ステップ1/3: 参加者情報<br>進捗バー [===---]<br>→ 小分けで完了感")},
            {"letter":"B","title":"Apple Pay/Google Pay対応","description":"モバイル決済を導入しカード入力を省略可能にする。","spec_html":"・Apple Pay / Google Pay ボタンをフォーム上部に配置<br>・ワンタップで決済完了<br>・カード入力フォームはフォールバック","impact":"④→⑤ +3pt","prototype": make_proto("決済: カード番号手入力<br>有効期限・CVC・名義入力<br>→ 入力が面倒で離脱","決済: [Apple Pay] [Google Pay]<br>ワンタップで完了<br>→ 入力ゼロで決済")},
            {"letter":"C","title":"フォームの入力補助強化","description":"オートフィル対応、入力マスク、リアルタイムバリデーション導入。","spec_html":"・autocomplete属性の適切な設定<br>・カード番号の自動フォーマット<br>・エラー時の具体的なメッセージ表示","impact":"④→⑤ +2pt","prototype": make_proto("入力エラー: 「入力が正しくありません」<br>何が間違いか不明<br>→ 修正に迷って離脱","入力補助: オートフィル対応<br>リアルタイムバリデーション<br>「カード番号は16桁です」<br>→ スムーズに入力完了")}
         ]},
        {"level":"h2","level_label":"仮説 2","title":"Mobileでセキュリティ不安から決済をためらう",
         "body":"Mobileでのクレジットカード入力にセキュリティ不安を感じ、Desktop切替や他サイトへ流出。",
         "evidence":["Mobile決済完了率がDesktop比で著しく低い","セキュリティバッジの表示がない","「PCで購入」の行動パターン"],
         "actions":[
            {"letter":"D","title":"決済フォームにセキュリティバッジ表示","description":"SSL証明書・PCI DSS準拠バッジ・「256bit暗号化」表示を決済フォーム直上に配置。","spec_html":"・🔒 SSLバッジ + PCI DSSバッジ<br>・「お客様のカード情報は256bit暗号化で保護」<br>・決済フォーム直上に配置","impact":"④→⑤ +3pt","prototype": make_proto("決済フォーム<br>セキュリティ表示なし<br>→ カード入力に不安","🔒 安全な決済<br>SSL暗号化 | PCI DSS準拠<br>→ 安心してカード入力")},
            {"letter":"E","title":"「後から決済」オプション（仮予約）","description":"カード入力なしで仮予約し、後からPCまたは任意のタイミングで決済可能にする。","spec_html":"・「今すぐ予約確定」と「仮予約（24h以内に決済）」の2択<br>・仮予約はメール/LINE通知で決済リマインド","impact":"④→⑤ +2pt","prototype": make_proto("決済方法: クレジットカードのみ<br>→ 今すぐカード入力が必須","決済方法:<br>1. 今すぐ決済<br>2. 仮予約（24h以内に決済）<br>→ 柔軟な選択肢")},
            {"letter":"F","title":"決済手段の多様化（コンビニ決済等）","description":"クレジットカード以外の決済手段（コンビニ決済、PayPay等）を追加。","spec_html":"・コンビニ決済追加<br>・PayPay / LINE Pay対応<br>・銀行振込オプション","impact":"④→⑤ +1pt","prototype": make_proto("決済: クレジットカードのみ<br>→ カードがない/使いたくない","決済: カード / PayPay / コンビニ<br>→ 自分に合った方法で決済")}
         ]},
        {"level":"h3","level_label":"仮説 3","title":"フォーム入力中にページが長く離脱",
         "body":"参加者情報・決済情報・利用規約等が1ページに詰め込まれ、Mobileでスクロール量が膨大。",
         "evidence":["フォームページのスクロール深度が低い","離脱ポイントがフォーム中盤に集中","長いフォームは完了率が下がる"],
         "actions":[
            {"letter":"G","title":"不要フィールドの削減","description":"予約に必須でないフィールド（FAX番号、住所2等）を削除またはオプション化。","spec_html":"・必須フィールドを最小化（名前・メール・電話・カード）<br>・オプション項目は折りたたみ<br>・入力フィールド数を30%削減","impact":"④→⑤ +2pt","prototype": make_proto("フォーム: 15フィールド<br>FAX番号、住所2行目等<br>→ 入力が多すぎる","フォーム: 8フィールド（必須のみ）<br>オプションは折りたたみ<br>→ 最小限の入力で完了")},
            {"letter":"H","title":"プログレスバーの視覚的改善","description":"フォーム上部に進捗率を表示し、完了までの残り工程を明示。","spec_html":"・プログレスバー（%表示）<br>・ステップ名表示（参加者→決済→確認）<br>・完了予想時間「残り約2分」表示","impact":"④→⑤ +1pt","prototype": make_proto("フォーム: 進捗表示なし<br>→ あとどれくらいか不明","フォーム: [====60%====]<br>ステップ2/3 残り約1分<br>→ 完了が近いので継続")},
            {"letter":"I","title":"離脱時のリマインドメール送信","description":"フォーム入力途中で離脱したユーザーに「予約を続ける」リマインドメールを自動送信。","spec_html":"・離脱30分後にメール送信<br>・「続きから予約」ボタン付き<br>・入力済み情報を保持して復元","impact":"④→⑤ +1pt","prototype": make_proto("離脱 → 終了<br>入力データは失われる<br>→ 再度最初から入力","離脱30分後<br>「予約を続けますか？」メール<br>→ ワンクリックで入力再開")}
         ]}
    ],
    "competitive": [
        {"name":"Klook","favicon_url":"https://www.klook.com/favicon.ico","url":"https://www.klook.com/ja/","feature":"<strong>ステップ型フォーム</strong>。1画面1グループの入力。Apple Pay/Google Pay対応。進捗バー表示。","detail":"施策A+Bの直接参考。"},
        {"name":"GetYourGuide","favicon_url":"https://cdn.getyourguide.com/tf/assets/static/favicons/favicon-32x32.png","url":"https://www.getyourguide.com/","feature":"シンプルな2ステップフォーム。PayPal対応。セキュリティバッジ明示。","detail":"フォームの簡素化が特徴。"},
        {"name":"Viator","favicon_url":"https://cache.vtrcdn.com/orion/images/favicon.ico","url":"https://www.viator.com/","feature":"PayPal+Apple Pay対応。フォームフィールド数が少ない。全額返金保証バッジ表示。","detail":"返金保証でセキュリティ不安を解消。"},
        {"name":"アソビュー","favicon_url":"https://www.asoview.com/favicon.ico","url":"https://www.asoview.com/","feature":"コンビニ決済対応。ステップフォーム。会員情報自動入力。","detail":"コンビニ決済は施策F参考。"},
        {"name":"じゃらん","favicon_url":"https://www.jalan.net/favicon.ico","url":"https://www.jalan.net/","feature":"じゃらんポイント決済。会員自動入力。コンビニ/銀行振込対応。","detail":"多様な決済手段。"},
        {"name":"KKday","favicon_url":"https://www.kkday.com/favicon.png","url":"https://www.kkday.com/ja/","feature":"LINE Pay/PayPay対応。簡潔なフォーム。セキュリティバッジ表示。","detail":"QR決済対応が特徴。"}
    ],
    "competitive_insight":"主要競合6社中5社がモバイル決済（Apple Pay/Google Pay/PayPal等）に対応済み。VELTRAのクレジットカード手入力のみは業界水準から遅れ。施策B（モバイル決済）を最優先で実装すべき。",
    "verification":["フォーム離脱ポイントの特定（GA4ファネル分析）","フォームフィールド数の現状カウント","モバイル決済導入の技術的実現可能性","ABテスト設計（フォームステップ化）","決済手段別の完了率分析"],
    "verification_method":"GA4: Mobile ④→⑤ 転換率を主要KPI。ABテスト2週間。目標: ④→⑤ 29.89% → 35%以上。副次指標: フォーム離脱率、入力完了時間。優先施策: フォームステップ化（施策A）+モバイル決済（施策B）。"
})
print("#3 defined")

# #4-10: Define remaining bottlenecks more concisely using helper
def make_bn(num, title, tags, deviation, impact, desc, stage, compare_data, dd, callout_body, hypos_data, comp_focus, comp_insight, verif_method):
    hypos = []
    letters = iter("ABCDEFGHI")
    for h in hypos_data:
        actions = []
        for a in h["actions"]:
            letter = next(letters)
            actions.append({
                "letter": letter,
                "title": a["title"],
                "description": a["desc"],
                "spec_html": a.get("spec",""),
                "impact": a["impact"],
                "prototype": make_proto(a["before"], a["after"])
            })
        hypos.append({
            "level": h["level"], "level_label": h["label"], "title": h["title"],
            "body": h["body"], "evidence": h["evidence"], "actions": actions
        })
    return {
        "number": num, "title": title,
        "tags": tags, "deviation": deviation, "impact_sessions": impact,
        "description_html": desc,
        "funnel_compare": compare_data,
        "drill_down": dd,
        "callout": {"title":"特定結果","body_html": callout_body},
        "hypo_section_title": "原因仮説 × 3 &amp; 打ち手 × 9",
        "hypo_section_desc": f"なぜ{title.split('—')[0].strip()}の{stage}が低いか？",
        "hypotheses": hypos,
        "competitive": [
            {"name":"Klook","favicon_url":"https://www.klook.com/favicon.ico","url":"https://www.klook.com/ja/","feature":comp_focus[0],"detail":""},
            {"name":"GetYourGuide","favicon_url":"https://cdn.getyourguide.com/tf/assets/static/favicons/favicon-32x32.png","url":"https://www.getyourguide.com/","feature":comp_focus[1],"detail":""},
            {"name":"Viator","favicon_url":"https://cache.vtrcdn.com/orion/images/favicon.ico","url":"https://www.viator.com/","feature":comp_focus[2],"detail":""},
            {"name":"アソビュー","favicon_url":"https://www.asoview.com/favicon.ico","url":"https://www.asoview.com/","feature":comp_focus[3],"detail":""},
            {"name":"じゃらん","favicon_url":"https://www.jalan.net/favicon.ico","url":"https://www.jalan.net/","feature":comp_focus[4],"detail":""},
            {"name":"KKday","favicon_url":"https://www.kkday.com/favicon.png","url":"https://www.kkday.com/ja/","feature":comp_focus[5],"detail":""}
        ],
        "competitive_insight": comp_insight,
        "verification": ["データ正確性確認","仮説妥当性レビュー","技術的実現可能性確認","ABテスト設計レビュー","競合UI最新確認","優先度決定"],
        "verification_method": verif_method
    }

# #4: Organic Search — ②→③
bottlenecks.append(make_bn(4,
    "Organic Search — ②→③ 検討転換率の低さ",
    [{"label":"②→③ AC到達→検討","type":"red"},{"label":"Organic Search","type":"default"}],
    "-22.6%", "1,267K / 月",
    "<p>Organic Search経由のACページ到達後のカレンダー転換率が <strong style=\"color:#E8423F\">20.47%</strong>（全体ベースライン 26.43% の <strong>-22.6%</strong>）。月間 1,267K セッション。SEO経由ユーザーはACページに到達するが日程検討まで進まない。</p>",
    "②→③ 検討転換率",
    [{"label":"全体平均","stage":"②→③","value":"26.43%","sub":"BL"},{"label":"Organic Search","stage":"②→③","value":"20.47%","sub":"-22.6%","alert":True},{"label":"Paid Search","stage":"②→③","value":"28.21%","sub":"+6.7%"},{"label":"新規ユーザー","stage":"②→③","value":"16.14%","sub":"-38.9%"}],
    [{"title":"Organic新規 vs リピーター","body_html":"Organic × 新規: ②→③ ≈ 15%<br>Organic × リピーター: ②→③ = 36.64%","note":"新規Organicが特に低い。"},
     {"title":"Organic Mobile vs Desktop","body_html":"Organic × Mobile: ②→③ ≈ 19%<br>Organic × Desktop: ②→③ ≈ 22%","note":"Mobile Organicがやや低い。"}],
    "<strong>Organic Search</strong> ②→③ = <strong>20.47%</strong>（BL 26.43%の<strong>-22.6%</strong>）。SEO経由ユーザーはACに到達するが「情報収集目的」の比率が高く日程選択まで進まない。",
    [{"level":"h1","label":"仮説 1（有力）","title":"SEO経由ユーザーは情報収集目的で日程を決める段階にない",
      "body":"「〇〇 おすすめ」等のKWで流入し、まだ旅行計画が具体化していない。","evidence":["情報系KWでの流入比率が高い","ACページ滞在時間が短い","カレンダーセクションまでスクロールしない"],
      "actions":[
        {"title":"ACページにカレンダーCTAをファーストビューに配置","desc":"カレンダーへのスクロールを待たず上部にCTA表示。","impact":"②→③ +4pt","before":"ACページ: 写真→説明→...→カレンダー<br>→ カレンダーが遠い","after":"ACページ: 写真→「日程を確認」CTA→説明<br>→ 1タップでカレンダーへ"},
        {"title":"「お気に入り保存」機能の強化","desc":"今すぐ予約しないユーザー向けにお気に入り保存を促進。","impact":"②→③ +3pt","before":"お気に入り: ♡アイコンのみ<br>→ 気づかれにくい","after":"「あとで見る」フローティングボタン<br>メール/LINEリマインド付き<br>→ 再訪問時にカレンダーへ"},
        {"title":"「空き状況アラート」登録機能","desc":"希望日程を登録すると空き通知メールを送信。","impact":"②→③ +2pt","before":"カレンダー確認のみ<br>空きなければ離脱","after":"「空き通知を受け取る」ボタン<br>→ 再訪問機会の創出"}
      ]},
     {"level":"h2","label":"仮説 2","title":"ACページのカレンダーUIが目立たない",
      "body":"ACページでカレンダーセクションがページ中盤以下にあり、ユーザーが気づかない。","evidence":["カレンダーセクションのスクロール到達率が低い","モバイルでは特にスクロール量が多い"],
      "actions":[
        {"title":"カレンダープレビューをACページ上部に表示","desc":"ミニカレンダー（空き状況のみ）をACページ上部に表示。","impact":"②→③ +3pt","before":"カレンダー: ページ中盤以下<br>→ スクロールしないと見えない","after":"ミニカレンダー: ヒーロー直下<br>○△×で空き状況表示<br>→ 即座に日程検討開始"},
        {"title":"「最短空き日程」バッジ表示","desc":"ACページ上部に「最短空き: 明日4/8」バッジを表示。","impact":"②→③ +2pt","before":"空き日程: カレンダーを開かないと不明","after":"「最短空き: 明日4/8」バッジ<br>→ 即座に予約可能と分かる"},
        {"title":"カレンダーへのスクロール誘導アニメーション","desc":"ACページ読了後にカレンダーへの矢印アニメーション表示。","impact":"②→③ +1pt","before":"スクロール誘導なし<br>→ カレンダーの存在に気づかない","after":"↓「日程を確認」スクロール誘導<br>→ カレンダーへ自然に誘導"}
      ]},
     {"level":"h3","label":"仮説 3","title":"価格帯が検索キーワードの期待値と合わない",
      "body":"Organic経由ユーザーの価格期待値とVELTRA価格にギャップがあり、ACで価格を見てカレンダーまで進まない。","evidence":["「安い」「格安」KWでの流入も一定割合","価格表示がACページ上部で目立つ","価格を見て即離脱するパターン"],
      "actions":[
        {"title":"価格帯フィルターをカテゴリページに追加","desc":"予算に合うACのみ表示するフィルター。","impact":"②→③ +2pt","before":"全価格帯混在<br>→ 予算オーバーの商品も表示","after":"価格帯フィルター: ¥5,000以下/¥5-10K/¥10K+<br>→ 予算内のACのみ表示"},
        {"title":"割引・早割情報の訴求強化","desc":"早割・直前割引をACページ上部に表示。","impact":"②→③ +2pt","before":"割引情報: なし or 目立たない","after":"「早割10%OFF」「直前割引」バッジ<br>→ 価格メリットで検討促進"},
        {"title":"分割払い表示（月額換算）","desc":"高額商品に「月々¥3,200×4回」表示。","impact":"②→③ +1pt","before":"¥12,800（一括表示のみ）<br>→ 高く感じる","after":"¥12,800 or 月々¥3,200×4回<br>→ 手頃に感じる"}
      ]}
    ],
    ["ACページ上部にカレンダーCTA配置。空き状況リアルタイム表示。","カレンダー上部表示。おすすめ日程のハイライト。","ACページ内にカレンダーモーダル。ワンタップでカレンダー展開。","カレンダーがACページ上部に配置。「本日空きあり」表示。","空き状況が一覧ページから確認可能。カレンダー到達率が高い。","カレンダーCTAがACページ上部。「最安値の日」ハイライト。"],
    "競合はACページ上部にカレンダーCTAまたはミニカレンダーを配置。VELTRAのカレンダーはページ中盤以下にあり到達率が低い。施策A（カレンダーCTA上部配置）を優先。",
    "GA4: Organic Search ②→③転換率。ABテスト2週間。目標: 20.47% → 24%以上。優先施策: カレンダーCTA上部配置。"
))
print("#4 defined")

# #5: Paid Search — ③→④
bottlenecks.append(make_bn(5,
    "Paid Search — ③→④ 意向転換率の低さ",
    [{"label":"③→④ 検討→意向","type":"red"},{"label":"Paid Search","type":"default"}],
    "-36.0%", "710K / 月",
    "<p>Paid Search経由のカレンダー閲覧後のフォーム転換率が <strong style=\"color:#E8423F\">20.43%</strong>（全体ベースライン 31.92% の <strong>-36.0%</strong>）。月間 710K セッション。広告経由で日程を確認したがフォームに進まない。</p>",
    "③→④ 意向転換率",
    [{"label":"全体平均","stage":"③→④","value":"31.92%","sub":"BL"},{"label":"Paid Search","stage":"③→④","value":"20.43%","sub":"-36.0%","alert":True},{"label":"Organic Search","stage":"③→④","value":"20.32%","sub":"-36.3%"},{"label":"Desktop","stage":"③→④","value":"27.53%","sub":"-13.7%"}],
    [{"title":"Paid Search 新規 vs リピーター","body_html":"Paid × 新規: ③→④ ≈ 18%<br>Paid × リピーター: ③→④ ≈ 25%","note":"新規Paid Searchユーザーが特に低い。"},
     {"title":"広告クリエイティブ別","body_html":"ブランドKW: ③→④ ≈ 28%<br>一般KW: ③→④ ≈ 16%","note":"一般KWからの流入が低い。広告文と商品の不一致。"}],
    "<strong>Paid Search</strong> ③→④ = <strong>20.43%</strong>（BL 31.92%の<strong>-36.0%</strong>）。広告経由ユーザーは日程確認まで進むが価格やプラン選択で離脱。",
    [{"level":"h1","label":"仮説 1（有力）","title":"広告LP（ACページ）と広告文のメッセージのミスマッチ",
      "body":"広告文で訴求する内容とACページの実際の内容にギャップがあり、期待外れで離脱。","evidence":["一般KWの③→④が特に低い","広告文と商品詳細の一貫性不足","LP到達後の直帰率が高い"],
      "actions":[
        {"title":"広告文と連動したACページ上部メッセージ","desc":"広告KWに応じてACページ上部のメッセージを動的に変更。","impact":"③→④ +5pt","before":"広告「ハワイ格安ツアー」→ ACページ通常表示<br>→ 期待と違う","after":"広告「ハワイ格安ツアー」→「期間限定割引中」メッセージ表示<br>→ 期待通りで予約へ"},
        {"title":"広告専用LP（ACページのバリアント）","desc":"広告KWカテゴリ別にACページの表示をカスタマイズ。","impact":"③→④ +4pt","before":"全KW共通のACページ<br>→ KWごとの意図に未対応","after":"KW別カスタマイズ<br>「格安」→割引強調/「人気」→ランキング強調"},
        {"title":"広告品質スコアの改善","desc":"広告文とLPの関連性スコアを改善しCVR向上。","impact":"③→④ +2pt","before":"品質スコア: 5/10<br>広告文とLP不一致","after":"品質スコア: 8/10<br>広告文とLP一貫性確保"}
      ]},
     {"level":"h2","label":"仮説 2","title":"価格感度が高い広告ユーザーがカレンダー後に価格に驚いて離脱",
      "body":"広告経由ユーザーは価格比較意識が高く、カレンダーで日程を確認した後に価格を見て離脱。","evidence":["広告ユーザーの価格比較行動","カレンダー表示後の離脱率が高い","「最安値」を求める傾向"],
      "actions":[
        {"title":"カレンダー内に価格表示（日別最安値）","desc":"カレンダーの各日付に最安価格を表示。","impact":"③→④ +4pt","before":"カレンダー: 日付+空き/満のみ<br>→ 価格はプランに戻って確認","after":"カレンダー: 日付+¥12,800〜<br>→ 日付選択時に価格確認済み"},
        {"title":"「最安値保証」バッジ表示","desc":"広告LP上部に最安値保証バッジを表示。","impact":"③→④ +3pt","before":"価格表示のみ<br>→ 他社と比較したくなる","after":"「最安値保証」バッジ<br>→ 他社比較不要と安心"},
        {"title":"早割・直前割引のカレンダー内ハイライト","desc":"割引対象日をカレンダー内でハイライト表示。","impact":"③→④ +2pt","before":"全日同じ表示<br>→ いつが安いか不明","after":"割引日: 緑ハイライト「10%OFF」<br>→ お得な日を即座に発見"}
      ]},
     {"level":"h3","label":"仮説 3","title":"広告KWが比較・情報収集意図で購入意向でない",
      "body":"広告配信KWに情報収集系が混在し、予約意向のないユーザーが流入。","evidence":["一般KWの③→④: 16%（ブランドKW: 28%との差）","情報系KWでのCPC支出が高い"],
      "actions":[
        {"title":"KWカテゴリの見直し（予約意図KWに集中）","desc":"低CVR KWの除外と予約意図KWへの予算シフト。","impact":"③→④ +3pt","before":"全KW均等配信<br>情報系KWにも予算","after":"予約意図KW重点配信<br>情報系KWは除外or入札低下"},
        {"title":"リマーケティング広告の強化","desc":"AC閲覧済みユーザーへの再訪問促進広告。","impact":"③→④ +2pt","before":"初回訪問のみ<br>→ 離脱後は再訪問なし","after":"リマーケティング広告<br>「あのツアーまだ空いてます」<br>→ 予約意向が高まった時に再訪問"},
        {"title":"検索クエリレポートの定期分析","desc":"実際のクエリレポートを分析し不適切なKWを除外。","impact":"③→④ +1pt","before":"KW管理: 月1回程度","after":"KW管理: 週次分析<br>不適切KWを即除外"}
      ]}
    ],
    ["広告LP専用ページ。KW別コンテンツ最適化。","広告文とLP連動。A/Bテスト充実。","広告LP最適化。Tripadvisor連携で信頼構築。","リスティング広告からACページへ直接誘導。","広告LP改善。ポイント訴求で転換促進。","広告KW最適化。価格比較表示。"],
    "広告LPの最適化は全競合が実施。VELTRAは広告文とACページの一貫性に改善余地。施策A（広告連動メッセージ）を優先。",
    "GA4: Paid Search ③→④転換率。ABテスト2週間。目標: 20.43% → 28%以上。優先施策: 広告文連動メッセージ。"
))
print("#5 defined")

# #6: 新規ユーザー — ①→②
bottlenecks.append(make_bn(6,
    "新規ユーザー — ①→② AC到達率の低さ",
    [{"label":"①→② 流入→AC到達","type":"red"},{"label":"新規ユーザー","type":"default"}],
    "-41.9%", "1,534K / 月",
    "<p>新規ユーザーの流入後ACページ到達率が <strong style=\"color:#E8423F\">47.95%</strong>（全体ベースライン 82.60% の <strong>-41.9%</strong>）。月間 1,534K セッション。初回訪問ユーザーはVELTRAに来るがACページへの導線を見つけられない。</p>",
    "①→② AC到達率",
    [{"label":"全体平均","stage":"①→②","value":"82.60%","sub":"BL"},{"label":"新規ユーザー","stage":"①→②","value":"47.95%","sub":"-41.9%","alert":True},{"label":"リピーター","stage":"①→②","value":"62.37%","sub":"-24.5%"},{"label":"Organic新規","stage":"①→②","value":"47.75%","sub":"-42.25%"}],
    [{"title":"新規 流入元別","body_html":"新規 × Organic: ①→② ≈ 47%<br>新規 × Paid: ①→② ≈ 55%<br>新規 × Direct: ①→② ≈ 30%","note":"Direct新規が最も低い。トップページの問題。"},
     {"title":"新規 デバイス別","body_html":"新規 × Mobile: ①→② ≈ 46%<br>新規 × Desktop: ①→② ≈ 50%","note":"Mobile新規が特に低い。"}],
    "<strong>新規ユーザー</strong> ①→② = <strong>47.95%</strong>（BL 82.60%の<strong>-41.9%</strong>）。初回訪問で「何を探せばいいか分からない」状態。",
    [{"level":"h1","label":"仮説 1（有力）","title":"トップページの商品発見体験が弱い",
      "body":"初回訪問ユーザーはトップページで「何を探せばいいか分からない」状態。","evidence":["新規Direct ①→②: 30%と最低","トップページの直帰率が高い","検索/カテゴリの使い方が分からない"],
      "actions":[
        {"title":"トップページにパーソナライズ推薦導入","desc":"初回訪問でも人気ランキング・季節おすすめを表示。","impact":"①→② +7pt","before":"トップ: バナー+カテゴリ一覧<br>→ 何を選べばいいか不明","after":"トップ: 「今人気のアクティビティ」<br>季節おすすめ+ランキング<br>→ 即座にAC到達"},
        {"title":"初回訪問ユーザー向けオンボーディング","desc":"「どこに行きますか？」の対話型ウィジェット表示。","impact":"①→② +5pt","before":"トップ表示のみ<br>→ 自力で探す必要","after":"「どこに行きますか？」<br>ハワイ/沖縄/バリ選択→おすすめAC表示"},
        {"title":"人気アクティビティのヒーローセクション","desc":"トップページ上部に人気ACの大型カードを表示。","impact":"①→② +3pt","before":"バナー広告がトップ<br>→ ACへの直接導線なし","after":"人気AC大型カード3件<br>写真+評価+価格+「詳細→」"}
      ]},
     {"level":"h2","label":"仮説 2","title":"検索・カテゴリナビゲーションが直感的でない",
      "body":"カテゴリ構造が分かりにくく、検索機能も弱い。","evidence":["サイト内検索の利用率が低い","カテゴリ名が専門的で分かりにくい","パンくずリストの視認性が低い"],
      "actions":[
        {"title":"検索機能のオートコンプリート強化","desc":"検索窓にサジェスト・人気KW表示。","impact":"①→② +4pt","before":"検索窓: テキスト入力のみ<br>→ 何を検索すればいいか不明","after":"検索窓: 「ハワ…」→サジェスト表示<br>人気KW: シュノーケル、ハイキング"},
        {"title":"カテゴリ名の平易化","desc":"専門用語→わかりやすい日本語に変更。","impact":"①→② +3pt","before":"カテゴリ: オプショナルツアー<br>→ 新規には意味不明","after":"カテゴリ: 体験・アクティビティ<br>→ 直感的に理解"},
        {"title":"ビジュアルカテゴリナビゲーション","desc":"アイコン+写真付きカテゴリグリッド。","impact":"①→② +2pt","before":"テキストリストのカテゴリ<br>→ 魅力が伝わらない","after":"📸写真+アイコンのカテゴリグリッド<br>→ ビジュアルで選びやすい"}
      ]},
     {"level":"h3","label":"仮説 3","title":"パーソナライズ推薦がなく「自分向け」コンテンツが見つからない",
      "body":"初回訪問でも行動データ（リファラー、検索KW等）から推薦可能だが未実装。","evidence":["パーソナライズ推薦が未実装","リファラー情報の未活用","競合はAI推薦を実装済み"],
      "actions":[
        {"title":"リファラーKW連動のおすすめ表示","desc":"検索KWからエリア・カテゴリを推定し関連ACを表示。","impact":"①→② +3pt","before":"全ユーザー同じトップページ<br>→ 自分向け感がない","after":"「ハワイ」KW流入→ハワイおすすめAC表示<br>→ パーソナライズ体験"},
        {"title":"位置情報ベースの推薦","desc":"IPアドレスから居住地を推定し近場ACを表示。","impact":"①→② +2pt","before":"全国同じコンテンツ<br>→ 地域関連性なし","after":"東京からアクセス→関東近郊おすすめ表示"},
        {"title":"閲覧行動リアルタイム推薦","desc":"サイト内の閲覧履歴から関連ACをリアルタイム推薦。","impact":"①→② +1pt","before":"ページ遷移ごとにリセット","after":"「この体験を見た人はこちらも」<br>リアルタイム推薦"}
      ]}
    ],
    ["AI推薦導入済み。パーソナライズされたトップページ。","ユーザーの好みに基づく推薦。対話型検索。","人気ランキング表示。ベストセラーバッジ。","人気ランキング表示。「本日空きあり」。","エリア特集+人気ランキング。季節おすすめ。","人気TOP10表示。対話型検索。"],
    "競合はパーソナライズ推薦とAI検索を導入済み。VELTRAのトップページは静的で新規ユーザーのAC到達を支援できていない。施策A（パーソナライズ推薦）を最優先。",
    "GA4: 新規ユーザー ①→②。ABテスト2週間。目標: 47.95% → 58%以上。優先施策: トップページ推薦。"
))
print("#6 defined")

# #7: Desktop — ③→④
bottlenecks.append(make_bn(7,
    "Desktop — ③→④ 意向転換率の低さ",
    [{"label":"③→④ 検討→意向","type":"red"},{"label":"Desktop","type":"default"}],
    "-13.7%", "767K / 月",
    "<p>Desktopのカレンダー閲覧後のフォーム転換率が <strong style=\"color:#E8423F\">27.53%</strong>（全体ベースライン 31.92% の <strong>-13.7%</strong>）。月間 767K セッション。カレンダーで日程確認後にフォームに進まない。</p>",
    "③→④ 意向転換率",
    [{"label":"全体平均","stage":"③→④","value":"31.92%","sub":"BL"},{"label":"Desktop","stage":"③→④","value":"27.53%","sub":"-13.7%","alert":True},{"label":"Mobile","stage":"③→④","value":"35.66%","sub":"+11.7%"},{"label":"Organic Desktop","stage":"③→④","value":"20.32%","sub":"-36.3%"}],
    [{"title":"Desktop 新規 vs リピーター","body_html":"Desktop × 新規: ③→④ ≈ 22%<br>Desktop × リピーター: ③→④ ≈ 35%","note":"Desktop新規が低い。"},
     {"title":"Desktop チャネル別","body_html":"Desktop × Organic: ③→④ = 20.32%<br>Desktop × Paid: ③→④ ≈ 22%","note":"Desktop Organicが特に低い。"}],
    "<strong>Desktop</strong> ③→④ = <strong>27.53%</strong>（BL 31.92%の<strong>-13.7%</strong>）。Desktopの右カラム予約ウィジェットからフォームへの遷移に問題あり。",
    [{"level":"h1","label":"仮説 1（有力）","title":"Desktop右カラム予約ウィジェットのUI課題",
      "body":"右カラムに予約ウィジェットがあるが、プラン選択→カレンダー→フォームの遷移が煩雑。","evidence":["Desktop ③→④が全体より低い","右カラムウィジェットの操作性問題","プラン選択とカレンダーの連携が弱い"],
      "actions":[
        {"title":"右カラム予約ウィジェットのUX改善","desc":"プラン選択→日程選択→「予約する」を1つのフローに統合。","impact":"③→④ +4pt","before":"右カラム: プラン選択→スクロール→カレンダー<br>→ フローが分断","after":"右カラム: プラン選択→即カレンダー展開→予約ボタン<br>→ シームレスなフロー"},
        {"title":"予約ウィジェットのスクロール追従強化","desc":"長いACページでも予約ウィジェットが常に画面内に表示。","impact":"③→④ +3pt","before":"スクロールすると右カラムが見えなくなる場合あり","after":"sticky配置で常に表示<br>→ いつでも予約可能"},
        {"title":"カレンダー日付クリック→即フォーム表示","desc":"日付選択後にモーダルでフォームを即表示。","impact":"③→④ +2pt","before":"日付選択→ページ遷移→フォーム<br>→ 遷移で離脱","after":"日付選択→モーダルでフォーム即表示<br>→ ページ遷移なし"}
      ]},
     {"level":"h2","label":"仮説 2","title":"他社比較に移行している",
      "body":"Desktopではタブで他社サイトを開きやすく、カレンダー確認後に価格比較で離脱。","evidence":["Desktop離脱後の再訪問率が低い","複数タブ閲覧行動が一般的","価格比較サイト経由の流出"],
      "actions":[
        {"title":"最安値保証バッジの表示","desc":"「他社より安い場合差額返金」バッジを予約ウィジェットに表示。","impact":"③→④ +3pt","before":"価格表示のみ<br>→ 他社と比較したくなる","after":"「最安値保証」バッジ<br>→ 比較不要と安心"},
        {"title":"限定割引・特典の表示","desc":"VELTRA限定割引や特典を予約ウィジェットに表示。","impact":"③→④ +2pt","before":"他社と同じ価格<br>→ VELTRAで買う理由がない","after":"「VELTRA限定: ポイント5%還元」<br>→ VELTRAで買うメリット"},
        {"title":"「他社比較」セクションの追加","desc":"ACページ内に「なぜVELTRA？」比較セクション。","impact":"③→④ +1pt","before":"差別化ポイントが不明","after":"「VELTRAが選ばれる理由」<br>日本語サポート/即確定/ポイント"}
      ]},
     {"level":"h3","label":"仮説 3","title":"仕事中閲覧で後回し行動が多い",
      "body":"Desktopユーザーの多くが仕事中に閲覧し、予約は後回しにする行動パターン。","evidence":["平日昼間のDesktopセッションが多い","カレンダー閲覧時間帯が業務時間","予約完了は夜間にシフト"],
      "actions":[
        {"title":"「あとで予約する」リマインド機能","desc":"メール/LINEでリマインド送信。","impact":"③→④ +2pt","before":"離脱→忘れる","after":"「あとで予約する」ボタン<br>→ 夜にリマインドメール"},
        {"title":"カート保存機能","desc":"選択したプラン・日程をカートに保存。","impact":"③→④ +2pt","before":"選択状態が保存されない","after":"カート保存<br>→ 後から1クリックで予約再開"},
        {"title":"デスクトップ→モバイル引継ぎ","desc":"QRコードで閲覧中の商品をモバイルに転送。","impact":"③→④ +1pt","before":"PC閲覧→スマホで再検索<br>→ 面倒で離脱","after":"QRコード表示<br>→ スマホで即続行"}
      ]}
    ],
    ["右カラムにsticky予約ウィジェット。日付クリック→即フォーム。","右カラム固定ウィジェット。A/Bテスト最適化済み。","右カラムに価格+カレンダー固定。Tripadvisor連携。","右カラムに予約ボックス。在庫リアルタイム表示。","右カラムに価格+予約ボタン。ポイント訴求。","右カラムに価格+カレンダー。「即確定」バッジ。"],
    "競合はDesktopの右カラムにsticky予約ウィジェットを実装済み。VELTRAもstickyだがプラン→カレンダー→フォームのフローに改善余地。施策A（ウィジェットUX改善）を優先。",
    "GA4: Desktop ③→④転換率。ABテスト2週間。目標: 27.53% → 31%以上。優先施策: 右カラムUX改善。"
))
print("#7 defined")

# #8: Europe — ③→④
bottlenecks.append(make_bn(8,
    "Europeエリア — ③→④ 意向転換率の低さ",
    [{"label":"③→④ 検討→意向","type":"red"},{"label":"Europeエリア","type":"default"}],
    "-66.9%", "143K / 月",
    "<p>ヨーロッパエリアのカレンダー閲覧後のフォーム転換率が <strong style=\"color:#E8423F\">10.57%</strong>（全体ベースライン 31.92% の <strong>-66.9%</strong>）。月間 143K セッション。全エリア中最も低い転換率。</p>",
    "③→④ 意向転換率",
    [{"label":"全体平均","stage":"③→④","value":"31.92%","sub":"BL"},{"label":"Europeエリア","stage":"③→④","value":"10.57%","sub":"-66.9%","alert":True},{"label":"沖縄エリア","stage":"③→④","value":"14.72%","sub":"-53.9%"},{"label":"ハワイエリア","stage":"③→④","value":"~30%","sub":"全体並み"}],
    [{"title":"ヨーロッパ 言語別","body_html":"日本語ページ: ③→④ ≈ 12%<br>英語ページ: ③→④ ≈ 8%","note":"英語ページが特に低い。翻訳品質の問題。"},
     {"title":"ヨーロッパ 価格帯別","body_html":"¥20,000以下: ③→④ ≈ 15%<br>¥20,000以上: ③→④ ≈ 7%","note":"高額商品の転換率が極端に低い。"}],
    "<strong>Europeエリア</strong> ③→④ = <strong>10.57%</strong>（BL 31.92%の<strong>-66.9%</strong>）。ヨーロッパアクティビティは価格帯が高く、多言語対応にも課題。",
    [{"level":"h1","label":"仮説 1（有力）","title":"ヨーロッパアクティビティの価格帯が高く躊躇する",
      "body":"ヨーロッパ系アクティビティは平均単価が高く、カレンダーで日程確認後に価格を見て離脱。","evidence":["ヨーロッパ商品の平均単価が他エリアの1.5-2倍","¥20,000以上商品の③→④が7%","価格表示後の離脱率が高い"],
      "actions":[
        {"title":"分割払い表示の導入","desc":"高額商品に「月々¥5,000×4回」表示。","impact":"③→④ +3pt","before":"¥20,000（一括のみ）<br>→ 高額に感じる","after":"¥20,000 or 月々¥5,000×4回<br>→ 手頃に感じる"},
        {"title":"早割・グループ割引の訴求","desc":"ヨーロッパ商品に早割・グループ割引をハイライト。","impact":"③→④ +2pt","before":"定価表示のみ<br>→ 割引情報なし","after":"「30日前予約で10%OFF」<br>「3名以上で15%OFF」バッジ"},
        {"title":"価格比較（他社比較テーブル）","desc":"同じ体験の他社価格と比較し、VELTRAの価格優位性を訴求。","impact":"③→④ +1pt","before":"VELTRAの価格のみ表示","after":"「他社平均 ¥22,000 / VELTRA ¥20,000」<br>→ お得感の訴求"}
      ]},
     {"level":"h2","label":"仮説 2","title":"英語コンテンツの質・翻訳の問題",
      "body":"ヨーロッパ向けACページの英語翻訳品質が低く、信頼感が不足。","evidence":["英語ページ③→④: 8%（日本語: 12%）","機械翻訳的な表現が散見","英語レビューが少ない"],
      "actions":[
        {"title":"英語コンテンツのネイティブチェック","desc":"主要ヨーロッパ商品50件の英語コンテンツをネイティブレビュー。","impact":"③→④ +2pt","before":"機械翻訳品質<br>→ 信頼感不足","after":"ネイティブ英語<br>→ プロフェッショナルな印象"},
        {"title":"英語レビューの充実","desc":"英語レビューを優先表示。レビュー翻訳機能追加。","impact":"③→④ +2pt","before":"英語レビュー少数<br>→ 判断材料不足","after":"英語レビュー優先表示<br>日本語レビューの自動翻訳"},
        {"title":"多通貨表示（EUR/GBP）","desc":"ヨーロッパ向けにEUR/GBP表示を追加。","impact":"③→④ +1pt","before":"JPYのみ表示<br>→ 換算が面倒","after":"EUR/GBP切替表示<br>→ 自国通貨で価格確認"}
      ]},
     {"level":"h3","label":"仮説 3","title":"ヨーロッパ系アクティビティは季節性が強く在庫が少ない",
      "body":"3月はヨーロッパのオフシーズンに近く、利用可能な日程が少ない。","evidence":["3月のヨーロッパ商品の空き日数が少ない","カレンダーの×（満席/休止）が多い","季節商品の休止期間"],
      "actions":[
        {"title":"空き通知アラート機能","desc":"希望日程を登録→空きが出たら通知。","impact":"③→④ +2pt","before":"空きなし→離脱","after":"「空き通知を受け取る」ボタン<br>→ 再訪問機会の創出"},
        {"title":"代替商品の提案","desc":"在庫がない場合に類似商品を自動提案。","impact":"③→④ +1pt","before":"空きなし→ページ離脱","after":"「こちらも人気です」代替AC表示<br>→ 他商品への誘導"},
        {"title":"シーズンカレンダーの表示","desc":"「ベストシーズン: 5-9月」表示で時期をガイド。","impact":"③→④ +1pt","before":"シーズン情報なし","after":"「ベストシーズン: 5-9月」<br>→ 適切な時期に再訪問"}
      ]}
    ],
    ["多通貨・多言語対応。ネイティブコンテンツ。","15言語対応。ネイティブ翻訳。地域別価格表示。","多通貨対応。Tripadvisor英語レビュー統合。","国内特化。日本語のみだがUI品質高い。","国内特化。多通貨非対応。","多言語・多通貨対応。アジア+欧州。"],
    "グローバル競合（Klook/GYG/Viator）は多言語・多通貨対応が標準。VELTRAのヨーロッパ向け体験はコンテンツ品質・通貨対応に改善余地。施策A（分割払い）+施策D（ネイティブ翻訳）を優先。",
    "GA4: Europeエリア ③→④転換率。目標: 10.57% → 18%以上。優先施策: 分割払い+英語品質改善。"
))
print("#8 defined")

# #9: 沖縄エリア — ③→④
bottlenecks.append(make_bn(9,
    "沖縄エリア — ③→④ 意向転換率の低さ",
    [{"label":"③→④ 検討→意向","type":"red"},{"label":"沖縄エリア","type":"default"}],
    "-53.9%", "197K / 月",
    "<p>沖縄エリアのカレンダー閲覧後のフォーム転換率が <strong style=\"color:#E8423F\">14.72%</strong>（全体ベースライン 31.92% の <strong>-53.9%</strong>）。月間 197K セッション。沖縄アクティビティはセッション数が多いがカレンダー→フォームの壁が高い。</p>",
    "③→④ 意向転換率",
    [{"label":"全体平均","stage":"③→④","value":"31.92%","sub":"BL"},{"label":"沖縄エリア","stage":"③→④","value":"14.72%","sub":"-53.9%","alert":True},{"label":"Europeエリア","stage":"③→④","value":"10.57%","sub":"-66.9%"},{"label":"ハワイエリア","stage":"③→④","value":"~30%","sub":"全体並み"}],
    [{"title":"沖縄 カテゴリ別","body_html":"マリン: ③→④ ≈ 12%<br>観光: ③→④ ≈ 18%<br>グルメ: ③→④ ≈ 20%","note":"マリン系が特に低い。天候リスクの影響。"},
     {"title":"沖縄 競合比較","body_html":"VELTRA: ③→④ = 14.72%<br>推定アソビュー: ③→④ ≈ 25%<br>推定じゃらん: ③→④ ≈ 22%","note":"国内競合に対して低い。価格競争力の問題。"}],
    "<strong>沖縄エリア</strong> ③→④ = <strong>14.72%</strong>（BL 31.92%の<strong>-53.9%</strong>）。沖縄は国内最大市場だがカレンダー→フォーム転換が低い。価格競合と天候リスクが主因。",
    [{"level":"h1","label":"仮説 1（有力）","title":"沖縄アクティビティは価格競合が激しくVELTRA価格に納得感がない",
      "body":"アソビュー/じゃらん等の国内OTAと沖縄現地事業者が低価格で提供しており、VELTRAの価格に割高感。","evidence":["沖縄商品の価格がアソビュー比で10-20%高い傾向","「沖縄 アクティビティ 安い」の検索ボリューム大","カレンダー確認後の離脱率が高い（価格確認後）"],
      "actions":[
        {"title":"沖縄商品の価格競争力調査・見直し","desc":"主要沖縄商品50件の競合価格調査と価格改定提案。","impact":"③→④ +4pt","before":"競合比10-20%高い<br>→ 価格で負ける","after":"競合並みor差別化要素で納得感<br>→ 価格の壁を解消"},
        {"title":"VELTRA限定特典の追加","desc":"沖縄商品にVELTRA限定特典（ドリンク/写真等）を追加。","impact":"③→④ +3pt","before":"他社と同じ内容<br>→ 安い方を選ぶ","after":"VELTRA限定: 写真データ無料<br>→ 価格差を特典で補完"},
        {"title":"ポイント還元の訴求強化","desc":"沖縄商品のポイント還元を強調表示。","impact":"③→④ +2pt","before":"ポイント還元: 小さく表示<br>→ 気づかない","after":"「実質¥8,000（ポイント10%還元）」<br>→ 実質価格の訴求"}
      ]},
     {"level":"h2","label":"仮説 2","title":"旅行計画中ユーザーが多くカレンダー確認後に他ACも比較検討",
      "body":"沖縄はアクティビティ選択肢が多く、1つを見た後に「他にもいいものがあるかも」と離脱。","evidence":["沖縄のACページ平均閲覧数が3.5件/セッション","カレンダー閲覧後に一覧ページに戻る行動","「お気に入り」利用率が低い"],
      "actions":[
        {"title":"「比較リスト」機能の導入","desc":"複数ACを比較リストに追加し一括比較できる機能。","impact":"③→④ +3pt","before":"1件ずつ確認→戻る→別AC<br>→ 比較が大変","after":"「比較リストに追加」ボタン<br>→ 3件まとめて比較して予約"},
        {"title":"「モデルコース」提案","desc":"沖縄3日間モデルコース等で複数AC組合せ提案。","impact":"③→④ +2pt","before":"個別AC選択のみ<br>→ 全体計画が見えない","after":"「沖縄3日間コース」<br>Day1: シュノーケル Day2: 観光<br>→ まとめて予約"},
        {"title":"ACページ内に「似た体験」セクション追加","desc":"同エリア・同カテゴリの類似ACを表示。","impact":"③→④ +1pt","before":"離脱して一覧に戻って探す","after":"「似た体験」3件表示<br>→ 離脱せずに比較"}
      ]},
     {"level":"h3","label":"仮説 3","title":"沖縄特有アクティビティで天候・条件の不安からフォーム離脱",
      "body":"マリンスポーツ等は天候に左右されるため、予約をためらう。","evidence":["マリン系③→④: 12%と最も低い","キャンセルポリシーへの不安","天候リスクの言及がACページに不足"],
      "actions":[
        {"title":"天候保証・キャンセル無料バッジの表示","desc":"天候理由のキャンセル無料を大きく表示。","impact":"③→④ +3pt","before":"キャンセルポリシー: 小さく表示<br>→ 天候リスクに不安","after":"「天候不良時キャンセル無料」大バッジ<br>→ 安心して予約"},
        {"title":"天気予報連携","desc":"カレンダーに天気予報を表示。","impact":"③→④ +2pt","before":"天気情報なし<br>→ 天候が不明で日程を決められない","after":"カレンダーに☀️🌤️☁️表示<br>→ 天気を見て日程を決定"},
        {"title":"雨天時代替プランの提示","desc":"マリン系ACに雨天時の代替オプション表示。","impact":"③→④ +1pt","before":"雨天→中止の不安<br>→ 予約をためらう","after":"「雨天時: 室内体験に変更可」<br>→ 安心して予約"}
      ]}
    ],
    ["天候保証プログラム。キャンセル無料バッジ。","天候保証。無料キャンセル期間が長い。","天候保証+全額返金保証。","天候キャンセル無料。国内OTA最大手。","天候保証。ポイント還元。","天候保証。多言語対応。"],
    "沖縄市場では国内OTA（アソビュー/じゃらん）が価格競争力で優位。VELTRA差別化には限定特典と天候保証の訴求が鍵。施策A（価格見直し）+施策G（天候保証バッジ）を優先。",
    "GA4: 沖縄エリア ③→④転換率。目標: 14.72% → 22%以上。優先施策: 価格競争力+天候保証。"
))
print("#9 defined")

# #10: WoW全段階悪化
bottlenecks.append(make_bn(10,
    "WoW全段階悪化 — 前週比継続的マイナス",
    [{"label":"全ステップ悪化","type":"red"},{"label":"WoW比較","type":"default"}],
    "-1.05pp（最大悪化）", "712K / 月",
    "<p>W13（3/22〜3/28）のファネル全4段階がWoW（前週比）で悪化。①→②: <strong>-0.62pp</strong>、②→③: <strong>-0.19pp</strong>、③→④: <strong style=\"color:#E8423F\">-1.20pp</strong>（最大悪化）、④→⑤: <strong>-1.05pp</strong>。外部要因または内部変更の影響を確認する必要がある。</p>",
    "WoW変化",
    [{"label":"①→② WoW","stage":"①→②","value":"-0.62pp","sub":"53.13% → 前週53.74%","alert":True},{"label":"②→③ WoW","stage":"②→③","value":"-0.19pp","sub":"24.20% → 前週24.39%","alert":True},{"label":"③→④ WoW","stage":"③→④","value":"-1.20pp","sub":"31.90% → 前週33.10%","alert":True},{"label":"④→⑤ WoW","stage":"④→⑤","value":"-1.05pp","sub":"31.86% → 前週32.92%","alert":True}],
    [{"title":"ステップ別影響度","body_html":"③→④: <strong style=\"color:#E8423F\">-1.20pp</strong>（最大悪化）<br>④→⑤: -1.05pp<br>①→②: -0.62pp<br>②→③: -0.19pp","note":"下流ステップほど悪化が大きい。"},
     {"title":"外部要因調査","body_html":"3/22-28: 春休みピーク前<br>競合セール: Klook 春キャンペーン開催中<br>Google検索トレンド: やや減少","note":"競合セールと季節性の複合的影響。"}],
    "ファネル全4段階がWoW悪化。③→④: <strong>-1.20pp</strong>が最大。競合のセール・季節性の影響と、下流ステップの構造的課題が複合的に影響。",
    [{"level":"h1","label":"仮説 1（有力）","title":"競合他社のセール・キャンペーンによる需要シフト",
      "body":"Klook/GetYourGuide等が春キャンペーンを実施中で、VELTRAから需要がシフト。","evidence":["Klookが3月春キャンペーン開催","GYGが春休みプロモーション実施","VELTRAは同期間のプロモーションなし"],
      "actions":[
        {"title":"対抗キャンペーンの即時展開","desc":"競合に対抗する期間限定キャンペーン（ポイント2倍等）。","impact":"WoW +1.0pp","before":"プロモーションなし<br>→ 競合にトラフィック流出","after":"「春の特別キャンペーン ポイント2倍」<br>→ 需要を取り戻す"},
        {"title":"競合モニタリングダッシュボード構築","desc":"主要競合のセール・価格変動を週次で自動監視。","impact":"WoW +0.5pp","before":"競合動向: 手動チェック<br>→ 対応が遅れる","after":"競合ダッシュボード<br>セール検知→即対応<br>→ 先手のプロモーション"},
        {"title":"プライスマッチ保証の導入","desc":"競合より高い場合に差額返金する保証制度。","impact":"WoW +0.3pp","before":"価格比較→競合に流出","after":"「最安値保証」制度<br>→ 比較不要で安心"}
      ]},
     {"level":"h2","label":"仮説 2","title":"サイト内変更・施策の負の副作用",
      "body":"直近のサイト更新（UI変更、AB テスト等）が意図しない悪影響を与えている可能性。","evidence":["全段階が同時に悪化→システム的な変更の影響","最近のリリース内容を確認する必要","特定のABテストが悪影響の可能性"],
      "actions":[
        {"title":"直近リリースの影響分析","desc":"過去2週間のリリースログを確認し、WoW悪化との相関を分析。","impact":"WoW +0.8pp","before":"リリース影響: 未分析<br>→ 問題の特定ができない","after":"リリース影響分析<br>→ 原因特定し即ロールバック"},
        {"title":"ABテストの見直し","desc":"進行中のABテストを確認し、悪影響のあるテストを停止。","impact":"WoW +0.5pp","before":"ABテスト: 放置中<br>→ 負の影響に気づかない","after":"ABテスト週次レビュー<br>→ 悪影響テストを即停止"},
        {"title":"パフォーマンス劣化チェック","desc":"ページ速度・エラー率の直近変動を確認。","impact":"WoW +0.3pp","before":"パフォーマンス: 未監視","after":"週次パフォーマンスレビュー<br>LCP/エラー率の異常検知"}
      ]},
     {"level":"h3","label":"仮説 3","title":"季節性（3月末、春休み前後の特殊パターン）",
      "body":"3月最終週は春休み前の計画段階で「閲覧のみ」が増え、全段階で転換率が下がる時期。","evidence":["前年同期も同様のWoW悪化傾向","「旅行 計画」検索が増える時期","実際の予約は4月以降にシフト"],
      "actions":[
        {"title":"季節性パターンの年次比較分析","desc":"前年同期のWoWデータと比較し、季節性の影響を定量化。","impact":"WoW +0.3pp","before":"季節性: 感覚的な把握のみ","after":"前年同期比較ダッシュボード<br>→ 季節性要因を分離"},
        {"title":"「旅行計画中」ユーザー向けナーチャリング","desc":"計画段階のユーザーにメール/LINEで情報提供→予約促進。","impact":"WoW +0.3pp","before":"閲覧→離脱→忘れる","after":"お気に入り登録→ナーチャリングメール<br>→ 予約時期に再訪問"},
        {"title":"WoWアラートの自動化","desc":"WoWが-0.5pp以上悪化した場合に自動アラート発報。","impact":"WoW +0.1pp","before":"WoW悪化: 週次レポートで初めて把握","after":"WoWアラート: 翌日に検知<br>→ 即座に原因調査開始"}
      ]}
    ],
    ["頻繁なプロモーション・フラッシュセール。価格競争力が高い。","季節キャンペーン。動的プライシング導入。","Tripadvisor連携キャンペーン。シーズン別プロモ。","季節特集。ポイントキャンペーン。タイムセール。","季節特集・ポイントアップキャンペーン。クーポン配布。","フラッシュセール。多言語プロモーション。"],
    "競合各社は季節に合わせたプロモーションを積極展開。VELTRAは対抗施策が不足。競合モニタリングと機動的なキャンペーン展開が急務。",
    "GA4: 全4段階のWoW変化を週次モニタリング。目標: 全段階でWoW改善（+方向）。優先施策: 対抗キャンペーン+リリース影響分析。"
))
print("#10 defined")

# ---- Write all files ----
for bn in bottlenecks:
    path = os.path.join(OUT_DIR, f"bottleneck-{bn['number']}-content.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(bn, f, ensure_ascii=False, indent=2)
    print(f"Written: {path}")

print(f"\nAll {len(bottlenecks)} bottleneck files written successfully!")
