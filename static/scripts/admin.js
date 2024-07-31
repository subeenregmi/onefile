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
