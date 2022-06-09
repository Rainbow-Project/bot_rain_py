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
from graia.ariadne.message.parser.twilight import (FullMatch, MatchResult,
                                                   Twilight, WildcardMatch)
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from PIL import Image as IMG, ImageFilter, ImageDraw

channel = Channel.current()

channel.name("Audacious")
channel.description("发送'不如大胆@某人'制作不如大胆.jpg")
channel.author("IMT_MAX")


async def Audacious_fun(file1, file2):
    avatar = IMG.open(file1)
    avatar2 = IMG.open(file2)
    mask = IMG.new('L', avatar.size, 0)
    mask2 = IMG.new('L', avatar2.size, 0)
    draw = ImageDraw.Draw(mask)
    draw2 = ImageDraw.Draw(mask2)
    offset = 1
    draw.ellipse((offset, offset, avatar.size[0] - offset, avatar.size[1] - offset),
                 fill=255)
    draw2.ellipse((offset, offset, avatar2.size[0] - offset, avatar2.size[1] - offset),
                  fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0))
    mask2 = mask2.filter(ImageFilter.GaussianBlur(0))
    avatar.putalpha(mask)
    avatar2.putalpha(mask2)
    Audacious = IMG.open(Path(__file__).parent / 'Audacious.jpg')
    avatar = avatar.resize((85, 85), IMG.ANTIALIAS)
    avatar2 = avatar2.resize((150, 150), IMG.ANTIALIAS)
    Audacious.paste(avatar, (550, 90), mask=avatar)
    Audacious.paste(avatar2, (100, 500), mask=avatar2)
    Audacious = Audacious.convert('RGB')
    output = BytesIO()
    Audacious.save(output, format='jpeg')
    return output


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight([FullMatch("不如大胆"), WildcardMatch() @ "para"])]
))
async def Audacious_main(app: Ariadne, group: Group, member: Member, para: MatchResult):
    user = para.result.getFirst(At).target if para.matched and para.result.has(At) else member.id
    profile_url = f"http://q1.qlogo.cn/g?b=qq&nk={user}&s=640"
    async with aiohttp.request("GET", profile_url) as r:
        profile = BytesIO(await r.read())
    async with aiohttp.request("GET", f"http://q1.qlogo.cn/g?b=qq&nk={member.id}&s=640") as r:
        profile2 = BytesIO(await r.read())
    pic = await Audacious_fun(profile, profile2)
    await app.sendGroupMessage(group, MessageChain.create([Image(data_bytes=pic.getvalue())]))
