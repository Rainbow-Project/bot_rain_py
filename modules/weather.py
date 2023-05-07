import asyncio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    WildcardMatch,
    MatchResult,
)
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from ApiKeys import weatherApikey

channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([FullMatch("天气"), WildcardMatch(optional=True) @ "para"])
        ],
    )
)
async def wather(app: Ariadne, group: Group, message: MessageChain, para: MatchResult):
    city = para.result.display.strip() if para.matched else ""
    if city != "":
        session = Ariadne.service.client_session
        """
        如果不打算用也没事
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

        async with session.get(
            f"https://api.seniverse.com/v3/weather/now.json?key={weatherApikey}&location=CITY"
            "&language=zh-Hans&unit=c".replace("CITY", city)
        ) as resp:
            res = await resp.json()
            wather_text = res["results"][0]["now"]
            wa = wather_text["text"]
            tem = wather_text["temperature"]
            bot_message = await app.send_message(
                group, MessageChain(f"今天{city}天气" f"\n{wa}" f"温度{tem}")
            )
