# veltra-theme-lp ディレクトリ設計

> **対象リポジトリ**: https://github.com/veltra/veltra-theme-lp
> **目的**: ジャンル特集LP（スポーツ／演劇…）を増やしていく前提の、拡張に強いディレクトリ構成。
> **現状**: 野球LP 1ページのみ。今のうちに骨格だけ用意する。

---

## 1. 想定する将来像

```
スポーツ特集
 ├ 野球（今回のページ）
 │  └ 野球の下層コンテンツ（増える可能性）
 └ サッカー / F1 ...
演劇特集
 └ ...
```

→ **3層構造**で吸収する: `common（全テーマ共通）` / `<theme>（テーマ共通）` / `<page>（ページ固有）`

---

## 2. ディレクトリ構成

`src/` を**公開ルート**として扱う（パスはルート相対 `/...`。ページ階層が深くなっても壊れない）。

```
src/
├─ common/                      # 全テーマ横断の共通リソース
│  ├─ css/
│  │  └─ .gitkeep               # 将来: base.css（トークン/リセット/共通UI）
│  ├─ js/
│  │  └─ .gitkeep               # 将来: tracking.js（GA4共通ヘルパー）
│  └─ img/
│     ├─ logo_a1_jp-1.png       # Veltraロゴ
│     ├─ favicon-16x16.png
│     ├─ favicon-32x32.png
│     ├─ apple-touch-icon.png
│     ├─ veltraogp.png          # 既定OGP
│     └─ icon_merit_1〜3.png    # 予約メリットアイコン ※暫定common（後でsports移動可）
│
├─ sports/                      # スポーツ特集
│  ├─ assets/img/               # スポーツ横断で使い回す画像（現状は空 / .gitkeep）
│  └─ baseball/                 # 野球
│     ├─ index.html             # 野球トップ（今回のページ）
│     └─ assets/img/
│        ├─ hero-stadium.jpg
│        ├─ hero-stadium-s.jpg
│        └─ img_guide_1〜4.png
│     # 将来: baseball/teams/ など下層ページを追加可
│
└─ theater/                     # 演劇特集（将来・同じ構造で展開）
   └─ ...
```

---

## 3. アセット振り分け

| ファイル | 行き先 |
|---|---|
| logo_a1_jp-1.png | `src/common/img/` |
| favicon-16x16 / -32x32 / apple-touch-icon | `src/common/img/` |
| veltraogp.png | `src/common/img/` |
| icon_merit_1〜3.png | `src/common/img/`（暫定。スポーツ専用と判明したら sports へ） |
| hero-stadium.jpg / hero-stadium-s.jpg | `src/sports/baseball/assets/img/` |
| img_guide_1〜4.png | `src/sports/baseball/assets/img/` |

---

## 4. パス書き換え（現 v2-veltra-cvr → veltra-theme-lp）

現状 `../assets/img/xxx`（相対）→ **ルート相対**へ。

| 現状 | 新 |
|---|---|
| `../assets/img/logo_a1_jp-1.png` | `/common/img/logo_a1_jp-1.png` |
| `../assets/img/favicon-16x16.png` | `/common/img/favicon-16x16.png` |
| `../assets/img/favicon-32x32.png` | `/common/img/favicon-32x32.png` |
| `../assets/img/apple-touch-icon.png` | `/common/img/apple-touch-icon.png` |
| `../assets/img/icon_merit_1.png`（〜3） | `/common/img/icon_merit_1.png`（〜3） |
| `../assets/img/hero-stadium.jpg` | `/sports/baseball/assets/img/hero-stadium.jpg` |
| `../assets/img/hero-stadium-s.jpg` | `/sports/baseball/assets/img/hero-stadium-s.jpg` |
| `../assets/img/img_guide_1.png`（〜4） | `/sports/baseball/assets/img/img_guide_1.png`（〜4） |
| CSS内 `url("../assets/img/hero-stadium*.jpg")` | `url("/sports/baseball/assets/img/hero-stadium*.jpg")` |
| OGP/Twitter の絶対URL `https://v2-veltra-cvr.vercel.app/.../veltraogp.png` | デプロイ先ドメインに合わせ `/common/img/veltraogp.png`（または新ドメインの絶対URL） |

> ⚠️ ルート相対は **`src/` が配信ルート**である前提。サブパス配信なら相対パスへ要調整。

---

## 5. CSS/JS 共通化は「2ページ目」まで保留

- 今は野球1ページなので **インライン `<style>`/`<script>` のまま**にする（1ページで共通化は過剰設計）。
- `common/css/`・`common/js/` は **空の置き場（.gitkeep）だけ先に用意**。
- **2ページ目を作るタイミング**で、共通部（デザイントークン・リセット・GA4 `trackEvent`・フィルタ共通ロジック）を `common/` へ抽出する。
- GA4 の `LP_CONFIG`（lp_id 等）は**ページ固有**なので各 index.html に残す。共通の `trackEvent` だけ `common/js/tracking.js` に出す想定。

---

## 6. 移行コマンド（参考・veltra-theme-lp の clone 内で実行）

`$SRC` = v2-veltra-cvr の `planning/sports-mock` への絶対パス。

```bash
# ディレクトリ作成
mkdir -p src/common/img src/common/css src/common/js
mkdir -p src/sports/assets/img
mkdir -p src/sports/baseball/assets/img
touch src/common/css/.gitkeep src/common/js/.gitkeep src/sports/assets/img/.gitkeep

# common 画像
cp "$SRC"/assets/img/{logo_a1_jp-1.png,favicon-16x16.png,favicon-32x32.png,apple-touch-icon.png,veltraogp.png,icon_merit_1.png,icon_merit_2.png,icon_merit_3.png} src/common/img/

# 野球固有 画像
cp "$SRC"/assets/img/{hero-stadium.jpg,hero-stadium-s.jpg,img_guide_1.png,img_guide_2.png,img_guide_3.png,img_guide_4.png} src/sports/baseball/assets/img/

# HTML 配置
cp "$SRC"/baseball/index.html src/sports/baseball/index.html

# パス書き換え（index.html）
cd src/sports/baseball
sed -i \
 -e 's#\.\./assets/img/logo_a1_jp-1.png#/common/img/logo_a1_jp-1.png#g' \
 -e 's#\.\./assets/img/favicon-16x16.png#/common/img/favicon-16x16.png#g' \
 -e 's#\.\./assets/img/favicon-32x32.png#/common/img/favicon-32x32.png#g' \
 -e 's#\.\./assets/img/apple-touch-icon.png#/common/img/apple-touch-icon.png#g' \
 -e 's#\.\./assets/img/icon_merit_#/common/img/icon_merit_#g' \
 -e 's#\.\./assets/img/hero-stadium#/sports/baseball/assets/img/hero-stadium#g' \
 -e 's#\.\./assets/img/img_guide_#/sports/baseball/assets/img/img_guide_#g' \
 index.html
```

> ※OGP/Twitterのmetaにある `https://v2-veltra-cvr.vercel.app/planning/sports-mock/assets/img/veltraogp.png` は、デプロイ先ドメイン確定後に手動で差し替え。

---

## 7. 今後ページを増やすときのルール

| 追加対象 | 置き場所 |
|---|---|
| 新ジャンル（演劇等） | `src/theater/<page>/index.html` + `src/theater/<page>/assets/img/` |
| スポーツ新競技（サッカー等） | `src/sports/soccer/index.html` + `src/sports/soccer/assets/img/` |
| 野球の下層ページ | `src/sports/baseball/<sub>/index.html` |
| 複数ページ共通の画像 | テーマ共通=`src/<theme>/assets/`、全体共通=`src/common/img/` |
| 共通CSS/JS（2ページ目以降） | `src/common/css/`, `src/common/js/` に抽出 |
