import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import worker, { areaFor, emailSet, safeNext } from "../src/worker.mjs";

class FakeDatabase {
  constructor() {
    this.users = [];
    this.sessions = [];
    this.nextId = 1;
  }

  prepare(sql) {
    const db = this;
    const query = sql.replace(/\s+/g, " ").trim();
    let values = [];
    return {
      bind(...args) { values = args; return this; },
      async first() {
        if (query.includes("FROM sessions s JOIN users u")) {
          const [hash, now] = values;
          const session = db.sessions.find((item) => item.token_hash === hash && item.expires_at > now);
          if (!session) return null;
          const user = db.users.find((item) => item.id === session.user_id);
          return user ? { ...user, expires_at: session.expires_at } : null;
        }
        if (query.startsWith("SELECT id FROM users")) {
          const [provider, providerId, email] = values;
          return db.users.find((item) => (item.auth_provider === provider && item.provider_id === providerId) || item.email.toLowerCase() === email.toLowerCase()) || null;
        }
        if (query.includes("FROM users WHERE auth_provider")) {
          return db.users.find((item) => item.auth_provider === values[0] && item.provider_id === values[1]) || null;
        }
        if (query === "SELECT id, email, role, status FROM users WHERE id = ?") return db.users.find((item) => item.id === values[0]) || null;
        if (query.startsWith("SELECT COUNT(*) AS total")) {
          return { total: db.users.filter((item) => item.role === "admin" && item.status === "approved").length };
        }
        return null;
      },
      async all() {
        if (query.includes("FROM users ORDER BY")) return { results: [...db.users] };
        return { results: [] };
      },
      async run() {
        if (query.startsWith("INSERT INTO sessions")) {
          const [token_hash, user_id, expires_at, created_at, last_seen_at] = values;
          db.sessions.push({ token_hash, user_id, expires_at, created_at, last_seen_at });
        } else if (query.startsWith("INSERT INTO users")) {
          const [github_id, github_login, auth_provider, provider_id, provider_login, email, name, avatar_url, role, status, created_at, updated_at, last_login_at] = values;
          db.users.push({ id: db.nextId++, github_id, github_login, auth_provider, provider_id, provider_login, email, name, avatar_url, role, status, created_at, updated_at, last_login_at });
        } else if (query.startsWith("UPDATE users SET github_id")) {
          const [github_id, github_login, auth_provider, provider_id, provider_login, email, name, avatar_url, forceRole, updated_at, last_login_at, id] = values;
          const user = db.users.find((item) => item.id === id);
          Object.assign(user, { github_id, github_login, auth_provider, provider_id, provider_login, email, name, avatar_url, updated_at, last_login_at });
          if (forceRole) user.role = "admin";
          if (user.status !== "suspended") user.status = "approved";
        } else if (query === "DELETE FROM sessions WHERE token_hash = ?") {
          db.sessions = db.sessions.filter((item) => item.token_hash !== values[0]);
        } else if (query.startsWith("UPDATE users SET role")) {
          const [role, status, updated_at, id] = values;
          const user = db.users.find((item) => item.id === id);
          Object.assign(user, { role, status, updated_at });
        } else if (query === "DELETE FROM sessions WHERE user_id = ?") {
          db.sessions = db.sessions.filter((item) => item.user_id !== values[0]);
        }
        return { success: true };
      },
    };
  }
}

const identities = {
  "token-admin": { id: 101, login: "platform-admin", name: "Platform Admin", email: "admin@example.com" },
  "token-reader": { id: 202, login: "platform-reader", name: "Platform Reader", email: "reader@example.com" },
};

const googleIdentities = {
  "google-reader": { sub: "g-303", name: "Google Reader", email: "google@example.com", email_verified: true, picture: "https://lh3.googleusercontent.com/a/test" },
};

globalThis.fetch = async (input, init = {}) => {
  const url = String(input);
  if (url === "https://github.com/login/oauth/access_token") {
    const code = JSON.parse(init.body).code;
    return Response.json({ access_token: `token-${code}` });
  }
  if (url === "https://api.github.com/user") {
    const identity = identities[String(init.headers.authorization).replace("Bearer ", "")];
    return Response.json({ id: identity.id, login: identity.login, name: identity.name, avatar_url: "https://avatars.githubusercontent.com/u/1" });
  }
  if (url === "https://api.github.com/user/emails") {
    const identity = identities[String(init.headers.authorization).replace("Bearer ", "")];
    return Response.json([{ email: identity.email, primary: true, verified: true }]);
  }
  if (url === "https://oauth2.googleapis.com/token") {
    return Response.json({ access_token: new URLSearchParams(init.body).get("code") });
  }
  if (url === "https://openidconnect.googleapis.com/v1/userinfo") {
    const token = String(init.headers.authorization).replace("Bearer ", "");
    return Response.json(googleIdentities[token]);
  }
  throw new Error(`Unexpected fetch: ${url}`);
};

const db = new FakeDatabase();
const env = {
  DB: db,
  OAUTH_GITHUB_CLIENT_ID: "client-id",
  OAUTH_GITHUB_CLIENT_SECRET: "client-secret",
  OAUTH_GOOGLE_CLIENT_ID: "google-client-id",
  OAUTH_GOOGLE_CLIENT_SECRET: "google-client-secret",
  ADMIN_EMAILS: "admin@example.com",
  ASSETS: { fetch: async (request) => new Response(`asset:${new URL(request.url).pathname}`) },
};

async function call(path, { method = "GET", cookie = "", body, origin } = {}) {
  const headers = {};
  if (cookie) headers.cookie = cookie;
  if (origin) headers.origin = origin;
  if (body) headers["content-type"] = "application/json";
  return worker.fetch(new Request(`https://example.com${path}`, { method, headers, body }), env);
}

function cookieValue(response, name) {
  const match = (response.headers.get("set-cookie") || "").match(new RegExp(`${name}=([^;,]+)`));
  return match && match[1];
}

async function login(code, next = "/user/") {
  const start = await call(`/auth/github?next=${encodeURIComponent(next)}`);
  assert.equal(start.status, 302);
  const authorize = new URL(start.headers.get("location"));
  assert.equal(authorize.hostname, "github.com");
  assert.equal(authorize.searchParams.get("scope"), "read:user user:email");
  const stateCookie = cookieValue(start, "po_oauth_state");
  const state = authorize.searchParams.get("state");
  const callback = await call(`/auth/github/callback?code=${code}&state=${encodeURIComponent(state)}`, {
    cookie: `po_oauth_state=${stateCookie}`,
  });
  return { response: callback, session: cookieValue(callback, "po_session") };
}

async function googleLogin(code, next = "/user/") {
  const start = await call(`/auth/google?next=${encodeURIComponent(next)}`);
  assert.equal(start.status, 302);
  const authorize = new URL(start.headers.get("location"));
  assert.equal(authorize.hostname, "accounts.google.com");
  assert.equal(authorize.searchParams.get("scope"), "openid email profile");
  const stateCookie = cookieValue(start, "po_oauth_state");
  const state = authorize.searchParams.get("state");
  const callback = await call(`/auth/google/callback?code=${code}&state=${encodeURIComponent(state)}`, {
    cookie: `po_oauth_state=${stateCookie}`,
  });
  return { response: callback, session: cookieValue(callback, "po_session") };
}

assert.equal(areaFor("/admin%2Findex.html"), "admin");
const premiumSlugs = [
  "networking",
  "cloud",
  "gitops",
  "devops",
  "containers",
  "kubernetes",
  "openshift",
  "observability",
  "sre",
  "security",
  "platform-engineering",
];
for (const slug of premiumSlugs) {
  assert.equal(areaFor(`/categories/${slug}/index.html`), "premium");
}
assert.equal(areaFor("/public"), null);
assert.equal(safeNext("//evil.example"), "/user/");
assert.equal(safeNext("/admin/"), "/admin/");
assert.deepEqual([...emailSet(" A@example.com, b@example.com ")], ["a@example.com", "b@example.com"]);

let response = await call("/public/index.html");
assert.equal(response.status, 200);
assert.equal(await response.text(), "asset:/public/index.html");

response = await call("/admin/");
assert.equal(response.status, 302);
assert.equal(response.headers.get("location"), "/login/?next=%2Fadmin%2F");
assert.equal(response.headers.get("x-robots-tag"), "noindex, nofollow");

response = await call("/categories/platform-engineering/index.html");
assert.equal(response.status, 200);
assert.match(await response.text(), /Platform/);
assert.equal(response.headers.get("x-robots-tag"), "noindex, nofollow");

response = await call("/categories/kubernetes/index.html");
assert.equal(response.status, 200);
assert.match(await response.text(), /Kubernetes/);

response = await call("/auth/providers");
assert.deepEqual(await response.json(), { github: true, google: true });

const adminLogin = await login("admin");
assert.equal(adminLogin.response.status, 302);
assert.equal(adminLogin.response.headers.get("location"), "/admin/");
assert.ok(adminLogin.session);

response = await call("/admin/", { cookie: `po_session=${adminLogin.session}` });
assert.equal(response.status, 200);
assert.equal(await response.text(), "asset:/admin/");

response = await call("/auth/session", { cookie: `po_session=${adminLogin.session}` });
assert.equal(response.status, 200);
assert.equal((await response.json()).user.role, "admin");

const readerLogin = await login("reader");
assert.equal(readerLogin.response.headers.get("location"), "/user/");
response = await call("/user/", { cookie: `po_session=${readerLogin.session}` });
assert.equal(response.status, 200);

response = await call("/admin/api/users", { cookie: `po_session=${adminLogin.session}` });
assert.equal(response.status, 200);
const users = (await response.json()).users;
const reader = users.find((item) => item.email === "reader@example.com");
assert.equal(reader.status, "approved");

response = await call(`/admin/api/users/${reader.id}`, {
  method: "PATCH",
  cookie: `po_session=${adminLogin.session}`,
  origin: "https://evil.example",
  body: JSON.stringify({ role: "user", status: "approved" }),
});
assert.equal(response.status, 403);

response = await call(`/admin/api/users/${reader.id}`, {
  method: "PATCH",
  cookie: `po_session=${adminLogin.session}`,
  origin: "https://example.com",
  body: JSON.stringify({ role: "admin", status: "approved" }),
});
assert.equal(response.status, 403);

response = await call("/user/", { cookie: `po_session=${readerLogin.session}` });
assert.equal(response.status, 200);

response = await call("/categories/platform-engineering/index.html", { cookie: `po_session=${readerLogin.session}` });
assert.equal(response.status, 200);

response = await call("/categories/kubernetes/index.html", { cookie: `po_session=${readerLogin.session}` });
assert.equal(response.status, 200);

const googleReader = await googleLogin("google-reader");
assert.equal(googleReader.response.headers.get("location"), "/user/");
response = await call("/auth/session", { cookie: `po_session=${googleReader.session}` });
assert.equal((await response.json()).user.provider, "google");

response = await call("/admin/", { cookie: `po_session=${readerLogin.session}` });
assert.equal(response.status, 302);
assert.equal(response.headers.get("location"), "/user/?error=forbidden");

response = await call("/auth/logout", { method: "POST", cookie: `po_session=${readerLogin.session}` });
assert.equal(response.status, 303);
assert.equal(response.headers.get("location"), "/login/?status=signed-out");

const wrangler = readFileSync(new URL("../wrangler.jsonc", import.meta.url), "utf8");
assert.match(wrangler, /"binding"\s*:\s*"DB"/);
assert.match(wrangler, /"run_worker_first"[\s\S]*"\/auth\*"[\s\S]*"\/login\*"[\s\S]*"\/admin\*"[\s\S]*"\/user\*"/);
for (const slug of premiumSlugs) {
  assert.ok(wrangler.includes(`"/categories/${slug}*"`));
}

const sitemap = readFileSync(new URL("../dist/sitemap.xml", import.meta.url), "utf8");
for (const area of ["login", "admin", "user"]) {
  const html = readFileSync(new URL(`../dist/${area}/index.html`, import.meta.url), "utf8");
  assert.match(html, /<meta name="robots" content="noindex,nofollow">/);
  assert.doesNotMatch(sitemap, new RegExp(`/${area}/`));
}
assert.match(readFileSync(new URL("../dist/login/index.html", import.meta.url), "utf8"), /Continue with GitHub/);
assert.match(readFileSync(new URL("../dist/login/index.html", import.meta.url), "utf8"), /Create account/);
assert.doesNotMatch(readFileSync(new URL("../dist/login/index.html", import.meta.url), "utf8"), /assets\/search\.js/);
for (const slug of premiumSlugs) {
  assert.doesNotMatch(sitemap, new RegExp(`/categories/${slug}/`));
}
assert.match(readFileSync(new URL("../dist/admin/index.html", import.meta.url), "utf8"), /data-user-list/);

console.log("custom OAuth auth worker: ok");
