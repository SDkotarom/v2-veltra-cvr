(function () {
  var P = window.__PERF, off = {}, tableMetric = "lcp";

  function fmt(v, dec, unit) {
    if (v === null || v === undefined) return "—";
    var s = dec ? v.toFixed(dec) : Math.round(v).toLocaleString();
    return unit ? s + " " + unit : s;
  }
  function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c]; }); }
  function key(m, p) { return m + "|" + p; }
  function on(m, p) { return !off[key(m, p)]; }
  function days(a, b) { return (Date.parse(b) - Date.parse(a)) / 86400000; }

  /* 時間軸。左右に余白を持たせ、端のリリース点が切れないようにする */
  function scaleX(from, to, x0, x1) {
    var t0 = Date.parse(from), t1 = Date.parse(to);
    var pad = Math.max((t1 - t0) * 0.045, 6 * 86400000);
    var a = t0 - pad, b = t1 + pad;
    return function (d) { return x0 + (Date.parse(d) - a) / (b - a) * (x1 - x0); };
  }

  /* ---- チャート描画。表示中の系列だけで縦軸を張り直す ---- */
  function drawChart(mk) {
    var meta = P.meta[mk], host = document.getElementById("plot-" + mk);
    if (!host) return;
    var W = 560, H = 230, PL = 52, PR = 14, PT = 16, PB = 30;
    var weeks = P.weeks, series = P.metrics[mk];
    var shown = P.pages.filter(function (p) {
      return on(mk, p.key) && series[p.key] && series[p.key].some(function (v) { return v !== null; });
    });

    var vals = [];
    shown.forEach(function (p) {
      series[p.key].forEach(function (v) { if (v !== null) vals.push(v); });
    });
    vals.push(meta.good);
    var top = Math.max.apply(null, vals) * 1.12 || 1;
    var step = Math.pow(10, Math.floor(Math.log10(top / 3)));
    [1, 2, 2.5, 5, 10].some(function (f) { if (top / (step * f) <= 4.5) { step = step * f; return true; } });
    var ymax = Math.ceil(top / step) * step;

    var xEnd = weeks[weeks.length - 1];
    P.releases.forEach(function (r) { if (Date.parse(r.date) > Date.parse(xEnd)) xEnd = r.date; });
    var X = scaleX(weeks[0], xEnd, PL, W - PR);
    function Y(v) { return PT + (1 - v / ymax) * (H - PT - PB); }

    var o = [];
    for (var g = 0; g <= ymax + 1e-9; g += step) {
      o.push('<line class="grid" x1="' + PL + '" y1="' + Y(g).toFixed(1) + '" x2="' + (W - PR) + '" y2="' + Y(g).toFixed(1) + '"/>');
      o.push('<text class="ax" x="' + (PL - 8) + '" y="' + (Y(g) + 4).toFixed(1) + '" text-anchor="end">' + fmt(g, meta.dec, "") + '</text>');
    }
    o.push('<line class="target" x1="' + PL + '" y1="' + Y(meta.good).toFixed(1) + '" x2="' + (W - PR) + '" y2="' + Y(meta.good).toFixed(1) + '"/>');

    var seenM = {};
    weeks.forEach(function (w) {
      var d = new Date(w + "T00:00:00Z"), m = d.getUTCMonth();
      if (seenM[m]) return;
      seenM[m] = 1;
      o.push('<text class="ax" x="' + X(w).toFixed(1) + '" y="' + (H - 10) + '" text-anchor="middle">' + (m + 1) + '</text>');
    });

    P.releases.forEach(function (r) {
      o.push('<line class="rel" x1="' + X(r.date).toFixed(1) + '" y1="' + PT + '" x2="' + X(r.date).toFixed(1) + '" y2="' + (H - PB) + '"/>');
    });

    shown.forEach(function (p) {
      var seg = [], segs = [];
      series[p.key].forEach(function (v, i) {
        if (v === null) { if (seg.length) segs.push(seg); seg = []; return; }
        seg.push([X(weeks[i]), Y(v)]);
      });
      if (seg.length) segs.push(seg);
      segs.forEach(function (s) {
        o.push('<path class="ln" fill="none" stroke="' + p.color + '" d="M' +
          s.map(function (q) { return q[0].toFixed(1) + "," + q[1].toFixed(1); }).join(" L") + '"/>');
      });
      var lastIdx = -1;
      series[p.key].forEach(function (v, i) { if (v !== null) lastIdx = i; });
      if (lastIdx >= 0) {
        o.push('<circle cx="' + X(weeks[lastIdx]).toFixed(1) + '" cy="' + Y(series[p.key][lastIdx]).toFixed(1) +
          '" r="4" fill="' + p.color + '" stroke="var(--surface)" stroke-width="2"/>');
      }
    });

    host.innerHTML = '<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + esc(meta.ja) + '">' + o.join("") + "</svg>";
  }

  /* ---- 週次の表。リリースのあった週は注釈行を差し込む ---- */
  function drawTable() {
    var host = document.getElementById("trend-table");
    if (!host) return;
    var meta = P.meta[tableMetric], series = P.metrics[tableMetric];
    var cols = P.pages.filter(function (p) {
      return series[p.key] && series[p.key].some(function (v) { return v !== null; });
    });
    var lang = document.documentElement.getAttribute("data-lang") === "en" ? "en" : "ja";
    var h = "<table><thead><tr><th>" + (lang === "en" ? "Week ending" : "週末日") + "</th>" +
      cols.map(function (p) { return "<th>" + esc(p[lang]) + "</th>"; }).join("") + "</tr></thead><tbody>";

    P.weeks.forEach(function (w, i) {
      h += "<tr><td>" + w + "</td>" + cols.map(function (p) {
        var v = series[p.key][i];
        var bad = v !== null && v > meta.good;
        return "<td" + (bad ? ' class="bad"' : "") + ">" + fmt(v, meta.dec, "") + "</td>";
      }).join("") + "</tr>";

      P.releases.forEach(function (r) {
        var d = days(w, r.date);
        var prev = i > 0 ? P.weeks[i - 1] : null;
        var inWeek = prev ? (Date.parse(r.date) > Date.parse(prev) && Date.parse(r.date) <= Date.parse(w))
                          : Date.parse(r.date) <= Date.parse(w);
        var after = i === P.weeks.length - 1 && Date.parse(r.date) > Date.parse(w);
        if (!inWeek && !after) return;
        h += '<tr class="ann"><td>' + r.date + '</td><td colspan="' + cols.length + '">' +
          '<a href="https://app.clickup.com/t/31108037/' + esc(r.ticket) + '">' + esc(r.ticket) + "</a> " +
          esc(r.note[lang]) + ' <span class="ann-scope">' + esc(r.scope[lang]) + "</span></td></tr>";
      });
    });
    host.innerHTML = h + "</tbody></table>";
  }


  /* ---- リリース帯。各グラフと同じ日付レンジで点を打つ ---- */
  function drawStrip() {
    var host = document.getElementById("plot-releases");
    if (!host) return;
    var lang = document.documentElement.getAttribute("data-lang") === "en" ? "en" : "ja";
    var W = 1160, H = 74, PL = 52, PR = 14, BY = 30;
    var weeks = P.weeks, xEnd = weeks[weeks.length - 1];
    P.releases.forEach(function (r) { if (Date.parse(r.date) > Date.parse(xEnd)) xEnd = r.date; });
    var X = scaleX(weeks[0], xEnd, PL, W - PR);

    var o = ['<line class="strip-ax" x1="' + PL + '" y1="' + BY + '" x2="' + (W - PR) + '" y2="' + BY + '"/>'];
    var seenM = {};
    weeks.forEach(function (w) {
      var d = new Date(w + "T00:00:00Z"), m = d.getUTCMonth();
      if (seenM[m]) return;
      seenM[m] = 1;
      o.push('<line class="strip-tick" x1="' + X(w).toFixed(1) + '" y1="' + BY + '" x2="' + X(w).toFixed(1) + '" y2="' + (BY + 5) + '"/>');
      o.push('<text class="ax" x="' + X(w).toFixed(1) + '" y="' + (BY + 19) + '" text-anchor="middle">' + (m + 1) + '</text>');
    });

    /* 同じ日のリリースは1点にまとめ、チケットを並べる */
    var byDate = {};
    P.releases.forEach(function (r) { (byDate[r.date] = byDate[r.date] || []).push(r); });
    Object.keys(byDate).sort().forEach(function (d) {
      var g = byDate[d], x = X(d);
      var anchor = x > W * 0.72 ? "end" : "start";
      var tx = anchor === "end" ? x - 10 : x + 10;
      o.push('<line class="rel" x1="' + x.toFixed(1) + '" y1="8" x2="' + x.toFixed(1) + '" y2="' + BY + '"/>');
      o.push('<circle cx="' + x.toFixed(1) + '" cy="' + BY + '" r="5" fill="var(--brand)" stroke="var(--surface)" stroke-width="2"/>');
      o.push('<text class="rell" x="' + tx.toFixed(1) + '" y="14" text-anchor="' + anchor + '">' + esc(d) + "</text>");
      o.push('<text class="rels" x="' + tx.toFixed(1) + '" y="26" text-anchor="' + anchor + '">' +
        esc(g.map(function (r) { return r.ticket.replace("UX_DESIGN-", "#"); }).join(" / ")) + "</text>");
    });

    var list = Object.keys(byDate).sort().map(function (d) {
      return '<li><span class="rl-d">' + esc(d) + "</span>" + byDate[d].map(function (r) {
        return '<a href="https://app.clickup.com/t/31108037/' + esc(r.ticket) + '">' + esc(r.ticket) + "</a> " + esc(r.note[lang]);
      }).join('<span class="rl-sep"></span>') + "</li>";
    }).join("");

    host.innerHTML = '<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="releases">' + o.join("") + "</svg>" +
      '<ul class="rl">' + list + "</ul>";
  }

  function redrawAll() { drawStrip(); Object.keys(P.metrics).forEach(drawChart); drawTable(); }

  document.addEventListener("click", function (e) {
    var lg = e.target.closest ? e.target.closest(".lg") : null;
    if (lg) {
      var m = lg.dataset.metric, p = lg.dataset.page, k = key(m, p);
      var others = P.pages.filter(function (q) { return q.key !== p && on(m, q.key); });
      if (on(m, p) && others.length === 0) return;   // 最後の1本は消さない
      off[k] = on(m, p);
      lg.setAttribute("aria-pressed", String(!off[k]));
      drawChart(m);
      return;
    }
    var mt = e.target.closest ? e.target.closest(".mt") : null;
    if (mt) {
      tableMetric = mt.dataset.m;
      document.querySelectorAll(".mt").forEach(function (b) {
        b.setAttribute("aria-pressed", String(b.dataset.m === tableMetric));
      });
      drawTable();
    }
  });

  window.setLang = function (l) {
    document.documentElement.setAttribute("data-lang", l);
    document.getElementById("btn-ja").setAttribute("aria-pressed", String(l === "ja"));
    document.getElementById("btn-en").setAttribute("aria-pressed", String(l === "en"));
    try { localStorage.setItem("perf-report-lang", l); } catch (e) {}
    drawTable();
    drawStrip();
  };
  try { var s = localStorage.getItem("perf-report-lang"); if (s) window.setLang(s); } catch (e) {}

  redrawAll();
  addEventListener("resize", function () { drawStrip(); Object.keys(P.metrics).forEach(drawChart); });
})();
