(function () {
  var css = document.createElement('style');
  css.textContent =
    '.site-layout{display:grid;grid-template-columns:260px minmax(0,1fr);gap:0;max-width:1500px;margin:0 auto;padding:24px 24px 24px 0}' +
    '.site-nav{position:sticky;top:24px;align-self:start;padding:12px 8px;font-size:13px;max-height:calc(100vh - 48px);overflow-y:auto}' +
    '.site-nav a{display:block;padding:5px 10px;color:#6b6b6b;text-decoration:none;border-radius:4px;line-height:1.4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}' +
    '.site-nav a:hover{background:#e8e6e1;color:#1a1a1a}' +
    '.site-nav a.nav-active{color:#E8423F;font-weight:700}' +
    '.site-nav .nav-sep{border:none;border-top:1px solid #e8e6e1;margin:8px 10px}' +
    '.site-nav .nav-section{font-size:12px;font-weight:700;color:#1a1a1a;padding:8px 10px 4px;letter-spacing:.02em}' +
    '.site-nav .nav-section a{display:inline;padding:0;color:#1a1a1a;font-weight:700;font-size:12px;white-space:normal;overflow:visible}' +
    '.site-nav .nav-section a:hover{background:none;color:var(--red,#E8423F)}' +
    '.site-nav .nav-section a.nav-active{color:#E8423F}' +
    '.site-nav .nav-week-row{display:flex;align-items:center;gap:4px;padding:5px 10px;cursor:pointer;border-radius:4px;user-select:none}' +
    '.site-nav .nav-week-row:hover{background:#e8e6e1}' +
    '.site-nav .nav-week-toggle{font-size:10px;color:#aaa;flex-shrink:0;transition:transform .15s;line-height:1}' +
    '.site-nav .nav-week-toggle.open{transform:rotate(90deg)}' +
    '.site-nav .nav-week-id{font-family:"DM Sans",sans-serif;font-size:13px;font-weight:700;color:#E8423F;flex-shrink:0}' +
    '.site-nav .nav-week-label{font-size:11px;color:#aaa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}' +
    '.site-nav .nav-week-badge{font-size:10px;font-weight:700;background:#E8423F;color:#fff;padding:1px 6px;border-radius:8px;flex-shrink:0;margin-left:auto}' +
    '.site-nav .nav-bn-list{padding-left:6px}' +
    '.site-nav .nav-bn-item a{padding:3px 10px 3px 14px;font-size:12px;color:#6b6b6b;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-decoration:none;border-radius:4px;line-height:1.5}' +
    '.site-nav .nav-bn-item a:hover{background:#e8e6e1;color:#1a1a1a}' +
    '.site-nav .nav-bn-item a.nav-active{color:#E8423F;font-weight:700}' +
    '.site-nav .nav-bn-item .bn-num{font-family:"DM Sans",sans-serif;font-weight:700;color:#aaa;margin-right:4px;font-size:11px}' +
    '.site-nav .nav-bn-item a.nav-active .bn-num{color:#E8423F}' +
    '.site-main{min-width:0}' +
    '@media(max-width:900px){.site-layout{grid-template-columns:1fr;padding:0}.site-nav{display:none}.site-main{padding:0}}';
  document.head.appendChild(css);

  document.body.style.maxWidth = 'none';
  document.body.style.padding = '0';
  document.body.style.margin = '0';

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

  // ── Page type detection ──────────────────────────
  var path = location.pathname;
  var isTop    = (path === '/' || path === '/index.html');
  var isCycle  = (path === '/cycle.html');
  var isWeekSummary = /\/reports\/\d{4}-w\d+\/$/.test(path) || /\/reports\/\d{4}-w\d+\/index\.html$/.test(path);
  var isBottleneck  = /bottleneck-\d+\.html$/.test(path);

  var weekDir = '';
  var bnNum   = 0;
  var currentWeekId = '';
  if (isWeekSummary || isBottleneck) {
    weekDir = path.replace(/(?:index\.html|bottleneck-\d+\.html)$/, '');
    if (!weekDir.endsWith('/')) weekDir += '/';
    var wm = weekDir.match(/(\d{4}-w\d+)/);
    if (wm) currentWeekId = wm[1];
  }
  if (isBottleneck) {
    var bm = path.match(/bottleneck-(\d+)\.html$/);
    bnNum = bm ? parseInt(bm[1]) : 0;
  }

  // ── Expand state ─────────────────────────────────
  // latest week always expanded; current week expanded on report pages
  var expandedWeeks = {};

  // ── Render helpers ───────────────────────────────
  function weekLinkHref(w) {
    return w.path;
  }

  function bnLinkHref(w, n) {
    return w.path + 'bottleneck-' + n + '.html';
  }

  function renderWeekBlock(w, bns, isLatest) {
    var wid   = w.week_id.replace('2026-', '');
    var isCurrentWeek = (currentWeekId && w.week_id === currentWeekId);
    var expanded = expandedWeeks[w.week_id];

    var div = document.createElement('div');
    div.className = 'nav-week-block';
    div.dataset.weekId = w.week_id;

    // Week header row
    var header = document.createElement('div');
    header.className = 'nav-week-row';

    var toggle = document.createElement('span');
    toggle.className = 'nav-week-toggle' + (expanded ? ' open' : '');
    toggle.textContent = '▶';

    var idEl = document.createElement('span');
    idEl.className = 'nav-week-id';
    idEl.textContent = wid;

    var labelEl = document.createElement('span');
    labelEl.className = 'nav-week-label';
    // "3/30〜4/5" format
    var ds = w.date_start ? w.date_start.slice(5).replace('-', '/') : '';
    var de = w.date_end   ? w.date_end.slice(5).replace('-', '/') : '';
    labelEl.textContent = ds && de ? '(' + ds + '〜' + de + ')' : w.week_label;

    header.appendChild(toggle);
    header.appendChild(idEl);
    header.appendChild(labelEl);

    if (isLatest) {
      var badge = document.createElement('span');
      badge.className = 'nav-week-badge';
      badge.textContent = '最新';
      header.appendChild(badge);
    }

    // Bottleneck list
    var bnList = document.createElement('div');
    bnList.className = 'nav-bn-list';
    bnList.style.display = expanded ? 'block' : 'none';

    if (bns && bns.length) {
      bns.forEach(function (bn) {
        var item = document.createElement('div');
        item.className = 'nav-bn-item';
        var a = document.createElement('a');
        a.href = bnLinkHref(w, bn.rank);
        if (isCurrentWeek && bn.rank === bnNum) a.className = 'nav-active';
        var num = document.createElement('span');
        num.className = 'bn-num';
        num.textContent = '#' + bn.rank;
        a.appendChild(num);
        a.appendChild(document.createTextNode(bn.title));
        item.appendChild(a);
        bnList.appendChild(item);
      });
    } else {
      // Placeholder while loading
      var loading = document.createElement('div');
      loading.style.cssText = 'padding:3px 14px;font-size:11px;color:#bbb';
      loading.textContent = '読み込み中...';
      loading.dataset.placeholder = '1';
      bnList.appendChild(loading);
    }

    header.addEventListener('click', function () {
      var open = bnList.style.display !== 'none';
      bnList.style.display = open ? 'none' : 'block';
      toggle.className = 'nav-week-toggle' + (open ? '' : ' open');
      expandedWeeks[w.week_id] = !open;
    });

    div.appendChild(header);
    div.appendChild(bnList);
    return div;
  }

  // ── Build full nav ────────────────────────────────
  function buildNav(weeks, weekDataMap) {
    nav.innerHTML = '';

    // ■ サマリー
    var sumSection = document.createElement('div');
    sumSection.className = 'nav-section';
    var sumA = document.createElement('a');
    sumA.href = '/';
    sumA.textContent = '■ サマリー';
    if (isTop) sumA.className = 'nav-active';
    sumSection.appendChild(sumA);
    nav.appendChild(sumSection);

    nav.appendChild(makeSep());

    // ■ ボトルネック分析
    var bnSection = document.createElement('div');
    bnSection.className = 'nav-section';
    bnSection.textContent = '■ ボトルネック分析';
    nav.appendChild(bnSection);

    if (weeks && weeks.length) {
      var sorted = weeks.slice().reverse(); // latest first
      sorted.forEach(function (w, i) {
        var isLatest = i === 0;
        var bns = weekDataMap[w.week_id] || null;
        var block = renderWeekBlock(w, bns, isLatest);
        nav.appendChild(block);
      });
    }

    nav.appendChild(makeSep());

    // ■ CVR改善サイクル
    var cycleSection = document.createElement('div');
    cycleSection.className = 'nav-section';
    var cycleA = document.createElement('a');
    cycleA.href = '/cycle.html';
    cycleA.textContent = '■ CVR改善サイクル';
    if (isCycle) cycleA.className = 'nav-active';
    cycleSection.appendChild(cycleA);
    nav.appendChild(cycleSection);

    // Smooth scroll for hash links
    nav.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a || !a.hash) return;
      var target = document.querySelector(a.hash);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  }

  function makeSep() {
    var hr = document.createElement('hr');
    hr.className = 'nav-sep';
    return hr;
  }

  // ── Update bottleneck list for a week after data loads ──
  function updateWeekBnList(weekId, bns) {
    var block = nav.querySelector('[data-week-id="' + weekId + '"]');
    if (!block) return;
    var bnList = block.querySelector('.nav-bn-list');
    if (!bnList) return;
    // Remove placeholder
    var placeholder = bnList.querySelector('[data-placeholder]');
    if (placeholder) bnList.removeChild(placeholder);
    // Add items if list is still empty
    if (!bnList.children.length) {
      var wInfo = null;
      if (reportsIndex) {
        reportsIndex.weeks.forEach(function(w){ if(w.week_id===weekId) wInfo=w; });
      }
      bns.forEach(function (bn) {
        var item = document.createElement('div');
        item.className = 'nav-bn-item';
        var a = document.createElement('a');
        var weekPath = wInfo ? wInfo.path : '/reports/' + weekId + '/';
        a.href = weekPath + 'bottleneck-' + bn.rank + '.html';
        if (currentWeekId === weekId && bn.rank === bnNum) a.className = 'nav-active';
        var num = document.createElement('span');
        num.className = 'bn-num';
        num.textContent = '#' + bn.rank;
        a.appendChild(num);
        a.appendChild(document.createTextNode(bn.title));
        item.appendChild(a);
        bnList.appendChild(item);
      });
    }
  }

  // ── Load data ─────────────────────────────────────
  var reportsIndex = null;
  var weekDataMap  = {};

  fetch('/reports-index.json')
    .then(function (r) { return r.json(); })
    .then(function (idx) {
      reportsIndex = idx;
      var weeks = idx.weeks || [];

      // Determine which weeks to expand by default
      if (weeks.length) {
        var latestId = weeks[weeks.length - 1].week_id;
        expandedWeeks[latestId] = true;
        if (currentWeekId) expandedWeeks[currentWeekId] = true;
      }

      // Initial render (without bottleneck titles yet)
      buildNav(weeks, weekDataMap);

      // Load data.json for each week
      weeks.forEach(function (w) {
        fetch(w.data_path)
          .then(function (r) { return r.json(); })
          .then(function (d) {
            var bns = (d.bottlenecks || []).map(function(bn){
              return { rank: bn.rank, title: bn.title };
            });
            weekDataMap[w.week_id] = bns;
            updateWeekBnList(w.week_id, bns);
          })
          .catch(function () {});
      });
    })
    .catch(function () {
      buildNav([], {});
    });

})();
