from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    ElementMatch,
    ElementResult,
)
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from saucenao_api import AIOSauceNao
from saucenao_api.errors import SauceNaoApiError
from ApiKeys import saucenaoApiKey

channel = Channel.current()

"""              
去申请自己的           
           ｜        ｜
           ｜        ｜
           ｜        ｜
           ｜        ｜
            \        /
             \      /
              \    /
               \  /
                \/                                 
"""

apikey = saucenaoApiKey


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("色图大雷达"),
                    FullMatch("\n", optional=True),
                    "img" @ ElementMatch(Image, optional=True),
                ]
            ),
        ],
    )
)
async def saucenao(
    app: Ariadne, group: Group, member: Member, img: ElementResult, source: Source
):
    await app.send_group_message(group, MessageChain("我正在使用色图雷达"), quote=source.id)
    async with AIOSauceNao(apikey, numres=3) as snao:
        try:
            results = await snao.from_url(img.result.url)
        except SauceNaoApiError as e:
            await app.send_message(group, MessageChain("搜索失败desu"))
            return

    fwd_node_list = []
    for results in results.results:
        if len(results.urls) == 0:
            continue
        urls = "\n".join(results.urls)
        fwd_node_list.append(
            ForwardNode(
                target=app.account,
                sender_name="猜猜我是谁",
                time=datetime.now(),
                message=MessageChain(
                    f"相似度：{results.similarity}%\n标题：{results.title}\n节点名：{results.index_name}\n链接：{urls}"
                ),
            )
        )

    if len(fwd_node_list) == 0:
        await app.send_message(group, MessageChain("未找到有价值的数据"), quote=source.id)
    else:
        await app.send_message(group, MessageChain(Forward(node_list=fwd_node_list)))
