from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Quote
from graia.ariadne.model import Group

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from modules.wows.dataBase import update

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def gm(app: Ariadne, group: Group, message: MessageChain,message2: GroupMessage):
    if str(message) == "你好":
         await app.sendMessage(
            group,
            MessageChain.create(f"不要说{message.asDisplay()}"),
         )
         ''''
                                                            ｜        ｜
                                                            ｜        ｜
                                                            ｜        ｜
                                                            ｜        ｜
                                                             \        /
                                                              \      /
                                                               \    /
                                                                \  /
                                                                 \/
         '''
    elif str(message) == "强制更新" and message2.sender.id == 563748846:
        update()
        await app.sendMessage(
            group,
            MessageChain.create('强制更新完成'),
        )
    elif str(message) == "/help" and message2.sender.id == 563748846:
        await app.sendMessage(
            group,
            MessageChain.create('https://intmax.top/2022/05/13/%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%9F%BA%E7%A1%80%E6%8C%87'
                                '%E4%BB%A4/'),
        )
