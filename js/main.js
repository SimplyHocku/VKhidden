const PORT = 8080

function checkElement(element) {
    if (element) {
        return true
    }
    else {
        return false
    }
}

function getFullDialogSend(object) {
    console.log("send", object)

    window.location.href = `http://localhost:${PORT}/main/${object.id}`

}

async function getFullDialog(object) {
    let parent = document.getElementById("all_content")

    let response = await fetch(`http://localhost:${PORT}/get_full_dialog`, {
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
    response = await fetch(`http://localhost:${PORT}/is_login`, {
        "method": "POST",
        "mode": "cors",
        "headers": {
            "Content-Type": "application/json"
        }
    })
    if (response.ok) {
        let code = await response.json()
        if (code == 400) {
            return false
        }

        else if (code == 200) {
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
    elem.className="btn_login_style"

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
        window.location.href = `http://localhost:${PORT}/main`
    }
    else {
        let remember_checkbox = document.getElementById("remember_checkbox").checked
        let response = await fetch(`http://localhost:${PORT}/login`, {
            "method": "POST",
            "mode": "cors",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": JSON.stringify({ "key": key, "remember": remember_checkbox })
        })


        if (response.ok) {
            let code = await response.json()
            if (code["status_code"] == "200") {
                window.location.href = `http://localhost:${PORT}/main`
            }
            else {
                alert("Введенный токен недействительный")
            }

        }
    }
}


async function loginRememberSend(object) {
    let check = await checkLogin()
    if (check) {
        alert("Вход уже был выполнен")
        window.location.href = `http://localhost:${PORT}/main`
    }
    else {
        let key = object.innerText
        let response = await fetch(`http://localhost:${PORT}/login`, {
            "method": "POST",
            "mode": "cors",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": JSON.stringify({ "key": key })
        })


        if (response.ok) {
            let code = await response.json()
            if (code["status_code"] == "200") {
                window.location.href = `http://localhost:${PORT}/main`
            }

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
        elem.innerHTML = '<input class="vk_key_input" type="text" placeholder="VkKey" id="key_obj" oninput="keyChange(this)"><input type="checkbox" id="remember_checkbox"><label for="remember_checkbox">Запомнить</label>'
    }

    else if (parent_name == "right_form_div") {
        let response = await fetch(`http://localhost:${PORT}/get_keys`, {
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
    let decrypt_btn = document.getElementById("decrypt_btn")
    window.message_id_box = object.id
    if (event.target.className == "content") {
        if (window.key_exists == 200) {
            decrypt_btn.disabled = false
        }
    }

    else {
        decrypt_btn.disabled = true
    }


}

function checkIsMessage(object) {
    let decrypt_btn = document.getElementById("decrypt_btn")
    if (event.target.className != "content") {
        decrypt_btn.disabled = true
    }
}

async function sendMessage(object) {
    let crypto_box = document.getElementById("crypt_checkbox").checked
    let msg_text_field = document.getElementById("msg_text_filed")


    if (event.key === "Enter" || event.target.id == "send_msg_btn") {
        let msg_text = msg_text_field.value
        let user_id = window.location.href.split("/")
        let response = await fetch(`http://localhost:${PORT}/send_message`, {
            "method": "POST",
            "mode": "cors",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": JSON.stringify({ "msg_text": msg_text, "crypt": crypto_box, "user_id": Number(user_id[user_id.length - 1]) })

        })

        if (response.ok) {
            let key_exists = await response.json()
            if (key_exists["status_code"] == 200) {
                window.location.reload()
            }

        }

    }
}

async function createKey(object) {
    key_title = prompt("Название для ключа?")

    let response = await fetch(`http://localhost:${PORT}/create_key`, {
        "method": "POST",
        "mode": "cors",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": JSON.stringify({ "key_name": key_title })
    })

    if (response.status == 200) {

    }
}

async function decryptMessage() {
    let msg_text = document.getElementById(window.message_id_box).children[1].children[1].innerText

    let response = await fetch(`http://localhost:${PORT}/decrypt_message`, {
        "method": "POST",
        "mode": "cors",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": JSON.stringify({ "msg": msg_text })

    })

    if (response.ok) {
        let decrypted_msg = await response.json()
        msg_text = decrypted_msg["decrypted_msg"]
        if (msg_text == 400) {
            return
        }
        document.getElementById(window.message_id_box).children[1].children[1].innerText = msg_text

    }

}


async function exitVK(object) {
    let response = await fetch(`http://localhost:${PORT}/exit_vk`, {
        "method": "POST",
        "mode": "cors",
        "headers": {
            "Content-Type": "application/json"
        }
    })

    if (response.ok) {
        let decrypted_msg = await response.json()
        msg_text = decrypted_msg["decrypted_msg"]
        if (msg_text == 400) {
            return
        }
        else {
            window.location.href = `http://localhost:${PORT}/`
        }
    }
}


async function sendChangePerm(object) {
    let elements_child = object.parentElement.children
    let host = elements_child[0].innerText
    let alias = elements_child[1].innerText
    let allow = Boolean(elements_child[2].value)

    let response = await fetch(`http://localhost:${PORT}/permission_changed`, {
        "method": "POST",
        "mode": "cors",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": JSON.stringify({ "host": host, "alias": alias, "allow": allow })
    })
}

function scroolToEnd() {
    let end = document.getElementById("end")
    console.log(end)
    end.scrollIntoView()
}

async function loadForDialogTemplate() {
    // let end = document.getElementById("end")
    // console.log(end)
    // end.scrollIntoView()

    let response = await fetch(`http://localhost:${PORT}/key_exists`, {
        "method": "POST",
        "mode": "cors",
        "headers": {
            "Content-Type": "application/json"
        }
    },)

    if (response.ok) {
        let key_exists = await response.text()
        window.key_exists = Number(key_exists)
        if (Number(key_exists) == 400) {
            alert("Для расшифровки сообщении необходимо создать ключ шифрования")
        }

    }
}

async function loadForAwaitTemplate() {
    let userAlias = prompt("Какой у вас будет логин?")

    let host = window.location.href.split("/")[2]
    let response = await fetch(`https://${host}:${PORT}/allowed`, {
        "method": "POST",
        "mode": "cors",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": JSON.stringify({ "guest_alias": userAlias })
    })

    if (response.ok) {
        let guest = await response.json();
        let redirect = window.location.href + `get_secret_key/${guest["client_host"]}/${guest["alias"]}`
        if (guest["allow"]) {

            let key_reponse = await fetch(`https://${host}/get_secret_key`, {
                "method": "POST",
                "mode": "cors",
                "headers": {
                    "Content-Type": "application/json"
                },

            })

            if (key_reponse.ok) {
                let key = await key_reponse.json()
                document.body.innerHTML = `<h1>${key["key"]}</h1>`
            }
        }
    }
}

