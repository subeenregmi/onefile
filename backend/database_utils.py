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
    cur = conn.cursor()
    if (cur.execute("SELECT * FROM UserPrivileges").fetchone() is None):
        cur.executemany("""
            INSERT INTO UserPrivileges (Number, Type) VALUES (?, ?)
            """, privileges)
        conn.commit()


def createDefaultUser(conn: sqlite3.Connection):
    """ This function creates the default root users.

    username: root
    password: root

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
    cur = conn.cursor()
    if (cur.execute("SELECT * FROM Users").fetchone() is None):
        cur.executemany("""
            INSERT INTO Users (Username, PassHash, Privilege)
            VALUES (?, ?, ?)
        """, testUsers)
        conn.commit()


def initFiles(conn: sqlite3.Connection, filedir: str):
    """ Creates a file in entry for all the files in the 'shared_files'
    directory.

    Args:
        conn: The sqlite3 connection object connected to the database
        filedir: The directory where we want to look for files

    Returns:
        None
    """
    files = listdir(filedir)
    files = [(x, 0) for x in files]

    cur = conn.cursor()
    if (cur.execute("SELECT * FROM Files;").fetchone() is None):
        cur.executemany("""
            INSERT INTO Files (FileName, DownloadCount, UploadDate)
            VALUES (?, ?, DATETIME('now'))
        """, files)
        conn.commit()


def setupDatabase(
    name: str,
    filesFolder: str = "shared_files/"
) -> sqlite3.Connection:
    """ Setups the database and all tables.

    Args:
        name: Name of the database

    Returns:
        A connection to the database
    """
    conn = sqlite3.connect(name, check_same_thread=False)
    cur = conn.cursor()

    cur.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    database_tables.createUserPrivilegesTable(conn)
    initUserPrivileges(conn)

    database_tables.createFileTable(conn)
    initFiles(conn, filesFolder)

    database_tables.createUserTable(conn)
    createDefaultUser(conn)

    database_tables.createDownloadHistoryTable(conn)

    database_tables.createPagesTable(conn)
    database_tables.createPageVisitsTable(conn)

    createPageEntries(conn)

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
        case "Pages":
            return ["ID", "Name", "ViewCount"]
        case "PageVisits":
            return ["ID", "PageID", "UserID", "IpAddress", "Timestamp"]
        case _:
            return []


def createAnonUser(conn: sqlite3.Connection):
    """ Creates the anonymous user, which represents a user who has not
        logged in

        The anon user is only created when 'loginRequired' in config.yaml
        is set to false

        Args:
            conn: The sqlite3 connection object connected to the database

        Returns:
            None
    """
    cur = conn.cursor()

    anonUser = cur.execute("""
        SELECT *
        FROM Users
        WHERE Username = "Anonymous"
    """).fetchone()

    if not anonUser:
        cur.execute("""
            INSERT INTO Users (ID, Username, PassHash, Privilege)
            VALUES (-1, "Anonymous", "", 3)
        """)
        conn.commit()


def createPageEntries(conn: sqlite3.Connection):
    """ Creates the page entries for the pages in the website.

    Args:
        conn: The sqlite3 connection object connected to the database

    Returns:
        None
    """
    pages = [
        ("home", 0),
        ("dashboard", 0)
    ]
    cur = conn.cursor()

    pageEntries = cur.execute("""
        SELECT *
        FROM Pages
    """).fetchall()

    if not pageEntries:
        cur.executemany("""
            INSERT INTO Pages (Name, ViewCount)
            VALUES (?, ?)
        """, pages)
        conn.commit()
