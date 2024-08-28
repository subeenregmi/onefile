const loginAPI = "login";

async function login(host, form) {
    let formData = new FormData(form);
    //console.log(formData);
    let req = await fetch(
        `http://${host}:5000/${loginAPI}`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "username":`${formData.get("username")}`,
                "password":`${formData.get("password")}`,
            })
        }
    )
    if (req.status == 200) {
        window.location = `http://${host}:5000/dashboard`;
    }
}

function init(host) {
    document.getElementById("login-form").addEventListener("submit", function (e) {
        e.preventDefault();
        login(host, e.target);
    });
}
