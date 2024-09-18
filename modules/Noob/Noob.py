# -*- coding: UTF-8 -*-
"""
@Project ：bot_rain
@File    ：Noob.py
@Author  ：INTMAX
@Date    ：2022-06-05 10:40 a.m. 
"""
import asyncio
import os
from io import BytesIO
from pathlib import Path
import random

import aiohttp
import imageio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import (
    FullMatch,
    MatchResult,
    Twilight,
    WildcardMatch,
)
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from PIL import Image as IMG, ImageFilter, ImageDraw

channel = Channel.current()

async def Noob(file, squish=0):
    avatar = IMG.open(file)
    mask = IMG.new("L", avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    offset = 1
    draw.ellipse(
        (offset, offset, avatar.size[0] - offset, avatar.size[1] - offset), fill=255
    )
    mask = mask.filter(ImageFilter.GaussianBlur(0))
    avatar.putalpha(mask)
    avatar = avatar.rotate(random.randint(1, 1), IMG.BICUBIC)
    avatar = avatar.resize((47, 47), IMG.ANTIALIAS)
    noob = IMG.open(Path(__file__).parent / "Noob.jpg")
    noob.paste(avatar, (9, 35), mask=avatar)
    noob = noob.convert("RGB")
    output = BytesIO()
    noob.save(output, format="jpeg")
    return output


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("菜"), WildcardMatch() @ "para"])],
    )
)
async def Noob_main(app: Ariadne, group: Group, member: Member, para: MatchResult):
    user = (
        para.result.getFirst(At).target
        if para.matched and para.result.has(At)
        else member.id
    )
    profile_url = f"http://q1.qlogo.cn/g?b=qq&nk={user}&s=640"
    async with aiohttp.request("GET", profile_url) as r:
        profile = BytesIO(await r.read())
        out = await Noob(profile)
        await app.send_group_message(
            group, MessageChain([Image(data_bytes=out.getvalue())])
        )
