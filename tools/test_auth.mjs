import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import worker, { areaFor, emailSet, safeNext } from "../src/worker.mjs";

class FakeDatabase {
  constructor() {
    this.users = [];
    this.sessions = [];
    this.newsletter = [];
    this.campaigns = [];
    this.deliveries = [];
    this.nextId = 1;
    this.nextSubscriberId = 1;
    this.nextCampaignId = 1;
    this.nextDeliveryId = 1;
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
          if (query.includes("FROM newsletter_subscribers")) {
            return { total: db.newsletter.filter((item) => item.status === "subscribed").length };
          }
          if (query.includes("FROM newsletter_deliveries")) {
            return { total: db.deliveries.filter((item) => item.campaign_id === values[0] && item.status === "sent").length };
          }
          return { total: db.users.filter((item) => item.role === "admin" && item.status === "approved").length };
        }
        if (query.includes("FROM newsletter_subscribers") && query.includes("WHERE email")) {
          const [email] = values;
          return db.newsletter.find((item) => item.email.toLowerCase() === email.toLowerCase()) || null;
        }
        if (query === "SELECT * FROM newsletter_campaigns WHERE issue_path = ?") {
          return db.campaigns.find((item) => item.issue_path === values[0]) || null;
        }
        if (query.includes("SUM(CASE WHEN status = 'sent'")) {
          const rows = db.deliveries.filter((item) => item.campaign_id === values[0]);
          return {
            sent: rows.filter((item) => item.status === "sent").length,
            failed: rows.filter((item) => item.status === "failed").length,
          };
        }
        return null;
      },
      async all() {
        if (query.includes("FROM users ORDER BY")) return { results: [...db.users] };
        if (query.includes("FROM newsletter_subscribers") && query.includes("ORDER BY created_at DESC")) {
          return { results: [...db.newsletter].sort((a, b) => String(b.created_at).localeCompare(String(a.created_at))) };
        }
        if (query.includes("FROM newsletter_subscribers s") && query.includes("NOT EXISTS")) {
          const [campaignId, limit] = values;
          const sent = new Set(db.deliveries.filter((item) => item.campaign_id === campaignId && item.status === "sent").map((item) => item.subscriber_id));
          return { results: db.newsletter.filter((item) => item.status === "subscribed" && !sent.has(item.id)).slice(0, limit).map((item) => ({ id: item.id, email: item.email })) };
        }
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
        } else if (query.startsWith("INSERT INTO newsletter_subscribers")) {
          const [email, source, requested_topics, unsubscribe_token, created_at, updated_at] = values;
          db.newsletter.push({
            id: db.nextSubscriberId++,
            email,
            status: "subscribed",
            source,
            requested_topics,
            unsubscribe_token,
            created_at,
            updated_at,
            unsubscribed_at: null,
          });
        } else if (query.startsWith("UPDATE newsletter_subscribers")) {
          const [source, requested_topics, updated_at, id] = values;
          const subscriber = db.newsletter.find((item) => item.id === id);
          Object.assign(subscriber, { status: "subscribed", source, requested_topics, updated_at, unsubscribed_at: null });
        } else if (query.startsWith("INSERT INTO newsletter_campaigns")) {
          const [issue_number, issue_path, issue_title, issue_url, issue_blurb, created_at, updated_at] = values;
          db.campaigns.push({ id: db.nextCampaignId++, issue_number, issue_path, issue_title, issue_url, issue_blurb, status: "draft", subscriber_count: 0, sent_count: 0, failed_count: 0, created_at, updated_at, sent_at: null, last_error: null });
        } else if (query === "UPDATE newsletter_campaigns SET status = 'sending', updated_at = ? WHERE id = ?") {
          const [updated_at, id] = values;
          const campaign = db.campaigns.find((item) => item.id === id);
          Object.assign(campaign, { status: "sending", updated_at });
        } else if (query.startsWith("INSERT INTO newsletter_deliveries")) {
          const [campaign_id, subscriber_id, email, status, provider_message_id, error, created_at, updated_at] = values;
          const existing = db.deliveries.find((item) => item.campaign_id === campaign_id && item.subscriber_id === subscriber_id);
          if (existing) Object.assign(existing, { email, status, provider_message_id, error, updated_at });
          else db.deliveries.push({ id: db.nextDeliveryId++, campaign_id, subscriber_id, email, status, provider_message_id, error, created_at, updated_at });
        } else if (query.startsWith("UPDATE newsletter_campaigns SET status")) {
          const [status, subscriber_count, sent_count, failed_count, updated_at, markSent, sent_at, id] = values;
          const campaign = db.campaigns.find((item) => item.id === id);
          Object.assign(campaign, { status, subscriber_count, sent_count, failed_count, updated_at });
          if (markSent) campaign.sent_at = campaign.sent_at || sent_at;
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
  if (url === "https://api.resend.com/emails") {
    return Response.json({ id: "email-test-id" });
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
  RESEND_API_KEY: "resend-key",
  NEWSLETTER_BATCH_LIMIT: "2",
  ASSETS: {
    fetch: async (request) => {
      const path = new URL(request.url).pathname;
      if (path === "/assets/latest-issue.json") {
        return Response.json({
          number: 67,
          path: "Kubernetes/SERVICE-MESH-OPERATIONS/service-mesh-operations.html",
          title: "Service Mesh Operations",
          blurb: "mTLS identity, policy defaults, retries, and trace headers.",
          url: "https://example.com/Kubernetes/SERVICE-MESH-OPERATIONS/service-mesh-operations.html",
          published_at: "2026-09-15T15:00:00+00:00",
        });
      }
      return new Response(`asset:${path}`);
    },
  },
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
const premiumIssuePaths = [
  "/issues/index.html",
  "/Kubernetes/SERVICE-MESH-OPERATIONS/service-mesh-operations.html",
  "/Kubernetes/SERVICE-MESH-FUNDAMENTALS/service-mesh-fundamentals.html",
  "/Kubernetes/KUBERNETES-CLUSTER-OPERATIONS/kubernetes-cluster-operations.html",
  "/Kubernetes/KUBERNETES-AUTOSCALING/kubernetes-autoscaling.html",
  "/Kubernetes/KUBERNETES-SCHEDULING/kubernetes-scheduling.html",
  "/Kubernetes/KUBERNETES-CONFIG-AND-ACCESS/kubernetes-config-and-access.html",
  "/Kubernetes/KUBERNETES-WORKLOADS/kubernetes-workloads.html",
  "/OpenShift/OPENSHIFT-OPERATIONS/openshift-operations.html",
  "/OpenShift/OPENSHIFT-NETWORKING-STORAGE/openshift-networking-storage.html",
  "/OpenShift/OPENSHIFT-ARCHITECTURE/openshift-architecture.html",
  "/Infrastructure/OS/LINUX/GLOSSARY/linux-unix-glossary.html",
  "/Infrastructure/OS/LINUX/TROUBLESHOOTING/linux-troubleshooting.html",
  "/Infrastructure/OS/LINUX/ADVANCED/linux-advanced.html",
  "/Infrastructure/OS/LINUX/FUNDAMENTALS/linux-fundamentals.html",
  "/SRE/INCIDENT-MANAGEMENT/incident-management.html",
  "/DevOps/CICD/cicd-pipelines.html",
  "/DevOps/K8/OBSERVABILITY/k8-observability.html",
  "/DevOps/K8/STORAGE/k8-storage.html",
  "/DevOps/K8/ERROR/K8-error.html",
  "/DevOps/K8/ARCHITECTURE/k8-architecture.html",
  "/DevOps/K8/Networking/k8-networking.html",
];
for (const slug of premiumSlugs) {
  assert.equal(areaFor(`/categories/${slug}/index.html`), "premium");
}
for (const path of premiumIssuePaths) {
  assert.equal(areaFor(path), "premium");
}
assert.equal(areaFor("/public"), null);
assert.equal(safeNext("//evil.example"), "/user/");
assert.equal(safeNext("/admin/"), "/admin/");
assert.deepEqual([...emailSet(" A@example.com, b@example.com ")], ["a@example.com", "b@example.com"]);

let response = await call("/public/index.html");
assert.equal(response.status, 200);
assert.equal(await response.text(), "asset:/public/index.html");

response = await call("/api/subscribe", {
  method: "POST",
  origin: "https://evil.example",
  body: JSON.stringify({ email: "reader@example.com" }),
});
assert.equal(response.status, 403);

response = await call("/api/subscribe", {
  method: "POST",
  origin: "https://example.com",
  body: JSON.stringify({ email: " Reader@Example.COM ", source: "homepage", topic_request: "OpenShift, SRE" }),
});
assert.equal(response.status, 200);
assert.equal((await response.json()).subscribed, true);
assert.equal(db.newsletter.length, 1);
assert.equal(db.newsletter[0].email, "reader@example.com");
assert.equal(db.newsletter[0].requested_topics, "OpenShift, SRE");

response = await call("/api/subscribe", {
  method: "POST",
  origin: "https://example.com",
  body: JSON.stringify({ email: "reader@example.com", source: "footer" }),
});
assert.equal(response.status, 200);
assert.equal(db.newsletter.length, 1);
assert.equal(db.newsletter[0].source, "footer");

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

response = await call("/issues/index.html");
assert.equal(response.status, 200);
assert.match(await response.text(), /Latest Issues/);

response = await call("/Kubernetes/SERVICE-MESH-OPERATIONS/service-mesh-operations.html");
assert.equal(response.status, 200);
assert.match(await response.text(), /Latest Issues|Protected Path/);

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

response = await call("/admin/api/subscribers", { cookie: `po_session=${adminLogin.session}` });
assert.equal(response.status, 200);
assert.equal((await response.json()).subscribers[0].email, "reader@example.com");

response = await call("/admin/api/newsletter/latest", { cookie: `po_session=${adminLogin.session}` });
assert.equal(response.status, 200);
let newsletter = await response.json();
assert.equal(newsletter.emailConfigured, true);
assert.equal(newsletter.subscribers, 1);
assert.equal(newsletter.issue.number, 67);

response = await call("/admin/api/newsletter/send-latest", {
  method: "POST",
  cookie: `po_session=${adminLogin.session}`,
  origin: "https://evil.example",
  body: "{}",
});
assert.equal(response.status, 403);

response = await call("/admin/api/newsletter/send-latest", {
  method: "POST",
  cookie: `po_session=${adminLogin.session}`,
  origin: "https://example.com",
  body: "{}",
});
assert.equal(response.status, 200);
newsletter = await response.json();
assert.equal(newsletter.sent, 1);
assert.equal(newsletter.remaining, 0);
assert.equal(db.deliveries.length, 1);

response = await call("/admin/api/newsletter/send-latest", {
  method: "POST",
  cookie: `po_session=${adminLogin.session}`,
  origin: "https://example.com",
  body: "{}",
});
assert.equal(response.status, 200);
assert.equal((await response.json()).sent, 0);
assert.equal(db.deliveries.length, 1);

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

response = await call("/issues/index.html", { cookie: `po_session=${readerLogin.session}` });
assert.equal(response.status, 200);

response = await call("/Kubernetes/SERVICE-MESH-OPERATIONS/service-mesh-operations.html", { cookie: `po_session=${readerLogin.session}` });
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
assert.match(wrangler, /"run_worker_first"[\s\S]*"\/auth\*"[\s\S]*"\/api\*"[\s\S]*"\/login\*"[\s\S]*"\/admin\*"[\s\S]*"\/user\*"/);
for (const slug of premiumSlugs) {
  assert.ok(wrangler.includes(`"/categories/${slug}*"`));
}
for (const prefix of ["/issues*", "/Kubernetes*", "/OpenShift*", "/Infrastructure*", "/SRE*", "/DevOps*"]) {
  assert.ok(wrangler.includes(`"${prefix}"`));
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
assert.doesNotMatch(sitemap, /\/issues\//);
for (const path of premiumIssuePaths.filter((item) => item !== "/issues/index.html")) {
  assert.doesNotMatch(sitemap, new RegExp(path.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
}
assert.match(readFileSync(new URL("../dist/admin/index.html", import.meta.url), "utf8"), /data-user-list/);

console.log("custom OAuth auth worker: ok");
