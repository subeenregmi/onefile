import sqlite3
import os
from database_utils import getTableColumns, initFiles


def getUserData(
    conn: sqlite3.Connection,
    username: str = "",
    passHash: str = "",
    *args: str
) -> list[dict[str, str | int | None]]:
    """ This function gets a user(s) information provided the username

    Args:
        conn: The sqlite3 connection object connected to the database
        username: The username of the user, if omitted then it matches
                  all users
        passHash: The hash of the users password, if omitted then it
                  matches all pass hashes.
        *args: This represents the columns we want to query, by
               default this is all columns
Returns:
        A list of dictionaries in which the key is a column and the value
        is the stored data for that user.
    """
    cur = conn.cursor()
    users = cur.execute(f"""
        SELECT {", ".join([*args]) or "*"}
        FROM Users
        WHERE Username = {f"'{username}'" if username != "" else "Username"} 
        AND PassHash = {f"'{passHash}'" if passHash != "" else "PassHash"}
     """).fetchall()

    columns = [*args] or getTableColumns("Users")
    return [dict(zip(columns, user)) for user in users]


def getFileData(
    conn: sqlite3.Connection,
    filename: str = "",
    *args: str
) -> list[dict[str, str | int | None]]:
    """ This function gets a file(s) information provided the filename

    Args:
        conn: The sqlite3 connection object connected to the database
        filename: The file's name, if left then it will match all filenames
        *args: This represent all the columns that we want to query, by
               default this is all columns

    Returns:
        A list of dictionaries in which the key is a column and value is
        the stored data for that user.
    """
    cur = conn.cursor()
    files = cur.execute(f"""
        SELECT {", ".join([*args]) or "*"}
        FROM Files
        WHERE FileName = {f"'{filename}'" if filename != "" else "FileName"}
    """).fetchall()

    columns = [*args] or getTableColumns("Files")
    return [dict(zip(columns, file)) for file in files]


def getFileStatistics(
    conn: sqlite3.Connection,
    filename: str = "",
    *args: str
) -> list[dict[str, str | int | None]]:
    """ Gets the download history of a file

    Args:
        conn: The sqlite3 connection object connected to the database
        filename: The file's name, if left then it will match all filenames
        *args: This represent all the columns that we want to query, by
               default this is all columns

    Returns:
        List of dictionaries in which each dictionary contains the information
        for each download.
    """
    cur = conn.cursor()

    if filename:
        fileID = getFileData(conn, filename, "ID")[0]["ID"]
    else:
        fileID = "FileID"

    files = cur.execute(f"""
        SELECT {", ".join([*args]) or "*"}
        FROM DownloadHistory INNER JOIN Users
        ON DownloadHistory.UserID = Users.ID
        WHERE FileID = {fileID}
    """).fetchall()

    columns = [*args] or (
        getTableColumns("DownloadHistory") + getTableColumns("Users")
    )
    return [dict(zip(columns, file)) for file in files]


def addFile(conn: sqlite3.Connection, filename: str):
    """ Adds a file onto the database

    Args:
        conn: A sqlite3 connection object connected to the database
        filename: The name of the new file

    Returns:
        None
    """

    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO Files (FileName, DownloadCount, UploadDate)
        VALUES ('{filename}', 0, DATETIME('now', 'localtime'));
    """)
    conn.commit()


def incrementDownloadCount(conn: sqlite3.Connection, filename: str):
    """ Increments the download count of a file

    Args:
        conn: A sqlite3 connection object connected to the database
        filename: The name of file to be incremented

    Returns:
        None
    """
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE Files
        SET DownloadCount = DownloadCount + 1
        WHERE FileName = '{filename}';
    """)
    conn.commit()


def removeFile(conn: sqlite3.Connection, filename: str):
    """ Removes the file from the database

    Note: This does not remove the file from the 'shared_folder'
    directory

    Args:
        conn: A sqlite3 connection object connected to the database
        filename: The name of file to be deleted

    Returns: None
    """

    cur = conn.cursor()
    cur.execute(f"""
        DELETE FROM Files
        WHERE FileName = '{filename}'
    """)
    conn.commit()


def removeFileHistory(conn: sqlite3.Connection, filename: str):
    """ Removes the files download history.

    This is used to allow for user and file to be deleted.

    Args:
        conn: A sqlite3 connection object connected to the database
        filename: References to the file

    Returns:
        None
    """
    cur = conn.cursor()
    fileData = getFileData(conn, filename, "ID")[0]
    fileID = fileData['ID']

    cur.execute(f"""
        DELETE FROM DownloadHistory
        WHERE FileID = {fileID}
    """)
    conn.commit()


def refreshFiles(conn: sqlite3.Connection):
    """ Refreshes files on the database with the files in the
    shared_files directory.

    Args:
        conn: A sqlite3 connection object connected to the database

    Returns:
        None
    """
    initFiles(conn, "shared_files/")

    filesInDB = [x["FileName"] for x in getFileData(conn, "", "FileName")]
    filesInDir = os.listdir(os.path.join(
        os.path.dirname(__file__), "..", "shared_files/"
    ))

    filesToDelete = set(filesInDB) - set(filesInDir)

    for file in filesToDelete:
        removeFileHistory(conn, file)
        removeFile(conn, file)


def addDownloadTransaction(
    conn: sqlite3.Connection,
    userID: int,
    fileID: int
):
    """ Adds a new download transaction, commiting it as history
    on the database

    Args:
        conn: A sqlite3 connection object connected to the database
        userID: The user who downloaded the file
        fileID: The file which was downloaded

    Returns:
        None
    """
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO DownloadHistory (UserID, FileID, Timestamp)
        VALUES ('{userID}', '{fileID}', DATETIME('now', 'localtime'))
    """)
    conn.commit()


def createUser(
    conn: sqlite3.Connection,
    username: str,
    passhash: str,
    privilege: int
):
    """ Creates a new user into the database

    Args:
        conn: A sqlite3 connection object connected to the database
        username: The username of the new user
        passhash: The bcrypted hashed password
        privilege: The privilege level of the new user

    Returns:
        None
    """
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO Users (Username, PassHash, Privilege)
        VALUES ('{username}', '{passhash}', {privilege})
    """)
    conn.commit()


def removeUser(
    conn: sqlite3.Connection,
    username: str
):
    """ Deletes a user from the database

    Args:
        conn: A sqlite3 connection object connected to the database
        username: The username of the deleted user

    Returns:
        None
    """
    cur = conn.cursor()
    cur.execute(f"""
        DELETE FROM Users
        WHERE Username = '{username}'
    """)
    conn.commit()


def incrementPageVisits(conn: sqlite3.Connection, name: str):
    """ This increments the page view count in the pages table

    Args:
        conn: The sqlite connection to the database
        name: The page we want to view

    Returns:
        None
    """
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE Pages
        SET ViewCount = ViewCount + 1
        WHERE Name = '{name}';
    """)
    conn.commit()


def getPageData(
    conn: sqlite3.Connection,
    pageName: str = "",
    *args: str
) -> list[dict[str, str | int | None]]:
    """
    Args:
        conn: The sqlite3 connection object connected to the database
        pageName: The page's name we want to query data from
        *args: This represent all the columns that we want to query, by
               default this is all columns

    Returns:
        List of dictionaries in which each dictionary contains the information
        for each page.
    """

    cur = conn.cursor()
    pages = cur.execute(f"""
        SELECT {", ".join([*args]) or "*"}
        FROM Pages 
        WHERE Name = {f"'{pageName}'" if pageName != "" else "Name"}
     """).fetchall()

    columns = [*args] or getTableColumns("Pages")
    return [dict(zip(columns, page)) for page in pages]


def addPageVisit(
    conn: sqlite3.Connection,
    pageName: str,
    userID: int | None,
    ipAddress: str
):
    """ This adds a page visit transaction for a page in the PageVisits table

    Args:
        conn: The sqlite connection to the database
        pageName: The page we want to add a visit for
        userID: The user who went the page
        ipAddress: The ip address of the user

    Returns:
        None
    """
    cur = conn.cursor()

    pageID = getPageData(conn, pageName, "ID")[0]["ID"]

    cur.execute(f"""
        INSERT INTO PageVisits (PageID, UserID, IpAddress, Timestamp)
        VALUES (
        {pageID}, {userID or "NULL"}, '{ipAddress}',
        DATETIME('now', 'localtime'))
    """)
    conn.commit()


def getPageVisitsData(
    conn: sqlite3.Connection,
    pageID: int,
    *args: str
) -> list[dict[str, str | int | None]]:
    """
    Args:
        conn: The sqlite3 connection object connected to the database
        pageName: The page's name we want to query visits from
        *args: This represent all the columns that we want to query, by
               default this is all columns

    Returns:
        List of dictionaries in which each dictionary contains the visit
        history for each page.
    """

    cur = conn.cursor()

    pages = cur.execute(f"""
        SELECT {", ".join([*args]) or "*"}
        FROM PageVisits
        WHERE PageID = {pageID}
     """).fetchall()

    columns = [*args] or getTableColumns("PageVisits")
    return [dict(zip(columns, page)) for page in pages]
