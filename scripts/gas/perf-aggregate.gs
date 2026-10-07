/**
 * 表示速度モニタリング 集計レイヤー
 *
 * 役割は「生データの解釈を1か所に固定すること」。
 * crux_weekly / psi_daily の各タブを読み、確定した値だけを _summary と _defs に
 * 書き出す。レポートを作る側は _summary しか読まない。
 *
 * 置き方: 計測スプレッドシート → 拡張機能 → Apps Script に貼り、
 *         setUp() を1回実行（毎朝5:00のトリガー登録＋初回集計）
 *
 * データ取得（CrUX / PSI の収集）は別スクリプトの担当。ここでは行わない。
 */

var PAGES = [
  {key:'TOP',      ja:'TOP',        en:'TOP',       url:'https://www.veltra.com/jp/'},
  {key:'エリア',    ja:'エリア',      en:'Area',      url:'https://www.veltra.com/jp/japan/tokyo/'},
  {key:'地域',      ja:'地域',        en:'Region',    url:'https://www.veltra.com/jp/japan/kanto/'},
  {key:'カテゴリー', ja:'カテゴリー',  en:'Category',  url:'https://www.veltra.com/jp/japan/tokyo/ctg/183551:Yakatabune/'},
  {key:'AC詳細',    ja:'AC詳細',      en:'AC detail', url:'https://www.veltra.com/jp/japan/tokyo/a/160690'},
  {key:'検索結果',   ja:'検索結果',    en:'Search',    url:'https://www.veltra.com/jp/search?kw=tokyo'}
];

var THRESH = {lcp:{good:2500,ni:4000}, inp:{good:200,ni:500}, cls:{good:0.1,ni:0.25}, ttfb:{good:800,ni:1800}};
var SUMMARY_SHEET='_summary', DEFS_SHEET='_defs';

function setUp(){
  ScriptApp.getProjectTriggers().forEach(function(t){
    if(t.getHandlerFunction()==='aggregate') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('aggregate').timeBased().atHour(5).everyDays(1).create();
  aggregate();
}

/** 見出し行に必須カラムが揃うシートを返す（タブ名に依存しない） */
function findSheetByHeaders(required){
  var sheets=SpreadsheetApp.getActiveSpreadsheet().getSheets();
  for(var i=0;i<sheets.length;i++){
    var lc=sheets[i].getLastColumn(); if(lc<1) continue;
    var head=sheets[i].getRange(1,1,1,lc).getValues()[0].map(function(v){return String(v).trim();});
    if(required.every(function(r){return head.indexOf(r)>=0;})) return {sheet:sheets[i],head:head};
  }
  return null;
}

function readRows(found){
  if(!found) return [];
  var sh=found.sheet,last=sh.getLastRow();
  if(last<2) return [];
  return sh.getRange(2,1,last-1,found.head.length).getValues().map(function(row){
    var o={}; found.head.forEach(function(h,i){o[h]=row[i];}); return o;
  }).filter(function(o){
    return Object.keys(o).some(function(k){return o[k]!=='' && o[k]!==null;});
  });
}

function ymd(v){
  if(v instanceof Date) return Utilities.formatDate(v,'Asia/Tokyo','yyyy-MM-dd');
  return String(v).trim();
}

/** #NUM! や空欄は null（欠測）。0 では埋めない */
function num(v){
  if(v===''||v===null||v===undefined) return null;
  var n=Number(v); return isNaN(n)?null:n;
}

function verdict(metric,v){
  if(v===null) return '未計測';
  var t=THRESH[metric];
  if(v<=t.good) return '合格';
  if(v<=t.ni) return '要改善';
  return '不良';
}

/**
 * crux_weekly は収集のたびに全履歴が再掲される。
 * 最新の collected_at のブロックだけを使う。外すと同じ週を二重に数える。
 */
function cruxLatestBlock(){
  var rows=readRows(findSheetByHeaders(['collected_at','period_end','page','lcp_p75_ms']));
  if(!rows.length) return {collected:null,rows:[]};
  var collected=rows.map(function(r){return ymd(r['collected_at']);}).sort().pop();
  return {collected:collected, rows:rows.filter(function(r){return ymd(r['collected_at'])===collected;})
    .map(function(r){return {
      period_end:ymd(r['period_end']), page:String(r['page']).trim(),
      lcp:num(r['lcp_p75_ms']), inp:num(r['inp_p75_ms']),
      cls:num(r['cls_p75']),    ttfb:num(r['ttfb_p75_ms'])};})};
}

function psiLatest(){
  var rows=readRows(findSheetByHeaders(['collected_at','date','page','perf_score']));
  if(!rows.length) return {date:null,rows:[]};
  var d=rows.map(function(r){return ymd(r['date']);}).sort().pop();
  return {date:d, rows:rows.filter(function(r){return ymd(r['date'])===d;})
    .map(function(r){return {page:String(r['page']).trim(),perf:num(r['perf_score']),lcp:num(r['lcp_ms'])};})};
}

function aggregate(){
  var crux=cruxLatestBlock(), psi=psiLatest();
  if(!crux.rows.length) throw new Error('crux_weekly タブが見つからないか空です');

  var allWeeks=[];
  crux.rows.forEach(function(r){ if(allWeeks.indexOf(r.period_end)<0) allWeeks.push(r.period_end); });
  allWeeks.sort();
  var latest=allWeeks[allWeeks.length-1];
  var prev=allWeeks.length>1?allWeeks[allWeeks.length-2]:null;

  var header=['page_key','page_ja','page_en','url','source','granularity','period_end',
    'lcp_p75_ms','inp_p75_ms','cls_p75','ttfb_p75_ms',
    'lcp_prev_ms','lcp_delta_ms','lcp_verdict',
    'best_ms','best_period_end','delta_from_best_ms',
    'first_missing_week','data_status','psi_score','psi_lcp_ms'];
  var out=[header];

  PAGES.forEach(function(p){
    var mine=crux.rows.filter(function(r){return r.page===p.key;});
    var cur=mine.filter(function(r){return r.period_end===latest;})[0]||null;
    var pv=prev?(mine.filter(function(r){return r.period_end===prev;})[0]||null):null;

    var withVal=mine.filter(function(r){return r.lcp!==null;})
      .sort(function(a,b){return a.period_end<b.period_end?-1:1;});
    var best=null;
    withVal.forEach(function(r){ if(!best||r.lcp<best.lcp) best=r; });

    var firstMissing='';
    if(withVal.length){
      var i=allWeeks.indexOf(withVal[withVal.length-1].period_end);
      if(i>=0 && i+1<allWeeks.length) firstMissing=allWeeks[i+1];
    }

    var lcp=cur?cur.lcp:null;
    var status = mine.length===0 ? '未収集' : (lcp===null ? '欠測' : 'ok');
    var ps=psi.rows.filter(function(r){return r.page===p.key;})[0]||null;

    out.push([p.key,p.ja,p.en,p.url,
      mine.length?'crux_weekly':'', mine.length?'url':'', latest,
      lcp, cur?cur.inp:null, cur?cur.cls:null, cur?cur.ttfb:null,
      pv?pv.lcp:null,
      (lcp!==null&&pv&&pv.lcp!==null)?(lcp-pv.lcp):null,
      verdict('lcp',lcp),
      best?best.lcp:null, best?best.period_end:'',
      (lcp!==null&&best)?(lcp-best.lcp):null,
      firstMissing, status,
      ps?ps.perf:null, ps?ps.lcp:null]);
  });

  writeSheet(SUMMARY_SHEET,out);
  writeSheet(DEFS_SHEET,[
    ['key','value','note'],
    ['generated_at',Utilities.formatDate(new Date(),'Asia/Tokyo','yyyy-MM-dd HH:mm'),'JST'],
    ['latest_period_end',latest,'CrUX 週次の最終週。レポートの「対象週」はこれ'],
    ['crux_collected_at',crux.collected,'使用した収集ブロック'],
    ['psi_date',psi.date||'','PSI ラボ値の計測日（参考値）'],
    ['period_from',allWeeks[0],''],
    ['weeks_covered',allWeeks.length,'期間内の週数'],
    ['denominator',PAGES.length,'KPIの分母。測れないページも分母に残す'],
    ['granularity_rule','url-only','URL単位のCrUXのみ採用。origin値での代用はしない'],
    ['source_of_truth','crux_weekly','PSIラボ値は参考。実ユーザー値の正はCrUX週次タブ'],
    ['missing_rule','null','欠測は0で埋めず、線を途切れさせる'],
    ['lcp_good','2500','ms 以下で合格'],['lcp_ni','4000','ms 以下で要改善'],
    ['inp_good','200','ms 以下で合格'],['cls_good','0.1','以下で合格'],
    ['ttfb_good','800','ms 以下で合格'],
    ['crux_window','28','日間のローリング。リリース効果が出るまで数週かかる'],
    ['judge_env','production','本番のみで判定。dev の数値は使わない']
  ]);
}

function writeSheet(name,rows){
  var ss=SpreadsheetApp.getActiveSpreadsheet();
  var sh=ss.getSheetByName(name)||ss.insertSheet(name);
  sh.clear();
  sh.getRange(1,1,rows.length,rows[0].length).setValues(rows);
  sh.getRange(1,1,1,rows[0].length).setFontWeight('bold');
  sh.setFrozenRows(1);
}
