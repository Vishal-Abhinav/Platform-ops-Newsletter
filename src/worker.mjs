const SESSION_COOKIE = "po_session";
const OAUTH_STATE_COOKIE = "po_oauth_state";
const SESSION_TTL_SECONDS = 7 * 24 * 60 * 60;
const OAUTH_STATE_TTL_SECONDS = 10 * 60;

const SECURITY_HEADERS = {
  "content-security-policy": "font-src 'self'; frame-src 'self'; img-src 'self' data: https://avatars.githubusercontent.com https://lh3.googleusercontent.com; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; object-src 'none'; form-action 'self'; upgrade-insecure-requests",
  "strict-transport-security": "max-age=63072000; includeSubDomains; preload",
  "x-content-type-options": "nosniff",
  "referrer-policy": "strict-origin-when-cross-origin",
  "x-frame-options": "DENY",
  "permissions-policy": "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()",
  "cross-origin-opener-policy": "same-origin",
  "x-xss-protection": "0",
  "x-robots-tag": "noindex, nofollow",
};

function secure(response, { privatePage = true } = {}) {
  const secured = new Response(response.body, response);
  for (const [name, value] of Object.entries(SECURITY_HEADERS)) secured.headers.set(name, value);
  if (privatePage) secured.headers.set("cache-control", "no-store");
  return secured;
}

function json(body, status = 200, headers = {}) {
  return secure(new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...headers },
  }));
}

function redirect(location, status = 302, headers = {}) {
  return secure(new Response(null, { status, headers: { location, ...headers } }));
}

function randomToken(bytes = 32) {
  const value = new Uint8Array(bytes);
  crypto.getRandomValues(value);
  return btoa(String.fromCharCode(...value)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function sha256(value) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function parseCookies(request) {
  const result = {};
  for (const item of (request.headers.get("cookie") || "").split(";")) {
    const index = item.indexOf("=");
    if (index < 0) continue;
    result[item.slice(0, index).trim()] = item.slice(index + 1).trim();
  }
  return result;
}

function cookie(name, value, { maxAge = 0 } = {}) {
  return `${name}=${value}; Path=/; Max-Age=${maxAge}; HttpOnly; Secure; SameSite=Lax`;
}

function emailSet(value) {
  return new Set(String(value || "").split(",").map((email) => email.trim().toLowerCase()).filter(Boolean));
}

function safeNext(value, fallback = "/user/") {
  const candidate = String(value || "");
  if (!candidate.startsWith("/") || candidate.startsWith("//") || candidate.includes("\\")) return fallback;
  try {
    const decoded = decodeURIComponent(candidate);
    if (!decoded.startsWith("/") || decoded.startsWith("//") || decoded.includes("\\")) return fallback;
  } catch (_) {
    return fallback;
  }
  return candidate;
}

function areaFor(pathname) {
  let path;
  try {
    path = decodeURIComponent(pathname).replace(/\\/g, "/");
  } catch (_) {
    return null;
  }
  if (path === "/admin" || path.startsWith("/admin/")) return "admin";
  if (path === "/user" || path.startsWith("/user/")) return "user";
  if (path === "/categories/platform-engineering" || path.startsWith("/categories/platform-engineering/")) return "premium";
  return null;
}

function isApi(pathname) {
  return pathname.startsWith("/auth/") || pathname.includes("/api/");
}

function githubReady(env) {
  return Boolean(env.OAUTH_GITHUB_CLIENT_ID && env.OAUTH_GITHUB_CLIENT_SECRET);
}

function googleReady(env) {
  return Boolean(env.OAUTH_GOOGLE_CLIENT_ID && env.OAUTH_GOOGLE_CLIENT_SECRET);
}

function configurationReady(env) {
  return Boolean(env.DB && (githubReady(env) || googleReady(env)));
}

async function sessionFromRequest(request, env) {
  const token = parseCookies(request)[SESSION_COOKIE];
  if (!token || !env.DB) return null;
  const tokenHash = await sha256(token);
  const now = Math.floor(Date.now() / 1000);
  const row = await env.DB.prepare(`
    SELECT u.id, u.github_id, u.github_login, u.auth_provider, u.provider_id,
           u.provider_login, u.email, u.name, u.avatar_url, u.role, u.status,
           s.expires_at
      FROM sessions s JOIN users u ON u.id = s.user_id
     WHERE s.token_hash = ? AND s.expires_at > ?
  `).bind(tokenHash, now).first();
  if (!row) return null;
  return { tokenHash, user: row };
}

async function createSession(env, userId) {
  const token = randomToken();
  const tokenHash = await sha256(token);
  const now = Math.floor(Date.now() / 1000);
  await env.DB.prepare(`
    INSERT INTO sessions (token_hash, user_id, expires_at, created_at, last_seen_at)
    VALUES (?, ?, ?, ?, ?)
  `).bind(tokenHash, userId, now + SESSION_TTL_SECONDS, now, now).run();
  await env.DB.prepare("DELETE FROM sessions WHERE expires_at <= ?").bind(now).run();
  return token;
}

async function githubJson(path, accessToken) {
  const response = await fetch(`https://api.github.com${path}`, {
    headers: {
      accept: "application/vnd.github+json",
      authorization: `Bearer ${accessToken}`,
      "user-agent": "Platform-Ops-Newsletter",
      "x-github-api-version": "2022-11-28",
    },
  });
  if (!response.ok) throw new Error(`GitHub API ${response.status}`);
  return response.json();
}

async function exchangeGithubCode(code, redirectUri, env) {
  const response = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: { accept: "application/json", "content-type": "application/json" },
    body: JSON.stringify({
      client_id: env.OAUTH_GITHUB_CLIENT_ID,
      client_secret: env.OAUTH_GITHUB_CLIENT_SECRET,
      code,
      redirect_uri: redirectUri,
    }),
  });
  if (!response.ok) throw new Error("GitHub token exchange failed");
  const result = await response.json();
  if (!result.access_token) throw new Error(result.error || "GitHub did not return an access token");
  return result.access_token;
}

async function githubIdentity(accessToken) {
  const [profile, emails] = await Promise.all([githubJson("/user", accessToken), githubJson("/user/emails", accessToken)]);
  const verified = emails.filter((entry) => entry && entry.verified && entry.email);
  const selected = verified.find((entry) => entry.primary) || verified[0];
  if (!selected) throw new Error("A verified GitHub email is required");
  return {
    provider: "github",
    providerId: String(profile.id),
    login: String(profile.login || ""),
    email: String(selected.email).trim().toLowerCase(),
    name: String(profile.name || profile.login || selected.email),
    avatarUrl: String(profile.avatar_url || ""),
  };
}

async function exchangeGoogleCode(code, redirectUri, env) {
  const body = new URLSearchParams({
    client_id: env.OAUTH_GOOGLE_CLIENT_ID,
    client_secret: env.OAUTH_GOOGLE_CLIENT_SECRET,
    code,
    grant_type: "authorization_code",
    redirect_uri: redirectUri,
  });
  const response = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!response.ok) throw new Error("Google token exchange failed");
  const result = await response.json();
  if (!result.access_token) throw new Error("Google did not return an access token");
  return result.access_token;
}

async function googleIdentity(accessToken) {
  const response = await fetch("https://openidconnect.googleapis.com/v1/userinfo", {
    headers: { authorization: `Bearer ${accessToken}` },
  });
  if (!response.ok) throw new Error(`Google userinfo ${response.status}`);
  const profile = await response.json();
  if (!profile.sub || !profile.email || profile.email_verified !== true) {
    throw new Error("A verified Google email is required");
  }
  const email = String(profile.email).trim().toLowerCase();
  return {
    provider: "google",
    providerId: String(profile.sub),
    login: email.split("@", 1)[0],
    email,
    name: String(profile.name || email),
    avatarUrl: String(profile.picture || ""),
  };
}

async function upsertUser(env, identity) {
  const now = new Date().toISOString();
  const bootstrapAdmin = emailSet(env.ADMIN_EMAILS).has(identity.email);
  const existing = await env.DB.prepare(`
    SELECT id FROM users
     WHERE (auth_provider = ? AND provider_id = ?) OR email = ? COLLATE NOCASE
     LIMIT 1
  `).bind(identity.provider, identity.providerId, identity.email).first();
  const legacyId = identity.provider === "github" ? identity.providerId : `google:${identity.providerId}`;
  const legacyLogin = identity.login || `${identity.provider}-user`;
  if (existing) {
    await env.DB.prepare(`
      UPDATE users SET github_id = ?, github_login = ?, auth_provider = ?, provider_id = ?,
             provider_login = ?, email = ?, name = ?, avatar_url = ?,
             role = CASE WHEN ? THEN 'admin' ELSE role END,
             status = CASE WHEN ? THEN 'approved' ELSE status END,
             updated_at = ?, last_login_at = ?
       WHERE id = ?
    `).bind(
      legacyId, legacyLogin, identity.provider, identity.providerId, legacyLogin,
      identity.email, identity.name, identity.avatarUrl,
      bootstrapAdmin ? 1 : 0, bootstrapAdmin ? 1 : 0, now, now, existing.id,
    ).run();
  } else {
    await env.DB.prepare(`
      INSERT INTO users
        (github_id, github_login, auth_provider, provider_id, provider_login,
         email, name, avatar_url, role, status, created_at, updated_at, last_login_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      legacyId, legacyLogin, identity.provider, identity.providerId, legacyLogin,
      identity.email, identity.name, identity.avatarUrl,
      bootstrapAdmin ? "admin" : "user", bootstrapAdmin ? "approved" : "pending",
      now, now, now,
    ).run();
  }
  return env.DB.prepare(`
    SELECT id, github_id, github_login, auth_provider, provider_id, provider_login,
           email, name, avatar_url, role, status
      FROM users WHERE auth_provider = ? AND provider_id = ?
  `).bind(identity.provider, identity.providerId).first();
}

function publicUser(user) {
  return {
    id: user.id, login: user.provider_login || user.github_login,
    provider: user.auth_provider || "github", githubLogin: user.github_login,
    email: user.email, name: user.name,
    avatarUrl: user.avatar_url, role: user.role, status: user.status,
  };
}

async function beginGithub(request, env) {
  if (!env.DB || !githubReady(env)) return redirect("/login/?error=configuration");
  const url = new URL(request.url);
  const state = randomToken();
  const next = safeNext(url.searchParams.get("next"));
  const packedState = `${state}.${btoa(next).replace(/=+$/, "")}`;
  const authorize = new URL("https://github.com/login/oauth/authorize");
  authorize.searchParams.set("client_id", env.OAUTH_GITHUB_CLIENT_ID);
  authorize.searchParams.set("redirect_uri", `${url.origin}/auth/github/callback`);
  authorize.searchParams.set("scope", "read:user user:email");
  authorize.searchParams.set("state", packedState);
  return redirect(authorize.toString(), 302, {
    "set-cookie": cookie(OAUTH_STATE_COOKIE, state, { maxAge: OAUTH_STATE_TTL_SECONDS }),
  });
}

async function finishGithub(request, env) {
  if (!env.DB || !githubReady(env)) return redirect("/login/?error=configuration");
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const packedState = url.searchParams.get("state") || "";
  const [state, encodedNext = ""] = packedState.split(".", 2);
  const expectedState = parseCookies(request)[OAUTH_STATE_COOKIE];
  if (!code || !state || !expectedState || state !== expectedState) return redirect("/login/?error=state");
  let next = "/user/";
  try { next = safeNext(atob(encodedNext), next); } catch (_) { /* use default */ }
  try {
    const accessToken = await exchangeGithubCode(code, `${url.origin}/auth/github/callback`, env);
    const identity = await githubIdentity(accessToken);
    const user = await upsertUser(env, identity);
    if (!user || user.status === "suspended") return redirect("/login/?error=suspended");
    const session = await createSession(env, user.id);
    const destination = user.status === "approved"
      ? (user.role === "admin" && next === "/user/" ? "/admin/" : next)
      : "/login/?status=pending";
    const response = redirect(destination, 302, {
      "set-cookie": cookie(SESSION_COOKIE, session, { maxAge: SESSION_TTL_SECONDS }),
    });
    response.headers.append("set-cookie", cookie(OAUTH_STATE_COOKIE, "", { maxAge: 0 }));
    return response;
  } catch (_) {
    return redirect("/login/?error=github", 302, { "set-cookie": cookie(OAUTH_STATE_COOKIE, "", { maxAge: 0 }) });
  }
}

async function beginGoogle(request, env) {
  if (!env.DB || !googleReady(env)) return redirect("/login/?error=google-configuration");
  const url = new URL(request.url);
  const state = randomToken();
  const next = safeNext(url.searchParams.get("next"));
  const packedState = `${state}.${btoa(next).replace(/=+$/, "")}`;
  const authorize = new URL("https://accounts.google.com/o/oauth2/v2/auth");
  authorize.searchParams.set("client_id", env.OAUTH_GOOGLE_CLIENT_ID);
  authorize.searchParams.set("redirect_uri", `${url.origin}/auth/google/callback`);
  authorize.searchParams.set("response_type", "code");
  authorize.searchParams.set("scope", "openid email profile");
  authorize.searchParams.set("prompt", "select_account");
  authorize.searchParams.set("state", packedState);
  return redirect(authorize.toString(), 302, {
    "set-cookie": cookie(OAUTH_STATE_COOKIE, state, { maxAge: OAUTH_STATE_TTL_SECONDS }),
  });
}

async function finishGoogle(request, env) {
  if (!env.DB || !googleReady(env)) return redirect("/login/?error=google-configuration");
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const packedState = url.searchParams.get("state") || "";
  const [state, encodedNext = ""] = packedState.split(".", 2);
  const expectedState = parseCookies(request)[OAUTH_STATE_COOKIE];
  if (!code || !state || !expectedState || state !== expectedState) return redirect("/login/?error=state");
  let next = "/user/";
  try { next = safeNext(atob(encodedNext), next); } catch (_) { /* use default */ }
  try {
    const accessToken = await exchangeGoogleCode(code, `${url.origin}/auth/google/callback`, env);
    const identity = await googleIdentity(accessToken);
    const user = await upsertUser(env, identity);
    if (!user || user.status === "suspended") return redirect("/login/?error=suspended");
    const session = await createSession(env, user.id);
    const destination = user.status === "approved"
      ? (user.role === "admin" && next === "/user/" ? "/admin/" : next)
      : "/login/?status=pending";
    const response = redirect(destination, 302, {
      "set-cookie": cookie(SESSION_COOKIE, session, { maxAge: SESSION_TTL_SECONDS }),
    });
    response.headers.append("set-cookie", cookie(OAUTH_STATE_COOKIE, "", { maxAge: 0 }));
    return response;
  } catch (_) {
    return redirect("/login/?error=google", 302, { "set-cookie": cookie(OAUTH_STATE_COOKIE, "", { maxAge: 0 }) });
  }
}

async function logout(request, env) {
  const session = await sessionFromRequest(request, env);
  if (session) await env.DB.prepare("DELETE FROM sessions WHERE token_hash = ?").bind(session.tokenHash).run();
  return redirect("/login/?status=signed-out", 303, { "set-cookie": cookie(SESSION_COOKIE, "", { maxAge: 0 }) });
}

function sameOrigin(request) {
  return request.headers.get("origin") === new URL(request.url).origin;
}

async function listUsers(env) {
  const result = await env.DB.prepare(`
    SELECT id, github_login, auth_provider, provider_login, email, name, avatar_url,
           role, status, created_at, last_login_at
      FROM users ORDER BY CASE status WHEN 'pending' THEN 0 ELSE 1 END, created_at DESC
  `).all();
  return json({ users: result.results || [] });
}

async function updateUser(request, env, actor, id) {
  if (!sameOrigin(request)) return json({ error: "Invalid request origin" }, 403);
  let body;
  try { body = await request.json(); } catch (_) { return json({ error: "Invalid JSON" }, 400); }
  const role = body.role === "admin" ? "admin" : body.role === "user" ? "user" : null;
  const status = ["pending", "approved", "suspended"].includes(body.status) ? body.status : null;
  if (!role || !status) return json({ error: "Invalid role or status" }, 400);
  const target = await env.DB.prepare("SELECT id, role, status FROM users WHERE id = ?").bind(id).first();
  if (!target) return json({ error: "User not found" }, 404);
  if (Number(target.id) === Number(actor.id) && (role !== "admin" || status !== "approved")) {
    return json({ error: "You cannot remove your own administrator access" }, 409);
  }
  if (target.role === "admin" && target.status === "approved" && (role !== "admin" || status !== "approved")) {
    const count = await env.DB.prepare("SELECT COUNT(*) AS total FROM users WHERE role = 'admin' AND status = 'approved'").first();
    if (Number(count?.total || 0) < 2) return json({ error: "At least one approved administrator is required" }, 409);
  }
  await env.DB.prepare("UPDATE users SET role = ?, status = ?, updated_at = ? WHERE id = ?")
    .bind(role, status, new Date().toISOString(), id).run();
  if (status !== "approved") await env.DB.prepare("DELETE FROM sessions WHERE user_id = ?").bind(id).run();
  return json({ updated: true });
}

async function handleAuth(request, env, url) {
  if (url.pathname === "/auth/providers" && request.method === "GET") {
    return json({ github: githubReady(env), google: googleReady(env) });
  }
  if (url.pathname === "/auth/github" && request.method === "GET") return beginGithub(request, env);
  if (url.pathname === "/auth/github/callback" && request.method === "GET") return finishGithub(request, env);
  if (url.pathname === "/auth/google" && request.method === "GET") return beginGoogle(request, env);
  if (url.pathname === "/auth/google/callback" && request.method === "GET") return finishGoogle(request, env);
  if (url.pathname === "/auth/logout" && request.method === "POST") return logout(request, env);
  if (url.pathname === "/auth/session" && request.method === "GET") {
    const session = await sessionFromRequest(request, env);
    return session ? json({ authenticated: true, user: publicUser(session.user) }) : json({ authenticated: false }, 401);
  }
  return json({ error: "Not found" }, 404);
}

async function protectedRoute(request, env, url, area) {
  if ((area === "admin" || area === "user") && url.pathname === `/${area}`) return redirect(`/${area}/`, 308);
  if (!configurationReady(env)) return json({ error: "Authentication is not configured" }, 503);
  const session = await sessionFromRequest(request, env);
  if (!session) {
    if (isApi(url.pathname)) return json({ error: "Authentication required" }, 401);
    return redirect(`/login/?next=${encodeURIComponent(url.pathname + url.search)}`);
  }
  const user = session.user;
  if (user.status !== "approved") {
    if (isApi(url.pathname)) return json({ error: "Account approval required" }, 403);
    return redirect("/login/?status=pending");
  }
  if (area === "admin" && user.role !== "admin") return isApi(url.pathname)
    ? json({ error: "Administrator access required" }, 403)
    : redirect("/user/?error=forbidden");
  if ((area === "admin" || area === "user") && url.pathname === `/${area}/api/session`) return json({ authenticated: true, user: publicUser(user) });
  if (area === "admin" && url.pathname === "/admin/api/users" && request.method === "GET") return listUsers(env);
  const match = area === "admin" && url.pathname.match(/^\/admin\/api\/users\/(\d+)$/);
  if (match && request.method === "PATCH") return updateUser(request, env, user, Number(match[1]));
  if ((area === "admin" || area === "user") && url.pathname.startsWith(`/${area}/api/`)) return json({ error: "Not found" }, 404);
  if (!["GET", "HEAD"].includes(request.method)) return json({ error: "Method not allowed" }, 405, { allow: "GET, HEAD" });
  return secure(await env.ASSETS.fetch(request));
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/auth/")) return handleAuth(request, env, url);
    const area = areaFor(url.pathname);
    if (area) return protectedRoute(request, env, url, area);
    if (url.pathname === "/login" || url.pathname.startsWith("/login/")) return secure(await env.ASSETS.fetch(request));
    return env.ASSETS.fetch(request);
  },
};

export { areaFor, emailSet, safeNext, sha256 };
