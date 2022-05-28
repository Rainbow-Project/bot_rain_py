import asyncio

import aiohttp
from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import  MemberJoinEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.model import Member, Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from modules.ll_worship.worship import create_meme

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[MemberJoinEvent]))
async def newMember(app: Ariadne, event: MemberJoinEvent, member: Member, group: Group):
    msg_string = "欢迎大佬入群\n群地位-1"
    await app.sendGroupMessage(group,MessageChain.create(msg_string))
    url = f"https://q.qlogo.cn/g?b=qq&nk={member.id}&s=640"
    async with aiohttp.request("GET", url) as r:
        await app.sendGroupMessage(group,
                                   MessageChain.create(Image(data_bytes=await asyncio.to_thread(create_meme, await r.read()))))



