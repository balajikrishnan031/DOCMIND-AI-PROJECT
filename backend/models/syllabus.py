from models.db import get_db

class Syllabus:
    @staticmethod
    def add_unit(user_id, unit_title, unit_index):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO syllabus_units (user_id, unit_title, unit_index) VALUES (?, ?, ?)",
                (user_id, unit_title, unit_index)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding syllabus unit: {e}")
            db.rollback()
            return None

    @staticmethod
    def add_topic(unit_id, topic_name):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO syllabus_topics (unit_id, topic_name, status) VALUES (?, ?, 'pending')",
                (unit_id, topic_name)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding syllabus topic: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_user_syllabus(user_id):
        db = get_db()
        # Fetch units
        units_rows = db.execute(
            "SELECT * FROM syllabus_units WHERE user_id = ? ORDER BY unit_index ASC",
            (user_id,)
        ).fetchall()
        
        syllabus_structure = []
        for u_row in units_rows:
            unit = dict(u_row)
            # Fetch topics for this unit
            topics_rows = db.execute(
                """SELECT t.*, d.filename FROM syllabus_topics t 
                   LEFT JOIN documents d ON t.document_id = d.id 
                   WHERE t.unit_id = ? ORDER BY t.id ASC""",
                (unit['id'],)
            ).fetchall()
            
            unit['topics'] = [dict(t) for t in topics_rows]
            syllabus_structure.append(unit)
            
        return syllabus_structure

    @staticmethod
    def map_topic_to_doc(topic_id, doc_id, page_number):
        db = get_db()
        try:
            db.execute(
                """UPDATE syllabus_topics 
                   SET document_id = ?, page_number = ?, status = 'covered' 
                   WHERE id = ?""",
                (doc_id, page_number, topic_id)
            )
            db.commit()
            return True
        except Exception as e:
            print(f"Error mapping syllabus topic: {e}")
            db.rollback()
            return False

    @staticmethod
    def clear_syllabus(user_id):
        db = get_db()
        try:
            db.execute("DELETE FROM syllabus_units WHERE user_id = ?", (user_id,))
            db.commit()
            return True
        except Exception as e:
            print(f"Error clearing syllabus: {e}")
            db.rollback()
            return False
