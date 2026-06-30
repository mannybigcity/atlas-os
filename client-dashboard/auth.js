const ATLAS_PORTAL_USERS = [
  {
    username: 'atlas-admin',
    displayName: 'Manny / Atlas Admin',
    role: 'admin',
    clientSlug: 'qtime-productions',
    passwordHash: '27130f677defdf9a4434976d576fdeb7a8ffa0ac03a7bcc006f652267df95398'
  },
  {
    username: 'qtime-client',
    displayName: 'Quincy / QTIME PRODUCTIONS',
    role: 'client',
    clientSlug: 'qtime-productions',
    passwordHash: 'afd55daba099a3f2a87bd8688a2898499a63488f525ed72c653f68b28227b32b'
  }
];

const SESSION_KEY = 'atlasClientPortalSession';
const SESSION_VERSION = 'atl48-v1';

async function atlasSha256(value) {
  const encoded = new TextEncoder().encode(value);
  const buffer = await crypto.subtle.digest('SHA-256', encoded);
  return Array.from(new Uint8Array(buffer)).map(byte => byte.toString(16).padStart(2, '0')).join('');
}

function atlasGetSession() {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const session = JSON.parse(raw);
    if (session.version !== SESSION_VERSION) return null;
    if (!session.username || !session.role || !session.clientSlug) return null;
    return session;
  } catch (error) {
    return null;
  }
}

function atlasSetSession(user) {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify({
    version: SESSION_VERSION,
    username: user.username,
    displayName: user.displayName,
    role: user.role,
    clientSlug: user.clientSlug,
    signedInAt: new Date().toISOString()
  }));
}

function atlasLogout() {
  sessionStorage.removeItem(SESSION_KEY);
  window.location.href = '/client-sign-in/';
}

function atlasAllowed(session, required) {
  if (!session) return false;
  if (session.role === 'admin') return true;
  if (required === 'any') return true;
  if (required === 'qtime') return session.clientSlug === 'qtime-productions';
  return session.role === required;
}

function atlasProtectPage(required = 'any') {
  const session = atlasGetSession();
  if (session && session.role === 'client' && window.location.pathname.replace(/\/$/, '') === '/client-dashboard') {
    window.location.replace('/client-dashboard/qtime-productions/');
    return null;
  }
  if (!atlasAllowed(session, required)) {
    const next = encodeURIComponent(window.location.pathname + window.location.search + window.location.hash);
    window.location.replace(`/client-sign-in/?next=${next}`);
    return null;
  }
  document.documentElement.classList.add('portal-unlocked');
  document.querySelectorAll('[data-session-name]').forEach(el => { el.textContent = session.displayName; });
  document.querySelectorAll('[data-admin-only]').forEach(el => { el.hidden = session.role !== 'admin'; });
  document.querySelectorAll('[data-client-only]').forEach(el => { el.hidden = session.role !== 'client'; });
  document.querySelectorAll('[data-logout]').forEach(el => { el.addEventListener('click', atlasLogout); });
  return session;
}

async function atlasHandleLogin(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const message = document.getElementById('loginMessage');
  const username = form.username.value.trim().toLowerCase();
  const password = form.password.value;
  message.textContent = 'Checking secure sign-in...';
  try {
    const hash = await atlasSha256(password);
    const user = ATLAS_PORTAL_USERS.find(item => item.username === username && item.passwordHash === hash);
    if (!user) {
      message.textContent = 'Sign-in failed. Check the temporary username/password Manny controls.';
      return;
    }
    atlasSetSession(user);
    const requested = new URLSearchParams(window.location.search).get('next');
    const fallback = user.role === 'admin' ? '/client-dashboard/' : '/client-dashboard/qtime-productions/';
    const clientAllowedNext = requested && (requested.startsWith('/client-dashboard/qtime-productions/') || requested.startsWith('/client-portal/'));
    const next = user.role === 'admin'
      ? (requested && requested.startsWith('/') ? requested : fallback)
      : (clientAllowedNext ? requested : fallback);
    message.textContent = 'Access approved. Opening your dashboard...';
    window.location.href = next;
  } catch (error) {
    message.textContent = 'This sign-in requires HTTPS or a local web server so the browser can verify the password hash.';
  }
}
