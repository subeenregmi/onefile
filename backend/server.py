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
    setupDatabase
)
from bcrypt import hashpw, checkpw, gensalt


app = Flask(__name__,
            template_folder="../templates/",
            static_folder="../static/")
app.secret_key = (
    "7e6dac2a942ba1d025171d1d7d9b9719e003a6c85f599d8a1b0c2fa7d8899af1"
)

db_conn = setupDatabase("onefile.db")


@app.route("/")
def home():
    """ The login page users have to use to login to the app """

    return render_template("homepage.html")


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

    match privilege:
        case "1":
            return render_template("adminpage.html")
        case "2":
            return render_template("uploadpage.html")
        case "3":
            return render_template("loginpage.html", username=username)
        case _:
            return redirect(url_for('home'))


@app.route('/api/file/upload', methods=["POST"])
def uploadFile():
    """ Api route to upload a file, needs to be sent through post
    form data.
    """

    privilege = session.get("privilege")

    if (privilege != "1" and privilege != "2"):
        return "You need to be an admin or an uploader to upload files"

    filename = request.form["filename"]
    file = request.files["file"]
    file.save(f"shared_files/{filename}")
    addFile(db_conn, filename)

    return "The file has been successfully added"


@app.route('/api/file/delete', methods=["POST"])
def deleteFile():
    """ Api route to delete a file, needs to be sent through post
    form data.
    """

    privilege = session.get("privilege")

    if (privilege != "1" and privilege != "2"):
        return "You need to be an admin or an uploader to upload files"

    filename = request.form["filename"]
    removeFileHistory(db_conn, filename)
    removeFile(db_conn, filename)
    return "The file has been successfully deleted"


@app.route("/api/file/<filename>", methods=["GET"])
def getFile(filename):
    """ Api route to get file data. """

    columns = request.args.to_dict(flat=False)['cols']
    if filename == "all":
        filename = ""

    return getFileData(db_conn, filename, *columns)


@app.route("/api/download/<filename>", methods=["GET"])
def downloadFile(filename: str):
    """ Api route to download a file. """

    response = make_response(send_from_directory("../shared_files", filename))
    # Ensuring that files download automatically and not open in browser.
    response.headers["Content-Disposition"] = "attachment"

    file = getFileData(db_conn, filename)
    userID = session.get("user_id")

    addDownloadTransaction(db_conn, userID, file[0]['ID'])
    incrementDownloadCount(db_conn, filename)

    return response


@app.route("/api/file/stats", methods=["POST"])
def getFileStats():
    """ Api route to retrieve file download history.  """
    return getFileStatistics(db_conn, request.form['filename'])


@app.route("/api/user/create", methods=["POST"])
def addUser():
    """ Api route to create a new user, admins can only create new users """
    privilege = session.get("privilege")

    if (privilege != "1"):
        return "You need to be an admin to create new users"

    newUsername = request.form["username"]
    newPassword = request.form["passhash"].encode("UTF-8")
    newPassHash = hashpw(newPassword, gensalt()).decode("UTF-8")
    newPrivilege = request.form["privilege"]

    createUser(db_conn, newUsername, newPassHash, newPrivilege)
    return "The new user has been created"


@app.route("/api/user/delete", methods=["POST"])
def deleteUser():
    """ Api route to delete a user from the database """

    privilege = session.get("privilege")

    if (privilege != "1"):
        return "You need to be admin to remove new users"

    username = request.form["username"]
    removeUser(db_conn, username)
    return "The user has been deleted"


@app.route("/api/user/search/<username>")
def getUser(username: str):
    """ Retrieves information about a user """
    if username == "all":
        username = ""

    columns = request.args.to_dict(flat=False)['cols']

    return getUserData(db_conn, username, "", *columns)


if __name__ == "__main__":
    app.debug = True
    app.run()
