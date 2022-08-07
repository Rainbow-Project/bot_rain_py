import asyncio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import BotInvitedJoinGroupRequestEvent
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[BotInvitedJoinGroupRequestEvent]))
async def inv(app: Ariadne, event: BotInvitedJoinGroupRequestEvent):
    if event.supplicant == 563748846:
        await event.accept()
    else:
        await event.reject()
