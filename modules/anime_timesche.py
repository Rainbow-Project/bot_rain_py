from datetime import date, datetime
from io import BytesIO

import aiohttp
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import (
    FullMatch,
    MatchResult,
    Twilight,
    WildcardMatch,
)
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from PIL import Image as IMG
from PIL import ImageDraw, ImageFont

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([FullMatch("anime"), WildcardMatch(optional=True) @ "para"])
        ],
    )
)
async def anime(app: Ariadne, group: Group, para: MatchResult):
    today = int(datetime.fromisoformat(date.today().isoformat()).timestamp())
    date2ts = {"yesterday": today - 86400, "": today, "tomorrow": today + 86400}
    d = para.result.display.strip() if para.matched else ""

    if d in date2ts:
        date_ts = date2ts[d]
    else:
        await app.send_group_message(group, MessageChain("未知时间"))
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://bangumi.bilibili.com/web_api/timeline_global"
        ) as r:
            result = (await r.json())["result"]
            data = next(
                anime_ts["seasons"]
                for anime_ts in result
                if anime_ts["date_ts"] == date_ts
            )
        final_back = IMG.new("RGB", (1200, 300 * len(data)), (40, 41, 35))
        final_draw = ImageDraw.Draw(final_back)
        for n, single in enumerate(data):
            async with session.get(single["square_cover"]) as f:
                pic = IMG.open(BytesIO(await f.read()))
            if pic.size != (240, 240):
                pic = pic.resize((240, 240), IMG.ANTIALIAS)
            mask = IMG.new("L", (480, 480), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, 480, 480), 50, 255)
            final_back.paste(
                pic,
                (30, 30 + 300 * n, 270, 270 + 300 * n),
                mask=mask.resize((240, 240), IMG.ANTIALIAS),
            )

            ttf = ImageFont.truetype("src/font/SourceHanSans-Medium.otf", 60)
            ellipsis_size = ttf.getsize("...")[0]
            if ttf.getsize(single["title"])[0] >= 900:
                while ttf.getsize(single["title"])[0] > 900 - ellipsis_size:
                    single["title"] = single["title"][:-1]
                single["title"] = single["title"] + "..."
            final_draw.text(
                (300, 50 + 300 * n), single["title"], font=ttf, fill=(255, 255, 255)
            )
            final_draw.text(
                (300, 150 + 300 * n), single["pub_time"], font=ttf, fill=(255, 255, 255)
            )
            final_draw.text(
                (300 + ttf.getsize(single["pub_time"])[0] + 30, 150 + 300 * n),
                single["pub_index"]
                if "pub_index" in single
                else single["delay_index"] + single["delay_reason"],
                font=ttf,
                fill=(0, 160, 216),
            )
        final_back.save(out := BytesIO(), format="JPEG")
    await app.send_group_message(
        group, MessageChain([Image(data_bytes=out.getvalue())])
    )
