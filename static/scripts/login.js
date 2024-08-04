function createDownloadLinks(host) {
    let container = document.getElementById("files");
    fetch('http://' + host + ':5000/api/file/all?cols=FileName')
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
                let file = data[x];
                let fileAnchor = document.createElement('a');
                fileAnchor.href = (`/api/download/${file['FileName']}`);
                fileAnchor.innerHTML = file['FileName'];
                container.appendChild(fileAnchor);
            }
        })
        .catch(error => {
            console.error(error);
        })
}
