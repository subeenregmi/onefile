import Chart from "chart.js/auto";

const fileAPI           = "api/file/data";
const fileStatsAPI      = "api/file/downloadhistory";
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
    console.log(files);

    await createDownloadSummary(files);

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

    console.log(users);

    await createUsersSummary(users);

    let pageViewTransactions = await fetch(`http://${host}/${pageViewTransAPI}`)
}


quickSummary("192.168.0.200:5000");

   

