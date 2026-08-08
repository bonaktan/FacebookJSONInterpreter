#!/usr/bin/env python3
"""
FB Export Archive — one app that loads a Facebook data export into SQLite
and serves it as a browsable, paginated chat archive.

First run: open the app, it asks where your export folder is (and your
name, to align sent messages), parses everything, then shows the archive.
Later runs: it already has the data, so it goes straight to the archive.

Usage:
    python app.py [--db fb_data.sqlite3] [--port 5000] [--host 127.0.0.1]
"""

import argparse
import json
import math
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, g, redirect, render_template, request, url_for

app = Flask(__name__)

THREADS_PER_PAGE = 25
MESSAGES_PER_PAGE = 50
CATEGORIES = ["archived_threads", "filtered_threads", "inbox", "message_requests"]
ATTACHMENT_FIELDS = {
    "photos": "photo",
    "videos": "video",
    "gifs": "gif",
    "audio_files": "audio",
    "files": "file",
}

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS app_meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS threads (
    thread_path         TEXT PRIMARY KEY,
    category            TEXT NOT NULL CHECK (category IN
                            ('inbox','archived_threads','filtered_threads','message_requests')),
    title               TEXT,
    is_still_participant INTEGER,
    is_pending          INTEGER,
    cover_image_uri     TEXT,
    cover_image_ts      INTEGER,
    joinable_mode_mode  INTEGER,
    joinable_mode_link  TEXT
);

CREATE TABLE IF NOT EXISTS participants (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_path TEXT NOT NULL REFERENCES threads(thread_path) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    UNIQUE (thread_path, name)
);

CREATE TABLE IF NOT EXISTS messages (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_path             TEXT NOT NULL REFERENCES threads(thread_path) ON DELETE CASCADE,
    sender_name             TEXT NOT NULL,
    timestamp_ms            INTEGER NOT NULL,
    content                 TEXT,
    is_geoblocked_for_viewer INTEGER,
    call_duration           INTEGER,
    missed                  INTEGER,
    is_unsent               INTEGER,
    ip                      TEXT
);

CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_path);
CREATE INDEX IF NOT EXISTS idx_messages_ts     ON messages(timestamp_ms);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_name);

CREATE TABLE IF NOT EXISTS attachments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id  INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    kind        TEXT NOT NULL CHECK (kind IN ('photo','video','gif','audio','file','sticker')),
    uri         TEXT,
    creation_timestamp INTEGER
);

CREATE INDEX IF NOT EXISTS idx_attachments_message ON attachments(message_id);
CREATE INDEX IF NOT EXISTS idx_attachments_kind    ON attachments(kind);

CREATE TABLE IF NOT EXISTS shares (
    message_id  INTEGER PRIMARY KEY REFERENCES messages(id) ON DELETE CASCADE,
    link        TEXT,
    share_text  TEXT
);

CREATE TABLE IF NOT EXISTS reactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id  INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    reaction    TEXT,
    actor       TEXT
);

CREATE INDEX IF NOT EXISTS idx_reactions_message ON reactions(message_id);
"""


# ---------------------------------------------------------------- db helpers

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DB_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db_file(db_path: Path):
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()


def get_meta(conn, key, default=None):
    row = conn.execute("SELECT value FROM app_meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_meta(conn, key, value):
    conn.execute(
        "INSERT INTO app_meta (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def is_configured():
    db_path = Path(app.config["DB_PATH"])
    if not db_path.is_file():
        return False
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute("SELECT value FROM app_meta WHERE key = 'export_loaded'").fetchone()
        return bool(row and row[0] == "1")
    except sqlite3.OperationalError:
        return False
    finally:
        conn.close()


# ------------------------------------------------------------- loader logic

def fix_text(value):
    """FB exports encode UTF-8 bytes as Latin-1. Re-encode/decode to repair."""
    if not isinstance(value, str):
        return value
    try:
        return value.encode("latin1").decode("utf8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def fix_json(obj):
    if isinstance(obj, str):
        return fix_text(obj)
    if isinstance(obj, list):
        return [fix_json(x) for x in obj]
    if isinstance(obj, dict):
        return {fix_text(k): fix_json(v) for k, v in obj.items()}
    return obj


def find_thread_dirs(export_root: Path):
    for category in CATEGORIES:
        cat_dir = export_root / category
        if not cat_dir.is_dir():
            continue
        for thread_dir in sorted(cat_dir.iterdir()):
            if thread_dir.is_dir():
                yield category, thread_dir


def load_thread_messages(thread_dir: Path):
    msg_files = sorted(
        thread_dir.glob("message_*.json"),
        key=lambda p: int(p.stem.split("_")[-1]) if p.stem.split("_")[-1].isdigit() else 0,
    )
    if not msg_files:
        return None

    merged = None
    all_messages = []
    for mf in msg_files:
        with open(mf, "r", encoding="utf-8") as f:
            data = json.load(f)
        data = fix_json(data)
        all_messages.extend(data.get("messages", []))
        if merged is None:
            merged = data
        else:
            for key, val in data.items():
                if key != "messages" and key not in merged:
                    merged[key] = val

    merged["messages"] = all_messages
    return merged


def _to_int_bool(val):
    return None if val is None else int(bool(val))


def insert_thread(conn, category, thread_path, data):
    image = data.get("image") or {}
    joinable = data.get("joinable_mode") or {}

    conn.execute(
        """
        INSERT OR REPLACE INTO threads
            (thread_path, category, title, is_still_participant, is_pending,
             cover_image_uri, cover_image_ts, joinable_mode_mode, joinable_mode_link)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            thread_path,
            category,
            data.get("title"),
            _to_int_bool(data.get("is_still_participant")) if "is_still_participant" in data else None,
            _to_int_bool(data.get("is_pending")) if "is_pending" in data else None,
            image.get("uri"),
            image.get("creation_timestamp"),
            joinable.get("mode"),
            joinable.get("link"),
        ),
    )

    for p in data.get("participants", []):
        conn.execute(
            "INSERT OR IGNORE INTO participants (thread_path, name) VALUES (?, ?)",
            (thread_path, p.get("name")),
        )


def insert_message(conn, thread_path, msg):
    cur = conn.execute(
        """
        INSERT INTO messages
            (thread_path, sender_name, timestamp_ms, content,
             is_geoblocked_for_viewer, call_duration, missed, is_unsent, ip)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            thread_path,
            msg.get("sender_name"),
            msg.get("timestamp_ms"),
            msg.get("content"),
            _to_int_bool(msg.get("is_geoblocked_for_viewer")),
            msg.get("call_duration"),
            _to_int_bool(msg.get("missed")),
            _to_int_bool(msg.get("is_unsent")),
            msg.get("ip"),
        ),
    )
    message_id = cur.lastrowid

    for field, kind in ATTACHMENT_FIELDS.items():
        for item in msg.get(field, []) or []:
            conn.execute(
                "INSERT INTO attachments (message_id, kind, uri, creation_timestamp) VALUES (?, ?, ?, ?)",
                (message_id, kind, item.get("uri"), item.get("creation_timestamp")),
            )

    sticker = msg.get("sticker")
    if sticker:
        conn.execute(
            "INSERT INTO attachments (message_id, kind, uri, creation_timestamp) VALUES (?, 'sticker', ?, NULL)",
            (message_id, sticker.get("uri")),
        )

    share = msg.get("share")
    if share:
        conn.execute(
            "INSERT OR REPLACE INTO shares (message_id, link, share_text) VALUES (?, ?, ?)",
            (message_id, share.get("link"), share.get("share_text")),
        )

    for r in msg.get("reactions", []) or []:
        conn.execute(
            "INSERT INTO reactions (message_id, reaction, actor) VALUES (?, ?, ?)",
            (message_id, r.get("reaction"), r.get("actor")),
        )


def run_import(export_root: Path, owner_name: str):
    """Parse the export and load it into the configured SQLite DB."""
    db_path = Path(app.config["DB_PATH"])
    init_db_file(db_path)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    thread_count = 0
    message_count = 0

    for category, thread_dir in find_thread_dirs(export_root):
        data = load_thread_messages(thread_dir)
        if data is None:
            continue

        thread_path = data.get("thread_path") or f"{category}/{thread_dir.name}"

        insert_thread(conn, category, thread_path, data)
        for msg in data.get("messages", []):
            insert_message(conn, thread_path, msg)
            message_count += 1

        thread_count += 1
        conn.commit()

    set_meta(conn, "owner_name", owner_name or "")
    set_meta(conn, "export_root", str(export_root))
    set_meta(conn, "export_loaded", "1")
    conn.commit()
    conn.close()

    return thread_count, message_count


# ------------------------------------------------------------------ template filters

@app.template_filter("fmt_ts")
def fmt_ts(ms):
    if not ms:
        return ""
    return datetime.fromtimestamp(ms / 1000).strftime("%b %d, %Y · %I:%M %p")


@app.template_filter("initials")
def initials(name):
    if not name:
        return "?"
    parts = name.split()
    return "".join(p[0].upper() for p in parts[:2])


# ------------------------------------------------------------- setup gating

@app.before_request
def require_setup():
    if request.endpoint in ("setup", "static", None):
        return
    if not is_configured():
        return redirect(url_for("setup"))


# --------------------------------------------------------------------- routes

@app.route("/setup", methods=["GET", "POST"])
def setup():
    if request.method == "GET":
        if is_configured():
            return redirect(url_for("index"))
        return render_template("setup.html", error=None)

    export_path_raw = request.form.get("export_path", "").strip()
    owner_name = request.form.get("owner_name", "").strip()

    export_root = Path(export_path_raw).expanduser()
    if not export_path_raw or not export_root.is_dir():
        return render_template(
            "setup.html",
            error=f"Couldn't find a folder at: {export_path_raw or '(empty)'}",
        )

    found_any = any((export_root / c).is_dir() for c in CATEGORIES)
    if not found_any:
        return render_template(
            "setup.html",
            error="That folder doesn't contain any of inbox/, archived_threads/, "
                  "filtered_threads/, or message_requests/. Point me at the export root.",
        )

    thread_count, message_count = run_import(export_root, owner_name)

    return redirect(url_for("index", imported=f"{thread_count}:{message_count}"))


@app.route("/")
def index():
    db = get_db()
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "", type=str).strip()

    where = ""
    params = []
    if q:
        where = "WHERE t.title LIKE ? OR t.thread_path LIKE ?"
        params = [f"%{q}%", f"%{q}%"]

    total = db.execute(f"SELECT COUNT(*) FROM threads t {where}", params).fetchone()[0]
    page, total_pages, offset = paginate(total, page, THREADS_PER_PAGE)

    rows = db.execute(
        f"""
        SELECT
            t.thread_path, t.title, t.category, t.is_pending,
            COUNT(m.id) AS message_count,
            MAX(m.timestamp_ms) AS last_message_ms
        FROM threads t
        LEFT JOIN messages m ON m.thread_path = t.thread_path
        {where}
        GROUP BY t.thread_path
        ORDER BY (last_message_ms IS NULL), last_message_ms DESC
        LIMIT ? OFFSET ?
        """,
        params + [THREADS_PER_PAGE, offset],
    ).fetchall()

    threads = []
    for r in rows:
        parts = db.execute(
            "SELECT name FROM participants WHERE thread_path = ? LIMIT 4",
            (r["thread_path"],),
        ).fetchall()
        threads.append({**dict(r), "participants": [p["name"] for p in parts]})

    imported = request.args.get("imported")
    import_summary = None
    if imported and ":" in imported:
        t, m = imported.split(":")
        import_summary = f"Imported {t} threads, {m} messages."

    return render_template(
        "index.html",
        threads=threads,
        page=page,
        total_pages=total_pages,
        total=total,
        q=q,
        import_summary=import_summary,
    )


@app.route("/thread/<path:thread_path>")
def thread_view(thread_path):
    db = get_db()
    page = request.args.get("page", 1, type=int)

    thread = db.execute("SELECT * FROM threads WHERE thread_path = ?", (thread_path,)).fetchone()
    if thread is None:
        abort(404)

    participants = [
        r["name"] for r in db.execute(
            "SELECT name FROM participants WHERE thread_path = ?", (thread_path,)
        ).fetchall()
    ]

    total = db.execute(
        "SELECT COUNT(*) FROM messages WHERE thread_path = ?", (thread_path,)
    ).fetchone()[0]
    page, total_pages, offset = paginate(total, page, MESSAGES_PER_PAGE)

    msg_rows = db.execute(
        """
        SELECT * FROM messages
        WHERE thread_path = ?
        ORDER BY timestamp_ms ASC
        LIMIT ? OFFSET ?
        """,
        (thread_path, MESSAGES_PER_PAGE, offset),
    ).fetchall()

    message_ids = [r["id"] for r in msg_rows]
    attachments_by_msg, reactions_by_msg, shares_by_msg = {}, {}, {}

    if message_ids:
        placeholders = ",".join("?" * len(message_ids))
        for r in db.execute(f"SELECT * FROM attachments WHERE message_id IN ({placeholders})", message_ids):
            attachments_by_msg.setdefault(r["message_id"], []).append(dict(r))
        for r in db.execute(f"SELECT * FROM reactions WHERE message_id IN ({placeholders})", message_ids):
            reactions_by_msg.setdefault(r["message_id"], []).append(dict(r))
        for r in db.execute(f"SELECT * FROM shares WHERE message_id IN ({placeholders})", message_ids):
            shares_by_msg[r["message_id"]] = dict(r)

    owner = get_meta(db, "owner_name") or (participants[0] if participants else None)

    messages = []
    for r in msg_rows:
        m = dict(r)
        m["attachments"] = attachments_by_msg.get(r["id"], [])
        m["reactions"] = reactions_by_msg.get(r["id"], [])
        m["share"] = shares_by_msg.get(r["id"])
        m["is_owner"] = m["sender_name"] == owner
        messages.append(m)

    return render_template(
        "thread.html",
        thread=dict(thread),
        participants=participants,
        messages=messages,
        page=page,
        total_pages=total_pages,
        total=total,
        owner=owner,
    )


def paginate(total_rows, page, per_page):
    total_pages = max(1, math.ceil(total_rows / per_page))
    page = max(1, min(page, total_pages))
    offset = (page - 1) * per_page
    return page, total_pages, offset


# ---------------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description="FB export loader + archive viewer")
    parser.add_argument("--db", default="fb_data.sqlite3", help="Where to store/read the SQLite database")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    app.config["DB_PATH"] = args.db
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
