# docs/captures/ — VELTRAサイト キャプチャ置き場

> **目的**: 打ち手提案時にClaude（multi-modal）が「現物のUI」を視覚的に把握するため、主要ページのスクリーンショットをここに置く。
>
> **関連**: `docs/site-features.md`（文字による現仕様）、`known-implementations.json`（キーワード照合）

---

## 撮影ガイドライン

### ファイル命名規則

`{page}-{device}.png`

- `{page}`: 以下のいずれか（増やしてOK）
  - `top` / `region` / `area` / `category` / `ac` / `date-search` / `keyword-search` / `booking` / `wishlist` / `login` / `mypage` / `app-home` 等
- `{device}`: `pc` または `sp`

例:
```
top-pc.png
top-sp.png
ac-pc.png
ac-sp.png
booking-sp.png
```

### 追加バリエーションがある場合

`{page}-{device}-{variant}.png`

例:
```
ac-sp-calendar.png        # カレンダー開いた状態
booking-sp-payment.png    # 決済ステップ
area-pc-filter.png        # フィルター展開時
```

---

## 撮影推奨ページ一覧（最低限）

PC+SPペアで計 **14枚** あれば Phase 2 のボトルネック分析が相当楽になる:

| ページ | PC | SP | 備考 |
|--------|----|----|------|
| トップ `/jp/` | ✅ | ✅ | ファーストビュー |
| エリア（例: `/jp/hawaii/oahu/`） | ✅ | ✅ | ACカード一覧 |
| カテゴリ | ✅ | ✅ | フローティングフィルター写る状態で |
| AC詳細 | ✅ | ✅ | カレンダー+プラン一覧含む |
| 予約フォーム | ✅ | ✅ | 最初のステップ |
| 日程検索 or キーワード検索結果 | ✅ | ✅ | どちらかでOK |
| ウィッシュリスト（任意） | - | ✅ | お気に入り追加後 |

---

## 撮影サイズ（目安）

- **PC**: ウィンドウ幅 1440px前後、ファーストビュー〜スクロール2画面程度
- **SP**: iPhone標準（375×667 or 390×844）、ファーストビュー〜3スクロール分

ブラウザDevToolsのデバイスモードで撮ると再現性あり。

---

## 運用

1. ユーザーが画像ファイルをこのディレクトリに追加
2. `docs/site-features.md` の該当ページセクションに「**キャプチャ**: `docs/captures/xxx-pc.png`」の行を更新
3. Phase 2 実行時、Claudeはこのディレクトリの画像を `Read` ツールで読み込む
4. サイト改修があったら、旧キャプチャを `docs/captures/archive/YYYY-MM/` に移動して新版で差し替え

---

## よくある質問

**Q. 認証が必要なページ（マイページ等）はどうする？**
A. 撮影時のみログインして撮影 → 個人情報が写らないようマスキング（要黒塗り）。

**Q. 画像サイズ制限は？**
A. 1枚1MB以内が目安。PNGでOK、大きすぎる場合は品質80%のJPGに。

**Q. 何枚まで？**
A. 上限なし。ただし一度にClaudeが読むのは5〜7枚まで。Phase 2では必要な2〜3枚だけ `Read` する運用。

---

*v1 / 2026-04-20*
