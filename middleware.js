/**
 * Vercel Edge Middleware — サイト全体のアクセスゲート
 *
 * すべてのリクエスト（HTML / JSON / 画像）がここを通る。有効な署名付き Cookie を
 * 持たないリクエストはエッジで遮断されるため、URL を知っているだけでは中身を取得できない。
 *
 * 必要な環境変数（Vercel ダッシュボード → Settings → Environment Variables）:
 *   ACCESS_PASSCODE  関係者に共有するパスコード
 *   ACCESS_SECRET    Cookie 署名用の秘密鍵（32文字以上のランダム文字列）
 * どちらもリポジトリには置かない。未設定のときは fail-closed で全遮断する。
 *
 * 失効させたいときは ACCESS_PASSCODE と ACCESS_SECRET を差し替えて再デプロイする。
 * ACCESS_SECRET を変えると発行済み Cookie がすべて無効になる（＝全員ログアウト）。
 */

const COOKIE_NAME = 'v2_access';
const MAX_AGE = 60 * 60 * 24 * 60; // 60日。関係者が入り直す手間を減らすための期限
const TOKEN_VERSION = 'v1';

// 認証前でも到達できるパス。ログイン画面とその裏側の API のみ
const PUBLIC_PATHS = new Set(['/login.html', '/favicon.ico']);

const encoder = new TextEncoder();

export default async function middleware(request) {
  const url = new URL(request.url);
  const path = url.pathname;

  const secret = process.env.ACCESS_SECRET;
  const passcode = process.env.ACCESS_PASSCODE;
  if (!secret || !passcode) return misconfigured();

  if (path === '/api/session') return handleSession(request, secret);
  if (path === '/api/login') return handleLogin(request, url, secret, passcode);
  if (path === '/api/logout') return handleLogout(request, url);

  if (PUBLIC_PATHS.has(path)) return passThrough();
  if (await isAuthed(request, secret)) return passThrough();

  return deny(request, url);
}

/* ===== ゲート本体 ===== */

// Vercel のミドルウェアプロトコル。このヘッダを返すとリクエストがそのまま配信に進む
function passThrough() {
  return new Response(null, { headers: { 'x-middleware-next': '1' } });
}

function deny(request, url) {
  // ページ遷移ならログイン画面へ。fetch / curl には 401 を返して中身を渡さない
  const navigating =
    request.headers.get('sec-fetch-mode') === 'navigate' ||
    (request.headers.get('accept') || '').includes('text/html');

  if (!navigating) {
    return json({ error: 'unauthorized' }, 401);
  }

  const next = url.pathname + url.search;
  const location = next === '/' ? '/login.html' : '/login.html?next=' + encodeURIComponent(next);
  return new Response(null, {
    status: 302,
    headers: { location, 'cache-control': 'no-store' },
  });
}

function misconfigured() {
  return new Response(
    'ACCESS_PASSCODE / ACCESS_SECRET が未設定です。Vercel の Environment Variables を確認してください。',
    { status: 503, headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' } }
  );
}

/* ===== API ===== */

async function handleSession(request, secret) {
  return json({ authed: await isAuthed(request, secret) }, 200);
}

async function handleLogin(request, url, secret, passcode) {
  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);

  // SameSite=Lax に加えた CSRF 対策。他オリジンからの POST は受け付けない
  const origin = request.headers.get('origin');
  if (origin && origin !== url.origin) return json({ error: 'forbidden' }, 403);

  let body = null;
  try {
    body = await request.json();
  } catch (e) {
    body = null;
  }
  const supplied = body && typeof body.passcode === 'string' ? body.passcode.trim() : '';

  if (!(await secretEquals(secret, supplied, passcode.trim()))) {
    // 総当たりの試行速度を落とす
    await new Promise(function (r) { setTimeout(r, 600); });
    return json({ error: 'invalid_passcode' }, 401);
  }

  const exp = Math.floor(Date.now() / 1000) + MAX_AGE;
  const sig = await sign(secret, TOKEN_VERSION + '.' + exp);
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      'set-cookie': COOKIE_NAME + '=' + exp + '.' + sig +
        '; Path=/; Max-Age=' + MAX_AGE + '; HttpOnly; Secure; SameSite=Lax',
    },
  });
}

function handleLogout(request, url) {
  if (request.method !== 'POST') return json({ error: 'method_not_allowed' }, 405);
  const origin = request.headers.get('origin');
  if (origin && origin !== url.origin) return json({ error: 'forbidden' }, 403);
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      'set-cookie': COOKIE_NAME + '=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax',
    },
  });
}

/* ===== Cookie / 署名 ===== */

async function isAuthed(request, secret) {
  const token = readCookie(request, COOKIE_NAME);
  if (!token) return false;

  const sep = token.indexOf('.');
  if (sep < 0) return false;

  const exp = token.slice(0, sep);
  const sig = token.slice(sep + 1);
  const expSec = Number(exp);
  if (!Number.isFinite(expSec) || expSec * 1000 < Date.now()) return false;

  const expected = await sign(secret, TOKEN_VERSION + '.' + exp);
  return timingSafeEqual(sig, expected);
}

async function sign(secret, message) {
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const sig = await crypto.subtle.sign('HMAC', key, encoder.encode(message));
  return base64url(sig);
}

// 入力長を漏らさないよう、双方を HMAC に通してから固定長で比較する
async function secretEquals(secret, a, b) {
  const pair = await Promise.all([sign(secret, 'cmp.' + a), sign(secret, 'cmp.' + b)]);
  return timingSafeEqual(pair[0], pair[1]);
}

function timingSafeEqual(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function base64url(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function readCookie(request, name) {
  const header = request.headers.get('cookie');
  if (!header) return null;
  const parts = header.split(';');
  for (let i = 0; i < parts.length; i++) {
    const eq = parts[i].indexOf('=');
    if (eq < 0) continue;
    if (parts[i].slice(0, eq).trim() === name) return parts[i].slice(eq + 1).trim();
  }
  return null;
}

function json(payload, status) {
  return new Response(JSON.stringify(payload), {
    status: status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });
}
