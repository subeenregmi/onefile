import Chart from "chart.js/auto";

const fileAPI           = "api/file/data";
const fileStatsAPI      = "api/file/downloadhistory";
const uploadFileAPI     = "api/file/upload";
const deleteFileAPI     = "api/file/delete";
const addUserAPI        = "api/user/create";
const deleteUserAPI     = "api/user/delete";
const userAPI           = "api/user/search";
const pageViewTransAPI  = "api/pages/history";
const pageViewsAPI      = "api/pages/search";


async function createDownloadSummary(files) {
    
    new Chart (
        document.getElementById("chart1"),
        {
            type: 'bar',
            data: {
                labels: files.map(file => file.FileName),
                datasets: [
                    {
                        label: "Download Summary",
                        data: files.map(file => file.DownloadCount),
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.2)',
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                        ],
                        borderWidth: 1,
                    }
                ]
            },
        }
    )
}

async function createPageViewStats(pageViews) {
    let table = document.getElementById("pageviews-sum");
    let tableRow = document.createElement("tr");
    
    let headings = ["Page", "View count"];
    for (let i = 0; i < headings.length; i++) {
        let tableHeading = document.createElement("th");
        tableHeading.innerHTML = headings[i];
        tableRow.appendChild(tableHeading);
    }
    table.appendChild(tableRow);

    for (let i = 0; i < pageViews.length; i++) {
        let tr = document.createElement("tr");

        let td = document.createElement("td");
        td.innerHTML = pageViews[i].Name;

        let td2 = document.createElement("td");
        td2.innerHTML = pageViews[i].ViewCount;

        tr.appendChild(td);
        tr.appendChild(td2);
        table.appendChild(tr);
    }
}

async function createUsersSummary(users) {
    let table = document.getElementById("users-sum");
    let tableRow = document.createElement("tr");
    
    let headings = ["Username", "Privilege"];
    for (let i = 0; i < headings.length; i++) {
        let tableHeading = document.createElement("th");
        tableHeading.innerHTML = headings[i];
        tableRow.appendChild(tableHeading);
    }

    table.appendChild(tableRow);

    for (let i = 0; i < users.length; i++) {
        let tr = document.createElement("tr");

        let td = document.createElement("td");
        td.innerHTML = users[i].Username;

        let td2 = document.createElement("td");
        td2.innerHTML = translatePrivilege(users[i].Privilege);

        tr.appendChild(td);
        tr.appendChild(td2);
        table.appendChild(tr);
    }
}

async function createRecentViews(views) {
    let table = document.getElementById("views-sum");
    let tableRow = document.createElement("tr");
    
    let headings = ["ID", "IP", "Page", "Timestamp", "User"];
    for (let i = 0; i < headings.length; i++) {
        let tableHeading = document.createElement("th");
        tableHeading.innerHTML = headings[i];
        tableRow.appendChild(tableHeading);
    }

    table.appendChild(tableRow);

    for (let i = 0; i < 50; i++) {
        let tr = document.createElement("tr");

        let td = document.createElement("td");
        td.innerHTML = views[i].ID;
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = views[i].IpAddress;
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = views[i].PageID;
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = views[i].Timestamp;
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = views[i].UserID;
        tr.appendChild(td);

        table.appendChild(tr);
    }

}

function translatePrivilege(num){
    switch (num) {
        case 1:
            return "Admin";
        case 2:
            return "Uploader";
        case 3:
            return "User";
        default:
            return "Anon";
    }
}

async function deleteFile(host, fname) {
    let resp = await fetch(`http://${host}/${deleteFileAPI}`, {
        method: "POST" ,
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            filename: fname
        })
    });
    let respj = await resp.json();
    await popup(respj);
}


async function createFilesTable(host, files) {
    let table = document.getElementById("file-table-id");

    for (let i = 0; i < files.length; i++) {
        let tr = document.createElement("tr");

        let td = document.createElement("td");
        td.innerHTML = files[i].ID;
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = files[i].FileName;
        td.classList.add("delete-file");
        td.onclick = (() => {
            deleteFile(host, files[i].FileName);
        })
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = files[i].DownloadCount;
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = files[i].UploadDate;
        tr.appendChild(td);

        table.appendChild(tr);
    }
}

async function createUsersTable(host, users) {
    let table = document.getElementById("users-table-id");

    for (let i = 0; i < users.length; i++) {
        let tr = document.createElement("tr");

        let td = document.createElement("td");
        td.innerHTML = users[i].ID;
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = users[i].Username;
        td.classList.add("delete-file");
        td.onclick = (() => {
            deleteUserFromName(host, users[i].Username);
        })
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = translatePrivilege(users[i].Privilege);
        tr.appendChild(td);

        table.appendChild(tr);
    }
}


async function quickSummary(host) {

    let files = await fetch(`http://${host}/${fileAPI}?cols=all`, {
        method: "POST", 
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            filename: "all"
        })
    });
    files = await files.json();

    await createDownloadSummary(files);
    await createFilesTable(host, files);

    let pageViews = await fetch(`http://${host}/${pageViewsAPI}?cols=all`, {
        method: "POST", 
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            pagename: "all"
        })
    });
    pageViews = await pageViews.json();

    await createPageViewStats(pageViews);

    let users = await fetch(`http://${host}/${userAPI}?cols=all`, {
        method: "POST", 
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: "all"
        })
    });
    users = await users.json();

    await createUsersSummary(users);
    await createUsersTable(host, users);

    let pageViewTransactions = await fetch(
        `http://${host}/${pageViewTransAPI}?order=desc`, 
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                pagename: "all"
            })
        }
    );

    pageViewTransactions = await pageViewTransactions.json();

    await createViewTransactionsTable(pageViewTransactions, pageViews, users);
    await createRecentViews(pageViewTransactions);

    let fileDLHistory = await fetch(
        `http://${host}/${fileStatsAPI}`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                filename: "all"
            })
        }
    )
    fileDLHistory = await fileDLHistory.json();
    await createFileDownloadHistoryTable(fileDLHistory, files, users);
}

function createFileDownloadHistoryTable(fileDLHistory, files, users) { 
    let table = document.getElementById("download-history-table-id");

    for (let i = 0; i < fileDLHistory.length; i++) {
        let tr = document.createElement("tr");

        let td = document.createElement("td");
        if (fileDLHistory[i].FileID) {
            for (let j = 0; j < files.length; j++) {
                if (files[j].ID == fileDLHistory[i].FileID) {
                    td.innerHTML = files[j].FileName;
                }
            }
        }
        else {
            td.innerHTML = "Unknown file";
        }

        tr.appendChild(td);

        td = document.createElement("td");
        if (fileDLHistory[i].UserID) {
            td.innerHTML = users[fileDLHistory[i].UserID - 1].Username;
        }
        else {
            td.innerHTML = "Unknown user"
        }
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = fileDLHistory[i].Timestamp;
        tr.appendChild(td);


        table.appendChild(tr);
    }
    

}

function createViewTransactionsTable(views, pages, users) {
    let table = document.getElementById("view-table-id");

    for (let i = 0; i < views.length; i++) {
        let tr = document.createElement("tr");

        let td = document.createElement("td");
        td.innerHTML = views[i].ID;
        tr.appendChild(td);

        td = document.createElement("td");
        if (views[i].UserID){
            td.innerHTML = users[views[i].UserID - 1].Username
        }
        else{
            td.innerHTML = views[i].UserID;
        }
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = views[i].IpAddress;
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = pages[views[i].PageID - 1].Name;
        tr.appendChild(td);

        td = document.createElement("td");
        td.innerHTML = views[i].Timestamp;
        tr.appendChild(td);

        table.appendChild(tr);
    }
}


async function createNewUser(host, form) {
    let formData = new FormData(form);

    let resp = await fetch (
        `http://${host}/${addUserAPI}`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "username":`${formData.get("new-username")}`,
                "password":`${formData.get("new-password")}`,
                "privilege": Number(formData.get("new-privilege")),
            })
        }
    );
    let respj = await resp.json();
    await popup(respj);
}

async function deleteUser(host, form) {
    let formData = new FormData(form);

    let resp = await fetch(
        `http://${host}/${deleteUserAPI}`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "username": formData.get("username")
            })
        }
    )
    let respj = await resp.json();
    await popup(respj);
}

async function deleteUserFromName(host, username) {
    let resp = await fetch(
        `http://${host}/${deleteUserAPI}`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "username": username
            })
        }
    )
    let respj = await resp.json();
    await popup(respj);
}

async function uploadFile(host, form) {
    let formData = new FormData(form);
    let file = document.getElementById("file-upload-input").files[0];
    formData.append("file", file);

    let resp = await fetch(
        `http://${host}/${uploadFileAPI}`,
        {
            method: "POST",
            body: formData
        }
    )
    let respj = await resp.json();
    await popup(respj);
}

async function popup(response) {
    let container = document.getElementById("response-bubble");
    container.style.backgroundColor = "red";
    switch (response.RESP_CODE){
        case "SUCCESS":
            container.style.backgroundColor = "green";
            container.innerText = "Success!";
            break;
        case "USER_NOT_FOUND":
            container.innerText = "The user you have entered does not exist.";
            break;
        case "EMPTY_NAME":
            container.innerText = "The file name specified is not filled out."
            break;
        case "PRIVILEGE_ERROR":
            container.innerText = "Your account does not hold the required privileges to send out this request.";
            break;
        case "TAKEN_FILE_NAME":
            container.innerText = "The file name you specified has already been taken, try another name.";
            break;
        case "FILE_NOT_EXISTS":
            container.innerText = "The file you specified does not exist, try again.";
            break;
        case "EMPTY_USERNAME":
            container.innerText = "The username is not specified, enter a username.";
            break;
        case "TAKEN_USERNAME":
            container.innerText = "The username specified has already been taken, try again.";
            break;
        case "EMPTY_PASSWORD":
            container.innerText = "The password field was left empty, try again.";
            break;
        case "UNSPECIFIED_PRIVILEGE":
            container.innerText = "The privilege field was left empty, try again.";
            break;
        case "EMPTY_PAGE_NAME":
            container.innerText = "The page field was left empty, try again.";
            break;
        case "PAGE_NOT_FOUND":
            container.innerText = "The page specified does not exist.";
            break;
        case "PARAMETER_ERROR":
            container.innerText = "The parameters specified is not valid, try again.";
            break;
        case "FILE_NOT_UPLOADED":
            container.innerText = "The file provided is not valid, try again.";
            break;
        default:
            container.innerText = response.RESP_CODE; 
            break;
    }
    container.style.opacity = 1;
    setTimeout(() => {
        container.style.opacity = 0;
    }, 2500)
        
}

function makeViewsHidden() {
    let divs = document.getElementsByClassName("page");
    for (let i = 0; i<divs.length; i++) {
        divs[i].style.display = "none";
    }
}

function viewPage(host, pagename) {
    makeViewsHidden();
    let view = document.getElementById(pagename);
    view.style.display = "block";
}

function init(host) {
    document.getElementById("create-user-form").addEventListener("submit", function (e) {
        e.preventDefault();
        createNewUser(host, e.target);
    });
    document.getElementById("delete-user-form").addEventListener("submit", function (e) {
        e.preventDefault();
        deleteUser(host, e.target);
    });
    document.getElementById("upload-file-form-id").addEventListener("submit", function (e) {
        e.preventDefault();
        uploadFile(host, e.target);
    });
    
    let pages = ["home-page", "file-page", "users-page", "stats-page", 
        "settings-page"];
    let buttons = Array.from(document.getElementsByClassName("nav-button"));
    buttons = buttons.filter((button) => button.id != "logout-button");
    for (let i = 0; i<buttons.length; i++) {
        buttons[i].addEventListener("click", function (e) {
            e.preventDefault();
            viewPage(host, pages[i]);
        })
    }
}

window.quickSummary = quickSummary;
window.initform = init;
