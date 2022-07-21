import random

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, WildcardMatch, MatchResult
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("roll"),
         WildcardMatch(optional=True) @ "para"]
    )]
))
async def wows(app: Ariadne, group: Group, para: MatchResult):
    int_str = para.result.display.strip() if para.matched else ''
    cmd = int_str.split()
    lenCmd = len(cmd)
    try:
        if lenCmd == 0:
            await app.send_message(group, MessageChain(str(random.randint(1, 100))))
        elif lenCmd == 1:
            await app.send_message(group, MessageChain(str(random.randint(1, int(cmd[0])))))
        elif lenCmd == 2:
            await app.send_message(group, MessageChain(str(random.randint(int(cmd[0]), int(cmd[1])))))
        elif lenCmd == 3:
            msg = ''
            for i in range(int(cmd[2])):
                msg += str(random.randint(int(cmd[0]), int(cmd[1])))
                if i != int(cmd[2]) - 1:
                    msg += '\n'
            await app.send_message(group, MessageChain(msg))
        else:
            await app.send_message(group, MessageChain('参数太多了！'))
    except Exception:
        await app.send_message(group, MessageChain('你确定输入没有问题？'))
