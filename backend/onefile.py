from flask import (
    Flask, render_template, request, send_from_directory, make_response,
    redirect, url_for
)
from onefile_db import (
    setupDatabase, checkUser, setupTestUsers, initialiseFiles, getAllFileNames,
    incrementDownloadCount, getUserPrivilege, getAllFileData, addFile,
    removeFile, getUserID, addDownloadTransaction
)

app = Flask(__name__,
            template_folder="../templates/",
            static_folder="../static/",
            )
db_con = setupDatabase("onefile.db")


@app.route("/")
def home():
    return render_template("homepage.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']

    if checkUser(db_con, username, password):
        userPrivilege = getUserPrivilege(db_con, username)
        userID = getUserID(db_con, username)
        print(userID)

        response = redirect(url_for('dashboard'))
        response.set_cookie("username", username)
        response.set_cookie("privilege", userPrivilege)

        return response

    return render_template("homepage.html")


@app.route("/dashboard")
def dashboard():
    username = request.cookies.get("username")
    privilege = request.cookies.get("privilege")
    print(privilege)

    match privilege:
        case "Admin":
            return render_template("adminpage.html")
        case "Uploader":
            return render_template("uploadpage.html")
        case None:
            return redirect(url_for('home'))
        case _:

            return render_template("loginpage.html", username=username)


@app.route('/api/uploadFile', methods=["POST"])
def uploadFile():
    privilege = request.cookies.get("privilege")

    if (privilege != "Admin" and privilege != "Uploader"):
        return "You need to be an admin or an uploader to upload files"

    filename = request.form["filename"]
    file = request.files["file"]
    file.save(f"shared_files/{filename}")
    addFile(db_con, filename)

    return "The file has been successfully added"


@app.route('/api/deleteFile', methods=["POST"])
def deleteFile():
    privilege = request.cookies.get("privilege")

    if (privilege != "Admin" and privilege != "Uploader"):
        return "You need to be an admin or an uploader to upload files"

    filename = request.form["filename"]
    removeFile(db_con, filename)
    return "The File has been successfully deleted"


@app.route("/api/filenames", methods=["GET"])
def getFileNames():
    fileNames = getAllFileNames(db_con)
    return [x[0] for x in fileNames]


@app.route("/api/download/<filename>", methods=["GET"])
def downloadFile(filename):
    response = make_response(send_from_directory("shared_files", filename))
    response.headers["Content-Disposition"] = "attachment"
    incrementDownloadCount(db_con, filename)

    print(
        db_con.execute("SELECT FileName, DownloadCount FROM Files;").fetchall()
    )
    return response


@app.route("/api/file/all", methods=["GET"])
def allFileData():
    return getAllFileData(db_con)


if __name__ == "__main__":
    app.debug = True
    # print(db_con.execute("SELECT * FROM sqlite_master").fetchall())
    setupTestUsers(db_con)
    initialiseFiles(db_con)
    print(getAllFileData(db_con))
    app.run()
