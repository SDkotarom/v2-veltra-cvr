/* ─────────────────────────────────────────────
   週次サマリーページ の「詳細セクション」を描画
   - ファネルサマリー（28日ベースライン, 4 columns）
   - KPIストリップ（28日: セッション / CV / CVR）
   - ボトルネック分析 進捗バー
   - ボトルネック10件リスト（アコーディオン）

   使い方:
     <div id="summary-detail"></div>
     <script src="/summary-detail.js"></script>

   - 現在URLから /reports/{YYYY-wNN}/ を抽出し、./data.json を fetch
   ───────────────────────────────────────────── */
(function(){
  var m = location.pathname.match(/\/reports\/([\w-]+)\//);
  if (!m) return;
  var week = m[1];

  var STAGE_LABELS = {
    '1→2': '①→② 流入→AC到達',
    '2→3': '②→③ AC到達→検討',
    '3→4': '③→④ 検討→意向',
    '4→5': '④→⑤ 意向→完了',
    'all':  '全ステップ'
  };
  var STAGE_NAMES = {
    '1_to_2': { step: '①→②', name: '流入 → AC到達', metric: 'ac_page_reach_users' },
    '2_to_3': { step: '②→③', name: 'AC到達 → 検討', metric: 'calendar_view' },
    '3_to_4': { step: '③→④', name: '検討 → 意向', metric: 'form_start' },
    '4_to_5': { step: '④→⑤', name: '意向 → 完了', metric: 'purchase' }
  };
  var STATUS_META = {
    pending:       { icon: '○', label: '未着手',     color: '#999',    bg: '#F5F5F5' },
    analysis_done: { icon: '◔', label: '分析完了',   color: '#E88B00', bg: '#FFF4E0' },
    action_done:   { icon: '◑', label: '打ち手完了', color: '#1B82C5', bg: '#EBF4FA' },
    complete:      { icon: '✓', label: '完了',       color: '#2DAE6C', bg: '#E6F8EE' }
  };

  function pctFmt(v) { return (v * 100).toFixed(1) + '%'; }
  function ppFmt(v)  { return (v > 0 ? '+' : '') + (v * 100).toFixed(2) + 'pp'; }
  function fmtK(n)   { return n >= 1000000 ? (n/1000000).toFixed(0) + 'M' : n >= 1000 ? Math.round(n/1000) + 'K' : n.toString(); }
  function fmtNum(n) { return n.toLocaleString(); }

  fetch('./data.json')
    .then(function(r){ if(!r.ok) throw new Error(r.status); return r.json(); })
    .then(function(data){ render(data); })
    .catch(function(err){
      var el = document.getElementById('summary-detail');
      if (el) el.innerHTML = '<div class="card" style="padding:40px 44px;text-align:center;color:var(--red)">詳細データ読み込み失敗: ' + err.message + '</div>';
    });

  function render(data) {
    var target = document.getElementById('summary-detail');
    if (!target) return;
    var meta = data.meta || {};
    var bl = data.baseline || {};
    var cr = bl.conversion_rates || {};
    var wow = cr.wow_pp || {};
    var funnel = bl.funnel || {};
    var bns = data.bottlenecks || [];

    var rollingLabel = meta.rolling_start && meta.rolling_end ?
      meta.rolling_start.replace(/-/g,'/') + '〜' + meta.rolling_end.replace(/-/g,'/') : '';

    var html = '';

    // ── ファネルサマリー 28日 ──
    html += '<div class="card">';
    html += '<div class="sec-tag"><span class="sec-num">詳細</span><span class="sec-main">28日ベースライン（' + rollingLabel + '）</span></div>';
    html += '<div class="sec-big" style="padding-bottom:16px">ファネル通過率とCV推移</div>';
    html += '<hr class="divider-solid">';
    html += '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0;padding:28px 44px">';

    var steps = ['1_to_2','2_to_3','3_to_4','4_to_5'];
    steps.forEach(function(key, i){
      var s = STAGE_NAMES[key];
      var rate = cr[key] || 0;
      var wowVal = wow[key] || 0;
      var wowAbs = Math.abs(wowVal * 100);
      var isUp = wowVal > 0;
      var wowColor = isUp ? '#1a8c4e' : '#c0392b';
      var wowBg = isUp ? '#e6f7ee' : '#fdecea';
      var wowArrow = isUp ? '▲' : '▼';
      var metricVal = funnel[s.metric] || 0;
      var border = i < 3 ? 'border-right:1px solid var(--border);' : '';

      html += '<div style="padding:0 16px;' + border + '">';
      html += '<div style="font-size:13px;font-weight:700;color:var(--text3);letter-spacing:.06em;margin-bottom:10px">' + s.step + '</div>';
      html += '<div style="font-size:16px;font-weight:700;margin-bottom:8px">' + s.name + '</div>';
      html += '<div style="display:flex;align-items:baseline;gap:8px;margin-bottom:8px">';
      html += '<div style="font-family:\'DM Sans\';font-size:32px;font-weight:900;line-height:1">' + pctFmt(rate) + '</div>';
      html += '<div style="font-size:12px;font-weight:700;padding:2px 6px;border-radius:4px;color:' + wowColor + ';background:' + wowBg + '">' + wowArrow + wowAbs.toFixed(1) + 'pp</div>';
      html += '</div>';
      html += '<div style="height:6px;background:var(--border);border-radius:3px;margin-bottom:6px"><div style="height:6px;border-radius:3px;background:var(--red);width:' + pctFmt(rate) + '"></div></div>';
      html += '<div style="font-size:13px;color:var(--text3);line-height:1.6">' + fmtK(metricVal) + ' ' + s.metric.replace(/_/g,' ') + '</div>';
      html += '</div>';
    });
    html += '</div>';

    // ── KPI Strip 28d ──
    html += '<div style="display:flex;align-items:center;gap:28px;padding:0 44px 28px;flex-wrap:wrap">';
    html += '<div style="display:flex;align-items:center;gap:28px;padding:14px 20px;background:var(--bg);border-radius:8px;flex:1;flex-wrap:wrap">';
    html += '<div><div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--text3)">セッション数（28日）</div>';
    html += '<div style="font-family:\'DM Sans\';font-size:22px;font-weight:900">' + fmtNum(bl.sessions || 0) + '</div></div>';
    html += '<div style="width:1px;height:36px;background:var(--border)"></div>';
    html += '<div><div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--text3)">CV数（28日）</div>';
    html += '<div style="font-family:\'DM Sans\';font-size:22px;font-weight:900">' + fmtNum(bl.purchases || 0) + '</div></div>';
    html += '<div style="width:1px;height:36px;background:var(--border)"></div>';
    html += '<div><div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--text3)">CVR（28日）</div>';
    html += '<div style="font-family:\'DM Sans\';font-size:22px;font-weight:900;color:var(--red)">' + pctFmt(bl.cvr || 0) + '</div></div>';
    html += '</div></div>';
    html += '</div>';

    // ── Progress ──
    var progress = data.progress || null;
    var progStatusMap = {};
    var progOverall = { completed: 0, total: bns.length || 10, percentage: 0 };
    if (progress) {
      (progress.bottlenecks || []).forEach(function(p){ progStatusMap[p.rank] = p; });
      progOverall = progress.overall || progOverall;
    }

    html += '<div class="card">';
    html += '<div class="sec-tag"><span class="sec-num">詳細</span><span class="sec-main">ボトルネック分析 進捗</span></div>';
    html += '<hr class="divider-solid">';
    html += '<div style="padding:20px 44px 28px">';
    var progPct = Math.round(progOverall.percentage || 0);
    html += '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">';
    html += '<div style="font-size:14px;font-weight:700;color:var(--text2)">分析進捗</div>';
    html += '<div style="font-size:13px;color:var(--text3)"><strong style="color:var(--text1);font-size:16px">' + (progOverall.completed || 0) + '</strong> / ' + (progOverall.total || 10) + ' 件完了（' + progPct + '%）</div>';
    html += '</div>';
    html += '<div style="background:#F5F5F5;height:12px;border-radius:6px;overflow:hidden">';
    html += '<div style="background:linear-gradient(90deg,#2DAE6C 0%,#1B82C5 100%);height:100%;width:' + progPct + '%;transition:width .4s"></div>';
    html += '</div>';
    if (progress && progress.updated_at) {
      html += '<div style="margin-top:6px;font-size:11px;color:var(--text3);text-align:right">最終更新: ' + progress.updated_at.substring(0,16).replace('T',' ') + '</div>';
    }
    html += '</div></div>';

    // ── Bottleneck List ──
    html += '<div class="card">';
    html += '<div class="sec-tag"><span class="sec-num">詳細</span><span class="sec-main">ボトルネック10件（全リスト）</span></div>';
    html += '<hr class="divider-solid">';
    html += '<div class="bn-acc">';

    bns.forEach(function(bn){
      var stageLabel = STAGE_LABELS[bn.stage] || bn.stage;
      var gapPct = Math.round(Math.abs(bn.gap) * 100);
      var link = '/bottleneck.html?week=' + week + '&num=' + bn.rank;

      var bnProg = progStatusMap[bn.rank] || { status: 'pending', proto_done: 0, proto_total: 9 };
      var sm = STATUS_META[bnProg.status] || STATUS_META.pending;
      var statusExtra = '';
      if (bnProg.status === 'action_done' && bnProg.proto_done != null) {
        statusExtra = ' ' + bnProg.proto_done + '/' + (bnProg.proto_total || 9);
      }
      var statusBadge = '<span style="display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:700;color:' + sm.color + ';background:' + sm.bg + ';padding:3px 8px;border-radius:10px;white-space:nowrap">' + sm.icon + ' ' + sm.label + statusExtra + '</span>';

      html += '<div class="bn-acc-item">';
      html += '<a class="bn-acc-header" href="' + link + '">';
      html += '<div class="bn-acc-rank">#' + bn.rank + '</div>';
      html += '<div class="bn-acc-body">';
      html += '<div class="bn-acc-title">' + bn.title + '</div>';
      html += '<div class="bn-acc-tags"><span class="bn-acc-tag red">' + stageLabel + '</span>';
      html += '<span class="bn-acc-tag">' + bn.segment + '</span>' + statusBadge + '</div>';
      html += '</div>';
      html += '<div class="bn-acc-meta"><div class="bn-acc-gap-label">全体比乖離</div><div class="bn-acc-gap">-' + gapPct + '%</div></div>';
      html += '<div class="bn-acc-arrow">→</div>';
      html += '</a>';

      var summary = bn.summary || bn.title + '。全体比 -' + gapPct + '%。月間 ' + fmtK(bn.impact_sessions) + ' セッションに影響。';
      html += '<div class="bn-acc-detail"><div class="bn-acc-hypo">' + summary + '</div></div>';

      html += '</div>';
    });

    html += '</div></div>';

    target.innerHTML = html;
  }
})();
