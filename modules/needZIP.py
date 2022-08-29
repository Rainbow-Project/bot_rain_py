import random
import shutil
import string
import pyminizip
from pixivpy_async import *
import aiofiles
import os
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, MatchResult, WildcardMatch
from graia.ariadne.model import Group
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from io import BytesIO

channel = Channel.current()
saya = Saya.current()

Token = ''


async def getZIP(mode: str, app: Ariadne, group: Group):
    random_name_ini = str(''.join(random.sample(string.ascii_letters + string.digits, 8)).strip())
    random_name = ''.join(char for char in random_name_ini if char.isalnum())
    os.makedirs('tmp' + '/' + random_name)
    async with aiofiles.open('tmp' + '/' + random_name + '/random.txt', 'w') as file:
        await file.write(random_name)
    async with PixivClient() as client:
        aapi = AppPixivAPI(client=client)
        await aapi.login(refresh_token=Token)
        rank = await aapi.illust_ranking(mode)
        lis = random.sample(rank['illusts'], 10)
        success_pic = 0
        lost_connect = 0
        for i in lis:
            try:
                Pid = i['id']
                detail = await aapi.illust_detail(Pid)
                url = detail['illust']['meta_single_page']['original_image_url']
                await aapi.download(url, path='tmp/' + str(random_name),
                                    name=''.join(random.sample(string.ascii_letters + string.digits, 8)))
                success_pic += 1
            except Exception:
                lost_connect += 1
                pass
        msg = f'图片准备完成\n尝试数{success_pic + lost_connect}\n成功数{success_pic}\n失败数{lost_connect}'
        await app.send_group_message(group, MessageChain(msg))
        os.makedirs('tmp/zip/' + str(random_name))
        files = []
        path_setu = 'tmp/' + str(random_name) + '/'
        path_zip = 'tmp/zip/' + str(random_name) + '/'
        zip_path = []
        data_file = path_setu
        if os.path.exists(data_file):
            for dir_path, dir_names, file_names in os.walk(data_file):
                for filename in file_names:
                    file_path = os.path.join(dir_path, filename)
                    files.append(file_path)
                    zip_path.append('setu')
        pyminizip.compress_multiple(files, zip_path,
                                    path_zip + f'{random_name}.zip',
                                    random_name, 9)
        await app.send_group_message(group, MessageChain('压缩包准备完成'))
        async with aiofiles.open(f'tmp/zip/{random_name}/{random_name}.zip', 'rb') as aioFile:
            zip_read = BytesIO(await aioFile.read())
        passwd = random_name
        shutil.rmtree('tmp/' + str(random_name))
        shutil.rmtree('tmp/zip/' + str(random_name))
        return zip_read, passwd


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("看看你的"),
         WildcardMatch(optional=True) @ "para"]
    )]
))
async def needZIP(app: Ariadne, group: Group, para: MatchResult):
    await app.send_group_message(group, MessageChain('开始准备图片'))
    _cmd = (para.result.display.strip() if para.matched else '').split()
    _len = len(_cmd)
    match _len:
        case 1:
            if _cmd[0] == '18':
                mode = 'week_r18'
            else:
                mode = 'month'
        case _:
            mode = 'month'
    try:
        zipFile, passwd = await getZIP(mode, app, group)
        random_name_ini = str(''.join(random.sample(string.ascii_letters + string.digits, 8)).strip())
        random_name = ''.join(char for char in random_name_ini if char.isalnum())
        await app.upload_file(data=zipFile, target=group, path='can_can_need', name=f'加密的压缩包{random_name}.zip')
        await app.send_group_message(group, f'请记住密码{passwd}\n虽然我觉得你记不住')
    except Exception as e:
        await app.send_group_message(group, MessageChain('发生错误'))
        raise e
