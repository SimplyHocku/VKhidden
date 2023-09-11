# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import KeyResponse
from database import _get_keys
from pathlib import Path
from fastapi.responses import RedirectResponse, HTMLResponse
from vkapi import get_jinja_render, get_dialogs_html

# access_token=vk1.a.ztLZi_h9NOfOgzD2sEV0g3HIrOPlxySP2q80L5rCibpf1sTNiZKoAYLV07XoVRnutW32BthxcVyZy8FolA9w6_6NSM4qUcOJdPICAdUICZxpwYX4xVJzhtDwhB29RDAaGtWgySrT1QPonFSktgjE86amIE38l_JKIABJx6GV1Dj_4dVR3vYsclHB1G1aBJ8S1ngOXLbOMtDu5z8p6CQT3g
app = FastAPI()

TOKEN = ""

app.mount(
    "/css",
    StaticFiles(directory=Path("css").absolute()),
    name="css",
)

app.mount(
    "/js",
    StaticFiles(directory=Path("js").absolute()),
    name="js",
)
templates = Jinja2Templates(directory="template")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


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
async def main():
    if TOKEN:
        return HTMLResponse(content=await get_dialogs_html(), status_code=200)

# музыка - audio
# видео - video
# запись - wall
# документ- doc
# голосовое - audio_message
# ссылка - link
