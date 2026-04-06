(function () {
  var html = '<div class="card" style="margin-top:28px">' +
    '<details style="padding:24px 44px">' +
    '<summary style="cursor:pointer;font-size:14px;font-weight:700;letter-spacing:.08em;color:#aaa;list-style:none;display:flex;align-items:center;gap:8px">' +
    '<span style="font-size:16px;transition:transform .2s" class="fd-arrow">▸</span> ファネル データソース定義 — 各指標の集計方法と計算式</summary>' +
    '<table style="width:100%;border-collapse:collapse;margin-top:16px;font-size:14px">' +
    '<thead><tr style="border-bottom:2px solid #e8e6e1;text-align:left">' +
    '<th style="padding:8px 12px;font-weight:700;color:#6b6b6b">項目名</th>' +
    '<th style="padding:8px 12px;font-weight:700;color:#6b6b6b;width:72px">種別</th>' +
    '<th style="padding:8px 12px;font-weight:700;color:#6b6b6b">集計方法 / 計算式</th></tr></thead>' +
    '<tbody>' +
    '<tr style="border-bottom:1px solid #e8e6e1"><td style="padding:8px 12px">サイト訪問</td><td style="padding:8px 12px;color:#aaa">ファネル</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">全セッション数</td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1"><td style="padding:8px 12px">ACページ訪問</td><td style="padding:8px 12px;color:#aaa">ファネル</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">pagePath に <code>/a/</code> を含むセッション数</td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1"><td style="padding:8px 12px">カレンダー表示（予約押下）</td><td style="padding:8px 12px;color:#aaa">ファネル</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">GA4_vtjp_ex_yokka_view_booking_calendar イベント数</td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1"><td style="padding:8px 12px">予約フォーム表示</td><td style="padding:8px 12px;color:#aaa">ファネル</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">pagePath に <code>/jp/booking</code> を含むセッション数</td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1"><td style="padding:8px 12px">予約完了</td><td style="padding:8px 12px;color:#aaa">ファネル</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">purchase イベント数</td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1;background:#fafaf8"><td style="padding:8px 12px">ACページ訪問率</td><td style="padding:8px 12px;color:#aaa">通過率</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">ACページ訪問 ÷ サイト訪問 × 100</td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1;background:#fafaf8"><td style="padding:8px 12px">カレンダー表示率</td><td style="padding:8px 12px;color:#aaa">通過率</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">カレンダー表示 ÷ ACページ訪問 × 100</td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1;background:#fafaf8"><td style="padding:8px 12px">予約フォーム到達率</td><td style="padding:8px 12px;color:#aaa">通過率</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">予約フォーム表示 ÷ ACページ訪問 × 100<br><span style="font-size:12px;color:#aaa;font-family:inherit">※ カレンダーは任意ステップ（スキップ可）のため、直前のカレンダー表示ではなく ACページ訪問を母数とする</span></td></tr>' +
    '<tr style="border-bottom:1px solid #e8e6e1;background:#fafaf8"><td style="padding:8px 12px">予約完了率</td><td style="padding:8px 12px;color:#aaa">通過率</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">予約完了 ÷ 予約フォーム表示 × 100</td></tr>' +
    '<tr style="background:#fafaf8"><td style="padding:8px 12px">全体CVR</td><td style="padding:8px 12px;color:#aaa">通過率</td><td style="padding:8px 12px;font-family:\'DM Sans\',monospace;font-size:13px">予約完了 ÷ サイト訪問 × 100</td></tr>' +
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
