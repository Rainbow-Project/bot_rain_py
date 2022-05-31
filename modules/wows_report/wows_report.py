from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Quote, At
from graia.ariadne.message.parser.twilight import (FullMatch, MatchResult,
                                                   Twilight, WildcardMatch)
from graia.ariadne.model import Group
from io import BytesIO
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from PIL import Image as IMG, ImageFilter, ImageDraw
import easyocr

channel = Channel.current()


def pic_cut(file):
    pic_report = IMG.open(file)
    width, height = pic_report.size
    box = (500, 150, 1500, 600)
    region = pic_report.crop(box)
    output = BytesIO()
    region.save(output, format='jpeg')
    return output


def get_ship_data():
    dict_temp = {}
    with open("src/wows_data/wows_ship_v1.txt", 'r') as f:
        for line in f.readlines():
            line = line.strip()
            k = line.split(' ')[0]
            v = line.split(' ')[1]
            dict_temp[k] = v
    return dict_temp


def ocr_read(file):
    reader = easyocr.Reader(['ch_sim'], gpu=False)
    result = reader.readtext(file.getvalue(), detail=0)
    return result


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight([WildcardMatch() @ "para", FullMatch("举报"), ])]
))
async def report(app: Ariadne, group: Group, message: MessageChain, para: MatchResult):
    # await app.sendMessage(group, MessageChain.create('OCR检测开始'))
    target = para.result.getFirst(At).target
    org_element: Quote = message[1]
    message_id = org_element.id
    event: MessageEvent = await app.getMessageFromId(message_id)
    msg_chain = event.messageChain
    org_img = msg_chain.get(Image)[0]
    input = BytesIO(await org_img.get_bytes())
    out = pic_cut(input)
    res = ocr_read(file=input)
    dic_ship = get_ship_data()
    for res_sig in res:
        if res_sig in dic_ship.keys():
            await app.sendMessage(group,
                                  MessageChain.create(f'检测到船只 {res_sig}'))
            try:
                await app.muteMember(group, target, 1)
            except PermissionError:
                await app.sendGroupMessage(group, MessageChain.create('ERROR:权限不足'))
            break
