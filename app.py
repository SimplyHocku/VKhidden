# -*- coding: utf-8 -*-
import asyncio
import pprint

import aiohttp
import jinja2
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import KeyResponse
from database import _get_keys
from pathlib import Path
from fastapi.responses import RedirectResponse

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
        # return templates.TemplateResponse("index.html", {"request": request})
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
    environment = jinja2.Environment()
    template = environment.from_string(pattern)
    html = {"html": template.render(keys=keys)}

    return html


# asyncio.run(get_html({'0': 'asdasdasd21', '1': 'acxvgdas231asdasdasd21'}))


@app.post("/get_keys")
async def get_keys():
    keys = await _get_keys()
    return await get_html(keys)


# @app.get("/login")
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
    print(TOKEN)
    return "200" if TOKEN else "400"


@app.get("/main")
async def main(request: Request):
    if TOKEN:
        return templates.TemplateResponse("index.html", {"request": request})

# async def clear_(response):
#     print(response['response']['items'][0]) ###reply_message
#     data = {"messages": []}
#     for index in range(len(response["response"]["items"])):
#         point = response['response']['items'][index]['last_message']
#         data["messages"].append({f"{index}": {'from': point['from_id'],
#                                               'to_id': point['peer_id'],
#                                               'attach': point['attachments'],
#                                               'text': point['text']}})
#
#         # print(data["messages"])
#     [print(msg) for msg in data["messages"]]


# async def test_post():
#     async with aiohttp.ClientSession() as session:
#         head = {
#             "Authorization": "Bearer vk1.a.Bxln2YFBIkqt7INbF3zOtsTcwko7xKqdsevKY01kvRQ2od_ZeUO3vTgBFzN6PDFppC3HuLC0BpcNA1TVcEMNghLzoMFcMr_82dBwLPFYc_V6sdgRBba-s0hY2E8EjQAPGAofJkNv4ufnbJuEyB_B09KpGKZEohAOP58bvFx5hR1LxjvUP9UhID1wFTaAMU9u4tzt3J8FluapQq7AxGdsbw"
#         }
#         async with session.post("https://api.vk.com/method/messages.getConversations?count=50&v=5.131 HTTP/1.1",
#                                 headers=head) as resp:
#             response = await resp.json(encoding="utf-8")
#             # print(response)
#             await clear_(response)
#             return response


# музыка - audio
# видео - video
# запись - wall
# документ- doc
# голосовое - audio_message
# ссылка - link
