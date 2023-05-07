# -*- coding: UTF-8 -*-
"""
@Project ：Bot_rain
@File    ：APIs.py
@Author  ：INTMAX
@Date    ：2022-06-03 7:50 p.m.
"""
import asyncio
from graia.ariadne.util.async_exec import io_bound
import aiohttp
import ApiKeys
from wows import dataBase
from wows.utility import Pr, User, Ship, wows_user, wows_ship, wows_recent, wows_rank

"""
@Describe: 战舰世界查询/更新可能会用到的 API
@rule: 尽可能使用官方 API ，必要时使用第三方 API，如使用第三方API需要在API失效时也可正常运作
"""

"""
wows 的应用程序 ID
"""

application_id = ApiKeys.wowsApikey

"""
Wargaming 提供的API
"""

"""
获取玩家 account_id 的 API
"""
wows_account_players_ru = "https://api.worldofwarships.ru/wows/account/list/"
wows_account_players_eu = "https://api.worldofwarships.eu/wows/account/list/"
wows_account_players_na = "https://api.worldofwarships.com/wows/account/list/"
wows_account_players_asia = "https://api.worldofwarships.asia/wows/account/list/"

"""
根据 account_id 获取基础玩家基础信息的 API
"""

wows_account_player_personal_data_ru = (
    "https://api.worldofwarships.ru/wows/account/info/"
)
wows_account_player_personal_data_eu = (
    "https://api.worldofwarships.eu/wows/account/info/"
)
wows_account_player_personal_data_na = (
    "https://api.worldofwarships.com/wows/account/info/"
)
wows_account_player_personal_data_asia = (
    "https://api.worldofwarships.asia/wows/account/info/"
)

"""
根据 account_id 获取玩家 clan_id 的 API
"""

wows_clans_player_clan_data_ru = (
    "https://api.worldofwarships.ru/wows/clans/accountinfo/"
)
wows_clans_player_clan_data_eu = (
    "https://api.worldofwarships.eu/wows/clans/accountinfo/"
)
wows_clans_player_clan_data_na = (
    "https://api.worldofwarships.com/wows/clans/accountinfo/"
)
wows_clans_player_clan_data_asia = (
    "https://api.worldofwarships.asia/wows/clans/accountinfo/"
)

"""
根据 clan_id 获取军团 tag
"""

wows_clans_clan_details_ru = "https://api.worldofwarships.ru/wows/clans/info/"
wows_clans_clan_details_eu = "https://api.worldofwarships.eu/wows/clans/info/"
wows_clans_clan_details_na = "https://api.worldofwarships.com/wows/clans/info/"
wows_clans_clan_details_asia = "https://api.worldofwarships.asia/wows/clans/info/"

"""
根据 account_id 查询船只数据
"""
wows_warship_stat_ru = "https://api.worldofwarships.ru/wows/ships/stats/"
wows_warship_stat_eu = "https://api.worldofwarships.eu/wows/ships/stats/"
wows_warship_stat_na = "https://api.worldofwarships.com/wows/ships/stats/"
wows_warship_stat_asia = "https://api.worldofwarships.asia/wows/ships/stats/"

"""
Rank API
"""

api_wargaming_rank_ru = "https://api.worldofwarships.ru/wows/seasons/shipstats/"
api_wargaming_rank_eu = "https://api.worldofwarships.eu/wows/seasons/shipstats/"
api_wargaming_rank_na = "https://api.worldofwarships.com/wows/seasons/shipstats/"
api_wargaming_rank_asia = "https://api.worldofwarships.asia/wows/seasons/shipstats/"

api_wargaming_rank_stat_ru = "https://api.worldofwarships.ru/wows/seasons/accountinfo/"
api_wargaming_rank_stat_eu = "https://api.worldofwarships.eu/wows/seasons/accountinfo/"
api_wargaming_rank_stat_na = "https://api.worldofwarships.com/wows/seasons/accountinfo/"
api_wargaming_rank_stat_asia = (
    "https://api.worldofwarships.asia/wows/seasons/accountinfo/"
)


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


async def api_get_account_id(
    session: aiohttp.ClientSession, nickName: str, server: int
) -> dict:
    """
    根据 nickName 获取 account_id
    :param session: aiohttp 的 ClientSession
    :param nickName: 游戏内昵称
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return resp.json: 服务器返回值的 json 转码
    """
    API = ""
    match server:
        case 0:
            API = wows_account_players_asia
        case 1:
            API = wows_account_players_ru
        case 2:
            API = wows_account_players_eu
        case 3:
            API = wows_account_players_na

    params = [("application_id", application_id), ("search", nickName)]

    async with session.get(API, params=params) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data["status"] == "ok":
                return data["data"]
            else:
                raise APIError("参数出现错误")
        else:
            raise NetError("Wargaming 的 API 出现问题/网络出现问题")


async def api_get_play_personal_data(
    session: aiohttp.ClientSession, account_id: str, server: int
) -> dict:
    """
    根据 account_id 获取用户数据
    :param session: aiohttp 的 ClientSession
    :param account_id: 用户的 account_id
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return resp.json: 服务器返回值的 json 转码
    """
    API = ""
    match server:
        case 0:
            API = wows_account_player_personal_data_asia
        case 1:
            API = wows_account_player_personal_data_ru
        case 2:
            API = wows_account_player_personal_data_eu
        case 3:
            API = wows_account_player_personal_data_na

    params = [("application_id", application_id), ("account_id", account_id)]

    async with session.get(API, params=params) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data["status"] == "ok":
                return data["data"]
            else:
                raise APIError("参数出现错误")
        else:
            raise NetError("Wargaming 的 API 出现问题/网络出现问题")


async def api_get_rank_ships(
    session: aiohttp.ClientSession, account_id: str, server: int
) -> dict:
    """
    根据 account_id 获取 rank ships data
    :param session: aiohttp 的 ClientSession
    :param account_id: 用户的 account_id
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return resp.json: 服务器返回值的 json 转码
    """
    API = ""
    match server:
        case 0:
            API = api_wargaming_rank_asia
        case 1:
            API = api_wargaming_rank_ru
        case 2:
            API = api_wargaming_rank_eu
        case 3:
            API = api_wargaming_rank_na

    params = [("application_id", application_id), ("account_id", account_id)]

    async with session.get(API, params=params) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data["status"] == "ok":
                return data["data"]
            else:
                raise APIError("参数出现错误")
        else:
            raise NetError("Wargaming 的 API 出现问题/网络出现问题")


async def api_get_rank_stat(
    session: aiohttp.ClientSession, account_id: str, server: int
) -> dict:
    """
    根据 account_id 获取 rank ships data
    :param session: aiohttp 的 ClientSession
    :param account_id: 用户的 account_id
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return resp.json: 服务器返回值的 json 转码
    """
    API = ""
    match server:
        case 0:
            API = api_wargaming_rank_stat_asia
        case 1:
            API = api_wargaming_rank_stat_ru
        case 2:
            API = api_wargaming_rank_stat_eu
        case 3:
            API = api_wargaming_rank_stat_na

    params = [("application_id", application_id), ("account_id", account_id)]

    async with session.get(API, params=params) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data["status"] == "ok":
                return data["data"]
            else:
                raise APIError("参数出现错误")
        else:
            raise NetError("Wargaming 的 API 出现问题/网络出现问题")


async def api_get_clan_id(
    session: aiohttp.ClientSession, account_id: str, server: int
) -> dict:
    """
    根据 account_id 获取 clan_id
    :param session: aiohttp 的 ClientSession
    :param account_id: 用户的 account_id
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return resp.json: 服务器返回值的 json 转码
    """
    API = ""
    match server:
        case 0:
            API = wows_clans_player_clan_data_asia
        case 1:
            API = wows_clans_player_clan_data_ru
        case 2:
            API = wows_clans_player_clan_data_eu
        case 3:
            API = wows_clans_player_clan_data_na

    params = [("application_id", application_id), ("account_id", account_id)]

    async with session.get(API, params=params) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data["status"] == "ok":
                return data["data"]
            else:
                raise APIError("参数出现错误")
        else:
            raise NetError("Wargaming 的 API 出现问题/网络出现问题")


async def api_get_clan_details(
    session: aiohttp.ClientSession, clan_id: str, server: int
) -> dict:
    """
    获取军团具体信息 主要用来获取 tag
    :param session: aiohttp 的 ClientSession
    :param clan_id: 军团的 clan_id
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return resp.json: 服务器返回值的 json 转码
    """
    API = ""
    match server:
        case 0:
            API = wows_clans_clan_details_asia
        case 1:
            API = wows_clans_clan_details_ru
        case 2:
            API = wows_clans_clan_details_eu
        case 3:
            API = wows_clans_clan_details_na

    params = [("application_id", application_id), ("clan_id", clan_id)]

    async with session.get(API, params=params) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data["status"] == "ok":
                return data["data"]
            else:
                raise APIError("参数出现错误")
        else:
            raise NetError("Wargaming 的 API 出现问题/网络出现问题")


async def api_get_player_ship_data(
    session: aiohttp.ClientSession, account_id: str, server: int
) -> dict:
    """
    根据 account_id 获取玩家所有船只的数据
    :param session: aiohttp 的 ClientSession
    :param account_id: 用户的 account_id
    :param server: 服务器 0-3 依次是 亚服 毛服 欧服 美服
    :return resp.json: 服务器返回值的 json 转码
    """
    API = ""
    match server:
        case 0:
            API = wows_warship_stat_asia
        case 1:
            API = wows_warship_stat_ru
        case 2:
            API = wows_warship_stat_eu
        case 3:
            API = wows_warship_stat_na
    params = [("application_id", application_id), ("account_id", account_id)]
    async with session.get(API, params=params) as resp:
        if 200 == resp.status:
            data = await resp.json()
            if data["status"] == "ok":
                return data["data"]
            else:
                raise APIError("参数出现错误")
        else:
            raise NetError("Wargaming 的 API 出现问题/网络出现问题")


async def fun_wows_account_id(
    session: aiohttp.ClientSession,
    account_id: str,
    server: int,
    draws: dict,
    Fort: dict,
):
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
    task_get_warship_detail = asyncio.create_task(
        api_get_player_ship_data(session, account_id, server)
    )
    task.append(task_get_warship_detail)
    task_get_person_detail = asyncio.create_task(
        api_get_play_personal_data(session, account_id, server)
    )
    task.append(task_get_person_detail)
    res = await asyncio.gather(*task)
    clan_tag = ""
    item = res[0]
    if item[account_id] is None:
        clan_tag = "NO CLAN DATA"
    else:
        clan_id = str(item[account_id]["clan_id"])
        clan_details = await api_get_clan_details(session, clan_id, server)
        clan_tag = clan_details[clan_id]["tag"]
    user = User()
    user.init_user(res[2][account_id], res[1][account_id], server, None, clan_tag)
    await user.async_init(res[1][account_id])
    return await wows_user(user, draws, Fort)


async def fun_wows_account_id_no_clan(
    session: aiohttp.ClientSession,
    account_id: str,
    server: int,
    clan_tag: str,
    draws: dict,
    Font: dict,
):
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
    task_get_warship_detail = asyncio.create_task(
        api_get_player_ship_data(session, account_id, server)
    )
    task.append(task_get_warship_detail)
    task_get_person_detail = asyncio.create_task(
        api_get_play_personal_data(session, account_id, server)
    )
    task.append(task_get_person_detail)
    res = await asyncio.gather(*task)
    user = User()
    user.init_user(res[1][account_id], res[0][account_id], server, None, clan_tag)
    await user.async_init(res[0][account_id])
    return await wows_user(user, draws, Font)


async def fun_wows_nickName(
    session: aiohttp.ClientSession, nickName: str, server: int, draws: dict, Fort: dict
):
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
    account_id = str(_data[0]["account_id"])
    return await fun_wows_account_id(session, account_id, server, draws, Fort)


async def fun_wows_me(
    session: aiohttp.ClientSession,
    account_id: str,
    server: int,
    clan_tag: str,
    draws: dict,
    Fort: dict,
):
    return await fun_wows_account_id_no_clan(
        session, account_id, server, clan_tag, draws, Fort
    )


async def wows_get_ship_img(
    session: aiohttp.ClientSession,
    account_id: str,
    server: int,
    ship_id: str,
    shipName: str,
    draws: dict,
    Fort: dict,
):
    task = []
    task_get_clan_id = asyncio.create_task(api_get_clan_id(session, account_id, server))
    task.append(task_get_clan_id)
    task_get_warship_detail = asyncio.create_task(
        api_get_player_ship_data(session, account_id, server)
    )
    task.append(task_get_warship_detail)
    task_get_person_detail = asyncio.create_task(
        api_get_play_personal_data(session, account_id, server)
    )
    task.append(task_get_person_detail)
    res = await asyncio.gather(*task)
    clan_tag = ""
    item = res[0]
    if item[account_id] is None:
        clan_tag = "NO CLAN DATA"
    else:
        clan_id = str(item[account_id]["clan_id"])
        clan_details = await api_get_clan_details(session, clan_id, server)
        clan_tag = clan_details[clan_id]["tag"]
    user = User()
    user.init_user(res[2][account_id], res[1][account_id], server, None, clan_tag)
    await user.async_init(res[1][account_id])
    return await wows_ship(user, ship_id, draws, Fort)


async def wows_get_ship_img_me(
    session: aiohttp.ClientSession,
    account_id: str,
    server: int,
    ship_id: str,
    shipName: str,
    nickName: str,
    clan_tag,
    draws: dict,
    Fort: dict,
):
    task = []
    task_get_warship_detail = asyncio.create_task(
        api_get_player_ship_data(session, account_id, server)
    )
    task.append(task_get_warship_detail)
    task_get_person_detail = asyncio.create_task(
        api_get_play_personal_data(session, account_id, server)
    )
    task.append(task_get_person_detail)
    res = await asyncio.gather(*task)
    user = User()
    user.init_user(res[1][account_id], res[0][account_id], server, None, clan_tag)
    await user.async_init(res[0][account_id])
    return await wows_ship(user, ship_id, draws, Fort)


async def wows_get_ship_nickName(
    session: aiohttp.ClientSession,
    nickName: str,
    server: int,
    ship_id: str,
    shipName: str,
    draws: dict,
    Fort: dict,
):
    try:
        _data = await api_get_account_id(session, nickName, server)
        account_id = str(_data[0]["account_id"])
    except (APIError, NetError) as e:
        raise e
    try:
        out = await wows_get_ship_img(
            session, account_id, server, ship_id, shipName, draws, Fort
        )
        return out
    except (NetError, APIError) as e:
        raise e


async def wows_get_recent(
    session: aiohttp.ClientSession,
    account_id: str,
    server: int,
    clan_tag: str,
    date: int,
    draws: list,
    Fonts: list,
):
    task = []
    task_get_warship_detail = asyncio.create_task(
        api_get_player_ship_data(session, account_id, server)
    )
    task.append(task_get_warship_detail)
    task_get_person_detail = asyncio.create_task(
        api_get_play_personal_data(session, account_id, server)
    )
    task.append(task_get_person_detail)
    res = await asyncio.gather(*task)
    user = User()
    user.init_user(res[1][account_id], res[0][account_id], server, None, clan_tag)
    await user.async_init(res[0][account_id])
    current_user = user
    if date is None:
        """
        wows recent auto
        """
        past_user = await dataBase.read_recent_data_auto(account_id)
    else:
        past_user = await dataBase.read_recent_data(account_id, date)
    recent_user = current_user - past_user
    await recent_user.init_pr_sub()
    return await wows_recent(recent_user, draws, Fonts)


async def wows_rank_me(
    session: aiohttp.ClientSession,
    nick_name: str,
    account_id: str,
    server: int,
    clan_tag: str,
    draws: list,
    Fonts: list,
):
    task = []
    task_get_rank_ships = asyncio.create_task(
        api_get_rank_ships(session, account_id, server)
    )
    task_get_rank_stat = asyncio.create_task(
        api_get_rank_stat(session, account_id, server)
    )
    task = [task_get_rank_ships, task_get_rank_stat]
    res = await asyncio.gather(*task)
    ships_res = res[0]
    stat_res = res[1]
    if stat_res[account_id] is None and stat_res[account_id]["seasons"] is None:
        raise Notfound("找不到数据")
    seasons = [int(i) for i in stat_res[account_id]["seasons"].keys()]
    season_id = max(seasons)
    season_stat = stat_res[account_id]["seasons"][f"{season_id}"]
    if season_stat is None:
        raise Notfound("找不到数据")
    user_dic = {
        "account_id": account_id,
        "nickname": nick_name,
        "last_battle_time": 1,
        "leveling_tier": 1,
        "hidden_profile": None,
        "logout_at": 1,
        "created_at": 1,
        "statistics": {
            "pvp": {
                "battles": 0,
                "damage_dealt": 0,
                "wins": 0,
                "xp": 0,
                "frags": 0,
                "survived_battles": 0,
                "main_battery": {"shots": 0, "hits": 0},
                "max_damage_dealt": 0,
                "max_damage_scouting": 0,
                "max_frags_battle": 0,
                "max_planes_killed": 0,
                "max_total_agro": 0,
                "max_xp": 0,
                "max_ships_spotted": 0,
            }
        },
    }
    for week in season_stat.values():
        if week is not None:
            for rank in week.values():
                if rank is not None:
                    user_dic["statistics"]["pvp"]["battles"] += rank["battles"]
                    user_dic["statistics"]["pvp"]["damage_dealt"] += rank[
                        "damage_dealt"
                    ]
                    user_dic["statistics"]["pvp"]["wins"] += rank["wins"]
                    user_dic["statistics"]["pvp"]["xp"] += rank["xp"]
                    user_dic["statistics"]["pvp"]["frags"] += rank["frags"]
                    user_dic["statistics"]["pvp"]["survived_battles"] += rank[
                        "survived_battles"
                    ]
                    user_dic["statistics"]["pvp"]["max_damage_dealt"] = max(
                        rank["max_damage_dealt"],
                        user_dic["statistics"]["pvp"]["max_damage_dealt"],
                    )
                    user_dic["statistics"]["pvp"]["max_frags_battle"] = max(
                        rank["max_frags_battle"],
                        user_dic["statistics"]["pvp"]["max_frags_battle"],
                    )
                    user_dic["statistics"]["pvp"]["max_planes_killed"] = max(
                        rank["max_planes_killed"],
                        user_dic["statistics"]["pvp"]["max_planes_killed"],
                    )
                    user_dic["statistics"]["pvp"]["max_xp"] = max(
                        rank["max_xp"],
                        user_dic["statistics"]["pvp"]["max_xp"],
                    )
                    user_dic["statistics"]["pvp"]["main_battery"]["shots"] += rank[
                        "main_battery"
                    ]["shots"]
                    user_dic["statistics"]["pvp"]["main_battery"]["hits"] += rank[
                        "main_battery"
                    ]["hits"]
    if user_dic["statistics"]["pvp"]["battles"] == 0:
        raise Notfound("场数为0")
    user = User()
    user.season_id = str(season_id)
    if ships_res[account_id] is None:
        raise Notfound("没有船只数据")
    user.init_user(user_dic, None, server, None, clan_tag)

    def ship_generator():
        for ship in ships_res[account_id]:
            ship_dic = {
                "ship_id": ship["ship_id"],
                "last_battle_time": 1,
                "leveling_tier": 1,
                "hidden_profile": None,
                "logout_at": 1,
                "pvp": {
                    "battles": 0,
                    "damage_dealt": 0,
                    "wins": 0,
                    "xp": 0,
                    "frags": 0,
                    "survived_battles": 0,
                    "main_battery": {"shots": 0, "hits": 0},
                    "max_damage_dealt": 0,
                    "max_damage_scouting": 0,
                    "max_frags_battle": 0,
                    "max_planes_killed": 0,
                    "max_total_agro": 0,
                    "max_xp": 0,
                    "max_ships_spotted": 0,
                },
            }
            if str(season_id) not in ship["seasons"].keys():
                continue
            else:
                season_stat_ship = ship["seasons"][f"{season_id}"]
                for week in season_stat_ship.values():
                    if week is not None:
                        for rank in week.values():
                            if rank is not None:
                                ship_dic["pvp"]["battles"] += rank["battles"]
                                ship_dic["pvp"]["damage_dealt"] += rank["damage_dealt"]
                                ship_dic["pvp"]["wins"] += rank["wins"]
                                ship_dic["pvp"]["xp"] += rank["xp"]
                                ship_dic["pvp"]["frags"] += rank["frags"]
                                ship_dic["pvp"]["survived_battles"] += rank[
                                    "survived_battles"
                                ]
                                ship_dic["pvp"]["max_damage_dealt"] = max(
                                    rank["max_damage_dealt"],
                                    ship_dic["pvp"]["max_damage_dealt"],
                                )
                                ship_dic["pvp"]["max_frags_battle"] = max(
                                    rank["max_frags_battle"],
                                    ship_dic["pvp"]["max_frags_battle"],
                                )
                                ship_dic["pvp"]["max_planes_killed"] = max(
                                    rank["max_planes_killed"],
                                    ship_dic["pvp"]["max_planes_killed"],
                                )
                                ship_dic["pvp"]["max_xp"] = max(
                                    rank["max_xp"],
                                    ship_dic["pvp"]["max_xp"],
                                )
                                ship_dic["pvp"]["main_battery"]["shots"] += rank[
                                    "main_battery"
                                ]["shots"]
                                ship_dic["pvp"]["main_battery"]["hits"] += rank[
                                    "main_battery"
                                ]["hits"]
            if ship_dic["pvp"]["battles"] != 0:
                yield ship_dic

    ship_list = [i for i in ship_generator()]
    await user.async_init(ship_list)
    return await wows_rank(user, draws, Fonts)


async def wows_rank_account_id(
    session: aiohttp.ClientSession,
    nick_name: str,
    server: int,
    draws: list,
    Fonts: list,
):
    res_person_data = await api_get_account_id(session, nick_name, server)
    account_id = str(res_person_data[0]["account_id"])
    nick_name = str(res_person_data[0]["nickname"])
    res_clan_id = await api_get_clan_id(session, account_id, server)
    clan_tag = ""
    item = res_clan_id
    if item[account_id] is None:
        clan_tag = "NO CLAN DATA"
    else:
        clan_id = str(item[account_id]["clan_id"])
        clan_details = await api_get_clan_details(session, clan_id, server)
        clan_tag = clan_details[clan_id]["tag"]
    return await wows_rank_me(
        session, nick_name, account_id, server, clan_tag, draws, Fonts
    )
