# CLAUDE.md — veltra-theme-lp 開発ガイド（セッション引き継ぎ用）

> **新しいセッション開始時に必ずこのファイルを読むこと。**
> このリポジトリは「ジャンル特集LP（スポーツ／演劇…）」を量産する静的サイト基盤。
> 第1弾として **野球LP** を実装済み。元の制作は `SDkotarom/v2-veltra-cvr` で行い、本リポへ移植した。

---

## 0. このプロジェクトは何か

- 各ジャンルのVeltra AC（アクティビティ）を集約した**静的ランディングページ**群
- S3 にデプロイ → 既存 `dev.veltra.com` / `www.veltra.com` の CloudFront 経由、**`/jp/lp/` 配下**で配信
- `main` にマージ → **GitHub Actions が自動デプロイ**（Actionsタブで結果確認）

### 開発フロー（厳守）
1. ブランチを切る（`add-xxx` 等）
2. `src/` 配下を編集
3. push → **Pull Request** 作成（main直pushは非推奨）
4. レビュー → マージ → GitHub Actions 自動デプロイ
5. Actions が緑✅ を確認

---

## 1. ディレクトリ設計

`src/` を公開ルートとし、`common（全テーマ共通）` / `<theme>` / `<page>` の3層。

```
src/
├─ common/                      # 全テーマ横断
│  ├─ css/   （2ページ目以降に共通CSSを抽出）
│  ├─ js/    （2ページ目以降に共通JSを抽出）
│  └─ img/   logo, favicon×3, ogp, icon_merit×3
├─ sports/
│  ├─ assets/img/               # スポーツ横断で使う画像
│  └─ baseball/
│     ├─ index.html             # 野球LP（実装済み）
│     └─ assets/img/  hero-stadium.jpg / -s.jpg
└─ theater/ …                   # 将来、同じ構造で展開
```

### ページ追加ルール
| 追加対象 | 置き場所 |
|---|---|
| 新ジャンル | `src/<theme>/<page>/index.html` + 同階層 `assets/img/` |
| スポーツ新競技 | `src/sports/<sport>/index.html` |
| ジャンル下層 | `src/<theme>/<page>/<sub>/index.html` |
| 全体共通画像 | `src/common/img/` |
| 共通CSS/JS（2ページ目〜） | `src/common/css/`・`src/common/js/` に抽出 |

---

## 2. パスの注意（重要・デプロイ依存）

- 配信が **`/jp/lp/` 配下**のため、画像等の**ルート相対パスは要検証**。
- 現状 index.html は `/common/...`, `/sports/baseball/...` で記述。
  - もし `src/` が `/jp/lp/` にマッピングされる場合、`/jp/lp/common/...` へ要修正、または相対パスへ。
- **初回デプロイ後に画像が404なら**、`.github/workflows/deploy.yml` の `s3 sync` 先パスを確認して調整する。
- OGP/Twitter画像は `/common/img/veltraogp.png`。本番ドメイン確定後に**絶対URL化**推奨（クローラ対策）。

---

## 3. デザイン制作ルール（v2-veltra-cvr から継承・絶対遵守）

### Figma忠実化
- 「Figma通りに」と言われたら **必ず Figma MCP で実値を引いてから実装**。「それっぽく」「常識で」当てない。
- コンポーネント単位で nodeId を取得 → `get_design_context` で実値（border-radius / padding / font-weight / 色 / line-height / line-clamp）を取得 → 項目単位で差分を潰す。
- EC常識（例：価格はピンクで目立たせ）で勝手に補完しない。Figmaの設計意図を尊重。

### 用語・表記
| 項目 | 決定 |
|---|---|
| サービス名 | **Veltra**（表記揺れ禁止） |
| ユーザー主語 | **Traveler** |
| 最小フォント | 13px 以上（モック内UI再現を除く） |
| デザイン | ライトテーマ（白背景）。ダーク/コンサル風NG |

### デザイントークン（baseball/index.html 内で定義済み）
- `--ink:#484848` / `--ink-2:#7F7F7F` / `--line:#DADADA` / `--blue:#0077D9` / `--blue-dark:#376DAB` / `--blue-soft:#EFF4FA` / `--pink:#E4336B`
- **絞り込みチップ選択時** = Figma Chip(380-3546)準拠：bg `--blue-soft` / border・text `--blue-dark` / 通常太さ
- **主要CTA（絞り込み結果ボタン等）** = `--blue`（#0077D9）

---

## 4. Veltra AC データ取得ノウハウ（重要）

### MCP（Veltra AC Search）
- **PROD のみ使用**（DEVは本番データ無し）。`searchActivities` で keyword 検索（PRODは1回1回の承認不要に設定済み）。
- 売れ筋上位しか返らず、ランキング圏外ACは surface しないことがある。

### MCPの限界（手動取得が必要なケース）
- **価格**: MCPは AC一次通貨（USD/AUD/TWD/CAD）で返す。**Veltra JP表示の実JPYは取得不可**（固定レート換算では数十円ズレる）。
- **評価**: MCPの `rating` は10点満点・1桁丸め。`/2` して四捨五入しても**実表示の小数2桁（例 4.24）には戻らない**。
- → 正確な「最安値JPY・★評価2桁・体験談数」は**実ページから手動取得**してユーザーが提供する運用。
- カードの★表示は `toFixed(2)`。

### タイトル/画像
- AC タイトル・サムネ画像URLは MCP の値（公式表記）に合わせる。全角スペース等の表記揺れに注意。

---

## 5. GA4 / GTM 計測設計（実装済み・汎用）

- `LP_CONFIG = { lp_id, lp_genre, lp_name }` を各ページ先頭で定義（**ページ固有**）。
- `trackEvent(name, payload)` が全イベントに `lp_id / lp_genre / lp_name / page_path` を自動付与。
  - → GA4で **`lp_id=baseball` フィルタ＝そのページ単独の成績**、`lp_id`で group by＝全LP横断比較。
- 計測イベント（12種）: `lp_view` / `section_view`(IO) / `ac_click`(pickup,grid) / `filter_apply`(pc,mobile,modal,active_chip) / `filter_modal_open`/`close` / `filter_clear` / `sort_change` / `load_more` / `header_link_click` / `footer_link_click`。
- `data-event` + `data-payload` 属性を click delegation で吸い上げ。
- 絞り込みセット集計: `buildFilterSnapshot()` が `active_filter_signature` 等を生成。
- GTM: `GTM-5KFX5VX`。Event タグは Universal 1個で `event` 名と `event_payload` を動的展開。
- 設計詳細は v2-veltra-cvr の `planning/sports-mock/baseball/spec-and-tracking.md` 参照。

---

## 6. 野球ページ実装メモ（現状の仕様）

- 構成: Header → Breadcrumb → Hero(PC/SP別画像,768px切替) → Reasons → Pickup(固定4枚) → Tours(絞り込み+ソート+グリッド+もっと見る) → Guide(テキスト4枚) → FAQ(開閉なし) → Footer
- Pickup固定ID: `183789 / 192599 / 203447 / 193811`（大谷ドジャース主役）
- 絞り込み: city / team / cat の3軸（軸内OR・軸間AND）。SPはモーダル（主要+「もっと見る」展開）。
- ソート: recommend(=ACS宣言順) / rating / price-asc / price-desc
- モーダル: 右上「条件をクリア」+×、本文先頭タイトル、下部「{N}件の結果を表示」
- フッター: campaign.veltra.com 準拠（ロゴ40px、リンク#262626、コピーライト#000）

---

## 7. 関連リソース

- 元リポジトリ: `SDkotarom/v2-veltra-cvr`（`planning/sports-mock/baseball/` に原本、`planning/veltra-theme-lp-*` に設計書・移行バンドル）
- 設計書: `planning/veltra-theme-lp-DIRECTORY-DESIGN.md`
- 計測設計: `planning/sports-mock/baseball/spec-and-tracking.md`
- GA4 Property: `347074845` / GTM: `GTM-5KFX5VX`

---

## 8. 次にやること候補

- [ ] 初回デプロイ後の**画像パス検証**（/jp/lp/ 問題）
- [ ] GTMコンテナ設定（dataLayer→GA4変換）+ GA4カスタムディメンション登録
- [ ] 2ページ目着手時に common/css・common/js へ共通部抽出
- [ ] 14枚の未照合AC（rating null表示）の実値反映（手動取得）
