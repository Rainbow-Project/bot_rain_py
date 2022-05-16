import json
import math
from graia.ariadne.message.chain import MessageChain
import aiohttp
from PIL import Image
from PIL import Image as IMG
from PIL import ImageDraw, ImageFont
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import (FullMatch, MatchResult,
                                                   Twilight, WildcardMatch)
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import modules.Wows.wows_sql_data

dev = False

channel = Channel.current()
channel.name("Wows_checker")
channel.description("发送wows指令来进行查询")
channel.author("IntMax")
Dic_ID = {}
Wows_API_ID = "fc6d975614f91c3d2c87557577f4c60a"
wows_numbers_api = 'https://api.wows-numbers.com/personal/rating/expected/json/'
wows_http_getUID = "https://api.worldofwarships.SERVER/wows/account/list/?search=WOWSUSERNAME&application_id" \
                   "=1145141919810 "
wows_PERSONAL_DATA = "https://api.worldofwarships.SERVER/wows/account/info/?account_id=WOWSUID&application_id" \
                     "=1145141919810 "
wows_cl_Data = "https://api.worldofwarships.SERVER/wows/clans/info/?application_id=fc6d975614f91c3d2c87557577f4c60a" \
               "&clan_id=CLUID "
wows_pl_cl = "https://api.worldofwarships.SERVER/wows/clans/accountinfo/?application_id" \
             "=fc6d975614f91c3d2c87557577f4c60a&account_id=WOWSUID "
wows_pl_ship = 'https://api.worldofwarships.SERVER/wows/ships/stats/?application_id=fc6d975614f91c3d2c87557577f4c60a' \
               '&language=zh-cn&account_id=WOWSUID&ship_id=SHIP_ID '

wows_pl_ship_data = 'https://api.worldofwarships.SERVER/wows/ships/stats/?application_id' \
                    '=fc6d975614f91c3d2c87557577f4c60a&account_id=WOWS_ID '


async def get_pr(bts: int, wr: int, dmg: int):
    wr = (100 * wr)
    if bts <= 70:
        pr = (100 * math.atan(bts / 40) * wr + 100 * math.asin(wr / 100) * dmg + 100 * math.acos(bts / 70)) / 1000
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


async def get_pr_ship(bts: int, wr: int, dmg: int, frags: int, ship_id: str):
    ship_exp: dict
    ship_exp = wows_get_numbers_api()
    ship_exp = ship_exp['data'][ship_id]
    avg_dmg = ship_exp["average_damage_dealt"]
    avg_frags = ship_exp["average_frags"]
    avg_wr = ship_exp["win_rate"]
    rDmg = dmg / avg_dmg
    rFrags = frags / avg_frags
    rWins = wr * 100 / avg_wr
    nDmg = max(0, (rDmg - 0.4) / (1 - 0.4))
    nFrags = max(0, (rFrags - 0.1) / (1 - 0.1))
    nWins = max(0, (rWins - 0.7) / (1 - 0.7))
    wr = (100 * wr)
    wr_w = (100 * math.asin(wr / 100)) / 158

    pr = (350 + (350 * wr_w)) * nDmg + 300 * nFrags + (150 + (350 * (1 - wr_w))) * nWins
    return pr


async def get_pr_ship_pic(bts: int, wr: int, dmg: int, frags: int, ship_id: str):
    pr = await get_pr_ship(bts, wr, dmg, frags, ship_id)

    if pr >= 2450:
        return "wows_god.jpg"
    elif pr >= 2100:
        return "wows_dalao.jpg"
    elif pr >= 1750:
        return "wows_verygood.jpg"
    elif pr >= 1350:
        return "wows_good.jpg"
    elif pr >= 1100:
        return "wows_avg.jpg"
    elif pr >= 750:
        return "wows_avg-.jpg"
    else:
        return "wows_avg--.jpg"


def get_pr_img(pr: int):
    if pr >= 2450:
        return "wows_god.jpg"
    elif pr >= 2100:
        return "wows_dalao.jpg"
    elif pr >= 1750:
        return "wows_verygood.jpg"
    elif pr >= 1350:
        return "wows_good.jpg"
    elif pr >= 1100:
        return "wows_avg.jpg"
    elif pr >= 750:
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


def add_dic(QQ_ID: int, WowsID: str, ser: str):
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


def wows_get_numbers_api():
    data: json
    with open("src/wows_data/wows_exp.json", "r") as f:
        return json.load(f)


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


async def wows_c_pl_ship(ser: str, wows_id: str, ship_id: str):
    async with aiohttp.ClientSession() as s:
        async with s.get(wows_pl_ship.replace("SERVER", ser).replace("WOWSUID", wows_id)
                                 .replace("SHIP_ID", ship_id)) as res:
            return res.json()


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


async def wows_get_ship_data(ser: str, wowsUID: str, ship_id: str):
    data: json
    async with aiohttp.ClientSession() as s:
        api = wows_pl_ship.replace("SERVER", ser).replace("WOWSUID", wowsUID).replace("SHIP_ID", ship_id)
        async with s.get(api) as res:
            return await res.json()


async def wows_get_pl_ship_data(ser: str, wows_id: str):
    data: json
    async with aiohttp.ClientSession() as s:
        api = wows_pl_ship_data.replace("SERVER", ser).replace("WOWS_ID", wows_id)
        async with s.get(api) as res:
            return await res.json()


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


async def get_pr_v2(ser: str, wows_id: str):
    tpr = 0
    total_cont = 0
    data_ini = wows_sql_data.get_user_data_wg_api(wows_id, ser)
    if data_ini['status'] == 'ok':
        data = data_ini['data'][wows_id]
        for i in data:
            dic_tmp = {}
            ship_id = i['ship_id']
            i = i['pvp']
            battles = i['battles']
            damage_dealt = i['damage_dealt']
            wins = i['wins']
            frags = i['frags']
            try:
                tpr += await get_pr_ship(battles, wins / battles, damage_dealt / battles, frags / battles, str(ship_id))
                total_cont += 1
            except:
                None
        data_PD = await wows_c(ser, wows_id)
        if data_PD["status"] == "ok":
            cl_tag = await wows_get_cl_tag(wows_id, ser)
            data = data_PD['data'][wows_id]
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
            pr = tpr / total_cont
            PVP_WinRate = format(PVP_WinRate, ".2%")
            PVP_Main_Battery_Hit_Rate = format(PVP_Main_Battery_Hit_Rate, ".2%")
            pr_img = get_pr_img(pr)
            wows_img = await gen_img("LV" + str(tier), cl_tag, data['nickname'], str(PVP_battles), str(PVP_WinRate),
                                     str(PVP_AvgDmg),
                                     str(PVP_AvgXP), str(PVP_KD), str(PVP_Main_Battery_Hit_Rate), date_create,
                                     pr_img)
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
            PVP_KILL = round(data['statistics']['pvp']['frags'] / PVP_battles, 2)
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


async def wows_get_pl_ship(wows_id: str, ship_id: str, ser: str, ship_name_give: str):
    data = await wows_get_ship_data(ser, wows_id, ship_id)
    if data['status'] == 'ok':
        data = data['data'][wows_id][0]['pvp']
        bats = data['battles']
        WR = data['wins'] / bats
        frags = data['frags'] / bats
        dmg = round(data['damage_dealt'] / bats)
        XP = round(data['xp'] / bats)
        try:
            accu = data['main_battery']['hits'] / data['main_battery']['shots']
            accu = format(accu, ".2%")
        except:
            accu = "N/A"
        KD = round(data['frags'] / (max(bats - data['survived_battles'], 1)), 2)
        PR = await get_pr_ship_pic(int(bats), WR, dmg, frags, ship_id)
        WR = format(WR, ".2%")
        data_PD = await wows_c(ser, wows_id)
        if data_PD["status"] == "ok":
            cl_tag = await wows_get_cl_tag(wows_id, ser)
            data = data_PD['data'][wows_id]
            date_create = data['created_at']
            tier = data['leveling_tier']
            name = data['nickname']
            wows_img = await gen_img(ship_name_give, cl_tag, name, str(bats), str(WR),
                                     str(dmg),
                                     str(XP), str(KD), str(accu), date_create,
                                     PR)
            wows_img.save(out := BytesIO(), format='JPEG')
            return out


async def wows_recent(user_wows_id: str, user_server: str, user_past_data: dict):
    data_ini = wows_sql_data.get_user_data_wg_api(user_wows_id, user_server)
    dic_user_recent = {}
    dic_emp = {'battles': 0, 'damage_dealt': 0, 'wins': 0, 'frags': 0}
    if data_ini['status'] == 'ok':
        data = data_ini['data'][user_wows_id]
        for i in data:
            ship_id = i['ship_id']
            i = i['pvp']
            battles = i['battles']
            damage_dealt = i['damage_dealt']
            wins = i['wins']
            frags = i['frags']
            if str(ship_id) in user_past_data.keys():
                user_past_data_ship = user_past_data[str(ship_id)]
            else:
                user_past_data_ship = dic_emp
            if battles != user_past_data_ship['battles']:
                dic_user_recent[ship_id] = {'battles': battles - user_past_data_ship['battles'],
                                            'wins': wins - user_past_data_ship['wins'],
                                            'frags': frags - user_past_data_ship['frags'],
                                            'damage_dealt': damage_dealt - user_past_data_ship['damage_dealt']}
        if dic_user_recent == {}:
            return MessageChain.create("可能最近没有战斗或无法访问数据")
        else:
            tpr = 0
            total_cont = 0
            tw = 0
            td = 0
            tb = 0
            for i in dic_user_recent:
                dic_tmp = {}
                ship_id = i
                battles = dic_user_recent[ship_id]['battles']
                tb += battles
                damage_dealt = dic_user_recent[ship_id]['damage_dealt']
                td += damage_dealt
                wins = dic_user_recent[ship_id]['wins']
                tw += wins
                frags = dic_user_recent[ship_id]['frags']
                try:
                    tpr += await get_pr_ship(battles, wins / battles, damage_dealt / battles, frags / battles,
                                             str(ship_id))
                    total_cont += 1
                except:
                    None
            pr_img = get_pr_img(tpr/total_cont)
            data_PD = await wows_c(user_server, user_wows_id)
            if data_PD["status"] == "ok":
                cl_tag = await wows_get_cl_tag(user_wows_id, user_server)
                data = data_PD['data'][user_wows_id]
                date_create = data['created_at']
                tier = data['leveling_tier']
                wr = format(round((tw / tb), 6), ".2%")
                name = data['nickname']
                dmg = str(round(td/tb))
                wows_img = await gen_img("LV"+str(tier),cl_tag,name,str(tb),wr,dmg,"N/A","N/A",'N/A',date_create,pr_img)
                wows_img.save(out := BytesIO(), format='JPEG')
                return MessageChain.create([Image(data_bytes=out.getvalue())])


def get_ship_id(ship_name: str):
    dict_temp = {}
    with open("src/wows_data/wows_ship_v1.txt", 'r') as f:
        for line in f.readlines():
            line = line.strip()
            k = line.split(' ')[0]
            v = line.split(' ')[1]
            dict_temp[k] = v
    if ship_name in dict_temp.keys():
        return dict_temp[ship_name]
    else:
        return ''


def get_me_data(QQID: int):
    dic = read_dic()
    if str(QQID) in dic.keys():
        return dic[str(QQID)]
    else:
        return []


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
    if cm_0 in Server_list and list_cmd[-1] != 'ship':
        server_data = list_cmd[0]
        if list_cmd[1] == "me":
            await app.sendGroupMessage(group, MessageChain.create("非法操作"))
        else:
            out = await wows_get_data(cm_0, list_cmd[1])
            await app.sendGroupMessage(group, MessageChain.create([
                Image(data_bytes=out.getvalue())]))
    elif list_cmd[0] == "me":
        if len(list_cmd) == 1:
            lis = get_me_data(message.sender.id)
            if len(lis) == 2:
                out = await get_pr_v2(lis[1], lis[0])
                await app.sendGroupMessage(group, MessageChain.create([
                    Image(data_bytes=out.getvalue())]))
            else:
                await app.sendGroupMessage(group, MessageChain.create("找不到用户"))
        elif list_cmd[1].lower() == 'ship':
            lis = get_me_data(message.sender.id)
            if len(lis) == 2:
                if list_cmd[1].lower() == 'ship':
                    ship_id = get_ship_id(list_cmd[2])
                    if ship_id != '':
                        lis = get_me_data(message.sender.id)
                        out = await wows_get_pl_ship(lis[0], ship_id, lis[1], list_cmd[2])
                        # await app.sendGroupMessage(group, MessageChain.create(str(ship_id)))
                        await app.sendGroupMessage(group, MessageChain.create([
                            Image(data_bytes=out.getvalue())]))
                    else:
                        await app.sendGroupMessage(group, MessageChain.create("找不到船，可能是作者还没有反和谐"))
                else:
                    await app.sendGroupMessage(group, MessageChain.create("找不到用户"))
        elif list_cmd[-1] == "recent":
            lis = get_me_data(message.sender.id)
            user_wows_id = lis[0]
            user_recent_data = wows_sql_data.read_sql_data(user_wows_id)
            if user_recent_data == {}:
                await app.sendGroupMessage(group, MessageChain.create("正在更新或暂时无法查询"))
            else:
                out = await wows_recent(user_wows_id, lis[1], user_recent_data)
                await app.sendGroupMessage(group, out)

    elif list_cmd[0] == "set":
        if not dev:
            server_data = list_cmd[1]
            nickname = list_cmd[2]
            data_json = await wows_getUID(nickname, server_data)
            if data_json["status"] == "ok":
                data = data_json['data'][0]
                wows_UID_tmp = str(data['account_id'])
                add_dic(message.sender.id, wows_UID_tmp, server_data)
                await app.sendGroupMessage(group, MessageChain.create("绑定成功"))
        else:
            await app.sendGroupMessage(group, MessageChain.create("无法在开发状态下绑定"))
    elif list_cmd[-2] == "ship":
        if list_cmd[1] in Server_list:
            name = list_cmd[1]
            server = list_cmd[0]
        else:
            name = list_cmd[0]
            server = "asia"
        ship = list_cmd[-1]
        data_json = await wows_getUID(name, server)
        if data_json["status"] == "ok":
            data = data_json['data'][0]
            wows_id = str(data['account_id'])
            ship_id = get_ship_id(ship)
            if ship_id != '':
                out = await wows_get_pl_ship(str(wows_id), str(ship_id), server, list_cmd[-1])
                # await app.sendGroupMessage(group, MessageChain.create(str(ship_id)))
                await app.sendGroupMessage(group, MessageChain.create([
                    Image(data_bytes=out.getvalue())]))
            else:
                await app.sendGroupMessage(group, MessageChain.create("找不到船，可能是作者还没有反和谐"))
    else:
        out = await wows_get_data("asia", list_cmd[0])
        await app.sendGroupMessage(group, MessageChain.create([
            Image(data_bytes=out.getvalue())]))
