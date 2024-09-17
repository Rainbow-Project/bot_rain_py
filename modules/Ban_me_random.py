import random

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(".?禁言我.?")])],
    )
)
async def auto_ban(app: Ariadne, group: Group, member: Member):
    Ban_time_random = random.randrange(1, 114514)
    try:
        await app.mute_member(group, member, Ban_time_random)
        await app.send_group_message(group, MessageChain("那我就来实现你的愿望吧！"))
    except PermissionError:
        await app.send_group_message(group, MessageChain("对不起，我没有办法实现你的愿望555~"))
