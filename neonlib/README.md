# 📚 NeonLib — Library Management System v3.0

A full-featured library system built with Python + Streamlit + SQLite.
Cyberpunk neon dark theme **and** clean light theme — toggle anytime.

---

## ▶️ Quick Start

```bash
# 1. Install dependency
pip install streamlit

# 2. Seed sample data (run once)
python3 seed.py

# 3. Launch
streamlit run app.py
```

Open **http://localhost:8501**

---

## 🔑 Default Accounts

| Role    | Email                  | Password     |
|---------|------------------------|--------------|
| Admin   | admin@library.com      | Admin@123    |
| Student | alice@student.com      | Student@123  |
| Student | bob@student.com        | Student@123  |
| Student | zara@student.com       | Student@123  |
| Student | rahul@student.com      | Student@123  |

---

## 🗂 Project Structure

```
neonlib/
├── app.py          ← Streamlit UI only. Zero business logic.
├── auth.py         ← Login, Register, Session management
├── services.py     ← ALL business rules (issue, return, fines, requests…)
├── utils.py        ← Pure algorithms (search, sort, hash, ID generators)
├── models.py       ← Data shapes: User, Book, IssuedBook dataclasses
├── database.py     ← ONLY file that touches SQLite
├── seed.py         ← One-time sample data loader
├── library.db      ← Auto-created SQLite database
└── README.md
```

### Layer Rules (strict)
```
app.py  →  auth.py  →  database.py
app.py  →  services.py  →  database.py  +  utils.py
app.py  →  database.py  (read-only helpers like counts)
NEVER: app.py touches sqlite3 directly
NEVER: services.py imports streamlit
```

---

## 📊 Database Schema (6 Tables)

| Table            | Purpose                              |
|------------------|--------------------------------------|
| users            | Accounts, hashed passwords, roles    |
| books            | Inventory, copy counts, borrow stats |
| issued_books     | Active loans                         |
| fines            | Penalty records                      |
| book_requests    | Student → Admin requests             |
| notifications    | In-app activity feed                 |
| reading_history  | Returned books + star ratings        |
| wishlist         | Per-user saved books                 |

---

## ✨ Features

### 🌓 Theme
- Toggle **Dark** (neon cyberpunk) or **Light** (clean indigo) from sidebar
- Every colour, font, shadow, glow switches instantly

### 🔐 Auth
- Registration with live password strength meter (4-rule checker)
- SHA-256 hashed passwords — never stored in plaintext
- Role-based access: Admin vs Student
- Session via `st.session_state` (Dictionary O(1) read/write)

### 📚 Books
- Browse catalog with sort (Most Borrowed, A–Z, Available First)
- Linear search O(n) across title + author + category
- Add / Delete books (Admin only)
- Availability dot indicator (green / red)
- Star rating shown on each card

### 🔄 Issue / Return
- 7-day loan period
- Fine = ₹5 per day overdue
- Auto-recorded in reading history on return
- Admin can issue/return for any student

### 📬 Book Requests
- Students request books not in catalog
- Admin sees pending count badge (🔴) in sidebar
- Approve ✅ or Reject ❌ with custom note
- Student notified automatically

### 🔔 Notifications
- Auto-sent on: issue, return, fine, request response
- Unread badge in sidebar
- Mark all as read

### ♥ Wishlist
- Toggle from any book card
- Shows availability status

### 📖 Reading History + ⭐ Ratings
- Auto-recorded every time a book is returned
- Rate 1–5 stars, write a review
- Community average shown on book cards
- Personal stats: total read, days, avg rating, fav genre

### 👤 Profile
- Avatar with random neon colour
- Active loans, fine total, books read, wishlist count
- Fine history with paid/unpaid status

### 👥 All Users (Admin)
- Search users by name/email
- See each user's loans, books read, fine total

---

## 🧠 Data Structures & Algorithms

| Operation            | DS Used    | Algorithm      | Complexity  |
|----------------------|-----------|----------------|-------------|
| Book search          | List       | Linear Search  | O(n)        |
| Issued book lookup   | Dictionary | Hash get       | O(1)        |
| Unique authors       | Set        | Set comprehension | O(n)     |
| Top borrowed books   | List       | Timsort        | O(n log n)  |
| Password hashing     | —          | SHA-256        | O(k) fixed  |
| Session read/write   | Dictionary | Key lookup     | O(1)        |
| DB queries           | —          | SQLite B-tree  | O(log n)    |
