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
            let ul = document.createElement("ul")
            container.appendChild(ul)
            for(let x=0; x<data.length; x++){
                let file = data[x];
                let li = document.createElement("li");
                let fileAnchor = document.createElement('a');
                fileAnchor.href = (`/api/download/${file['FileName']}`);
                fileAnchor.innerHTML = file['FileName'];
                li.appendChild(fileAnchor);
                const hashP = async () => {
                    let hash = await getHash(file['FileName'], host)
                    let paragraph = document.createElement("p");
                    paragraph.innerText = "Hash: " + hash;
                    li.appendChild(paragraph);
                }
                hashP();
                ul.appendChild(li);
            }
        })
        .catch(error => {
            console.error(error);
        })
}

async function getHash(filename, host) {
    let hashP = await fetch('http://' + host + ':5000/api/file/hash/' + filename);
    let hash = hashP.text();
    return hash;

}
