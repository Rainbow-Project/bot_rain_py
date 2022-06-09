import asyncio
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
async def hitokoto(app: Ariadne, group: Group, message: MessageChain):
    if "一言" in str(message):
        session = get_running(Adapter).session
        async with session.get("https://v1.hitokoto.cn/?c=i&encode=text") as resp:
            res = await resp.text()
            bot_message = await app.sendMessage(group, MessageChain.create(res))
