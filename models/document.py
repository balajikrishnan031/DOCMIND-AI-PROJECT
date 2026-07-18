import json
from models.db import get_db

class Document:
    @staticmethod
    def create(user_id, filename, file_path, file_size, file_type):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                """INSERT INTO documents (user_id, filename, file_path, file_size, file_type, status) 
                   VALUES (?, ?, ?, ?, ?, 'processing')""",
                (user_id, filename, file_path, file_size, file_type)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating document: {e}")
            db.rollback()
            return None

    @staticmethod
    def update_status(doc_id, status):
        db = get_db()
        db.execute("UPDATE documents SET status = ? WHERE id = ?", (status, doc_id))
        db.commit()

    @staticmethod
    def get_by_id(doc_id):
        db = get_db()
        row = db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_by_user(user_id):
        db = get_db()
        rows = db.execute("SELECT * FROM documents WHERE user_id = ? ORDER BY uploaded_at DESC", (user_id,)).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def delete(doc_id):
        db = get_db()
        try:
            # Foreign keys ON DELETE CASCADE will handle child tables (chunks, features)
            db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            db.commit()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            db.rollback()
            return False

    @staticmethod
    def add_chunks(doc_id, chunks):
        """
        chunks is a list of tuples: (chunk_index, page_number, content)
        """
        db = get_db()
        try:
            db.executemany(
                "INSERT INTO document_chunks (document_id, chunk_index, page_number, content) VALUES (?, ?, ?, ?)",
                [(doc_id, c[0], c[1], c[2]) for c in chunks]
            )
            db.commit()
            return True
        except Exception as e:
            print(f"Error adding chunks: {e}")
            db.rollback()
            return False

    @staticmethod
    def get_chunks(doc_id):
        db = get_db()
        rows = db.execute(
            "SELECT * FROM document_chunks WHERE document_id = ? ORDER BY chunk_index ASC", 
            (doc_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_all_user_chunks(user_id):
        db = get_db()
        rows = db.execute(
            """SELECT c.*, d.filename FROM document_chunks c 
               JOIN documents d ON c.document_id = d.id 
               WHERE d.user_id = ?""", 
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def save_features(doc_id, summary_short, summary_medium, summary_long, keywords, definitions, formulas, key_questions):
        db = get_db()
        try:
            db.execute(
                """INSERT OR REPLACE INTO document_features 
                   (document_id, summary_short, summary_medium, summary_long, keywords, definitions, formulas, key_questions) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    doc_id,
                    summary_short,
                    summary_medium,
                    summary_long,
                    json.dumps(keywords),
                    json.dumps(definitions),
                    json.dumps(formulas),
                    json.dumps(key_questions)
                )
            )
            db.commit()
            return True
        except Exception as e:
            print(f"Error saving features: {e}")
            db.rollback()
            return False

    @staticmethod
    def get_features(doc_id):
        db = get_db()
        row = db.execute("SELECT * FROM document_features WHERE document_id = ?", (doc_id,)).fetchone()
        if not row:
            return None
        
        data = dict(row)
        # Decode JSON fields
        for field in ['keywords', 'definitions', 'formulas', 'key_questions']:
            try:
                data[field] = json.loads(data[field]) if data[field] else []
            except Exception:
                data[field] = []
        return data
