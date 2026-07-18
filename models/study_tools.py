import json
from models.db import get_db

class StudyTools:
    # ----------------- Flashcards Operations -----------------
    @staticmethod
    def add_flashcard(document_id, front, back):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO study_flashcards (document_id, front, back) VALUES (?, ?, ?)",
                (document_id, front, back)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding flashcard: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_flashcards(document_id):
        db = get_db()
        rows = db.execute(
            "SELECT * FROM study_flashcards WHERE document_id = ? ORDER BY id ASC",
            (document_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ----------------- Quizzes Operations -----------------
    @staticmethod
    def add_quiz_question(document_id, question, options, correct_option, explanation=""):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                """INSERT INTO study_quizzes (document_id, question, options_json, correct_option, explanation) 
                   VALUES (?, ?, ?, ?, ?)""",
                (document_id, question, json.dumps(options), correct_option, explanation)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding quiz question: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_quizzes(document_id):
        db = get_db()
        rows = db.execute(
            "SELECT * FROM study_quizzes WHERE document_id = ? ORDER BY id ASC",
            (document_id,)
        ).fetchall()
        
        quizzes = []
        for r in rows:
            q = dict(r)
            try:
                q['options'] = json.loads(q['options_json']) if q['options_json'] else []
            except Exception:
                q['options'] = []
            quizzes.append(q)
        return quizzes

    # ----------------- Quiz Attempts Logs -----------------
    @staticmethod
    def log_attempt(user_id, document_id, score, total):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                """INSERT INTO quiz_attempts (user_id, document_id, score, total) 
                   VALUES (?, ?, ?, ?)""",
                (user_id, document_id, score, total)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error logging quiz attempt: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_attempts(user_id, document_id=None):
        db = get_db()
        if document_id:
            rows = db.execute(
                """SELECT a.*, d.filename FROM quiz_attempts a 
                   JOIN documents d ON a.document_id = d.id 
                   WHERE a.user_id = ? AND a.document_id = ? 
                   ORDER BY a.attempted_at DESC""",
                (user_id, document_id)
            ).fetchall()
        else:
            rows = db.execute(
                """SELECT a.*, d.filename FROM quiz_attempts a 
                   JOIN documents d ON a.document_id = d.id 
                   WHERE a.user_id = ? 
                   ORDER BY a.attempted_at DESC""",
                (user_id,)
            ).fetchall()
        return [dict(r) for r in rows]
