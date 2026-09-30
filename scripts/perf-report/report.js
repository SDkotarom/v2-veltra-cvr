(function () {
  var P = window.__PERF, off = {}, tableMetric = "lcp", gran = "w", offset = 0;

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


  /* 月ごとの最終週。月次表示のときの x 位置に使う */
  var MONTHS = [], MONTH_LAST = {};
  P.weeks.forEach(function (w) {
    var m = w.slice(0, 7);
    if (MONTHS.indexOf(m) < 0) MONTHS.push(m);
    MONTH_LAST[m] = w;
  });

  /* 表示する期間。offset 0 が最新側。‹ で1期間ぶん過去へ戻る。 */
  var WIN = { w: 13, m: 12 };
  function axisDates() {
    return gran === "w" ? P.weeks.slice() : MONTHS.map(function (m) { return MONTH_LAST[m]; });
  }
  function windowInfo() {
    var all = axisDates(), size = WIN[gran];
    var maxOff = Math.max(0, Math.ceil(all.length / size) - 1);
    offset = Math.min(Math.max(offset, 0), maxOff);
    var end = all.length - offset * size;
    return { dates: all.slice(Math.max(0, end - size), end), maxOff: maxOff };
  }

  /* 描画する点列。週次はそのまま、月次は「その月で最後に値のある週」の値を採る。
     CrUX の値は28日ローリングの p75 なので、月内を平均してはいけない。 */
  function points(mk, key) {
    var vals = P.metrics[mk][key], out = [];
    if (gran === "w") {
      P.weeks.forEach(function (w, i) { out.push([w, vals[i]]); });
      return out;
    }
    var last = {};
    P.weeks.forEach(function (w, i) {
      if (vals[i] !== null && vals[i] !== undefined) last[w.slice(0, 7)] = [w, vals[i]];
    });
    MONTHS.forEach(function (m) { out.push(last[m] || [MONTH_LAST[m], null]); });
    return out;
  }

  /* ---- チャート描画。表示中の系列だけで縦軸を張り直す ---- */
  function drawChart(mk) {
    var meta = P.meta[mk], host = document.getElementById("plot-" + mk);
    if (!host) return;
    var W = 390, H = 205, PL = 46, PR = 10, PT = 14, PB = 26;
    var weeks = P.weeks, series = P.metrics[mk];
    var shown = P.pages.filter(function (p) {
      return on(mk, p.key) && series[p.key] && series[p.key].some(function (v) { return v !== null; });
    });

    var win = windowInfo(), wd = win.dates, inWin = {};
    wd.forEach(function (d) { inWin[d] = 1; });

    var PTS = {};
    shown.forEach(function (p) {
      PTS[p.key] = points(mk, p.key).filter(function (q) { return inWin[q[0]]; });
    });

    var vals = [];
    shown.forEach(function (p) {
      PTS[p.key].forEach(function (q) { if (q[1] !== null) vals.push(q[1]); });
    });
    vals.push(meta.good);
    var top = Math.max.apply(null, vals) * 1.12 || 1;
    var step = Math.pow(10, Math.floor(Math.log10(top / 3)));
    [1, 2, 2.5, 5, 10].some(function (f) { if (top / (step * f) <= 4.5) { step = step * f; return true; } });
    var ymax = Math.ceil(top / step) * step;

    var xStart = wd[0], xEnd = wd[wd.length - 1];
    if (offset === 0) {
      P.releases.forEach(function (r) { if (Date.parse(r.date) > Date.parse(xEnd)) xEnd = r.date; });
    }
    var X = scaleX(xStart, xEnd, PL, W - PR);
    function Y(v) { return PT + (1 - v / ymax) * (H - PT - PB); }

    var o = [];
    for (var g = 0; g <= ymax + 1e-9; g += step) {
      o.push('<line class="grid" x1="' + PL + '" y1="' + Y(g).toFixed(1) + '" x2="' + (W - PR) + '" y2="' + Y(g).toFixed(1) + '"/>');
      o.push('<text class="ax" x="' + (PL - 8) + '" y="' + (Y(g) + 4).toFixed(1) + '" text-anchor="end">' + fmt(g, meta.dec, "") + '</text>');
    }
    o.push('<line class="target" x1="' + PL + '" y1="' + Y(meta.good).toFixed(1) + '" x2="' + (W - PR) + '" y2="' + Y(meta.good).toFixed(1) + '"/>');

    var seenM = {};
    wd.forEach(function (w) {
      var m = new Date(w + "T00:00:00Z").getUTCMonth();
      if (seenM[m]) return;
      seenM[m] = 1;
      o.push('<text class="ax" x="' + X(w).toFixed(1) + '" y="' + (H - 10) + '" text-anchor="middle">' + (m + 1) + '</text>');
    });

    P.releases.forEach(function (r) {
      var t = Date.parse(r.date);
      if (t < Date.parse(xStart) || t > Date.parse(xEnd)) return;
      o.push('<line class="rel" x1="' + X(r.date).toFixed(1) + '" y1="' + PT + '" x2="' + X(r.date).toFixed(1) + '" y2="' + (H - PB) + '"/>');
    });

    shown.forEach(function (p) {
      var pts = PTS[p.key], seg = [], segs = [], lastPt = null;
      pts.forEach(function (q) {
        if (q[1] === null) { if (seg.length) segs.push(seg); seg = []; return; }
        seg.push([X(q[0]), Y(q[1])]);
        lastPt = q;
      });
      if (seg.length) segs.push(seg);
      segs.forEach(function (s) {
        if (s.length === 1) {
          o.push('<circle cx="' + s[0][0].toFixed(1) + '" cy="' + s[0][1].toFixed(1) +
            '" r="2.5" fill="' + p.color + '"/>');
          return;
        }
        o.push('<path class="ln" fill="none" stroke="' + p.color + '" d="M' +
          s.map(function (q) { return q[0].toFixed(1) + "," + q[1].toFixed(1); }).join(" L") + '"/>');
      });
      if (lastPt) {
        o.push('<circle cx="' + X(lastPt[0]).toFixed(1) + '" cy="' + Y(lastPt[1]).toFixed(1) +
          '" r="4" fill="' + p.color + '" stroke="var(--surface)" stroke-width="2"/>');
      }
    });

    host.innerHTML = '<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + esc(meta.ja) + '">' + o.join("") + "</svg>";
  }


  /* ---- PSI 日次。太線は7日移動平均、薄い線はその日の値 ---- */
  function movingAvg(vals, w) {
    return vals.map(function (_, i) {
      var seg = [];
      for (var k = Math.max(0, i - w + 1); k <= i; k++) if (vals[k] !== null) seg.push(vals[k]);
      return seg.length ? seg.reduce(function (a, b) { return a + b; }, 0) / seg.length : null;
    });
  }

  function drawPsi(which) {
    var host = document.getElementById("plot-" + which);
    var legendEl = document.getElementById(which === "psi" ? "psi-legend" : "tbt-legend");
    if (!host || !P.psi) return;
    var src = which === "psi" ? P.psi.score : P.psi.tbt;
    var dates = P.psi.dates, lang = document.documentElement.getAttribute("data-lang") === "en" ? "en" : "ja";
    var W = 824, H = 300, PL = 48, PR = 14, PT = 16, PB = 30;

    var shown = P.pages.filter(function (p) {
      return src[p.key] && src[p.key].some(function (v) { return v !== null; }) && !off[which + "|" + p.key];
    });
    if (!shown.length) shown = P.pages.slice(0, 1);

    var vals = [];
    shown.forEach(function (p) { src[p.key].forEach(function (v) { if (v !== null) vals.push(v); }); });
    var top = Math.max.apply(null, vals) * 1.1 || 1;
    var step = Math.pow(10, Math.floor(Math.log10(top / 3)));
    [1, 2, 2.5, 5, 10].some(function (f) { if (top / (step * f) <= 5) { step = step * f; return true; } });
    var ymax = which === "psi" ? 100 : Math.ceil(top / step) * step;

    var X = scaleX(dates[0], dates[dates.length - 1], PL, W - PR);
    function Y(v) { return PT + (1 - v / ymax) * (H - PT - PB); }

    var o = [];
    for (var g = 0; g <= ymax + 1e-9; g += step) {
      o.push('<line class="grid" x1="' + PL + '" y1="' + Y(g).toFixed(1) + '" x2="' + (W - PR) + '" y2="' + Y(g).toFixed(1) + '"/>');
      o.push('<text class="ax" x="' + (PL - 8) + '" y="' + (Y(g) + 4).toFixed(1) + '" text-anchor="end">' + Math.round(g) + '</text>');
    }
    var seenD = {};
    dates.forEach(function (d) {
      var lab = d.slice(5).replace("-", "/");
      if (seenD[lab] || Number(d.slice(8)) % 4 !== 0) return;
      seenD[lab] = 1;
      o.push('<text class="ax" x="' + X(d).toFixed(1) + '" y="' + (H - 8) + '" text-anchor="middle">' + lab + '</text>');
    });
    P.releases.forEach(function (r) {
      if (Date.parse(r.date) < Date.parse(dates[0]) || Date.parse(r.date) > Date.parse(dates[dates.length - 1])) return;
      o.push('<line class="rel" x1="' + X(r.date).toFixed(1) + '" y1="' + PT + '" x2="' + X(r.date).toFixed(1) + '" y2="' + (H - PB) + '"/>');
    });

    function path(vs, cls, col, wid) {
      var seg = [], segs = [];
      vs.forEach(function (v, i) {
        if (v === null) { if (seg.length) segs.push(seg); seg = []; return; }
        seg.push([X(dates[i]), Y(v)]);
      });
      if (seg.length) segs.push(seg);
      segs.forEach(function (sg) {
        if (sg.length < 2) return;
        o.push('<path class="' + cls + '" fill="none" stroke="' + col + '" stroke-width="' + wid + '" d="M' +
          sg.map(function (q) { return q[0].toFixed(1) + "," + q[1].toFixed(1); }).join(" L") + '"/>');
      });
    }
    shown.forEach(function (p) { path(src[p.key], "ln raw", p.color, 1); });
    shown.forEach(function (p) { path(movingAvg(src[p.key], 7), "ln", p.color, 2.4); });

    /* リリースの打刻。軸の上に点を置き、ホバーでその日の中身を出す */
    var byDate = {}, a0 = Date.parse(dates[0]), b0 = Date.parse(dates[dates.length - 1]);
    P.releases.forEach(function (r) {
      var tm = Date.parse(r.date);
      if (tm < a0 || tm > b0) return;
      (byDate[r.date] = byDate[r.date] || []).push(r);
    });
    var marks = Object.keys(byDate).sort().map(function (dd) {
      var g = byDate[dd], side = X(dd) / W > 0.6 ? " right" : "";
      var rows = g.map(function (r) {
        return '<a class="tp-row" href="https://app.clickup.com/t/31108037/' + esc(r.ticket) +
          '" target="_blank" rel="noopener"><span class="tp-tk">' + esc(r.ticket) + "</span>" +
          '<span class="tp-nt">' + esc(r.note[lang]) + "</span>" +
          '<span class="tp-sc">' + esc(r.scope[lang]) + "</span></a>";
      }).join("");
      return '<div class="rdot pm' + side + '" style="left:' + (X(dd) / W * 100).toFixed(2) + '%" tabindex="0">' +
        '<span class="rdot-mark">' + (g.length > 1 ? g.length : "") + "</span>" +
        '<span class="rdot-date">' + esc(dd.slice(5).replace("-", "/")) + "</span>" +
        '<div class="tip"><div class="tip-h">' + esc(dd) + " · " + g.length +
        (lang === "en" ? " releases" : " 件") + "</div>" + rows + "</div></div>";
    }).join("");

    host.innerHTML = '<div class="plot-wrap"><svg viewBox="0 0 ' + W + " " + H +
      '" role="img">' + o.join("") + "</svg>" + marks + "</div>";
    if (legendEl) {
      legendEl.innerHTML = P.pages.filter(function (p) {
        return src[p.key] && src[p.key].some(function (v) { return v !== null; });
      }).map(function (p) {
        return '<button class="lg" data-metric="' + which + '" data-page="' + p.key + '" aria-pressed="' +
          String(!off[which + "|" + p.key]) + '"><span class="dot" style="background:' + p.color + '"></span>' +
          '<span class="ja">' + esc(p.ja) + '</span><span class="en">' + esc(p.en) + "</span></button>";
      }).join("");
    }
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
    var wd = windowInfo().dates;
    var xStart = wd[0], xEnd = wd[wd.length - 1];
    if (offset === 0) {
      P.releases.forEach(function (r) { if (Date.parse(r.date) > Date.parse(xEnd)) xEnd = r.date; });
    }
    var PL = 48, PR = 14, W = 824;
    var X = scaleX(xStart, xEnd, PL, W - PR);
    function pct(d) { return (X(d) / W * 100).toFixed(2) + "%"; }

    var months = [], seen = {};
    wd.forEach(function (w) {
      var m = new Date(w + "T00:00:00Z").getUTCMonth();
      if (seen[m]) return;
      seen[m] = 1;
      months.push('<span class="sm" style="left:' + pct(w) + '">' + (m + 1) + (lang === "en" ? "" : "月") + "</span>");
    });

    var byDate = {}, a = Date.parse(xStart), b = Date.parse(xEnd);
    P.releases.forEach(function (r) {
      var t = Date.parse(r.date);
      if (t < a || t > b) return;
      (byDate[r.date] = byDate[r.date] || []).push(r);
    });

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

  /* 期間ラベルと ‹ › の有効・無効 */
  function renderRange() {
    var win = windowInfo(), wd = win.dates;
    var lang = document.documentElement.getAttribute("data-lang") === "en" ? "en" : "ja";
    var lab = document.getElementById("range-label");
    if (lab) {
      var cut = gran === "w" ? 10 : 7;
      lab.textContent = wd[0].slice(0, cut) + " 〜 " + wd[wd.length - 1].slice(0, cut);
    }
    var prev = document.querySelector('.rg[data-move="-1"]');
    var next = document.querySelector('.rg[data-move="1"]');
    var today = document.querySelector(".rg-today");
    if (prev) prev.disabled = offset >= win.maxOff;
    if (next) next.disabled = offset <= 0;
    if (today) {
      today.disabled = offset <= 0;
      today.textContent = gran === "w"
        ? (lang === "en" ? "This week" : "今週")
        : (lang === "en" ? "This month" : "今月");
    }
  }

  function redrawCharts() {
    drawPsi("psi");
    drawPsi("tbt");
    renderRange();
    Object.keys(P.metrics).forEach(drawChart);
    drawStrip();
  }

  function redrawAll() { redrawCharts(); drawTable(); }

  document.addEventListener("click", function (e) {
    var lg = e.target.closest ? e.target.closest(".lg") : null;
    if (lg) {
      var m = lg.dataset.metric, p = lg.dataset.page, k = key(m, p);
      var others = P.pages.filter(function (q) { return q.key !== p && on(m, q.key); });
      if (on(m, p) && others.length === 0) return;   // 最後の1本は消さない
      off[k] = on(m, p);
      lg.setAttribute("aria-pressed", String(!off[k]));
      if (m === "psi" || m === "tbt") drawPsi(m); else drawChart(m);
      return;
    }
    var gt = e.target.closest ? e.target.closest(".gt") : null;
    if (gt) {
      gran = gt.dataset.g;
      offset = 0;                       // 粒度を変えたら最新側に戻す
      document.querySelectorAll(".gt").forEach(function (b) {
        b.setAttribute("aria-pressed", String(b.dataset.g === gran));
      });
      redrawCharts();
      return;
    }
    var rg = e.target.closest ? e.target.closest(".rg") : null;
    if (rg && !rg.disabled) {
      offset = rg.classList.contains("rg-today") ? 0 : offset - Number(rg.dataset.move);
      redrawCharts();
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
    redrawCharts();
  };
  try { var s = localStorage.getItem("perf-report-lang"); if (s) window.setLang(s); } catch (e) {}

  redrawAll();
  addEventListener("resize", redrawCharts);
})();
