from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Quote
from graia.ariadne.model import Group

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from wows.dataBase import update

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def gm(app: Ariadne, group: Group, message: MessageChain, message2: GroupMessage):
    if str(message) == "你好":
        await app.send_message(
            group,
            MessageChain(f"不要说{message.display}"),
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
        await update()
        await app.send_message(
            group,
            MessageChain('强制更新完成'),
        )
    elif str(message) == "/help" and message2.sender.id == 563748846:
        await app.send_message(
            group,
            MessageChain('https://intmax.top/2022/05/13/%E6%9C%BA%E5%99%A8%E4%BA%BA%E5%9F%BA%E7%A1%80%E6%8C%87'
                                '%E4%BB%A4/'),
        )
