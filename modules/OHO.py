import asyncio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def gm(app: Ariadne, group: Group, message: MessageChain):
    if "饿还饿" in str(message):
        session = get_running(Adapter).session
        async with session.get("https://intmax.top/img/pic_src/pic/OHO.jpg") as resp:  # type: ignore
            img_bytes = await resp.read()
        bot_message = await app.sendMessage(group, MessageChain.create(Image(data_bytes=img_bytes)))
        await asyncio.sleep(2)
        async with session.get("https://intmax.top/img/pic_src/pic/OHO2.jpg") as resp:  # type: ignore
            img_bytes = await resp.read()
        bot_message = await app.sendMessage(group, MessageChain.create(Image(data_bytes=img_bytes)))
        await asyncio.sleep(2)
        async with session.get("https://intmax.top/img/pic_src/pic/OHO3.png") as resp:  # type: ignore
            img_bytes = await resp.read()
        bot_message = await app.sendMessage(group, MessageChain.create(Image(data_bytes=img_bytes)))