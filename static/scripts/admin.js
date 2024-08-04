function displayFileStats(host) {
    let container = document.getElementById("files")
    fetch ("http://" + host + ":5000/api/file/all?cols=FileName&cols=DownloadCount")
        .then (response => {
            if (response.ok) {
                return response.json();
            }
            else {
                throw new Error("API request failed");
            }
        })
        .then (data => {
            console.log(data);
            console.log(data[0]);
            for (let file in data) {
                let paragraph = document.createElement("p");
                paragraph.innerText = data[file]['FileName'] + ": " + data[file]['DownloadCount'];
                container.appendChild(paragraph);
            }
        })
        .catch (error => {
           console.error(error);
        })
}


function displayUsers(host){
    let container = document.getElementById("users");
    fetch ("http://" + host + ":5000/api/user/search/all?cols=Username&cols=ID")
        .then (response => {
            if (response.ok) {
                return response.json();
            }
            else {
                throw new Error("API request failed.");
            }
        })
        .then (data => {
            for (let user in data){
                let paragraph = document.createElement("p");
                paragraph.innerText = data[user]['ID'] + " " + data[user]['Username'];
                container.appendChild(paragraph);
            }
        })
        .catch (error => {
            console.error(error);
        })
}


function displayPageData(host) {
    let container = document.getElementById("page-data")
    fetch ("http://" + host + ":5000/api/pages/all?cols=Name&cols=ViewCount")
        .then (response => {
            if (response.ok) {
                return response.json();
            }
            else {
                throw new Error("API request failed");
            }
        })
        .then (data => {
            for (let page in data) {
                let paragraph = document.createElement("p");
                paragraph.innerText = data[page]['Name'] + ": " + data[page]['ViewCount'];
                container.appendChild(paragraph);
            }
        })
        .catch (error => {
           console.error(error);
        })
}
