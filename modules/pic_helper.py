from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, ElementMatch, ElementResult
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from saucenao_api import AIOSauceNao
from saucenao_api.errors import SauceNaoApiError

channel = Channel.current()

channel.name("Saucenao")
channel.description("以图搜图")
channel.author("I_love_study，intmax")

'''              
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
'''

apikey = "1145141919810"


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([
                           FullMatch("色图大雷达"),
                           FullMatch("\n", optional=True),
                           "img" @ ElementMatch(Image, optional=True),
                       ]),
                   ]))
async def saucenao(app: Ariadne, group: Group, member: Member, img: ElementResult, source: Source):
    await app.sendGroupMessage(group, MessageChain.create("我正在使用色图雷达"), quote=source.id)
    async with AIOSauceNao(apikey, numres=3) as snao:
        try:
            results = await snao.from_url(img.result.url)
        except SauceNaoApiError as e:
            await app.sendMessage(group, MessageChain.create("搜索失败desu"))
            return

    fwd_nodeList = []
    for results in results.results:
        if len(results.urls) == 0:
            continue
        urls = "\n".join(results.urls)
        fwd_nodeList.append(
            ForwardNode(
                target=app.account,
                senderName="猜猜我是谁",
                time=datetime.now(),
                message=MessageChain.create(
                    f"相似度：{results.similarity}%\n标题：{results.title}\n节点名：{results.index_name}\n链接：{urls}"
                )))

    if len(fwd_nodeList) == 0:
        await app.sendMessage(group, MessageChain.create("未找到有价值的数据"), quote=source.id)
    else:
        await app.sendMessage(group, MessageChain.create(Forward(nodeList=fwd_nodeList)))