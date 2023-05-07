import asyncio
from io import BytesIO
from pathlib import Path

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
from PIL import Image as IMG

channel = Channel.current()

channel.name("support")
channel.description("发送'精神支柱@某人'制作精神支柱.jpg")
channel.author("IMT_MAX")


async def support(file, squish=0):
    avatar = IMG.open(file).convert("RGBA")
    support = IMG.open(Path(__file__).parent / "support.png")
    frame = IMG.new("RGBA", (1293, 1164), (255, 255, 255, 0))
    avatar = avatar.resize((815, 815), IMG.ANTIALIAS).rotate(23, expand=True)
    frame.paste(avatar, (-172, -17))
    frame.paste(support, mask=support)
    frame = frame.convert("RGB")
    frame.save(ret := BytesIO(), format="jpeg")
    return ret


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("精神支柱"), WildcardMatch() @ "para"])],
    )
)
async def support_main(app: Ariadne, group: Group, member: Member, para: MatchResult):
    user = (
        para.result.getFirst(At).target
        if para.matched and para.result.has(At)
        else member.id
    )
    profile_url = f"http://q1.qlogo.cn/g?b=qq&nk={user}&s=640"
    async with aiohttp.request("GET", profile_url) as r:
        profile = BytesIO(await r.read())
    pic = await support(profile)
    await app.send_group_message(
        group, MessageChain([Image(data_bytes=pic.getvalue())])
    )
