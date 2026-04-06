# 次セッション指示（コピペ用）

## Phase 2 実行指示

```
playbook.md と veltra-design-system.md を読んでください。

W14（2026-03-09〜2026-04-05）の Phase 2 を実行してください。
data.json は最新データで更新済みです。

やること:
1. data.json からボトルネック10件を特定（インパクト順）
2. reports/2026-w14/index.html のボトルネック一覧テーブルを更新
3. bottleneck-1.html をフル再生成（仮説×3 → 打ち手×3（仮説ごと）→ プロトタイプ → 競合比較）
   - UIはアコーディオン型ドリルダウン（仮説→🔻打ち手→📐プロトタイプ）
   - プロトタイプのモックアップは veltra-design-system.md 準拠
4. bottleneck-2〜10.html を再生成（仮説×3 + 打ち手×3 + 競合比較）
5. git commit & push to main（Vercel自動デプロイ）

注意:
- ファネル通過率の用語統一: ①→② 流入→AC到達 / ②→③ AC到達→検討 / ③→④ 検討→意向 / ④→⑤ 意向→完了
- data.json の数値を正とする（HTMLにハードコードした値との乖離に注意）
- 「仮想データ」表記を入れない
- タイムアウト防止のため、#1はOpusで、#2〜#10はSonnetで並列エージェント推奨

6. Phase 4: デプロイ後に検証スクリプトを実行
   python3 scripts/validate-report.py --week 2026-w14
   エラーがあれば修正 → 再デプロイ → playbook.md の手順も改善
```
