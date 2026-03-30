(function () {
  var host = location.hostname;
  if (host === 'localhost' || host === '127.0.0.1' || host === '') {
    // local: still render nav
  }

  // Inject CSS
  var css = document.createElement('style');
  css.textContent =
    '.site-layout{display:grid;grid-template-columns:200px minmax(0,1fr);gap:0;max-width:1440px;margin:0 auto;padding:24px 24px 24px 0}' +
    '.site-nav{position:sticky;top:24px;align-self:start;padding:16px 12px;font-size:13px;max-height:calc(100vh - 48px);overflow-y:auto}' +
    '.site-nav a{display:block;padding:5px 10px;color:#6b6b6b;text-decoration:none;border-radius:4px;line-height:1.5}' +
    '.site-nav a:hover{background:#e8e6e1;color:#1a1a1a}' +
    '.site-nav a.nav-active{color:#E8423F;font-weight:700}' +
    '.site-nav .nav-sep{border:none;border-top:1px solid #e8e6e1;margin:8px 10px}' +
    '.site-nav .nav-head{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#aaa;padding:10px 10px 4px;margin-top:4px}' +
    '.site-main{min-width:0}' +
    '@media(max-width:900px){.site-layout{grid-template-columns:1fr;padding:0}.site-nav{display:none}.site-main{padding:0}}';
  document.head.appendChild(css);

  // Override body styles for layout
  document.body.style.maxWidth = 'none';
  document.body.style.padding = '0';
  document.body.style.margin = '0';

  // Wrap body contents
  var children = Array.prototype.slice.call(document.body.childNodes);
  var layout = document.createElement('div');
  layout.className = 'site-layout';

  var nav = document.createElement('nav');
  nav.className = 'site-nav';

  var main = document.createElement('div');
  main.className = 'site-main';
  main.style.padding = '48px 32px';
  main.style.maxWidth = '1200px';

  children.forEach(function (c) { main.appendChild(c); });
  layout.appendChild(nav);
  layout.appendChild(main);
  document.body.appendChild(layout);

  // Determine page type and build nav
  var path = location.pathname;
  var links = '';

  if (path === '/' || path === '/index.html') {
    // Top page: auto-detect sections
    links = '<div class="nav-head">セクション</div>';
    var sections = main.querySelectorAll('.sec-label');
    sections.forEach(function (el, i) {
      var id = 'sec-' + i;
      el.id = id;
      var text = el.textContent.trim().replace(/\s*（[^）]*）/g, '').replace(/\s*\([^)]*\)/g, '');
      links += '<a href="#' + id + '">' + text + '</a>';
    });
    links += '<hr class="nav-sep">';
    links += '<div class="nav-head">レポート</div>';
    links += '<a href="/reports/2026-w14/">W14 レポート →</a>';

  } else if (/\/reports\/\d{4}-w\d+\/index\.html$/.test(path) || /\/reports\/\d{4}-w\d+\/$/.test(path)) {
    // Weekly summary page
    links = '<a href="/">← トップ</a>';
    links += '<hr class="nav-sep">';
    links += '<div class="nav-head">このレポート</div>';
    var sections = main.querySelectorAll('.sec-label');
    sections.forEach(function (el, i) {
      var id = 'sec-' + i;
      el.id = id;
      var text = el.textContent.trim().replace(/\s*（[^）]*）/g, '').replace(/\s*\([^)]*\)/g, '');
      links += '<a href="#' + id + '">' + text + '</a>';
    });
    links += '<hr class="nav-sep">';
    links += '<div class="nav-head">個別ページ</div>';
    for (var n = 2; n <= 10; n++) {
      links += '<a href="bottleneck-' + n + '.html">#' + n + ' 詳細</a>';
    }

  } else if (/bottleneck-\d+\.html$/.test(path)) {
    // Bottleneck detail page
    var match = path.match(/bottleneck-(\d+)\.html$/);
    var num = match ? parseInt(match[1]) : 0;
    var weekDir = path.replace(/bottleneck-\d+\.html$/, '');

    links = '<a href="' + weekDir + '">← サマリー</a>';
    links += '<a href="/">← トップ</a>';
    links += '<hr class="nav-sep">';
    links += '<div class="nav-head">ボトルネック</div>';
    for (var n = 2; n <= 10; n++) {
      var cls = (n === num) ? ' class="nav-active"' : '';
      links += '<a' + cls + ' href="bottleneck-' + n + '.html">#' + n + '</a>';
    }
  }

  nav.innerHTML = links;

  // Smooth scroll for anchor links
  nav.addEventListener('click', function (e) {
    var a = e.target.closest('a');
    if (!a || !a.hash) return;
    var target = document.querySelector(a.hash);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
})();
