from graia.ariadne import get_running
from graia.ariadne.adapter import Adapter
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import GroupRecallEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import Image
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupRecallEvent]))
async def recall(app: Ariadne, group: Group, mem: Member):
    session = get_running(Adapter).session
    if mem.id != 214047076:
        async with session.get("https://intmax.top/img/pic_src/pic/Recall.jpg") as resp:  # type: ignore
            img_bytes = await resp.read()
        bot_message = await app.sendMessage(group, MessageChain.create(Image(data_bytes=img_bytes)))
