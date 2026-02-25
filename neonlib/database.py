"""
database.py
Layer   : Data Access Layer (lowest layer)
Rule    : ONLY this file opens SQLite connections.
          Nothing else imports sqlite3.
Exports : initialize_database() + one function per SQL operation.
"""

import sqlite3
import os

DB_PATH = "library.db"


# ─── connection ───────────────────────────────────────────────
def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row          # row["col"] dict-style access
    c.execute("PRAGMA journal_mode=WAL")  # faster concurrent reads
    c.execute("PRAGMA foreign_keys=ON")
    return c


# ══════════════════════════════════════════════════════════════
# STEP-BY-STEP DATABASE INITIALISATION
# Called once at app startup.  Creates every table if absent,
# then seeds a default admin account when the DB is brand new.
# ══════════════════════════════════════════════════════════════
def initialize_database():
    """
    STEP 1  Connect / create library.db
    STEP 2  Create  users          table
    STEP 3  Create  books          table
    STEP 4  Create  issued_books   table
    STEP 5  Create  fines          table
    STEP 6  Create  book_requests  table
    STEP 7  Create  notifications  table
    STEP 8  Create  reading_history table
    STEP 9  Create  wishlist       table
    STEP 10 Seed default admin (only when users table is empty)
    """
    c = _conn()

    # STEP 2 ── users ─────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id      TEXT PRIMARY KEY,
            name         TEXT NOT NULL,
            email        TEXT UNIQUE NOT NULL,
            password     TEXT NOT NULL,       -- SHA-256 hex digest
            role         TEXT NOT NULL DEFAULT 'student',
            created_at   TEXT NOT NULL,
            avatar_color TEXT DEFAULT '#00f5ff'
        )""")

    # STEP 3 ── books ─────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id          TEXT PRIMARY KEY,
            title            TEXT NOT NULL,
            author           TEXT NOT NULL,
            category         TEXT NOT NULL,
            total_copies     INTEGER NOT NULL DEFAULT 1,
            available_copies INTEGER NOT NULL DEFAULT 1,
            added_by         TEXT,
            added_at         TEXT NOT NULL,
            borrow_count     INTEGER DEFAULT 0
        )""")

    # STEP 4 ── issued_books ──────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS issued_books (
            issue_id   TEXT PRIMARY KEY,
            book_id    TEXT NOT NULL,
            user_id    TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            due_date   TEXT NOT NULL,
            FOREIGN KEY (book_id) REFERENCES books(book_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )""")

    # STEP 5 ── fines ─────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS fines (
            fine_id    TEXT PRIMARY KEY,
            user_id    TEXT NOT NULL,
            book_id    TEXT NOT NULL,
            issue_id   TEXT NOT NULL,
            days_late  INTEGER NOT NULL,
            amount     REAL NOT NULL,
            paid       INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )""")

    # STEP 6 ── book_requests ─────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS book_requests (
            request_id TEXT PRIMARY KEY,
            user_id    TEXT NOT NULL,
            user_name  TEXT NOT NULL,
            book_title TEXT NOT NULL,
            author     TEXT DEFAULT '',
            reason     TEXT DEFAULT '',
            status     TEXT DEFAULT 'pending',
            admin_note TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )""")

    # STEP 7 ── notifications ─────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            notif_id   TEXT PRIMARY KEY,
            user_id    TEXT NOT NULL,
            message    TEXT NOT NULL,
            type       TEXT DEFAULT 'info',
            is_read    INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )""")

    # STEP 8 ── reading_history ───────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS reading_history (
            history_id TEXT PRIMARY KEY,
            user_id    TEXT NOT NULL,
            book_id    TEXT NOT NULL,
            book_title TEXT NOT NULL,
            author     TEXT NOT NULL,
            category   TEXT NOT NULL,
            returned_at TEXT NOT NULL,
            days_kept  INTEGER DEFAULT 0,
            rating     INTEGER DEFAULT 0,
            review     TEXT DEFAULT ''
        )""")

    # STEP 9 ── wishlist ──────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            wish_id  TEXT PRIMARY KEY,
            user_id  TEXT NOT NULL,
            book_id  TEXT NOT NULL,
            added_at TEXT NOT NULL,
            UNIQUE(user_id, book_id)
        )""")

    c.commit()

    # STEP 10 ── seed default admin ───────────────────────────
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        import hashlib
        from datetime import datetime
        pw = hashlib.sha256("Admin@123".encode()).hexdigest()
        c.execute("""
            INSERT INTO users (user_id,name,email,password,role,created_at,avatar_color)
            VALUES (?,?,?,?,?,?,?)
        """, ("ADMIN001", "Super Admin", "admin@library.com",
              pw, "admin", datetime.now().isoformat(), "#ff00ff"))
        c.commit()

    c.close()


# ══════════════════════════════════════════════════════════════
# USER QUERIES
# ══════════════════════════════════════════════════════════════
def insert_user(user_id, name, email, pw_hash, role, created_at, avatar_color):
    c = _conn()
    try:
        c.execute("""INSERT INTO users
            (user_id,name,email,password,role,created_at,avatar_color)
            VALUES (?,?,?,?,?,?,?)""",
            (user_id, name, email, pw_hash, role, created_at, avatar_color))
        c.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        c.close()

def get_user_by_email(email):
    c = _conn()
    row = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    c.close()
    return row

def get_user_by_id(uid):
    c = _conn()
    row = c.execute("SELECT * FROM users WHERE user_id=?", (uid,)).fetchone()
    c.close()
    return row

def get_all_users():
    c = _conn()
    rows = c.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    c.close()
    return rows

def count_users():
    c = _conn()
    n = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    c.close()
    return n


# ══════════════════════════════════════════════════════════════
# BOOK QUERIES
# ══════════════════════════════════════════════════════════════
def insert_book(book_id, title, author, category, total_copies, added_by, added_at):
    c = _conn()
    c.execute("""INSERT INTO books
        (book_id,title,author,category,total_copies,available_copies,added_by,added_at,borrow_count)
        VALUES (?,?,?,?,?,?,?,?,0)""",
        (book_id, title, author, category, total_copies, total_copies, added_by, added_at))
    c.commit()
    c.close()

def get_all_books():
    c = _conn()
    rows = c.execute("SELECT * FROM books ORDER BY added_at DESC").fetchall()
    c.close()
    return rows

def get_book_by_id(book_id):
    c = _conn()
    row = c.execute("SELECT * FROM books WHERE book_id=?", (book_id,)).fetchone()
    c.close()
    return row

def update_book_availability(book_id, delta):
    """delta=-1 when issuing (also bumps borrow_count), +1 when returning."""
    c = _conn()
    if delta < 0:
        c.execute("""UPDATE books
            SET available_copies=available_copies+?,
                borrow_count=borrow_count+1
            WHERE book_id=?""", (delta, book_id))
    else:
        c.execute("UPDATE books SET available_copies=available_copies+? WHERE book_id=?",
                  (delta, book_id))
    c.commit()
    c.close()

def delete_book(book_id):
    c = _conn()
    c.execute("DELETE FROM books WHERE book_id=?", (book_id,))
    c.commit()
    c.close()

def count_books():
    c = _conn()
    n = c.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    c.close()
    return n

def get_top_borrowed_books(limit=3):
    c = _conn()
    rows = c.execute("SELECT * FROM books ORDER BY borrow_count DESC LIMIT ?", (limit,)).fetchall()
    c.close()
    return rows


# ══════════════════════════════════════════════════════════════
# ISSUED-BOOKS QUERIES
# ══════════════════════════════════════════════════════════════
def insert_issued_book(issue_id, book_id, user_id, issue_date, due_date):
    c = _conn()
    c.execute("""INSERT INTO issued_books
        (issue_id,book_id,user_id,issue_date,due_date) VALUES (?,?,?,?,?)""",
        (issue_id, book_id, user_id, issue_date, due_date))
    c.commit()
    c.close()

def get_issued_books_by_user(user_id):
    c = _conn()
    rows = c.execute("""
        SELECT ib.*, b.title, b.author, b.category
        FROM issued_books ib JOIN books b ON ib.book_id=b.book_id
        WHERE ib.user_id=? ORDER BY ib.issue_date DESC""", (user_id,)).fetchall()
    c.close()
    return rows

def get_all_issued_books():
    c = _conn()
    rows = c.execute("""
        SELECT ib.*, b.title, u.name AS borrower_name, u.email
        FROM issued_books ib
        JOIN books b ON ib.book_id=b.book_id
        JOIN users u ON ib.user_id=u.user_id
        ORDER BY ib.issue_date DESC""").fetchall()
    c.close()
    return rows

def get_issue_record(book_id, user_id):
    c = _conn()
    row = c.execute(
        "SELECT * FROM issued_books WHERE book_id=? AND user_id=?",
        (book_id, user_id)).fetchone()
    c.close()
    return row

def delete_issue_record(issue_id):
    c = _conn()
    c.execute("DELETE FROM issued_books WHERE issue_id=?", (issue_id,))
    c.commit()
    c.close()

def count_issued():
    c = _conn()
    n = c.execute("SELECT COUNT(*) FROM issued_books").fetchone()[0]
    c.close()
    return n


# ══════════════════════════════════════════════════════════════
# FINES QUERIES
# ══════════════════════════════════════════════════════════════
def insert_fine(fine_id, user_id, book_id, issue_id, days_late, amount, created_at):
    c = _conn()
    c.execute("""INSERT INTO fines
        (fine_id,user_id,book_id,issue_id,days_late,amount,paid,created_at)
        VALUES (?,?,?,?,?,?,0,?)""",
        (fine_id, user_id, book_id, issue_id, days_late, amount, created_at))
    c.commit()
    c.close()

def get_fines_by_user(user_id):
    c = _conn()
    rows = c.execute("""
        SELECT f.*, b.title FROM fines f JOIN books b ON f.book_id=b.book_id
        WHERE f.user_id=? ORDER BY f.created_at DESC""", (user_id,)).fetchall()
    c.close()
    return rows

def get_total_fine_by_user(user_id):
    c = _conn()
    n = c.execute(
        "SELECT COALESCE(SUM(amount),0) FROM fines WHERE user_id=? AND paid=0",
        (user_id,)).fetchone()[0]
    c.close()
    return n


# ══════════════════════════════════════════════════════════════
# BOOK-REQUESTS QUERIES
# ══════════════════════════════════════════════════════════════
def insert_request(req_id, user_id, user_name, book_title, author, reason, ts):
    c = _conn()
    c.execute("""INSERT INTO book_requests
        (request_id,user_id,user_name,book_title,author,reason,status,admin_note,created_at,updated_at)
        VALUES (?,?,?,?,?,?,'pending','',?,?)""",
        (req_id, user_id, user_name, book_title, author, reason, ts, ts))
    c.commit()
    c.close()

def get_all_requests():
    c = _conn()
    rows = c.execute("SELECT * FROM book_requests ORDER BY created_at DESC").fetchall()
    c.close()
    return rows

def get_requests_by_user(user_id):
    c = _conn()
    rows = c.execute(
        "SELECT * FROM book_requests WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)).fetchall()
    c.close()
    return rows

def update_request_status(req_id, status, note, ts):
    c = _conn()
    c.execute(
        "UPDATE book_requests SET status=?,admin_note=?,updated_at=? WHERE request_id=?",
        (status, note, ts, req_id))
    c.commit()
    c.close()

def count_pending_requests():
    c = _conn()
    n = c.execute(
        "SELECT COUNT(*) FROM book_requests WHERE status='pending'").fetchone()[0]
    c.close()
    return n


# ══════════════════════════════════════════════════════════════
# NOTIFICATIONS QUERIES
# ══════════════════════════════════════════════════════════════
def insert_notification(notif_id, user_id, message, ntype, ts):
    c = _conn()
    c.execute("""INSERT INTO notifications
        (notif_id,user_id,message,type,is_read,created_at) VALUES (?,?,?,?,0,?)""",
        (notif_id, user_id, message, ntype, ts))
    c.commit()
    c.close()

def get_notifications(user_id, limit=30):
    c = _conn()
    rows = c.execute(
        "SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)).fetchall()
    c.close()
    return rows

def mark_notifications_read(user_id):
    c = _conn()
    c.execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (user_id,))
    c.commit()
    c.close()

def count_unread_notifications(user_id):
    c = _conn()
    n = c.execute(
        "SELECT COUNT(*) FROM notifications WHERE user_id=? AND is_read=0",
        (user_id,)).fetchone()[0]
    c.close()
    return n


# ══════════════════════════════════════════════════════════════
# READING HISTORY QUERIES
# ══════════════════════════════════════════════════════════════
def insert_reading_history(hist_id, user_id, book_id, book_title, author, category, returned_at, days_kept):
    c = _conn()
    c.execute("""INSERT OR IGNORE INTO reading_history
        (history_id,user_id,book_id,book_title,author,category,returned_at,days_kept,rating,review)
        VALUES (?,?,?,?,?,?,?,?,0,'')""",
        (hist_id, user_id, book_id, book_title, author, category, returned_at, days_kept))
    c.commit()
    c.close()

def get_reading_history(user_id):
    c = _conn()
    rows = c.execute(
        "SELECT * FROM reading_history WHERE user_id=? ORDER BY returned_at DESC",
        (user_id,)).fetchall()
    c.close()
    return rows

def update_rating_review(hist_id, rating, review):
    c = _conn()
    c.execute("UPDATE reading_history SET rating=?,review=? WHERE history_id=?",
              (rating, review, hist_id))
    c.commit()
    c.close()

def get_book_avg_rating(book_id):
    c = _conn()
    row = c.execute(
        "SELECT AVG(rating), COUNT(*) FROM reading_history WHERE book_id=? AND rating>0",
        (book_id,)).fetchone()
    c.close()
    return round(row[0] or 0, 1), row[1] or 0

def get_reviews_for_book(book_id):
    c = _conn()
    rows = c.execute("""
        SELECT rh.*, u.name AS reviewer_name FROM reading_history rh
        JOIN users u ON rh.user_id=u.user_id
        WHERE rh.book_id=? AND rh.review!='' ORDER BY rh.returned_at DESC""",
        (book_id,)).fetchall()
    c.close()
    return rows


# ══════════════════════════════════════════════════════════════
# WISHLIST QUERIES
# ══════════════════════════════════════════════════════════════
def add_to_wishlist(wish_id, user_id, book_id, added_at):
    c = _conn()
    try:
        c.execute("INSERT INTO wishlist (wish_id,user_id,book_id,added_at) VALUES (?,?,?,?)",
                  (wish_id, user_id, book_id, added_at))
        c.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        c.close()

def remove_from_wishlist(user_id, book_id):
    c = _conn()
    c.execute("DELETE FROM wishlist WHERE user_id=? AND book_id=?", (user_id, book_id))
    c.commit()
    c.close()

def get_wishlist(user_id):
    c = _conn()
    rows = c.execute("""
        SELECT w.*, b.title, b.author, b.category, b.available_copies
        FROM wishlist w JOIN books b ON w.book_id=b.book_id
        WHERE w.user_id=? ORDER BY w.added_at DESC""", (user_id,)).fetchall()
    c.close()
    return rows

def is_in_wishlist(user_id, book_id):
    c = _conn()
    r = c.execute(
        "SELECT 1 FROM wishlist WHERE user_id=? AND book_id=?",
        (user_id, book_id)).fetchone()
    c.close()
    return r is not None
