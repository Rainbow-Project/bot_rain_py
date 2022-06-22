# -*- coding: UTF-8 -*-
"""
@Project ：Bot_rain
@File    ：APIs.py
@Author  ：INTMAX
@Date    ：2022-06-03 7:50 p.m. 
"""
import aiohttp
from ApiKeys import wowsApikey
import requests
from bs4 import BeautifulSoup

"""
@Describe: 战舰世界查询/更新可能会用到的 API
@rule: 尽可能使用官方 API ，必要时使用第三方 API，如使用第三方API需要在API失效时也可正常运作
"""

"""
Wargaming 提供的API
"""
api_wargaming_account_players = 'https://api.worldofwarships.SERVER/wows/account/list/'
api_wargaming_account_personal_data = 'https://api.worldofwarships.SERVER/wows/account/info/'
api_wargaming_account_statistics_by_date = 'https://api.worldofwarships.SERVER/wows/account/statsbydate/'
api_wargaming_warships_player_ship = 'https://api.worldofwarships.SERVER/wows/ships/stats/'
api_wargaming_clans_player_clan = 'https://api.worldofwarships.SERVER/wows/clans/accountinfo/'
api_wargaming_clans_clans_details = 'https://api.worldofwarships.SERVER/wows/clans/info/'

"""
非 Wargaming 官方 API
"""
api_wows_numbers = 'https://api.wows-numbers.com/personal/rating/expected/json/'

# 开发者提供的API 考虑到服务器的负载，头需要的信息就找我来要吧

api_wargaming_rank = 'http://wows.SERVER.intmax.top/community/accounts/tab/rank/overview/'


class ApiError(Exception):
    """
        api 状态异常
    """

    def __init__(self, arg):
        self.args = arg


class Notfound(Exception):
    """
        user 找不到类型
    """

    def __init__(self, arg):
        self.args = arg


class UserNoClan(Exception):
    """
        user 用户无军团
    """

    def __init__(self, arg):
        self.args = arg


async def fun_api_get_ship_exp() -> dict:
    """
    从 wows-numbers 获取船只的期望数据
    :return: dict
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(api_wows_numbers) as resp:
            if 200 == resp.status:
                return await resp.json()
            else:
                raise ApiError('Wargaming 的 API 出现问题/网络出现问题')


async def fun_api_get_player_personal_data(server: str, account_id: str) -> dict:
    """
    根据 account id 查询玩家作战数据
    :param server: 服务器信息
    :param account_id: Wargaming 用户的唯一ID
    :return:
    """
    if server == "na":
        server = 'com'
    params = [('application_id', wowsApikey),
              ('account_id', account_id)
              ]
    api = api_wargaming_account_personal_data.replace("SERVER", server)
    async with aiohttp.ClientSession() as session:
        async with session.get(api, params=params) as resp:
            if 200 == resp.status:
                return await resp.json()
            else:
                raise ApiError('Wargaming 的 API 出现问题/网络出现问题')


async def fun_api_get_player_data(server: str, nickName: str) -> dict:
    """
    从 Wargaming 获取用户的 数据
    :param server: 服务器信息
    :param nickName: 用户昵称
    :return: dict of user data
    """
    if server == "na":
        server = 'com'
    params = [('application_id', wowsApikey),
              ('search', nickName)
              ]
    api = api_wargaming_account_players.replace("SERVER", server)
    async with aiohttp.ClientSession() as session:
        async with session.get(api, params=params) as resp:
            if 200 == resp.status:
                return await resp.json()
            else:
                raise ApiError('Wargaming 的 API 出现问题/网络出现问题')


async def fun_api_get_player_clan_data(server: str, account_id: str) -> dict:
    """
    从 Wargaming 获取对应 account id 的军团信息
    :param server: 服务器信息
    :param account_id: Wargaming 用户的唯一ID
    :return: dict
    """
    if server == "na":
        server = 'com'
    params = [('application_id', wowsApikey),
              ('account_id', account_id)
              ]
    api = api_wargaming_clans_player_clan.replace("SERVER", server)
    async with aiohttp.ClientSession() as session:
        async with session.get(api, params=params) as resp:
            if 200 == resp.status:
                return await resp.json()
            else:
                raise ApiError('Wargaming 的 API 出现问题/网络出现问题')


async def fun_api_get_clan_data(server: str, clan_id: str) -> dict:
    """
    从 Wargaming 获取相应 clan id 的军团信息
    :param server: 服务器信息
    :param clan_id: Wargaming 军团的唯一 ID
    :return: dict
    """
    if server == "na":
        server = 'com'
    params = [('application_id', wowsApikey),
              ('clan_id', clan_id)
              ]
    api = api_wargaming_clans_clans_details.replace("SERVER", server)
    async with aiohttp.ClientSession() as session:
        async with session.get(api, params=params) as resp:
            if 200 == resp.status:
                return await resp.json()
            else:
                raise ApiError('Wargaming 的 API 出现问题/网络出现问题')


async def fun_api_get_player_ship(server: str, account_id: str) -> dict:
    """
    根据 account id 找船只列表
    :param server: 服务器信息
    :param account_id: Wargaming 用户的唯一ID
    :return:
    """
    if server == "na":
        server = 'com'
    params = [('application_id', wowsApikey),
              ('account_id', account_id)
              ]
    api = api_wargaming_warships_player_ship.replace("SERVER", server)
    async with aiohttp.ClientSession() as session:
        async with session.get(api, params=params) as resp:
            if 200 == resp.status:
                return await resp.json()
            else:
                raise ApiError('Wargaming 的 API 出现问题/网络出现问题')


async def fun_api_get_rank_data(server: str, account_id: str) -> str:
    """
    爬取 Wargaming 的 Rank 数据
    :param server: 服务器信息
    :param account_id: Wargaming 用户的唯一ID
    :return:
    考虑到服务器的负载，头需要的信息就找我来要吧
    """
    headers = {
    }
    api = api_wargaming_rank.replace("SERVER", server)+account_id+"/"
    async with aiohttp.ClientSession() as session:
        async with session.get(api, headers=headers) as resp:
            if 200 == resp.status:
                return await resp.text()
            else:
                raise ApiError('Wargaming 的 API 出现问题/网络出现问题')


async def fun_get_rank_data(server: str, account_id: str):
    """
    解析 Rank 数据
    :param server:
    :param account_id:
    :return:
    """
    try:
        getdata = await fun_api_get_rank_data(server, account_id)
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


async def fun_get_ship_list(server: str, account_id: str) -> list:
    """
    根据 account id 返回船只列表
    :param server: 服务器信息
    :param account_id: Wargaming 用户的唯一ID
    :return:
    """
    if server == "na":
        server = 'com'
    try:
        getdata = await fun_api_get_player_ship(server, account_id)
        if getdata['status'] == 'ok':
            if getdata['data'][account_id] is not None and len(getdata['data'][account_id]) != 0:
                return getdata['data'][account_id]
            else:
                raise Notfound('找不到用户数据')
        else:
            raise ApiError('Wargaming 的 API 出现问题/网络出现问题')
    except ApiError:
        raise ApiError('Wargaming 的 API 出现问题/网络出现问题')


async def fun_get_ship_data(server: str, account_id: str, ship_id):
    """
    根据 account id 和 ship id 查找船只数据
    :param server: 服务器信息
    :param account_id: Wargaming 用户的唯一ID
    :param ship_id:
    :return:
    """
    try:
        getlist = await fun_get_ship_list(server, account_id)
        if len(getlist) != 0:
            for ship in getlist:
                if ship['ship_id'] == int(ship_id):
                    pvp = ship['pvp']
                    xp = pvp['xp']
                    survived_battles = pvp['survived_battles']
                    battles = pvp['battles']
                    frags = pvp['frags']
                    damage_dealt = pvp['damage_dealt']
                    wins = pvp['wins']
                    main_battery = pvp['main_battery']
                    return xp, survived_battles, battles, frags, damage_dealt, wins, main_battery, ship
                    break
            raise Notfound('找不到目标船')
        else:
            raise Notfound('船只列表为空')
    except ApiError:
        raise ApiError('Wargaming 的 API 出现问题/网络出现问题')
    except Notfound:
        raise Notfound('找不到用户数据')


async def fun_get_clan_id(server: str, account_id: str) -> str:
    """
    根据 account id 获取 clan id
    :param server: 服务器信息
    :param account_id: Wargaming 用户的唯一ID
    :return:
    """
    try:
        getdata = await fun_api_get_player_clan_data(server, account_id)
        if getdata['status'] == 'ok':
            if len(getdata['data']) != 0:
                if getdata['data'][str(account_id)] is None:
                    raise UserNoClan('用户没有军团')
                else:
                    return str(getdata['data'][str(account_id)]['clan_id'])
            else:
                raise Notfound("找不到 account id 对应的军团")
        else:
            raise ApiError('Wargaming 的 API 出现问题/网络出现问题')
    except ApiError:
        raise ApiError('Wargaming 的 API 出现问题/网络出现问题')


async def fun_get_personal_data(server: str, account_id: str, mode=0):
    """
    根据 account id 获取用户战斗数据
    :param mode: 输出模式 0 为默认 1 为简易输出
    :param server: 服务器信息
    :param account_id: Wargaming 用户的唯一ID
    :return:
    """
    try:
        getdata = await fun_api_get_player_personal_data(server, account_id)
        if getdata['status'] == 'ok':
            if len(getdata['data']) != 0 and getdata['data'][account_id] is not None:
                data = getdata['data'][account_id]
                leveling_tier = data['leveling_tier']
                created_at = data['created_at']
                nickname = data['nickname']
                stat = data['statistics']
                pvp = stat['pvp']
                battles = pvp['battles']
                xp = pvp['xp']
                frags = pvp['frags']
                survived_battles = pvp['survived_battles']
                wins = pvp['wins']
                damage_dealt = pvp['damage_dealt']
                main_battery = pvp['main_battery']
                if mode == 0:
                    return leveling_tier, created_at, nickname, battles, xp, frags, survived_battles, wins, damage_dealt, main_battery
                if mode == 1:
                    return nickname, created_at
            else:
                raise Notfound('找不到用户数据')

        else:
            raise ApiError('Wargaming 的 API 出现问题/网络出现问题')
    except ApiError:
        raise ApiError('Wargaming 的 API 出现问题/网络出现问题')


async def fun_get_clan_tag(server: str, clan_id: str) -> str:
    """
    根据 clan id 来获取军团名字
    :param server: 服务器信息
    :param clan_id: Wargaming 的军团唯一 ID
    :return:
    """
    try:
        getdata = await fun_api_get_clan_data(server, clan_id)
        if getdata['status'] == 'ok':
            if len(getdata['data']) != 0:
                if getdata['data'][str(clan_id)] is None:
                    raise Notfound("找不到 clan_id 对应的数据")
                else:
                    return '「' + str(getdata['data'][str(clan_id)]['tag']) + '」'
            else:
                raise Notfound("找不到 clan_id 对应的数据")
        else:
            raise ApiError('Wargaming 的 API 出现问题/网络出现问题')
    except ApiError:
        raise ApiError('Wargaming 的 API 出现问题/网络出现问题')


async def fun_get_userid(server: str, nickName: str) -> str:
    """
    从 Wargaming 获取用户的 account id
    :param server: 服务器信息
    :param nickName: 用户昵称
    :return: account id
    """
    try:
        getdata = await fun_api_get_player_data(server, nickName)
        if getdata['status'] == 'ok':
            if len(getdata['data']) != 0:
                return str(getdata['data'][0]['account_id'])
            else:
                raise Notfound('找不到用户数据')
        else:
            raise ApiError('Wargaming 的 API 出现问题/网络出现问题')
    except ApiError:
        raise ApiError('Wargaming 的 API 出现问题/网络出现问题')
