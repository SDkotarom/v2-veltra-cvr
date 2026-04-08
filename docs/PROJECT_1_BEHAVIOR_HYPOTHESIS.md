# Project 1: ボトルネック分析への行動仮説レイヤー追加

> **ステータス**: 計画中 → Phase 2（Opus生成指示）から着手
> **オーナー**: KotaroM（UX Design Squad）
> **関連**: Project 2（ペルソナ別ジャーニーマップ）の前提となるプロジェクト

---

## 1. 背景と課題

現在の週次CVRレポート（v2-veltra-cvr）は、ファネル×セグメントのクロス分析でボトルネック10件を特定し、仮説・施策・プロトタイプを生成している。

**できていること:**
- 「どこで・誰が落ちているか」の特定（ファネル5段階 × チャネル/デバイス/新規リピーター/エリア）
- ボトルネックごとの仮説×3 → 施策×9 → Before/Afterプロトタイプの生成

**できていないこと:**
- **「なぜ落ちたか」の行動レベルの仮説がない。** 数値の乖離は見えているが、「ユーザーが実際にどういう行動をとった結果この数字になったのか」の推定がない
- 仮説と施策の間に飛躍がある。なぜその施策が有効なのかの論理的な橋渡しがない
- 2025年のABテスト結果（勝ち/負けパターン）がレポートから参照されていない

**結果として:**
- レポートを読んだ人が、自分で「なぜ」を推理する必要がある
- 施策の方向性（引き算 vs 足し算）の判断根拠が不明確
- 同じ負けパターン（個別最適）を繰り返すリスクがある

---

## 2. ゴール

ボトルネック分析の各ページに、以下の4つの情報を追加する:

| 追加要素 | 内容 | 例 |
|---------|------|-----|
| 推定行動 | ユーザーが実際にとった行動の推定 | 「Acページに到達したがカレンダーまでスクロールせず離脱」 |
| 根拠 | 推定行動を裏付けるデータパターン | 「Ac到達率は平均並みだがカレンダー表示率のみ大幅低下」 |
| ページ役割チェック | 戦略ガイドSection 3との照合 | 「Ac＝確信する場。カレンダー到達前に離脱＝確信プロセスに入れていない」 |
| 引き算チェック | 情報追加より引き算で解決できないか | 「Ac上部の情報整理がCTA追加より優先」 |

**Before → After のイメージ:**

```
【Before（現状）】
ボトルネック#1: Mobile × Organic × カレンダー表示率 -38%
  仮説1: ページ内のCTA視認性が低い
  仮説2: カレンダーの読み込みが遅い
  仮説3: 料金が不透明で離脱
  → 施策A〜I + プロトタイプ

【After（目標）】
ボトルネック#1: Mobile × Organic × カレンダー表示率 -38%
  ● 推定行動: Acページ到達後、カレンダーセクションまでスクロールせず離脱
  ● 根拠: Ac到達率は平均並み（22%）だがカレンダー表示率のみ-38%乖離
  ● ページ役割: Ac＝「不安を解消し確信する場」→ 確信プロセスに入れていない
  ● 引き算チェック: Ac上部の情報整理（スケジュール/含まれるもの圧縮）が優先

  仮説1: Acページ上部の情報過多でスクロール前に離脱
    ↳ 2025年パターン: ハイライト非表示+3.8%（情報の引き算 = 勝ちパターン）
  仮説2: ...
  仮説3: ...
  → 施策A〜I + プロトタイプ
```

---

## 3. 設計

### 3-1. content.json スキーマ拡張

現在の `bottleneck-{N}-content.json`（ARCHITECTURE.md §4）に `behavior_context` フィールドを追加する。

```jsonc
{
  // ====== 既存フィールド（変更なし） ======
  "number": 1,
  "title": "Organic Search × Mobile — ③→④ 意向転換率の低さ",
  "tags": [...],
  "deviation": "-42%",
  "impact_sessions": "923K / 月",
  "description_html": "...",
  "funnel_overview": {...},
  "funnel_compare": [...],
  "drill_down": [...],
  "callout": {...},

  // ====== ★追加: 行動仮説レイヤー ======
  "behavior_context": {
    "estimated_action": "Acページに到達したが、カレンダーセクションまでスクロールせず離脱した可能性が高い",
    "evidence": [
      "当セグメントのAc到達率（①→②）は22.04%で全体平均26.10%と同水準",
      "一方、カレンダー表示率（②→③）は-38%乖離しており、Acページ内の問題に絞られる",
      "Mobileではカレンダーがfold下（スクロール3〜4画面目）に位置する"
    ],
    "page_role_check": "Acページ＝「不安を解消し確信する場」（戦略ガイドSection 3）。カレンダー到達前に離脱＝確信プロセスに入れていない",
    "subtraction_check": "Acページ上部の情報を整理しカレンダーまでの距離を短縮する方が、新要素追加より優先（2025年の学び: 引き算が勝ちパターン）",
    "pattern_references": [
      "勝ち: ハイライト非表示 +3.8%（情報の引き算）",
      "勝ち: タブ切り替え化 +2%（並走型UI）",
      "負け: ランキングナビ追加（探索行動を阻害）"
    ]
  },

  // ====== 既存フィールド（変更なし） ======
  "hypo_section_title": "...",
  "hypo_section_desc": "...",
  "hypotheses": [...],
  "verification_method": "...",
  "competitive": [...],
  "competitive_insight": "...",
  "verification": [...]
}
```

**フィールド定義:**

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `estimated_action` | string | ✅ | ユーザーが実際にとった行動の推定。1文で要約 |
| `evidence` | string[] | ✅ | 推定行動を裏付けるデータパターン。2〜4件 |
| `page_role_check` | string | ✅ | 戦略ガイドSection 3のページ役割定義との照合結果 |
| `subtraction_check` | string | ✅ | 引き算で解決できないかのチェック結果 |
| `pattern_references` | string[] | 任意 | 関連する2025年ABテスト勝ち/負けパターン。0〜3件 |

### 3-2. hypotheses への影響

既存の `hypotheses` 構造はそのまま使う。ただし、Opus生成時に以下のルールを追加する:

- 各仮説は `behavior_context.estimated_action` と整合すること
- 仮説には「施策起因」「外部要因起因」「構造的問題」の3カテゴリを含めること（3つの仮説が全て同じカテゴリにならないこと）
- `pattern_references` に該当する勝ち/負けパターンがあれば、仮説の `evidence` に明記すること

### 3-3. 生成フローへの組み込み

現行のPhase分担（PLAYBOOK.md §3）への影響:

| Phase | 現状 | 変更後 |
|-------|------|--------|
| Phase 1（Sonnet） | GA4クエリ → data.json | **変更なし** |
| Phase 2（Opus） | data.json → content.json（仮説・施策・プロトタイプ） | content.json に `behavior_context` を追加生成 |
| Phase 3（Sonnet） | サマリーページ + デプロイ | **変更なし** |

Phase 2 のOpusへの指示に以下を追加する:

```
## 行動仮説レイヤーの生成ルール

各ボトルネックの content.json を作成する際、hypotheses の前に behavior_context を生成すること。

1. estimated_action: ボトルネックのセグメント×ファネル段階から、ユーザーがとった行動を1文で推定する
   - 「〜した可能性が高い」「〜と推定される」等の表現を使う（断定しない）

2. evidence: 推定行動を裏付けるデータパターンを2〜4件列挙する
   - data.json の数値を具体的に引用する（「Ac到達率22.04%」等）
   - 「このセグメントだけ落ちている」「他の段階は正常」等、比較による根拠を示す

3. page_role_check: 戦略ガイドSection 3のページ役割と照合する
   - Area/Top: 「どこで何ができるかを大づかみする場」
   - Ctg: 「候補を絞り込む場」
   - Ac: 「不安を解消し確信する場」
   - Booking form: 「迷わず完了する場」
   - ボトルネックの段階がどのページに該当するかを判定し、
     役割が果たされていない理由を記述する

4. subtraction_check: 情報の追加ではなく引き算で解決できないかを検討する
   - 「引き算で解決可能」「引き算だけでは不十分、〇〇の追加が必要」等を明記

5. pattern_references: 2025年ABテスト結果から関連するパターンを引用する
   - 勝ち: 情報のシンプル化 / 並走型UI / 行動喚起の明確化 / 構造の統一
   - 負け: ノイズになる機能追加 / 意思決定に影響しない細部の変更
   - 該当がなければ空配列でよい

6. hypotheses との整合: behavior_context を先に書き、
   それと整合する仮説を3つ生成する
```

### 3-4. bottleneck.html テンプレートへの表示追加

動的テンプレート（/bottleneck.html）に `behavior_context` の表示セクションを追加する。
表示位置は `callout`（特定結果コールアウト）と `hypo_section_title` の間。

```
[既存] タイトル + タグ + 乖離率 + 影響セッション数
[既存] 説明文（description_html）
[既存] ファネル全体比較 + Tier1比較
[既存] 深掘り分析
[既存] 特定結果コールアウト

★追加: 行動仮説セクション
  ┌──────────────────────────────────────┐
  │ ● 推定行動                           │
  │   Acページに到達したが...             │
  │                                      │
  │ ● 根拠                               │
  │   ・Ac到達率は平均並み（22.04%）      │
  │   ・カレンダー表示率のみ-38%乖離     │
  │                                      │
  │ ● ページ役割チェック                  │
  │   Ac＝「確信する場」→ 確信に入れていない│
  │                                      │
  │ ● 引き算チェック                      │
  │   上部情報の整理が新要素追加より優先   │
  │                                      │
  │ ● 関連パターン（2025年）              │
  │   ✅ 情報の引き算 +3.8%               │
  │   ✅ 並走型UI +2%                     │
  │   ❌ ナビ追加は不発                   │
  └──────────────────────────────────────┘

[既存] 仮説セクションタイトル
[既存] 仮説×3 → 施策×9 → プロトタイプ
[既存] 検証方法 + 競合比較 + チェックリスト
```

UIスタイルは既存の `callout` セクションと同じトーン。
`behavior_context` がない content.json はセクションを非表示にする（後方互換）。

---

## 4. ファネル段階別の行動仮説テンプレート

Opus が仮説を生成する際の参考テンプレート。全パターンを網羅する必要はなく、データと整合するものを選ぶ。

### ①→② Session → Ac到達（回遊）

| 行動パターン | 発生条件 | 関連ページ |
|-------------|---------|-----------|
| LP/一覧で目的の商品を見つけられず離脱 | 一覧の情報不足 or 並び順の問題 | Area / Ctg |
| 検索結果が期待と合わず離脱 | 検索キーワードとLP内容のミスマッチ | Search / Ctg |
| 候補が多すぎて選べず離脱 | 比較情報の過多 | Ctg |
| ページ読み込みが遅く離脱 | TBT/TTFB問題 | 全ページ |

### ②→③ Ac到達 → カレンダー表示（検討）

| 行動パターン | 発生条件 | 関連ページ |
|-------------|---------|-----------|
| カレンダーまでスクロールせず離脱 | 上部セクションが長い / 情報過多 | Ac |
| 料金が見えず不安で離脱 | 料金表示の位置が深い | Ac |
| 他の候補と比較するために一覧に戻った | 確信が持てない / 比較情報不足 | Ac → Ctg |
| 体験談を読んで不安になり離脱 | ネガティブレビューの影響 | Ac |

### ③→④ カレンダー表示 → フォーム遷移（意向）

| 行動パターン | 発生条件 | 関連ページ |
|-------------|---------|-----------|
| 希望日程の在庫がなく離脱 | 在庫なし表示 | Ac（カレンダー） |
| 料金を見て予算オーバーで離脱 | 価格と期待のギャップ | Ac（カレンダー） |
| プラン選択で迷って離脱 | プランが多すぎる / 違いが不明確 | Ac（プラン選択） |
| 予約ボタンが見つからず離脱 | CTAの視認性問題 | Ac |

### ④→⑤ フォーム遷移 → 予約完了（完了）

| 行動パターン | 発生条件 | 関連ページ |
|-------------|---------|-----------|
| 入力項目が多すぎて途中離脱 | フォームの長さ | Booking form |
| 決済手段が合わず離脱 | 希望の決済方法がない | Booking form |
| 確認画面で不安になり離脱 | 最終確認時の情報不足 | Booking form |
| エラーが出て再入力が面倒で離脱 | バリデーションUX | Booking form |

---

## 5. 品質チェックルール（ARCHITECTURE.md §6 への追記）

### 5-1. behavior_context チェック（§6.1 に追加）

| チェック項目 | 必須値 |
|-------------|--------|
| `behavior_context` | オブジェクトが存在すること |
| `behavior_context.estimated_action` | 空でないこと |
| `behavior_context.evidence` | 2件以上 |
| `behavior_context.page_role_check` | 空でないこと |
| `behavior_context.subtraction_check` | 空でないこと |

### 5-2. 自動チェックコマンド（§6.3 への追記）

```python
# behavior_context チェック（既存チェックに追加）
bc = d.get('behavior_context', {})
if not bc.get('estimated_action'):
    print(f'#{i}: behavior_context.estimated_action MISSING'); ok = False
if len(bc.get('evidence', [])) < 2:
    print(f'#{i}: behavior_context.evidence < 2'); ok = False
if not bc.get('page_role_check'):
    print(f'#{i}: behavior_context.page_role_check MISSING'); ok = False
if not bc.get('subtraction_check'):
    print(f'#{i}: behavior_context.subtraction_check MISSING'); ok = False
```

---

## 6. 実装手順（Claude Code 指示書）

以下の順序でClaude Codeに指示する。各ステップは独立して実行可能。

### Step 1: ARCHITECTURE.md の更新

```
ARCHITECTURE.md を開いて以下を更新してください。

1. §4 content.json スキーマに behavior_context フィールドを追加
   - hypotheses の直前に配置
   - フィールド: estimated_action (string, 必須), evidence (string[], 必須, 2件以上),
     page_role_check (string, 必須), subtraction_check (string, 必須),
     pattern_references (string[], 任意)

2. §6.1 構造チェックに behavior_context の4項目を追加

3. §6.3 自動チェックコマンドに behavior_context のバリデーションを追加

参照: PROJECT_1_BEHAVIOR_HYPOTHESIS.md の §3-1（スキーマ定義）と §5（チェックルール）
```

### Step 2: bottleneck.html テンプレートの更新

```
/bottleneck.html を開いて、behavior_context の表示セクションを追加してください。

表示位置: callout（特定結果コールアウト）と hypo_section_title の間。

表示内容:
- セクションタイトル「行動仮説」
- 推定行動（estimated_action）: アイコン ● + テキスト
- 根拠（evidence）: リスト形式
- ページ役割チェック（page_role_check）: テキスト
- 引き算チェック（subtraction_check）: テキスト
- 関連パターン（pattern_references）: ✅/❌ アイコン付きリスト（任意、空なら非表示）

スタイルは bottleneck.css に追加。既存のcalloutセクションと同じトーンで。
content.json に behavior_context がない場合はセクション自体を非表示にする
（後方互換性のため）。

参照: PROJECT_1_BEHAVIOR_HYPOTHESIS.md の §3-4（表示レイアウト）
```

### Step 3: PLAYBOOK.md の更新

```
PLAYBOOK.md §3 Phase 2 の説明に、behavior_context の生成指示を追記してください。

Phase 2（Opus）のステップを以下に更新:
1. data.json からインパクト順で10件ランキング
2. 各ボトルネックについて behavior_context を先に生成
   - estimated_action: データパターンから行動を推定
   - evidence: data.json の具体的数値を引用
   - page_role_check: 戦略ガイドSection 3と照合
   - subtraction_check: 引き算で解決可能か検討
   - pattern_references: 2025年ABテスト結果を参照
3. behavior_context と整合する仮説×3、施策×9、プロトタイプを生成
4. content.json に出力

参照: PROJECT_1_BEHAVIOR_HYPOTHESIS.md の §3-3（Opus向け生成ルール全文）
```

### Step 4: 次回のレポート生成で試行

```
次回の週次レポート生成（Phase 2）で、ボトルネック#1〜#3 の content.json に
behavior_context を含めて生成してください。

#4〜#10 は従来通り（behavior_context なし）でOK。
#1〜#3 の生成結果を確認してから、全10件に展開します。

生成時の参照ドキュメント:
- ARCHITECTURE.md §4（content.json スキーマ）
- PROJECT_1_BEHAVIOR_HYPOTHESIS.md §4（ファネル段階別テンプレート）
- 戦略ガイドPDF Section 2（勝ち/負けパターン）, Section 3（ページ役割定義）
```

---

## 7. Project 2 との関係

このプロジェクトで蓄積される行動仮説が、Project 2（ペルソナ別ジャーニーマップ）の材料になる。

```
Project 1（週次）                     Project 2（四半期）
┌──────────────────────┐             ┌──────────────────────┐
│ ボトルネック分析       │             │ ジャーニーマップ       │
│ + behavior_context   │──蓄積──→    │ ペルソナ別行動構造    │
│ + 勝ち/負けパターン照合│             │ + 季節変動            │
└──────────────────────┘             └──────────────────────┘
```

- ボトルネックに繰り返し登場するセグメント（例: Mobile × Organic × 新規）がペルソナ候補になる
- 各ボトルネックの estimated_action を時系列で並べると、そのペルソナのジャーニーが浮かぶ
- Project 1 の蓄積が3ヶ月分たまった時点で、Project 2 のペルソナ定義に着手する

---

## 8. 成功指標

| 指標 | 現状 | 目標 |
|------|------|------|
| ボトルネック→施策の論理的接続 | 仮説と施策に飛躍あり | behavior_context が橋渡しする |
| 負けパターンの再発 | 未チェック | pattern_references で事前検出 |
| ページ役割との整合 | 未チェック | page_role_check で全件チェック |
| レポート読了→施策方向の合意 | チーム議論で時間がかかる | 行動仮説が議論の出発点になる |

---

## 9. 次のアクション

- [ ] このドキュメントの内容を関係者と確認
- [ ] Claude Code に Step 1（ARCHITECTURE.md 更新）を指示
- [ ] Claude Code に Step 2（bottleneck.html 更新）を指示
- [ ] Claude Code に Step 3（PLAYBOOK.md 更新）を指示
- [ ] 次回レポート生成で #1〜#3 を試行（Step 4）
- [ ] 試行結果を確認し、全10件に展開
