from graia.ariadne import get_running
from graia.ariadne.adapter import Adapter
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import GroupRecallEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import Image, Voice
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
import os
import random
import graia
import io

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def zao(app: Ariadne, group: Group, message: MessageChain):
    if "早上好" in str(message):
        path = "src/dinggong_silk/"
        audios = []
        for x in os.listdir(path):
            audios.append(x)
        audio_random = path+random.sample(audios,1)[0]
        with open(audio_random,'rb') as f:
            file = io.BytesIO(f.read())
            await app.sendMessage(group, MessageChain.create(Voice(data_bytes=file.getvalue())))
