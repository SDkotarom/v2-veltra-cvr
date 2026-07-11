# scripts/teardown

競合予約フロー teardown レポートの生成器一式。

- `../build-teardown.py` … config→spot HTML の生成（決定論）。`python3 scripts/build-teardown.py --config scripts/teardown/config.example.json`
- `style.css` … `spot/traveler-pain-framework.html` から vendoring したデザイン（手編集しない）
- `config.example.json` … 動くサンプル（現行 teardown を再現）

パイプライン全体（撮影→分析→生成→PR）と config スキーマは
**`.claude/skills/competitor-teardown/`**（SKILL.md / references/config-schema.md / references/capture.example.py）を参照。
