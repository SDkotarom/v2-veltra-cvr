(function () {
  var css = document.createElement('style');
  css.textContent =
    '.site-layout{display:grid;grid-template-columns:240px minmax(0,1fr);gap:0;max-width:1500px;margin:0 auto;padding:20px 24px 24px 16px}' +
    '.site-nav{position:sticky;top:20px;align-self:start;padding:48px 10px 16px;max-height:calc(100vh - 40px);overflow-y:auto;background:#f0ede8;border-radius:16px}' +
    /* Logo area */
    '.site-nav .nav-logo{padding:10px 10px 12px;display:flex;align-items:center;gap:8px}' +
    '.site-nav .nav-logo img{width:28px;height:28px;object-fit:contain}' +
    '.site-nav .nav-logo-text{font-size:13px;font-weight:700;color:#1a1a1a;line-height:1.3;letter-spacing:.03em}' +
    '.site-nav .nav-logo-sub{font-size:11px;font-weight:400;color:#999;letter-spacing:.05em}' +
    /* Section label */
    '.site-nav .nav-label{font-size:12px;font-weight:700;color:#aaa;padding:10px 12px 4px;letter-spacing:.05em}' +
    /* Top-level nav items */
    '.site-nav .nav-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:10px;cursor:pointer;margin:1px 0;text-decoration:none;color:#666;font-size:14px;line-height:1.3;transition:background .12s}' +
    '.site-nav .nav-item:hover{background:rgba(255,255,255,.6);color:#1a1a1a}' +
    '.site-nav .nav-item.nav-active{background:#fff;color:#1a1a1a;font-weight:700;box-shadow:0 1px 6px rgba(0,0,0,.09)}' +
    '.site-nav .nav-item .nav-icon{flex-shrink:0;width:20px;height:20px;opacity:.45}' +
    '.site-nav .nav-item.nav-active .nav-icon{opacity:1}' +
    /* Separator */
    '.site-nav .nav-sep{border:none;border-top:1px solid rgba(0,0,0,.08);margin:6px 10px}' +
    /* Week accordion */
    '.site-nav .nav-week-row{display:flex;align-items:center;gap:8px;padding:8px 12px;border-radius:10px;cursor:pointer;margin:1px 0;transition:background .12s}' +
    '.site-nav .nav-week-row:hover{background:rgba(255,255,255,.6)}' +
    '.site-nav .nav-week-toggle{font-size:9px;color:#bbb;flex-shrink:0;transition:transform .15s;line-height:1}' +
    '.site-nav .nav-week-toggle.open{transform:rotate(90deg)}' +
    '.site-nav .nav-week-id{font-size:15px;font-weight:700;color:#E8423F;flex-shrink:0;font-family:"DM Sans",sans-serif}' +
    '.site-nav .nav-week-label{font-size:12px;color:#aaa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1}' +
    '.site-nav .nav-week-badge{font-size:11px;font-weight:700;background:#E8423F;color:#fff;padding:2px 8px;border-radius:8px;flex-shrink:0;white-space:nowrap}' +
    /* Bottleneck items */
    '.site-nav .nav-bn-list{padding-left:4px;margin-bottom:2px}' +
    '.site-nav .nav-bn-item a{display:flex;align-items:center;gap:6px;padding:7px 10px 7px 16px;font-size:14px;color:#777;border-radius:8px;text-decoration:none;line-height:1.4;transition:background .12s}' +
    '.site-nav .nav-bn-item a:hover{background:rgba(255,255,255,.7);color:#1a1a1a}' +
    '.site-nav .nav-bn-item a.nav-active{background:#fff;color:#E8423F;font-weight:700;box-shadow:0 1px 4px rgba(0,0,0,.07)}' +
    '.site-nav .nav-bn-item .bn-num{font-family:"DM Sans",sans-serif;font-weight:700;color:#ccc;font-size:12px;flex-shrink:0}' +
    '.site-nav .nav-bn-item a.nav-active .bn-num{color:#E8423F}' +
    /* Main area */
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
  var isTop      = (path === '/' || path === '/index.html');
  var isCycle    = (path === '/cycle.html');
  var isAnalysis = (path === '/analysis.html');
  var isArchive = (path === '/reports/' || path === '/reports/index.html');
  var isWeekSummary = !isArchive && (/\/reports\/\d{4}-w\d+\/$/.test(path) || /\/reports\/\d{4}-w\d+\/index\.html$/.test(path));
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
  var expandedWeeks = {};

  // ── SVG icons ────────────────────────────────────
  function icon(d, vb) {
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', vb || '0 0 20 20');
    svg.setAttribute('fill', 'currentColor');
    svg.className.baseVal = 'nav-icon';
    var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', d);
    svg.appendChild(path);
    return svg;
  }

  var ICONS = {
    summary: 'M3 3h6v6H3V3zm0 8h6v6H3v-6zm8-8h6v6h-6V3zm0 8h6v6h-6v-6z',
    bottleneck: 'M2 14h3v3H2v-3zm4-4h3v7H6v-7zm4-4h3v11h-3V6zm4-6h3v17h-3V0z',
    cycle: 'M10 2a8 8 0 1 0 0 16A8 8 0 0 0 10 2zm1 11.93V15a1 1 0 1 1-2 0v-1.07A6.002 6.002 0 0 1 4 8a1 1 0 0 1 2 0 4 4 0 0 0 4 4 1 1 0 0 1 1 1.93zM10 6a1 1 0 0 1 1 1v3.586l1.707 1.707a1 1 0 0 1-1.414 1.414l-2-2A1 1 0 0 1 9 11V7a1 1 0 0 1 1-1z',
  };

  // Better icons using clip paths
  function makeIcon(type) {
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '2');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');
    svg.className.baseVal = 'nav-icon';

    function addPath(d) {
      var p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      p.setAttribute('d', d);
      svg.appendChild(p);
    }
    function addRect(x, y, w, h, rx) {
      var r = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      r.setAttribute('x', x); r.setAttribute('y', y);
      r.setAttribute('width', w); r.setAttribute('height', h);
      if (rx) r.setAttribute('rx', rx);
      svg.appendChild(r);
    }
    function addLine(x1, y1, x2, y2) {
      var l = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      l.setAttribute('x1', x1); l.setAttribute('y1', y1);
      l.setAttribute('x2', x2); l.setAttribute('y2', y2);
      svg.appendChild(l);
    }
    function addPolyline(pts) {
      var pl = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
      pl.setAttribute('points', pts);
      svg.appendChild(pl);
    }

    if (type === 'summary') {
      // Grid 2×2
      addRect(3,3,7,7,1); addRect(14,3,7,7,1);
      addRect(3,14,7,7,1); addRect(14,14,7,7,1);
    } else if (type === 'bottleneck') {
      // Bar chart ascending
      addLine(18,20,18,10); addLine(12,20,12,4); addLine(6,20,6,14);
      addPolyline('2,20 22,20');
    } else if (type === 'cycle') {
      // Refresh arrows
      addPath('M23 4v6h-6');
      addPath('M1 20v-6h6');
      addPath('M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15');
    } else if (type === 'analysis') {
      // Book with magnifier
      addPath('M4 19.5A2.5 2.5 0 0 1 6.5 17H20');
      addPath('M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z');
      addLine(9,7,15,7); addLine(9,11,13,11);
    }
    return svg;
  }

  // ── Render helpers ───────────────────────────────
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
    var ds = w.date_start ? w.date_start.slice(5).replace('-', '/') : '';
    var de = w.date_end   ? w.date_end.slice(5).replace('-', '/') : '';
    labelEl.textContent = ds && de ? ds + '〜' + de : w.week_label;

    header.appendChild(toggle);
    header.appendChild(idEl);
    header.appendChild(labelEl);

    if (isLatest) {
      var badge = document.createElement('span');
      badge.className = 'nav-week-badge';
      badge.textContent = '最新';
      header.appendChild(badge);
    }

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
      var loading = document.createElement('div');
      loading.style.cssText = 'padding:6px 16px;font-size:11px;color:#bbb';
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

    // Logo
    var logoArea = document.createElement('div');
    logoArea.className = 'nav-logo';
    var logoImg = document.createElement('img');
    logoImg.src = '/veltra-logo.png';
    logoImg.onerror = function() { this.style.display='none'; };
    var logoText = document.createElement('div');
    logoText.className = 'nav-logo-text';
    logoText.innerHTML = 'VELTRA CVR REPORT<br><span class="nav-logo-sub">BOOKING BEHAVIOR ANALYSIS</span>';
    logoArea.appendChild(logoImg);
    logoArea.appendChild(logoText);
    nav.appendChild(logoArea);

    nav.appendChild(makeSep());

    // ■ サマリー
    var sumA = document.createElement('a');
    sumA.href = '/';
    sumA.className = 'nav-item' + (isTop ? ' nav-active' : '');
    sumA.appendChild(makeIcon('summary'));
    sumA.appendChild(document.createTextNode('サマリー'));
    nav.appendChild(sumA);

    nav.appendChild(makeSep());

    // ■ ボトルネック分析
    var bnA = document.createElement('a');
    bnA.href = '/reports/';
    bnA.className = 'nav-item' + (isArchive || isWeekSummary || isBottleneck ? ' nav-active' : '');
    bnA.appendChild(makeIcon('bottleneck'));
    bnA.appendChild(document.createTextNode('ボトルネック分析'));
    nav.appendChild(bnA);

    if (weeks && weeks.length) {
      var sorted = weeks.slice().reverse();
      sorted.forEach(function (w, i) {
        var isLatest = i === 0;
        var bns = weekDataMap[w.week_id] || null;
        nav.appendChild(renderWeekBlock(w, bns, isLatest));
      });
    }

    nav.appendChild(makeSep());

    // ■ CVR改善サイクル
    var cycleA = document.createElement('a');
    cycleA.href = '/cycle.html';
    cycleA.className = 'nav-item' + (isCycle ? ' nav-active' : '');
    cycleA.appendChild(makeIcon('cycle'));
    cycleA.appendChild(document.createTextNode('CVR改善サイクル'));
    nav.appendChild(cycleA);

    // ■ 分析ガイド
    var analysisA = document.createElement('a');
    analysisA.href = '/analysis.html';
    analysisA.className = 'nav-item' + (isAnalysis ? ' nav-active' : '');
    analysisA.appendChild(makeIcon('analysis'));
    analysisA.appendChild(document.createTextNode('分析ガイド'));
    nav.appendChild(analysisA);

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

  // ── Update bottleneck list after data loads ──────
  function updateWeekBnList(weekId, bns) {
    var block = nav.querySelector('[data-week-id="' + weekId + '"]');
    if (!block) return;
    var bnList = block.querySelector('.nav-bn-list');
    if (!bnList) return;
    var placeholder = bnList.querySelector('[data-placeholder]');
    if (placeholder) bnList.removeChild(placeholder);
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
      // 時系列順にソート（古い→新しい。最新が末尾）
      weeks.sort(function(a, b) { return a.week_id.localeCompare(b.week_id); });

      if (weeks.length) {
        var latestId = weeks[weeks.length - 1].week_id;
        expandedWeeks[latestId] = true;
        // 現在見ているページの週も開く（最新以外のページを直接開いた場合）
        if (currentWeekId && currentWeekId !== latestId) expandedWeeks[currentWeekId] = true;
      }

      buildNav(weeks, weekDataMap);

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
