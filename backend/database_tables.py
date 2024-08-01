import sqlite3


def createUserPrivilegesTable(cur: sqlite3.Cursor):
    """ Creates the user privileges table in the sql database.

    Type is one of the following: "Admin", "Uploader", "Viewer".

    Args:
        cur: A cursor to the sqlite3 database

    Returns:
        None
    """
    cur.execute("""
        CREATE TABLE IF NOT EXISTS UserPrivileges (
            Number INTEGER PRIMARY KEY,
            Type VARCHAR(64) NOT NULL
        );
    """)


def createUserTable(cur: sqlite3.Cursor):
    """ Creates the users tables

    This table stores all of the users information, the privilege level
    is used to give the user more or less features.

    Args:
        cur: A cursor to the sqlite3 database

    Returns:
        None
    """
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            ID INTEGER PRIMARY KEY,
            Username VARCHAR(255),
            PassHash VARCHAR(255),
            Privilege INTEGER NOT NULL,
            FOREIGN KEY (Privilege) REFERENCES UserPrivileges (Number)
        );
    """)


def createFileTable(cur: sqlite3.Cursor):
    """ Creates the files table

    This table stores all most all information about a file.

    Args:
        cur: A cursor to the sqlite3 database

    Returns:
        None
    """
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Files (
            ID INTEGER PRIMARY KEY,
            FileName VARCHAR(255) NOT NULL,
            DownloadCount INTEGER,
            UploadDate DATE
        );
    """)


def createDownloadHistoryTable(cur: sqlite3.Cursor):
    """ Creates the table that stores information on who has downloaded a
    file.

    Args:
        cur: A cursor to the sqlite3 database

    Returns:
        None
    """
    cur.execute("""
        CREATE TABLE IF NOT EXISTS DownloadHistory (
            UserID INTEGER NOT NULL,
            FileID INTEGER NOT NULL,
            Timestamp DATE,
            FOREIGN KEY (UserID) REFERENCES Users (ID),
            FOREIGN KEY (FileID) REFERENCES Files (ID)
        );
    """)
