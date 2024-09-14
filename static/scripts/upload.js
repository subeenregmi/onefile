const hashAPI = "api/file/hash";
const fileAPI = "api/file/data";
const downloadFileAPI = "api/file/download"

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
        let files = await fetch(`http://${host}/${fileAPI}?cols=all`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    filename: "all"
                }),
            });
        files = await files.json();

        for (let i = 0; i < files.length; i++) {
            let file = files[i];
            let newFile = new OneFile(
                file["FileName"],
                await fetch(`http://${host}/${hashAPI}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        filename: file["FileName"] 
                    }),
                }),
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
    if (fileExtension == undefined) {
        fileExtension = "txt";
    }
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

async function uploadFile(host, form) {
    const uploadFileAPI = "api/file/upload";

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

window.init = init;

function init(host) {
    document.getElementById("upload-file-form-id").addEventListener("submit", function (e) {
            e.preventDefault();
            uploadFile(host, e.target);
        });
    displayFiles(host);
}
