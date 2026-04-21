# 【調査】カテゴリーページ・予約モーダルのローディング時間改善
# [Investigation] Reduce Loading Time on Category Pages and Booking Modal

## 背景・目的 / Background & Purpose

CVR改善のボトルネック分析（BN3 Mobile ①→② = 2,076K/月）で、ページ遷移時・操作時のローディング時間が離脱要因として挙がった。**まずは技術的な原因調査と、低工数で試せる改善余地の洗い出し**を行いたい。

Our CVR bottleneck analysis (BN3 Mobile ①→② = 2,076K sessions/month) identified page-transition and in-page loading time as a major drop-off factor. **We first want to investigate the technical root cause and identify low-effort improvements that can be tried quickly.**

本チケットは**調査フェーズ**。調査結果をもとに、追加の改善実装チケットを別途起票する。

This ticket is the **investigation phase**. Based on the findings, separate implementation tickets will be filed.

## 調査対象 / Investigation Targets

### ① カテゴリーページ表示時のローディング / Loading on Category Page Display

カテゴリーページを開くと、毎回ローディングスピナーが回る。早いページもあるが、遅いページでは体感で離脱リスクを感じるレベル。

When opening a category page, a loading spinner appears every time. Some pages load quickly, but slower ones feel slow enough to risk user drop-off.

**具体例（調査の起点URL）/ Reference URLs**:

- https://www.veltra.com/jp/japan/osaka/ctg/161512:Bus_tour/
- https://www.veltra.com/jp/japan/osaka/ctg/181188:Bus/

### ② 「今すぐ予約」モーダル内の再読み込み / Reloading Inside the "Book Now" Modal

ACページ→「今すぐ予約」で開くモーダル内で、以下の操作のたびにローディングが発生する。1回あたりは致命的ではないが、**日程は複数回切り替える前提の操作**のため、累積でストレスになる。

Inside the modal opened from "Book Now" on an AC (Activity) page, loading occurs every time the user performs the operations below. Each load isn't critical on its own, but since **users typically switch dates multiple times**, the cumulative friction becomes stressful.

- カレンダーで参加日を選んだとき / When selecting a date on the calendar
- 利用人数を変更したとき / When changing the number of participants
- 開始時間を変更したとき / When changing the start time

## 調査スコープ / Investigation Scope

### 1. 原因切り分け / Root Cause Isolation

- サーバーサイド応答時間（在庫/料金計算API等） / Server-side response time (inventory / pricing APIs, etc.)
- クライアントサイド処理（再レンダー、重い計算） / Client-side processing (re-renders, heavy computation)
- キャッシュ効いていない項目の有無 / Items that are not being cached
- 不要なAPIコールが発生していないか（例：同じパラメータでの重複取得） / Unnecessary API calls (e.g., duplicate fetches with the same parameters)

### 2. 改善可能性の洗い出し / Identifying Possible Improvements

- デバウンス/スロットリング可能な操作はないか / Operations that could be debounced/throttled
- オプティミスティックUI（先に画面だけ更新）で体感改善できないか / Optimistic UI (updating the view before the server responds) to improve perceived speed
- スケルトン/プレースホルダで「何かが動いている」感を出せないか / Using skeletons / placeholders to convey "something is happening"
- キャッシュ戦略（同一日程の再選択時など） / Caching strategy (e.g., when the same date is re-selected)
- ローディング中に離脱防止のコンテンツ表示可否（旅行TIPS等。※別案件で要検討） / Whether to show drop-off-prevention content during loading (travel tips, etc. — to be considered separately)

## 完了条件 / Definition of Done

- [ ] 対象ページ/操作のロード時間ボトルネックがレポート化されている（主要処理の内訳・所要時間） / A report of the load-time bottlenecks (breakdown of main operations and durations) exists for the target pages/operations
- [ ] 原因カテゴリが特定されている（サーバー/クライアント/ネットワーク/キャッシュ等） / The cause category is identified (server / client / network / cache, etc.)
- [ ] **低工数（例: S〜Mエフォート）で試せる改善案がリストアップされている** / **A list of low-effort (S–M) improvement ideas has been compiled**
- [ ] 低工数案のうち、即実装可能なものがあれば本チケット内で対応 / Any low-effort items that can be implemented immediately are handled within this ticket
- [ ] それ以外の改善案は別チケット化 / Remaining ideas are split into separate tickets

## 優先度・エフォート / Priority & Effort

- **優先度 / Priority**: 高 / High（BN3＝モバイル流入→AC到達、月2,076Kセッション影響 / BN3 = Mobile traffic → AC reach, impact of 2,076K sessions/month）
- **エフォート / Effort**: 調査フェーズ=S〜M、改善実装は調査結果次第 / Investigation phase = S–M; improvement implementation depends on findings

## 関連 / References

- ボトルネック分析 W15 #3（Mobile ①→②）/ Bottleneck analysis W15 #3 (Mobile ①→②): https://v2-veltra-cvr.vercel.app/bottleneck.html?week=2026-w15&num=3
- 施策一覧スプレッドシート / Initiatives spreadsheet: https://docs.google.com/spreadsheets/d/1MMjIEdcU9Bme8WVDHLP28XEr2EsLQwG2K57ZYBdnmbM/edit?gid=1609841755
