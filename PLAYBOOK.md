# PLAYBOOK.md — 週次レポート運用マニュアル

> **毎週のレポート生成時にこのファイルを読む。**
> 技術仕様・スキーマ・UI ルールは `ARCHITECTURE.md` を参照。

---

## 1. プロジェクト概要

- **目的**: VELTRA の CVR 改善。ファネル×セグメントでボトルネック 10 件を特定し、仮説・施策・プロトタイプを生成
- **GA4 Property**: `347074845`
- **URL**: https://v2-veltra-cvr.vercel.app/
- **デプロイ**: main push → Vercel 自動デプロイ

---

## 2. ファネル定義（5段階）

| 段階 | ラベル | GA4 条件 | 通過率 |
|------|--------|---------|--------|
| ① | 流入 | 全セッション | — |
| ② | AC到達 | pagePath `/a/` | ①→② |
| ③ | 検討 | `GA4_vtjp_ex_yokka_view_booking_calendar` | ②→③ |
| ④ | 意向 | pagePath `/jp/booking` | ③→④ |
| ⑤ | 完了 | `purchase` | ④→⑤ |

CVR = `purchases / sessions`

---

## 3. 週次サイクル

### Phase 1: データ取得（Sonnet + GA4 MCP）

```bash
python3 scripts/generate-week.py --week {YYYY}-w{WW}
```

**日付範囲** → `ARCHITECTURE.md` §5 参照

**GA4 クエリ一覧（Q1〜Q10）:**

| Query | 内容 | dimensions | 格納先 |
|-------|------|-----------|--------|
| Q1 | ベースラインファネル | — | `baseline` |
| Q2 | チャネル別 | sessionDefaultChannelGroup | `segments.channel` |
| Q3 | デバイス別 | deviceCategory | `segments.device` |
| Q4 | 新規/リピーター | newVsReturning | `segments.new_returning` |
| Q5 | チャネル×デバイス | channel + device | `segments.channel_device` |
| Q6 | チャネル×新規リピーター | channel + newVsReturning | `segments.channel_new_returning` |
| Q7 | エリア別（20エリア） | landingPage フィルタ | `segments.area` |
| Q8 | 「その他」内訳 | landingPage（Q7除外） | `segments.area.other.sub_areas` |
| Q9 | サマリー（月次/週次） | — | `summary-data.json`, `weekly-summary.json` |
| Q10 | 7日ファネル（WoW） | — | `funnel_7d` |

共通条件: Property `347074845` / 期間: 直近28日（Q10のみ7日） / rates は小数

**Phase 1 完了条件**: data.json に `baseline`, `funnel_7d`, `segments`, `bottlenecks` が全て入っていること。

### Phase 2: ボトルネック分析 → content.json（Opus）

1. `data.json` からインパクト順で 10 件ランキング
2. `bottleneck-{1-10}-content.json` を作成（スキーマ → `ARCHITECTURE.md` §4）
   - 仮説 × 3 / 施策 × 9（各仮説に3つ）/ **全施策に prototype 必須** / 競合 6 社 / 検証チェックリスト
3. 静的 HTML 生成は不要（`/bottleneck.html` が動的描画）

**品質チェック**: `ARCHITECTURE.md` §6 の自動チェックコマンドを実行。90 個のプロトタイプが揃っていること。

### Phase 3: サマリーページ + デプロイ（Sonnet）

1. `reports/{week}/index.html` を前週テンプレートからデータ差し替え（バインド箇所 → `ARCHITECTURE.md` §7.3）
2. ルートファイル更新（`ARCHITECTURE.md` §7.2 参照）
3. `git push origin main` → Vercel 自動デプロイ

### Phase 4: 検証 → 修正 → 指示書改善

```bash
python3 scripts/validate-report.py --week {YYYY}-w{WW}
```

エラーがあれば修正 → 再 push → 再検証。同じエラーの再発防止のため **PLAYBOOK.md 自体を改善**する。

---

## 4. エリア定義（20セグメント）

| キー | 表示名 | GA4フィルタ |
|------|--------|-----------|
| `hawaii` | ハワイ | `/hawaii/` |
| `bali` | バリ | `/bali/` |
| `guam` | グアム | `/guam/` |
| `cebu` | セブ | `/cebu/` |
| `singapore` | シンガポール | `/singapore/` |
| `taiwan` | 台湾 | `/taiwan/` |
| `hongkong` | 香港・マカオ | `/hongkong/` |
| `thailand` | タイ | `/thailand/` |
| `vietnam` | ベトナム | `/vietnam/` |
| `europe` | ヨーロッパ | `/europe/` |
| `australia` | オーストラリア | `/australia/` |
| `okinawa` | 沖縄 | `/okinawa/` |
| `tokyo` | 東京 | `/tokyo/` |
| `osaka` | 大阪 | `/osaka/` |
| `kyoto` | 京都 | `/kyoto/` |
| `hokkaido` | 北海道 | `/hokkaido/` |
| `kanto` | 関東 | `/kanto/` |
| `kyushu` | 九州 | `/kyushu/` |
| `ishigaki_miyako` | 石垣島・宮古島 | `/ishigaki/` or `/miyako/` |
| `other` | その他 | 上記以外 |

---

## 5. AI モデル使い分け

| Phase | モデル | 対象 |
|-------|--------|------|
| Phase 1 | **Sonnet** | スキャフォールド / GA4 クエリ / data.json 組み立て |
| Phase 2 | **Opus** | ボトルネック分析 / 仮説・施策・プロトタイプ・競合比較 |
| Phase 3 | **Sonnet** | サマリーページ / commit & push |

---

## 6. 週次スケジュール

毎週月曜 AM 4:00 JST に Phase 1→2→3 を順次実行。

```
Phase 1 (Sonnet):  スキャフォールド → GA4 クエリ → data.json     ~15分
Phase 2 (Opus):    ボトルネック分析 → content.json 生成            ~30分
Phase 3 (Sonnet):  サマリーページ → commit & push → デプロイ       ~5分
```
