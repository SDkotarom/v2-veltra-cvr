/**
 * 表示速度モニタリング 週次レポート自動生成
 *
 * 計測スプレッドシート（CrUX週次 / PSI日次 / リリース注釈）を読み、
 * 固定の Google ドキュメントを毎回上書きする。
 * そのドキュメントを Google サイトに1回埋め込めば、以降は自動で追従する。
 *
 * 置き方:
 *   計測スプレッドシートを開く → 拡張機能 → Apps Script → 本ファイルを貼る
 *   → setUp() を1回実行（ドキュメント作成＋毎日05:00のトリガー登録）
 *
 * タブは「名前」ではなく「見出し行の並び」で探す。タブ名を変えても壊れない。
 */

var DOC_TITLE = '表示速度モニタリング 週次レポート';
var PROP_DOC_ID = 'PERF_REPORT_DOC_ID';
var PROP_CHART_SHEET = 'PERF_CHART_SHEET_NAME';
var CHART_SHEET_NAME = '_report_chart';

var TARGET_LCP = 2500;   // 合格ライン(ms)
var NI_LCP = 4000;       // 要改善の上限(ms)

// ---------------------------------------------------------------- setup

function setUp() {
  var props = PropertiesService.getScriptProperties();
  if (!props.getProperty(PROP_DOC_ID)) {
    var doc = DocumentApp.create(DOC_TITLE);
    props.setProperty(PROP_DOC_ID, doc.getId());
    Logger.log('created doc: ' + doc.getUrl());
  }
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'buildReport') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('buildReport').timeBased().atHour(5).everyDays(1).create();
  buildReport();
  Logger.log('doc url: ' + DocumentApp.openById(props.getProperty(PROP_DOC_ID)).getUrl());
}

// ------------------------------------------------------- sheet discovery

/** 見出し行に必須カラムがすべて含まれるシートを返す */
function findSheetByHeaders(required) {
  var sheets = SpreadsheetApp.getActiveSpreadsheet().getSheets();
  for (var i = 0; i < sheets.length; i++) {
    var lastCol = sheets[i].getLastColumn();
    if (lastCol < 1) continue;
    var head = sheets[i].getRange(1, 1, 1, lastCol).getValues()[0]
      .map(function (v) { return String(v).trim(); });
    var ok = required.every(function (r) { return head.indexOf(r) >= 0; });
    if (ok) return { sheet: sheets[i], head: head };
  }
  return null;
}

/** シートを {header: value} の配列にする */
function readRows(found) {
  if (!found) return [];
  var sh = found.sheet;
  var last = sh.getLastRow();
  if (last < 2) return [];
  var values = sh.getRange(2, 1, last - 1, found.head.length).getValues();
  return values.map(function (row) {
    var o = {};
    found.head.forEach(function (h, i) { o[h] = row[i]; });
    return o;
  }).filter(function (o) {
    return Object.keys(o).some(function (k) { return o[k] !== '' && o[k] !== null; });
  });
}

function toDateString(v) {
  if (v instanceof Date) return Utilities.formatDate(v, 'Asia/Tokyo', 'yyyy-MM-dd');
  return String(v).trim();
}

function num(v) {
  if (v === '' || v === null || v === undefined) return null;
  var n = Number(v);
  return isNaN(n) ? null : n;   // #NUM! 等は null（欠測）。0で埋めない
}

// ------------------------------------------------------------ data build

/**
 * CrUX週次タブは収集のたびに全履歴が再掲される。
 * 最新の collected_at のブロックだけを使う。ここを外すと同じ週を二重に数える。
 */
function latestCruxRows() {
  var rows = readRows(findSheetByHeaders(['collected_at', 'period_end', 'page', 'lcp_p75_ms']));
  if (!rows.length) return [];
  var latest = rows.map(function (r) { return toDateString(r['collected_at']); })
    .sort().pop();
  return rows.filter(function (r) { return toDateString(r['collected_at']) === latest; })
    .map(function (r) {
      return {
        collected_at: latest,
        period_end: toDateString(r['period_end']),
        page: String(r['page']).trim(),
        lcp: num(r['lcp_p75_ms']),
        inp: num(r['inp_p75_ms']),
        cls: num(r['cls_p75']),
        ttfb: num(r['ttfb_p75_ms'])
      };
    });
}

function latestPsiRows() {
  var rows = readRows(findSheetByHeaders(['collected_at', 'date', 'page', 'perf_score']));
  if (!rows.length) return [];
  var latest = rows.map(function (r) { return toDateString(r['date']); }).sort().pop();
  return rows.filter(function (r) { return toDateString(r['date']) === latest; })
    .map(function (r) {
      return { date: latest, page: String(r['page']).trim(), perf: num(r['perf_score']), lcp: num(r['lcp_ms']) };
    });
}

function releaseRows() {
  return readRows(findSheetByHeaders(['date', 'ticket', 'target', 'type', 'note']))
    .map(function (r) {
      return {
        date: toDateString(r['date']),
        ticket: String(r['ticket']).trim(),
        target: String(r['target']).trim(),
        type: String(r['type']).trim(),
        note: String(r['note']).trim()
      };
    })
    .filter(function (r) { return r.date; })
    .sort(function (a, b) { return a.date < b.date ? 1 : -1; });
}

/**
 * グラフ用シートを作り直す。
 * 列: period_end | ページごとのLCP... | リリース
 * リリース列は、その週にリリースがあった場合だけ値を入れる（点として描画される）
 */
function rebuildChartSheet(crux, releases) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(CHART_SHEET_NAME);
  if (!sh) sh = ss.insertSheet(CHART_SHEET_NAME);
  sh.clear();
  sh.getCharts().forEach(function (c) { sh.removeChart(c); });

  var pages = [];
  crux.forEach(function (r) { if (pages.indexOf(r.page) < 0) pages.push(r.page); });
  var weeks = [];
  crux.forEach(function (r) { if (weeks.indexOf(r.period_end) < 0) weeks.push(r.period_end); });
  weeks.sort();

  var header = ['週'].concat(pages).concat(['リリース']);
  var table = [header];

  weeks.forEach(function (w) {
    var row = [w];
    pages.forEach(function (p) {
      var hit = crux.filter(function (r) { return r.period_end === w && r.page === p; })[0];
      row.push(hit && hit.lcp !== null ? hit.lcp : '');   // 欠測は空。線が途切れる
    });
    // その週（週末日を含む直前7日）にリリースがあれば点を打つ
    var hasRelease = releases.some(function (rel) {
      var wd = new Date(w + 'T00:00:00+09:00');
      var rd = new Date(rel.date + 'T00:00:00+09:00');
      var diff = (wd - rd) / 86400000;
      return diff >= 0 && diff < 7;
    });
    row.push(hasRelease ? TARGET_LCP : '');
    table.push(row);
  });

  sh.getRange(1, 1, table.length, header.length).setValues(table);

  var chart = sh.newChart()
    .asLineChart()
    .addRange(sh.getRange(1, 1, table.length, header.length))
    .setNumHeaders(1)
    .setOption('title', 'LCP p75 の推移（実ユーザー・モバイル）')
    .setOption('height', 420)
    .setOption('width', 900)
    .setOption('interpolateNulls', false)
    .setOption('pointSize', 0)
    .setOption('series', buildSeriesOption(pages.length))
    .setPosition(1, header.length + 2, 0, 0)
    .build();
  sh.insertChart(chart);
  SpreadsheetApp.flush();
  return { sheet: sh, pages: pages, weeks: weeks };
}

/** 最後の系列（リリース）だけ線を消して点だけにする */
function buildSeriesOption(pageCount) {
  var s = {};
  for (var i = 0; i < pageCount; i++) s[i] = { lineWidth: 2, pointSize: 0 };
  s[pageCount] = { lineWidth: 0, pointSize: 9, labelInLegend: 'リリース' };
  return s;
}

// ------------------------------------------------------------- doc build

function verdict(lcp) {
  if (lcp === null) return 'データなし';
  if (lcp <= TARGET_LCP) return '合格';
  if (lcp <= NI_LCP) return '要改善';
  return '不良';
}

function buildReport() {
  var crux = latestCruxRows();
  var psi = latestPsiRows();
  var releases = releaseRows();
  if (!crux.length) throw new Error('CrUX週次タブが見つからないか、データが空です');

  var built = rebuildChartSheet(crux, releases);
  var latestWeek = built.weeks[built.weeks.length - 1];
  var prevWeek = built.weeks.length > 1 ? built.weeks[built.weeks.length - 2] : null;

  var docId = PropertiesService.getScriptProperties().getProperty(PROP_DOC_ID);
  var doc = DocumentApp.openById(docId);
  var body = doc.getBody();
  body.clear();

  var now = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd HH:mm');

  body.appendParagraph('表示速度モニタリング').setHeading(DocumentApp.ParagraphHeading.TITLE);
  body.appendParagraph('対象週（CrUX 週末日）: ' + latestWeek + '　／　生成: ' + now + ' JST');

  // サマリー
  body.appendParagraph('サマリー').setHeading(DocumentApp.ParagraphHeading.HEADING1);
  var sum = [['ページ', 'LCP p75', '判定', '前週差']];
  built.pages.forEach(function (p) {
    var cur = crux.filter(function (r) { return r.page === p && r.period_end === latestWeek; })[0];
    var prv = prevWeek ? crux.filter(function (r) { return r.page === p && r.period_end === prevWeek; })[0] : null;
    var lcp = cur ? cur.lcp : null;
    var diff = (lcp !== null && prv && prv.lcp !== null) ? (lcp - prv.lcp) : null;
    sum.push([
      p,
      lcp === null ? '—' : lcp + ' ms',
      verdict(lcp),
      diff === null ? '—' : (diff > 0 ? '+' : '') + diff + ' ms'
    ]);
  });
  body.appendTable(sum);

  // チャート
  body.appendParagraph('週次推移').setHeading(DocumentApp.ParagraphHeading.HEADING1);
  var charts = built.sheet.getCharts();
  if (charts.length) {
    body.appendImage(charts[0].getBlob().getAs('image/png'));
  }
  body.appendParagraph(
    '点はその週にリリースがあったことを示す。合格ラインは LCP 2,500ms。' +
    'CrUX は28日間の実ユーザーデータのため、リリースの効果が数値に出るまで数週かかる。'
  );

  // 指標詳細
  body.appendParagraph('指標詳細（最新週）').setHeading(DocumentApp.ParagraphHeading.HEADING1);
  var det = [['ページ', 'LCP', 'INP', 'CLS', 'TTFB']];
  built.pages.forEach(function (p) {
    var r = crux.filter(function (x) { return x.page === p && x.period_end === latestWeek; })[0];
    det.push([
      p,
      r && r.lcp !== null ? r.lcp + ' ms' : '—',
      r && r.inp !== null ? r.inp + ' ms' : '—',
      r && r.cls !== null ? String(r.cls) : '—',
      r && r.ttfb !== null ? r.ttfb + ' ms' : '—'
    ]);
  });
  body.appendTable(det);

  // PSI
  if (psi.length) {
    body.appendParagraph('PageSpeed Insights（ラボ・' + psi[0].date + '）')
      .setHeading(DocumentApp.ParagraphHeading.HEADING1);
    var pt = [['ページ', 'スコア', 'LCP']];
    psi.forEach(function (r) {
      pt.push([r.page, r.perf === null ? '—' : String(r.perf), r.lcp === null ? '—' : r.lcp + ' ms']);
    });
    body.appendTable(pt);
    body.appendParagraph('ラボ値は日次でばらつきが大きい。傾向を見る用途に限る。');
  }

  // リリース記録
  body.appendParagraph('リリース記録').setHeading(DocumentApp.ParagraphHeading.HEADING1);
  if (releases.length) {
    var rt = [['日付', 'チケット', '対象', '内容']];
    releases.forEach(function (r) { rt.push([r.date, r.ticket, r.target, r.note]); });
    body.appendTable(rt);
    body.appendParagraph('チケットは ClickUp: https://app.clickup.com/t/31108037/<チケットID>');
  } else {
    body.appendParagraph('リリース注釈タブが空です。');
  }

  // フッター
  body.appendParagraph('データソース').setHeading(DocumentApp.ParagraphHeading.HEADING1);
  body.appendParagraph(
    'CrUX 週次（実ユーザー p75・collected_at ' + crux[0].collected_at + ' のブロック）と ' +
    'PageSpeed Insights 日次。いずれも本番 www.veltra.com・モバイル。' +
    'dev 環境は設定が異なるため判定に使わない。'
  );
  doc.saveAndClose();
}
