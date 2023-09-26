import jinja2
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI
from aiohttp import ClientSession
from dataclasses import dataclass
from pathlib import Path

TOKEN = ""

HEAD_LOGIN = {
    "Authorization": f"Bearer {TOKEN}"
}

app = FastAPI()

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


@dataclass
class VkUrlPost:
    section_api: str
    method: str  #
    query: dict = None
    version: str = "v=5.131"
    http_version: str = "HTTP/1.1"

    query_string = None

    @staticmethod
    def pretty_query(self, values):
        queries = "&".join([f"{key}={value}" for key, value in values.items()])
        return queries

    def __post_init__(self):
        if self.query is not None:
            self.version = "&v=5.131"

        self.query_string = "https://api.vk.com/method/{}.{}?{}".format(
            self.section_api, self.method,
            f"{self.version} {self.http_version}" if self.query is None else f"{self.pretty_query(self, self.query)}"
                                                                             f"{self.version} {self.http_version}")


def get_jinja_render():
    environment = jinja2.Environment()
    return environment


async def get_more_info(user_id):
    info = dict()
    response = await post_to_vkapi(
        VkUrlPost(section_api="users", method="get", query={"fields": "crop_photo", "user_ids": user_id}))

    if response["response"]:
        point = response["response"][0]
        response = response["response"][0]["crop_photo"]["photo"]["sizes"][1]["url"] if point.get(
            "crop_photo") is not None else "url"
        info.update({"image": response, "first_name": point["first_name"], "last_name": point["last_name"]})

    return info


async def _get_clear_dialogs(response):
    data = {"messages": []}
    for index in range(len(response["response"]["items"])):
        point = response['response']['items'][index]['last_message']
        more = await get_more_info(point["peer_id"])
        if more:
            data["messages"].append({'from': point['from_id'],
                                     'to_id': point['peer_id'],
                                     'attach': point['attachments'][0]["type"] if point[
                                         "attachments"] else None,
                                     'text': point["text"],
                                     "image": more["image"],
                                     "first_name": more["first_name"],
                                     "last_name": more["last_name"]})

    return data


async def post_to_vkapi(param: VkUrlPost):
    async with ClientSession() as session:
        async with session.post(param.query_string,
                                headers=HEAD_LOGIN) as resp:
            response = await resp.json(encoding="utf-8")
            return response


async def get_dialogs_html(
        param: VkUrlPost = VkUrlPost(section_api="messages", method="getConversations", query={"count": 50})):
    response = await(post_to_vkapi(param))
    dialogs = await _get_clear_dialogs(response)

    return dialogs["messages"]


async def get_profile(profile_id: int = None):
    if profile_id is None:
        response = await post_to_vkapi(
            VkUrlPost(section_api="users", method="get", query={"fields": "photo_50"}))
    else:
        response = await post_to_vkapi(
            VkUrlPost(section_api="users", method="get", query={"user_ids": profile_id, "fields": "photo_50"}))
    response = response["response"][0]
    return {"id": response["id"], "image": response["photo_50"], "name": response["first_name"]}


async def _get_full_dialog(user_id):
    data = dict()
    param = VkUrlPost(section_api="messages", method="getHistory",
                      query={"user_id": user_id, "extended": 1, "fields": "photo_50", "count": 25})
    response = await post_to_vkapi(param)

    my_profile = await get_profile()
    peer_profile = await get_profile(user_id)
    data["data"] = []
    image, name = None, None
    for index, msg in enumerate(response["response"]["items"]):
        if my_profile["id"] == msg["from_id"]:
            image = my_profile["image"]
            name = my_profile["name"]
        if peer_profile["id"] == msg["from_id"]:
            image = peer_profile["image"]
            name = peer_profile["name"]
        text = msg["text"]
        message_id = msg["conversation_message_id"]
        d = {"image": image, "name": name, "text": text, "message_id": message_id}
        data["data"].append(d)
    data["data"] = list(reversed(data["data"]))

    return data["data"]


async def _send_message(message_lex):
    await post_to_vkapi(VkUrlPost(section_api="messages", method="send",
                                  query={"user_id": message_lex["user_id"], "random_id": 0,
                                         "message": message_lex["msg_text"]}))
