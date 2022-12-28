# -*- coding: UTF-8 -*-
"""
@Project ：Bot_rain
@File    ：APIs.py
@Author  ：INTMAX
@Date    ：2022-06-03 7:50 p.m.
"""
import asyncio
import json
import math
import datetime
from io import BytesIO

import aiofiles
from PIL import ImageFont
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from bs4 import BeautifulSoup
from graia.ariadne.util.async_exec import io_bound
from PIL import ImageDraw
import aiohttp
import ApiKeys
from modules.wows import dataBase
import cv2 as cv

"""
@Describe: 战舰世界查询/更新可能会用到的 API
@rule: 尽可能使用官方 API ，必要时使用第三方 API，如使用第三方API需要在API失效时也可正常运作
"""

'''
wows 的应用程序 ID
'''

application_id = ApiKeys.wowsApikey

"""
Wargaming 提供的API
"""

'''
获取玩家 account_id 的 API
'''
wows_account_players_ru = 'https://api.worldofwarships.ru/wows/account/list/'
wows_account_players_eu = 'https://api.worldofwarships.eu/wows/account/list/'
wows_account_players_na = 'https://api.worldofwarships.com/wows/account/list/'
wows_account_players_asia = 'https://api.worldofwarships.asia/wows/account/list/'

'''
根据 account_id 获取基础玩家基础信息的 API
'''

wows_account_player_personal_data_ru = 'https://api.worldofwarships.ru/wows/account/info/'
wows_account_player_personal_data_eu = 'https://api.worldofwarships.eu/wows/account/info/'
wows_account_player_personal_data_na = 'https://api.worldofwarships.com/wows/account/info/'
wows_account_player_personal_data_asia = 'https://api.worldofwarships.asia/wows/account/info/'

'''
根据 account_id 获取玩家 clan_id 的 API
'''

wows_clans_player_clan_data_ru = 'https://api.worldofwarships.ru/wows/clans/accountinfo/'
wows_clans_player_clan_data_eu = 'https://api.worldofwarships.eu/wows/clans/accountinfo/'
wows_clans_player_clan_data_na = 'https://api.worldofwarships.com/wows/clans/accountinfo/'
wows_clans_player_clan_data_asia = 'https://api.worldofwarships.asia/wows/clans/accountinfo/'

'''
根据 clan_id 获取军团 tag
'''

wows_clans_clan_details_ru = 'https://api.worldofwarships.ru/wows/clans/info/'
wows_clans_clan_details_eu = 'https://api.worldofwarships.eu/wows/clans/info/'
wows_clans_clan_details_na = 'https://api.worldofwarships.com/wows/clans/info/'
wows_clans_clan_details_asia = 'https://api.worldofwarships.asia/wows/clans/info/'

'''
根据 account_id 查询船只数据
'''
wows_warship_stat_ru = 'https://api.worldofwarships.ru/wows/ships/stats/'
wows_warship_stat_eu = 'https://api.worldofwarships.eu/wows/ships/stats/'
wows_warship_stat_na = 'https://api.worldofwarships.com/wows/ships/stats/'
wows_warship_stat_asia = 'https://api.worldofwarships.asia/wows/ships/stats/'

"""
非 Wargaming 官方 API
"""

api_wargaming_rank_ru = 'http://wows.ru.intmax.top/community/accounts/tab/rank/overview/'
api_wargaming_rank_eu = 'http://wows.eu.intmax.top/community/accounts/tab/rank/overview/'
api_wargaming_rank_na = 'http://wows.na.intmax.top/community/accounts/tab/rank/overview/'
api_wargaming_rank_asia = 'http://wows.asia.intmax.top/community/accounts/tab/rank/overview/'

"""
逆向工程 API
"""

"""
根据 account_id, ship_id 查询船只数据 // 逆向工程 API
"""

wows_warship_stat_re = 'https://vortex.worldofwarships.'


class NetError(Exception):
    """
        网络状态异常
    """

    def __init__(self, arg):
        self.args = arg


class APIError(Exception):
    """
        参数不正确找不到类型
    """

    def __init__(self, arg):
        self.args = arg


class Notfound(Exception):
    """
        user 找不到类型
    """

    def __init__(self, arg):
        self.args = arg


async def read_ship_dic_api():
    async with aiofiles.open('src/wows_data/wows_ship_list.json', 'r') as f:
        js = await f.read()
        json_dic = json.loads(js)
        return json_dic


@io_bound
def fun_gen_img_cv2(hit_tag: str, clan: str, nickName: str, battles: str, winRate: str, damage: str, XP: str, KD: str,
                    accu: str, timestamp_crate: str, PR: str, draws: dict, Fort: dict):
    """
    用 CV2 来绘制战绩图片
    :param hit_tag: 介于昵称与创建时间的变量
    :param clan: 军团TAG
    :param nickName: 昵称
    :param battles: 战斗场数
    :param winRate: 胜率
    :param damage: 伤害
    :param XP: 经验
    :param KD: KD
    :param accu: 主炮精准度
    :param timestamp_crate: 账号创建时间
    :param PR: PR等级字符串
    :param draws: 预加载的图片
    :param Fort: 预加载的字体
    :return: 二进制图片
    """
    # 复制图片
    img = draws[PR][1].copy()
    # 字体设置
    FORT = cv.FONT_HERSHEY_SIMPLEX
    FONT_THICKNESS = 5
    FONT_SCALE = 1.5
    FONT_THICKNESS_BIG = 7
    FONT_SCALE_BIG = 1.9
    # 绘制
    (label_width, label_height), baseline = cv.getTextSize(hit_tag, FORT, FONT_SCALE_BIG, FONT_THICKNESS_BIG)
    org = (int(625 - (int(label_width) / 2)), 400)
    cv.putText(img, hit_tag, org, FORT, FONT_SCALE_BIG, (0, 0, 0), FONT_THICKNESS_BIG)

    (label_width, label_height), baseline = cv.getTextSize(timestamp_crate, FORT, FONT_SCALE, FONT_THICKNESS)
    org = (int(625 - (int(label_width) / 2)), 590)
    cv.putText(img, timestamp_crate, org, FORT, FONT_SCALE, (0, 0, 0), FONT_THICKNESS)

    (label_width, label_height), baseline = cv.getTextSize(clan, FORT, FONT_SCALE_BIG, FONT_THICKNESS_BIG)
    org = (int(625 - (int(label_width) / 2)), 150)
    cv.putText(img, clan, org, FORT, FONT_SCALE_BIG, (0, 0, 0), FONT_THICKNESS_BIG)

    (label_width, label_height), baseline = cv.getTextSize(nickName, FORT, FONT_SCALE_BIG, FONT_THICKNESS_BIG)
    org = (int(625 - (int(label_width) / 2)), 270)
    cv.putText(img, nickName, org, FORT, FONT_SCALE_BIG, (0, 0, 0), FONT_THICKNESS_BIG)

    (label_width, label_height), baseline = cv.getTextSize(battles, FORT, FONT_SCALE, FONT_THICKNESS)
    org = (int(245 - (int(label_width) / 2)), 1190)
    cv.putText(img, battles, org, FORT, FONT_SCALE, (0, 0, 0), FONT_THICKNESS)

    (label_width, label_height), baseline = cv.getTextSize(winRate, FORT, FONT_SCALE, FONT_THICKNESS)
    org = (int(630 - (int(label_width) / 2)), 1190)
    cv.putText(img, winRate, org, FORT, FONT_SCALE, (0, 0, 0), FONT_THICKNESS)

    (label_width, label_height), baseline = cv.getTextSize(damage, FORT, FONT_SCALE, FONT_THICKNESS)
    org = (int(1040 - (int(label_width) / 2)), 1190)
    cv.putText(img, damage, org, FORT, FONT_SCALE, (0, 0, 0), FONT_THICKNESS)

    (label_width, label_height), baseline = cv.getTextSize(XP, FORT, FONT_SCALE, FONT_THICKNESS)
    org = (int(245 - (int(label_width) / 2)), 1720)
    cv.putText(img, XP, org, FORT, FONT_SCALE, (0, 0, 0), FONT_THICKNESS)

    (label_width, label_height), baseline = cv.getTextSize(KD, FORT, FONT_SCALE, FONT_THICKNESS)
    org = (int(630 - (int(label_width) / 2)), 1720)
    cv.putText(img, KD, org, FORT, FONT_SCALE, (0, 0, 0), FONT_THICKNESS)

    (label_width, label_height), baseline = cv.getTextSize(accu, FORT, FONT_SCALE, FONT_THICKNESS)
    org = (int(1040 - (int(label_width) / 2)), 1720)
    cv.putText(img, accu, org, FORT, FONT_SCALE, (0, 0, 0), FONT_THICKNESS)

    is_success, im_buf_arr = cv.imencode(".jpg", img)

    byte_im = im_buf_arr.tobytes()
    return byte_im


@io_bound
def fun_gen_img(hit_tag: str, clan: str, nickName: str, battles: str, winRate: str, damage: str, XP: str, KD: str,
                accu: str,
                timestamp_crate: str, PR: str, draws: dict, Fort: dict):
    """
    用 PIL 来绘制战绩图片
    :param hit_tag: 介于昵称与创建时间的变量
    :param clan: 军团TAG
    :param nickName: 昵称
    :param battles: 战斗场数
    :param winRate: 胜率
    :param damage: 伤害
    :param XP: 经验
    :param KD: KD
    :param accu: 主炮精准度
    :param timestamp_crate: 账号创建时间
    :param PR: PR等级字符串
    :param draws: 预加载的图片
    :param Fort: 预加载的字体
    :return: 二进制图片
    """
    img = draws[PR][0].copy()
    # 新建绘图对象
    draw = ImageDraw.Draw(img)
    # 选择文字字体和大小
    setFont = Fort['setFont']
    setFont_big = Fort['setFont_big']
    fillColor = (0, 0, 0)  # 文字颜色：黑色
    w, h = setFont.getsize(hit_tag)
    draw.text((621 - (w / 2), 340), hit_tag, font=setFont, fill=fillColor)
    w, h = setFont.getsize(timestamp_crate)
    draw.text((621 - (w / 2), 520), timestamp_crate, font=setFont, fill=fillColor)
    w, h = setFont_big.getsize(clan)
    draw.text((621 - (w / 2), 100), clan, font=setFont_big, fill=fillColor)
    w, h = setFont_big.getsize(nickName)
    draw.text((621 - (w / 2), 200), nickName, font=setFont_big, fill=fillColor)
    w, h = setFont.getsize(battles)
    draw.text((245 - (w / 2), 1170), battles, font=setFont, fill=fillColor)
    w, h = setFont.getsize(winRate)
    draw.text((630 - (w / 2), 1170), winRate, font=setFont, fill=fillColor)
    w, h = setFont.getsize(damage)
    draw.text((1040 - (w / 2), 1170), damage, font=setFont, fill=fillColor)
    w, h = setFont.getsize(XP)
    draw.text((245 - (w / 2), 1700), XP, font=setFont, fill=fillColor)
    w, h = setFont.getsize(KD)
    draw.text((630 - (w / 2), 1700), KD, font=setFont, fill=fillColor)
    w, h = setFont.getsize(accu)
    draw.text((1040 - (w / 2), 1700), accu, font=setFont, fill=fillColor)
    img.save(out := BytesIO(), format='JPEG')
    return out.getvalue()


@io_bound
def fun_gen_recent_img(battles: str, winRate: str, damage: str, XP: str, accuRate: str, nickName: str, PR: str,
                       clan_tag: str, KD: str, pr_tag: str, pr_color, PRList: list, shipList: list):
    font_path = "src/font/SourceHanSans-Medium.otf"  # Your font path goes here
    fm.fontManager.addfont(font_path)
    prop = fm.FontProperties(fname=font_path)

    plt.rcParams['font.family'] = prop.get_name()
    plt.rcParams['mathtext.fontset'] = 'cm'  # 'cm' (Computer Modern)

    img_head = Image.open('wows_pic/wows_recent.jpg')
    draw_head = ImageDraw.Draw(img_head)
    PR_tag = pr_tag
    today = str((datetime.date.today() - datetime.timedelta(days=30)).day)
    x = [
        str((datetime.date.today() - datetime.timedelta(days=6)).day),
        str((datetime.date.today() - datetime.timedelta(days=5)).day),
        str((datetime.date.today() - datetime.timedelta(days=4)).day),
        str((datetime.date.today() - datetime.timedelta(days=3)).day),
        str((datetime.date.today() - datetime.timedelta(days=2)).day),
        str((datetime.date.today() - datetime.timedelta(days=1)).day),
        str((datetime.date.today()).day),
    ]
    y = PRList
    parameters = {'ytick.labelsize': 20,
                  'xtick.labelsize': 20}
    plt.rcParams.update(parameters)
    plt.figure(figsize=(15.525, 6.5), dpi=80)
    plt.plot(x, y, "g", marker='D', markersize=10, label="PR")
    plt.xlabel("日期(只有日)", fontsize=20)
    plt.ylabel("PR", fontsize=20)
    plt.title("近期PR", fontsize=40)
    plt.legend(loc="lower right")
    for x1, y1 in zip(x, y):
        plt.text(x1, y1, str(y1), ha='center', va='bottom', fontsize=25)
    read = BytesIO()
    plt.savefig(read, format="jpg")
    plt.clf()
    img_body = Image.open(read)

    font = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 30)
    font_50 = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 50)

    fillColor = (0, 0, 0)
    PR_Color = pr_color

    w, h = font_50.getsize('「' + clan_tag + '」' + nickName)
    draw_head.text((620 - (w / 2), 30), '「' + clan_tag + '」' + nickName, font=font_50, fill=fillColor)

    draw_head.rectangle((0, 124, 1248, 235), PR_Color)

    w, h = font_50.getsize(PR_tag + ' ' + PR)
    draw_head.text((620 - (w / 2), 140), PR_tag + ' ' + PR, font=font_50, fill=fillColor)

    w, h = font.getsize(battles)
    draw_head.text((135 - (w / 2), 480), battles, font=font, fill=fillColor)
    w, h = font.getsize(winRate)
    draw_head.text((335 - (w / 2), 480), winRate, font=font, fill=fillColor)
    w, h = font.getsize(damage)
    draw_head.text((525 - (w / 2), 480), damage, font=font, fill=fillColor)
    w, h = font.getsize(XP)
    draw_head.text((725 - (w / 2), 480), XP, font=font, fill=fillColor)
    w, h = font.getsize(KD)
    draw_head.text((920 - (w / 2), 480), KD, font=font, fill=fillColor)
    w, h = font.getsize(accuRate)
    draw_head.text((1117 - (w / 2), 480), accuRate, font=font, fill=fillColor)
    if len(shipList) <= 15:
        size_ships = len(shipList)
    else:
        size_ships = 15
    img_ships = Image.new('RGB', (1242, 150 + (80 * size_ships)), (255, 255, 255))
    draw_ships = ImageDraw.Draw(img_ships)
    w, h = font_50.getsize('近期船只数据')
    draw_ships.text((620 - (w / 2), 10), '近期船只数据', font=font_50, fill=fillColor)

    w, h = font.getsize('战舰名称')
    draw_ships.text((130 - (w / 2), 100), '战舰名称', font=font, fill=fillColor)
    w, h = font.getsize('场数')
    draw_ships.text((350 - (w / 2), 100), '场数', font=font, fill=fillColor)
    w, h = font.getsize('胜率')
    draw_ships.text((500 - (w / 2), 100), '胜率', font=font, fill=fillColor)
    w, h = font.getsize('场均')
    draw_ships.text((700 - (w / 2), 100), '场均', font=font, fill=fillColor)
    w, h = font.getsize('XP')
    draw_ships.text((850 - (w / 2), 100), 'XP', font=font, fill=fillColor)
    w, h = font.getsize('PR')
    draw_ships.text((1000 - (w / 2), 100), 'PR', font=font, fill=fillColor)
    w, h = font.getsize('击沉')
    draw_ships.text((1150 - (w / 2), 100), '击沉', font=font, fill=fillColor)

    y_pos = 160
    limiter = 0
    for ship_tmp in shipList:
        if limiter >= 15:
            break
        ship_name = ship_tmp['name']
        ship_color = ship_tmp['PR_color']
        ship_battles = str(ship_tmp['pvp']['battles'])
        ship_damage = str(round(ship_tmp['pvp']['damage_dealt'] / ship_tmp['pvp']['battles']))
        ship_winRate = str(format(ship_tmp['pvp']['wins'] / ship_tmp['pvp']['battles'], '.2%'))
        ship_Kill = str(ship_tmp['pvp']['frags'])
        ship_PR = str(ship_tmp['PR'])
        ship_xp = str(round(ship_tmp['pvp']['xp'] / ship_tmp['pvp']['battles']))
        w, h = font.getsize(ship_name)
        draw_ships.text((130 - (w / 2), y_pos), ship_name, font=font, fill=ship_color)
        w, h = font.getsize(ship_battles)
        draw_ships.text((350 - (w / 2), y_pos), ship_battles, font=font, fill=fillColor)
        w, h = font.getsize(ship_winRate)
        draw_ships.text((500 - (w / 2), y_pos), ship_winRate, font=font, fill=fillColor)
        w, h = font.getsize(ship_xp)
        draw_ships.text((680 - (w / 2), y_pos), ship_damage, font=font, fill=fillColor)
        w, h = font.getsize(ship_xp)
        draw_ships.text((850 - (w / 2), y_pos), ship_xp, font=font, fill=fillColor)
        w, h = font.getsize(ship_PR)
        draw_ships.text((1000 - (w / 2), y_pos), ship_PR, font=font, fill=ship_color)
        w, h = font.getsize(ship_Kill)
        draw_ships.text((1150 - (w / 2), y_pos), ship_Kill, font=font, fill=fillColor)
        y_pos += 80
        limiter += 1

    h_img_ship = img_ships.height

    img_out = Image.new('RGB', (1242, 1120 + h_img_ship), (255, 0, 0))

    img_out.paste(img_head, (0, 0))
    img_out.paste(img_body, (0, 600))
    img_out.paste(img_ships, (0, 1120))

    img_out.save(out := BytesIO(), format='JPEG')
    return out.getvalue()


async def fun_get_pr_color(pr: int):
    if pr >= 2450:
        return '神佬平均', (138, 43, 226)
    elif pr >= 2100:
        return '大佬平均', (255, 0, 255)
    elif pr >= 1750:
        return '很好', (0, 100, 0)
    elif pr >= 1350:
        return '好', (0, 255, 0)
    elif pr >= 1100:
        return "平均水平", (255, 236, 139)
    elif pr >= 750:
        return '低于平均', (238, 173, 14)
    else:
        return '还需努力', (255, 0, 0)


async def fun_get_pr_rank(pr: int):
    """
    获取对应 PR 的图片名
    :param pr: PR 的数字
    :return string: PR底图的文件名
    """
    if pr >= 2450:
        return "draw_god"
    elif pr >= 2100:
        return "draw_dalao"
    elif pr >= 1750:
        return "draw_very_good"
    elif pr >= 1350:
        return "draw_good"
    elif pr >= 1100:
        return "draw_avg"
    elif pr >= 750:
        return "draw_below_avg"
    else:
        return "draw_work_hard"


async def fun_get_ship_pr(ship: dict):
    """
    计算单船 PR
    :param ship: 船只数据
    :return pr: 当前船只的 PR 数值
    :return pr_rank: 当前船只的 PR 水平
    """
    ship_exp = await dataBase.wows_get_numbers_api()
    try:
        ship_id = ship['ship_id']
        ship_exp = ship_exp['data'][str(ship_id)]
    except Exception:
        ship_id = 4255037136
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


async def get_re_pr(ship: dict):
    """
    计算单船 PR
    :param ship: 船只数据
    :return pr: 当前船只的 PR 数值
    :return pr_rank: 当前船只的 PR 水平
    """
    ship_exp = await dataBase.wows_get_numbers_api()
    ship_id = "4255037136"
    ship_exp = ship_exp['data'][ship_id]
    """
    期望数据
    """
    avg_dmg = ship_exp["average_damage_dealt"]
    avg_frags = ship_exp["average_frags"]
    avg_wr = ship_exp["win_rate"]
    """
    实际数据
    """
    pvp = ship
    battles = pvp['battles_count']
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


async def fun_get_gen_pr(shipList: dict):
    """
    计算账号的整体 PR
    :param shipList: 玩家船只列表
    :return pr: 当前玩家 PR 数值
    :return pr_rank: 当前玩家 PR 水平
    """
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
    pr_avg = round(pr_total / battles_total)
    pr_rank = await fun_get_pr_rank(int(pr_avg))
    return pr_avg, pr_rank


async def api_get_account_id(session: aiohttp.ClientSession, nickName: str, server: int) -> dict:
    """
    根据 nickName 获取 account_id
    :param session: aiohttp 的 ClientSession
    :param nickName: 游戏内昵称
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return resp.json: 服务器返回值的 json 转码
    """
    API = ''
    match server:
        case 0:
            API = wows_account_players_asia
        case 1:
            API = wows_account_players_ru
        case 2:
            API = wows_account_players_eu
        case 3:
            API = wows_account_players_na

    params = [('application_id', application_id),
              ('search', nickName)
              ]

    async with session.get(API, params=params) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data['status'] == 'ok':
                return data['data']
            else:
                raise APIError('参数出现错误')
        else:
            raise NetError('Wargaming 的 API 出现问题/网络出现问题')


async def api_get_play_personal_data(session: aiohttp.ClientSession, account_id: str, server: int) -> dict:
    """
    根据 account_id 获取用户数据
    :param session: aiohttp 的 ClientSession
    :param account_id: 用户的 account_id
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return resp.json: 服务器返回值的 json 转码
    """
    API = ''
    match server:
        case 0:
            API = wows_account_player_personal_data_asia
        case 1:
            API = wows_account_player_personal_data_ru
        case 2:
            API = wows_account_player_personal_data_eu
        case 3:
            API = wows_account_player_personal_data_na

    params = [('application_id', application_id),
              ('account_id', account_id)
              ]

    async with session.get(API, params=params) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data['status'] == 'ok':
                return data['data']
            else:
                raise APIError('参数出现错误')
        else:
            raise NetError('Wargaming 的 API 出现问题/网络出现问题')


async def api_get_clan_id(session: aiohttp.ClientSession, account_id: str, server: int) -> dict:
    """
    根据 account_id 获取 clan_id
    :param session: aiohttp 的 ClientSession
    :param account_id: 用户的 account_id
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return resp.json: 服务器返回值的 json 转码
    """
    API = ''
    match server:
        case 0:
            API = wows_clans_player_clan_data_asia
        case 1:
            API = wows_clans_player_clan_data_ru
        case 2:
            API = wows_clans_player_clan_data_eu
        case 3:
            API = wows_clans_player_clan_data_na

    params = [('application_id', application_id),
              ('account_id', account_id)
              ]

    async with session.get(API, params=params) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data['status'] == 'ok':
                return data['data']
            else:
                raise APIError('参数出现错误')
        else:
            raise NetError('Wargaming 的 API 出现问题/网络出现问题')


async def api_get_clan_details(session: aiohttp.ClientSession, clan_id: str, server: int) -> dict:
    """
    获取军团具体信息 主要用来获取 tag
    :param session: aiohttp 的 ClientSession
    :param clan_id: 军团的 clan_id
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return resp.json: 服务器返回值的 json 转码
    """
    API = ''
    match server:
        case 0:
            API = wows_clans_clan_details_asia
        case 1:
            API = wows_clans_clan_details_ru
        case 2:
            API = wows_clans_clan_details_eu
        case 3:
            API = wows_clans_clan_details_na

    params = [('application_id', application_id),
              ('clan_id', clan_id)
              ]

    async with session.get(API, params=params) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data['status'] == 'ok':
                return data['data']
            else:
                raise APIError('参数出现错误')
        else:
            raise NetError('Wargaming 的 API 出现问题/网络出现问题')


async def api_get_player_ship_data(session: aiohttp.ClientSession, account_id: str, server: int) -> dict:
    """
    根据 account_id 获取玩家所有船只的数据
    :param session: aiohttp 的 ClientSession
    :param account_id: 用户的 account_id
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return resp.json: 服务器返回值的 json 转码
    """
    API = ''
    match server:
        case 0:
            API = wows_warship_stat_asia
        case 1:
            API = wows_warship_stat_ru
        case 2:
            API = wows_warship_stat_eu
        case 3:
            API = wows_warship_stat_na
    params = [('application_id', application_id),
              ('account_id', account_id)
              ]
    async with session.get(API, params=params) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data['status'] == 'ok':
                return data['data']
            else:
                raise APIError('参数出现错误')
        else:
            raise NetError('Wargaming 的 API 出现问题/网络出现问题')


async def reapi_get_player_ship_data(session: aiohttp.ClientSession, account_id: str, server: int, ship_id) -> dict:
    API = wows_warship_stat_re
    match server:
        case 0:
            API += "asia"
        case 1:
            API += "ru"
        case 2:
            API += "eu"
        case 3:
            API += "com"
    API += '/api/accounts/{}/ships/{}/pvp/'.format(account_id, ship_id)
    async with session.get(API) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data['status'] == 'ok':
                return data['data']
            else:
                raise APIError('参数出现错误')
        else:
            raise NetError('逆向工程的 API 出现问题/网络出现问题')


async def reapi_get_ships(session: aiohttp.ClientSession, account_id: str, server: int):
    API = wows_warship_stat_re
    match server:
        case 0:
            API += "asia"
        case 1:
            API += "ru"
        case 2:
            API += "eu"
        case 3:
            API += "com"
    API += '/api/accounts/{}/ships/'.format(account_id)
    async with session.get(API) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data['status'] == 'ok':
                return data['data']
            else:
                raise APIError('参数出现错误')
        else:
            raise NetError('逆向工程的 API 出现问题/网络出现问题')


async def api_get_rank_data(server: int, account_id: str) -> str:
    """
    爬取 Wargaming 的 Rank 数据
    :param server: 服务器信息
    :param account_id: Wargaming 用户的唯一ID
    :return:
    """
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }
    API = ''
    match server:
        case 0:
            API = api_wargaming_rank_asia + account_id + "/"
        case 1:
            API = api_wargaming_rank_ru + account_id + "/"
        case 2:
            API = api_wargaming_rank_eu + account_id + "/"
        case 3:
            API = api_wargaming_rank_na + account_id + "/"

    async with aiohttp.ClientSession() as session:
        async with session.get(API, headers=headers) as resp:
            if 200 == resp.status:
                return await resp.text()
            else:
                raise NetError('API 出现问题/网络出现问题')


async def fun_get_rank_data(server: int, account_id: str):
    """
    解析 Rank 数据
    :param server:
    :param account_id:
    :return:
    """
    try:
        getdata = await api_get_rank_data(server, account_id)
        soup = BeautifulSoup(getdata, 'lxml')
        list_get = soup.find('div', class_='_values').text.split()
        battles = list_get[0]
        winRate = list_get[1]
        xp = list_get[2]
        damage = list_get[3]
        kd = list_get[4]
        return battles, winRate, xp, damage, kd
    except Exception as e:
        raise e


async def fun_wows_account_id(session: aiohttp.ClientSession, account_id: str, server: int, draws: dict, Fort: dict):
    """
    根据 account_id 获取玩家概览图
    :param Fort:
    :param draws:
    :param session: aiohttp 的 ClientSession
    :param account_id: 用户的 account_id
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return img: 图片一张
    """
    task = []
    task_get_clan_id = asyncio.create_task(api_get_clan_id(session, account_id, server))
    task.append(task_get_clan_id)
    task_get_warship_detail = asyncio.create_task(api_get_player_ship_data(session, account_id, server))
    task.append(task_get_warship_detail)
    task_get_person_detail = asyncio.create_task(api_get_play_personal_data(session, account_id, server))
    task.append(task_get_person_detail)
    res = await asyncio.gather(*task)
    _init = '_init'
    _NA = 'N/A'
    clan_tag = _init
    PR = _init
    PR_tag = _init
    nickName = _init
    created_at = _init
    battles = _init
    winRate = _init
    damageAvg = _init
    xpAvg = _init
    KD = _init
    accuRate = _init
    for i in range(3):
        match i:
            case 0:
                item = res[0]
                if item[account_id] is None:
                    clan_tag = 'NO CLAN DATA'
                else:
                    clan_id = str(item[account_id]['clan_id'])
                    clan_details = await api_get_clan_details(session, clan_id, server)
                    clan_tag = clan_details[clan_id]['tag']
            case 1:
                item = res[1]
                shipList = item[account_id]
                PR, PR_tag = await fun_get_gen_pr(shipList)
            case 2:
                item = res[2]
                nickName = item[account_id]['nickname']
                battles = item[account_id]['statistics']['pvp']['battles']
                if int(battles) != 0:
                    winRate = format(item[account_id]['statistics']['pvp']['wins'] / int(battles), '.2%')
                    damageAvg = round(item[account_id]['statistics']['pvp']['damage_dealt'] / int(battles))
                    xpAvg = round(item[account_id]['statistics']['pvp']['xp'] / int(battles))
                    if int(battles) - int(item[account_id]['statistics']['pvp']['survived_wins']) != 0:
                        KD = round(item[account_id]['statistics']['pvp']['frags'] / (
                                int(battles) - int(item[account_id]['statistics']['pvp']['survived_battles'])), 2)
                    else:
                        KD = _NA
                else:
                    winRate = _NA
                    damageAvg = _NA
                    xpAvg = _NA
                    KD = _NA
                if int(item[account_id]['statistics']['pvp']['main_battery']['shots']) != 0:
                    accuRate = format(item[account_id]['statistics']['pvp']['main_battery']['hits'] /
                                      item[account_id]['statistics']['pvp']['main_battery']['shots'], '.2%')
                else:
                    accuRate = _NA
                created_at = datetime.datetime.fromtimestamp(item[account_id]['created_at'])
    return await fun_gen_img_cv2('PR=' + str(PR), str(clan_tag), str(nickName), str(battles), str(winRate),
                                 str(damageAvg),
                                 str(xpAvg), str(KD), str(accuRate), str(created_at), str(PR_tag), draws, Fort)


async def fun_wows_account_id_no_clan(session: aiohttp.ClientSession, account_id: str, server: int, clan_tag: str,
                                      draws: dict, Fort: dict):
    """
    根据 account_id 获取玩家概览图
    :param clan_tag:
    :param Fort:
    :param draws:
    :param session: aiohttp 的 ClientSession
    :param account_id: 用户的 account_id
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return img: 图片一张
    """
    task = []
    task_get_warship_detail = asyncio.create_task(api_get_player_ship_data(session, account_id, server))
    task.append(task_get_warship_detail)
    task_get_person_detail = asyncio.create_task(api_get_play_personal_data(session, account_id, server))
    task.append(task_get_person_detail)
    res = await asyncio.gather(*task)
    _init = '_init'
    _NA = 'N/A'
    PR = _init
    PR_tag = _init
    nickName = _init
    created_at = _init
    battles = _init
    winRate = _init
    damageAvg = _init
    xpAvg = _init
    KD = _init
    accuRate = _init
    for i in range(2):
        match i:
            case 0:
                item = res[0]
                shipList = item[account_id]
                PR, PR_tag = await fun_get_gen_pr(shipList)
            case 1:
                item = res[1]
                nickName = item[account_id]['nickname']
                battles = item[account_id]['statistics']['pvp']['battles']
                if int(battles) != 0:
                    winRate = format(item[account_id]['statistics']['pvp']['wins'] / int(battles), '.2%')
                    damageAvg = round(item[account_id]['statistics']['pvp']['damage_dealt'] / int(battles))
                    xpAvg = round(item[account_id]['statistics']['pvp']['xp'] / int(battles))
                    if int(battles) - int(item[account_id]['statistics']['pvp']['survived_wins']) != 0:
                        KD = round(item[account_id]['statistics']['pvp']['frags'] / (
                                int(battles) - int(item[account_id]['statistics']['pvp']['survived_battles'])), 2)
                    else:
                        KD = _NA
                else:
                    winRate = _NA
                    damageAvg = _NA
                    xpAvg = _NA
                    KD = _NA
                if int(item[account_id]['statistics']['pvp']['main_battery']['shots']) != 0:
                    accuRate = format(item[account_id]['statistics']['pvp']['main_battery']['hits'] /
                                      item[account_id]['statistics']['pvp']['main_battery']['shots'], '.2%')
                else:
                    accuRate = _NA
                created_at = datetime.datetime.fromtimestamp(item[account_id]['created_at'])
    return await fun_gen_img_cv2('PR=' + str(PR), str(clan_tag), str(nickName), str(battles), str(winRate),
                                 str(damageAvg),
                                 str(xpAvg), str(KD), str(accuRate), str(created_at), str(PR_tag), draws, Fort)


async def fun_wows_nickName(session: aiohttp.ClientSession, nickName: str, server: int, draws: dict, Fort: dict):
    """
    根据 nickName 获取概览图
    :param Fort:
    :param draws:
    :param session: aiohttp 的 ClientSession
    :param nickName: 游戏内昵称
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return img: 图片一张
    """
    _data = await api_get_account_id(session, nickName, server)
    account_id = str(_data[0]['account_id'])
    return await fun_wows_account_id(session, account_id, server, draws, Fort)


async def fun_wows_me(session: aiohttp.ClientSession, account_id: str, server: int, clan_tag: str, draws: dict,
                      Fort: dict):
    return await fun_wows_account_id_no_clan(session, account_id, server, clan_tag, draws, Fort)


async def fun_get_rank_img(session: aiohttp.ClientSession, server: int, account_id: str, draws: dict, Fort: dict):
    """
    生成 rank 的图片
    :param Fort:
    :param session:
    :param server:
    :param account_id:
    :param draws:
    :return:
    """
    _clan_data = await api_get_clan_id(session, account_id, server)
    if _clan_data[account_id] is None:
        clan_tag = 'NO CLAN DATA'
    else:
        clan_id = str(_clan_data[account_id]['clan_id'])
        clan_details = await api_get_clan_details(session, clan_id, server)
        clan_tag = clan_details[clan_id]['tag']
    _personal_data = await api_get_play_personal_data(session, account_id, server)
    nickName = _personal_data[account_id]['nickname']
    created_at = datetime.datetime.fromtimestamp(_personal_data[account_id]['created_at'])
    try:
        battles, winRate, xp, damage, kd = await fun_get_rank_data(server, account_id)
    except Exception as e:
        raise e
    return await fun_gen_img_cv2("unknown", str(clan_tag), str(nickName), str(battles), str(winRate),
                                 str(damage), str(xp), str(kd), "N/A", str(created_at),
                                 'draw_unknown', draws, Fort)


async def fun_get_me_rank_img(session: aiohttp.ClientSession, server: int, account_id: str, clan_tag: str, draws: dict,
                              Fort: dict):
    _personal_data = await api_get_play_personal_data(session, account_id, server)
    nickName = _personal_data[account_id]['nickname']
    created_at = datetime.datetime.fromtimestamp(_personal_data[account_id]['created_at'])
    try:
        battles, winRate, xp, damage, kd = await fun_get_rank_data(server, account_id)
    except Exception as e:
        raise e
    return await fun_gen_img_cv2("unknown", str(clan_tag), str(nickName), str(battles), str(winRate),
                                 str(damage), str(xp), str(kd), "N/A", str(created_at),
                                 'draw_unknown', draws, Fort)


async def fun_wows_username_rank(session: aiohttp.ClientSession, server: int, nickName: str, draws: dict, Fort: dict):
    """
    处理 wows exboom rank 的情况 和 wows asia exboom rank 的情况
    :param Fort:
    :param draws:
    :param session:
    :param server:
    :param nickName:
    :return:
    """
    try:
        _data = await api_get_account_id(session, nickName, server)
        account_id = str(_data[0]['account_id'])
    except (APIError, NetError) as e:
        raise e
    try:
        out = await fun_get_rank_img(session, server, account_id, draws, Fort)
        return out
    except (NetError, APIError) as e:
        raise e


async def fun_get_recent_img(session: aiohttp.ClientSession, account_id: str, server: int, clan_tag: str, nickName: str,
                             days: int,
                             draws: dict, Fort: dict):
    past_data = await dataBase.read_recent_data(account_id, days - 1)
    ship_data = await api_get_player_ship_data(session, account_id, server)
    ships_RE = await reapi_get_ships(session, account_id, server)
    ships_RE = ships_RE[account_id]['statistics']
    REs = []
    ship_read = await read_ship_dic_api()
    for ship_id, ship in ship_read.items():
        if ship['RE']:
            REs.append(ship_id)
    ship_list = ship_data[account_id]
    recent_data = []
    if past_data == {}:
        raise Notfound('找不到战绩信息，可能是刚刚绑定或绑定时间不足')
    else:
        battles = 0
        frags = 0
        damage = 0
        wins = 0
        xp = 0
        survived = 0
        shots = 0
        hits = 0
        for ship in ship_list:
            ship_id = ship['ship_id']
            if ship['pvp']['battles'] != 0:
                if str(ship_id) not in past_data.keys():
                    recent_data.append(ship)
                    battles += ship['pvp']['battles']
                    frags += ship['pvp']['frags']
                    damage += ship['pvp']['damage_dealt']
                    wins += ship['pvp']['wins']
                    xp += ship['pvp']['xp']
                    survived += ship['pvp']['survived_battles']
                    shots += ship['pvp']['main_battery']['shots']
                    hits += ship['pvp']['main_battery']['hits']
                elif (ship['pvp']['battles'] - past_data[str(ship_id)]['pvp']['battles']) != 0:
                    battles_recent = ship['pvp']['battles'] - past_data[str(ship_id)]['pvp']['battles']
                    frags_recent = ship['pvp']['frags'] - past_data[str(ship_id)]['pvp']['frags']
                    damage_recent = ship['pvp']['damage_dealt'] - past_data[str(ship_id)]['pvp']['damage_dealt']
                    wins_recent = ship['pvp']['wins'] - past_data[str(ship_id)]['pvp']['wins']
                    xp_recent = ship['pvp']['xp'] - past_data[str(ship_id)]['pvp']['xp']
                    survived_recent = ship['pvp']['survived_battles'] - past_data[str(ship_id)]['pvp'][
                        'survived_battles']
                    shots_recent = ship['pvp']['main_battery']['shots'] - \
                                   past_data[str(ship_id)]['pvp']['main_battery'][
                                       'shots']
                    hits_recent = ship['pvp']['main_battery']['hits'] - past_data[str(ship_id)]['pvp']['main_battery'][
                        'hits']
                    battles += battles_recent
                    frags += frags_recent
                    damage += damage_recent
                    wins += wins_recent
                    xp += xp_recent
                    survived += survived_recent
                    shots += shots_recent
                    hits += hits_recent
                    recent_data.append(
                        {
                            'pvp': {
                                'battles': battles_recent,
                                'frags': round(frags_recent),
                                'damage_dealt': round(damage_recent),
                                'wins': wins_recent,
                                'xp': round(xp_recent),
                                'survived_battles': round(survived_recent),
                                'main_battery': {
                                    'shots': shots_recent,
                                    'hits': hits_recent,
                                }
                            },
                            'ship_id': ship_id
                        }
                    )
                else:
                    pass
            else:
                pass
        for ship_id_tmp in ships_RE.keys():
            if ship_id_tmp in REs:
                ship_tmp = await reapi_get_player_ship_data(session, account_id, server, ship_id_tmp)
                ship_tmp = ship_tmp[str(account_id)]['statistics'][str(ship_id_tmp)]['pvp']
                battles_tmp = ship_tmp['battles_count']
                wins_tmp = ship_tmp['wins']
                frags_tmp = ship_tmp['frags']
                damage_dealt_tmp = ship_tmp['damage_dealt']
                xp_tmp = ship_tmp['exp']
                shots_tmp = ship_tmp['shots_by_main']
                hits_tmp = ship_tmp['hits_by_main']
                survived_tmp = ship_tmp['survived']
                if str(ship_id_tmp) not in past_data.keys():
                    recent_data.append(
                        {
                            'pvp': {
                                'battles': battles_tmp,
                                'frags': round(frags_tmp),
                                'damage_dealt': round(damage_dealt_tmp),
                                'wins': wins_tmp,
                                'xp': round(xp_tmp),
                                'survived_battles': round(survived_tmp),
                                'main_battery': {
                                    'shots': shots_tmp,
                                    'hits': hits_tmp,
                                }
                            },
                            'ship_id': ship_id_tmp
                        }
                    )
                    battles += battles_tmp
                    frags += frags_tmp
                    damage += damage_dealt_tmp
                    wins += wins_tmp
                    xp += xp_tmp
                    survived += survived_tmp
                    shots += shots_tmp
                    hits += hits_tmp
                elif (battles_tmp - past_data[str(ship_id_tmp)]['pvp']['battles']) != 0:
                    battles_recent = battles_tmp - past_data[str(ship_id_tmp)]['pvp']['battles']
                    frags_recent = frags_tmp - past_data[str(ship_id_tmp)]['pvp']['frags']
                    damage_recent = damage_dealt_tmp - past_data[str(ship_id_tmp)]['pvp']['damage_dealt']
                    wins_recent = wins_tmp - past_data[str(ship_id_tmp)]['pvp']['wins']
                    xp_recent = xp_tmp - past_data[str(ship_id_tmp)]['pvp']['xp']
                    survived_recent = survived_tmp - past_data[str(ship_id_tmp)]['pvp'][
                        'survived_battles']
                    shots_recent = shots_tmp - \
                                   past_data[str(ship_id_tmp)]['pvp']['main_battery'][
                                       'shots']
                    hits_recent = hits_tmp - \
                                  past_data[str(ship_id_tmp)]['pvp']['main_battery'][
                                      'hits']
                    battles += battles_recent
                    frags += frags_recent
                    damage += damage_recent
                    wins += wins_recent
                    xp += xp_recent
                    survived += survived_recent
                    shots += shots_recent
                    hits += hits_recent
                    recent_data.append(
                        {
                            'pvp': {
                                'battles': battles_recent,
                                'frags': round(frags_recent),
                                'damage_dealt': round(damage_recent),
                                'wins': wins_recent,
                                'xp': round(xp_recent),
                                'survived_battles': round(survived_recent),
                                'main_battery': {
                                    'shots': shots_recent,
                                    'hits': hits_recent,
                                }
                            },
                            'ship_id': ship_id_tmp
                        }
                    )
                else:
                    pass

        if battles != 0:
            _shipName = await read_ship_dic_api()
            day_list = [7, 6, 5, 4, 3, 2, 1]
            pr_list = []
            for day in day_list:
                read_tmp = await dataBase.read_recent_data(account_id, day - 1)
                if read_tmp == {}:
                    pr_list.append(0)
                else:
                    pr_ship_list_tmp = []
                    for ship_id_tmp, ship_tmp in read_tmp.items():
                        pr_ship_list_tmp.append(
                            {
                                'ship_id': ship_id_tmp,
                                'pvp': ship_tmp['pvp'],
                            }
                        )
                    pr, pr_rank = await fun_get_gen_pr(pr_ship_list_tmp)
                    pr_list.append(round(pr))
            recent_ship_list = []
            for ship in recent_data:
                try:
                    pr_rank, pr = await fun_get_ship_pr(ship)
                    pr_tag_tmp, pr_color_tmp = await fun_get_pr_color(round(pr))
                    ship_id_tmp = ship['ship_id']
                    ship['PR'] = str(round(pr))
                    ship['PR_color'] = pr_color_tmp
                    ship['name'] = _shipName[str(ship_id_tmp)]['name']
                    recent_ship_list.append(ship)
                except Exception as e:
                    print(e.args)
                    pass
            pr, pr_rank = await fun_get_gen_pr(recent_data)
            pr_tag, pr_color = await fun_get_pr_color(round(pr))
            battles_img = str(battles)
            winRate_img = str(format(wins / battles, '.2%'))
            damage_img = str(round(damage / battles))
            xp_img = str(round(xp / battles))
            try:
                kd_img = str(round(frags / (battles - survived), 2))
            except Exception:
                kd_img = 'N/A'
            try:
                accuRate_img = str(format(hits / shots, '.2%'))
            except Exception:
                accuRate_img = 'N/A'
            return await fun_gen_recent_img(battles_img, winRate_img, damage_img, xp_img, accuRate_img, nickName,
                                            str(round(pr)), clan_tag, kd_img, pr_tag, pr_color, pr_list,
                                            recent_ship_list)
        else:
            raise Notfound('更新后可能没有进行游戏')


async def wows_get_ship_img(session: aiohttp.ClientSession, account_id: str, server: int, ship_id: str, shipName: str,
                            draws: dict,
                            Fort: dict):
    RE = await re_ship_check(ship_id)
    if RE:
        task = asyncio.create_task(reapi_get_player_ship_data(session, account_id, server, ship_id))
    else:
        task = asyncio.create_task(api_get_player_ship_data(session, account_id, server))
    tasks = [
        asyncio.create_task(api_get_clan_id(session, account_id, server)),
        asyncio.create_task(api_get_play_personal_data(session, account_id, server)),
        task
    ]
    _init = '_init'
    _NA = 'N/A'
    PR = _init
    clan_tag = _init
    PR_tag = _init
    nickName = _init
    battles = _init
    winRate = _init
    damageAvg = _init
    xpAvg = _init
    KD = _init
    accuRate = _init
    res = await asyncio.gather(*tasks)
    for i in range(3):
        match i:
            case 0:
                item = res[0]
                if item[account_id] is None:
                    clan_tag = '「」'
                else:
                    clan_id = str(item[account_id]['clan_id'])
                    clan_details = await api_get_clan_details(session, clan_id, server)
                    clan_tag = clan_details[clan_id]['tag']
            case 1:
                item = res[1]
                nickName = item[account_id]['nickname']
            case 2:
                if RE:
                    ship = res[2]
                    ship = ship[str(account_id)]['statistics'][str(ship_id)]['pvp']
                    PR_tag, PR = await get_re_pr(ship)
                    battles = ship['battles_count']
                    wins = ship['wins']
                    frags = ship['frags']
                    damage_dealt = ship['damage_dealt']
                    xp = ship['exp']
                    shots = ship['shots_by_main']
                    hits = ship['hits_by_main']
                    damageAvg = round(damage_dealt / battles)
                    winRate = str(format(wins / battles, '.2%'))
                    xpAvg = str(round(xp / battles))
                    try:
                        KD = str(round(frags / (battles - ship['survived']), 2))
                    except Exception:
                        KD = _NA
                    try:
                        accuRate = str(format(hits / shots, '.2%'))
                    except Exception:
                        accuRate = _NA
                else:
                    item = res[2]
                    shipList = item[account_id]
                    ship_ans = None
                    for _ship in shipList:
                        if str(_ship['ship_id']) == ship_id:
                            ship_ans = _ship
                    if ship_ans is None:
                        raise Notfound('没有该船只')
                    else:
                        PR_tag, PR = await fun_get_ship_pr(ship_ans)
                        ship = ship_ans['pvp']
                        battles = ship['battles']
                        wins = ship['wins']
                        frags = ship['frags']
                        damage_dealt = ship['damage_dealt']
                        xp = ship['xp']
                        shots = ship['main_battery']['shots']
                        hits = ship['main_battery']['hits']
                        damageAvg = round(damage_dealt / battles)
                        winRate = str(format(wins / battles, '.2%'))
                        xpAvg = str(round(xp / battles))
                        try:
                            KD = str(round(frags / (battles - ship['survived_battles']), 2))
                        except Exception:
                            KD = _NA
                        try:
                            accuRate = str(format(hits / shots, '.2%'))
                        except Exception:
                            accuRate = _NA
    return await fun_gen_img(shipName, str(clan_tag), str(nickName), str(battles), str(winRate),
                             str(damageAvg), str(xpAvg), str(KD), str(accuRate), "_NA", str(PR_tag), draws, Fort)


async def wows_get_ship_img_me(session: aiohttp.ClientSession, account_id: str, server: int, ship_id: str,
                               shipName: str,
                               nickName: str, clan_tag, draws: dict, Fort: dict):
    _init = '_init'
    _NA = 'N/A'
    PR = _init
    PR_tag = _init
    battles = _init
    winRate = _init
    damageAvg = _init
    xpAvg = _init
    KD = _init
    accuRate = _init
    RE = await re_ship_check(ship_id)
    if RE:
        ship = await reapi_get_player_ship_data(session, account_id, server, ship_id)
        ship = ship[str(account_id)]['statistics'][str(ship_id)]['pvp']
        PR_tag, PR = await get_re_pr(ship)
        battles = ship['battles_count']
        wins = ship['wins']
        frags = ship['frags']
        damage_dealt = ship['damage_dealt']
        xp = ship['exp']
        shots = ship['shots_by_main']
        hits = ship['hits_by_main']
        damageAvg = round(damage_dealt / battles)
        winRate = str(format(wins / battles, '.2%'))
        xpAvg = str(round(xp / battles))
        try:
            KD = str(round(frags / (battles - ship['survived']), 2))
        except Exception:
            KD = _NA
        try:
            accuRate = str(format(hits / shots, '.2%'))
        except Exception:
            accuRate = _NA
    else:
        item = await api_get_player_ship_data(session, account_id, server)
        shipList = item[account_id]
        ship_ans = None
        for _ship in shipList:
            if str(_ship['ship_id']) == ship_id:
                ship_ans = _ship
        if ship_ans is None:
            raise Notfound('没有该船只')
        else:
            PR_tag, PR = await fun_get_ship_pr(ship_ans)
            ship = ship_ans['pvp']
            battles = ship['battles']
            wins = ship['wins']
            frags = ship['frags']
            damage_dealt = ship['damage_dealt']
            xp = ship['xp']
            shots = ship['main_battery']['shots']
            hits = ship['main_battery']['hits']
            damageAvg = round(damage_dealt / battles)
            winRate = str(format(wins / battles, '.2%'))
            xpAvg = str(round(xp / battles))
            try:
                KD = str(round(frags / (battles - ship['survived_battles']), 2))
            except Exception:
                KD = _NA
            try:
                accuRate = str(format(hits / shots, '.2%'))
            except Exception:
                accuRate = _NA
    return await fun_gen_img(shipName, str(clan_tag), str(nickName), str(battles), str(winRate),
                             str(damageAvg), str(xpAvg), str(KD), str(accuRate), _NA, str(PR_tag), draws, Fort)


async def wows_get_ship_nickName(session: aiohttp.ClientSession, nickName: str, server: int, ship_id: str,
                                 shipName: str,
                                 draws: dict, Fort: dict):
    try:
        _data = await api_get_account_id(session, nickName, server)
        account_id = str(_data[0]['account_id'])
    except (APIError, NetError) as e:
        raise e
    try:
        out = await wows_get_ship_img(session, account_id, server, ship_id, shipName, draws, Fort)
        return out
    except (NetError, APIError) as e:
        raise e


async def re_ship_check(ship_id: str) -> bool:
    ships = await read_ship_dic_api()
    return ships[ship_id]['RE']
