import asyncio
import random
from pathlib import Path

from graia.ariadne import get_running
from graia.ariadne.adapter import Adapter
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def img(app: Ariadne, group: Group, message: MessageChain):
    if "给我爬" in str(message):
        session = get_running(Adapter).session
        s_pa = "" if random.randrange(1, 3) != 2 else "2"
        async with session.get("https://intmax.top/img/pic_src/pic/paXXX.jpg".replace("XXX",s_pa)) as resp:  # type: ignore
            img_bytes = await resp.read()
        bot_message = await app.sendMessage(group, MessageChain.create(Image(data_bytes=img_bytes)))