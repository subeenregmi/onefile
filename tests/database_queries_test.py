import pytest
import sqlite3
import sys
import os
import bcrypt
sys.path.insert(0, "..")
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
)
import backend.database_queries as dbqueries
import backend.database_utils as dbutils


try:
    os.remove("temp/test_db_queries.db")
except FileNotFoundError:
    pass


class TestDatabaseQueries:
    db_conn = dbutils.setupDatabase("temp/test_db_queries.db", "temp/images")
    db_cur = db_conn.cursor()

    def test_getUserData_one(self):
        test = dbqueries.getUserData(self.db_conn)
        assert len(test) == 1

    def test_getUserData_two(self):
        test = dbqueries.getUserData(self.db_conn, "John")
        assert len(test) == 0

    def test_getUserData_three(self):
        test = dbqueries.getUserData(self.db_conn, "", "")
        assert len(test) == 1

    def test_getUserData_four(self):
        test = dbqueries.getUserData(self.db_conn, "", "", "Username")
        assert len(test) == 1

    def test_getUserData_five(self):
        with pytest.raises(sqlite3.OperationalError) as excinfo:
           dbqueries.getUserData(self.db_conn, "", "", "togo")

        assert excinfo.type == sqlite3.OperationalError

    def test_getUserData_six(self):
        test = dbqueries.getUserData(self.db_conn, "root", "", "Privilege",
                                     "Username")
        assert test[0]["Privilege"] == 1

    def test_getUserData_seven(self):
        test = dbqueries.getUserData(self.db_conn, "root", "", "PassHash")[0]
        assert bcrypt.checkpw("root".encode("UTF-8"),
                              test["PassHash"].encode("UTF-8"))

    def test_getFileData_one(self):
        test = dbqueries.getFileData(self.db_conn)
        assert len(test) == 3

    def test_getFileData_two(self):
        test = dbqueries.getFileData(self.db_conn, "earth.jpg")
        assert len(test) == 1

        test = dbqueries.getFileData(self.db_conn, "linux.png")
        assert len(test) == 1

        test = dbqueries.getFileData(self.db_conn, "statue.png")
        assert len(test) == 1

    def test_getFileData_three(self):
        with pytest.raises(sqlite3.OperationalError) as excinfo:
            dbqueries.getFileData(self.db_conn, "earth.jpg", "Dirtake")

        assert excinfo.type == sqlite3.OperationalError

    def test_getFileData_four(self):
        test = dbqueries.getFileData(
            self.db_conn, "linux.png", "DownloadCount"
        )
        assert test[0]["DownloadCount"] == 0

    def test_getFileData_five(self):
        test = dbqueries.getFileData(self.db_conn, "", "ID")
        assert test[0]["ID"] == 1

    # TODO: rest of testing
