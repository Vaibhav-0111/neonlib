"""
seed.py — Run ONCE to populate library.db with sample data.
Usage:   python3 seed.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import initialize_database
import database as db
from utils import gen_book_id, gen_user_id, now_iso, hash_password, random_neon

initialize_database()

# ── sample books ──────────────────────────────────────────────
BOOKS = [
    ("Dune",                    "Frank Herbert",       "Sci-Fi",      3),
    ("Clean Code",              "Robert C. Martin",    "Programming", 2),
    ("The Great Gatsby",        "F. Scott Fitzgerald", "Classic",     4),
    ("Atomic Habits",           "James Clear",         "Self-Help",   5),
    ("1984",                    "George Orwell",       "Dystopian",   3),
    ("Python Crash Course",     "Eric Matthes",        "Programming", 2),
    ("Sapiens",                 "Yuval Noah Harari",   "History",     3),
    ("The Alchemist",           "Paulo Coelho",        "Fiction",     4),
    ("Neuromancer",             "William Gibson",      "Sci-Fi",      2),
    ("Deep Work",               "Cal Newport",         "Self-Help",   3),
    ("The Pragmatic Programmer","David Thomas",        "Programming", 2),
    ("Brave New World",         "Aldous Huxley",       "Dystopian",   3),
]

if db.count_books() == 0:
    for title, author, cat, copies in BOOKS:
        bid = gen_book_id()
        db.insert_book(bid, title, author, cat, copies, "ADMIN001", now_iso())
    print(f"  ✓ {len(BOOKS)} books inserted")
else:
    print(f"  · Books already seeded ({db.count_books()} exist)")

# ── sample students ───────────────────────────────────────────
STUDENTS = [
    ("Alice Kumar",   "alice@student.com"),
    ("Bob Singh",     "bob@student.com"),
    ("Zara Ahmed",    "zara@student.com"),
    ("Rahul Sharma",  "rahul@student.com"),
]

pw = hash_password("Student@123")
created = 0
for name, email in STUDENTS:
    if not db.get_user_by_email(email):
        db.insert_user(gen_user_id(), name, email, pw,
                       "student", now_iso(), random_neon())
        created += 1

if created:
    print(f"  ✓ {created} student accounts created  (password: Student@123)")
else:
    print("  · Students already seeded")

print("\nDone! Login: admin@library.com / Admin@123")
