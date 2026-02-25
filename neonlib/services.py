"""
services.py
Layer : Business Logic Layer
Rule  : All domain rules live here.
        May call database.py and utils.py.
        Must NOT import streamlit.
        UI layer calls these functions and renders the results.
"""

from datetime import datetime
import database as db
from utils import (
    gen_book_id, gen_issue_id, gen_fine_id,
    gen_request_id, gen_notif_id, gen_hist_id, gen_wish_id,
    now_iso, due_iso,
    linear_search_books, linear_search_users,
    get_unique_authors, get_unique_categories,
    get_top_n_books,
)


# ══════════════════════════════════════════════════════════════
# BOOK SERVICES
# ══════════════════════════════════════════════════════════════

def add_book(title, author, category, total_copies, added_by) -> tuple[bool, str]:
    if not title.strip():   return False, "Title cannot be empty."
    if not author.strip():  return False, "Author cannot be empty."
    if not category.strip():return False, "Category cannot be empty."
    if total_copies < 1:    return False, "Copies must be at least 1."
    bid = gen_book_id()
    db.insert_book(bid, title.strip(), author.strip(),
                   category.strip(), total_copies, added_by, now_iso())
    return True, f"'{title}' added. ID: {bid}"


def remove_book(book_id) -> tuple[bool, str]:
    book = db.get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    for row in db.get_all_issued_books():
        if row["book_id"] == book_id:
            return False, "Cannot delete: book has active loans."
    db.delete_book(book_id)
    return True, f"'{book['title']}' deleted."


def all_books_as_dicts() -> list:
    return [dict(r) for r in db.get_all_books()]


def search_books(query: str) -> list:
    """Linear search O(n) via utils.py."""
    return linear_search_books(all_books_as_dicts(), query)


def all_users_as_dicts() -> list:
    return [dict(r) for r in db.get_all_users()]


def search_users(query: str) -> list:
    return linear_search_users(all_users_as_dicts(), query)


def library_stats() -> dict:
    """
    Builds the admin dashboard metrics.
    Uses SET for unique counts (O(n) build / O(1) membership).
    Uses SORT for top books O(n log n).
    """
    books = all_books_as_dicts()
    return {
        "total_books":        db.count_books(),
        "total_users":        db.count_users(),
        "total_issued":       db.count_issued(),
        "unique_authors":     len(get_unique_authors(books)),
        "unique_categories":  len(get_unique_categories(books)),
        "top_books":          get_top_n_books(books, 3),
        "authors_set":        get_unique_authors(books),
    }


# ══════════════════════════════════════════════════════════════
# ISSUE / RETURN SERVICES
# ══════════════════════════════════════════════════════════════

def issue_book(book_id: str, user_id: str) -> tuple[bool, str]:
    """
    Rules:
      1. Book must exist.
      2. At least one copy must be available.
      3. User must not already have this book issued.
    """
    book = db.get_book_by_id(book_id)
    if not book:
        return False, "Book not found. Check the Book ID."
    if book["available_copies"] < 1:
        return False, f"'{book['title']}' is fully issued. No copies available."
    if db.get_issue_record(book_id, user_id):
        return False, "You already have this book issued."

    issue_id  = gen_issue_id()
    issue_dt  = now_iso()
    due_dt    = due_iso(7)        # 7-day loan

    db.update_book_availability(book_id, delta=-1)
    db.insert_issued_book(issue_id, book_id, user_id, issue_dt, due_dt)

    _notify(user_id,
            f"📚 '{book['title']}' issued. Due: {due_dt[:10]}", "info")
    return True, f"'{book['title']}' issued! Due: {due_dt[:10]}"


def return_book(book_id: str, user_id: str) -> tuple[bool, str, float]:
    """
    Rules:
      1. Active issue record must exist for (book_id, user_id).
      2. Calculate fine = days_late × ₹5.
      3. Record reading history, delete issue, restore copy, save fine.
    """
    issue = db.get_issue_record(book_id, user_id)
    if not issue:
        return False, "No active loan found for this book under your account.", 0.0

    due_dt   = datetime.fromisoformat(issue["due_date"])
    days_late = max(0, (datetime.now() - due_dt).days)
    fine      = days_late * 5.0

    # record history before deleting issue
    book = db.get_book_by_id(book_id)
    issued_dt = datetime.fromisoformat(issue["issue_date"])
    days_kept = max(1, (datetime.now() - issued_dt).days)
    db.insert_reading_history(
        gen_hist_id(), user_id, book_id,
        book["title"], book["author"], book["category"],
        now_iso(), days_kept)

    db.delete_issue_record(issue["issue_id"])
    db.update_book_availability(book_id, delta=+1)

    if days_late > 0:
        db.insert_fine(gen_fine_id(), user_id, book_id,
                       issue["issue_id"], days_late, fine, now_iso())
        msg = (f"'{book['title']}' returned. "
               f"⚠️ {days_late} day(s) late — fine ₹{fine:.0f}")
        _notify(user_id, f"⚠️ {msg}", "warning")
    else:
        msg = f"'{book['title']}' returned on time! No fine."
        _notify(user_id, f"✅ {msg}", "success")

    return True, msg, fine


# ══════════════════════════════════════════════════════════════
# STUDENT HELPERS
# ══════════════════════════════════════════════════════════════

def student_issued_books(user_id: str) -> list:
    rows = db.get_issued_books_by_user(user_id)
    result = []
    for row in rows:
        item = dict(row)
        due = datetime.fromisoformat(item["due_date"])
        days_left = (due - datetime.now()).days
        item["days_left"]  = days_left
        item["is_overdue"] = days_left < 0
        item["fine"]       = abs(days_left) * 5 if days_left < 0 else 0
        result.append(item)
    return result


def student_fines(user_id: str) -> tuple[list, float]:
    rows  = db.get_fines_by_user(user_id)
    total = db.get_total_fine_by_user(user_id)
    return [dict(r) for r in rows], total


# ══════════════════════════════════════════════════════════════
# BOOK-REQUEST SERVICES
# ══════════════════════════════════════════════════════════════

def submit_request(user_id, user_name, book_title, author, reason) -> tuple[bool, str]:
    if not book_title.strip():
        return False, "Book title is required."
    rid = gen_request_id()
    db.insert_request(rid, user_id, user_name,
                      book_title.strip(), author.strip(), reason.strip(), now_iso())
    # notify all admins
    for u in db.get_all_users():
        if u["role"] == "admin":
            _notify(u["user_id"],
                    f"📬 New request from {user_name}: '{book_title}'", "info")
    return True, f"Request submitted! Admin will review '{book_title}'."


def respond_to_request(req_id, status, note, admin_name) -> tuple[bool, str]:
    all_r = db.get_all_requests()
    req   = next((dict(r) for r in all_r if r["request_id"] == req_id), None)
    if not req:
        return False, "Request not found."
    db.update_request_status(req_id, status, note, now_iso())
    icon = "✅" if status == "approved" else "❌"
    _notify(req["user_id"],
            f"{icon} Your request for '{req['book_title']}' was {status}. "
            f"{('Admin note: ' + note) if note else ''}",
            "success" if status == "approved" else "warning")
    return True, f"Request {status} and student notified."


# ══════════════════════════════════════════════════════════════
# WISHLIST SERVICES
# ══════════════════════════════════════════════════════════════

def toggle_wishlist(user_id, book_id) -> tuple[bool, str]:
    if db.is_in_wishlist(user_id, book_id):
        db.remove_from_wishlist(user_id, book_id)
        return True, "Removed from wishlist."
    db.add_to_wishlist(gen_wish_id(), user_id, book_id, now_iso())
    return True, "Added to wishlist ♥"


# ══════════════════════════════════════════════════════════════
# RATING / REVIEW SERVICES
# ══════════════════════════════════════════════════════════════

def rate_book(history_id, rating, review) -> tuple[bool, str]:
    if not (1 <= rating <= 5):
        return False, "Rating must be 1–5."
    db.update_rating_review(history_id, rating, review.strip())
    return True, "Rating saved! ⭐"


# ══════════════════════════════════════════════════════════════
# INTERNAL HELPER
# ══════════════════════════════════════════════════════════════

def _notify(user_id, message, ntype="info"):
    db.insert_notification(gen_notif_id(), user_id, message, ntype, now_iso())
