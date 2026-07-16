(function () {
  var css = document.createElement('style');
  css.textContent =
    '.site-layout{display:grid;grid-template-columns:240px minmax(0,1fr);gap:0;max-width:1500px;margin:0 auto;padding:20px 24px 24px 16px;transition:grid-template-columns .18s ease}' +
    '.site-layout.nav-collapsed{grid-template-columns:0 minmax(0,1fr)}' +
    '.site-nav{position:sticky;top:20px;align-self:start;padding:48px 10px 16px;max-height:calc(100vh - 40px);overflow-y:auto;background:#f0ede8;border-radius:16px;transition:opacity .15s ease,visibility .15s}' +
    '.site-layout.nav-collapsed .site-nav{opacity:0;visibility:hidden;pointer-events:none;overflow:hidden}' +
    /* Nav collapse toggle button (inside nav) */
    '.nav-collapse-btn{position:absolute;top:12px;right:12px;width:26px;height:26px;border:1px solid rgba(0,0,0,.1);background:#fff;border-radius:8px;cursor:pointer;font-size:13px;color:#666;display:flex;align-items:center;justify-content:center;padding:0;line-height:1;z-index:2;transition:background .12s}' +
    '.nav-collapse-btn:hover{background:#f5f2ec;color:#1a1a1a}' +
    /* Floating expand button (shown when nav is collapsed) */
    '.nav-expand-btn{position:fixed;top:24px;left:12px;width:32px;height:32px;border:1px solid rgba(0,0,0,.12);background:#fff;border-radius:10px;cursor:pointer;font-size:16px;color:#666;display:none;align-items:center;justify-content:center;padding:0;line-height:1;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.08);transition:background .12s}' +
    '.nav-expand-btn:hover{background:#f5f2ec;color:#1a1a1a}' +
    '.nav-expand-btn.visible{display:flex}' +
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
    /* Spot analysis group (collapsible) */
    '.site-nav .nav-spot-row{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:10px;cursor:pointer;margin:1px 0;color:#666;font-size:14px;transition:background .12s}' +
    '.site-nav .nav-spot-row:hover{background:rgba(255,255,255,.6);color:#1a1a1a}' +
    '.site-nav .nav-spot-row.has-active{color:#1a1a1a;font-weight:700}' +
    '.site-nav .nav-spot-row .nav-icon{flex-shrink:0;width:20px;height:20px;opacity:.45}' +
    '.site-nav .nav-spot-row.has-active .nav-icon{opacity:1}' +
    '.site-nav .nav-spot-row .nav-spot-label{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}' +
    '.site-nav .nav-spot-toggle{font-size:9px;color:#bbb;transition:transform .15s;line-height:1;flex-shrink:0}' +
    '.site-nav .nav-spot-toggle.open{transform:rotate(90deg)}' +
    '.site-nav .nav-spot-list{padding-left:4px;margin-bottom:2px}' +
    '.site-nav .nav-spot-item a{display:flex;align-items:center;gap:8px;padding:7px 10px 7px 16px;font-size:13px;color:#777;border-radius:8px;text-decoration:none;line-height:1.4;transition:background .12s}' +
    '.site-nav .nav-spot-item a:hover{background:rgba(255,255,255,.7);color:#1a1a1a}' +
    '.site-nav .nav-spot-item a.nav-active{background:#fff;color:#E8423F;font-weight:700;box-shadow:0 1px 4px rgba(0,0,0,.07)}' +
    '.site-nav .nav-spot-item .spot-dot{font-size:10px;color:#ccc;flex-shrink:0}' +
    '.site-nav .nav-spot-item a.nav-active .spot-dot{color:#E8423F}' +
    '.site-nav .spot-num{font-family:DM Sans,sans-serif;font-weight:900;font-size:11px;color:#aaa;flex-shrink:0;min-width:20px}' +
    '.site-nav .nav-spot-item a.nav-active .spot-num,.site-nav .nav-spot-parent.nav-active .spot-num{color:#E8423F}' +
    /* Nested spot children (sub-pages under a parent spot analysis) */
    '.site-nav .nav-spot-parent{display:flex;align-items:center;gap:8px;padding:7px 10px 7px 16px;font-size:13px;color:#777;border-radius:8px;text-decoration:none;line-height:1.4;cursor:pointer;transition:background .12s}' +
    '.site-nav .nav-spot-parent:hover{background:rgba(255,255,255,.7);color:#1a1a1a}' +
    '.site-nav .nav-spot-parent.has-active{color:#1a1a1a;font-weight:700}' +
    '.site-nav .nav-spot-parent-link{flex:1;color:inherit;text-decoration:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}' +
    '.site-nav .nav-spot-parent.nav-active{background:#fff;color:#E8423F;font-weight:700;box-shadow:0 1px 4px rgba(0,0,0,.07)}' +
    '.site-nav .nav-spot-parent.nav-active .nav-spot-parent-link{color:#E8423F}' +
    '.site-nav .nav-spot-parent .spot-dot{font-size:10px;color:#ccc;flex-shrink:0}' +
    '.site-nav .nav-spot-parent.nav-active .spot-dot,.site-nav .nav-spot-parent.has-active .spot-dot{color:#E8423F}' +
    '.site-nav .nav-spot-children{padding-left:14px;margin:2px 0 4px;border-left:1px dashed rgba(0,0,0,.1);margin-left:22px}' +
    '.site-nav .nav-spot-child a{display:flex;align-items:center;gap:6px;padding:5px 10px 5px 10px;font-size:12px;color:#888;border-radius:6px;text-decoration:none;line-height:1.3;transition:background .12s}' +
    '.site-nav .nav-spot-child a:hover{background:rgba(255,255,255,.7);color:#1a1a1a}' +
    '.site-nav .nav-spot-child a.nav-active{background:#fff;color:#E8423F;font-weight:700}' +
    '.site-nav .nav-spot-child .child-dot{font-size:9px;color:#ccc;flex-shrink:0}' +
    '.site-nav .nav-spot-child a.nav-active .child-dot{color:#E8423F}' +
    '.site-nav .nav-spot-parent-toggle{font-size:8px;color:#bbb;transition:transform .15s;line-height:1;flex-shrink:0;cursor:pointer;padding:2px 4px}' +
    '.site-nav .nav-spot-parent-toggle.open{transform:rotate(90deg)}' +
    /* Main area */
    '.site-main{min-width:0}' +
    '@media(max-width:900px){.site-layout{grid-template-columns:1fr;padding:0}.site-nav{display:none}.site-main{padding:0}}' +
    /* Breadcrumb */
    '#site-breadcrumb{display:flex;align-items:center;flex-wrap:wrap;font-size:13px;color:#aaa;margin-bottom:20px;padding-bottom:14px;border-bottom:1px solid rgba(0,0,0,.07)}' +
    '#site-breadcrumb a{color:#aaa;text-decoration:none;padding:2px 5px;border-radius:5px;transition:background .12s,color .12s}' +
    '#site-breadcrumb a:hover{background:rgba(0,0,0,.05);color:#333}' +
    '#site-breadcrumb .bc-sep{color:#ccc;margin:0 1px;font-size:12px;line-height:1}' +
    '#site-breadcrumb .bc-current{color:#333;font-weight:700;padding:2px 5px}';
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

  // ── Nav collapse toggle ──────────────────────────
  var collapseBtn = document.createElement('button');
  collapseBtn.className = 'nav-collapse-btn';
  collapseBtn.type = 'button';
  collapseBtn.setAttribute('aria-label', '左ナビをたたむ');
  collapseBtn.textContent = '‹';
  nav.appendChild(collapseBtn);

  var expandBtn = document.createElement('button');
  expandBtn.className = 'nav-expand-btn';
  expandBtn.type = 'button';
  expandBtn.setAttribute('aria-label', '左ナビを開く');
  expandBtn.textContent = '☰';
  document.body.appendChild(expandBtn);

  function setCollapsed(collapsed) {
    if (collapsed) {
      layout.classList.add('nav-collapsed');
      expandBtn.classList.add('visible');
    } else {
      layout.classList.remove('nav-collapsed');
      expandBtn.classList.remove('visible');
    }
    try { localStorage.setItem('veltra-nav-collapsed', collapsed ? '1' : '0'); } catch (e) {}
  }

  collapseBtn.addEventListener('click', function () { setCollapsed(true); });
  expandBtn.addEventListener('click', function () { setCollapsed(false); });

  try {
    if (localStorage.getItem('veltra-nav-collapsed') === '1') setCollapsed(true);
  } catch (e) {}

  // ── Page type detection ──────────────────────────
  // (breadcrumb inserted below after detection)
  var path = location.pathname;
  // week_id（例 2026-w15）を半期フォルダ込みのディレクトリ URL に変換する。
  // 2026 上半期 = W1〜W26 → 2026-h1、下半期 = W27〜 → 2026-h2。
  function weekDirFor(week) {
    var m = /^(\d{4})-w(\d+)$/.exec(week || '');
    if (!m) return '/reports/';
    return '/reports/' + m[1] + '-' + (parseInt(m[2], 10) <= 26 ? 'h1' : 'h2') + '/' + week + '/';
  }
  var isTop      = (path === '/' || path === '/index.html');
  var isCvr      = (path === '/cvr.html');
  var isKpi      = (path === '/kpi.html');
  var isCycle    = (path === '/cycle.html');
  var isAnalysis = (path === '/analysis.html');
  var isBehaviorGuide = (path === '/behavior-guide.html');
  var isEntryJourney = (path === '/entry-journey.html');
  var isPlanning = (path === '/planning/' || path === '/planning/index.html');
  var isPlanningItem = /^\/planning\/.+\.html$/.test(path) && !isPlanning;
  var isGwDecline = (path === '/spot/2026-gw-cvr-decline.html');
  var isGwMacro = (path === '/spot/2026-gw/01-macro.html');
  var isGwCompetitive = (path === '/spot/2026-gw/02-competitive.html');
  var isGwPricing = (path === '/spot/2026-gw/03-pricing.html');
  var isGwProduct = (path === '/spot/2026-gw/04-product.html');
  var isGwBehavior = (path === '/spot/2026-gw/05-customer-behavior.html');
  var isGwUiux = (path === '/spot/2026-gw/06-uiux.html');
  var isGwSub = isGwMacro || isGwCompetitive || isGwPricing || isGwProduct || isGwBehavior || isGwUiux;
  var isAcDiscovery = (path === '/spot/2026-ac-discovery.html');
  var isSurfaceWf = (path === '/spot/2026-surface-wireframes.html');
  var isMayJunCvr = /^\/spot\/2026-may-jun-cvr-trend(\.html)?$/.test(path);
  var isH1Wrap = /^\/spot\/2026-h1-cvr-wrap(\.html)?$/.test(path);
  var isH2UxMission = /^\/spot\/2026-h2-ux-squad-mission(\.html)?$/.test(path);
  var isVeltraTopSection = /^\/spot\/veltra-top-section-visibility(\.html)?$/.test(path);
  var isTaiwanSection = /^\/spot\/taiwan-section-visibility(\.html)?$/.test(path);
  var isJiufenSection = /^\/spot\/jiufen-category-section-visibility(\.html)?$/.test(path);
  var isAcSection = /^\/spot\/ac-page-section-visibility(\.html)?$/.test(path);
  var isPainFramework = /^\/spot\/traveler-pain-framework(\.html)?$/.test(path);
  var isAnySpot = isEntryJourney || isGwDecline || isGwSub || isAcDiscovery || isSurfaceWf || isMayJunCvr || isH1Wrap || isH2UxMission || isVeltraTopSection || isTaiwanSection || isJiufenSection || isAcSection || isPainFramework;
  var isArchive = (path === '/reports/' || path === '/reports/index.html');
  var isWeekSummary = !isArchive && /\/reports\/(?:\d{4}-h[12]\/)?\d{4}-w\d+\/(?:index\.html)?$/.test(path);
  var qp = new URLSearchParams(location.search);
  var isBottleneck  = /\/bottleneck\.html$/.test(path) && qp.has('num');
  var isReport = /\/report\.html$/.test(path) && qp.has('week');

  var weekDir = '';
  var bnNum   = 0;
  var currentWeekId = '';
  if (isWeekSummary) {
    weekDir = path.replace(/(?:index\.html)$/, '');
    if (!weekDir.endsWith('/')) weekDir += '/';
    var wm = weekDir.match(/(\d{4}-w\d+)/);
    if (wm) currentWeekId = wm[1];
  }
  if (isBottleneck) {
    currentWeekId = qp.get('week') || '';
    bnNum = parseInt(qp.get('num'), 10) || 0;
    weekDir = weekDirFor(currentWeekId);
  }
  if (isReport) {
    currentWeekId = qp.get('week') || '';
    weekDir = weekDirFor(currentWeekId);
  }

  // ── Breadcrumb ───────────────────────────────────
  var bcLastEl = null;
  (function () {
    if (isTop) return; // no breadcrumb on top page
    var bc = document.createElement('nav');
    bc.id = 'site-breadcrumb';

    function mkA(text, href) {
      var a = document.createElement('a');
      a.href = href;
      a.textContent = text;
      return a;
    }
    function mkSep() {
      var s = document.createElement('span');
      s.className = 'bc-sep';
      s.textContent = '›';
      return s;
    }
    function mkCurrent(text) {
      var s = document.createElement('span');
      s.className = 'bc-current';
      s.textContent = text;
      return s;
    }
    function append() {
      for (var i = 0; i < arguments.length; i++) {
        if (i > 0) bc.insertBefore(mkSep(), null);
        bc.appendChild(arguments[i]);
      }
    }

    var wid = currentWeekId ? currentWeekId.replace('2026-', '').toUpperCase() : '';
    var homeA = mkA('ホーム', '/');
    var bnA   = mkA('ボトルネック分析', '/reports/');

    if (isArchive) {
      append(homeA, mkCurrent('ボトルネック分析'));
    } else if (isKpi) {
      append(homeA, mkCurrent('KPIダッシュボード'));
    } else if (isCycle) {
      append(homeA, mkCurrent('CVR改善サイクル'));
    } else if (isAnalysis) {
      append(homeA, mkCurrent('分析ガイド'));
    } else if (isBehaviorGuide) {
      append(homeA, mkCurrent('行動仮説ガイド'));
    } else if (isEntryJourney) {
      append(homeA, mkCurrent('スポット分析'), mkCurrent('エントリー別CVRジャーニー'));
    } else if (isAcDiscovery) {
      append(homeA, mkCurrent('スポット分析'), mkCurrent('新規ユーザー転換｜探索分解と施策'));
    } else if (isSurfaceWf) {
      append(homeA, mkCurrent('スポット分析'), mkA('新規ユーザー転換｜探索分解と施策', '/spot/2026-ac-discovery.html'), mkCurrent('画面別 改修ワイヤー'));
    } else if (isVeltraTopSection) {
      append(homeA, mkCurrent('スポット分析'), mkCurrent('セクション閲覧｜ベルトラTOPページ'));
    } else if (isTaiwanSection) {
      append(homeA, mkCurrent('スポット分析'), mkCurrent('セクション閲覧｜台湾トップページ'));
    } else if (isJiufenSection) {
      append(homeA, mkCurrent('スポット分析'), mkCurrent('セクション閲覧｜九份カテゴリーページ'));
    } else if (isAcSection) {
      append(homeA, mkCurrent('スポット分析'), mkCurrent('セクション閲覧｜商品詳細(AC)ページ'));
    } else if (isMayJunCvr) {
      append(homeA, mkCurrent('スポット分析'), mkCurrent('繁忙期前のCVR反落｜何が伸びなかったか'));
    } else if (isH1Wrap) {
      append(homeA, mkCurrent('スポット分析'), mkCurrent('3-6月 CVR改善プロジェクト 振り返り'));
    } else if (isPainFramework) {
      append(homeA, mkCurrent('スポット分析'), mkCurrent('Traveler ペイン洗い出しフレームワーク'));
    } else if (isH2UxMission) {
      append(homeA, mkCurrent('スポット分析'), mkCurrent('UX Design Squad｜2026 H2 ミッション'));
    } else if (isPlanning) {
      append(homeA, mkCurrent('施策案'));
    } else if (isPlanningItem) {
      append(homeA, mkA('施策案', '/planning/'), mkCurrent('ドキュメント'));
    } else if (isGwDecline) {
      append(homeA, mkCurrent('スポット分析'), mkCurrent('2026 GW CVR 構造低下'));
    } else if (isGwSub) {
      var subLabel = isGwMacro ? '01 マクロ環境'
        : isGwCompetitive ? '02 競合シェア'
        : isGwPricing ? '03 価格戦略'
        : isGwProduct ? '04 商品'
        : isGwBehavior ? '05 顧客行動'
        : isGwUiux ? '06 UIUX 構造課題'
        : '';
      append(homeA, mkCurrent('スポット分析'), mkA('2026 GW CVR 構造低下', '/spot/2026-gw-cvr-decline.html'), mkCurrent(subLabel));
    } else if (isWeekSummary || isReport) {
      append(homeA, bnA, mkCurrent(wid));
    } else if (isBottleneck) {
      var weekHref = currentWeekId ? weekDirFor(currentWeekId) : '/reports/';
      var bnEl = mkCurrent('#' + bnNum);
      bcLastEl = bnEl;
      append(homeA, bnA, mkA(wid, weekHref), bnEl);
    } else {
      return;
    }
    main.insertBefore(bc, main.firstChild);
  })();

  // ── Expand state ─────────────────────────────────
  var expandedWeeks = {};
  var spotExpanded = isAnySpot; // default open when viewing any spot page
  var gwDeclineExpanded = isGwDecline || isGwSub; // sub-tree default open on its pages

  // ── Spot analysis registry ───────────────────────
  // Hierarchical: items may have a `children` array for sub-pages.
  // 新しい順（新しいものが上 = 大きい番号）。番号は描画時に position から自動採番。
  var SPOT_ITEMS = [
    { id: 'pain-framework', href: '/spot/traveler-pain-framework.html', label: 'Traveler ペイン洗い出しフレームワーク', match: function(){ return isPainFramework; } },
    { id: 'h2-ux-mission', href: '/spot/2026-h2-ux-squad-mission.html', label: 'UX Design Squad｜2026 H2 ミッション', match: function(){ return isH2UxMission; } },
    { id: 'h1-wrap', href: '/spot/2026-h1-cvr-wrap.html', label: '3-6月 CVR改善プロジェクト 振り返り', match: function(){ return isH1Wrap; } },
    { id: 'mayjun-cvr', href: '/spot/2026-may-jun-cvr-trend.html', label: '繁忙期前のCVR反落｜何が伸びなかったか', match: function(){ return isMayJunCvr; } },
    {
      id: 'ac-discovery',
      href: '/spot/2026-ac-discovery.html',
      label: '新規ユーザー転換｜探索分解と施策',
      match: function(){ return isAcDiscovery; },
      hasActiveChild: function(){ return isSurfaceWf; },
      children: [
        { id: 'surface-wf', href: '/spot/2026-surface-wireframes.html', label: '画面別 改修ワイヤー', match: function(){ return isSurfaceWf; } }
      ]
    },
    { id: 'sec-veltra-top', href: '/spot/veltra-top-section-visibility.html', label: 'セクション閲覧｜ベルトラTOPページ', match: function(){ return isVeltraTopSection; } },
    { id: 'sec-taiwan', href: '/spot/taiwan-section-visibility.html', label: 'セクション閲覧｜台湾トップページ', match: function(){ return isTaiwanSection; } },
    { id: 'sec-jiufen', href: '/spot/jiufen-category-section-visibility.html', label: 'セクション閲覧｜九份カテゴリーページ', match: function(){ return isJiufenSection; } },
    { id: 'sec-ac', href: '/spot/ac-page-section-visibility.html', label: 'セクション閲覧｜商品詳細(AC)ページ', match: function(){ return isAcSection; } },
    {
      id: 'gw-decline',
      href: '/spot/2026-gw-cvr-decline.html',
      label: '2026 GW CVR 構造低下',
      match: function(){ return isGwDecline; },
      hasActiveChild: function(){ return isGwSub; },
      children: [
        { id: 'gw-01', href: '/spot/2026-gw/01-macro.html',             label: '01 マクロ環境',    match: function(){ return isGwMacro; } },
        { id: 'gw-02', href: '/spot/2026-gw/02-competitive.html',       label: '02 競合シェア',    match: function(){ return isGwCompetitive; } },
        { id: 'gw-03', href: '/spot/2026-gw/03-pricing.html',           label: '03 価格戦略',      match: function(){ return isGwPricing; } },
        { id: 'gw-04', href: '/spot/2026-gw/04-product.html',           label: '04 商品',          match: function(){ return isGwProduct; } },
        { id: 'gw-05', href: '/spot/2026-gw/05-customer-behavior.html', label: '05 顧客行動',      match: function(){ return isGwBehavior; } },
        { id: 'gw-06', href: '/spot/2026-gw/06-uiux.html',              label: '06 UIUX 構造課題', match: function(){ return isGwUiux; } }
      ]
    },
    { id: 'entry-journey', href: '/entry-journey.html', label: 'エントリー別CVRジャーニー', match: function(){ return isEntryJourney; } }
  ];

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
    } else if (type === 'kpi') {
      // Target / bullseye
      addPath('M22 12h-4');
      addPath('M6 12H2');
      addPath('M12 6V2');
      addPath('M12 22v-4');
      var c1 = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      c1.setAttribute('cx','12'); c1.setAttribute('cy','12'); c1.setAttribute('r','8');
      svg.appendChild(c1);
      var c2 = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      c2.setAttribute('cx','12'); c2.setAttribute('cy','12'); c2.setAttribute('r','4');
      svg.appendChild(c2);
    } else if (type === 'analysis') {
      // Book with magnifier
      addPath('M4 19.5A2.5 2.5 0 0 1 6.5 17H20');
      addPath('M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z');
      addLine(9,7,15,7); addLine(9,11,13,11);
    } else if (type === 'planning') {
      // Lightbulb (idea / proposal)
      addPath('M9 18h6');
      addPath('M10 22h4');
      addPath('M12 2a7 7 0 0 0-4 12.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26A7 7 0 0 0 12 2z');
    }
    return svg;
  }

  // ── Render helpers ───────────────────────────────
  function bnLinkHref(w, n) {
    return '/bottleneck.html?week=' + w.week_id + '&num=' + n;
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
    toggle.style.cssText = 'flex-shrink:0;padding:4px 6px 4px 0';

    // Week ID + label as link to week summary
    var weekLink = document.createElement('a');
    weekLink.href = w.path;
    weekLink.style.cssText = 'display:flex;align-items:center;gap:6px;flex:1;min-width:0;text-decoration:none;color:inherit';
    if ((isWeekSummary || isReport) && isCurrentWeek) weekLink.style.fontWeight = '700';

    var idEl = document.createElement('span');
    idEl.className = 'nav-week-id';
    idEl.textContent = wid.toUpperCase();

    var labelEl = document.createElement('span');
    labelEl.className = 'nav-week-label';
    var rs = w.rolling_start || w.date_start || '';
    var re = w.rolling_end || w.date_end || '';
    var fmtFull = function(d) { return d ? d.slice(0,4) + '/' + d.slice(5).replace('-', '/') : ''; };
    var fmtShort = function(d) { return d ? d.slice(5).replace('-', '/') : ''; };
    labelEl.textContent = rs && re ? fmtFull(rs) + '〜' + fmtShort(re) : w.week_label;

    weekLink.appendChild(idEl);
    weekLink.appendChild(labelEl);

    header.appendChild(toggle);
    header.appendChild(weekLink);

    if (isLatest) {
      var badge = document.createElement('span');
      badge.className = 'nav-week-badge';
      badge.textContent = '最新';
      header.appendChild(badge);
    }

    var bnList = document.createElement('div');
    bnList.className = 'nav-bn-list';
    bnList.style.display = expanded ? 'block' : 'none';

    // "週次サマリー" as first item in the list
    var summaryItem = document.createElement('div');
    summaryItem.className = 'nav-bn-item';
    var summaryA = document.createElement('a');
    summaryA.href = w.path;
    if ((isWeekSummary || isReport) && isCurrentWeek) summaryA.className = 'nav-active';
    summaryA.style.cssText = 'font-weight:600;color:#555';
    var summaryIcon = document.createElement('span');
    summaryIcon.style.cssText = 'font-size:11px;color:#bbb;flex-shrink:0';
    summaryIcon.textContent = '≡';
    summaryA.appendChild(summaryIcon);
    summaryA.appendChild(document.createTextNode('週次サマリー'));
    summaryItem.appendChild(summaryA);
    bnList.appendChild(summaryItem);

    if (bns && bns.length) {
      bnList.dataset.bnAdded = '1';
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

    function doToggle() {
      var open = bnList.style.display !== 'none';
      bnList.style.display = open ? 'none' : 'block';
      toggle.className = 'nav-week-toggle' + (open ? '' : ' open');
      expandedWeeks[w.week_id] = !open;
    }
    // Arrow: toggle only
    toggle.addEventListener('click', function (e) { e.stopPropagation(); doToggle(); });
    // Week link (ID + label): navigate; stop bubble so header doesn't also toggle
    weekLink.addEventListener('click', function (e) { e.stopPropagation(); });
    // Rest of header row: toggle
    header.addEventListener('click', function (e) {
      if (toggle.contains(e.target) || weekLink.contains(e.target)) return;
      doToggle();
    });

    div.appendChild(header);
    div.appendChild(bnList);
    return div;
  }

  // ── Build full nav ────────────────────────────────
  function buildNav(weeks, weekDataMap) {
    nav.innerHTML = '';

    // Logo
    var logoArea = document.createElement('a');
    logoArea.href = '/';
    logoArea.style.textDecoration = 'none';
    logoArea.className = 'nav-logo';
    var logoImg = document.createElement('img');
    logoImg.src = '/veltra-logo.png';
    logoImg.onerror = function() { this.style.display='none'; };
    var logoText = document.createElement('div');
    logoText.className = 'nav-logo-text';
    logoText.innerHTML = 'UX Design Squad<br><span class="nav-logo-sub">Northstar</span>';
    logoArea.appendChild(logoImg);
    logoArea.appendChild(logoText);
    nav.appendChild(logoArea);

    nav.appendChild(makeSep());

    // ■ ホーム（Northstar hub）
    var homeA = document.createElement('a');
    homeA.href = '/';
    homeA.className = 'nav-item' + (isTop ? ' nav-active' : '');
    homeA.appendChild(makeIcon('summary'));
    homeA.appendChild(document.createTextNode('ホーム（Northstar）'));
    nav.appendChild(homeA);

    // ■ CVR サマリー
    var sumA = document.createElement('a');
    sumA.href = '/cvr.html';
    sumA.className = 'nav-item' + (isCvr ? ' nav-active' : '');
    sumA.appendChild(makeIcon('summary'));
    sumA.appendChild(document.createTextNode('CVR サマリー'));
    nav.appendChild(sumA);

    // ■ KPIダッシュボード
    var kpiA = document.createElement('a');
    kpiA.href = '/kpi.html';
    kpiA.className = 'nav-item' + (isKpi ? ' nav-active' : '');
    kpiA.appendChild(makeIcon('kpi'));
    kpiA.appendChild(document.createTextNode('KPIダッシュボード'));
    nav.appendChild(kpiA);

    // ■ 施策案（折りたたみ：manifest.json から子リンクを読み込む）
    var planExpanded = isPlanning || isPlanningItem;
    var planRow = document.createElement('div');
    planRow.className = 'nav-spot-row' + (isPlanning || isPlanningItem ? ' has-active' : '');
    planRow.appendChild(makeIcon('planning'));
    var planLabelWrap = document.createElement('a');
    planLabelWrap.href = '/planning/';
    planLabelWrap.className = 'nav-spot-label';
    planLabelWrap.style.cssText = 'color:inherit;text-decoration:none;display:block';
    planLabelWrap.textContent = '施策案';
    planRow.appendChild(planLabelWrap);
    var planToggle = document.createElement('span');
    planToggle.className = 'nav-spot-toggle' + (planExpanded ? ' open' : '');
    planToggle.textContent = '▶';
    planRow.appendChild(planToggle);

    var planList = document.createElement('div');
    planList.className = 'nav-spot-list';
    planList.style.display = planExpanded ? 'block' : 'none';
    var planLoading = document.createElement('div');
    planLoading.className = 'nav-spot-item';
    planLoading.style.cssText = 'padding:6px 16px;font-size:12px;color:#bbb';
    planLoading.textContent = '読み込み中…';
    planList.appendChild(planLoading);

    // Toggle: clicking the toggle (not the label) flips the list
    planToggle.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      var open = planList.style.display !== 'none';
      planList.style.display = open ? 'none' : 'block';
      planToggle.className = 'nav-spot-toggle' + (open ? '' : ' open');
      planExpanded = !open;
    });

    nav.appendChild(planRow);
    nav.appendChild(planList);

    // Populate planning sub-items async from manifest.json
    fetch('/planning/manifest.json', { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        var items = (data && data.items) || [];
        planList.innerHTML = '';
        if (!items.length) {
          var empty = document.createElement('div');
          empty.style.cssText = 'padding:6px 16px;font-size:12px;color:#bbb';
          empty.textContent = '（まだありません）';
          planList.appendChild(empty);
          return;
        }
        items.forEach(function (it) {
          var hasChildren = it.children && it.children.length > 0;
          var itemHref = '/planning/' + it.file;
          var isItemActive = (path === itemHref);
          var hasActiveChild = hasChildren && it.children.some(function (c) {
            return path === '/planning/' + c.file;
          });

          if (hasChildren) {
            // Parent with toggle and children list (mirrors spot-parent pattern)
            var parentRow = document.createElement('div');
            parentRow.className = 'nav-spot-parent' + (isItemActive ? ' nav-active' : (hasActiveChild ? ' has-active' : ''));

            var pDot = document.createElement('span');
            pDot.className = 'spot-dot';
            pDot.textContent = '●';
            parentRow.appendChild(pDot);

            var pLink = document.createElement('a');
            pLink.href = itemHref;
            pLink.className = 'nav-spot-parent-link';
            pLink.textContent = it.title || it.file;
            parentRow.appendChild(pLink);

            var childOpen = isItemActive || hasActiveChild;
            var pToggle = document.createElement('span');
            pToggle.className = 'nav-spot-parent-toggle' + (childOpen ? ' open' : '');
            pToggle.textContent = '▶';
            parentRow.appendChild(pToggle);
            planList.appendChild(parentRow);

            var childList = document.createElement('div');
            childList.className = 'nav-spot-children';
            childList.style.display = childOpen ? 'block' : 'none';
            it.children.forEach(function (c) {
              var ci = document.createElement('div');
              ci.className = 'nav-spot-child';
              var ca = document.createElement('a');
              ca.href = '/planning/' + c.file;
              if (path === '/planning/' + c.file) ca.className = 'nav-active';
              var cdot = document.createElement('span');
              cdot.className = 'child-dot';
              cdot.textContent = '●';
              ca.appendChild(cdot);
              ca.appendChild(document.createTextNode(c.title || c.file));
              ci.appendChild(ca);
              childList.appendChild(ci);
            });
            planList.appendChild(childList);

            pToggle.addEventListener('click', function (e) {
              e.preventDefault();
              e.stopPropagation();
              var open = childList.style.display !== 'none';
              childList.style.display = open ? 'none' : 'block';
              pToggle.className = 'nav-spot-parent-toggle' + (open ? '' : ' open');
            });
          } else {
            var item = document.createElement('div');
            item.className = 'nav-spot-item';
            var a = document.createElement('a');
            a.href = itemHref;
            if (isItemActive) a.className = 'nav-active';
            var dot = document.createElement('span');
            dot.className = 'spot-dot';
            dot.textContent = '●';
            a.appendChild(dot);
            a.appendChild(document.createTextNode(it.title || it.file));
            item.appendChild(a);
            planList.appendChild(item);
          }
        });
      })
      .catch(function () {
        planList.innerHTML = '';
        var err = document.createElement('div');
        err.style.cssText = 'padding:6px 16px;font-size:12px;color:#bbb';
        err.textContent = '読み込み失敗';
        planList.appendChild(err);
      });

    nav.appendChild(makeSep());

    // ■ スポット分析（折りたたみ）
    var hasActiveSpot = SPOT_ITEMS.some(function(s){ return s.match(); });
    var spotRow = document.createElement('div');
    spotRow.className = 'nav-spot-row' + (hasActiveSpot ? ' has-active' : '');
    spotRow.appendChild(makeIcon('analysis'));
    var spotLabel = document.createElement('span');
    spotLabel.className = 'nav-spot-label';
    spotLabel.textContent = 'スポット分析';
    spotRow.appendChild(spotLabel);
    var spotToggle = document.createElement('span');
    spotToggle.className = 'nav-spot-toggle' + (spotExpanded ? ' open' : '');
    spotToggle.textContent = '▶';
    spotRow.appendChild(spotToggle);

    var spotList = document.createElement('div');
    spotList.className = 'nav-spot-list';
    spotList.style.display = spotExpanded ? 'block' : 'none';

    SPOT_ITEMS.forEach(function (s, idx) {
      var spotNum = SPOT_ITEMS.length - idx; // 新しいものほど大きい番号（最上段が最大）
      if (s.children && s.children.length) {
        // Parent with children: parent row + toggle + children list
        var parentRow = document.createElement('div');
        var parentActive = s.match();
        var hasChildActive = s.hasActiveChild ? s.hasActiveChild() : false;
        parentRow.className = 'nav-spot-parent' + (parentActive ? ' nav-active' : (hasChildActive ? ' has-active' : ''));

        var pNum = document.createElement('span');
        pNum.className = 'spot-num';
        pNum.textContent = '#' + spotNum;
        parentRow.appendChild(pNum);

        var pLink = document.createElement('a');
        pLink.href = s.href;
        pLink.className = 'nav-spot-parent-link';
        pLink.textContent = s.label;
        pLink.addEventListener('click', function(ev){ ev.stopPropagation(); });
        parentRow.appendChild(pLink);

        var pToggle = document.createElement('span');
        var expanded = parentActive || hasChildActive || gwDeclineExpanded;
        pToggle.className = 'nav-spot-parent-toggle' + (expanded ? ' open' : '');
        pToggle.textContent = '▶';
        parentRow.appendChild(pToggle);

        spotList.appendChild(parentRow);

        var childList = document.createElement('div');
        childList.className = 'nav-spot-children';
        childList.style.display = expanded ? 'block' : 'none';
        s.children.forEach(function(c){
          var ci = document.createElement('div');
          ci.className = 'nav-spot-child';
          var ca = document.createElement('a');
          ca.href = c.href;
          if (c.match()) ca.className = 'nav-active';
          var cd = document.createElement('span');
          cd.className = 'child-dot';
          cd.textContent = '└';
          ca.appendChild(cd);
          ca.appendChild(document.createTextNode(c.label));
          ci.appendChild(ca);
          childList.appendChild(ci);
        });
        spotList.appendChild(childList);

        // Toggle children open/close on the row click (except when clicking the parent link)
        parentRow.addEventListener('click', function(ev){
          if (ev.target === pLink) return;
          var open = childList.style.display !== 'none';
          childList.style.display = open ? 'none' : 'block';
          pToggle.className = 'nav-spot-parent-toggle' + (open ? '' : ' open');
        });
      } else {
        // Flat item
        var item = document.createElement('div');
        item.className = 'nav-spot-item';
        var a = document.createElement('a');
        a.href = s.href;
        if (s.match()) a.className = 'nav-active';
        var num = document.createElement('span');
        num.className = 'spot-num';
        num.textContent = '#' + spotNum;
        a.appendChild(num);
        a.appendChild(document.createTextNode(s.label));
        item.appendChild(a);
        spotList.appendChild(item);
      }
    });

    spotRow.addEventListener('click', function () {
      var open = spotList.style.display !== 'none';
      spotList.style.display = open ? 'none' : 'block';
      spotToggle.className = 'nav-spot-toggle' + (open ? '' : ' open');
      spotExpanded = !open;
    });

    nav.appendChild(spotRow);
    nav.appendChild(spotList);

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

    // ■ 行動仮説ガイド
    var behaviorA = document.createElement('a');
    behaviorA.href = '/behavior-guide.html';
    behaviorA.className = 'nav-item' + (isBehaviorGuide ? ' nav-active' : '');
    behaviorA.appendChild(makeIcon('analysis'));
    behaviorA.appendChild(document.createTextNode('行動仮説ガイド'));
    nav.appendChild(behaviorA);

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
    if (bnList.dataset.bnAdded) return; // already populated
    bnList.dataset.bnAdded = '1';
    bns.forEach(function (bn) {
      var item = document.createElement('div');
      item.className = 'nav-bn-item';
      var a = document.createElement('a');
      a.href = '/bottleneck.html?week=' + weekId + '&num=' + bn.rank;
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
        if (currentWeekId) {
          // 特定の週を見ているとき: その週だけ開く（最新週は閉じる）
          expandedWeeks[currentWeekId] = true;
        } else {
          // 週ページ以外: 最新週をデフォルトで開く
          expandedWeeks[latestId] = true;
        }
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
            // Update breadcrumb title for bottleneck pages
            if (bcLastEl && currentWeekId === w.week_id && bnNum) {
              var currentBn = null;
              for (var bi = 0; bi < bns.length; bi++) {
                if (bns[bi].rank === bnNum) { currentBn = bns[bi]; break; }
              }
              if (currentBn) bcLastEl.textContent = '#' + bnNum + ' ' + currentBn.title;
            }
          })
          .catch(function () {});
      });
    })
    .catch(function () {
      buildNav([], {});
    });

})();
