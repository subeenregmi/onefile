import sqlite3
import database_tables
from os import listdir
from bcrypt import hashpw, gensalt


def initUserPrivileges(conn: sqlite3.Connection):
    """ Sets the basic user privileges that are available.

    Args:
        conn: The sqlite3 connection object connected to the database

    Returns:
        None
    """
    privileges = [
        (1, "Admin"),
        (2, "Uploader"),
        (3, "Viewer")
    ]
    if (conn.execute("SELECT * FROM UserPrivileges").fetchone() is None):
        conn.executemany("""
            INSERT INTO UserPrivileges (Number, Type) VALUES (?, ?)
            """, privileges)
        conn.commit()


def createTestUsers(conn: sqlite3.Connection):
    """ This function creates some test users.

    Args:
        conn: The sqlite3 connection object connected to the database

    Returns:
        None
    """
    testUsers = [
        (
            "root",
            f"{hashpw("root".encode("UTF-8"), gensalt()).decode("UTF-8")}",
            "1"
        )
    ]
    if (conn.execute("SELECT * FROM Users").fetchone() is None):
        conn.executemany("""
            INSERT INTO Users (Username, PassHash, Privilege)
            VALUES (?, ?, ?)
        """, testUsers)
        conn.commit()


def initFiles(conn: sqlite3.Connection):
    """ Creates a file in entry for all the files in the 'shared_files'
    directory.

    Args:
        conn: The sqlite3 connection object connected to the database

    Returns:
        None
    """
    files = listdir("shared_files/")
    files = [(x, 0) for x in files]

    if (conn.execute("SELECT * FROM Files;").fetchone() is None):
        conn.executemany("""
            INSERT INTO Files (FileName, DownloadCount, UploadDate)
            VALUES (?, ?, DATETIME('now'))
        """, files)
        conn.commit()


def setupDatabase(name: str) -> sqlite3.Connection:
    """ Setups the database and all tables.

    Args:
        name: Name of the database

    Returns:
        A connection to the database
    """
    conn = sqlite3.connect(name, check_same_thread=False)

    conn.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    database_tables.createUserPrivilegesTable(conn)
    initUserPrivileges(conn)

    database_tables.createFileTable(conn)
    initFiles(conn)

    database_tables.createUserTable(conn)
    createTestUsers(conn)

    database_tables.createDownloadHistoryTable(conn)
    return conn


def getTableColumns(tableName: str) -> list[str]:
    """ Gets all the columns for tables in the database

    Args:
        tableName: The name of the table

    Returns:
        A list of strings representing the columns of the table.
    """
    match tableName:
        case "Users":
            return ["ID", "Username", "PassHash", "Privilege"]
        case "Files":
            return ["ID", "FileName", "DownloadCount", "UploadDate"]
        case "DownloadHistory":
            return ["UserID", "FileID", "Timestamp"]
        case "UserPrivileges":
            return ["Number", "Type"]
        case _:
            return []
