# -*- coding: UTF-8 -*-
"""
@Project ：Bot_rain
@File    ：report.py
@Author  ：INTMAX
@Date    ：2022-06-03 7:49 p.m. 
"""
import base64
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Quote, At
from graia.ariadne.message.parser.twilight import (
    FullMatch,
    MatchResult,
    Twilight,
    WildcardMatch,
)
from graia.ariadne.model import Group
from io import BytesIO
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from PIL import Image as IMG, ImageFilter, ImageDraw
from ApiKeys import ocrApiKey

offline = False

channel = Channel.current()

APIKEY = ocrApiKey

API = "https://api.ocr.space/parse/imageurl?apikey=APIKEY&url=PIC_URL&language=chs&OCREngine=3&scale=true"


def pic_cut(file):
    pic_report = IMG.open(file)
    width, height = pic_report.size
    box = (500, 150, 1500, 600)
    region = pic_report.crop(box)
    output = BytesIO()
    region.save(output, format="jpeg")
    return output


def get_ship_data():
    dict_temp = {}
    with open("src/wows_data/wows_ship_v1.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()
            k = line.split(" ")[0]
            v = line.split(" ")[1]
            dict_temp[k] = v
    return dict_temp

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    WildcardMatch() @ "para",
                    FullMatch("口"),
                ]
            )
        ],
    )
)
async def report(app: Ariadne, group: Group, message: MessageChain, para: MatchResult):
    if offline:
        pass
    else:
        target = para.result.getFirst(At).target
        org_element: Quote = message[1]
        message_id = org_element.id
        event: MessageEvent = await app.getMessageFromId(message_id)
        msg_chain = event.messageChain
        org_img = msg_chain.get(Image)[0]
        input = BytesIO(await org_img.get_bytes())
        out = pic_cut(input)
        url: str = org_img.url
        session = Ariadne.service.client_session
        async with session.get(API.replace("APIKEY", APIKEY).replace("PIC_URL", url)) as resp:  # type: ignore
            data = await resp.json()
            dic = get_ship_data()
            val = data["ParsedResults"][0]["ParsedText"]
            for ship in dic.keys():
                if ship in val:
                    await app.send_message(group, MessageChain(f"检测到船只 {ship}"))
                    try:
                        await app.mute_member(group, target, 3600)
                    except PermissionError:
                        await app.send_group_message(group, MessageChain("ERROR:权限不足"))
                    break
