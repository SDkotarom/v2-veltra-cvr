---
name: competitor-teardown
description: 競合の予約フローをブラウザで（半自動で）実地調査し、旅行者ペイン5分類にマッピングして spot/ レポート（ライトボックス付き）を生成・PRするパイプライン。「競合調査」「競合の予約フローを撮って」「teardownを更新」などのときに使う。
---

# Competitor Booking-Flow Teardown（半自動パイプライン）

競合の「探す→比べる→決める→予約フォーム（支払い入力の手前）」を実地取得し、
`spot/traveler-pain-framework.html` のペイン5分類（手間/不安/待ち/分からない/裏切り）に沿って
分析し、`spot/2026-competitor-booking-teardown.html` 系のレポートを生成・PR する。

**役割分担**：巡回とスクショは自動、フロー定義と分析は人（＋Claude）。`scripts/` は決定論的な生成のみ、分析は Claude が config に落とす、という当リポジトリの原則に沿う。

## いつ使うか
- 競合の予約フロー/入力項目/確定方式を新しく調べたい・定点観測したい
- 既存 teardown レポートを最新のキャプチャで更新したい

## パイプライン（5ステージ）

### ① Capture（半自動 / Playwright）
- **Claude in Chrome 拡張は `getyourguide.com` などに許可ドメインが固定**され、多くの競合を開けない。競合の自動巡回は **Playwright**（許可リストに縛られない）で行う。
- 雛形：`references/capture.example.py`。`competitors.json` にサイトごとの「フロー手順（開くURL→クリック/入力の並び→撮る箇所）」を書き、Playwright が巡回してスクショを `spot/assets/teardown/` に保存する。
- **ガードレール（厳守）**：
  - **決済情報の入力・予約確定は絶対に行わない**（支払い画面が出たら停止して撮るだけ）。
  - **CAPTCHA / bot 検知は回避しない**。ブロックされたら記録してスキップ。
  - 各社の **利用規約・robots** を尊重。過度なアクセスをしない。
  - 認証情報は**ハードコードしない**（環境変数）。テストデータのみ使用。
- **フォールバック（手動）**：Playwright で撮れない画面は、人が手動で撮り Google Drive フォルダに投入 → Drive コネクタ（`search_files` で `parentId='<folderId>'`）で読み込む。テキスト未抽出の画像は `download_file_content`（巨大 base64 はツール結果ファイルに保存される）→ `python3` で `base64` デコード → 目視。

### ② Handoff / 整理
- スクショを `spot/assets/teardown/` に、`<site>-<screen>.jpg` 命名で配置（例 `klook-form.jpg`）。
- **PII**：氏名・住所・生年月日・電話・決済・確認メール等が写る画面は**掲載しない**か、**マスキング**してから使う。掲載は UX 要点が出る画面（商品/日付/在庫/フォーム構造）に限定する。

### ③ Analyze（Claude）
- 各社スクショを読み、**ペイン5分類 × ジャーニー①〜④**でマッピング。
- 比較軸（確定スピード/予約ハードル低減/入力の重さ/ログイン/日本語品質 など）を ◎○△✕ で評価。
- 結果を **config JSON**（`scripts/teardown/config.example.json` がテンプレ）に落とす。スキーマは `references/config-schema.md`。

### ④ Build（決定論）
```bash
python3 scripts/build-teardown.py --config scripts/teardown/<name>.json
# --dry-run で概要のみ、--out で出力先を上書き
```
- `scripts/teardown/style.css`（`traveler-pain-framework.html` から vendoring）を使い、hero / 比較表 / ライトボックス・ギャラリー / マトリクス / ステップ / 任意HTML を生成。

### ⑤ Publish（PR → 本番）
```bash
git checkout -b claude/competitor-teardown-<yyMMdd>
git add spot/<report>.html spot/assets/teardown
git commit -m "feat(spot): 競合予約フロー teardown を更新"
git push -u origin HEAD
gh pr create ...
```
- Vercel が **`main` を本番デプロイ**。人が PR を確認してマージ（`gh pr merge <n> --merge`）。定期実行する場合はドラフトPRまでを自動化し、マージは人。

## ファイル構成
- `scripts/build-teardown.py` … config→HTML の生成器（決定論）
- `scripts/teardown/style.css` … vendoring 済みデザイン（pain-framework 継承）
- `scripts/teardown/config.example.json` … 動くサンプル（今回の teardown を再現）
- `.claude/skills/competitor-teardown/references/config-schema.md` … config スキーマ
- `.claude/skills/competitor-teardown/references/capture.example.py` … Playwright キャプチャ雛形
- `spot/assets/teardown/*.jpg` … キャプチャ画像
- 出力：`spot/<report>.html`

## 次に増やせる仕組み（未実装）
- Playwright キャプチャ本実装（`competitors.json` のフロー手順で全社巡回）
- 四半期ごとの定期実行（routine/cron）→ 自動でドラフトPRまで。マージは人。
