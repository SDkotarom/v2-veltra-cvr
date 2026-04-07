(function () {
  var html = '<div class="card" style="margin-top:28px">' +
    '<details open style="padding:24px 44px">' +
    '<summary style="cursor:pointer;font-size:14px;font-weight:700;letter-spacing:.08em;color:#aaa;list-style:none;display:flex;align-items:center;gap:8px">' +
    '<span style="font-size:16px;transition:transform .2s;transform:rotate(90deg)" class="fd-arrow">▸</span> ファネル データソース定義 — 各指標の集計方法と計算式</summary>' +
    '<p style="margin:12px 0 16px;font-size:13px;color:#aaa;line-height:1.7">ファネル①〜⑤の各ステップ数は <strong style="color:#6b6b6b">activeUsers（ユニークユーザー）</strong> ベース。<br>主要KPIサマリーの「セッション数」「CVR」は <strong style="color:#6b6b6b">延べセッション数（sessions）</strong> ベースであり、別指標です。延べセッション数＝訪問回数の合計（同一人物の複数訪問を含む）。</p>' +
    '<table style="width:100%;border-collapse:collapse;margin-top:0;font-size:14px">' +
    '<thead><tr style="border-bottom:2px solid #e8e6e1;text-align:left">' +
    '<th style="padding:8px 12px;font-weight:700;color:#6b6b6b">項目名</th>' +
    '<th style="padding:8px 12px;font-weight:700;color:#6b6b6b;width:90px">種別</th>' +
    '<th style="padding:8px 12px;font-weight:700;color:#6b6b6b">集計方法 / 計算式</th></tr></thead>' +
    '<tbody>' +
    '<tr style="border-bottom:1px solid #e8e6e1"><td style="padding:8px 12px">サイト訪問</td><td style="padding:8px 12px;color:#aaa">ファネル</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">activeUsers（ユニークユーザー数）</td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1"><td style="padding:8px 12px">ACページ訪問</td><td style="padding:8px 12px;color:#aaa">ファネル</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">pagePath に <code>/a/</code> を含む activeUsers 数</td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1"><td style="padding:8px 12px">カレンダー表示（予約押下）</td><td style="padding:8px 12px;color:#aaa">ファネル</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">GA4_vtjp_ex_yokka_view_booking_calendar イベントを発火した activeUsers 数</td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1"><td style="padding:8px 12px">予約フォーム表示</td><td style="padding:8px 12px;color:#aaa">ファネル</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">pagePath に <code>/jp/booking</code> を含む activeUsers 数</td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1"><td style="padding:8px 12px">予約完了</td><td style="padding:8px 12px;color:#aaa">ファネル</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">purchase イベント数（transactions）</td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1;background:#fafaf8"><td style="padding:8px 12px">ACページ訪問率</td><td style="padding:8px 12px;color:#aaa">通過率</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">ACページ訪問 ÷ サイト訪問 × 100<br><code style="font-size:13px;color:#aaa">ac_page_reach_users / session_start_users</code></td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1;background:#fafaf8"><td style="padding:8px 12px">カレンダー表示率</td><td style="padding:8px 12px;color:#aaa">通過率</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">カレンダー表示 ÷ ACページ訪問 × 100<br><code style="font-size:13px;color:#aaa">calendar_view / ac_page_reach_users</code></td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1;background:#fafaf8"><td style="padding:8px 12px">予約フォーム到達率</td><td style="padding:8px 12px;color:#aaa">通過率</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">予約フォーム表示 ÷ カレンダー表示 × 100<br><code style="font-size:13px;color:#aaa">form_start / calendar_view</code></td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1;background:#fafaf8"><td style="padding:8px 12px">予約完了率</td><td style="padding:8px 12px;color:#aaa">通過率</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">予約完了 ÷ 予約フォーム表示 × 100<br><code style="font-size:13px;color:#aaa">purchase / form_start</code></td></tr>' +
    '<tr style="background:#fafaf8"><td style="padding:8px 12px">全体CVR</td><td style="padding:8px 12px;color:#aaa">通過率</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">予約完了 ÷ 全セッション数 × 100<br><code style="font-size:13px;color:#aaa">purchases / sessions</code> <span style="font-size:13px;color:#aaa">※sessionsベース（KPIサマリーと同値）</span></td></tr>' +
    '</tbody></table></details></div>';

  var footers = document.querySelectorAll('.footer');
  footers.forEach(function (f) {
    var container = f.closest('.card');
    if (container) {
      container.insertAdjacentHTML('beforebegin', html);
    }
  });

  document.addEventListener('click', function (e) {
    var details = e.target.closest('details');
    if (!details) return;
    var arrow = details.querySelector('.fd-arrow');
    if (arrow) {
      arrow.style.transform = details.open ? 'rotate(0deg)' : 'rotate(90deg)';
    }
  });
})();
