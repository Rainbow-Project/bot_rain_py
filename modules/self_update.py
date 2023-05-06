from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
import os
import subprocess

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def gm(app: Ariadne, group: Group, message: MessageChain, message2: GroupMessage):
    if str(message) == "/self update" and message2.sender.id == 563748846:
        current_directory = os.getcwd()
        os.chdir(current_directory)
        try:
            subprocess.check_call(['git', 'pull'])
        except subprocess.CalledProcessError as error:
            await app.send_message(
            group,
            MessageChain(str(error)),
        )
        await app.send_message(
            group,
            MessageChain('尝试重启程序'),
        )
        os.execvp('poetry', ['poetry', 'run', 'python', 'main.py'])


