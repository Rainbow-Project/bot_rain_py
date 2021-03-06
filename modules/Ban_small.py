from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()

channel.name("BanMe")
channel.description("发送'禁言我'禁言(前提是有权限)")
channel.author("INT_MAX")

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight([RegexMatch(".?禁言体验卡.?")])]
))
async def auto_ban(app: Ariadne, group: Group, member: Member):
    try:
        await app.muteMember(group, member, 60)
        await app.sendGroupMessage(group, MessageChain.create('那我就来实现你的愿望吧！'))
    except PermissionError:
        await app.sendGroupMessage(group, MessageChain.create('对不起，我没有办法实现你的愿望555~'))