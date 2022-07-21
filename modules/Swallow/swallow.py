import asyncio
import os
from io import BytesIO
from pathlib import Path
import random

import aiohttp
import imageio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import (FullMatch, MatchResult,
                                                   Twilight, WildcardMatch)
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from PIL import Image as IMG, ImageFilter, ImageDraw

channel = Channel.current()

channel.name("throw")
channel.description("发送'吞@某人'制作吞.gif")
channel.author("IMTMAX")


async def swallow(file, squish=0):
    avatar = IMG.open(file)
    frame_locs = [(180, 60, 100, 100), (184, 75, 100, 100),
                  (183, 98, 100, 100), (179, 118, 110, 100),
                  (156, 194, 150, 48), (178, 136, 122, 69),
                  (175, 66, 122, 85), (170, 42, 130, 96),
                  (175, 34, 118, 95), (179, 35, 110, 93),
                  (180, 54, 102, 93), (183, 58, 97, 92),
                  (174, 35, 120, 94), (179, 35, 109, 93),
                  (181, 54, 101, 92), (182, 59, 98, 92),
                  (183, 71, 90, 96), (180, 131, 92, 101)]
    raw_frames = [f"{os.getcwd()}/modules/Swallow/SwallowedFrames/frame{i}.png" for i in range(23)]
    raw_frames = [IMG.open(i).convert('RGBA') for i in raw_frames]

    avatar_frames = []
    for i in range(len(frame_locs)):
        frame = IMG.new('RGBA', (480, 400), (255, 255, 255, 0))
        x, y, l, w = frame_locs[i]
        avatar_resized = avatar.resize((l, w), IMG.ANTIALIAS)
        frame.paste(avatar_resized, (x, y))
        img = raw_frames[i]
        frame.paste(img, mask=img)
        avatar_frames.append(frame)

    frames = []
    for i in range(2):
        frames.extend(avatar_frames[0:12])
    frames.extend(avatar_frames[0:8])
    frames.extend(avatar_frames[12:18])
    frames.extend(raw_frames[18:23])
    imageio.mimsave(output := BytesIO(), frames, format='gif', duration=0.06)
    return output


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight([FullMatch("吞"), WildcardMatch() @ "para"])]
))
async def swallow_main(app: Ariadne, group: Group, member: Member, para: MatchResult):
    user = para.result.getFirst(At).target if para.matched and para.result.has(At) else member.id
    profile_url = f"http://q1.qlogo.cn/g?b=qq&nk={user}&s=640"
    async with aiohttp.request("GET", profile_url) as r:
        profile = BytesIO(await r.read())
    pic = await swallow(profile)
    await app.send_group_message(group, MessageChain([Image(data_bytes=pic.getvalue())]))
