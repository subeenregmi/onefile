const hashAPI = "api/file/hash";
const fileAPI = "api/file";
const downloadFileAPI = "api/download"

class OneFile {
    constructor(name, hash, downloadLink, downloadCount, uploadDate) {
        this.name = name;
        this.hash = hash;
        this.downloadLink = downloadLink;
        this.downloadCount = downloadCount;
        this.uploadDate = uploadDate;
    }
}


async function initialiseFiles(host) {
    let oneFilesList = [];
    try {
        let files = await fetch(`http://${host}/${fileAPI}/all?cols=all`);
        files = await files.json();

        for (let i = 0; i < files.length; i++) {
            let file = files[i];
            let newFile = new OneFile(
                file["FileName"],
                await fetch(`http://${host}/${hashAPI}/${file["FileName"]}`),
                `http://${host}/${downloadFileAPI}/${file["FileName"]}`,
                file["DownloadCount"],
                file["UploadDate"]
            )
            oneFilesList.push(newFile); 
        }
        return oneFilesList;
    }
    catch (err) {
        console.log(err);
    }
}

function createIcon(host, file) {
    let container = document.createElement("div");
    let a = document.createElement("a");
    let image = document.createElement("img");
    let paragraph = document.createElement("p");

    container.classList.add("file-container");
    let fileExtension = file.name.split(".").at(-1);
    image.src = `http://${host}/static/images/${fileExtension}_file_icon.png`;
    paragraph.innerHTML = file.name;
    a.href = file.downloadLink;

    a.appendChild(image);
    a.appendChild(paragraph);
    container.appendChild(a);

    return container;
}

async function displayFiles(host) {
    let oneFilesList = await initialiseFiles(host);
    let container = document.getElementById("files");
    for (let i = 0; i < oneFilesList.length; i++) {
        let fileIcon = createIcon(host, oneFilesList[i]);
        container.appendChild(fileIcon);
    }
}

displayFiles("192.168.0.200:5000");


