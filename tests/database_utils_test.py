import pytest
import sqlite3
import sys
import os
import bcrypt
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
)
import backend.database_tables as dbtables
import backend.database_utils as dbutils


try:
    os.remove("temp/test_db_utils.db")
except FileNotFoundError:
    pass


class TestDatabaseUtils:
    db_conn = sqlite3.connect("temp/test_db_utils.db")
    db_cur = db_conn.cursor()
    db_cur.execute("PRAGMA foreign_keys = ON;")
    db_conn.commit()

    dbtables.createUserPrivilegesTable(db_cur)
    dbtables.createUserTable(db_cur)
    dbtables.createFileTable(db_cur)
    dbtables.createDownloadHistoryTable(db_cur)

    def test_initUserPrivileges_one(self):
        dbutils.initUserPrivileges(self.db_conn)
        test = self.db_cur.execute("""
            SELECT Type
            FROM UserPrivileges
            WHERE Number = 1
        """).fetchone()
        assert test[0] == "Admin"

    def test_initUserPrivileges_two(self):
        dbutils.initUserPrivileges(self.db_conn)
        test = self.db_cur.execute("""
            SELECT Number
            FROM UserPrivileges
            WHERE Type = "Viewer"
        """).fetchone()
        assert test[0] == 3

    def test_initUserPrivileges_three(self):
        dbutils.initUserPrivileges(self.db_conn)
        test = self.db_cur.execute("""
            SELECT Type
            FROM UserPrivileges
            WHERE Number = 2
        """).fetchone()
        assert test[0] == "Uploader"

    def test_createTestUsers_one(self):
        dbutils.createTestUsers(self.db_conn)
        test = self.db_cur.execute("""
            SELECT Username
            FROM Users
        """).fetchone()
        assert test[0] == "root"

    def test_createTestUsers_two(self):
        test = self.db_cur.execute("""
            SELECT PassHash
            FROM Users
        """).fetchone()
        assert bcrypt.checkpw("root".encode("UTF-8"), test[0].encode("UTF-8"))

    def test_initFiles_one(self):
        dbutils.initFiles(self.db_conn, "temp/images/")
        test = self.db_cur.execute("""
            SELECT FileName
            FROM Files
        """).fetchall()
        test = [x[0] for x in test]
        assert "earth.jpg" in test
        assert "linux.png" in test
        assert "statue.png" in test

    def test_createAnonUser_one(self):
        dbutils.createAnonUser(self.db_conn)
        test = self.db_cur.execute("""
            SELECT Username
            FROM Users
            WHERE ID = -1
        """).fetchone()
        assert test[0] == "Anonymous"

    def test_createAnonUser_two(self):
        dbutils.createAnonUser(self.db_conn)
        test = self.db_cur.execute("""
            SELECT Privilege
            FROM Users
            WHERE ID = -1
        """).fetchone()
        assert test[0] == 3
