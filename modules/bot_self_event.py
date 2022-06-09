import asyncio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import BotInvitedJoinGroupRequestEvent
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[BotInvitedJoinGroupRequestEvent]))
async def inv(app: Ariadne, event: BotInvitedJoinGroupRequestEvent):
    '''
    看下面千万要记得改自己的qq号
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
    if event.supplicant == 1145141919810:
        event.accept()
    else:
        event.reject()

