from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def gm(app: Ariadne, group: Group, message: MessageChain):
    if str(message) == "你好":
         await app.sendMessage(
            group,
            MessageChain.create(f"不要说{message.asDisplay()}"),
         )