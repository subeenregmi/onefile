function displayFileStats() {
    let container = document.getElementById("files")
    fetch ("http://localhost:5000/api/file/all?cols=FileName&cols=DownloadCount")
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

document.addEventListener('DOMContentLoaded', displayFileStats);

function displayUsers(){
    let container = document.getElementById("users");
    fetch ("http://localhost:5000/api/user/search/all?cols=Username&cols=ID")
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

document.addEventListener('DOMContentLoaded', displayUsers);
