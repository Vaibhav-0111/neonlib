"""
utils.py
Layer : Utility Layer (pure functions, no side-effects)
Rule  : No DB calls.  No Streamlit imports.
        All DSA algorithms, hashing, ID generators, date helpers live here.
"""

import hashlib
import uuid
import random
from datetime import datetime, timedelta


# ══════════════════════════════════════════════════════════════
# DATA STRUCTURE 1 – LIST  (linear search + sorting)
# ══════════════════════════════════════════════════════════════

def linear_search_books(books: list, query: str) -> list:
    """
    Linear Search across title / author / category fields.
    Time Complexity : O(n)  – one pass through the list.
    Why List?       : ordered, iterable, cheap append.
    """
    if not query or not query.strip():
        return books
    q = query.strip().lower()
    return [b for b in books
            if q in b["title"].lower()
            or q in b["author"].lower()
            or q in b["category"].lower()]


def linear_search_users(users: list, query: str) -> list:
    """O(n) linear search over name + email fields."""
    if not query or not query.strip():
        return users
    q = query.strip().lower()
    return [u for u in users
            if q in u["name"].lower() or q in u["email"].lower()]


def sort_books_by_borrow_count(books: list, desc: bool = True) -> list:
    """
    Python's built-in sorted() uses Timsort → O(n log n).
    Returns a NEW list; original is unchanged.
    """
    return sorted(books, key=lambda b: b.get("borrow_count", 0), reverse=desc)


def get_top_n_books(books: list, n: int = 3) -> list:
    """Sort then slice – O(n log n) + O(1)."""
    return sort_books_by_borrow_count(books)[:n]


# ══════════════════════════════════════════════════════════════
# DATA STRUCTURE 2 – SET  (unique authors / categories)
# ══════════════════════════════════════════════════════════════

def get_unique_authors(books: list) -> set:
    """
    Set comprehension → O(n) to build, O(1) membership check.
    Auto-deduplicates: 'Frank Herbert' appears once even with 10 books.
    """
    return {b["author"] for b in books}


def get_unique_categories(books: list) -> set:
    return {b["category"] for b in books}


# ══════════════════════════════════════════════════════════════
# DATA STRUCTURE 3 – DICTIONARY  (issued_books O(1) lookup)
# ══════════════════════════════════════════════════════════════

def build_issued_dict(issued_rows: list) -> dict:
    """
    Converts a list of issued-book rows into a dict keyed by book_id.
    Build cost: O(n).  Lookup cost: O(1).
    Use case: 'Is BK-XXXX currently out?' → instant answer.
    """
    d = {}
    for row in issued_rows:
        d[row["book_id"]] = {
            "user_id":    row["user_id"],
            "issue_id":   row["issue_id"],
            "issue_date": row["issue_date"],
            "due_date":   row["due_date"],
        }
    return d


# ══════════════════════════════════════════════════════════════
# PASSWORD UTILITIES
# ══════════════════════════════════════════════════════════════

def hash_password(plain: str) -> str:
    """SHA-256 one-way hash.  O(k) where k = password length."""
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


def verify_password(plain: str, stored_hash: str) -> bool:
    """Re-hash input, compare digests.  Never compares plaintext."""
    return hash_password(plain) == stored_hash


def validate_password(pw: str) -> tuple[bool, str]:
    """
    Returns (is_valid, message).
    Rules: 8+ chars, 1 uppercase, 1 digit, 1 special char.
    """
    if len(pw) < 8:
        return False, "Minimum 8 characters required."
    if not any(c.isupper() for c in pw):
        return False, "Must contain at least one uppercase letter."
    if not any(c.isdigit() for c in pw):
        return False, "Must contain at least one number."
    if not any(c in "@#$%^&*!_-" for c in pw):
        return False, "Must contain at least one special character (@#$%^&*!_-)."
    return True, "Strong password ✓"


def pw_score(pw: str) -> int:
    """Returns 0-4 strength score used by the UI strength bar."""
    score = 0
    if len(pw) >= 8:                              score += 1
    if any(c.isupper() for c in pw):             score += 1
    if any(c.isdigit() for c in pw):             score += 1
    if any(c in "@#$%^&*!_-" for c in pw):      score += 1
    return score


# ══════════════════════════════════════════════════════════════
# ID GENERATORS
# ══════════════════════════════════════════════════════════════

def gen_user_id()    -> str: return f"USR-{uuid.uuid4().hex[:6].upper()}"
def gen_book_id()    -> str: return f"BK-{uuid.uuid4().hex[:6].upper()}"
def gen_issue_id()   -> str: return f"ISS-{uuid.uuid4().hex[:8].upper()}"
def gen_fine_id()    -> str: return f"FIN-{uuid.uuid4().hex[:8].upper()}"
def gen_request_id() -> str: return f"REQ-{uuid.uuid4().hex[:8].upper()}"
def gen_notif_id()   -> str: return f"NTF-{uuid.uuid4().hex[:8].upper()}"
def gen_hist_id()    -> str: return f"HST-{uuid.uuid4().hex[:8].upper()}"
def gen_wish_id()    -> str: return f"WSH-{uuid.uuid4().hex[:8].upper()}"


# ══════════════════════════════════════════════════════════════
# DATE HELPERS
# ══════════════════════════════════════════════════════════════

def now_iso() -> str:
    return datetime.now().isoformat()

def due_iso(days: int = 7) -> str:
    return (datetime.now() + timedelta(days=days)).isoformat()

def fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%d %b %Y")
    except Exception:
        return iso

def days_until_due(due_iso: str) -> int:
    """Positive = days remaining.  Negative = days overdue."""
    try:
        return (datetime.fromisoformat(due_iso) - datetime.now()).days
    except Exception:
        return 0


# ══════════════════════════════════════════════════════════════
# AVATAR COLOR
# ══════════════════════════════════════════════════════════════

_NEON = ["#00f5ff","#ff00ff","#00ff88","#ff6b35","#7b2fff","#ff2d55","#ffd700","#00bfff"]

def random_neon() -> str:
    return random.choice(_NEON)
