import sqlite3
from database_utils import getTableColumns


def getUserData(
    conn: sqlite3.Connection,
    username: str = "",
    passHash: str = "",
    *args: str
) -> list[dict[str, str | int | None]]:
    """ This function gets a user(s) information provided the username

    Args:
        conn: A sqlite3 connection object connected to the database
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

    users = conn.execute(f"""
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
        conn: A sqlite3 connection object connected to the database
        filename: The file's name, if left then it will match all filenames
        *args: This represent all the columns that we want to query, by
               default this is all columns

    Returns:
        A list of dictionaries in which the key is a column and value is
        the stored data for that user.
    """

    files = conn.execute(f"""
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
        conn: A sqlite3 connection object connected to the database
        filename: The file's name, if left then it will match all filenames
        *args: This represent all the columns that we want to query, by
               default this is all columns

    Returns:
        List of dictionaries in which each dictionary contains the information
        for each download.
    """

    if filename:
        fileID = getFileData(conn, filename, "ID")[0]["ID"]
    else:
        fileID = "FileID"

    files = conn.execute(f"""
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

    conn.execute(f"""
        INSERT INTO Files (FileName, DownloadCount, UploadDate)
        VALUES ('{filename}', 0, DATETIME('now'));
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
    conn.execute(f"""
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
    conn.execute(f"""
        DELETE FROM Files
        WHERE FileName = '{filename}'
    """)
    conn.commit()


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
    conn.execute(f"""
        INSERT INTO DownloadHistory (UserID, FileID, Timestamp)
        VALUES ('{userID}', '{fileID}', DATETIME('now'))
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
    """
    conn.execute(f"""
        INSERT INTO Users (Username, PassHash, Privilege)
        VALUES ('{username}', '{passhash}', {privilege})
    """)
    conn.commit()
