"""`db_handler` module handles database interactions
"""

import sqlite3
from sqlite3 import Error
from os import path
import time
import sys

#
# Constants
#

DB_NAME = "data.db"
LOG_FILE = "db-error-log.txt"
SQL_CREATE_USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS users (
        uid TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        masterpass TEXT NOT NULL )
"""
SQL_CREATE_ENTRIES_TABLE = """
    CREATE TABLE IF NOT EXISTS entries (
        uid TEXT,
        url TEXT NOT NULL,
        username TEXT,
        password TEXT,
        FOREIGN KEY (uid)
        REFERENCES users (uid)
            ON DELETE CASCADE )
"""

#
# Init functions definition
#

__CONN__ = None

def __init__():
    global __CONN__
    if not path.exists(DB_NAME):
        __CONN__ = __create_connection__(DB_NAME)
        __create_table__(SQL_CREATE_USERS_TABLE)
        __create_table__(SQL_CREATE_ENTRIES_TABLE)
    else:
        __CONN__ = __create_connection__(DB_NAME)

def __create_connection__(db_file):
    """Create a database connection to a SQLite3 database specified by db_file

    Creates the database if it doesn't already exist

    Args:
        db_file(str): database file

    Returns:
        conn: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        __log_errors__(str(e), LOG_FILE)

    return conn

def __create_table__(create_table_sql):
    """Create a table from the create_table_sql statement

    Args:
        create_table_sql(str): a CREATE TABLE statement
    """
    try:
        cur = __CONN__.cursor()
        cur.execute(create_table_sql)
    except Error as e:
        __log_errors__(str(e), LOG_FILE)

def __log_errors__(err_msg, log_file=None):
    """Log err_msg to log_file, or to stderr if log_file is None

    Args:
        err_msg(str): error message
        log_file(str): log file or None
    """
    t = time.time()
    output = f"{time.ctime(t)} : {err_msg}"

    if log_file is None:
        print(output, file=sys.stderr)
    else:
        with open(log_file, 'a') as f:
            f.write(f"{time.ctime(t)} : {err_msg}\n")
            f.close()
#
# Handler classes definition
#

class HandlerException(Exception):
    """Base class for database handlers exceptions.
    """
    pass

class UserHandler:
    """UserHandler class handles database interactions with users table
    
    users table columns:
        - uid: user discord id (primary key)
        - name: user discord name
        - masterpass: master password (hashed)

    Note: Master password should be already hashed when passed to the handlers
    """
    @staticmethod
    def add(uid: int, name: str, masterpass: str) -> bool:
        """Add a new user account

        Args:
            uid(int): user discord id
            name(str): user discord name
            masterpass(str): master password (hashed)

        Returns:
            success(bool): returns False if uid already exists, True otherwise
        """
        with __CONN__:
            cur = __CONN__.cursor()

            # check that uid doesn't already exist
            sql = """
                SELECT 1 FROM users
                WHERE uid = ?
            """
            cur.execute(sql, (uid,))
            if cur.fetchone() is not None:
                return False

            sql = """
                INSERT INTO users(uid, name, masterpass)
                VALUES(?, ?, ?)
            """
            cur.execute(sql, (uid, name, masterpass))
            __CONN__.commit()

            return True

    @staticmethod
    def update(uid: int, name: str, masterpass: str) -> bool:
        """Update a user account

        Args:
            uid(int): user discord id
            name(str): user discord name
            masterpass(str): master password (hashed)

        Returns:
            success(bool): returns False if uid doesn't exist, True otherwise
        """
        with __CONN__:
            cur = __CONN__.cursor()

            # check that uid exists
            sql = """
                SELECT 1 FROM users
                WHERE uid = ?
            """
            cur.execute(sql, (uid,))
            if cur.fetchone() is None:
                return False

            sql = """
                UPDATE users
                SET name = ?,
                    masterpass = ?
                WHERE uid = ?
            """
            cur.execute(sql, (name, masterpass, uid))
            __CONN__.commit()

            return True

    @staticmethod
    def delete(uid: int) -> bool:
        """Delete a user account alongside the entries relative to it

        Args:
            uid(int): user discord id

        Returns:
            success(bool): returns False if uid doesn't exist, True otherwise
        """
        with __CONN__:
            cur = __CONN__.cursor()

            # check that uid exists
            sql = """
                SELECT 1 FROM users
                WHERE uid = ?
            """
            cur.execute(sql, (uid,))
            if cur.fetchone() is None:
                return False

            sql = """
                DELETE FROM users
                WHERE uid = ?
            """
            cur.execute(sql, (uid,))
            __CONN__.commit()

            return True

    @staticmethod
    def get(uid: int) -> dict:
        """Get user account info using uid

        Args:
            uid(int): user discord id

        Returns:
            user(dict): returns user account info as a dict {uid, name, masterpass} if uid exists, None otherwise
        """
        with __CONN__:
            cur = __CONN__.cursor()
            sql = """
                SELECT name, masterpass FROM users
                WHERE uid = ?
            """
            cur.execute(sql, (uid,))

            row = cur.fetchone()
            if row is None:
                return None

            return {
                'name': row[0],
                'masterpass': row[1]
            }

class EntryHandler:
    """EntryHandler class handles database interactions with entries table
    
    entries table columns:
        - uid: user discord id (foreign key)
        - url: website url
        - username: account username for url (encrypted)
        - password: account password for url (encrypted)

    Account username and password should be already encrypted using the masterpass when passed to the handlers
    """
    @staticmethod
    def add(uid: int, url: str, username: str, password: str) -> bool:
        """Add a new entry

        Args:
            uid(int): user discord id
            url(str): website url
            username(str): account username for url (encrypted)
            password(str): account password for url (encrypted)

        Note: username and password are truncated to 255 characters

        Returns:
            success(bool): returns False if uid doesn't exist or url already exists, True otherwise
        """
        with __CONN__:
            cur = __CONN__.cursor()

            # check that uid exists
            sql = """
                SELECT 1 FROM users
                WHERE uid = ?
            """
            cur.execute(sql, (uid,))
            if cur.fetchone() is None:
                return False

            # check that url doesn't exist
            sql = """
                SELECT 1 FROM entries
                WHERE uid = ? AND url = ?
            """
            cur.execute(sql, (uid, url))
            if cur.fetchone() is not None:
                return False

            sql = """
                INSERT INTO entries(uid, url, username, password)
                VALUES(?, ?, SUBSTR(?, 1, 255), SUBSTR(?, 1, 255))
            """
            cur.execute(sql, (uid, url, username, password))
            __CONN__.commit()

            return True

    @staticmethod
    def update(uid: int, url: str, username: str, password: str) -> bool:
        """Update an entry

        Args:
            uid(int): user discord id
            url(str): website url
            username(str): account username for url (encrypted)
            password(str): account password for url (encrypted)

        Note: username and password are truncated to 255 characters

        Returns:
            success(bool): returns False if uid doesn't exist or url doesn't exist, True otherwise
        """
        with __CONN__:
            cur = __CONN__.cursor()

            # check that uid exists
            sql = """
                SELECT 1 FROM users
                WHERE uid = ?
            """
            cur.execute(sql, (uid,))
            if cur.fetchone() is None:
                return False

            # check that url exists
            sql = """
                SELECT 1 FROM entries
                WHERE uid = ? AND url = ?
            """
            cur.execute(sql, (uid, url))
            if cur.fetchone() is None:
                return False

            sql = """
                UPDATE entries
                SET username = SUBSTR(?, 1, 255),
                    password = SUBSTR(?, 1, 255)
                WHERE uid = ? AND url = ?
            """
            cur.execute(sql, (username, password, uid, url))
            __CONN__.commit()

            return True

    @staticmethod
    def delete(uid: int, url: str) -> bool:
        """Delete an entry

        Args:
            uid(int): user discord id
            url(str): website url

        Returns:
            success(bool): returns False if uid doesn't exist or url doesn't exist, True otherwise
        """
        with __CONN__:
            cur = __CONN__.cursor()

            # check that uid exists
            sql = """
                SELECT 1 FROM users
                WHERE uid = ?
            """
            cur.execute(sql, (uid,))
            if cur.fetchone() is None:
                return False

            # check that url exists
            sql = """
                SELECT 1 FROM entries
                WHERE uid = ? AND url = ?
            """
            cur.execute(sql, (uid, url))
            if cur.fetchone() is None:
                return False

            sql = """
                DELETE FROM entries
                WHERE uid = ? AND url = ?
            """
            cur.execute(sql, (uid, url))
            __CONN__.commit()

            return True

    @staticmethod
    def get(uid: int, url: str) -> dict:
        """Get an entry using uid and url

        Args:
            uid(int): user discord id
            url(str): website url

        Returns:
            entry(dict): returns entry as a dict {uid, url, username, password} if uid and url exist, None otherwise
        """
        with __CONN__:
            cur = __CONN__.cursor()
            sql = """
                SELECT username, password FROM entries
                WHERE uid = ? AND url = ?
            """
            cur.execute(sql, (uid, url))

            row = cur.fetchone()
            if row is None:
                return None

            return {
                'username': row[0],
                'password': row[1]
            }

    @staticmethod
    def getall(uid: int) -> list:
        """Get all entries using uid

        Args:
            uid(int): user discord id

        Returns:
            entries(list of dict): returns the list of entries if uid exists, None otherwise
        """
        with __CONN__:
            cur = __CONN__.cursor()

            # check that uid exists
            sql = """
                SELECT 1 FROM users
                WHERE uid = ?
            """
            cur.execute(sql, (uid,))
            if cur.fetchone() is None:
                return None

            sql = """
                SELECT url, username, password FROM entries
                WHERE uid = ?
            """
            cur.execute(sql, (uid,))

            rows = cur.fetchall()

            return [ {
                'url': row[0],
                'username': row[1],
                'password': row[2]
            } for row in rows ]

#
# initialization
#

__init__()
if __CONN__ is None:
    raise HandlerException("Database connection could not be initialized!")
