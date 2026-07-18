from werkzeug.security import generate_password_hash, check_password_hash
from models.db import get_db

class User:
    @staticmethod
    def create(username, email, password):
        db = get_db()
        cursor = db.cursor()
        password_hash = generate_password_hash(password)
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            db.commit()
            user_id = cursor.lastrowid
            
            # Create default settings for the user
            cursor.execute(
                "INSERT INTO user_settings (user_id, api_provider, api_key, theme) VALUES (?, 'local', '', 'dark')",
                (user_id,)
            )
            db.commit()
            return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return row

    @staticmethod
    def get_by_username(username):
        db = get_db()
        row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return row

    @staticmethod
    def authenticate(username_or_email, password):
        db = get_db()
        row = db.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username_or_email, username_or_email)
        ).fetchone()
        if row and check_password_hash(row['password_hash'], password):
            return row
        return None

    @staticmethod
    def get_settings(user_id):
        db = get_db()
        row = db.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,)).fetchone()
        if not row:
            # Create default if missing
            db.execute(
                "INSERT OR IGNORE INTO user_settings (user_id, api_provider, api_key, theme) VALUES (?, 'local', '', 'dark')",
                (user_id,)
            )
            db.commit()
            row = db.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def update_settings(user_id, api_provider, api_key, theme):
        db = get_db()
        db.execute(
            """UPDATE user_settings 
               SET api_provider = ?, api_key = ?, theme = ? 
               WHERE user_id = ?""",
            (api_provider, api_key, theme, user_id)
        )
        db.commit()
        return True
