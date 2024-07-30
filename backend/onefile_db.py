import sqlite3
from os import listdir


def setupUserPrivileges(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS UserPrivileges (
            Number INTEGER PRIMARY KEY,
            Type VARCHAR(64) NOT NULL
        );
    """)
    privileges = [
        (1, "Admin"),
        (2, "Uploader"),
        (3, "Viewer")
    ]
    if (con.execute("SELECT * FROM UserPrivileges").fetchone() is None):
        con.executemany("""
            INSERT INTO UserPrivileges (Number, Type) VALUES (?, ?)
            """, privileges)
        con.commit()


def setupUserTable(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            ID INTEGER PRIMARY KEY,
            Username VARCHAR(255),
            PassHash VARCHAR(255),
            Privilege INTEGER NOT NULL,
            FOREIGN KEY (Privilege) REFERENCES UserPrivileges (Number)
        );
    """)


def setupFileTable(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS Files (
            ID INTEGER PRIMARY KEY,
            FileName VARCHAR(255) NOT NULL,
            DownloadCount INTEGER,
            UploadDate DATE
        );
    """)


def setupDownloadHistory(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS DownloadHistory (
            UserID INTEGER NOT NULL,
            FileID INTEGER NOT NULL,
            Timestamp DATE,
            FOREIGN KEY (UserID) REFERENCES Users (ID),
            FOREIGN KEY (FileID) REFERENCES Files (ID)
        );
                """)


def setupUserPermissionTable(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS PermittedUsers (
            UserID INTEGER NOT NULL,
            FileID INTEGER NOT NULL,
            PRIMARY KEY (UserID, FileID),
            FOREIGN KEY (UserID) REFERENCES Users (ID),
            FOREIGN KEY (FileID) REFERENCES Files (ID)
        );
    """)


def setupTestUsers(con):
    data = [
        ("Subeen", "123", "1"),
        ("John", "456", "3"),
        ("Adam", "789", "3")
    ]
    if (con.execute("SELECT * FROM Users").fetchone() is None):
        con.executemany("""
            INSERT INTO Users (Username, PassHash, Privilege) VALUES (?, ?, ?)
        """, data)
        con.commit()


def checkUser(con, username, passhash):
    res = con.execute(f"""
       SELECT * FROM Users WHERE Username = '{username}'
       AND PassHash = '{passhash}';
    """)
    return res.fetchone() is not None


def getAllFileNames(con):
    return con.execute("SELECT FileName FROM Files;").fetchall()


def initialiseFiles(con):
    files = listdir("shared_files/")
    files = [(x, 0) for x in files]

    if (con.execute("SELECT * FROM Files;").fetchone() is None):
        con.executemany("""
            INSERT INTO Files (FileName, DownloadCount, UploadDate)
            VALUES (?, ?, DATETIME('now'))
        """, files)
        con.commit()


def addFile(con, filename):
    con.execute(f"""
        INSERT INTO Files (FileName, DownloadCount, UploadDate)
        VALUES ('{filename}', 0, DATETIME('now'));
                """)
    con.commit()


def incrementDownloadCount(con, fileName):
    con.execute(f"""
        UPDATE Files
        SET DownloadCount = DownloadCount + 1
        WHERE FileName = '{fileName}';
                """)
    con.commit()


def getAllFileData(con):
    return dict(con.execute("""
        SELECT FileName, DownloadCount
        FROM Files;
                """).fetchall())


def removeFile(con, filename):
    con.execute(f"""
        DELETE FROM Files
        WHERE FileName = '{filename}'
                """)
    con.commit()


def getUserPrivilege(con, username):
    return con.execute(f"""
        SELECT Type
        FROM Users INNER JOIN UserPrivileges
        ON Users.Privilege = UserPrivileges.Number
        WHERE Username = '{username}'
    """).fetchall()[0][0]


def addDownloadTransaction(con, userID, fileID):
    con.execute(f"""
        INSERT INTO DownloadHistory (UserID, FileID, Timestamp)
        VALUES ('{userID}', '{fileID}', DATETIME('now'))
                """)


def getUserID(con, username):
    return con.execute(f"""
        SELECT ID
        FROM Users
        WHERE Username = '{username}'
                       """).fetchone()[0]


def getFileID(con, filename):
    return con.execute(f"""
        SELECT ID
        FROM Files
        WHERE FileName = '{filename}'
                """).fetchone()[0]


def getFileStatistics(con, filename):
    fileID = getFileID(con, filename)
    return con.execute(f"""
        SELECT Username, Timestamp
        FROM DownloadHistory INNER JOIN Users
        ON DownloadHistory.UserID = Users.ID
        WHERE FileID = {fileID}
                      """).fetchall()


def setupDatabase(name):
    con = sqlite3.connect(name, check_same_thread=False)
    setupUserPrivileges(con)
    setupFileTable(con)
    setupUserTable(con)
    setupDownloadHistory(con)
    setupUserPermissionTable(con)
    return con
