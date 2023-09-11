import jinja2
from aiohttp import ClientSession
from dataclasses import dataclass

HEAD_LOGIN = {
    "Authorization": "Bearer vk1.a.Bxln2YFBIkqt7INbF3zOtsTcwko7xKqdsevKY01kvRQ2od_ZeUO3vTgBFzN6PDFppC3HuLC0BpcNA1TVcEMNghLzoMFcMr_82dBwLPFYc_V6sdgRBba-s0hY2E8EjQAPGAofJkNv4ufnbJuEyB_B09KpGKZEohAOP58bvFx5hR1LxjvUP9UhID1wFTaAMU9u4tzt3J8FluapQq7AxGdsbw"
}


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
                                     'text': point['text'],
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
    stm = """<!DOCTYPE html>
<html lang="ru">

<head>
    <meta charset="UTF-8">
    <title>VkHidden</title>
    <link href="../css/normal.css" rel="stylesheet">
    <link href="../css/index_style.css" rel="stylesheet">
</head>

<body>
    <div class="main">
        <div class="container">
            <div class="left_side">
                <a href="#" class="menu_btn">Сообщения</a>
                <a href="#" class="menu_btn">Друзья</a>
            </div>
                <div class="right_side_inner_content">
                {% for content in range(data|length) %}
                <div class="content">
                    <div class="inner_left">
                        <img src="{{data[content]["image"]}}" alt="" class="diaglog_img">
                    </div>

                    <div class="inner_right">
                        <p class="name">{{data[content]["first_name"]}} {{data[content]["last_name"]}}</p>
                        <p class="message">{{data[content]["text"]}}</p>
                    </div>
                    
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</body>

</html>"""

    environment = get_jinja_render()
    template = environment.from_string(stm)
    html = template.render(data=dialogs["messages"])
    return html
