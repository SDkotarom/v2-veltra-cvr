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
    /* 見出しの1列目に指標名を出す。スクロールしても何の表か分かるようにするため */
    var unit = meta.unit ? "（" + meta.unit + "）" : "";
    var h = "<table><thead><tr><th>" + (lang === "en" ? "Week ending" : "週末日") +
      '<span class="th-m">' + esc(meta[lang]) + esc(lang === "en" ? (meta.unit ? " (" + meta.unit + ")" : "") : unit) + "</span></th>" +
      cols.map(function (p) { return "<th>" + esc(p[lang]) + "</th>"; }).join("") + "</tr></thead><tbody>";

    P.weeks.forEach(function (w, i) {
      h += "<tr><td>" + w + "</td>" + cols.map(function (p) {
        var v = series[p.key][i];
        var bad = v !== null && v > meta.good;
        return "<td" + (bad ? ' class="bad"' : "") + ">" + fmt(v, meta.dec, "") + "</td>";
      }).join("") + "</tr>";

      /* その週に出したリリース。行が長くなりすぎないよう1行にまとめ、開くと中身が出る */
      var prev = i > 0 ? P.weeks[i - 1] : null;
      var rel = P.releases.filter(function (r) {
        var inWeek = prev ? (Date.parse(r.date) > Date.parse(prev) && Date.parse(r.date) <= Date.parse(w))
                          : Date.parse(r.date) <= Date.parse(w);
        var after = i === P.weeks.length - 1 && Date.parse(r.date) > Date.parse(w);
        return inWeek || after;
      });
      if (!rel.length) return;

      var dates = [];
      rel.forEach(function (r) { if (dates.indexOf(r.date) < 0) dates.push(r.date); });
      var label = (lang === "en" ? rel.length + (rel.length > 1 ? " releases" : " release") : "リリース " + rel.length + " 件") +
        " · " + dates.sort().map(function (d) { return d.slice(5).replace("-", "/"); }).join(", ");
      var items = rel.map(function (r) {
        return '<li><span class="rl-d">' + esc(r.date.slice(5).replace("-", "/")) + "</span>" +
          '<a href="https://app.clickup.com/t/31108037/' + esc(r.ticket) + '" target="_blank" rel="noopener">' +
          esc(r.ticket) + "</a>" +
          '<span class="rl-sc">' + esc(r.scope[lang]) + "</span>" +
          '<span class="rl-n">' + esc(r.note[lang]) + "</span></li>";
      }).join("");

      h += '<tr class="ann"><td colspan="' + (cols.length + 1) + '">' +
        '<details class="ann-d"><summary>' + esc(label) + '</summary>' +
        '<ul class="rl ann-l">' + items + "</ul></details></td></tr>";
    });
    host.innerHTML = h + "</tbody></table>";
    /* 最新週を初期表示に入れる。表の中だけのスクロールでページは動かない */
    host.scrollTop = host.scrollHeight;
  }


  /* ---- リリース帯。軸はSVG、点はHTMLで置いてホバーで内容を出す ---- */
  function drawStrip() {
    var host = document.getElementById("plot-releases");
    if (!host) return;
    var lang = document.documentElement.getAttribute("data-lang") === "en" ? "en" : "ja";
    var weeks = P.weeks, xEnd = weeks[weeks.length - 1];
    P.releases.forEach(function (r) { if (Date.parse(r.date) > Date.parse(xEnd)) xEnd = r.date; });
    var PL = 52, PR = 14, W = 1160;
    var X = scaleX(weeks[0], xEnd, PL, W - PR);
    function pct(d) { return (X(d) / W * 100).toFixed(2) + "%"; }

    var months = [], seen = {};
    weeks.forEach(function (w) {
      var m = new Date(w + "T00:00:00Z").getUTCMonth();
      if (seen[m]) return;
      seen[m] = 1;
      months.push('<span class="sm" style="left:' + pct(w) + '">' + (m + 1) + (lang === "en" ? "" : "月") + "</span>");
    });

    var byDate = {};
    P.releases.forEach(function (r) { (byDate[r.date] = byDate[r.date] || []).push(r); });

    var dots = Object.keys(byDate).sort().map(function (d) {
      var g = byDate[d];
      var side = X(d) / W > 0.6 ? " right" : "";
      var rows = g.map(function (r) {
        return '<a class="tp-row" href="https://app.clickup.com/t/31108037/' + esc(r.ticket) + '" target="_blank" rel="noopener">' +
          '<span class="tp-tk">' + esc(r.ticket) + "</span>" +
          '<span class="tp-nt">' + esc(r.note[lang]) + "</span>" +
          '<span class="tp-sc">' + esc(r.scope[lang]) + "</span></a>";
      }).join("");
      return '<div class="rdot' + side + '" style="left:' + pct(d) + '" tabindex="0">' +
        '<span class="rdot-mark">' + (g.length > 1 ? g.length : "") + "</span>" +
        '<span class="rdot-date">' + esc(d.slice(5).replace("-", "/")) + "</span>" +
        '<div class="tip"><div class="tip-h">' + esc(d) + " · " + g.length +
        (lang === "en" ? " releases" : " 件") + "</div>" + rows + "</div></div>";
    }).join("");

    var all = Object.keys(byDate).sort().reverse().map(function (d) {
      return byDate[d].map(function (r) {
        return '<li><span class="rl-d">' + esc(d) + "</span>" +
          '<a href="https://app.clickup.com/t/31108037/' + esc(r.ticket) + '" target="_blank" rel="noopener">' +
          esc(r.ticket) + "</a>" +
          '<span class="rl-sc">' + esc(r.scope[lang]) + "</span>" +
          '<span class="rl-n">' + esc(r.note[lang]) + "</span></li>";
      }).join("");
    }).join("");

    host.innerHTML =
      '<div class="strip-wrap">' +
      '<div class="strip-rail" style="left:' + (PL / W * 100).toFixed(2) + '%;right:' + (PR / W * 100).toFixed(2) + '%"></div>' +
      dots + '<div class="strip-months">' + months.join("") + "</div></div>" +
      '<details class="rl-toggle"><summary>' +
      (lang === "en" ? "All releases (" + P.releases.length + ")" : "リリース一覧（" + P.releases.length + "件）") +
      '</summary><ul class="rl">' + all + "</ul></details>";
  }

  /* ---- ホバーの吹き出しの置き場所。画面からはみ出す側には開かない ---- */
  function placeTip(dot) {
    var tip = dot.querySelector(".tip");
    if (!tip) return;
    tip.classList.remove("up");
    tip.style.maxHeight = "";
    tip.style.transform = "";

    var vh = window.innerHeight || document.documentElement.clientHeight;
    var vw = window.innerWidth || document.documentElement.clientWidth;
    var dr = dot.getBoundingClientRect();
    var anchor = dr.top + 38;                    /* 点の中心あたり */
    var below = vh - anchor - 40, above = anchor - 40;

    /* 下に入りきらず、上のほうが空いているなら上向きに開く */
    if (below < 200 && above > below) { tip.classList.add("up"); }
    var room = (tip.classList.contains("up") ? above : below) - 16;
    tip.style.maxHeight = Math.max(Math.min(320, room), 140) + "px";

    /* 左右のはみ出しを測って内側へ寄せる */
    var vis = tip.style.visibility;
    tip.style.visibility = "hidden";
    tip.style.display = "block";
    var tr = tip.getBoundingClientRect();
    tip.style.display = "";
    tip.style.visibility = vis;

    var shift = 0;
    if (tr.right > vw - 12) shift = vw - 12 - tr.right;
    if (tr.left + shift < 12) shift = 12 - tr.left;
    if (shift) tip.style.transform = "translateX(" + Math.round(shift) + "px)";
  }

  /* 表の中のリリース行。開いたときに表示範囲の外だと読めないので寄せる */
  document.addEventListener("toggle", function (e) {
    var d = e.target;
    if (d && d.classList && d.classList.contains("ann-d") && d.open) {
      d.scrollIntoView({ block: "nearest" });
    }
  }, true);

  ["mouseover", "focusin"].forEach(function (ev) {
    document.addEventListener(ev, function (e) {
      var dot = e.target.closest ? e.target.closest(".rdot") : null;
      if (dot) placeTip(dot);
    }, true);
  });

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
