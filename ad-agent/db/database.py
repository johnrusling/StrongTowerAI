import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'ads.db')


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            platform    TEXT    NOT NULL,
            objective   TEXT,
            budget_daily REAL,
            start_date  TEXT,
            end_date    TEXT,
            status      TEXT    DEFAULT 'draft',
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS ads (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id         INTEGER REFERENCES campaigns(id),
            platform            TEXT    NOT NULL,
            campaign_name       TEXT,
            headline            TEXT,
            body_copy           TEXT,
            cta                 TEXT,
            creative_notes      TEXT,
            audience            TEXT,
            offer               TEXT,
            goal                TEXT,
            status              TEXT    DEFAULT 'draft',
            edit_notes          TEXT,
            created_at          TEXT    DEFAULT (datetime('now')),
            approved_at         TEXT,
            published_at        TEXT,
            platform_campaign_id TEXT,
            platform_ad_id      TEXT,
            image_path          TEXT
        );

        CREATE TABLE IF NOT EXISTS performance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_id       INTEGER REFERENCES ads(id),
            date        TEXT    NOT NULL,
            impressions INTEGER DEFAULT 0,
            clicks      INTEGER DEFAULT 0,
            ctr         REAL    DEFAULT 0,
            spend       REAL    DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            cpc         REAL    DEFAULT 0,
            roas        REAL    DEFAULT 0,
            fetched_at  TEXT    DEFAULT (datetime('now'))
        );
    ''')
    conn.commit()

    # Migrate existing databases: add image_path if missing
    cols = [r[1] for r in conn.execute("PRAGMA table_info(ads)")]
    if 'image_path' not in cols:
        conn.execute('ALTER TABLE ads ADD COLUMN image_path TEXT')
        conn.commit()

    conn.close()


def get_approved_without_images() -> list[dict]:
    conn = get_connection()
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM ads WHERE status = 'approved' AND (image_path IS NULL OR image_path = '')"
    )]
    conn.close()
    return rows


def save_image_path(ad_id: int, image_path: str):
    conn = get_connection()
    conn.execute('UPDATE ads SET image_path = ? WHERE id = ?', (image_path, ad_id))
    conn.commit()
    conn.close()


def save_ads(ads: list[dict]) -> list[int]:
    conn = get_connection()
    ids = []
    for ad in ads:
        cur = conn.execute(
            '''INSERT INTO ads
               (platform, campaign_name, headline, body_copy, cta,
                creative_notes, audience, offer, goal)
               VALUES (:platform, :campaign_name, :headline, :body_copy,
                       :cta, :creative_notes, :audience, :offer, :goal)''',
            ad,
        )
        ids.append(cur.lastrowid)
    conn.commit()
    conn.close()
    return ids


def get_ads_by_status(status: str) -> list[dict]:
    conn = get_connection()
    rows = [dict(r) for r in conn.execute(
        'SELECT * FROM ads WHERE status = ? ORDER BY created_at DESC', (status,)
    )]
    conn.close()
    return rows


def update_ad_status(ad_id: int, status: str, **kwargs):
    conn = get_connection()
    updates: dict = {'status': status}
    updates.update(kwargs)

    if status == 'approved' and 'approved_at' not in updates:
        updates['approved_at'] = datetime.now().isoformat()
    elif status == 'live' and 'published_at' not in updates:
        updates['published_at'] = datetime.now().isoformat()

    set_clause = ', '.join(f'{k} = ?' for k in updates)
    conn.execute(
        f'UPDATE ads SET {set_clause} WHERE id = ?',
        [*updates.values(), ad_id],
    )
    conn.commit()
    conn.close()


def save_performance(metrics: dict):
    conn = get_connection()
    conn.execute(
        '''INSERT INTO performance
           (ad_id, date, impressions, clicks, ctr, spend, conversions, cpc, roas)
           VALUES (:ad_id, :date, :impressions, :clicks, :ctr,
                   :spend, :conversions, :cpc, :roas)''',
        metrics,
    )
    conn.commit()
    conn.close()


def get_live_ads() -> list[dict]:
    conn = get_connection()
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM ads WHERE status = 'live'"
    )]
    conn.close()
    return rows


def get_status_counts() -> list[dict]:
    conn = get_connection()
    rows = [dict(r) for r in conn.execute(
        'SELECT status, COUNT(*) as count FROM ads GROUP BY status ORDER BY status'
    )]
    conn.close()
    return rows
