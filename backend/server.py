from flask import (
    Flask, render_template, request, send_from_directory, make_response,
    redirect, url_for, session
)
from database_queries import (
    getUserData, addFile, removeFile, getFileData, addDownloadTransaction,
    incrementDownloadCount, getFileStatistics, createUser, removeUser,
    removeFileHistory
)
from database_utils import (
    setupDatabase, createAnonUser
)
from bcrypt import hashpw, checkpw, gensalt
from config import getConfig
from logging.config import dictConfig


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
                "filename": "server.log",
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


@app.route("/")
def home():
    """ The login page users have to use to login to the app """

    if config['loginRequired']:
        return render_template("homepage.html")
    else:
        app.logger.info("Anonymous user logged in.")
        session['username'] = "Anonymous"
        session['privilege'] = "3"
        session['user_id'] = "-1"
        return redirect(url_for('dashboard'))


@app.route("/login", methods=["POST"])
def login():
    """ The api correlating to the logging in to the user."""

    username = request.form['username']
    password = request.form['password'].encode("UTF-8")

    user = getUserData(db_conn, username, "")

    # If the user does not exist, redirect to homepage
    if not user:
        return render_template("homepage.html")

    user = user[0]

    if not checkpw(password, user['PassHash'].encode("UTF-8")):
        app.logger.info(f"User '{username}' login failed.")
        return render_template("homepage.html")

    session["username"] = user['Username']
    session["privilege"] = str(user['Privilege'])
    session["user_id"] = str(user["ID"])

    return redirect(url_for('dashboard'))


@app.route("/dashboard")
def dashboard():
    """ This is the page for whom who successfully login. """

    username = session.get("username")
    privilege = session.get("privilege")

    # Cannot login with the anonymous account if login is needed
    if username == "Anonymous" and config["loginRequired"]:
        app.logger.warning(
            "Anonymous passed login but failed dashboard check."
        )
        return redirect(url_for('home'))

    match privilege:
        case "1":
            app.logger.info(f"Admin '{username}' has successfully logged in.")
            return render_template("adminpage.html")
        case "2":
            app.logger.info(
                f"Uploader '{username}' has successfully logged in."
            )
            return render_template("uploadpage.html")
        case "3":
            app.logger.info(f"Viewer '{username}' has successfully logged in.")
            return render_template("loginpage.html", username=username)
        case _:
            app.logger.warning(
                f"User '{username}' has tried to login with unknown privilege."
            )
            return redirect(url_for('home'))


@app.route('/api/file/upload', methods=["POST"])
def uploadFile():
    """ Api route to upload a file, needs to be sent through post
    form data.
    """

    username = session.get("username")
    privilege = session.get("privilege")

    if (privilege != "1" and privilege != "2"):
        app.logger.warning(
            f"User '{username}' has tried to upload a file without the correct"
            " permissions.")
        return "You need to be an admin or an uploader to upload files"

    filename = request.form["filename"]
    file = request.files["file"]
    file.save(f"shared_files/{filename}")
    addFile(db_conn, filename)

    app.logger.info(f"User {username} has added a new file: '{filename}'.")
    return "The file has been successfully added"


@app.route('/api/file/delete', methods=["POST"])
def deleteFile():
    """ Api route to delete a file, needs to be sent through post
    form data.
    """

    username = session.get("username")
    privilege = session.get("privilege")

    if (privilege != "1" and privilege != "2"):
        app.logger.warning(
            f"User '{username}' has tried to delete a file without the correct"
            " permissions.")
        return "You need to be an admin or an uploader to upload files"

    filename = request.form["filename"]
    removeFileHistory(db_conn, filename)
    removeFile(db_conn, filename)

    app.logger.info(f"User {username} has delete a new file: '{filename}'.")
    return "The file has been successfully deleted"


@app.route("/api/file/<filename>", methods=["GET"])
def getFile(filename):
    """ Api route to get file data. """

    columns = request.args.to_dict(flat=False)['cols']
    if filename == "all":
        filename = ""

    app.logger.debug(
        f"File information for '{filename or "*"}' is being retrieved."
    )
    return getFileData(db_conn, filename, *columns)


@app.route("/api/download/<filename>", methods=["GET"])
def downloadFile(filename: str):
    """ Api route to download a file. """

    response = make_response(send_from_directory("../shared_files", filename))

    # Ensuring that files download automatically and not open in browser.
    response.headers["Content-Disposition"] = "attachment"

    file = getFileData(db_conn, filename)
    username = session.get("username")
    userID = session.get("user_id")

    addDownloadTransaction(db_conn, userID, file[0]['ID'])
    incrementDownloadCount(db_conn, filename)

    app.logger.info(f"User {username} has downloaded {filename}.")
    return response


@app.route("/api/file/stats", methods=["POST"])
def getFileStats():
    """ Api route to retrieve file download history.  """

    app.logger.debug(
        f"File statistics for '{request.form['filename']}' retrieved."
    )
    return getFileStatistics(db_conn, request.form['filename'])


@app.route("/api/user/create", methods=["POST"])
def addUser():
    """ Api route to create a new user, admins can only create new users """
    privilege = session.get("privilege")
    username = session.get("username")

    if (privilege != "1"):
        app.logger.warning(
            f"User '{username}' has tried to add a new user without the"
            " correct permissions."
        )
        return "You need to be an admin to create new users"

    newUsername = request.form["username"]
    newPassword = request.form["passhash"].encode("UTF-8")
    newPassHash = hashpw(newPassword, gensalt()).decode("UTF-8")
    newPrivilege = request.form["privilege"]

    createUser(db_conn, newUsername, newPassHash, newPrivilege)
    app.logger.info(
        f"New user '{newUsername}' has been created by '{username}'."
    )
    return "The new user has been created"


@app.route("/api/user/delete", methods=["POST"])
def deleteUser():
    """ Api route to delete a user from the database """

    privilege = session.get("privilege")
    usern = session.get("username")

    if (privilege != "1"):
        app.logger.warning(
            f"User '{usern}' has tried to delete a user without the"
            " correct permissions."
        )
        return "You need to be admin to remove new users"

    username = request.form["username"]
    removeUser(db_conn, username)

    app.logger.info(f"User '{username}' has been deleted by user '{usern}'.")
    return "The user has been deleted"


@app.route("/api/user/search/<username>")
def getUser(username: str):
    """ Retrieves information about a user """
    if username == "all":
        username = ""

    columns = request.args.to_dict(flat=False)['cols']

    app.logger.debug(f"User data for '{username or "*"}' has been retrieved.")
    return getUserData(db_conn, username, "", *columns)


def main():
    app.debug = True

    if not config['loginRequired']:
        app.logger.info("Anonymous user has been created.")
        createAnonUser(db_conn)

    app.logger.info("="*50)
    app.logger.info("Starting app...")
    app.run()


if __name__ == "__main__":
    main()
