import pytest
import sqlite3
import sys
import os
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
)
import backend.database_queries as dbqueries
import backend.database_utils as dbutils
import backend.database_tables as dbtables


try:
    os.remove("temp/test_db_queries.db")
except FileNotFoundError:
    pass


class TestDatabaseQueries:
    db_conn = sqlite3.connect("temp/test_db_queries.db")
    db_cur = db_conn.cursor()

    dbtables.createUserPrivilegesTable(db_conn)
    dbtables.createUserTable(db_conn)
    dbtables.createFileTable(db_conn)
    dbtables.createDownloadHistoryTable(db_conn)

    dbutils.initFiles(db_conn, "temp/images/")
    dbutils.createDefaultUser(db_conn)
