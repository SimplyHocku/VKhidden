function checkElement(element) {
    if (element) {
        return true
    }
    else {
        return false
    }
}

async function getFullDialogSend(object) {
    window.location.href = `http://localhost:8080/main/${object.id}`

}

async function getFullDialog(object) {
    let parent = document.getElementById("all_content")

    let response = await fetch("http://localhost:8080/get_full_dialog", {
        "method": "POST",
        "mode": "cors",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": JSON.stringify({ "id": object.id })
    })
    if (response.ok) {
        let html = await response.json();
        parent.innerHTML = html["html"]
        goToEnd()
    }
}



async function checkLogin() {
    response = await fetch("http://localhost:8080/is_login", {
        "method": "POST",
        "mode": "cors",
        "headers": {
            "Content-Type": "application/json"
        }
    })
    if (response.ok) {
        let code = await response.json()
        if (code == "400") {
            return false
        }

        else if (code == "200") {
            return true
        }
    }
}


function keyChange(object) {
    let parent = document.getElementById("all_content")
    let btn_log = document.getElementById("login_btn")

    let elem = document.createElement("input")
    elem.id = "login_btn"
    elem.type = "submit"
    elem.value = "Войти"

    if (object.value) {
        if (!btn_log) {
            elem.addEventListener("click", event => { loginSend(event) })
            parent.append(elem)
        }
    }
    else {
        btn_log.remove()
    }
}


async function loginSend() {
    let key
    let target = event.target
    let targetClassName = target.className
    if (targetClassName == "key_value") {
        key = target.innerText
    }
    else if (target.id == "login_btn") {
        key = document.getElementById("key_obj").value
    }

    else {
        return
    }
    let check = await checkLogin()
    if (check) {
        alert("Вход уже был выполнен")
        window.location.href = "http://localhost:8080/main"
    }
    else {

        let response = await fetch("http://localhost:8080/login", {
            "method": "POST",
            "mode": "cors",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": JSON.stringify({ "key": key })
        })


        if (response.status == 200) {
            window.location.href = "http://localhost:8080/redir"
            window.location.href = "http://localhost:8080/main"

        }
    }
}


async function checkRadio(object) {

    let exist_element = document.getElementById("key_obj")
    if (checkElement(exist_element)) {
        let p = exist_element.parentElement.parentElement
        let pr = exist_element.parentElement
        p.removeChild(pr)

    }
    let elem = document.createElement("div")
    let main_div = document.getElementById("all_content")
    let parent_name = object.parentNode.className



    if (parent_name == "left_form_div") {
        elem.innerHTML = '<input type="text" placeholder="VkKey" id="key_obj" oninput="keyChange(this)">'
    }

    else if (parent_name == "right_form_div") {
        let response = await fetch("http://localhost:8080/get_keys", {
            "method": "POST",
            "mode": "cors",
            "headers": {
                "Content-Type": "application/json"
            },
        })
        if (response.ok) {
            let html = await response.json();
            elem.innerHTML = html["html"]
        }
    }

    main_div.append(elem)

}

async function selectMessage(object) {
    console.log(object)
}

async function sendMessage(object) {
    if (event.key ==="Enter") {
        console.log(object)
    }
}