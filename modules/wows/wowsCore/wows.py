# -*- coding: UTF-8 -*-
"""
@Project ：Bot_rain
@File    ：wows.py
@Author  ：INTMAX
@Date    ：2022-06-03 7:48 p.m. 
"""
import asyncio
import math
from graia.ariadne.message.chain import MessageChain
from PIL import Image
from PIL import Image as IMG
from PIL import ImageDraw, ImageFont
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import (FullMatch, MatchResult,
                                                   Twilight, WildcardMatch)
from graia.ariadne.model import Group
from graia.broadcast.interrupt import Waiter, InterruptControl
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
import difflib
from modules.wows import dataBase
from modules.wows import APIs

saya = Saya.current()
channel = Channel.current()
interrupt = InterruptControl(saya.broadcast)
channel.name("wows_helper")
channel.description("发送wows指令来进行查询")
channel.author("IntMax")


async def fun_get_me(sender_id: int) -> dict:
    """
    找找 me 是谁
    :param sender_id: 发送者的 QQ 号
    :return:
    """
    dic_users = dataBase.read_user_data()
    if str(sender_id) in dic_users.keys():
        return dic_users[str(sender_id)]
    else:
        raise APIs.Notfound('找不到绑定数据')


async def fun_get_pr_rank(pr: int):
    """
    获取对应 PR 的图片名
    :param pr:
    :return:
    """
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


async def fun_get_ship_pr(ship: dict):
    """
    计算单船 PR
    :param ship:
    :return:
    """
    ship_exp = dataBase.wows_get_numbers_api()
    ship_id = ship['ship_id']
    ship_exp = ship_exp['data'][str(ship_id)]
    """
    期望数据
    """
    avg_dmg = ship_exp["average_damage_dealt"]
    avg_frags = ship_exp["average_frags"]
    avg_wr = ship_exp["win_rate"]
    """
    实际数据
    """
    pvp = ship['pvp']
    battles = pvp['battles']
    damage_dealt = pvp['damage_dealt']
    wins = pvp['wins']
    frags = pvp['frags']
    """
    与期望的比率
    """
    rDmg = (damage_dealt / battles) / avg_dmg
    rFrags = (frags / battles) / avg_frags
    rWins = (wins / battles) * 100 / avg_wr
    """
    正则化数据
    """
    nDmg = max(0, (rDmg - 0.4) / (1 - 0.4))
    nFrags = max(0, (rFrags - 0.1) / (1 - 0.1))
    nWins = max(0, (rWins - 0.7) / (1 - 0.7))
    """
    计算 PR
    """
    wr = (100 * (wins / battles))
    wr_w = (100 * math.asin(wr / 100)) / 158
    pr = (350 + (350 * wr_w)) * nDmg + 300 * nFrags + (150 + (350 * (1 - wr_w))) * nWins
    pr_rank = await fun_get_pr_rank(int(pr))
    return pr_rank, pr


async def fun_get_gen_pr(server: str, account_id: str):
    """
    计算账号的整体 PR
    :param server: 服务器信息
    :param account_id: Wargaming 的唯一 ID
    :return:
    """
    try:
        shipList = await APIs.fun_get_ship_list(server, account_id)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    """
    逐个计算 PR 与场数进行加权平均
    """
    pr_total = 0
    battles_total = 0
    for ship in shipList:
        try:
            pvp = ship['pvp']
            battles = pvp['battles']
            pr_rank, pr = await fun_get_ship_pr(ship)
            pr_total += pr * battles
            battles_total += battles
        except Exception:
            continue
    pr_avg = pr_total / battles_total
    pr_rank = await fun_get_pr_rank(int(pr_avg))
    return pr_avg, pr_rank


async def fun_gen_img(LV: str, cl: str, name: str, bats: str, wr: str, dmg: str, XP: str, KD: str, accu: str,
                      timestamp_crate: str, PR: str):
    """
    用来绘制战绩图片
    :param LV:
    :param cl:
    :param name:
    :param bats:
    :param wr:
    :param dmg:
    :param XP:
    :param KD:
    :param accu:
    :param timestamp_crate:
    :param PR:
    :return:
    """
    if cl is None:
        cl = "「 」"
    img = IMG.open("wows_pic/" + PR)
    # 新建绘图对象
    draw = ImageDraw.Draw(img)
    # 选择文字字体和大小
    setFont = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 50)
    setFont_big = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 70)
    fillColor = (0, 0, 0)  # 文字颜色：黑色
    dt_object = timestamp_crate
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


async def fun_get_out_img_ship(server: str, account_id: str, ship_id: str):
    """
    根据 account id 和 ship id 生成可输出的单船战绩图片
    :param server: 服务器信息
    :param account_id: Wargaming 的唯一 ID
    :param ship_id: 船只的唯一 ID
    :return:
    """
    try:
        nickname, created_at = await APIs.fun_get_personal_data(server, account_id, mode=1)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    try:
        clan_id = await APIs.fun_get_clan_id(server, account_id)
        clan_tag = await APIs.fun_get_clan_tag(server, clan_id)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    except APIs.UserNoClan:
        clan_tag = '「 」'
    try:
        xp, survived_battles, battles, frags, damage_dealt, wins, \
        main_battery, ship = await APIs.fun_get_ship_data(server, account_id, ship_id)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    pr_rank, pr = await fun_get_ship_pr(ship)
    """
    图片中会出现的数据依次是
    昵称
    船只名称
    创建时间
    PR——等级
    战斗场数
    胜率
    场均
    平均经验
    KD
    主炮命中率
    """
    nickName_img = nickname
    leveling_tier_img = dataBase.get_ship_name(ship_id)
    created_at_img = datetime.fromtimestamp(created_at)
    pr_rank_img = pr_rank
    battles_img = str(battles)
    winRate_img = format(wins / battles, '.2%')
    avgDamage_img = round(damage_dealt / battles)
    avgXP_img = round(xp / battles)
    try:
        KD_img = round((frags / (battles - survived_battles)), 2)
    except Exception:
        KD_img = round((frags+1 / (battles - survived_battles)+1), 2)
    try:
        accuRate = format((main_battery['hits'] / main_battery['shots']), '.2%')
    except Exception:
        accuRate = "N/A"
    img_out = await fun_gen_img(str(leveling_tier_img), str(clan_tag), str(nickName_img), str(battles_img),
                                str(winRate_img), str(avgDamage_img), str(avgXP_img), str(KD_img), str(accuRate),
                                str(created_at_img), str(pr_rank_img))
    img_out.save(out := BytesIO(), format='JPEG')
    return out


async def fun_get_out_img_account_id(server: str, account_id: str):
    """
    根据 account id 生成可输出的战绩图片
    :param server: 服务器信息
    :param account_id: Wargaming 的唯一 ID
    :return:
    """
    try:
        leveling_tier, created_at, nickname, battles, xp, frags, survived_battles, \
        wins, damage_dealt, main_battery = await APIs.fun_get_personal_data(server, account_id, mode=0)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    pr, pr_rank = await fun_get_gen_pr(server, account_id)
    try:
        clan_id = await APIs.fun_get_clan_id(server, account_id)
        clan_tag = await APIs.fun_get_clan_tag(server, clan_id)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    except APIs.UserNoClan:
        clan_tag = '「 」'
    """
    图片中会出现的数据依次是
    昵称
    等级
    创建时间
    PR——等级
    战斗场数
    胜率
    场均
    平均经验
    KD
    主炮命中率
    """
    nickName_img = nickname
    leveling_tier_img = "LV" + str(leveling_tier)
    created_at_img = datetime.fromtimestamp(created_at)
    pr_rank_img = pr_rank
    battles_img = str(battles)
    winRate_img = format(wins / battles, '.2%')
    avgDamage_img = round(damage_dealt / battles)
    avgXP_img = round(xp / battles)
    try:
        KD_img = round((frags / (battles - survived_battles)), 2)
    except Exception:
        KD_img = round((frags + 1 / (battles - survived_battles) + 1), 2)
    try:
        accuRate = format((main_battery['hits'] / main_battery['shots']), '.2%')
    except Exception:
        accuRate = "N/A"
    img_out = await fun_gen_img(str(leveling_tier_img), str(clan_tag), str(nickName_img), str(battles_img),
                                str(winRate_img), str(avgDamage_img), str(avgXP_img), str(KD_img), str(accuRate),
                                str(created_at_img), str(pr_rank_img))
    img_out.save(out := BytesIO(), format='JPEG')
    return out


async def fun_get_recent_img(server: str, account_id: str):
    """
    生成近期战绩的 img
    :param server: 服务器信息
    :param account_id: Wargaming 的唯一 ID
    :return:
    """
    dic_past = dataBase.read_sql_data(account_id)
    try:
        leveling_tier, created_at, nickname, battles, xp, frags, survived_battles, \
        wins, damage_dealt, main_battery = await APIs.fun_get_personal_data(server, account_id, mode=0)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    if dic_past == {}:
        raise APIs.Notfound("正在更新或绑定当天无法查询")
    try:
        shipList = await APIs.fun_get_ship_list(server, account_id)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    pr_total = 0
    battles_recent = 0
    wins_recent = 0
    frags_recent = 0
    damage_dealt_recent = 0
    try:
        clan_id = await APIs.fun_get_clan_id(server, account_id)
        clan_tag = await APIs.fun_get_clan_tag(server, clan_id)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    for ship in shipList:
        try:
            ship_id = ship['ship_id']
            pvp = ship['pvp']
            battles = pvp['battles']
            damage_dealt = pvp['damage_dealt']
            wins = pvp['wins']
            frags = pvp['frags']
            ship_tmp = {}
            if battles != dic_past[str(ship_id)]['battles']:
                battles_recent_tmp = battles - dic_past[str(ship_id)]['battles']
                wins_recent_tmp = wins - dic_past[str(ship_id)]['wins']
                frags_recent_tmp = frags - dic_past[str(ship_id)]['frags']
                damage_dealt_recent_tmp = damage_dealt - dic_past[str(ship_id)]['damage_dealt']
                pvp = {'battles': battles - dic_past[str(ship_id)]['battles'],
                       'wins': wins - dic_past[str(ship_id)]['wins'],
                       'frags': frags - dic_past[str(ship_id)]['frags'],
                       'damage_dealt': damage_dealt - dic_past[str(ship_id)]['damage_dealt']}
                ship_tmp['ship_id'] = ship_id
                ship_tmp['pvp'] = pvp
                battles_recent += battles_recent_tmp
                wins_recent += wins_recent_tmp
                frags_recent += frags_recent_tmp
                damage_dealt_recent += damage_dealt_recent_tmp
                pr_rank, pr = await fun_get_ship_pr(ship)
                pr_total += pr * battles_recent_tmp
        except Exception:
            continue
    if battles_recent == 0:
        raise APIs.Notfound("近期可能无数据或无法查询")
    else:
        pr_recent = pr_total / battles_recent
        pr_rank_recent = await fun_get_pr_rank(pr_recent)
        recent_img = await fun_gen_img("PR = " + str(round(pr_recent)), str(clan_tag), str(nickname),
                                       str(battles_recent),
                                       str(format(wins_recent / battles_recent, '.2%')),
                                       str(round(damage_dealt_recent / battles_recent)), "N/A", "N/A", "N/A",
                                       str(datetime.fromtimestamp(created_at)), pr_rank_recent)
        recent_img.save(out := BytesIO(), format='JPEG')
        return out


async def fun_get_rank_data(server: str, account_id: str):
    """
    根据 account id 找 rank 的数据
    :param server: 服务器信息
    :param account_id: Wargaming 的唯一 ID
    :return: 
    """
    try:
        battles, winRate, xp, damage, kd = await APIs.fun_get_rank_data(server, account_id)
        return battles, winRate, xp, damage, kd
    except APIs.ApiError as e:
        raise e
    except Exception:
        raise APIs.Notfound("数据异常，可能是本赛季没有 Rank 数据")


async def fun_get_rank_img(server: str, account_id: str):
    """
    生成 rank 的图片
    :param server:
    :param account_id:
    :return:
    """
    try:
        nickname, created_at = await APIs.fun_get_personal_data(server, account_id, mode=1)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    try:
        battles, winRate, xp, damage, kd = await fun_get_rank_data(server, account_id)
    except Exception as e:
        raise e
    try:
        clan_id = await APIs.fun_get_clan_id(server, account_id)
        clan_tag = await APIs.fun_get_clan_tag(server, clan_id)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    except APIs.UserNoClan:
        clan_tag = '「 」'
    rank_img = await fun_gen_img("Rank 模式下 PR 不可用", str(clan_tag), str(nickname), str(battles), str(winRate),
                                 str(damage), str(xp), str(kd), "N/A", str(datetime.fromtimestamp(created_at)),
                                 "wows_unknown.jpg")
    rank_img.save(out := BytesIO(), format='JPEG')
    return out


async def fun_wows_me_rank(sender_id: str):
    """
    处理 rank 的情况
    :param sender_id: 发送者的 QQ 号
    :return:
    """
    try:
        userData = await fun_get_me(sender_id)
    except APIs.Notfound:
        raise APIs.Notfound('找不到绑定数据')
    account_id = userData[0]
    server = userData[1]
    try:
        out = await fun_get_rank_img(server, account_id)
        return out
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e


async def fun_wows_username_rank(server: str, nickName: str):
    """
    处理 wows exboom rank 的情况 和 wows asia exboom rank 的情况
    :param server:
    :param nickName:
    :return:
    """
    try:
        account_id = await APIs.fun_get_userid(server, nickName)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    try:
        out = await fun_get_rank_img(server, account_id)
        return out
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e


async def fun_wows_me_recent(sender_id: str):
    """
    处理 recent 的情况
    :param sender_id: 发送者的 QQ 号
    :return:
    """
    try:
        userData = await fun_get_me(sender_id)
    except APIs.Notfound:
        raise APIs.Notfound('找不到绑定数据')
    account_id = userData[0]
    server = userData[1]
    try:
        out = await fun_get_recent_img(server, account_id)
        return out
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e


async def fun_wows_userName(server: str, nickName: str):
    """
    用来处理 wows exboom 的情况
    或者 wows asia exboom 的情况
    :param server: 服务器信息
    :param nickName: 用户昵称
    :return:
    """
    try:
        account_id = await APIs.fun_get_userid(server, nickName)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    try:
        out = await fun_get_out_img_account_id(server, account_id)
        return out
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e


async def fun_wows_me_ship(sender_id: str, ship_id):
    """
    用来处理 wows me ship 大胆 的情况
    :param sender_id: 发送者的 QQ 号
    :param ship_id: 船只的唯一 ID
    :return:
    """
    try:
        userData = await fun_get_me(sender_id)
    except APIs.Notfound:
        raise APIs.Notfound('找不到绑定数据')
    account_id = userData[0]
    server = userData[1]
    try:
        out = await fun_get_out_img_ship(server, account_id, ship_id)
        return out
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e


async def fun_wows_username_ship(server: str, nickName: str, ship_id: str):
    """
    用来处理 wows exboom ship 大胆
    和 wows asia exboom ship 大胆 的情况
    :param ship_id: 船只的唯一 ID
    :param server: 服务器信息
    :param nickName: 用户昵称
    :return:
    """
    try:
        account_id = await APIs.fun_get_userid(server, nickName)
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e
    try:
        out = await fun_get_out_img_ship(server, account_id, ship_id)
        return out
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e


async def fun_wows_me(sender_id: int):
    """
    用来处理 wows me 的情况
    :param sender_id: 发送者的 QQ 号
    :return:
    """
    try:
        userData = await fun_get_me(sender_id)
    except APIs.Notfound:
        raise APIs.Notfound('找不到绑定数据')
    account_id = userData[0]
    server = userData[1]
    try:
        out = await fun_get_out_img_account_id(server, account_id)
        return out
    except (APIs.Notfound, APIs.ApiError) as e:
        raise e


def fun_fuzzy_finder(shipInputName: str):
    dict_temp = {}
    with open("src/wows_data/wows_ship_official_name.txt", 'r') as f:
        for line in f.readlines():
            line = line.strip()
            k = line.split(' ')[0]
            v = line.split(' ')[1]
            dict_temp[v] = k
        list_find = difflib.get_close_matches(shipInputName, dict_temp.keys(), 5, cutoff=0.2)
        return list_find


def fun_get_reply(ship_list: list):
    msg_rep = ''
    if len(ship_list) != 0:
        if len(ship_list) == 2:
            msg_rep = f'猜你想找\n' \
                      f'1.{ship_list[0]}\n' \
                      f'2.{ship_list[1]}'
        elif len(ship_list) == 3:
            msg_rep = f'猜你想找\n' \
                      f'1.{ship_list[0]}\n' \
                      f'2.{ship_list[1]}\n' \
                      f'3.{ship_list[2]}'
        elif len(ship_list) == 4:
            msg_rep = f'猜你想找\n' \
                      f'1.{ship_list[0]}\n' \
                      f'2.{ship_list[1]}\n' \
                      f'3.{ship_list[2]}\n' \
                      f'4.{ship_list[3]}\n'
        elif len(ship_list) == 5:
            msg_rep = f'猜你想找\n' \
                      f'1.{ship_list[0]}\n' \
                      f'2.{ship_list[1]}\n' \
                      f'3.{ship_list[2]}\n' \
                      f'4.{ship_list[3]}\n' \
                      f'5.{ship_list[4]}'
        return msg_rep


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("wows"),
         WildcardMatch(optional=True) @ "para"]
    )]
))
async def wows(app: Ariadne, group: Group, para: MatchResult, message: GroupMessage, member: Member):
    int_str = para.result.asDisplay().strip() if para.matched else ''
    list_cmd = int_str.split()
    Server_list = ["asia", "eu", "na", "ru"]
    '''
       wows指令判断
       '''
    if len(list_cmd) == 1:
        '''当指令长度为1时只有wows me 和 wows exboom wows help 3种情况'''
        if list_cmd[0] == 'me':
            '''
            wows me
            直接去找me 并且判断是否含有服务器和UID信息
            '''
            try:
                out = await fun_wows_me(message.sender.id)
                await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
            except (APIs.Notfound, APIs.ApiError) as e:
                await app.sendGroupMessage(group, MessageChain.create(e.args))
        elif list_cmd[0] == 'help':
            """
            简易的help
            """
            await app.sendGroupMessage(group, MessageChain.create("完整指令请尝试/help\n"
                                                                  "wows set 服务器 你的wows名字"
                                                                  "\n服务器从[asia, eu, na, ru]中选择"))
        elif list_cmd[0] == '正常模式' and message.sender.id == 563748846:
            dataBase.set_dev("0")
            await app.sendGroupMessage(group, MessageChain.create("已修改"))
        else:
            '''wows exboom 默认去找亚服当exboom'''
            nickName = list_cmd[0]
            server = "asia"
            try:
                out = await fun_wows_userName(server, nickName)
                await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
            except (APIs.Notfound, APIs.ApiError) as e:
                await app.sendGroupMessage(group, MessageChain.create(e.args))

    elif len(list_cmd) == 2:
        '''
        当指令长度为2时
        会出现wows me recent 和 wows asia exboom
        wows me rank 
        wows exboom rank
        '''
        if list_cmd[-1] == 'recent':
            '''
            当有人尝试查询recent
            先看看他是否在查自己
            随后找出数据
            '''
            if list_cmd[0] == 'me':
                try:
                    out = await fun_wows_me_recent(message.sender.id)
                    await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
                except (APIs.Notfound, APIs.ApiError) as e:
                    await app.sendGroupMessage(group, MessageChain.create(e.args))
            else:
                await app.sendGroupMessage(group, MessageChain.create("暂不支持非绑定查询"))
        elif list_cmd[-1] == 'rank':
            '''
            当有人尝试查询recent
            先看看他是否在查自己
            随后找出数据
            '''
            if list_cmd[0] == 'me':
                try:
                    out = await fun_wows_me_rank(message.sender.id)
                    await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
                except (APIs.Notfound, APIs.ApiError) as e:
                    await app.sendGroupMessage(group, MessageChain.create(e.args))
            else:
                try:
                    nickName = list_cmd[0]
                    out = await fun_wows_username_rank('asia', nickName)
                    await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
                except (APIs.Notfound, APIs.ApiError) as e:
                    await app.sendGroupMessage(group, MessageChain.create(e.args))
        elif list_cmd[0] in Server_list:
            '''
            当有人查wows asia exboom
            找亚服中当exboom
            '''
            nickName = list_cmd[1]
            server = list_cmd[0]
            try:
                out = await fun_wows_userName(server, nickName)
                await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
            except (APIs.Notfound, APIs.ApiError) as e:
                await app.sendGroupMessage(group, MessageChain.create(e.args))
        else:
            await app.sendGroupMessage(group, MessageChain.create("未知指令"))
    elif len(list_cmd) == 3:
        '''
        当指令为3时可能出现
        wows me ship 大胆
        wows exboom ship 大胆
        wows set asia exboom
        wows asia exboom rank
        '''
        if list_cmd[0] == 'me' and list_cmd[-2] == 'ship':
            """
            wows me ship 大胆
            """
            shipInputName = list_cmd[2]
            ship_id = dataBase.get_ship_id(shipInputName)
            if ship_id != '':
                try:
                    out = await fun_wows_me_ship(str(message.sender.id), ship_id)
                    await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
                except (APIs.Notfound, APIs.ApiError) as e:
                    await app.sendGroupMessage(group, MessageChain.create(e.args))
            else:
                shipInputName = shipInputName.upper()
                ship_list = fun_fuzzy_finder(shipInputName)
                if len(ship_list) < 1:
                    await app.sendMessage(group, MessageChain.create("猜不到你想找什么船"))
                elif len(ship_list) == 1:
                    ship_id = dataBase.get_ship_id(ship_list[0])
                    try:
                        out = await fun_wows_me_ship(str(message.sender.id), ship_id)
                        await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
                    except (APIs.Notfound, APIs.ApiError) as e:
                        await app.sendGroupMessage(group, MessageChain.create(e.args))
                elif 1 < len(ship_list) <= 5:
                    msg_reply = fun_get_reply(ship_list)
                    await app.sendGroupMessage(group, MessageChain.create(msg_reply))

                    @Waiter.create_using_function([GroupMessage])
                    async def InterruptWaiter(g: Group, m: Member, msg: MessageChain):
                        if group.id == g.id and member.id == m.id:
                            return msg

                    try:
                        rep_msg: message = await interrupt.wait(InterruptWaiter, timeout=15)
                        rep_str: str = rep_msg.asDisplay()
                        lenList = len(ship_list)
                        rep_int = int(rep_str)
                        if 0 < rep_int <= lenList:
                            ship_id = dataBase.get_ship_id_fuzzy(ship_list[rep_int - 1])
                            """
                            找到 ship id 复用
                            """
                            try:
                                out = await fun_wows_me_ship(str(message.sender.id), ship_id)
                                await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
                            except (APIs.Notfound, APIs.ApiError) as e:
                                await app.sendGroupMessage(group, MessageChain.create(e.args))
                        else:
                            await app.sendMessage(group, MessageChain.create("这样可没人愿意帮你找的！"))
                    except asyncio.TimeoutError:
                        await app.sendMessage(group, MessageChain.create("不说就当没有了！"))
        elif list_cmd[0] in Server_list and list_cmd[-1] == 'rank':
            try:
                nickName = list_cmd[1]
                server = list_cmd[0]
                out = await fun_wows_username_rank(server, nickName)
                await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
            except (APIs.Notfound, APIs.ApiError) as e:
                await app.sendGroupMessage(group, MessageChain.create(e.args))
        elif list_cmd[0] != 'set' and list_cmd[-2] == 'ship':
            """
            wows exboom ship 大胆
            """
            nickName = list_cmd[0]
            server = "asia"
            shipInputName = list_cmd[-1]
            ship_id = dataBase.get_ship_id(shipInputName)
            if ship_id != '':
                try:
                    out = await fun_wows_username_ship(server, nickName, ship_id)
                    await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
                except (APIs.Notfound, APIs.ApiError) as e:
                    await app.sendGroupMessage(group, MessageChain.create(e.args))
            else:
                """
                模糊搜索
                """
                shipInputName = shipInputName.upper()
                ship_list = fun_fuzzy_finder(shipInputName)
                if len(ship_list) < 1:
                    await app.sendMessage(group, MessageChain.create("猜不到你想找什么船"))
                elif len(ship_list) == 1:
                    ship_id = dataBase.get_ship_id(ship_list[0])
                    try:
                        out = await fun_wows_me_ship(str(message.sender.id), ship_id)
                        await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
                    except (APIs.Notfound, APIs.ApiError) as e:
                        await app.sendGroupMessage(group, MessageChain.create(e.args))
                elif 1 < len(ship_list) <= 5:
                    msg_reply = fun_get_reply(ship_list)
                    await app.sendGroupMessage(group, MessageChain.create(msg_reply))

                    @Waiter.create_using_function([GroupMessage])
                    async def InterruptWaiter(g: Group, m: Member, msg: MessageChain):
                        if group.id == g.id and member.id == m.id:
                            return msg

                    try:
                        rep_msg: message = await interrupt.wait(InterruptWaiter, timeout=15)
                        rep_str: str = rep_msg.asDisplay()
                        lenList = len(ship_list)
                        rep_int = int(rep_str)
                        if 0 < rep_int <= lenList:
                            ship_id = dataBase.get_ship_id_fuzzy(ship_list[rep_int - 1])
                            """
                            找到 ship id 复用
                            """
                            try:
                                out = await fun_wows_username_ship(server, nickName, ship_id)
                                await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
                            except (APIs.Notfound, APIs.ApiError) as e:
                                await app.sendGroupMessage(group, MessageChain.create(e.args))
                        else:
                            await app.sendMessage(group, MessageChain.create("这样可没人愿意帮你找的！"))
                    except asyncio.TimeoutError:
                        await app.sendMessage(group, MessageChain.create("不说就当没有了！"))
        elif list_cmd[0] == 'set' and list_cmd[-2] in Server_list:
            if not dataBase.get_dev():
                server = list_cmd[1]
                nickName = list_cmd[2]
                try:
                    account_id = await APIs.fun_get_userid(server, nickName)
                    try:
                        dataBase.add_user(message.sender.id, account_id, server)
                        await app.sendGroupMessage(group, MessageChain.create("绑定成功"))
                    except Exception as e:
                        await app.sendGroupMessage(group, MessageChain.create(e.args))
                except (APIs.Notfound, APIs.ApiError) as e:
                    await app.sendGroupMessage(group, MessageChain.create(e.args))
            else:
                await app.sendGroupMessage(group, MessageChain.create("无法在开发状态下绑定"))
        else:
            await app.sendGroupMessage(group, MessageChain.create("未知指令"))
    elif len(list_cmd) == 4:
        '''
        当指令为4时可能出现
        wows asia exboom ship 大胆
        '''
        if list_cmd[0] in Server_list and list_cmd[-2] == 'ship':
            server = list_cmd[0]
            nickName = list_cmd[1]
            shipInputName = list_cmd[-1]
            ship_id = dataBase.get_ship_id(shipInputName)
            if ship_id != '':
                try:
                    out = await fun_wows_username_ship(server, nickName, ship_id)
                    await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
                except (APIs.Notfound, APIs.ApiError) as e:
                    await app.sendGroupMessage(group, MessageChain.create(e.args))
            else:
                """
                模糊搜索
                """
                shipInputName = shipInputName.upper()
                ship_list = fun_fuzzy_finder(shipInputName)
                if len(ship_list) < 1:
                    await app.sendMessage(group, MessageChain.create("猜不到你想找什么船"))
                elif len(ship_list) == 1:
                    ship_id = dataBase.get_ship_id(ship_list[0])
                    try:
                        out = await fun_wows_me_ship(str(message.sender.id), ship_id)
                        await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
                    except (APIs.Notfound, APIs.ApiError) as e:
                        await app.sendGroupMessage(group, MessageChain.create(e.args))
                elif 1 < len(ship_list) <= 5:
                    msg_reply = fun_get_reply(ship_list)
                    await app.sendGroupMessage(group, MessageChain.create(msg_reply))

                    @Waiter.create_using_function([GroupMessage])
                    async def InterruptWaiter(g: Group, m: Member, msg: MessageChain):
                        if group.id == g.id and member.id == m.id:
                            return msg

                    try:
                        rep_msg: message = await interrupt.wait(InterruptWaiter, timeout=15)
                        rep_str: str = rep_msg.asDisplay()
                        lenList = len(ship_list)
                        rep_int = int(rep_str)
                        if 0 < rep_int <= lenList:
                            ship_id = dataBase.get_ship_id_fuzzy(ship_list[rep_int - 1])
                            """
                            找到 ship id 复用
                            """
                            try:
                                out = await fun_wows_username_ship(server, nickName, ship_id)
                                await app.sendGroupMessage(group, MessageChain.create(Image(data_bytes=out.getvalue())))
                            except (APIs.Notfound, APIs.ApiError) as e:
                                await app.sendGroupMessage(group, MessageChain.create(e.args))
                        else:
                            await app.sendMessage(group, MessageChain.create("这样可没人愿意帮你找的！"))
                    except asyncio.TimeoutError:
                        await app.sendMessage(group, MessageChain.create("不说就当没有了！"))

        else:
            await app.sendGroupMessage(group, MessageChain.create("未知指令"))
    else:
        await app.sendGroupMessage(group, MessageChain.create("过多或过少的参数"))
