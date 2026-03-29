# v2-veltra-cvr デプロイ作業指示（Claude Code用）

## やること
1. ファイルをローカルディレクトリにコピー
2. GitHubリポジトリを作成してpush
3. Vercelでデプロイ確認

## Step 1: ファイルをコピー

claude.aiのoutputsからダウンロードした以下のファイル群を配置してください。

```bash
mkdir -p /Users/kusudama/Documents/v2-veltra-cvr/reports/2026-w14

# トップページ（フレームワーク）
# → /Users/kusudama/Documents/v2-veltra-cvr/index.html

# 生成指示書
# → /Users/kusudama/Documents/v2-veltra-cvr/GENERATION_GUIDE.md

# README
# → /Users/kusudama/Documents/v2-veltra-cvr/README.md

# W14レポート（#1詳細 + サマリー）
# → /Users/kusudama/Documents/v2-veltra-cvr/reports/2026-w14/index.html

# W14 ボトルネック個別ページ
# → /Users/kusudama/Documents/v2-veltra-cvr/reports/2026-w14/bottleneck-2.html
# → /Users/kusudama/Documents/v2-veltra-cvr/reports/2026-w14/bottleneck-3.html
# → ...
# → /Users/kusudama/Documents/v2-veltra-cvr/reports/2026-w14/bottleneck-10.html
```

## Step 2: GitHubリポジトリ作成 & push

```bash
cd /Users/kusudama/Documents/v2-veltra-cvr

git init
git add .
git commit -m "initial: CVR analysis framework + W14 bottleneck report template"

# GitHubでリポジトリ作成（CLIの場合）
gh repo create SDkotarom/v2-veltra-cvr --public --source=. --push

# gh CLIがなければ手動で:
# 1. https://github.com/new → リポジトリ名: v2-veltra-cvr
# 2. git remote add origin https://github.com/SDkotarom/v2-veltra-cvr.git
# 3. git branch -M main
# 4. git push -u origin main
```

## Step 3: Vercelデプロイ

```bash
# Vercel CLI がある場合
cd /Users/kusudama/Documents/v2-veltra-cvr
vercel --prod

# CLIがなければブラウザで:
# 1. https://vercel.com/new にアクセス
# 2. Import Git Repository → v2-veltra-cvr を選択
# 3. Framework Preset: Other
# 4. Root Directory: . （デフォルト）
# 5. Build Command: 空欄
# 6. Output Directory: . 
# 7. Deploy
```

## Step 3.5: URL確認

デプロイ後、以下のURLでアクセスできることを確認：

- トップ: https://v2-veltra-cvr.vercel.app/
- W14レポート: https://v2-veltra-cvr.vercel.app/reports/2026-w14/
- #2詳細: https://v2-veltra-cvr.vercel.app/reports/2026-w14/bottleneck-2.html

※ プロジェクト名が `v2-veltra-cvr` なら、自動的に `v2-veltra-cvr.vercel.app` になる。
　 `v2.veltra-cvr.vercel.app`（サブドメイン形式）にしたい場合はVercelのDomain設定が必要。

## ファイル一覧（全13ファイル）

```
v2-veltra-cvr/
├── index.html                           ← フレームワーク（トップ）
├── GENERATION_GUIDE.md                  ← AI生成指示書
├── README.md                            ← デプロイ手順
└── reports/
    └── 2026-w14/
        ├── index.html                   ← W14レポート本体
        ├── bottleneck-2.html
        ├── bottleneck-3.html
        ├── bottleneck-4.html
        ├── bottleneck-5.html
        ├── bottleneck-6.html
        ├── bottleneck-7.html
        ├── bottleneck-8.html
        ├── bottleneck-9.html
        └── bottleneck-10.html
```

## 注意事項
- 全て静的HTMLなのでビルド不要。そのままデプロイするだけ。
- Vercel の Framework Preset は必ず「Other」を選ぶ（Next.js等ではない）。
- index.html 内のリンクはすべて相対パス。ディレクトリ構造を維持すればリンクは動く。
