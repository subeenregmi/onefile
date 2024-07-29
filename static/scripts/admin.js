function displayFileStats() {
    let container = document.getElementById("files")
    fetch ("http://localhost:5000/api/file/all")
        .then (response => {
            if (response.ok) {
                return response.json();
            }
            else {
                throw new Error("API request failed");
            }
        })
        .then (data => {
            for (let key in data) {
                let paragraph = document.createElement("p");
                paragraph.innerText = key + ": " + data[key];
                container.appendChild(paragraph);
            }
        })
        .catch (error => {
           console.error(error);
        })
}

document.addEventListener('DOMContentLoaded', displayFileStats);

