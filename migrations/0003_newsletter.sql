CREATE TABLE IF NOT EXISTS newsletter_subscribers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL COLLATE NOCASE UNIQUE,
  status TEXT NOT NULL DEFAULT 'subscribed' CHECK (status IN ('subscribed', 'unsubscribed')),
  source TEXT NOT NULL DEFAULT 'homepage',
  requested_topics TEXT NOT NULL DEFAULT '',
  unsubscribe_token TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  unsubscribed_at TEXT
);

CREATE INDEX IF NOT EXISTS newsletter_subscribers_status_created_idx
  ON newsletter_subscribers(status, created_at);

CREATE INDEX IF NOT EXISTS newsletter_subscribers_email_idx
  ON newsletter_subscribers(email);
