import sqlite3
import shutil
import time
import os


class DBManager:
    def __init__(self, database):
        self.db = database
        self.column_names = ["id", "title", "text"]

        # set max db size to 100M
        self.max_size = 1024 * 1024 * 100

        self.init_db()

    def restore(self):
        shutil.copy(f"{self.db}.bak", self.db)

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
                CREATE TABLE pastes (
                        {} text,
                        {} text,
                        {} text
                    )
                """.format(
                    *self.column_names
                )
            )

    def paste_exists(self, paste_id):
        return self.execute_query("SELECT * FROM pastes WHERE id=?", (paste_id,)) != []

    def add_paste(self, paste_id, title, text):
        if os.path.getsize(self.db) > self.max_size:
            self.restore()

        self.execute_query(
            "INSERT INTO pastes VALUES(?, ?, ?)", (paste_id, title, text)
        )

    def get_paste(self, paste_id):
        result = self.execute_query("SELECT * FROM pastes WHERE id=?", (paste_id,))

        if result == []:
            return None

        return result[0]

    def get_paste_field(self, paste_id, field):
        result = self.execute_query(
            "SELECT {} FROM pastes WHERE id=?".format(field), (paste_id,)
        )

        if result == []:
            return None

        return result[0][0]

    def delete_paste(self, paste_id):
        self.execute_query("DELETE FROM pastes WHERE id=?", (paste_id,))
