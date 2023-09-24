# -*- coding: utf-8 -*-
import asyncio

import aiofiles
import fastapi.responses
import rsa
from cryptography.fernet import Fernet
from fastapi import Request, Response
from vkapi import app, TOKEN
from models import KeyResponse, UserIdResponse, MsgForEncrypt, SecretKey, Message, GuestModel
from database import _get_keys, _save_vk_token, _add_host_guest, _get_host_guest_allow, _get_guest_exist, \
    _get_all_guests_with_perm
from fastapi.responses import RedirectResponse, HTMLResponse
from vkapi import get_jinja_render, get_dialogs_html, _get_full_dialog, templates, _send_message
from vk_crypt import create_key, _check_key_exists, encrypt_message, _decrypt_message


# from vk_crypt import encrypt


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
            <p class="key_value" id="remember_key_id" onclick="loginRememberSend(this)">{{value}}</p>
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
    html = {"html": await _get_full_dialog(cur_id)}
    return html


@app.post("/get_keys")
async def get_keys():
    keys = await _get_keys()
    return await get_html(keys)


@app.post("/login")
async def login(params: KeyResponse):
    global TOKEN
    params = params.model_dump()
    TOKEN = params["key"]
    if params["remember"]:
        await _save_vk_token(params["key"])
    return 200


@app.post("/is_login")
async def check_login(response: Response):
    code = 200
    if not TOKEN:
        code = 400

    return {"status_code": code}


@app.post("/key_exists")
async def check_key_exists():
    exists = await _check_key_exists()
    return 200 if exists else 400


@app.get("/main")
async def main(request: Request):
    if TOKEN:
        a = await get_dialogs_html()
        return templates.TemplateResponse("all_dialogs.html", {"request": request, "data": a})
    else:
        return RedirectResponse("/")


@app.get("/main/{dialog_id}")
async def get_dialog_by_id(request: Request, dialog_id):
    a = await _get_full_dialog(dialog_id)
    return templates.TemplateResponse("dialog_html.html", {"request": request, "data": a})


@app.post("/create_key")
async def create_secret_key(name: SecretKey):
    await create_key(name.model_dump()["key_name"])


@app.post("/send_message")
async def send_key(message: Message):
    code = 200
    message = message.model_dump()
    if message["crypt"]:
        message["msg_text"] = await encrypt_message(message["msg_text"])
    await _send_message(message)
    return {"status_code": code}


@app.post("/decrypt_message")
async def decrypt_message(msg: MsgForEncrypt):
    decrypted_msg = await _decrypt_message(msg.model_dump()["msg"])
    if not decrypted_msg:
        return 400

    return {"decrypted_msg": decrypted_msg}


@app.post('/exit_vk')
async def exit_vk():
    global TOKEN
    TOKEN = ""
    return 200


@app.get("/get_secret_key_login")
async def get_secret_message(request: Request):
    return templates.TemplateResponse("await.html", {"request": request})


@app.post("/allowed")
async def allowed(guest: GuestModel, request: Request):
    is_guest = guest.model_dump()
    exist_guest = await _get_guest_exist(request.client.host, is_guest["guest_alias"])
    # print(type(request.client.host))

    if exist_guest is None:
        await _add_host_guest(request.client.host, is_guest["guest_alias"])
    allow = await _get_host_guest_allow(request.client.host, is_guest["guest_alias"])
    return {"allow": True, "client_host": request.client.host, "alias": is_guest["guest_alias"]} if allow else {
        "allow": False}


@app.get("/get_secret_key/{host}/{alias}")
async def get_secret_key(host: str, alias: str):
    allow = await _get_host_guest_allow(host, alias)
    if allow:
        return fastapi.responses.FileResponse("Pab.key")
    else:
        return "Fuck you"


@app.get("/set_up_access")
async def set_up_access(request: Request):
    guests = await _get_all_guests_with_perm()
    print(guests)
    return templates.TemplateResponse("set_allow.html", {"request": request, "guests": guests})
