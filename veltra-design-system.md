# VELTRA デザインルール v2（現行サイト準拠）

> **目的**: Claude Code がプロトタイプを生成する際、現行 VELTRA サイト（veltra.com/jp）のルック＆フィールを正確に再現するためのリファレンス。  
> **対象**: SP（モバイル）+ PC　全ページタイプ・全ファネル  
> **更新**: 2026年4月 / SP・PCスクリーンショット全ファネル + 戦略ガイド（2026年度版）に基づく

---

## 1. カラーシステム

### 1.1 パレット定義

#### ブランドカラー
| 用途 | カラー名 | HEX | CSS変数 |
|------|----------|-----|---------|
| プライマリ（CTA・リンク） | ビビッドブルー | `#1B82C5` | `--color-primary` |
| プライマリ（ホバー/ダーク） | ダークブルー | `#1570A8` | `--color-primary-dark` |
| プライマリ（薄背景） | ライトブルー | `#F0F7FC` | `--color-primary-light` |
| プライマリ（ボーダー） | ペールブルー | `#D0E8F7` | `--color-primary-border` |
| アクセント（価格・割引） | ストロングレッド | `#D91F26` | `--color-price` |
| 告知バー・キャンペーン | ホットピンク | `#E8386E` | `--color-campaign` |
| 評価・コーラル | コーラルレッド | `#E94B5A` | `--color-accent` |
| 即予約可能・成功 | グリーン | `#2DAE6C` | `--color-success` |
| 警告・残りわずか | オレンジ | `#F57C00` | `--color-warning` |
| 星評価 | ゴールデンイエロー | `#FFAA00` | `--color-rating` |

#### ニュートラル
| 用途 | HEX | CSS変数 |
|------|-----|---------|
| ページ背景 | `#F2F5F8` | `--color-bg-page` |
| カード・モーダル背景 | `#FFFFFF` | `--color-bg-card` |
| セクション背景（薄色） | `#F0F7FC` | `--color-bg-section` |
| フッター背景 | `#F5F5F5` | `--color-bg-footer` |
| 本文テキスト | `#333333` | `--color-text-primary` |
| サブテキスト | `#666666` | `--color-text-secondary` |
| 補助テキスト | `#999999` | `--color-text-tertiary` |
| ボーダー・区切り線 | `#E0E0E0` | `--color-border` |
| インプットボーダー | `#CCCCCC` | `--color-border-input` |

### 1.2 カラー運用ルール

- **CTAは常にブルー `#1B82C5`**。ピンク・レッドをボタンに使わない
- **価格・割引率はレッド `#D91F26`**。ブルーを価格に使わない
- **告知バーのホットピンク `#E8386E`** はグローバルナビ最上部限定。コンテンツエリアには使わない
- **背景色**は `#FFFFFF` と `#F2F5F8` を交互に使いセクション境界を示す
- **リンクテキスト**はブルー `#1B82C5`。下線なし。ホバー時に下線
- **セクション背景の薄ブルー `#F0F7FC`** はプラン情報・インフォメーションブロック等に限定使用

---

## 2. タイポグラフィ

### 2.1 フォントファミリー

```css
/* 日本語 */
font-family: "Hiragino Kaku Gothic ProN", "Hiragino Sans", "Meiryo", sans-serif;

/* 数字・英字（価格・評点） */
font-family: "Helvetica Neue", Arial, sans-serif;
```

### 2.2 フォントサイズスケール

| 役割 | サイズ | Weight | CSS変数 |
|------|--------|--------|---------|
| メタ・キャプション | 11px | 400 | `--text-xs` |
| パンくず・フッター | 12px | 400 | `--text-sm` |
| 本文・カード商品名 | 13–14px | 400 / 700 | `--text-base` |
| ボタンラベル | 14–16px | 700 | `--text-md` |
| 価格（大） | 16–18px | 700 | `--text-lg` |
| セクション見出し（h2） | 18–20px | 700 | `--text-xl` |
| ページ大見出し（h1） | 24px (PC: 24–28px) | 700 | `--text-2xl` |

### 2.3 行間・字間

| コンテキスト | line-height | letter-spacing |
|-------------|-------------|----------------|
| 本文 | 1.6 | default |
| 見出し | 1.3 | default |
| ボタン | 1.2 | default |

---

## 3. スペーシング

### 3.1 基本単位: 4px

| トークン | 値 | CSS変数 | 主な用途 |
|---------|-----|---------|---------|
| 1 | 4px | `--space-1` | アイコンとテキストの間 |
| 2 | 8px | `--space-2` | コンポーネント内最小余白 |
| 3 | 12px | `--space-3` | カード内パディング、カード間ギャップ |
| 4 | 16px | `--space-4` | ページ左右パディング（PC） |
| 5 | 20px | `--space-5` | 中間余白 |
| 6 | 24px | `--space-6` | セクション間マージン（SP） |
| 8 | 32px | `--space-8` | セクション間マージン（PC） |

---

## 4. グリッド・レイアウト

### 4.1 ブレークポイント

```css
/* SP */ max-width: 767px
/* PC */ min-width: 768px
```

### 4.2 PC レイアウト

| 項目 | 値 | CSS変数 |
|------|-----|---------|
| コンテンツ最大幅 | 960–1020px | `--max-width` |
| サイドバー幅（Ctg絞り込み） | 200–220px | `--sidebar-width` |
| 予約サマリーサイドバー幅 | 240–260px | `--booking-sidebar-width` |
| カード間ギャップ | 12–16px | — |
| ページ左右パディング | 16–24px | `--page-padding` |

### 4.3 SP レイアウト

| 項目 | 値 | CSS変数 |
|------|-----|---------|
| フルワイド左右パディング | 12–16px | `--sp-page-padding` |
| カルーセルカード幅 | 150–160px | `--sp-carousel-card-width` |
| リストカード画像幅（固定） | 120px | `--sp-card-image-width` |
| スティッキーフッター高さ | 64px | `--sp-sticky-footer-height` |
| タブ高さ | 44px | `--sp-tab-height` |

---

## 5. コンポーネント仕様

### 5.1 ボタン

#### プライマリCTA
```css
.btn-primary {
  background-color: #1B82C5;
  color: #FFFFFF;
  border-radius: 4px;
  padding: 12px 20px;
  font-size: 15px;
  font-weight: 700;
  border: none;
  width: 100%;
}
.btn-primary:hover { background-color: #1570A8; }
```

#### セカンダリ（アウトライン）
```css
.btn-secondary {
  background-color: #FFFFFF;
  color: #1B82C5;
  border: 1px solid #1B82C5;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 13px;
}
```

### 5.2 商品カード

#### SP カテゴリページ（リスト表示）
- 左画像固定幅 **120px**、右テキストエリアは残り全幅
- カード間: `border-bottom: 1px solid #E0E0E0`（シャドウなし）

#### SP カルーセル
- カード幅: **150–160px**固定、`aspect-ratio: 3/2`
- `scroll-snap-type: x mandatory`
- シャドウ: `0 1px 4px rgba(0,0,0,0.12)`

#### ランキングカード
- 順位バッジ: 1–3位ピンク背景、4位以降グレー、`border-radius: 50%`

### 5.3 カレンダー（日付選択）

```css
/* 選択可能 */
border: 1px solid #1B82C5; color: #1B82C5;

/* 選択済み */
background-color: #1B82C5; color: #FFFFFF;

/* 選択不可 */
color: #CCCCCC; border-color: transparent;
```

### 5.4 数量セレクター（人数選択）

```css
/* ＋/−ボタン（アクティブ） */
background-color: #1B82C5; color: #FFFFFF;
border-radius: 50%; width: 32px; height: 32px;

/* −ボタン（数量=0：非アクティブ） */
background-color: #CCCCCC;

/* 価格（行内） */
color: #D91F26; font-weight: 700;
```

### 5.5 フォーム要素

```css
.form-input {
  border: 1px solid #CCCCCC;
  border-radius: 4px;
  padding: 10px 12px;
  font-size: 14px;
  color: #333333;
}
.form-input:focus {
  border-color: #1B82C5;
  box-shadow: 0 0 0 2px rgba(27,130,197,0.2);
}
```

#### 絞り込みチップ（トグル）
```css
/* 未選択 */
border: 1px solid #CCCCCC; border-radius: 4px;
padding: 6px 12px; font-size: 13px; color: #333;

/* 選択済み */
border-color: #1B82C5; color: #1B82C5; background: #F0F7FC;
```

### 5.6 ナビゲーション

#### グローバルヘッダー（SP）
```
┌─────────────────────────────────────────┐
│ [告知バー: #E8386E 背景]                 │
├─────────────────────────────────────────┤
│ ☰       VELTRA ロゴ（中央）        🔍 👤 │  ← 高さ約50px / 背景#FFFFFF
│ [カテゴリタブ: 横スクロール]              │
└─────────────────────────────────────────┘
```
- ロゴ: **中央配置**（SPのみ）

### 5.7 タブ
- アクティブ: `border-bottom: 2px solid #1B82C5`、テキスト `#1B82C5`、Bold
- 非アクティブ: `color: #666`
- 高さ: 44px（SP）

### 5.8 バッジ・ラベル

```css
/* 割引バッジ */
background: #D91F26; color: #FFF;
font-size: 11px; padding: 2px 6px; border-radius: 2px;

/* 即予約確定 */
background: #2DAE6C; color: #FFF;
font-size: 11px; padding: 2px 6px; border-radius: 2px;

/* カテゴリタグ（ピル型） */
background: #F0F7FC; color: #1B82C5;
border: 1px solid #D0E8F7;
font-size: 12px; padding: 4px 10px; border-radius: 20px;
```

### 5.9 スティッキーフッター（SP ACページ）
```css
position: fixed; bottom: 0; left: 0; right: 0;
background: #FFFFFF; border-top: 1px solid #E0E0E0;
padding: 10px 16px; height: 64px;
display: flex; align-items: center; gap: 12px;
```
- 左: 価格（`font-size: 16px; font-weight: 700`）
- 右: 「今すぐ予約する」ボタン（プライマリCTA）

### 5.10 評価（スター）
```css
color: #FFAA00; font-size: 13px; /* 星 */
color: #333; font-weight: 700;   /* 評点 */
color: #666; font-size: 12px;    /* 件数 */
```

---

## 6. インタラクション・状態定義

| 状態 | 表現 |
|------|------|
| ホバー（ボタン） | `#1570A8` |
| フォーカス（入力） | `border-color: #1B82C5` + `box-shadow: 0 0 0 2px rgba(27,130,197,0.2)` |
| アクティブ（タブ） | `border-bottom: 2px solid #1B82C5`、テキスト `#1B82C5` |
| 非アクティブ | `color: #999; opacity: 0.5` |

### タップターゲットサイズ（SP）
- **最小タップターゲット: 44×44px**

---

## 7. 施策判断の禁則（2025年ABテストの知見）

### ❌ やってはいけない（負けパターン）
- 情報の追加でノイズを増やす（ハイライト追加、ランキングナビ追加）
- ページの役割外の情報を置く
- 細部だけの変更（ボタン色・テキストのみ）
- 比較対象を増やす（迷いの増大）

### ✅ やるべき（勝ちパターン）
- 情報の引き算・シンプル化（ハイライト非表示 +3.8%、タブ化 +2%で実証済）
- 並走型UI（タブで整理）
- 視認性の向上（コントラスト確保、CTAの明確化）
- ページ役割の純化

### ページ役割定義
| ページ | 役割 | 出すべき情報 | 出してはいけない |
|--------|------|-------------|----------------|
| Area/Top | 大づかみ | エリアの魅力・カテゴリ構造 | 追加ナビゲーション |
| Ctg（一覧） | 候補を絞る | 比較情報・価格・評価・フィルタ | プラン詳細の先出し |
| Ac（詳細） | 不安解消・確信 | スケジュール・料金・体験談 | 過剰な関連商品 |
| Booking form | 迷わず完了 | 最小限フィールド・明確CTA | 追加商品提案 |

---

## 8. CSS変数テンプレート（コピペ用）

```css
:root {
  --color-primary: #1B82C5;
  --color-primary-dark: #1570A8;
  --color-primary-light: #F0F7FC;
  --color-primary-border: #D0E8F7;
  --color-accent: #E94B5A;
  --color-campaign: #E8386E;
  --color-price: #D91F26;
  --color-success: #2DAE6C;
  --color-warning: #F57C00;
  --color-rating: #FFAA00;

  --color-bg-page: #F2F5F8;
  --color-bg-card: #FFFFFF;
  --color-bg-section: #F0F7FC;
  --color-bg-footer: #F5F5F5;
  --color-text-primary: #333333;
  --color-text-secondary: #666666;
  --color-text-tertiary: #999999;
  --color-text-link: #1B82C5;
  --color-border: #E0E0E0;
  --color-border-input: #CCCCCC;

  --font-jp: "Hiragino Kaku Gothic ProN", "Hiragino Sans", "Meiryo", sans-serif;
  --font-en: "Helvetica Neue", Arial, sans-serif;

  --radius-sm: 4px;
  --radius-pill: 20px;
  --shadow-card: 0 1px 4px rgba(0,0,0,0.12);
  --shadow-modal: 0 4px 20px rgba(0,0,0,0.15);

  --sp-sticky-footer-height: 64px;
  --sp-tab-height: 44px;
  --sp-touch-target: 44px;
}
```

---

## 9. Claude Code 向けクイックリファレンス

### プロンプトに含める一文:
```
VELTRAの現行デザインルール（veltra-design-system.md）に従うこと。
プライマリ #1B82C5、ページ背景 #F2F5F8、カード背景 #FFFFFF、価格 #D91F26。
フォントは "Hiragino Kaku Gothic ProN", sans-serif。
タップターゲットは最小44×44pxを確保。
情報の引き算を優先し、ページの役割から外れる要素は追加しない。
```

### プロトタイプ出力時チェックリスト:
- [ ] CTAボタンはブルー `#1B82C5`、`border-radius: 4px`
- [ ] 価格表示はレッド `#D91F26` で太字
- [ ] カレンダーの予約可能日はブルー枠
- [ ] SPではスティッキーフッター（価格+CTA）が画面下部固定
- [ ] フォーム必須項目に赤い `*`（`#D91F26`）
- [ ] SPタップターゲットが44px以上
- [ ] ページの役割外の情報を追加していない

### やってはいけないこと:
- ❌ ボタンにピンク/レッドを使う（価格・割引専用）
- ❌ 影を強くする（`0 1px 4px` 程度に抑える）
- ❌ セクション背景に多色使用（白 or `#F2F5F8` のみ）
- ❌ 装飾的アニメーション
- ❌ 情報の追加でノイズを増やす

---

*v2 / 2026年4月 / veltra.com/jp 現行サイト準拠*
