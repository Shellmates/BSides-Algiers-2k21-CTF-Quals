import sqlite3
import os
import time

class ImageHandler:
    def __init__(self, db_dir):
        self.db = os.path.join(db_dir, "db.sqlite3")
        self.column_names = [
            "path",
            "title",
            "created_at"
        ]

        self.init_db()

    def execute_query(self, query, params=()):
        conn = sqlite3.connect(self.db)
        curs = conn.cursor()
        curs.execute(query, params)
        result = curs.fetchall()
        conn.commit()
        conn.close()

        return result

    def init_db(self):
        if not os.path.exists(self.db):
            self.execute_query(
                """
                CREATE TABLE images (
                        {} TEXT PRIMARY KEY,
                        {} TEXT,
                        {} DATE
                    )
                """.format(
                    *self.column_names
                )
            )

    def exists(self, path):
        result = self.execute_query("SELECT 1 FROM images WHERE path = ?", (path,))
        return len(result) != 0

    def add(self, path, title):
        if not self.exists(path):
            t = int(time.time())
            self.execute_query("INSERT INTO images(path, title, created_at) VALUES(?, ?, ?)", (path, title, t))
            return True
        else:
            return False

    def update(self, path, title):
        if self.exists(path):
            self.execute_query("UPDATE images SET title = ? WHERE path = ?", (title, path))
            return True
        else:
            return False

    def delete(self, path):
        if self.exists(path):
            self.execute_query("DELETE FROM images WHERE path = ?", (path,))
            return True
        else:
            return False

    def get(self, path):
        rows = self.execute_query("SELECT title, created_at FROM images WHERE path = ?", (path,))
        if len(rows) != 0:
            return {
                "path": path,
                "title": rows[0][0],
                "created_at": rows[0][1]
            }
        else:
            return None

    def getall(self):
        rows = self.execute_query("SELECT path, title, created_at FROM images")
        return [ {
            "path": row[0],
            "title": row[1],
            "created_at": row[2]
        } for row in rows ]
