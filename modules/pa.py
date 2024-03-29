import asyncio
import random
from pathlib import Path
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
        session = Ariadne.service.client_session
        if random.randrange(1, 3) != 2:
            s_pa = ""
        else:
            s_pa = "2"
        async with session.get(
            "https://int-0x7fffffff.github.io/img/pic_src/pic/paXXX.jpg".replace("XXX", s_pa)
        ) as resp:  # type: ignore
            img_bytes = await resp.read()
        bot_message = await app.send_message(
            group, MessageChain(Image(data_bytes=img_bytes))
        )
