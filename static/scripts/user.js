const oneFilesList = [];
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
    try {
        let files = await fetch(`http://${host}/${fileAPI}/all?cols=all`);
        files = await files.json();

        for (let i = 0; i < files.length; i++) {
            let file = files[i];
            let newFile = new OneFile(
                file["FileName"],
                0,
                `http://${host}/${downloadFileAPI}/${file["FileName"]}`,
                file["DownloadCount"],
                file["UploadDate"]
            )
            oneFilesList.push(newFile); 
        }
    }
    catch (err) {
        console.log(err);
    }
}

initialiseFiles("192.168.200:5000");
