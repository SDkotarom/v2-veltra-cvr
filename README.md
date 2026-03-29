# v2-veltra-cvr デプロイ手順

## ディレクトリ構成

```
v2-veltra-cvr/
├── index.html                        ← フレームワーク（トップページ）
├── reports/
│   └── 2026-w14/
│       ├── index.html                ← 週次レポート（#1 詳細）
│       ├── bottleneck-2.html
│       ├── bottleneck-3.html
│       ├── ...
│       └── bottleneck-10.html
└── README.md
```

## URL構成（公開後）

```
https://v2.veltra-cvr.vercel.app/              ← フレームワーク
https://v2.veltra-cvr.vercel.app/reports/2026-w14/  ← W14レポート
https://v2.veltra-cvr.vercel.app/reports/2026-w14/bottleneck-2.html
```

## 手順

### 1. ローカルにコピー

```bash
# このフォルダの中身を指定のディレクトリにコピー
cp -r v2-veltra-cvr/* /Users/kusudama/Documents/v2-veltra-cvr/
cd /Users/kusudama/Documents/v2-veltra-cvr/
```

### 2. GitHubリポジトリ作成 & push

```bash
cd /Users/kusudama/Documents/v2-veltra-cvr/

git init
git add .
git commit -m "initial: CVR analysis framework + bottleneck report template"

# GitHubで新しいリポジトリを作成（ブラウザで）
# https://github.com/new → リポジトリ名: v2-veltra-cvr

git remote add origin https://github.com/SDkotarom/v2-veltra-cvr.git
git branch -M main
git push -u origin main
```

### 3. Vercelでデプロイ

1. https://vercel.com/new にアクセス
2. 「Import Git Repository」→ `v2-veltra-cvr` を選択
3. **Framework Preset**: `Other`（静的HTMLなのでフレームワーク不要）
4. **Root Directory**: `.`（デフォルト）
5. **Build Command**: 空欄のまま
6. **Output Directory**: `.`
7. 「Deploy」をクリック

### 4. カスタムドメイン設定

1. Vercelのプロジェクト設定 → Domains
2. `v2.veltra-cvr.vercel.app` を追加
   - または既存の `veltra-cvr.vercel.app` のプロジェクト設定でサブドメインを設定

**注意**: `v2.veltra-cvr.vercel.app` は `issondodoitu-5880s-projects` のVercelアカウント内で、
新しいプロジェクトとして作成すれば自動的にこのURLが使えます。
プロジェクト名を `v2-veltra-cvr` にすれば `v2-veltra-cvr.vercel.app` になります。

もし `v2.veltra-cvr.vercel.app` の形式（サブドメイン）にしたい場合は、
カスタムドメイン設定が必要です。

### 5. 週次レポートの追加方法（今後）

新しい週のレポートが生成されたら：

```bash
# 新しい週のディレクトリを作成
mkdir -p reports/2026-w15/

# レポートファイルを配置
cp generated-report.html reports/2026-w15/index.html
cp bottleneck-*.html reports/2026-w15/

# index.html のアーカイブセクションに新しいエントリを追加
# （手動 or AIが自動更新）

# push
git add .
git commit -m "add: W15 bottleneck report"
git push
# → Vercelが自動デプロイ
```
