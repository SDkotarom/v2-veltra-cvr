(function () {
  // CSS for tabs
  var css = document.createElement('style');
  css.textContent =
    '.proto-tabs{padding:24px 44px}' +
    '.proto-tabs .pt-header{font-size:13px;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px}' +
    '.proto-tab-bar{display:flex;gap:0;border-bottom:2px solid #e8e6e1;margin-bottom:20px}' +
    '.proto-tab-btn{padding:10px 20px;font-size:14px;font-weight:700;color:#6b6b6b;background:none;border:none;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .15s}' +
    '.proto-tab-btn:hover{color:#1a1a1a}' +
    '.proto-tab-btn.active{color:#E8423F;border-bottom-color:#E8423F}' +
    '.proto-tab-panel{display:none}' +
    '.proto-tab-panel.active{display:block}' +
    '.proto-card{border:1px solid #e8e6e1;border-radius:10px;overflow:hidden}' +
    '.proto-card-head{padding:16px 20px;border-bottom:1px solid #e8e6e1;display:flex;justify-content:space-between;align-items:center}' +
    '.proto-card-head .label{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.06em}' +
    '.proto-card-head .label.a{color:#E8423F}' +
    '.proto-card-head .label.b{color:#d97706}' +
    '.proto-card-head .label.c{color:#6b6b6b}' +
    '.proto-card-head .impact{font-size:13px;color:#aaa}' +
    '.proto-card-body{display:grid;grid-template-columns:1fr 1fr;gap:0}' +
    '.proto-half{padding:20px}' +
    '.proto-half:first-child{border-right:1px solid #e8e6e1}' +
    '.proto-half-label{font-size:11px;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px}' +
    '.proto-spec{font-size:14px;color:#6b6b6b;line-height:1.7}' +
    '.proto-spec strong{color:#1a1a1a}' +
    '.proto-mockup{border:2px dashed #d0cec8;border-radius:8px;padding:32px;text-align:center;color:#aaa;font-size:14px;min-height:120px;display:flex;flex-direction:column;align-items:center;justify-content:center}' +
    '.proto-mockup .icon{font-size:28px;margin-bottom:8px}' +
    '@media(max-width:768px){.proto-card-body{grid-template-columns:1fr}.proto-half:first-child{border-right:none;border-bottom:1px solid #e8e6e1}}';
  document.head.appendChild(css);

  // Find targets: pages with prototype placeholder
  var targets = document.querySelectorAll('.proto-tabs-target');
  if (!targets.length) return;

  targets.forEach(function (target) {
    var pageData = target.getAttribute('data-bottleneck') || '';
    var hypotheses = [];
    // Try to get hypothesis text from the page
    var hypCards = target.closest('.card') ?
      target.closest('.card').querySelectorAll('[data-hypothesis]') : [];

    var tabs = [
      { id: 'a', label: '施策 A', cls: 'a', desc: '仮説1に基づく改善案' },
      { id: 'b', label: '施策 B', cls: 'b', desc: '仮説2に基づく改善案' },
      { id: 'c', label: '施策 C', cls: 'c', desc: '仮説3に基づく改善案' }
    ];

    var html = '<div class="pt-header">打ち手 × 3 + プロトタイプ</div>';
    html += '<div class="proto-tab-bar">';
    tabs.forEach(function (t, i) {
      html += '<button class="proto-tab-btn' + (i === 0 ? ' active' : '') + '" data-tab="' + t.id + '">' + t.label + '</button>';
    });
    html += '</div>';

    tabs.forEach(function (t, i) {
      html += '<div class="proto-tab-panel' + (i === 0 ? ' active' : '') + '" data-panel="' + t.id + '">';
      html += '<div class="proto-card">';
      html += '<div class="proto-card-head"><span class="label ' + t.cls + '">' + t.label + ' — ' + t.desc + '</span><span class="impact">期待効果: 本番データ接続後に算出</span></div>';
      html += '<div class="proto-card-body">';
      html += '<div class="proto-half"><div class="proto-half-label">開発仕様</div>';
      html += '<div class="proto-spec">GA4 MCPからリアルデータを取得後、<br><strong>原因仮説に基づく具体的な開発仕様</strong>を自動生成します。<br><br>対象画面・変更内容・技術要件を含みます。</div>';
      html += '</div>';
      html += '<div class="proto-half"><div class="proto-half-label">Before / After プロトタイプ</div>';
      html += '<div class="proto-mockup"><div class="icon">📐</div>本番データ接続後にビジュアルを自動生成</div>';
      html += '</div>';
      html += '</div></div>';
      html += '</div>';
    });

    target.innerHTML = html;

    // Tab switching
    target.addEventListener('click', function (e) {
      var btn = e.target.closest('.proto-tab-btn');
      if (!btn) return;
      var tabId = btn.getAttribute('data-tab');
      target.querySelectorAll('.proto-tab-btn').forEach(function (b) { b.classList.remove('active'); });
      target.querySelectorAll('.proto-tab-panel').forEach(function (p) { p.classList.remove('active'); });
      btn.classList.add('active');
      target.querySelector('[data-panel="' + tabId + '"]').classList.add('active');
    });
  });
})();
