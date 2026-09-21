CREATE TABLE IF NOT EXISTS newsletter_campaigns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  issue_number INTEGER NOT NULL,
  issue_path TEXT NOT NULL UNIQUE,
  issue_title TEXT NOT NULL,
  issue_url TEXT NOT NULL,
  issue_blurb TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'sending', 'partial', 'sent', 'failed')),
  subscriber_count INTEGER NOT NULL DEFAULT 0,
  sent_count INTEGER NOT NULL DEFAULT 0,
  failed_count INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  sent_at TEXT,
  last_error TEXT
);

CREATE TABLE IF NOT EXISTS newsletter_deliveries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  campaign_id INTEGER NOT NULL REFERENCES newsletter_campaigns(id) ON DELETE CASCADE,
  subscriber_id INTEGER NOT NULL REFERENCES newsletter_subscribers(id) ON DELETE CASCADE,
  email TEXT NOT NULL COLLATE NOCASE,
  status TEXT NOT NULL CHECK (status IN ('sent', 'failed')),
  provider_message_id TEXT,
  error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(campaign_id, subscriber_id)
);

CREATE INDEX IF NOT EXISTS newsletter_deliveries_campaign_status_idx
  ON newsletter_deliveries(campaign_id, status);

CREATE INDEX IF NOT EXISTS newsletter_deliveries_subscriber_idx
  ON newsletter_deliveries(subscriber_id);
