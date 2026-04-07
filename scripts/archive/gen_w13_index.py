#!/usr/bin/env python3
"""Generate W13 index.html from W14 template with W13 data."""
import re

# Read W14 template
with open('/home/user/v2-veltra-cvr/reports/2026-w14/index.html', 'r') as f:
    w14 = f.read()

# Extract CSS (everything up to </style>)
css_end = w14.index('</style>') + len('</style>')
css = w14[:css_end]

# Build W13 HTML
html = css + """
</head>
<body>

<!-- ======================== HEADER ======================== -->
<div class="card">
  <div class="header-band">
    <div class="logo">V2</div>
    <div class="right">
      週次ボトルネック分析レポート<br>
      <strong>2026年 第13週（3/22〜3/28）</strong>
    </div>
  </div>
  <div style="padding:24px 44px;display:flex;gap:32px;flex-wrap:wrap;font-size:14px;line-height:1.8;color:var(--text2)">
    <div><span style="color:var(--text3);font-weight:600">分析対象データ</span><br>GA4 Property 347074845<br>直近28日間（3/1〜3/28）</div>
    <div><span style="color:var(--text3);font-weight:600">レポート発行週</span><br>2026年 W13（3/22〜3/28）</div>
    <div><span style="color:var(--text3);font-weight:600">生成日時</span><br>2026-04-07 04:00 JST</div>
  </div>
</div>

<!-- ======================== STEP 1: BASELINE ======================== -->
<div class="card">
  <div class="sec-label">Step 1 — ベースライン（全体ファネル転換率）</div>
  <hr class="divider-solid">
  <div style="padding:28px 44px">
    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0;border:1px solid var(--border);border-radius:10px;overflow:hidden">
      <div style="padding:20px;text-align:center;border-right:1px solid var(--border)">
        <div style="font-size:12px;color:var(--text3);font-weight:700;text-transform:uppercase">①流入</div>
        <div style="font-family:'DM Sans';font-size:32px;font-weight:900;margin:8px 0 2px">2.92M</div>
        <div style="font-size:13px;color:var(--text3)">sessions</div>
        <div style="font-size:12px;color:var(--text3);margin-top:4px">（2,915,100）</div>
      </div>
      <div style="padding:20px;text-align:center;border-right:1px solid var(--border)">
        <div style="font-size:12px;color:var(--text3);font-weight:700;text-transform:uppercase">②AC到達</div>
        <div style="font-family:'DM Sans';font-size:32px;font-weight:900;margin:8px 0 2px">82.60%</div>
        <div style="font-size:13px;color:var(--text3)">①→② 転換率</div>
      </div>
      <div style="padding:20px;text-align:center;border-right:1px solid var(--border)">
        <div style="font-size:12px;color:var(--text3);font-weight:700;text-transform:uppercase">③検討</div>
        <div style="font-family:'DM Sans';font-size:32px;font-weight:900;margin:8px 0 2px">26.43%</div>
        <div style="font-size:13px;color:var(--text3)">②→③ 転換率</div>
      </div>
      <div style="padding:20px;text-align:center;border-right:1px solid var(--border)">
        <div style="font-size:12px;color:var(--text3);font-weight:700;text-transform:uppercase">④意向</div>
        <div style="font-family:'DM Sans';font-size:32px;font-weight:900;margin:8px 0 2px">31.92%</div>
        <div style="font-size:13px;color:var(--text3)">③→④ 転換率</div>
      </div>
      <div style="padding:20px;text-align:center">
        <div style="font-size:12px;color:var(--text3);font-weight:700;text-transform:uppercase">⑤完了</div>
        <div style="font-family:'DM Sans';font-size:32px;font-weight:900;margin:8px 0 2px;color:var(--red)">1.48%</div>
        <div style="font-size:13px;color:var(--text3)">43,195 purchases</div>
      </div>
    </div>
    <div style="margin-top:16px;display:grid;grid-template-columns:repeat(4,1fr);gap:8px">
      <div style="padding:10px 14px;background:var(--red-light);border-radius:6px;text-align:center;border:1px solid var(--red)">
        <div style="font-size:11px;color:var(--text3)">WoW ①→②</div>
        <div style="font-family:'DM Sans';font-size:18px;font-weight:700;color:var(--red)">-0.62pp</div>
      </div>
      <div style="padding:10px 14px;background:var(--red-light);border-radius:6px;text-align:center;border:1px solid var(--red)">
        <div style="font-size:11px;color:var(--text3)">WoW ②→③</div>
        <div style="font-family:'DM Sans';font-size:18px;font-weight:700;color:var(--red)">-0.19pp</div>
      </div>
      <div style="padding:10px 14px;background:var(--red-light);border-radius:6px;text-align:center;border:1px solid var(--red)">
        <div style="font-size:11px;color:var(--text3)">WoW ③→④</div>
        <div style="font-family:'DM Sans';font-size:18px;font-weight:700;color:var(--red)">-1.20pp</div>
      </div>
      <div style="padding:10px 14px;background:var(--red-light);border-radius:6px;text-align:center;border:1px solid var(--red)">
        <div style="font-size:11px;color:var(--text3)">WoW ④→⑤</div>
        <div style="font-family:'DM Sans';font-size:18px;font-weight:700;color:var(--red)">-1.05pp</div>
      </div>
    </div>
  </div>
</div>
"""
print("Part 1 done: header + baseline")
# Deep dive #1
html += """
<!-- ======================== BOTTLENECK #1 DEEP DIVE ======================== -->
<div class="card">
  <div class="sec-label">ボトルネック #1（詳細分析例）</div>
  <hr class="divider-solid">

  <!-- Header with rank, title, metrics -->
  <div class="bn-header">
    <div>
      <div style="display:flex;align-items:center;gap:16px;margin-bottom:8px">
        <div class="bn-rank">#1</div>
        <div>
          <div class="bn-title">Organic Search — ①→② AC到達率の低さ</div>
          <div class="bn-segment">
            <span class="bn-tag red">①→② 流入→AC到達</span>
            <span class="bn-tag">Organic Search</span>
          </div>
        </div>
      </div>
    </div>
    <div class="bn-metrics-grid">
      <div class="bmg-cell">
        <div class="bmg-label">ベースライン（全体平均）</div>
        <div class="bmg-val">82.60%</div>
      </div>
      <div class="bmg-cell alert">
        <div class="bmg-label">今週実績</div>
        <div class="bmg-val neg">47.75%</div>
      </div>
      <div class="bmg-cell alert">
        <div class="bmg-label">Gap</div>
        <div class="bmg-val neg">-42.25%<span class="bmg-pp">（-34.85pp）</span></div>
      </div>
      <div class="bmg-cell">
        <div class="bmg-label">影響セッション</div>
        <div class="bmg-val">1.27M<span class="bmg-pp">/月</span></div>
      </div>
    </div>
  </div>

  <hr class="divider">

  <!-- Step 2: Tier 1 comparison -->
  <div style="padding:24px 44px 12px">
    <div style="font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px">Step 2-3 — Tier 1 比較：①→② AC到達率</div>
  </div>
  <div class="funnel-compare">
    <div class="fc-cell">
      <div class="fc-label">全体平均</div>
      <div class="fc-stage">①→② AC到達</div>
      <div class="fc-val" style="font-size:28px;margin-top:8px">82.60%</div>
      <div class="fc-val-label">ベースライン</div>
    </div>
    <div class="fc-cell alert">
      <div class="fc-label" style="color:var(--red)">Organic Search</div>
      <div class="fc-stage">①→② AC到達</div>
      <div class="fc-val neg" style="font-size:28px;margin-top:8px">47.75%</div>
      <div class="fc-val-label" style="color:var(--red)">-42.25% vs 全体 ← アラート</div>
    </div>
    <div class="fc-cell">
      <div class="fc-label">Paid Search</div>
      <div class="fc-stage">①→② AC到達</div>
      <div class="fc-val" style="font-size:28px;margin-top:8px">57.19%</div>
      <div class="fc-val-label">-30.8% vs 全体</div>
    </div>
    <div class="fc-cell">
      <div class="fc-label">新規ユーザー</div>
      <div class="fc-stage">①→② AC到達</div>
      <div class="fc-val" style="font-size:28px;margin-top:8px">47.95%</div>
      <div class="fc-val-label">-41.9% vs 全体</div>
    </div>
  </div>

  <!-- Step 4-5: Tier 2-3 drill down -->
  <div style="padding:0 44px 20px">
    <div style="font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px">Step 4-5 — Tier 2-3 深掘り</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <div style="border:1px solid var(--border);border-radius:8px;padding:16px 20px">
        <div style="font-size:14px;font-weight:700;margin-bottom:8px">新規 vs リピーター</div>
        <div style="font-size:15px;color:var(--text2);line-height:1.7">
          <strong style="color:var(--red)">新規: ①→② = 47.95%</strong>（全体比 -42%）<br>
          リピーター: ①→② = 62.37%（全体比 -24%）
        </div>
        <div style="font-size:13px;color:var(--text3);margin-top:8px">→ 新規ユーザーが特に低い。初回訪問時のAC到達導線に問題。</div>
      </div>
      <div style="border:1px solid var(--border);border-radius:8px;padding:16px 20px">
        <div style="font-size:14px;font-weight:700;margin-bottom:8px">デバイス別（Organic Search内）</div>
        <div style="font-size:15px;color:var(--text2);line-height:1.7">
          <strong style="color:var(--red)">Mobile: ①→② = 52.31%</strong>（全体比 -37%）<br>
          Desktop: ①→② = 52.93%（全体比 -36%）
        </div>
        <div style="font-size:13px;color:var(--text3);margin-top:8px">→ デバイス間の差は小さい。Organic Search全体の構造的な問題。</div>
      </div>
    </div>
  </div>

  <div class="callout" style="margin-top:0">
    <div class="ct">特定結果</div>
    <div class="cb"><strong>Organic Search</strong> の ①→② AC到達率が <strong>47.75%</strong>（全体平均 82.60% の <strong>-42.25%</strong>）。<br>月間 1,267Kセッション（最大チャネル）。<br>SEO検索結果からの流入後、トップページやカテゴリページで離脱しACページへたどり着かない。<br>新規ユーザー（47.95%）が特に低く、デバイス差は小さい → チャネル固有のLP→AC導線の問題。</div>
  </div>

  <hr class="divider">
"""
print("Part 2 done: deep dive header")
# Hypotheses section
html += """
  <!-- Step 6: Hypotheses -->
  <div style="padding:24px 44px 16px">
    <div style="font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">Step 6 — 原因仮説 × 3</div>
    <div style="font-size:15px;color:var(--text2)">なぜ Organic Search の ①→② AC到達率が低いか？</div>
  </div>
  <div class="hypo-grid">
    <div class="hypo-card h1">
      <div class="hypo-num">仮説 1（有力）</div>
      <div class="hypo-title">SEOランディングページからACページへの導線が弱い</div>
      <div class="hypo-body">Organic検索で到達するページ（トップ・カテゴリ・エリア一覧）からACページへのリンクが目立たず、ユーザーが商品詳細まで進めていない。</div>
      <div class="hypo-evidence"><strong>施策:</strong></div>
      <div class="hypo-tactics">
        <div class="hypo-tactics-label">施策</div>
        <div class="hypo-tactic"><div class="ht-left"><div class="ht-id">施策A</div><div class="ht-title">カテゴリページにACカード型レイアウト導入</div></div><div class="ht-impact">①→② +8pt</div></div>
        <div class="hypo-tactic"><div class="ht-left"><div class="ht-id">施策B</div><div class="ht-title">エリアページにパーソナライズ推薦セクション追加</div></div><div class="ht-impact">①→② +5pt</div></div>
        <div class="hypo-tactic"><div class="ht-left"><div class="ht-id">施策C</div><div class="ht-title">SEO LP内にインライン商品プレビュー埋め込み</div></div><div class="ht-impact">①→② +3pt</div></div>
      </div>
    </div>
    <div class="hypo-card h2">
      <div class="hypo-num">仮説 2</div>
      <div class="hypo-title">検索意図のミスマッチ（情報収集 vs 予約）</div>
      <div class="hypo-body">Organic検索ユーザーの多くが「〇〇 おすすめ」「〇〇 観光」等の情報収集キーワードで流入。予約意向がなくACまで進まない。</div>
      <div class="hypo-evidence"><strong>施策:</strong></div>
      <div class="hypo-tactics">
        <div class="hypo-tactics-label">施策</div>
        <div class="hypo-tactic"><div class="ht-left"><div class="ht-id">施策D</div><div class="ht-title">情報系LPに「体験を探す」CTA設置</div></div><div class="ht-impact">①→② +4pt</div></div>
        <div class="hypo-tactic"><div class="ht-left"><div class="ht-id">施策E</div><div class="ht-title">ブログ・ガイド記事内にACリンクカード挿入</div></div><div class="ht-impact">①→② +3pt</div></div>
        <div class="hypo-tactic"><div class="ht-left"><div class="ht-id">施策F</div><div class="ht-title">検索キーワード別LP最適化（予約意図の高いKWに注力）</div></div><div class="ht-impact">①→② +2pt</div></div>
      </div>
    </div>
    <div class="hypo-card h3">
      <div class="hypo-num">仮説 3</div>
      <div class="hypo-title">ページ表示速度・技術的課題による離脱</div>
      <div class="hypo-body">SEOランディングページの読み込み速度がモバイルで遅く、ユーザーがACページに到達する前にバウンスしている可能性。</div>
      <div class="hypo-evidence"><strong>施策:</strong></div>
      <div class="hypo-tactics">
        <div class="hypo-tactics-label">施策</div>
        <div class="hypo-tactic"><div class="ht-left"><div class="ht-id">施策G</div><div class="ht-title">LCPの改善（画像遅延読み込み・CDN最適化）</div></div><div class="ht-impact">①→② +3pt</div></div>
        <div class="hypo-tactic"><div class="ht-left"><div class="ht-id">施策H</div><div class="ht-title">プリフェッチによるAC遷移高速化</div></div><div class="ht-impact">①→② +2pt</div></div>
        <div class="hypo-tactic"><div class="ht-left"><div class="ht-id">施策I</div><div class="ht-title">Core Web Vitals継続モニタリング設置</div></div><div class="ht-impact">①→② +1pt</div></div>
      </div>
    </div>
  </div>

  <hr class="divider">
"""
print("Part 3 done: hypotheses")
# Prototype section
html += """
  <!-- Prototype -->
  <div style="padding:24px 44px 16px">
    <div style="font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">プロトタイプ — 施策1-A カテゴリページ改善</div>
    <div style="font-size:15px;color:var(--text2)">カテゴリ/エリアページの Before / After — ①→② AC到達率改善</div>
  </div>

  <div class="proto-section">
    <div class="ba-grid">
      <!-- Before -->
      <div class="ba-col" style="padding:40px 24px 24px">
        <div class="ba-label">Before（現状）</div>
        <div class="mobile-frame">
          <div class="mobile-notch">veltra.com/jp/hawaii/oahu/</div>
          <div class="mobile-body">
            <div style="background:#1B82C5;padding:12px 16px;color:#fff">
              <div style="font-size:15px;font-weight:900">VELTRA</div>
            </div>
            <div style="padding:12px 16px;background:#f8f8f8;font-size:13px;font-weight:700">オアフ島のオプショナルツアー</div>
            <div style="padding:8px 16px;font-size:11px;color:#999">258件のツアーが見つかりました</div>
            <div style="padding:8px 16px;border-bottom:1px solid #f0f0f0">
              <div style="font-size:12px;font-weight:700;padding:6px 0">ダイヤモンドヘッド日の出ハイキング</div>
              <div style="font-size:10px;color:#999">★4.52（328件） | ¥12,800〜</div>
            </div>
            <div style="padding:8px 16px;border-bottom:1px solid #f0f0f0">
              <div style="font-size:12px;font-weight:700;padding:6px 0">ノースショア観光ツアー</div>
              <div style="font-size:10px;color:#999">★4.31（156件） | ¥15,200〜</div>
            </div>
            <div style="padding:8px 16px;border-bottom:1px solid #f0f0f0">
              <div style="font-size:12px;font-weight:700;padding:6px 0">シュノーケリング体験</div>
              <div style="font-size:10px;color:#999">★4.67（89件） | ¥9,800〜</div>
            </div>
            <div style="padding:8px 16px;font-size:10px;color:#ccc;text-align:center">テキストリスト表示 → 商品の魅力が伝わらない</div>
          </div>
        </div>
      </div>
      <!-- After -->
      <div class="ba-col" style="padding:40px 24px 24px">
        <div class="ba-label after">After（施策1-A適用）</div>
        <div class="mobile-frame">
          <div class="mobile-notch">veltra.com/jp/hawaii/oahu/</div>
          <div class="mobile-body">
            <div style="background:#1B82C5;padding:12px 16px;color:#fff">
              <div style="font-size:15px;font-weight:900">VELTRA</div>
            </div>
            <div style="padding:12px 16px;background:#f8f8f8;font-size:13px;font-weight:700">オアフ島のオプショナルツアー</div>
            <div style="padding:8px 16px">
              <div style="border:1px solid #ddd;border-radius:8px;overflow:hidden;margin-bottom:10px">
                <div style="height:80px;background:linear-gradient(135deg,#2196F3,#0D47A1);display:flex;align-items:flex-end;padding:8px">
                  <span style="color:#fff;font-size:11px;font-weight:700">📸 ダイヤモンドヘッド</span>
                </div>
                <div style="padding:8px 10px">
                  <div style="font-size:12px;font-weight:700">ダイヤモンドヘッド日の出ハイキング</div>
                  <div style="display:flex;justify-content:space-between;margin-top:4px">
                    <span style="font-size:10px;color:#FFAA00">★4.52（328件）</span>
                    <span style="font-size:12px;font-weight:900;color:#D91F26">¥12,800〜</span>
                  </div>
                  <div style="background:#E8386E;color:#fff;padding:6px;border-radius:4px;font-size:11px;font-weight:700;text-align:center;margin-top:6px">詳細を見る →</div>
                </div>
              </div>
              <div style="border:1px solid #ddd;border-radius:8px;overflow:hidden">
                <div style="height:80px;background:linear-gradient(135deg,#4CAF50,#1B5E20);display:flex;align-items:flex-end;padding:8px">
                  <span style="color:#fff;font-size:11px;font-weight:700">🏄 シュノーケリング</span>
                </div>
                <div style="padding:8px 10px">
                  <div style="font-size:12px;font-weight:700">シュノーケリング体験</div>
                  <div style="display:flex;justify-content:space-between;margin-top:4px">
                    <span style="font-size:10px;color:#FFAA00">★4.67（89件）</span>
                    <span style="font-size:12px;font-weight:900;color:#D91F26">¥9,800〜</span>
                  </div>
                </div>
              </div>
            </div>
            <div style="padding:4px 16px 12px;font-size:10px;color:var(--green);text-align:center;font-weight:500">カード型レイアウトでACページへの誘導率UP</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Change summary -->
  <div style="padding:0 44px 32px">
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
      <div class="callout-green callout" style="margin:0">
        <div class="ct">施策1-A 反映</div>
        <div class="cb" style="font-size:14px">カテゴリページをカード型レイアウトに変更。写真・評価・価格を一覧表示しACページへの誘導を強化。</div>
      </div>
      <div class="callout-green callout" style="margin:0">
        <div class="ct">施策1-B 反映</div>
        <div class="cb" style="font-size:14px">エリアページにパーソナライズ推薦セクションを追加。閲覧履歴に基づくおすすめACを表示。</div>
      </div>
      <div class="callout-green callout" style="margin:0">
        <div class="ct">仮説2 対応</div>
        <div class="cb" style="font-size:14px">情報系LPに「体験を探す」CTAを設置。情報収集ユーザーをACページへ転換。</div>
      </div>
    </div>
  </div>

  <!-- Verification -->
  <div class="callout-amber callout">
    <div class="ct">検証方法</div>
    <div class="cb">ABテスト 2週間。対象: Organic Search 全体。<br>
    主要指標: ①→② AC到達率（現状 47.75% → 目標 60%以上）。<br>
    副次指標: CVR、②→③ 検討転換率への波及効果。</div>
  </div>

  <hr class="divider">
"""
print("Part 4 done: prototype + verification")
# Competitive analysis
html += """
  <!-- Competitive Analysis -->
  <div style="padding:24px 44px 16px">
    <div style="font-size:13px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">競合のカテゴリ/一覧ページ比較 <span style="background:var(--red-light);color:var(--red);padding:2px 8px;border-radius:4px;font-size:11px;margin-left:6px">LP→ACページ導線視点</span></div>
    <div style="font-size:15px;color:var(--text2)">ボトルネックが「Organic Search ①→②」のため、カテゴリ/エリア一覧ページからACページへの導線を中心に比較。</div>
  </div>

  <div style="padding:0 44px 32px">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
      <div style="border:1px solid var(--border);border-radius:10px;padding:18px 20px">
        <div style="font-size:16px;font-weight:700;margin-bottom:10px">Klook</div>
        <div style="font-size:14px;color:var(--text2);line-height:1.7;margin-bottom:10px">
          カテゴリページはカード型レイアウト。各カードに写真・評価・価格・「即確定」バッジを表示。タップで即ACページへ遷移。フィルター・ソート機能が充実。
        </div>
        <div style="font-size:12px;color:var(--text3)">注目点: ビジュアル重視のカード型UIでAC到達率を最大化。施策Aの直接参考。</div>
      </div>
      <div style="border:1px solid var(--border);border-radius:10px;padding:18px 20px">
        <div style="font-size:16px;font-weight:700;margin-bottom:10px">GetYourGuide</div>
        <div style="font-size:14px;color:var(--text2);line-height:1.7;margin-bottom:10px">
          一覧ページに「おすすめ」「人気」バッジ表示。カード内に空き状況インジケーターを表示。地図ビューとリストビューの切り替え機能。
        </div>
        <div style="font-size:12px;color:var(--text3)">注目点: 空き状況の事前表示でAC到達前に情報提供。施策Bのパーソナライズと方向性一致。</div>
      </div>
      <div style="border:1px solid var(--border);border-radius:10px;padding:18px 20px">
        <div style="font-size:16px;font-weight:700;margin-bottom:10px">Viator</div>
        <div style="font-size:14px;color:var(--text2);line-height:1.7;margin-bottom:10px">
          写真カード+Tripadvisorレビュー統合。「ベストセラー」「割引あり」ラベル表示。カテゴリページ内にミニ商品プレビュー（写真複数枚）。
        </div>
        <div style="font-size:12px;color:var(--text3)">注目点: レビュー統合による信頼構築。ミニプレビューは施策Cのインライン商品表示と類似。</div>
      </div>
      <div style="border:1px solid var(--border);border-radius:10px;padding:18px 20px">
        <div style="font-size:16px;font-weight:700;margin-bottom:10px">アソビュー</div>
        <div style="font-size:14px;color:var(--text2);line-height:1.7;margin-bottom:10px">
          カード型一覧に「本日空きあり」「残りわずか」リアルタイム表示。価格比較しやすいレイアウト。エリア×カテゴリのクロスフィルター。
        </div>
        <div style="font-size:12px;color:var(--text3)">注目点: リアルタイム在庫表示がAC到達前にアクションを促す。</div>
      </div>
      <div style="border:1px solid var(--border);border-radius:10px;padding:18px 20px">
        <div style="font-size:16px;font-weight:700;margin-bottom:10px">じゃらん</div>
        <div style="font-size:14px;color:var(--text2);line-height:1.7;margin-bottom:10px">
          エリア特集ページからアクティビティ一覧へ自然な導線。写真カード+口コミ数表示。「じゃらんポイント使える」バッジで会員訴求。
        </div>
        <div style="font-size:12px;color:var(--text3)">注目点: ポイント訴求は情報収集ユーザーの予約転換に効果的。</div>
      </div>
      <div style="border:1px solid var(--border);border-radius:10px;padding:18px 20px">
        <div style="font-size:16px;font-weight:700;margin-bottom:10px">KKday</div>
        <div style="font-size:14px;color:var(--text2);line-height:1.7;margin-bottom:10px">
          カード型一覧に「即確定」「キャンセル無料」バッジ。価格表示が明瞭。「今週の人気TOP10」セクションでACへの誘導を強化。
        </div>
        <div style="font-size:12px;color:var(--text3)">注目点: 人気ランキング表示でAC到達のモチベーションを提供。</div>
      </div>
    </div>

    <div class="callout" style="margin:20px 0 0">
      <div class="ct">競合比較から得られる示唆</div>
      <div class="cb">主要競合6社すべてがカテゴリ/一覧ページにカード型ビジュアルレイアウトを採用済み。VELTRAのテキストリスト表示は業界水準から大きく乖離。施策A（カード型レイアウト）は最優先で実装すべき。加えて、空き状況・バッジ表示（即確定/人気/割引）でAC到達前のモチベーション向上も有効。</div>
    </div>
  </div>

</div>
"""
print("Part 5 done: competitive")
# Accordion #2-#10
html += """
<!-- ======================== REMAINING 9 BOTTLENECKS (SUMMARY) ======================== -->
<div class="card">
  <div class="sec-label">ボトルネック #2〜#10（サマリー）</div>
  <hr class="divider-solid">
  <div class="bn-acc" id="bn-acc-list">

    <div class="bn-acc-item">
      <div class="bn-acc-header" onclick="toggleBnAcc(this)">
        <div class="bn-acc-rank">#2</div>
        <div class="bn-acc-body">
          <div class="bn-acc-title">新規ユーザー — ②→③ 検討転換率の低さ</div>
          <div class="bn-acc-tags"><span class="bn-acc-tag red">②→③ AC到達→検討</span><span class="bn-acc-tag">新規ユーザー</span></div>
        </div>
        <div class="bn-acc-meta"><div class="bn-acc-gap-label">全体比乖離</div><div class="bn-acc-gap">-39%</div></div>
        <div class="bn-acc-chevron">▶</div>
      </div>
      <div class="bn-acc-detail">
        <div class="bn-acc-hypo">新規ユーザーのAC到達後のカレンダー転換率 16.14% vs 26.43% ベースライン（-10.29pp）。1,534Kセッション/月。初回訪問ユーザーはACページを閲覧するが価格・プランの判断に迷い日程選択まで進まない。</div>
        <a class="bn-acc-link" href="/bottleneck.html?week=2026-w13&num=2">詳細分析を見る →</a>
      </div>
    </div>

    <div class="bn-acc-item">
      <div class="bn-acc-header" onclick="toggleBnAcc(this)">
        <div class="bn-acc-rank">#3</div>
        <div class="bn-acc-body">
          <div class="bn-acc-title">Mobile — ④→⑤ 完了率の低さ</div>
          <div class="bn-acc-tags"><span class="bn-acc-tag red">④→⑤ 意向→完了</span><span class="bn-acc-tag">Mobile</span></div>
        </div>
        <div class="bn-acc-meta"><div class="bn-acc-gap-label">全体比乖離</div><div class="bn-acc-gap">-14%</div></div>
        <div class="bn-acc-chevron">▶</div>
      </div>
      <div class="bn-acc-detail">
        <div class="bn-acc-hypo">Mobileの購入完了率 29.89% vs 34.57% ベースライン（-4.68pp）。101Kセッション/月。Mobileのフォーム入力・決済UIが使いにくく最終段階で離脱。</div>
        <a class="bn-acc-link" href="/bottleneck.html?week=2026-w13&num=3">詳細分析を見る →</a>
      </div>
    </div>

    <div class="bn-acc-item">
      <div class="bn-acc-header" onclick="toggleBnAcc(this)">
        <div class="bn-acc-rank">#4</div>
        <div class="bn-acc-body">
          <div class="bn-acc-title">Organic Search — ②→③ 検討転換率の低さ</div>
          <div class="bn-acc-tags"><span class="bn-acc-tag red">②→③ AC到達→検討</span><span class="bn-acc-tag">Organic Search</span></div>
        </div>
        <div class="bn-acc-meta"><div class="bn-acc-gap-label">全体比乖離</div><div class="bn-acc-gap">-23%</div></div>
        <div class="bn-acc-chevron">▶</div>
      </div>
      <div class="bn-acc-detail">
        <div class="bn-acc-hypo">Organic Search ②→③ 転換率 20.47% vs 26.43% ベースライン（-5.96pp）。1,267Kセッション/月。SEO経由ユーザーはACページに到達するが日程検討まで進まない。</div>
        <a class="bn-acc-link" href="/bottleneck.html?week=2026-w13&num=4">詳細分析を見る →</a>
      </div>
    </div>

    <div class="bn-acc-item">
      <div class="bn-acc-header" onclick="toggleBnAcc(this)">
        <div class="bn-acc-rank">#5</div>
        <div class="bn-acc-body">
          <div class="bn-acc-title">Paid Search — ③→④ 意向転換率の低さ</div>
          <div class="bn-acc-tags"><span class="bn-acc-tag red">③→④ 検討→意向</span><span class="bn-acc-tag">Paid Search</span></div>
        </div>
        <div class="bn-acc-meta"><div class="bn-acc-gap-label">全体比乖離</div><div class="bn-acc-gap">-36%</div></div>
        <div class="bn-acc-chevron">▶</div>
      </div>
      <div class="bn-acc-detail">
        <div class="bn-acc-hypo">Paid Search ③→④ 転換率 20.43% vs 31.92% ベースライン（-11.49pp）。710Kセッション/月。広告経由で日程を確認したがフォームに進まない。</div>
        <a class="bn-acc-link" href="/bottleneck.html?week=2026-w13&num=5">詳細分析を見る →</a>
      </div>
    </div>

    <div class="bn-acc-item">
      <div class="bn-acc-header" onclick="toggleBnAcc(this)">
        <div class="bn-acc-rank">#6</div>
        <div class="bn-acc-body">
          <div class="bn-acc-title">新規ユーザー — ①→② AC到達率の低さ</div>
          <div class="bn-acc-tags"><span class="bn-acc-tag red">①→② 流入→AC到達</span><span class="bn-acc-tag">新規ユーザー</span></div>
        </div>
        <div class="bn-acc-meta"><div class="bn-acc-gap-label">全体比乖離</div><div class="bn-acc-gap">-42%</div></div>
        <div class="bn-acc-chevron">▶</div>
      </div>
      <div class="bn-acc-detail">
        <div class="bn-acc-hypo">新規ユーザー ①→② AC到達率 47.95% vs 82.60% ベースライン（-34.65pp）。1,534Kセッション/月。初回訪問ユーザーがサイト流入後ACページへ進まない。</div>
        <a class="bn-acc-link" href="/bottleneck.html?week=2026-w13&num=6">詳細分析を見る →</a>
      </div>
    </div>

    <div class="bn-acc-item">
      <div class="bn-acc-header" onclick="toggleBnAcc(this)">
        <div class="bn-acc-rank">#7</div>
        <div class="bn-acc-body">
          <div class="bn-acc-title">Desktop — ③→④ 意向転換率の低さ</div>
          <div class="bn-acc-tags"><span class="bn-acc-tag red">③→④ 検討→意向</span><span class="bn-acc-tag">Desktop</span></div>
        </div>
        <div class="bn-acc-meta"><div class="bn-acc-gap-label">全体比乖離</div><div class="bn-acc-gap">-14%</div></div>
        <div class="bn-acc-chevron">▶</div>
      </div>
      <div class="bn-acc-detail">
        <div class="bn-acc-hypo">Desktop ③→④ 転換率 27.53% vs 31.92% ベースライン（-4.39pp）。767Kセッション/月。Desktopでカレンダー閲覧後にフォームに進まない。</div>
        <a class="bn-acc-link" href="/bottleneck.html?week=2026-w13&num=7">詳細分析を見る →</a>
      </div>
    </div>

    <div class="bn-acc-item">
      <div class="bn-acc-header" onclick="toggleBnAcc(this)">
        <div class="bn-acc-rank">#8</div>
        <div class="bn-acc-body">
          <div class="bn-acc-title">Europeエリア — ③→④ 意向転換率の低さ</div>
          <div class="bn-acc-tags"><span class="bn-acc-tag red">③→④ 検討→意向</span><span class="bn-acc-tag">Europeエリア</span></div>
        </div>
        <div class="bn-acc-meta"><div class="bn-acc-gap-label">全体比乖離</div><div class="bn-acc-gap">-67%</div></div>
        <div class="bn-acc-chevron">▶</div>
      </div>
      <div class="bn-acc-detail">
        <div class="bn-acc-hypo">Europeエリア ③→④ 転換率 10.57% vs 31.92% ベースライン（-21.35pp）。143Kセッション/月。ヨーロッパアクティビティでカレンダー→フォーム転換が最も低い。</div>
        <a class="bn-acc-link" href="/bottleneck.html?week=2026-w13&num=8">詳細分析を見る →</a>
      </div>
    </div>

    <div class="bn-acc-item">
      <div class="bn-acc-header" onclick="toggleBnAcc(this)">
        <div class="bn-acc-rank">#9</div>
        <div class="bn-acc-body">
          <div class="bn-acc-title">沖縄エリア — ③→④ 意向転換率の低さ</div>
          <div class="bn-acc-tags"><span class="bn-acc-tag red">③→④ 検討→意向</span><span class="bn-acc-tag">沖縄エリア</span></div>
        </div>
        <div class="bn-acc-meta"><div class="bn-acc-gap-label">全体比乖離</div><div class="bn-acc-gap">-54%</div></div>
        <div class="bn-acc-chevron">▶</div>
      </div>
      <div class="bn-acc-detail">
        <div class="bn-acc-hypo">沖縄エリア ③→④ 転換率 14.72% vs 31.92% ベースライン（-17.20pp）。197Kセッション/月。沖縄アクティビティはセッション数が多いがカレンダー→フォームの壁が高い。</div>
        <a class="bn-acc-link" href="/bottleneck.html?week=2026-w13&num=9">詳細分析を見る →</a>
      </div>
    </div>

    <div class="bn-acc-item">
      <div class="bn-acc-header" onclick="toggleBnAcc(this)">
        <div class="bn-acc-rank">#10</div>
        <div class="bn-acc-body">
          <div class="bn-acc-title">WoW全段階悪化 — 前週比継続的マイナス</div>
          <div class="bn-acc-tags"><span class="bn-acc-tag red">全ステップ悪化</span><span class="bn-acc-tag">WoW比較</span></div>
        </div>
        <div class="bn-acc-meta"><div class="bn-acc-gap-label">最大悪化</div><div class="bn-acc-gap">-1.2pp</div></div>
        <div class="bn-acc-chevron">▶</div>
      </div>
      <div class="bn-acc-detail">
        <div class="bn-acc-hypo">全4段階がWoW悪化: ①→②:-0.62pp, ②→③:-0.19pp, ③→④:-1.20pp, ④→⑤:-1.05pp。712Kセッション/月。外部要因（季節・競合イベント）または内部変更の影響を確認する必要がある。</div>
        <a class="bn-acc-link" href="/bottleneck.html?week=2026-w13&num=10">詳細分析を見る →</a>
      </div>
    </div>

  </div>
</div>

<!-- ======================== FOOTER ======================== -->
<div class="card">
  <div class="footer">
    <span>VELTRA CVR改善チーム — UIUX Design Squad</span>
    <span><a href="https://analytics.google.com/analytics/web/#/p347074845/reports/reportinghub" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline">GA4: 347074845</a></span>
    <span>2026-04-07</span>
  </div>
</div>

<script src="/nav.js"></script>
<script src="/funnel-def.js"></script>
<script>
function toggleBnAcc(header) {
  var item = header.parentElement;
  var isOpen = item.classList.contains('open');
  item.classList.toggle('open', !isOpen);
}
</script>
</body>
</html>
"""

# Write the file
with open('/home/user/v2-veltra-cvr/reports/2026-w13/index.html', 'w') as f:
    f.write(html)

print(f"W13 index.html written successfully ({len(html)} chars)")
