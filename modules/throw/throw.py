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
channel.description("发送'丢@某人'制作丢.gif")
channel.author("IMTMAX")


async def throw(file, squish=0):
    avatar = IMG.open(file)
    mask = IMG.new('L', avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    offset = 1
    draw.ellipse((offset, offset, avatar.size[0] - offset, avatar.size[1] - offset),
                 fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0))
    avatar.putalpha(mask)
    avatar = avatar.rotate(random.randint(1, 360), IMG.BICUBIC)
    avatar = avatar.resize((143, 143), IMG.ANTIALIAS)
    throw = IMG.open(Path(__file__).parent/'throw.png')
    throw.paste(avatar, (15, 178), mask=avatar)
    throw = throw.convert('RGB')
    throw.save(output := BytesIO(), format='jpeg')
    return output

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight([FullMatch("丢"), WildcardMatch() @ "para"])]
))
async def throw_main(app: Ariadne, group: Group, member: Member, para: MatchResult):
    user = para.result.getFirst(At).target if para.matched and para.result.has(At) else member.id
    profile_url = f"http://q1.qlogo.cn/g?b=qq&nk={user}&s=640"
    async with aiohttp.request("GET", profile_url) as r:
        profile = BytesIO(await r.read())
    pic = await throw(profile)
    await app.sendGroupMessage(group, MessageChain.create([Image(data_bytes=pic.getvalue())]))