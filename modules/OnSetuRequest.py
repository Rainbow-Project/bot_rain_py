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
    if message.asDisplay().strip() != "色图雷达":
        return
    session = get_running(Adapter).session
    random_int = random.randrange(1,930)
    async with session.get("https://intmax.top/img/pic_src/setu_src/setu%20(XXX).jpg".replace("XXX",str(random_int))) as resp:  # type: ignore
        img_bytes = await resp.read()
    bot_message = await app.sendMessage(group, MessageChain.create(Image(data_bytes=img_bytes)))
    await asyncio.sleep(120)
    await app.recallMessage(bot_message)