function toggleHypoActions(id) {
  var el = document.getElementById(id);
  var num = id.replace('hypo-actions-', '');
  var toggleEl = document.getElementById('hypo-toggle-' + num);
  if (el.style.display === 'none') {
    el.style.display = 'block';
    if (toggleEl) toggleEl.innerHTML = '&#x1F53A; 打ち手を閉じる';
  } else {
    el.style.display = 'none';
    if (toggleEl) toggleEl.innerHTML = '&#x1F53B; 打ち手を見る';
  }
}
function toggleProto(id) {
  var el = document.getElementById(id);
  var letter = id.replace('proto-', '');
  var toggleEl = document.getElementById('proto-toggle-' + letter);
  if (el.style.display === 'none') {
    el.style.display = 'block';
    if (toggleEl) toggleEl.innerHTML = '&#x1F4D0; プロトタイプを閉じる &#x25BE;';
  } else {
    el.style.display = 'none';
    if (toggleEl) toggleEl.innerHTML = '&#x1F4D0; プロトタイプを見る &#x25B8;';
  }
}
function toggleBnAcc(id) {
  var el = document.getElementById(id);
  if (el.style.display === 'none') {
    el.style.display = 'block';
  } else {
    el.style.display = 'none';
  }
}
