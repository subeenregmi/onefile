from flask import (
    Flask, render_template, request, send_from_directory, make_response,
    redirect, url_for, session
)
from flask_apscheduler import APScheduler
from werkzeug.utils import secure_filename
from database_queries import (
    getUserData, addFile, removeFile, getFileData, addDownloadTransaction,
    incrementDownloadCount, getFileStatistics, createUser, removeUser,
    removeFileHistory, addPageVisit, incrementPageVisits, getPageData,
    getPageVisitsData, refreshFiles
)
from database_utils import (
    setupDatabase, createAnonUser
)
from server_utils import Responses, Privilege, createResp, checkPrivilege
from bcrypt import hashpw, checkpw, gensalt
from config import getConfig
from logging.config import dictConfig
import hashlib
import os


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format":
                "[%(asctime)s] | %(levelname)s %(funcName)s | %(message)s",
                "datefmt": "%H:%M - %d-%m-%Y ",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/server.log",
                "maxBytes": 5000000,
                "backupCount": 5,
                "formatter": "default"
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": [
                "console",
                "file"
            ]
        },
    }
)


config = getConfig("config.yaml")
app = Flask(__name__,
            template_folder="../templates/",
            static_folder="../static/")

app.secret_key = config['secret_key']

db_conn = setupDatabase(config['database'])
fileHashes = dict()


@app.route("/")
def home():
    """ The login page users have to use to login to the app """
    incrementPageVisits(db_conn, "login")
    addPageVisit(db_conn, "login", None, request.remote_addr)

    if config["loginRequired"]:
        return render_template("loginpage.html", host=config["host"])
    else:
        app.logger.info("Anonymous user logged in.")
        session["username"] = "Anonymous"
        session["privilege"] = Privilege.USER.value
        session["user_id"] = -1
        return redirect(url_for('dashboard'))


@app.route("/login", methods=["POST"])
def login():
    """ The api correlating to the logging in to the user."""

    username = request.json.get("username")
    password = request.json.get("password").encode("UTF-8")

    user = getUserData(db_conn, username, "")

    # If the user does not exist, redirect to homepage
    if not user:
        app.logger.info(
            f"User '{username}' tried to login, but does not exist."
        )
        return redirect(url_for("home"), 403)

    user = user[0]

    if not checkpw(password, user["PassHash"].encode("UTF-8")):
        app.logger.info(f"User '{username}' login failed.")
        return redirect(url_for("home"), 403)

    session["username"] = user["Username"]
    session["privilege"] = user["Privilege"]
    session["user_id"] = user["ID"]

    return redirect(url_for('dashboard'))


@app.route("/dashboard")
def dashboard():
    """ This is the page for whom who successfully login. """

    username = session.get("username")
    privilege = Privilege(session.get("privilege"))

    if username is None:
        app.logger.info("User tried to access dashboard before logging in.")
        return redirect(url_for("home"), 403)

    # Cannot login with the anonymous account if login is needed
    if username == "Anonymous" and config["loginRequired"]:
        app.logger.warning(
            "Anonymous passed login but failed dashboard check."
        )
        return redirect(url_for("home"), 403)

    incrementPageVisits(db_conn, "dashboard")
    addPageVisit(
        db_conn,
        "dashboard",
        session.get("user_id"),
        request.remote_addr
    )

    match privilege:
        case Privilege.ADMIN:
            app.logger.info(f"Admin '{username}' has successfully logged in.")
            return render_template("adminpage.html", host=config["host"])

        case Privilege.UPLOADER:
            app.logger.info(
                f"Uploader '{username}' has successfully logged in."
            )
            return render_template("uploadpage.html")

        case Privilege.USER:
            app.logger.info(f"Viewer '{username}' has successfully logged in.")
            return render_template("userpage.html", username=username,
                                   host=config["host"])

        case _:
            app.logger.warning(
                f"User '{username}' has tried to login with unknown privilege."
            )
            return redirect(url_for("home"), 403)


@app.route('/api/file/upload', methods=["POST"])
def uploadFile():
    """ Api route to upload a file, needs to be sent through post
    form data.
    """

    username = session.get("username")
    privilege = Privilege(session.get("privilege"))

    if not checkPrivilege(privilege, Privilege.UPLOADER):
        app.logger.warning(
            f"User '{username}' has tried to upload a file without the correct"
            " permissions.")
        return createResp(Responses.PRIVILEGE_ERROR)

    filename = request.form.get("filename")
    file = request.files.get("file")

    # Empty file name
    if not filename:
        app.logger.info(
            f"User '{username}' is trying to upload a file with no name."
        )
        return createResp(Responses.EMPTY_NAME)

    filename = secure_filename(filename)

    # File name is taken
    if getFileData(db_conn, filename):
        app.logger.info(
            f"User '{username}' is trying to upload '{filename}', "
            "this name has been taken."
        )
        return createResp(Responses.TAKEN_FILE_NAME)

    file.save(f"shared_files/{filename}")
    addFile(db_conn, filename)

    app.logger.info(f"User {username} has added a new file: '{filename}'.")

    return createResp(Responses.SUCCESS)


@app.route('/api/file/delete', methods=["POST"])
def deleteFile():
    """ Api route to delete a file, needs to be sent through post
    form data.
    """

    username = session.get("username")
    privilege = Privilege(session.get("privilege"))

    if not checkPrivilege(privilege, Privilege.UPLOADER):
        app.logger.warning(
            f"User '{username}' has tried to delete a file without the correct"
            " permissions.")
        return createResp(Responses.PRIVILEGE_ERROR)

    filename = request.json.get("filename")

    if not filename:
        return createResp(Responses.EMPTY_NAME)

    if not getFileData(db_conn, filename):
        return createResp(Responses.FILE_NOT_EXISTS)

    removeFileHistory(db_conn, filename)
    removeFile(db_conn, filename)

    app.logger.info(f"User {username} has delete a new file: '{filename}'.")
    return createResp(Responses.SUCCESS)


@app.route("/api/file/data", methods=["POST"])
def getFile():
    """ Api route to get file data. """

    privilege = Privilege(session.get("privilege"))
    if not checkPrivilege(privilege, Privilege.USER):
        return createResp(Responses.PRIVILEGE_ERROR)

    filename = request.json.get("filename")

    if not filename:
        return createResp(Responses.EMPTY_NAME)

    if not getFileData(db_conn, filename):
        return createResp(Responses.FILE_NOT_EXISTS)

    columns = request.args.to_dict(flat=False).get("cols")
    if filename == "all":
        filename = ""

    app.logger.debug(
        f"File information for '{filename or "*"}' is being retrieved."
    )

    if columns == ["all"] or not columns:
        columns = []

    return getFileData(db_conn, filename, *columns)[0]


@app.route("/api/file/download", methods=["POST"])
def downloadFile():
    """ Api route to download a file. """

    privilege = Privilege(session.get("privilege"))
    if not checkPrivilege(privilege, Privilege.USER):
        return createResp(Responses.PRIVILEGE_ERROR)

    filename = request.json.get("filename")

    if not filename:
        return createResp(Responses.EMPTY_NAME)

    if not (file := getFileData(db_conn, filename)):
        return createResp(Responses.FILE_NOT_EXISTS)

    response = make_response(send_from_directory("../shared_files", filename))

    # Ensuring that files download automatically and not open in browser.
    response.headers["Content-Disposition"] = "attachment"

    username = session.get("username")
    userID = session.get("user_id")

    addDownloadTransaction(db_conn, userID, file[0]["ID"])
    incrementDownloadCount(db_conn, filename)

    app.logger.info(f"User {username} has downloaded {filename}.")
    return response


@app.route("/api/file/downloadhistory", methods=["POST"])
def getFileStats():
    """ Api route to retrieve file download history."""

    privilege = Privilege(session.get("privilege"))
    if not checkPrivilege(privilege, Privilege.USER):
        return createResp(Responses.PRIVILEGE_ERROR)

    app.logger.debug(
        f"File statistics for '{request.json["filename"]}' retrieved."
    )
    filename = request.json.get("filename")

    if not filename:
        return createResp(Responses.EMPTY_NAME)

    if not getFileData(db_conn, filename):
        return createResp(Responses.FILE_NOT_EXISTS)

    return getFileStatistics(db_conn, filename)


@app.route("/api/file/hash", methods=["POST"])
def getHash():
    """ Retrieves the hash of a file in the shared_files directory. """

    privilege = Privilege(session.get("privilege"))
    if not checkPrivilege(privilege, Privilege.USER):
        return createResp(Responses.PRIVILEGE_ERROR)

    filename = request.json.get("filename")
    app.logger.info(f"Retrieving hash for {filename}.")

    if cacheResult := fileHashes.get(filename):
        return {
            "filename": filename,
            "hash": cacheResult
        }

    if not filename:
        return createResp(Responses.EMPTY_NAME)

    if not getFileData(db_conn, filename):
        return createResp(Responses.FILE_NOT_EXISTS)

    pathToFile = os.path.join(
        os.path.dirname(__file__),
        "..",
        "shared_files/",
        secure_filename(filename)
    )

    if not os.path.isfile(pathToFile):
        return createResp(Responses.FILE_NOT_EXISTS)

    sha_hash = hashlib.sha256()
    bufferSize = 65536  # 64KB

    with open(pathToFile, "rb") as f:
        while True:
            data = f.read(bufferSize)
            if not data:
                break
            sha_hash.update(data)

    fileHashes[filename] = sha_hash.hexdigest()
    return {
        "filename": filename,
        "hash": fileHashes[filename]
    }


@app.route("/api/user/create", methods=["POST"])
def addUser():
    """ Api route to create a new user, admins can only create new users """
    username = session.get("username")
    privilege = Privilege(session.get("privilege"))

    if not checkPrivilege(privilege, Privilege.ADMIN):
        app.logger.warning(
            f"User '{username}' has tried to add a new user without the"
            " correct permissions."
        )
        return createResp(Responses.PRIVILEGE_ERROR)

    newUsername = request.json.get("username")

    if not newUsername:
        return createResp(Responses.EMPTY_USERNAME)

    if getUserData(db_conn, newUsername):
        return createResp(Responses.TAKEN_USERNAME)

    newPassword = request.json.get("password")

    if not newPassword:
        return createResp(Responses.EMPTY_PASSWORD)

    newPassword = newPassword.encode("UTF-8")

    newPassHash = hashpw(newPassword, gensalt()).decode("UTF-8")
    newPrivilege = Privilege(request.json.get("privilege"))

    if newPrivilege is Privilege.UNKNOWN:
        return createResp(Responses.UNSPECIFIED_PRIVILEGE)

    createUser(db_conn, newUsername, newPassHash, newPrivilege.value)
    app.logger.info(
        f"New user '{newUsername}' has been created by '{username}'."
    )

    return createResp(Responses.SUCCESS)


@app.route("/api/user/delete", methods=["POST"])
def deleteUser():
    """ Api route to delete a user from the database """

    usern = session.get("username")
    privilege = Privilege(session.get("privilege"))

    if not checkPrivilege(privilege, Privilege.ADMIN):
        app.logger.warning(
            f"User '{usern}' has tried to delete a user without the"
            " correct permissions."
        )
        return createResp(Responses.PRIVILEGE_ERROR)

    username = request.json.get("username")

    if not username:
        return createResp(Responses.EMPTY_USERNAME)

    if not getUserData(db_conn, username):
        return createResp(Responses.USER_NOT_FOUND)

    # TODO: Fix? Foreign key constraint
    # Add a deleted user
    removeUser(db_conn, username)

    app.logger.info(f"User '{username}' has been deleted by user '{usern}'.")
    return createResp(Responses.SUCCESS)


@app.route("/api/user/search", methods=["POST"])
def getUser():
    """ Retrieves information about a user """

    privilege = Privilege(session.get("privilege"))
    if not checkPrivilege(privilege, Privilege.USER):
        return createResp(Responses.PRIVILEGE_ERROR)

    username = request.json.get("username")

    if not username:
        return createResp(Responses.EMPTY_USERNAME)

    if not getUserData(db_conn, username) and username != "all":
        return createResp(Responses.USER_NOT_FOUND)

    if username == "all":
        username = ""

    columns = request.args.to_dict(flat=False).get("cols")

    if columns == ["all"] or not columns:
        columns = ""

    app.logger.debug(f"User data for '{username or "*"}' has been retrieved.")
    return getUserData(db_conn, username, "", *columns)


@app.route("/api/pages/history", methods=["POST"])
def getPageStats():
    """ Retrieves page viewing history. """

    privilege = Privilege(session.get("privilege"))
    if not checkPrivilege(privilege, Privilege.USER):
        return createResp(Responses.PRIVILEGE_ERROR)

    pageName = request.json.get("pagename")

    if not pageName:
        return createResp(Responses.EMPTY_PAGE_NAME)

    if not (pageID := getPageData(db_conn, pageName, "ID")):
        return createResp(Responses.PAGE_NOT_FOUND)

    # TODO: Fix this?
    app.logger.info("")

    pageID = pageID[0]["ID"]

    return getPageVisitsData(db_conn, pageID)


@app.route("/api/pages", methods=["POST"])
def retrievePageData():
    """ Retrieves information about a page """

    privilege = Privilege(session.get("privilege"))
    if not checkPrivilege(privilege, Privilege.USER):
        return createResp(Responses.PRIVILEGE_ERROR)

    pageName = request.json.get("pagename")

    if not pageName:
        return createResp(Responses.EMPTY_PAGE_NAME)

    if not getPageData(db_conn, pageName, "ID") and pageName != "all":
        return createResp(Responses.PAGE_NOT_FOUND)

    if pageName == "all":
        pageName = ""

    columns = request.args.to_dict(flat=False).get('cols')
    if columns == ["all"] or not columns:
        columns = ""

    return getPageData(db_conn, pageName, *columns)


def main():
    app.debug = True

    # Add timed job to refresh files
    scheduler = APScheduler()
    scheduler.add_job(
        "refreshfiles",
        func=refreshFiles,
        args=[db_conn],
        trigger="interval",
        seconds=config["refresh_files"]
    )
    scheduler.start()

    if not config['loginRequired']:
        app.logger.info("Anonymous user has been created.")
        createAnonUser(db_conn)

    app.logger.info("="*50)
    app.logger.info("Starting app...")
    app.run(host=config["host"])


if __name__ == "__main__":
    main()
