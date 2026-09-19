# Authentication setup

The newsletter and core knowledge base remain public. A custom Platform Ops
login protects `/admin*`, `/user*`, and `/categories/platform-engineering*`.
GitHub or Google proves identity; the Worker owns the session; D1 stores account
status and roles. Platform Ops never receives a provider password or stores an
OAuth access token.

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

## 4. Bootstrap the administrator

Add one more repository Actions secret:

```text
ADMIN_EMAILS
```

Its value is a comma-separated list of verified provider email addresses that
must become administrators. The first successful login for a listed email is
approved automatically and receives the `admin` role.

Every other new identity enters `pending`. An administrator reviews it
under `/admin/` and changes its status to `approved`, or to `suspended` when
access must be revoked.

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
2. The configured administrator signs in with GitHub or Google and reaches `/admin/`.
3. A new reader signs in and sees the pending-approval message.
4. The administrator approves that reader in `/admin/`.
5. The reader can then open `/user/` and the Platform Engineering category, but not `/admin/`.
6. A signed-out visitor opening Platform Engineering returns to the requested page after sign-in.
7. Signing out removes the server-side session and clears the browser cookie.

## Security properties

- OAuth state is checked before accepting either provider callback.
- Only verified provider email addresses are accepted.
- Provider access tokens are used once and never persisted.
- Browser session tokens are random; D1 stores only their SHA-256 hashes.
- Session cookies are `HttpOnly`, `Secure`, and `SameSite=Lax`.
- Administrator writes require a same-origin request.
- The last approved administrator cannot remove their own access.
- Private pages use `noindex`, `no-store`, and restrictive security headers.
