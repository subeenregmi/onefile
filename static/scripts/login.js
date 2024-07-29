function createDownloadLinks() {
    let container = document.getElementById("files");
    fetch('http://localhost:5000/api/filenames')
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            else {
                throw new Error('API request failed');
            }
        })
        .then(data => {
            for(let x=0; x<data.length; x++){
                let fileName = data[x];
                let fileAnchor = document.createElement('a');
                fileAnchor.href = (`/api/download/${fileName}`);
                fileAnchor.innerHTML = fileName;
                container.appendChild(fileAnchor);
            }
        })
        .catch(error => {
            console.error(error);
        })
}

document.addEventListener('DOMContentLoaded', createDownloadLinks)
