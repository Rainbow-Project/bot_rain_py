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
    if message.display.strip() != "色图雷达":
        return
    session = Ariadne.service.client_session
    random_int = random.randrange(1, 930)
    async with session.get(
        "https://int-0x7fffffff.github.io/img/pic_src/setu_src/setu%20(XXX).jpg".replace(
            "XXX", str(random_int)
        )
    ) as resp:
        img_bytes = await resp.read()
    bot_message = await app.send_message(
        group, MessageChain(Image(data_bytes=img_bytes))
    )
    await asyncio.sleep(120)
    await app.recall_message(bot_message)
