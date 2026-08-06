# web-performance ｜ ClickUp 起票ガイド

レイテンシー改善プロジェクト（proj-web-performance）のタスクを ClickUp に積むときのルールとテンプレ集。
CVR リストの既存チケットから型を抽出したもの。**新規起票時はこのガイドに沿う。**

関連：プロジェクトページ `/2026h2/projects/latency.html`（背景・調査方法・着手優先度）／ Slack `#proj-web-performance`

---

## 1. 起票先リスト

| 項目 | 値 |
|------|----|
| リスト名 | **web-performance** |
| list_id | `901820239496` |
| Space | UX Design Squad (`901810555568`) |
| URL | https://app.clickup.com/31108037/v/l/li/901820239496 |

**ステータス遷移**：
`to do` → `planning` → `in progress` →（必要に応じ `at risk` / `update required` / `on hold`）→ `complete`（中止は `cancelled`）

- 実装前の調査・仕様詰め段階＝ `planning`
- 未着手のバックログ＝ `to do`

参考リスト（同チームの使い方の見本）：**CVR** `901817269796`（UX_DESIGN-** チケット群）

---

## 2. 命名規則

- 形式：`[Perf] 日本語タイトル / English title`
- **日英併記**（海外エンジニア Piotr 等も読むため。参考チケットも全て併記）
- プレフィックス `[Perf]` で web-performance 案件を識別（CVR リストの `[CVR]` に相当）
- タイトルは「何をするか」を動詞で。数値は本文へ（タイトルに詰め込まない）

例：
- `[Perf] 未使用 GTM/計測タグの削除 / Remove unused GTM & tracking tags`
- `[Perf] LCP 画像 preload を残りページへ展開 / Extend LCP image preload to remaining pages`
- `[Perf] img に width/height 付与（CLS対策）/ Add width/height to <img> for CLS`

---

## 3. チケットの型（用途別 3 パターン）

用途に応じて A / B / C を使い分ける。見出しはすべて **日本語 / English 併記**、
完了条件・受け入れ要件は **チェックボックス**、末尾に **関連リンク** を必ず置く。

### 型A：調査チケット（Survey & Investigation）
実態がまだ割れていないものを「まず測る」ためのチケット。Quick Win 実装前の原因切り分け向き。
（見本：UX_DESIGN-167 [Reduce Loading Time on Category Pages and Booking Modal](https://app.clickup.com/t/86exabgp7)）

```markdown
## 背景・目的 / Background & Purpose
なぜ調べるか。どのデータ/ボトルネックが起点か（例：BN3 Mobile ①→② = 月2,076K）。
本チケットは調査フェーズ。結果をもとに実装チケットを別途起票する旨を明記。

## 調査対象 / Investigation Targets
対象ページ・操作を列挙。**調査の起点URLを必ず貼る**（例：カテゴリページ実URL）。

## 調査スコープ / Investigation Scope
### 1. 原因切り分け / Root Cause Isolation
- サーバー応答（API/DB/キャッシュ）/ クライアント処理（再レンダー）/ ネットワーク / 重複コール …
### 2. 改善可能性の洗い出し / Identifying Improvements
- デバウンス / オプティミスティックUI / スケルトン / キャッシュ戦略 …

## 完了条件 / Definition of Done
- [ ] ロード時間ボトルネックがレポート化（主要処理の内訳・所要時間）
- [ ] 原因カテゴリの特定（server / client / network / cache）
- [ ] 低工数（S〜M）で試せる改善案のリスト化
- [ ] 即実装可能なものは本チケット内で対応、他は別チケット化

## 優先度・エフォート / Priority & Effort
優先度と、調査＝S〜M など。

## 関連 / References
ボトルネック分析・スプレッドシート・プロジェクトページ 等のリンク。
```

### 型B：施策 / A-B テスト（Initiative & Experiment）
効果検証を伴う改善。仮説→証拠→施策→指標→リスクの順。
（見本：UX_DESIGN-85 [Filter modal speed improvement](https://app.clickup.com/t/86ex94rpk)）

```markdown
## 概要 / Overview
何を、どのページ/操作で改善するか。スコープの前提（共通パーツか要確認 等）。

## 仮説 / Hypothesis
### 課題 / Problem
### 期待する成果 / Outcome

## 背景と証拠 / Background & Evidence
### 定量データ / Quantitative Data   ← GA4/GTM の数値を表で
### 定性データ / Qualitative Evidence ← 体感確認・競合比較

## 提案する施策 / Proposed Feature
### やること / What we build（解決策アイデアは複数可）
### ターゲット / Target（対象サイト JP/HA・デバイス・ページ）
### ユーザーストーリー / User Story
### 対象外 / Out of Scope

## 指標 / Metrics
| 種別 | 指標 | 現状値 | 目標値 |
| Success / Sub / Guardrail 行で。Guardrail（悪化させない指標）を必ず入れる。

## 計測方法 / Measurement（GA4/GTM のイベント・判定方法）
## 判定方法 / Evaluation（比較期間・判定日・判定基準）

## リスクと対策 / Risks & Mitigation
| リスク | 影響 | 対策 |

## 参考情報 / References
```

### 型C：開発依頼（Dev Request）
エンジニアへの実装依頼。仕様が固まっているもの。コード/DOM 例を添える。
（見本：UX_DESIGN-124 [Braze Content Cards スロット埋め込み](https://app.clickup.com/t/86exm6d6m)）

```markdown
### 概要 / Overview
何を実装するか。前提（既存SDK稼働中 等）と本チケットの対象範囲。

### 背景 / Background
なぜ必要か。現状の問題。

### 依頼事項 / Implementation Tasks
1. 具体的な作業（DOM追加・ロジック・イベント送信 …）
   - 必要ならコードブロックで例示（html / js）
   - **非破壊改修**なら「既存◯◯は全て保持」と明記

### 仕様詳細 / Specifications
CLS対策（ゼロ件時は高さ0で非表示）など、パフォーマンス観点の注意も明記。

### 受け入れ要件 / Acceptance Criteria
- [ ] 想定位置に要素が存在する
- [ ] 期待挙動を確認
- [ ] クロスブラウザ確認（Chrome / Safari / Firefox）

### 対象外 / Out of Scope
別チケット/別チームが対応する範囲を明記。
```

---

## 4. カスタムフィールド

新リスト web-performance には現状 **`Squad`（dropdown）** のみ設定済み。

- `Squad` は **UX Design** を選択（`dbbb6c46-4df6-48d8-bdec-7c5c5e4cae49`）

CVR リストにある以下のフィールド（Impact / Confidence&Ease / Urgency / Task Type / Device / Health / Release date 等）を
使いたい場合は、リストにフィールドを追加するか、**本文の「優先度・エフォート」節で ICE を表現**する。

**ICE の書き方（本文）**：`ICE = Impact × Confidence ÷ Effort`
- Impact：CVR/CWV への効き × 影響ページ規模（高/中/低）
- Effort：実装＋検証の人日（S ≦2 / M 3〜5 / L 1週間+）
- Confidence：効く見込み（1〜5）

---

## 5. 起票時の標準デフォルト（未指定時）

| 項目 | 既定値 |
|------|--------|
| プレフィックス | `[Perf]` |
| 言語 | 日英併記 |
| ステータス | `to do`（調査で即動くものは `planning`） |
| 担当 | 空（後で割当） |
| Squad | UX Design |

指示で上書き可。作成後は必ず custom_id と URL を報告する。

---

## 6. 着手優先度（Quick Win から）と起票の対応

`/2026h2/projects/latency.html` の「着手優先度」表と対応。まず 1〜3 を起票して着手する。

| # | 施策 | 推奨タイプ | 参照 |
|---|------|-----------|------|
| 1 | 未使用 GTM/計測タグの削除 | C（+一部A） | SEO-14 / SEO-177 / SEO-178 |
| 2 | LCP 画像 preload を残りページへ展開 | C | MKT-94 |
| 3 | img に width/height 付与（CLS） | C | SEO改善TASK シート |
| 4 | 画像 WebP化 + immutable Cache-Control | C | FS-320 |
| 5 | カテゴリの重い処理削減（メモ化/不要API削除） | A→C | UX_DESIGN-167 |
| 6 | Page cache Phase2（ETag展開） | C | CS24-4217 |
| 7 | 上流レイテンシー（Booking quote <1s） | B/A | New Platform P2 |

> 着手前に **Lighthouse CI / DevTools でベースラインを固定**（0番目）。効果は前後比較で測る。
