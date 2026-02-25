"""
auth.py
Layer : Service Layer — Authentication Subsystem
Rule  : May call database.py and utils.py.
        May call streamlit ONLY for session_state helpers.
        No business logic about books or fines.
"""

import streamlit as st
import database as db
from models import User
from utils import (
    hash_password, verify_password, validate_password,
    gen_user_id, random_neon, now_iso,
)


# ══════════════════════════════════════════════════════════════
# REGISTRATION
# ══════════════════════════════════════════════════════════════

def register_user(name: str, email: str, password: str, role: str) -> tuple[bool, str]:
    """
    Flow:
      1. Validate name / email format
      2. Validate password strength (utils.py)
      3. Hash password (SHA-256)
      4. Generate unique user_id + avatar colour
      5. Persist to DB via database.insert_user()
      6. Return (True, success_msg) or (False, error_msg)
    """
    if not name.strip():
        return False, "Name cannot be empty."
    if not email.strip() or "@" not in email or "." not in email:
        return False, "Enter a valid email address."

    ok, msg = validate_password(password)
    if not ok:
        return False, msg

    uid   = gen_user_id()
    color = random_neon()
    pw_h  = hash_password(password)

    saved = db.insert_user(uid, name.strip(), email.strip().lower(),
                           pw_h, role, now_iso(), color)
    if not saved:
        return False, "An account with this email already exists."
    return True, f"Account created! Your ID: {uid}"


# ══════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════

def login_user(email: str, password: str) -> tuple[bool, str, dict | None]:
    """
    Flow:
      1. Fetch user row by email from DB
      2. Verify password hash (utils.py)
      3. Build User object → stripped session dict (no password)
      4. Return (True, welcome_msg, session_dict) or (False, error, None)
    """
    if not email.strip() or not password:
        return False, "Email and password are required.", None

    row = db.get_user_by_email(email.strip().lower())
    if not row:
        return False, "No account found with this email.", None

    if not verify_password(password, row["password"]):
        return False, "Incorrect password.", None

    user = User.from_row(row)
    return True, f"Welcome back, {user.name}!", user.to_session_dict()


# ══════════════════════════════════════════════════════════════
# SESSION STATE  (DATA STRUCTURE: Dictionary — O(1) read/write)
# st.session_state behaves exactly like a Python dict.
# It persists across Streamlit reruns within the same browser tab.
# ══════════════════════════════════════════════════════════════

def save_session(user_dict: dict) -> None:
    st.session_state["user"]       = user_dict   # O(1) write
    st.session_state["logged_in"]  = True

def logout_user() -> None:
    for k in list(st.session_state.keys()):
        del st.session_state[k]

def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)

def current_user() -> dict | None:
    return st.session_state.get("user", None)      # O(1) read


# ══════════════════════════════════════════════════════════════
# ACCESS GUARDS  (called at top of protected page functions)
# ══════════════════════════════════════════════════════════════

def require_login() -> None:
    if not is_logged_in():
        st.error("🔒 Please login to access this page.")
        st.stop()

def require_admin() -> None:
    u = current_user()
    if not u or u.get("role") != "admin":
        st.error("⛔ Admin access required.")
        st.stop()
