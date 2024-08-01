import pytest
import sqlite3
import sys
import os
sys.path.insert(0, "..")

import backend.database_tables as dbtables

try:
    os.remove("temp/test_db.db")
except FileNotFoundError:
    pass


class TestDatabaseTables:
    db_conn = sqlite3.connect("temp/test_db.db")
    db_cur = db_conn.cursor()
    db_cur.execute("PRAGMA foreign_keys = ON;")
    db_conn.commit()

    def test_user_privileges_create(self):
        dbtables.createUserPrivilegesTable(self.db_cur)
        tables = self.db_cur.execute("""
            SELECT name FROM sqlite_master;
        """).fetchone()
        assert tables[0] == "UserPrivileges"

    def test_user_privileges_insert(self):
        self.db_cur.execute("""
            INSERT INTO UserPrivileges (Number, Type)
            VALUES (1, "Admin")
        """)
        self.db_conn.commit()
        test = self.db_cur.execute("""
            SELECT Type
            FROM UserPrivileges
            WHERE Number = 1
        """).fetchone()
        assert test[0] == "Admin"

    def test_users_create(self):
        dbtables.createUserTable(self.db_cur)
        tables = self.db_cur.execute("""
            SELECT name
            FROM sqlite_master
            WHERE name = "Users";
        """).fetchone()
        assert tables[0] == "Users"

    def test_users_insert_one(self):
        self.db_cur.execute("""
            INSERT INTO Users (Username, PassHash, Privilege)
            VALUES ("test_one", "wordpass", "1")
        """)
        self.db_conn.commit()
        test = self.db_cur.execute("""
            SELECT PassHash
            FROM Users
            WHERE Username = "test_one"
        """).fetchone()
        assert test[0] == "wordpass"

    def test_users_foreign_key(self):
        with pytest.raises(sqlite3.IntegrityError) as excinfo:
            self.db_cur.execute("""
                INSERT INTO Users (Username, PassHash, Privilege)
                VALUES ("test_two", "abc", "2")
            """)
            self.db_conn.commit()

        assert excinfo.type == sqlite3.IntegrityError

    def test_files_create(self):
        dbtables.createFileTable(self.db_cur)
        tables = self.db_cur.execute("""
            SELECT name
            FROM sqlite_master
            WHERE name = "Files";
        """).fetchone()
        assert tables[0] == "Files"

    def test_files_insert(self):
        self.db_cur.execute("""
            INSERT INTO Files (FileName, DownloadCount, UploadDate)
            VALUES ("testfile.txt", 0, DATETIME('now'))
        """)
        self.db_conn.commit()
        test = self.db_cur.execute("""
            SELECT DownloadCount
            FROM Files
            WHERE FileName = "testfile.txt"
        """).fetchone()
        assert test[0] == 0

    def test_download_history_create(self):
        dbtables.createDownloadHistoryTable(self.db_cur)
        tables = self.db_cur.execute("""
            SELECT name
            FROM sqlite_master
            WHERE name = "DownloadHistory";
        """).fetchone()
        assert tables[0] == "DownloadHistory"

    def test_download_history_insert(self):
        self.db_cur.execute("""
            INSERT INTO DownloadHistory (UserID, FileID)
            VALUES (1, 1)
        """)
        self.db_conn.commit()
        test = self.db_cur.execute("""
            SELECT UserID
            FROM DownloadHistory
            WHERE FileID = 1
        """).fetchone()
        assert test[0] == 1

    def test_download_history_foreign_key(self):
        with pytest.raises(sqlite3.IntegrityError) as excinfo:
            self.db_cur.execute("""
                INSERT INTO DownloadHistory (UserID, FileID)
                VALUES (3, 3)
            """)
            self.db_conn.commit()

        assert excinfo.type == sqlite3.IntegrityError
