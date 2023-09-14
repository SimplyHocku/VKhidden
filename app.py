# -*- coding: utf-8 -*-
from fastapi import Request
from vkapi import app, TOKEN
from models import KeyResponse, UserIdResponse
from database import _get_keys
from fastapi.responses import RedirectResponse, HTMLResponse
from vkapi import get_jinja_render, get_dialogs_html, _get_full_dialog, templates


@app.get("/")
async def home(request: Request):
    global TOKEN
    if TOKEN:
        return RedirectResponse("/main")
    return templates.TemplateResponse("login.html", {"request": request})


async def get_html(keys):
    pattern = """
<div class="table_with_key" id="key_obj" onclick="loginSend()">
    {% for key, value in keys.items() %}
        <div class="key_block">
            <p class="key_id">{{key}}</p>
            <p class="key_value">{{value}}</p>
        </div>
    {% endfor %}
</div>
    """
    environment = get_jinja_render()
    template = environment.from_string(pattern)
    html = {"html": template.render(keys=keys)}

    return html


@app.post("/get_full_dialog")
async def get_full_dialog(user_id: UserIdResponse):
    cur_id = user_id.model_dump()["id"]
    print(cur_id)
    html = {"html": await _get_full_dialog(cur_id)}
    return html


@app.post("/get_keys")
async def get_keys():
    keys = await _get_keys()
    return await get_html(keys)


@app.post("/login")
async def login(key: KeyResponse):
    global TOKEN
    if TOKEN:
        print("Token", TOKEN)
    key = key.model_dump()
    TOKEN = key["key"]
    return 200


@app.post("/is_login")
async def check_login():
    return "200" if TOKEN else "400"


@app.get("/main")
async def main(request: Request):
    if TOKEN:
        a = await get_dialogs_html()
        return templates.TemplateResponse("all_dialogs.html", {"request": request, "data": a})


@app.get("/main/{dialog_id}")
async def get_dialog_by_id(request: Request, dialog_id):
    a = await _get_full_dialog(dialog_id)
    return templates.TemplateResponse("dialog_html.html", {"request": request, "data": a})
