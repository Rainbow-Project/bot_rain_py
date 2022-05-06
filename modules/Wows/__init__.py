import json
from PIL import Image, ImageDraw, ImageFont
import aiohttp
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import (FullMatch, MatchResult,
                                                   Twilight, WildcardMatch)
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from PIL import Image as IMG
from PIL import ImageDraw, ImageFont
import math

channel = Channel.current()
channel.name("Wows_checker")
channel.description("发送wows指令来进行查询")
channel.author("IntMax")
Dic_ID = {}
Wows_API_ID = "fc6d975614f91c3d2c87557577f4c60a"
wows_http_getUID = "https://api.worldofwarships.SERVER/wows/account/list/?search=WOWSUSERNAME&application_id=1145141919810"
wows_PERSONAL_DATA = "https://api.worldofwarships.SERVER/wows/account/info/?account_id=WOWSUID&application_id=1145141919810"
wows_cl_Data = "https://api.worldofwarships.SERVER/wows/clans/info/?application_id=fc6d975614f91c3d2c87557577f4c60a&clan_id=CLUID"
wows_pl_cl = "https://api.worldofwarships.SERVER/wows/clans/accountinfo/?application_id=fc6d975614f91c3d2c87557577f4c60a&account_id=WOWSUID"


async def get_pr(bts: int, wr: int, dmg: int):
    wr = (100 * wr)
    if bts <= 70:
        (100 * math.atan(bts / 40) * wr + 100 * math.asin(wr / 100) * dmg + 100 * math.acos(bts / 70)) / 1000
    else:
        pr = (10000 * math.atan(bts / 40) * wr + (1 * 100 * math.asin(wr / 100) * dmg)) / 1000
    if pr >= 6766:
        return "wows_god.jpg"
    elif pr >= 5766:
        return "wows_dalao.jpg"
    elif pr >= 5000:
        return "wows_verygood.jpg"
    elif pr >= 4500:
        return "wows_good.jpg"
    elif pr >= 3233:
        return "wows_avg.jpg"
    elif pr >= 2500:
        return "wows_avg-.jpg"
    else:
        return "wows_avg--.jpg"


async def gen_img(LV: str, cl: str, name: str, bats: str, wr: str, dmg: str, XP: str, KD: str, accu: str,
                  timestamp_crate: int, PR: str):
    img = IMG.open("wows_pic/" + PR)
    # 新建绘图对象
    draw = ImageDraw.Draw(img)
    # 选择文字字体和大小
    setFont = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 50)
    setFont_big = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 70)
    fillColor = (0, 0, 0)  # 文字颜色：黑色
    dt_object = datetime.fromtimestamp(timestamp_crate)
    date_crate = str(dt_object)
    w, h = setFont.getsize(LV)
    draw.text((621 - (w / 2), 340), LV, font=setFont, fill=fillColor)
    w, h = setFont.getsize(date_crate)
    draw.text((621 - (w / 2), 520), date_crate, font=setFont, fill=fillColor)
    w, h = setFont_big.getsize(cl)
    draw.text((621 - (w / 2), 100), cl, font=setFont_big, fill=fillColor)
    w, h = setFont_big.getsize(name)
    draw.text((621 - (w / 2), 200), name, font=setFont_big, fill=fillColor)
    w, h = setFont.getsize(bats)
    draw.text((245 - (w / 2), 1170), bats, font=setFont, fill=fillColor)
    w, h = setFont.getsize(wr)
    draw.text((630 - (w / 2), 1170), wr, font=setFont, fill=fillColor)
    w, h = setFont.getsize(dmg)
    draw.text((1040 - (w / 2), 1170), dmg, font=setFont, fill=fillColor)
    w, h = setFont.getsize(XP)
    draw.text((245 - (w / 2), 1700), XP, font=setFont, fill=fillColor)
    w, h = setFont.getsize(KD)
    draw.text((630 - (w / 2), 1700), KD, font=setFont, fill=fillColor)
    w, h = setFont.getsize(accu)
    draw.text((1040 - (w / 2), 1700), accu, font=setFont, fill=fillColor)
    return img


def add_dic(QQ_ID: int, WowsID: int, ser: str):
    dic = read_dic()
    lis = []
    lis += [str(WowsID)]
    lis += [ser]
    dic[QQ_ID] = lis
    write_dic(dic)


def read_dic():
    file = open('src/wows_data/user_data.data', 'r')
    js = file.read()
    try:
        dic = json.loads(js)
    except:
        dic = {}
    print(dic)
    file.close()
    return dic


def write_dic(dic: dict):
    json_str = json.dumps(dic)
    file = open('src/wows_data/user_data.data', 'w')
    file.write(json_str)
    file.close()


async def wows_getUID(nickName: str, server: str):
    data: json
    async with aiohttp.ClientSession() as s:
        api = wows_http_getUID.replace("SERVER", server).replace("WOWSUSERNAME", nickName).replace("1145141919810",
                                                                                                   Wows_API_ID)
        async with s.get(api) as res:
            return await res.json()


async def wows_c(ser: str, WOWS_UID: str):
    async with aiohttp.ClientSession() as s:
        async with s.get(wows_PERSONAL_DATA.replace("SERVER", ser).replace("WOWSUID", WOWS_UID)
                                 .replace("1145141919810", Wows_API_ID)) as res:
            return await res.json()


async def wows_get_pl_cl(WOWS_UID: str, ser: str):
    async with aiohttp.ClientSession() as s:
        async with s.get(wows_pl_cl.replace("SERVER", ser).replace("WOWSUID", WOWS_UID)) as res:
            return await res.json()


async def wows_get_cl(CLUID: str, ser: str):
    async with aiohttp.ClientSession() as s:
        async with s.get(wows_cl_Data.replace("SERVER", ser).replace("CLUID", CLUID)) as res:
            return await res.json()


async def wows_get_cl_tag(wows_UID_tmp: str, ser: str):
    data_pl_cr = await wows_get_pl_cl(wows_UID_tmp, ser)
    if data_pl_cr["status"] == "ok":
        try:
            cl_id = data_pl_cr["data"][wows_UID_tmp]["clan_id"]
            data_cl = await wows_get_cl(str(cl_id), ser)
            if data_cl["status"] == "ok":
                cl_tag = data_cl['data'][str(cl_id)]['tag']
                return "[" + cl_tag + "]"
        except:
            return ""


async def wows_get_data_UID(server_data: str, wows_UID_tmp: str):
    data_PD = await wows_c(server_data, wows_UID_tmp)
    if data_PD["status"] == "ok":
        cl_tag = await wows_get_cl_tag(wows_UID_tmp, server_data)
        data = data_PD['data'][wows_UID_tmp]
        PVP_battles = data['statistics']['pvp']['battles']
        PVP_WinRate = round((data['statistics']['pvp']['wins'] / PVP_battles), 6)
        PVP_AvgDmg = round(data['statistics']['pvp']['damage_dealt'] / PVP_battles)
        PVP_AvgXP = round(data['statistics']['pvp']['xp'] / PVP_battles)
        PVP_KD = round((data['statistics']['pvp']['frags'] / (PVP_battles - data['statistics']
        ['pvp']['survived_battles'])), 2)
        PVP_Main_Battery_Hit_Rate = round((data['statistics']['pvp']['main_battery']
                                           ['hits'] / data['statistics']['pvp']['main_battery']['shots']),
                                          6)
        date_create = data['created_at']
        tier = data['leveling_tier']
        pr = await get_pr(PVP_battles, PVP_WinRate, PVP_AvgDmg)
        PVP_WinRate = format(PVP_WinRate, ".2%")
        PVP_Main_Battery_Hit_Rate = format(PVP_Main_Battery_Hit_Rate, ".2%")
        wows_img = await gen_img("LV" + str(tier), cl_tag, data['nickname'], str(PVP_battles), str(PVP_WinRate),
                                 str(PVP_AvgDmg),
                                 str(PVP_AvgXP), str(PVP_KD), str(PVP_Main_Battery_Hit_Rate), date_create,
                                 pr)
        '''await app.sendGroupMessage(group, MessageChain.create(f"Wows_UID = {wows_UID_tmp} "
                                                              f"\nName = {nickName}"
                                                              f"\n总场数: {PVP_battles}"
                                                              f"\n胜率: {PVP_WinRate}"
                                                              f"\n场均: {PVP_AvgDmg}"
                                                              f"\n经验: {PVP_AvgXP}"
                                                              f"\nKD: {PVP_KD}"
                                                              f"\n命中率: {PVP_Main_Battery_Hit_Rate}"))'''
        wows_img.save(out := BytesIO(), format='JPEG')
        return out


async def wows_get_data(server_data: str, nickname: str):
    data_json = await wows_getUID(nickname, server_data)
    if data_json["status"] == "ok":
        data = data_json['data'][0]
        wows_UID_tmp = str(data['account_id'])
        nickName = data['nickname']
        data_PD = await wows_c(server_data, wows_UID_tmp)
        if data_PD["status"] == "ok":
            cl_tag = await wows_get_cl_tag(wows_UID_tmp, server_data)
            data = data_PD['data'][wows_UID_tmp]
            PVP_battles = data['statistics']['pvp']['battles']
            PVP_WinRate = round((data['statistics']['pvp']['wins'] / PVP_battles), 6)
            PVP_AvgDmg = round(data['statistics']['pvp']['damage_dealt'] / PVP_battles)
            PVP_AvgXP = round(data['statistics']['pvp']['xp'] / PVP_battles)
            PVP_KD = round((data['statistics']['pvp']['frags'] / (PVP_battles - data['statistics']
            ['pvp']['survived_battles'])), 2)
            PVP_Main_Battery_Hit_Rate = round((data['statistics']['pvp']['main_battery']
                                               ['hits'] / data['statistics']['pvp']['main_battery']['shots']),
                                              6)
            date_create = data['created_at']
            tier = data['leveling_tier']
            pr = await get_pr(PVP_battles, PVP_WinRate, PVP_AvgDmg)
            PVP_WinRate = format(PVP_WinRate, ".2%")
            PVP_Main_Battery_Hit_Rate = format(PVP_Main_Battery_Hit_Rate, ".2%")
            wows_img = await gen_img("LV" + str(tier), cl_tag, nickName, str(PVP_battles), str(PVP_WinRate),
                                     str(PVP_AvgDmg),
                                     str(PVP_AvgXP), str(PVP_KD), str(PVP_Main_Battery_Hit_Rate), date_create,
                                     pr)
            '''await app.sendGroupMessage(group, MessageChain.create(f"Wows_UID = {wows_UID_tmp} "
                                                                  f"\nName = {nickName}"
                                                                  f"\n总场数: {PVP_battles}"
                                                                  f"\n胜率: {PVP_WinRate}"
                                                                  f"\n场均: {PVP_AvgDmg}"
                                                                  f"\n经验: {PVP_AvgXP}"
                                                                  f"\nKD: {PVP_KD}"
                                                                  f"\n命中率: {PVP_Main_Battery_Hit_Rate}"))'''
            wows_img.save(out := BytesIO(), format='JPEG')
            return out


def get_me_data(QQID: int):
    dic = read_dic()
    return dic[str(QQID)]


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("wows"),
         WildcardMatch(optional=True) @ "para"]
    )]
))
async def wows(app: Ariadne, group: Group, para: MatchResult, message: GroupMessage):
    int_str = para.result.asDisplay().strip() if para.matched else ''
    list_cmd = int_str.split()
    Server_list = ["asia", "eu", "na", "ru"]
    cm_0 = list_cmd[0].lower()
    if cm_0 in Server_list:
        server_data = list_cmd[0]
        if list_cmd[1] == "me":
            await app.sendGroupMessage(group, MessageChain.create("非法操作"))
        else:
            out = await wows_get_data(cm_0, list_cmd[1])
            await app.sendGroupMessage(group, MessageChain.create([
                Image(data_bytes=out.getvalue())]))

    elif list_cmd[0] == "me":
        lis = get_me_data(message.sender.id)
        if len(lis) == 2:
            out = await wows_get_data_UID(lis[1], lis[0])
            await app.sendGroupMessage(group, MessageChain.create([
                Image(data_bytes=out.getvalue())]))
        else:
            await app.sendGroupMessage(group, MessageChain.create("找不到用户"))


    elif list_cmd[0] == "set":
        server_data = list_cmd[1]
        nickname = list_cmd[2]
        data_json = await wows_getUID(nickname, server_data)
        if data_json["status"] == "ok":
            data = data_json['data'][0]
            wows_UID_tmp = str(data['account_id'])
            add_dic(message.sender.id, wows_UID_tmp, server_data)
    else:
        out = await wows_get_data("asia", list_cmd[0])
        await app.sendGroupMessage(group, MessageChain.create([
            Image(data_bytes=out.getvalue())]))
