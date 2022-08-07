# -*- coding: UTF-8 -*-
"""
@Project ：Bot_rain
@File    ：dataBase.py
@Author  ：INTMAX
@Date    ：2022-06-03 7:50 p.m. 
"""
import asyncio
import datetime
import json
import random

import aiofiles
import aiohttp
import aiosqlite

import ApiKeys

application_id = ApiKeys.wowsApikey


async def get_user_data(account_id: str, server: int):
    wows_account_player_personal_data_ru = 'https://api.worldofwarships.ru/wows/account/info/'
    wows_account_player_personal_data_eu = 'https://api.worldofwarships.eu/wows/account/info/'
    wows_account_player_personal_data_na = 'https://api.worldofwarships.com/wows/account/info/'
    wows_account_player_personal_data_asia = 'https://api.worldofwarships.asia/wows/account/info/'
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
    async with aiohttp.ClientSession() as session:
        async with session.get(API, params=params) as resp:
            if 200 == resp.status:
                data = await resp.json()
                if data['status'] == 'ok':
                    return data['data']
                else:
                    print(data)
                    return {}
            else:
                print(resp.status)
                return {}


async def update_ship_data():
    api = 'https://api.wows-numbers.com/personal/rating/expected/json/'
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as resp:
            if 200 == resp.status:
                data = await resp.json()
                async with aiofiles.open('src/wows_data/wows_exp.json', mode='w') as f:
                    await f.write(json.dumps(data, ensure_ascii=False, indent=4))


async def read_user_data():
    async with aiofiles.open('src/wows_data/user_data.json', mode='r') as f:
        js = await f.read()
        try:
            dic = json.loads(js)
        except Exception:
            dic = {}
        return dic


async def update_user_ship_list(account_id: str, server: int):
    wows_warship_stat_ru = 'https://api.worldofwarships.ru/wows/ships/stats/'
    wows_warship_stat_eu = 'https://api.worldofwarships.eu/wows/ships/stats/'
    wows_warship_stat_na = 'https://api.worldofwarships.com/wows/ships/stats/'
    wows_warship_stat_asia = 'https://api.worldofwarships.asia/wows/ships/stats/'
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

    async with aiohttp.ClientSession() as session:
        async with session.get(API, params=params) as resp:
            if 200 == resp.status:
                data = await resp.json()
                if data['status'] == 'ok':
                    print('sql:' + str(account_id))
                    shipList = data['data'][account_id]
                    today = str(datetime.date.today())
                    print(account_id)
                    key_insert = str(account_id) + '_' + today
                    oneMago = str(datetime.date.today() - datetime.timedelta(days=30))
                    key_del = str(account_id) + '_' + oneMago
                    async with aiosqlite.connect('src/wows_data/user_recent_data.db') as db:
                        try:
                            await db.execute("DROP TABLE '%s'" % key_insert)
                        except Exception:
                            print(key_insert)
                            pass
                        try:
                            await db.execute("DROP TABLE '%s'" % key_del)
                        except Exception:
                            pass
                        await db.execute(
                            "CREATE TABLE '%s'(SHIP_ID INT NOT NULL, BATTLES INT NOT NULL, FRAGS INT NOT NULL, "
                            "XP INT NOT NULL, DAMAGE INT NOT NULL, WINS INT NOT NULL, SURVIVED INT NOT NULL, "
                            "SHOTS INT NOT NULL, HITS INT NOT NULL);" % key_insert)
                        for ship in shipList:
                            ship_id = ship['ship_id']
                            battles = ship['pvp']['battles']
                            frags = ship['pvp']['frags']
                            XP = ship['pvp']['xp']
                            damage = ship['pvp']['damage_dealt']
                            wins = ship['pvp']['wins']
                            survived = ship['pvp']['survived_battles']
                            shots = ship['pvp']['main_battery']['shots']
                            hits = ship['pvp']['main_battery']['hits']
                            sql_cmd = '''INSERT INTO '{}' (SHIP_ID, BATTLES, FRAGS, XP, DAMAGE, WINS, SURVIVED, 
                            SHOTS, HITS) VALUES ({},{},{},{},{},{},{},{},{})'''.format(
                                key_insert, int(ship_id), battles, frags, XP, damage, wins, survived, shots, hits)
                            await db.execute(sql_cmd)
                        await db.commit()
                else:
                    print(data)
            else:
                print(resp.status)


async def wows_get_numbers_api():
    async with aiofiles.open('src/wows_data/wows_exp.json', mode='r') as f:
        js = await f.read()
        try:
            dic = json.loads(js)
        except Exception:
            dic = {}
        return dic


async def update_user_past_data():
    users = await read_user_data()
    task = []
    for user in users.values():
        for accounts in user:
            account_id = accounts['account_id']
            server = accounts['server']
            task.append(asyncio.create_task(update_user_ship_list(account_id, server)))
            await asyncio.sleep(random.randrange(10, 20) / 100)
    await asyncio.gather(*task)
    return


async def get_clan_data(account_id: str, server: int):
    wows_clans_player_clan_data_ru = 'https://api.worldofwarships.ru/wows/clans/accountinfo/'
    wows_clans_player_clan_data_eu = 'https://api.worldofwarships.eu/wows/clans/accountinfo/'
    wows_clans_player_clan_data_na = 'https://api.worldofwarships.com/wows/clans/accountinfo/'
    wows_clans_player_clan_data_asia = 'https://api.worldofwarships.asia/wows/clans/accountinfo/'
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
    async with aiohttp.ClientSession() as session:
        async with session.get(API, params=params) as resp:
            if 200 == resp.status:
                data = await resp.json()
                if data['status'] == 'ok':
                    return data['data']
                else:
                    print(data)
                    return {}
            else:
                print(resp.status)
                return {}


async def get_clan_tag(clan_id: str, server: int):
    wows_clans_clan_details_ru = 'https://api.worldofwarships.ru/wows/clans/info/'
    wows_clans_clan_details_eu = 'https://api.worldofwarships.eu/wows/clans/info/'
    wows_clans_clan_details_na = 'https://api.worldofwarships.com/wows/clans/info/'
    wows_clans_clan_details_asia = 'https://api.worldofwarships.asia/wows/clans/info/'
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
    async with aiohttp.ClientSession() as session:
        async with session.get(API, params=params) as resp:
            if 200 == resp.status:
                data = await resp.json()
                if data['status'] == 'ok':
                    return data['data']
                else:
                    print(data)
                    return {}
            else:
                print(resp.status)
                return {}


async def update_task(accounts: list, sender_id: int):
    tmp_list = []
    for account in accounts:
        account_id = account['account_id']
        server = account['server']
        item = await get_clan_data(account_id, server)
        if item != {}:
            if item[str(account_id)] is not None:
                nickName = item[str(account_id)]['account_name']
                if item[account_id] is None:
                    clan_tag = 'NO CLAN DATA'
                else:
                    clan_id = str(item[account_id]['clan_id'])
                    clan_details = await get_clan_tag(clan_id, server)
                    clan_tag = clan_details[clan_id]['tag']
                tmp_list.append({
                    'account_id': account_id,
                    'server': server,
                    'clan_tag': clan_tag,
                    'nickName': nickName
                })
            else:
                account['clan_tag'] = 'NO CLAN DATA'
                item = await get_user_data(account_id, server)
                if item == {}:
                    pass
                else:
                    account['nickName'] = item[account_id]['nickname']
                tmp_list.append(account)
        else:
            tmp_list.append(account)
    print('json' + str(sender_id))
    return [sender_id, tmp_list]


async def add_user(sender_id: int, user_add: dict):
    sender_id = str(sender_id)
    old_data = await read_user_data()
    if old_data[sender_id] is not None:
        tmp_list = old_data[sender_id]
        if len(tmp_list) < 6:
            add_stat = True
            for account in tmp_list:
                if account['account_id'] == user_add['account_id']:
                    add_stat = False
                    break
            if add_stat:
                tmp_list.append(user_add)
                old_data[sender_id] = tmp_list
            else:
                return 2
        else:
            return 1
    else:
        old_data[sender_id] = [user_add]
    async with aiofiles.open('src/wows_data/user_data.json', mode='w') as f:
        await f.write(json.dumps(old_data, ensure_ascii=False, indent=4))
    return 0


async def update_user_detail():
    user_detail = {}
    old_data = await read_user_data()
    task = []
    for sender_id, accounts in old_data.items():
        task.append(asyncio.create_task(update_task(accounts, sender_id)))
        await asyncio.sleep(random.randrange(50, 100) / 100)
    res = await asyncio.gather(*task)
    for item in res:
        sender_id = item[0]
        tmp_list = item[1]
        user_detail[sender_id] = tmp_list
    async with aiofiles.open('src/wows_data/user_data.json', mode='w') as f:
        await f.write(json.dumps(user_detail, ensure_ascii=False, indent=4))
    return


async def read_recent_data(account_id: str, days: int):
    async with aiosqlite.connect('src/wows_data/user_recent_data.db') as db:
        date_cmp = str(datetime.date.today() - datetime.timedelta(days=days))
        data_check = account_id + '_' + date_cmp
        shipList = {}
        try:
            cursor = await db.execute(
                "SELECT SHIP_ID, BATTLES, FRAGS, XP, DAMAGE, WINS, SURVIVED, SHOTS, HITS  from '%s'" % data_check)
            rows = await cursor.fetchall()
            for row in rows:
                ship_id = row[0]
                battles = row[1]
                frags = row[2]
                xp = row[3]
                damage = row[4]
                wins = row[5]
                survived = row[6]
                shots = row[7]
                hits = row[8]
                shipList[str(ship_id)] = {
                    'pvp': {
                        'battles': battles,
                        'frags': frags,
                        'damage_dealt': damage,
                        'wins': wins,
                        'xp': xp,
                        'survived_battles': survived,
                        'main_battery': {
                            'shots': shots,
                            'hits': hits
                        }
                    }
                }
            return shipList
        except Exception as e:
            print(e)
            return {}


async def update():
    await update_user_detail(),
    task = [
        asyncio.create_task(update_user_past_data()),
        asyncio.create_task(update_ship_data()),
    ]
    await asyncio.gather(*task)
    return


async def read_ship_dic():
    async with aiofiles.open('src/wows_data/wows_ship_list.json', 'r') as f:
        js = await f.read()
        json_dic = json.loads(js)
        data_name = {}
        for ship_id, ship in json_dic.items():
            data_name[ship['name']] = ship_id
        return data_name
