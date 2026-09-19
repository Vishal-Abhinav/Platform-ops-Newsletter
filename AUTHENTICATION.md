# Authentication setup

The newsletter and core knowledge base remain public. A custom Platform Ops
login protects `/admin*`, `/user*`, and the isolated operations path:
Networking, Cloud, GitOps, DevOps, Containers, Kubernetes, OpenShift,
Observability, SRE, Security, and Platform Engineering.
GitHub or Google proves identity; the Worker owns the session; D1 stores account
status and roles. Signup opens a normal user account immediately. Platform Ops
never receives a provider password or stores an OAuth access token.

## 1. Create the D1 database

In **Cloudflare Dashboard > Storage & databases > D1 SQL Database**, create:

```text
platform-ops-auth
```

Copy its database ID. Add it to the GitHub repository's Actions secrets as:

```text
D1_DATABASE_ID
```

The deployment workflow inserts that ID into a temporary Wrangler config and
applies all files in `migrations/` before deploying. The ID is never written to
the tracked config.

## 2. Create the GitHub OAuth application

Open **GitHub > Settings > Developer settings > OAuth Apps > New OAuth App**.

```text
Application name: Platform Ops
Homepage URL: https://platformops.srivantechnologies.com/
Authorization callback URL: https://platformops.srivantechnologies.com/auth/github/callback
```

Create a client secret. Store the OAuth values as repository Actions secrets:

```text
OAUTH_GITHUB_CLIENT_ID
OAUTH_GITHUB_CLIENT_SECRET
```

Never commit or paste the client secret into an issue, log, or chat.

## 3. Optional: enable Google sign-in

In [Google Cloud Console](https://console.cloud.google.com/apis/credentials),
configure the OAuth consent screen and create a **Web application** OAuth client.

```text
Authorized JavaScript origin: https://platformops.srivantechnologies.com
Authorized redirect URI: https://platformops.srivantechnologies.com/auth/google/callback
```

Add the values as optional GitHub Actions secrets. The Google button remains
hidden until both are present, so GitHub authentication continues to work by
itself.

```text
OAUTH_GOOGLE_CLIENT_ID
OAUTH_GOOGLE_CLIENT_SECRET
```

## 4. Restrict the administrator

Add one more repository Actions secret:

```text
ADMIN_EMAILS
```

Its value is a comma-separated list of verified provider email addresses that
may become administrators. Set this to Vishal's verified GitHub/Google email.
The first successful login for a listed email receives the `admin` role.

Every other new identity becomes an approved `user` immediately after signup.
The admin console can suspend or restore users, but it cannot promote another
email to administrator unless that email is listed in `ADMIN_EMAILS`.

The repository must also retain its existing deployment secrets:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

## 5. Deploy and verify

```bash
bash tools/build.sh
node tools/test_auth.mjs
git add -A
git commit -m "Enhance member authentication and premium access"
git push
```

The workflow refuses to deploy without every required value, applies the D1
migration, syncs encrypted Worker secrets, deploys, and verifies that both
authenticated areas are protected by the Worker.

Verify in a private browser window:

1. `/login/` shows the branded Platform Ops sign-in page.
2. A signed-out visitor opening an isolated operations category sees the category heading and a login-required panel.
3. The configured Vishal administrator signs in with GitHub or Google and reaches `/admin/`.
4. A new reader signs up and lands directly in `/user/`.
5. The reader can open isolated operations categories, but not `/admin/`.
6. Signing out removes the server-side session and clears the browser cookie.

## Security properties

- OAuth state is checked before accepting either provider callback.
- Only verified provider email addresses are accepted.
- Provider access tokens are used once and never persisted.
- Browser session tokens are random; D1 stores only their SHA-256 hashes.
- Session cookies are `HttpOnly`, `Secure`, and `SameSite=Lax`.
- Administrator writes require a same-origin request.
- Only `ADMIN_EMAILS` accounts can receive the administrator role.
- The last administrator cannot remove their own access.
- Private pages use `noindex`, `no-store`, and restrictive security headers.
