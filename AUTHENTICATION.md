# Authentication setup

The knowledge base remains public. A custom Platform Ops login protects only
`/admin*` and `/user*`. GitHub proves identity; the Worker owns the session;
D1 stores account status and roles. Platform Ops never receives a password or
stores a GitHub access token.

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
applies `migrations/0001_auth.sql` before deploying. The ID is never written to
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

## 3. Bootstrap the administrator

Add one more repository Actions secret:

```text
ADMIN_EMAILS
```

Its value is a comma-separated list of verified GitHub email addresses that
must become administrators. The first successful login for a listed email is
approved automatically and receives the `admin` role.

Every other new GitHub identity enters `pending`. An administrator reviews it
under `/admin/` and changes its status to `approved`, or to `suspended` when
access must be revoked.

The repository must also retain its existing deployment secrets:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

## 4. Deploy and verify

```bash
bash tools/build.sh
node tools/test_auth.mjs
git add -A
git commit -m "Add custom GitHub authentication and account approval"
git push
```

The workflow refuses to deploy without every required value, applies the D1
migration, syncs encrypted Worker secrets, deploys, and verifies that both
private areas redirect to the custom login.

Verify in a private browser window:

1. `/login/` shows the branded Platform Ops sign-in page.
2. The configured administrator signs in with GitHub and reaches `/admin/`.
3. A new reader signs in and sees the pending-approval message.
4. The administrator approves that reader in `/admin/`.
5. The reader can then open `/user/` but cannot open `/admin/`.
6. Signing out removes the server-side session and clears the browser cookie.

## Security properties

- OAuth state is checked before accepting GitHub's callback.
- Only verified GitHub email addresses are accepted.
- GitHub access tokens are used once and never persisted.
- Browser session tokens are random; D1 stores only their SHA-256 hashes.
- Session cookies are `HttpOnly`, `Secure`, and `SameSite=Lax`.
- Administrator writes require a same-origin request.
- The last approved administrator cannot remove their own access.
- Private pages use `noindex`, `no-store`, and restrictive security headers.
