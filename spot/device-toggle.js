// 全体 / PC / モバイル のトグル。data-all / data-pc / data-mb を持つ要素を切替時に書き換える。
// セクション閲覧分析ページ共通。データは各ページの data 属性に持つ（GA4 deviceCategory 集計値）。
(function () {
  var css =
    '.devtoggle{display:inline-flex;gap:4px;background:#eef2f7;border:1px solid #e2e8f0;border-radius:10px;padding:4px;margin:0 0 10px}' +
    '.devtoggle button{font:inherit;font-size:13px;font-weight:800;border:0;background:transparent;color:#3f4d60;padding:6px 16px;border-radius:7px;cursor:pointer;line-height:1.2}' +
    '.devtoggle button.on{background:#1b82c5;color:#fff;box-shadow:0 1px 3px rgba(0,0,0,.12)}' +
    '.devtoggle button:not(.on):hover{color:#1b82c5}' +
    '.dev-hint{font-size:12.5px;color:#7b8794;margin:0 0 14px;line-height:1.6}';
  var s = document.createElement('style');
  s.textContent = css;
  document.head.appendChild(s);

  var grp = document.querySelector('.devtoggle');
  if (!grp) return;

  function apply(dev) {
    document.querySelectorAll('[data-all]').forEach(function (el) {
      var v = el.getAttribute('data-' + dev);
      if (v !== null) el.textContent = v;
    });
    grp.querySelectorAll('button').forEach(function (b) {
      b.classList.toggle('on', b.getAttribute('data-dev') === dev);
    });
  }

  grp.addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (!b) return;
    apply(b.getAttribute('data-dev'));
  });
})();
