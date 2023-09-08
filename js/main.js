function checkElement(element) {
    if (element) {
        return true
    }
    else {
        return false
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
        elem.innerHTML = '<input type="text" placeholder="VkKey" id="key_obj">'
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