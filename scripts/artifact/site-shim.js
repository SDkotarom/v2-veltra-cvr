/* Artifact 配信用 shim。build.py が全ページの <head> 先頭に注入する。
 *
 * ページごとに build.py が先に書き出す 2 つの値を前提にする:
 *   window.__SITE_BASE__  そのページから見たサイトルートへの相対パス（例 "../../"）
 *   window.__SITE_PATH__  リポジトリ上のパス（例 "/2026h1/kpi.html"）
 *
 * 役割:
 *   1. ルート絶対パス（/summary-data.json 等）の fetch を相対パスへ解決する
 *   2. bottleneck-N-content.json を統合済み bottlenecks.json へ振り替える
 *   3. JS が実行時に組み立てた絶対パスの href / src を解決する
 *      （bottleneck.html の basePath のように、静的な書き換えでは届かない箇所）
 *
 * これによりページ側の JS を 1 行も書き換えずに済む。
 */
(function () {
  var BASE = window.__SITE_BASE__ || './';
  if (!window.fetch) return;
  var nativeFetch = window.fetch.bind(window);

  function resolve(url) {
    if (typeof url !== 'string') return url;
    if (url.charAt(0) === '#') return url;
    if (/^[a-z][a-z0-9+.-]*:/i.test(url) || url.indexOf('//') === 0) return url;
    if (url.charAt(0) !== '/') return url;
    return BASE + url.replace(/^\/+/, '');
  }

  var BOTTLENECK = /^(.*?)bottleneck-(\d+)-content\.json(\?.*)?$/;

  function jsonResponse(body, status) {
    return new Response(JSON.stringify(body), {
      status: status || 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  window.fetch = function (input, init) {
    var url = (typeof input === 'string') ? input
            : (input && typeof input.url === 'string') ? input.url
            : null;
    if (url === null) return nativeFetch(input, init);

    var m = BOTTLENECK.exec(url);
    if (m) {
      var key = m[2];
      return nativeFetch(resolve(m[1] + 'bottlenecks.json'), init).then(function (res) {
        if (!res.ok) return res;
        return res.json().then(function (all) {
          if (!all || !Object.prototype.hasOwnProperty.call(all, key)) {
            return jsonResponse({}, 404);
          }
          return jsonResponse(all[key]);
        });
      });
    }

    return nativeFetch(resolve(url), init);
  };

  /* --- 実行時に生成される絶対パスの解決 ---
   * ビルド時の書き換えは静的な markup にしか届かない。JS が後から差し込む
   * a[href^="/"] や img[src^="/"] はここで拾う。 */

  function fixAttr(el, attr) {
    var v = el.getAttribute(attr);
    if (!v || v.charAt(0) !== '/' || v.indexOf('//') === 0) return;
    el.setAttribute(attr, resolve(v));
  }

  function sweep(node) {
    if (!node || node.nodeType !== 1) return;
    if (node.matches && node.matches('a[href^="/"]')) fixAttr(node, 'href');
    if (node.matches && node.matches('[src^="/"]')) fixAttr(node, 'src');
    if (!node.querySelectorAll) return;
    var i, list = node.querySelectorAll('a[href^="/"]');
    for (i = 0; i < list.length; i++) fixAttr(list[i], 'href');
    list = node.querySelectorAll('[src^="/"]');
    for (i = 0; i < list.length; i++) fixAttr(list[i], 'src');
  }

  if (window.MutationObserver) {
    new MutationObserver(function (records) {
      for (var i = 0; i < records.length; i++) {
        var added = records[i].addedNodes;
        for (var j = 0; j < added.length; j++) sweep(added[j]);
      }
    }).observe(document.documentElement, { childList: true, subtree: true });
  }

  /* MutationObserver が走る前のクリックも取りこぼさない最後の砦 */
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    var href = a.getAttribute('href');
    if (!href || href.charAt(0) !== '/' || href.indexOf('//') === 0) return;
    e.preventDefault();
    location.href = resolve(href);
  }, true);

  /* ページ側が動的に遷移先を組み立てる場合の出口 */
  window.__site = resolve;
})();
