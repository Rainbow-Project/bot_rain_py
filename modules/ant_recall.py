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
    session = Ariadne.service.client_session
    if mem.id != 214047076:
        async with session.get("https://intmax.top/img/pic_src/pic/Recall.jpg") as resp:  # type: ignore
            img_bytes = await resp.read()
        bot_message = await app.send_message(
            group, MessageChain(Image(data_bytes=img_bytes))
        )
