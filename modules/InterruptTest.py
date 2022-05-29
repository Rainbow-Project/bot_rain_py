import asyncio

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import ListenerSchema

saya = Saya.current()
channel = Channel.current()
interrupt = InterruptControl(saya.broadcast)


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def interPt(app: Ariadne, group: Group, message: MessageChain, member: Member):
    if "中断" in str(message):
        await app.sendGroupMessage(group,
                                   MessageChain.create("我在听"))

        @Waiter.create_using_function([GroupMessage])
        async def InterruptWaiter(g: Group, m: Member, msg: MessageChain):
            if group.id == g.id and member.id == m.id:
                return msg

        try:
            rep_msg = await interrupt.wait(InterruptWaiter, timeout=15)
            await app.sendMessage(group, MessageChain.create(f'你是说了{rep_msg.asDisplay()}?'))
        except asyncio.TimeoutError:
            await app.sendMessage(group, MessageChain.create("不说就当没有了！"))
