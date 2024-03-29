from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import NudgeEvent
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[NudgeEvent]))
async def getup(app: Ariadne, event: NudgeEvent):
    if event.context_type == "group":
        if event.target == 214047076:
            await app.send_group_message(event.group_id, MessageChain("你不要光天化日之下在这里戳我啊"))  # type: ignore
    elif event.context_type == "friend":
        await app.sendFriendMessage(event.friend_id, MessageChain("别戳我，好痒！"))  # type: ignore
