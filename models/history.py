import json
from models.db import get_db

class QAHistory:
    @staticmethod
    def add(user_id, document_id, question, answer, sources):
        """
        sources: list of dicts [{"document_name": "...", "page": N, "snippet": "..."}]
        """
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                """INSERT INTO qa_history (user_id, document_id, question, answer, sources) 
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, document_id, question, answer, json.dumps(sources))
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding QA history: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_by_user(user_id, document_id=None):
        db = get_db()
        if document_id:
            rows = db.execute(
                """SELECT h.*, d.filename FROM qa_history h 
                   LEFT JOIN documents d ON h.document_id = d.id 
                   WHERE h.user_id = ? AND h.document_id = ? 
                   ORDER BY h.created_at DESC""",
                (user_id, document_id)
            ).fetchall()
        else:
            rows = db.execute(
                """SELECT h.*, d.filename FROM qa_history h 
                   LEFT JOIN documents d ON h.document_id = d.id 
                   WHERE h.user_id = ? 
                   ORDER BY h.created_at DESC""",
                (user_id,)
            ).fetchall()
            
        history_list = []
        for r in rows:
            d = dict(r)
            try:
                d['sources'] = json.loads(d['sources']) if d['sources'] else []
            except Exception:
                d['sources'] = []
            history_list.append(d)
        return history_list

    @staticmethod
    def clear(user_id):
        db = get_db()
        try:
            db.execute("DELETE FROM qa_history WHERE user_id = ?", (user_id,))
            db.commit()
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            db.rollback()
            return False
