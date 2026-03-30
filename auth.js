(function () {
  var host = location.hostname;
  if (host === 'localhost' || host === '127.0.0.1' || host === '') return;
  if (sessionStorage.getItem('gauth_user')) {
    document.documentElement.classList.remove('auth-pending');
    return;
  }
  document.documentElement.classList.add('auth-pending');
  var s = document.createElement('style');
  s.textContent = 'html.auth-pending{visibility:hidden!important}';
  document.head.appendChild(s);
  sessionStorage.setItem('auth_redirect', location.href);
  location.replace('/login.html');
})();
