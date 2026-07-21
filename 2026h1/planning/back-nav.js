(function () {
  // Skip if user is on the planning index itself
  if (/\/planning\/?$/.test(location.pathname) || /\/planning\/index\.html$/.test(location.pathname)) return;

  function inject() {
    if (document.getElementById('planning-back-nav')) return;
    var bar = document.createElement('a');
    bar.id = 'planning-back-nav';
    bar.href = '/2026h1/planning/';
    bar.innerHTML = '<span style="display:inline-block;transform:translateY(-1px)">←</span> 施策案一覧へ';
    bar.style.cssText = [
      'position:fixed',
      'top:16px',
      'left:16px',
      'z-index:9999',
      'background:rgba(255,255,255,0.96)',
      'color:#1a1a1a',
      'font-family:"Noto Sans JP","Hiragino Sans","Yu Gothic",system-ui,sans-serif',
      'font-size:13px',
      'font-weight:700',
      'padding:8px 14px',
      'border:1px solid #e2e8f0',
      'border-radius:999px',
      'box-shadow:0 2px 8px rgba(0,0,0,0.08)',
      'text-decoration:none',
      'transition:transform .12s ease, box-shadow .12s ease, background .12s ease',
      'backdrop-filter:blur(6px)',
      '-webkit-backdrop-filter:blur(6px)',
      'display:inline-flex',
      'align-items:center',
      'gap:6px',
      'line-height:1'
    ].join(';');
    bar.addEventListener('mouseenter', function () {
      bar.style.transform = 'translateY(-1px)';
      bar.style.boxShadow = '0 4px 14px rgba(0,0,0,0.12)';
      bar.style.background = '#fff';
    });
    bar.addEventListener('mouseleave', function () {
      bar.style.transform = 'translateY(0)';
      bar.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
      bar.style.background = 'rgba(255,255,255,0.96)';
    });
    document.body.appendChild(bar);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
