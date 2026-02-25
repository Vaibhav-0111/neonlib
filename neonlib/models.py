"""
models.py
Layer : Domain Model Layer
Rule  : Pure Python dataclasses.  No DB calls.  No Streamlit.
        Defines the shape of every object the app passes around.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    user_id:      str
    name:         str
    email:        str
    password:     str          # SHA-256 hex digest – never plaintext
    role:         str          # "admin" | "student"
    created_at:   str
    avatar_color: str = "#00f5ff"

    def is_admin(self) -> bool:
        return self.role == "admin"

    def to_session_dict(self) -> dict:
        """Stripped dict safe to store in st.session_state (no password)."""
        return {
            "user_id":      self.user_id,
            "name":         self.name,
            "email":        self.email,
            "role":         self.role,
            "created_at":   self.created_at,
            "avatar_color": self.avatar_color,
        }

    @classmethod
    def from_row(cls, row) -> "User":
        return cls(
            user_id      = row["user_id"],
            name         = row["name"],
            email        = row["email"],
            password     = row["password"],
            role         = row["role"],
            created_at   = row["created_at"],
            avatar_color = row["avatar_color"] or "#00f5ff",
        )


@dataclass
class Book:
    book_id:          str
    title:            str
    author:           str
    category:         str
    total_copies:     int
    available_copies: int
    added_by:         str
    added_at:         str
    borrow_count:     int = 0

    def is_available(self) -> bool:
        return self.available_copies > 0

    @classmethod
    def from_row(cls, row) -> "Book":
        return cls(
            book_id          = row["book_id"],
            title            = row["title"],
            author           = row["author"],
            category         = row["category"],
            total_copies     = row["total_copies"],
            available_copies = row["available_copies"],
            added_by         = row["added_by"] or "",
            added_at         = row["added_at"],
            borrow_count     = row["borrow_count"] or 0,
        )


@dataclass
class IssuedBook:
    issue_id:     str
    book_id:      str
    user_id:      str
    issue_date:   str
    due_date:     str
    title:        str = ""
    author:       str = ""
    borrower_name: str = ""

    def days_overdue(self) -> int:
        due = datetime.fromisoformat(self.due_date)
        return max(0, (datetime.now() - due).days)

    def fine_amount(self) -> float:
        return self.days_overdue() * 5.0

    @classmethod
    def from_row(cls, row) -> "IssuedBook":
        keys = row.keys()
        return cls(
            issue_id      = row["issue_id"],
            book_id       = row["book_id"],
            user_id       = row["user_id"],
            issue_date    = row["issue_date"],
            due_date      = row["due_date"],
            title         = row["title"]         if "title"         in keys else "",
            author        = row["author"]        if "author"        in keys else "",
            borrower_name = row["borrower_name"] if "borrower_name" in keys else "",
        )
