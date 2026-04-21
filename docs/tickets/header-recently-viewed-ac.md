# 【実装】ヘッダー/SPメニューに「最近見たAC」ショートカット追加（リピーター向け）
# [Implementation] Add "Recently Viewed Activities" Shortcut to Header / SP Menu (Returning Users)

## 背景・目的 / Background & Purpose

リピーターはOrganic Search・Direct経由でサイトに戻ってきても、どのページにいてもACへの直接導線がなく、マイページ完結で離脱している。

Returning users who come back via Organic Search or Direct have no shortcut to AC pages from anywhere on the site, leading them to drop off within My Page without reaching an AC.

ヘッダー/SPメニューに「最近見たAC」導線を追加し、どのページからでもワンタップでACへ遷移できるようにする。

By adding a "Recently Viewed" shortcut to the header / SP menu, users can reach an AC page with one tap from anywhere on the site.

## 対象ユーザー / Target Users

- ログイン済みリピーター（過去に1件以上予約済み）
- ゲストユーザーは対象外（ログインしていない場合は非表示）

- Logged-in returning users (at least one past booking)
- Guest users are excluded (hidden when not logged in)

## 要件 / Requirements

### 表示条件 / Display Conditions

- ログイン済みかつ閲覧履歴が1件以上ある場合に表示
- 閲覧履歴がない場合はアイコン/セクション自体を非表示

- Shown only when the user is logged in and has at least one browsing history entry
- Hidden entirely if no browsing history exists

### PC：ヘッダー / PC: Header

- ヘッダーナビ内にアイコン（例：時計マーク）＋「最近見たAC」テキストを追加
- ホバーまたはクリックでドロップダウン表示
- ドロップダウン内に最近閲覧したAC最大3件を表示（ACサムネ＋タイトル＋価格）
- 各ACをクリックでACページへ遷移

- Add an icon (e.g., clock icon) + "Recently Viewed" label to the header nav
- Show dropdown on hover or click
- Display up to 3 recently viewed ACs in the dropdown (thumbnail + title + price)
- Each item links directly to the AC page

### SP：メニュー / SP: Menu

- ハンバーガーメニューを開いた内部に「最近見たAC」セクションを追加
- 最近閲覧したAC最大3件を縦並びで表示（ACサムネ＋タイトル＋価格）
- 各ACをタップでACページへ遷移

- Add a "Recently Viewed" section inside the hamburger menu
- Display up to 3 recently viewed ACs in a vertical list (thumbnail + title + price)
- Each item links directly to the AC page

### 閲覧履歴のロジック / Browsing History Logic

- 取得元：既存のAC閲覧履歴データ（ローカルストレージ or サーバーサイドセッション）を使用
- 表示順：直近閲覧順（新しいものが上）
- 重複除外：同じACは1件のみ表示

- Source: Use existing AC browsing history data (localStorage or server-side session)
- Order: Most recently viewed first
- Deduplication: Show each AC only once

## 完了条件 / Definition of Done

- [ ] ログイン済みリピーターのヘッダー（PC）に「最近見たAC」ドロップダウンが表示される
- [ ] ログイン済みリピーターのSPメニュー内に「最近見たAC」セクションが表示される
- [ ] 閲覧履歴がない場合は非表示になる
- [ ] 未ログイン時は非表示になる
- [ ] ACカードをクリック/タップするとACページへ正しく遷移する
- [ ] 既存のヘッダー/SPメニューのレイアウトに影響がない

- [ ] Logged-in returning users see a "Recently Viewed" dropdown in the PC header
- [ ] Logged-in returning users see a "Recently Viewed" section in the SP menu
- [ ] The section is hidden when there is no browsing history
- [ ] The section is hidden when the user is not logged in
- [ ] Clicking/tapping an AC card navigates correctly to the AC page
- [ ] No regression to existing header / SP menu layout

## 優先度・エフォート / Priority & Effort

- **優先度 / Priority**: 高 / High（BN2＝リピーター流入→AC到達、月1,166Kセッション影響 / BN2 = Returning user traffic → AC reach, impact of 1,166K sessions/month）
- **エフォート / Effort**: M（閲覧履歴データの取得方法により変動 / May vary depending on how browsing history data is retrieved）

## 関連 / References

- ボトルネック分析 W15 #2（リピーター ①→②）/ Bottleneck analysis W15 #2 (Returning users ①→②): https://v2-veltra-cvr.vercel.app/bottleneck.html?week=2026-w15&num=2
- 施策一覧スプレッドシート / Initiatives spreadsheet: https://docs.google.com/spreadsheets/d/1MMjIEdcU9Bme8WVDHLP28XEr2EsLQwG2K57ZYBdnmbM/edit?gid=1609841755
