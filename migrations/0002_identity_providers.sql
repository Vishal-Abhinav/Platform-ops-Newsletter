ALTER TABLE users ADD COLUMN auth_provider TEXT NOT NULL DEFAULT 'github';
ALTER TABLE users ADD COLUMN provider_id TEXT;
ALTER TABLE users ADD COLUMN provider_login TEXT;

UPDATE users
   SET auth_provider = 'github',
       provider_id = github_id,
       provider_login = github_login
 WHERE provider_id IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS users_provider_identity_idx
  ON users(auth_provider, provider_id);

