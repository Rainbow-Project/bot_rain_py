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
from PIL import Image as IMG, ImageFilter,ImageDraw

channel = Channel.current()

channel.name("throw")
channel.description("发送'爬@某人'制作爬.jpg")
channel.author("IMTMAX")


async def crawl(file, squish=0):
    avatar = IMG.open(file)
    mask = IMG.new('L', avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    offset = 1
    draw.ellipse((offset, offset, avatar.size[0] - offset, avatar.size[1] - offset),
                 fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0))
    avatar.putalpha(mask)
    images = list(os.listdir(f"{os.getcwd()}/modules/crawl/crawl"))
    crawl = IMG.open(f"{os.getcwd()}/modules/crawl/crawl/{random.choice(images)}").resize(
        (500, 500), IMG.ANTIALIAS)
    avatar = avatar.resize((100, 100), IMG.ANTIALIAS)
    crawl.paste(avatar, (0, 400), mask=avatar)
    crawl = crawl.convert('RGB')
    output = BytesIO()
    crawl.save(output, format='jpeg')
    return output

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight([FullMatch("爬"), WildcardMatch() @ "para"])]
))
async def crawl_main(app: Ariadne, group: Group, member: Member, para: MatchResult):
    user = para.result.getFirst(At).target if para.matched and para.result.has(At) else member.id
    profile_url = f"http://q1.qlogo.cn/g?b=qq&nk={user}&s=640"
    async with aiohttp.request("GET", profile_url) as r:
        profile = BytesIO(await r.read())
    pic = await crawl(profile)
    await app.sendGroupMessage(group, MessageChain.create([Image(data_bytes=pic.getvalue())]))