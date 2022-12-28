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
                    async with aiosqlite.connect('src/wows_data/user_recent_data.db') as db:
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
                            sql_cmd = """INSERT INTO ships (account_id, ship_id, date, battles, wins, shots, hit, 
                            damage, frags, survive, xp) VALUES (?,?,?,?,?,?,?,?,?,?,?)
                            ON CONFLICT (account_id, ship_id, date) DO
                            UPDATE SET account_id=excluded.account_id,
                            ship_id=excluded.ship_id,
                            date=excluded.date,
                            battles=excluded.battles,
                            wins=excluded.wins,
                            shots=excluded.shots,
                            hit=excluded.hit
                            ; """
                            await db.execute(sql_cmd, (
                                account_id, ship_id, today, battles, wins, shots, hits, damage, frags, survived, XP))
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
            if str(account_id) in item.keys() and item[str(account_id)] is not None:
                nickName = item[str(account_id)]['account_name']
                if account_id not in item.keys():
                    clan_tag = 'NO CLAN DATA'
                else:
                    clan_id = str(item[account_id]['clan_id'])
                    clan_details = await get_clan_tag(clan_id, server)
                    if clan_details != {}:
                        clan_tag = clan_details[clan_id]['tag']
                    else:
                        clan_tag = 'NO CLAN DATA'
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
    if sender_id in old_data.keys():
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
    async with aiosqlite.connect('src/wows_data/user_recent_data.db') as db:
        insert_task = []
        for qid, accounts in user_detail.items():
            for account in accounts:
                account_id = account['account_id']
                server = account['server']
                clan_tag = account['clan_tag']
                nickName = account['nickName']
                if clan_tag == 'NO CLAN DATA':
                    clan_tag = None
                sql_cmd = """
                INSERT INTO users (account_id, server, nickName, clan_tag)
                VALUES (?,?,?,?)
                ON CONFLICT (account_id) DO
                UPDATE SET account_id=excluded.account_id,
                           server=excluded.server,
                           nickName=excluded.nickName,
                           clan_tag=excluded.clan_tag
                ;
                """
                insert_task.append(asyncio.create_task(db.execute(sql_cmd, (account_id, server, nickName, clan_tag))))
        await asyncio.gather(*insert_task)
        await db.commit()
    return


async def read_recent_data(account_id: str, days: int):
    async with aiosqlite.connect('src/wows_data/user_recent_data.db') as db:
        date_cmp = str(datetime.date.today() - datetime.timedelta(days=days))
        shipList = {}
        sql_cmd = """
        SELECT ship_id, battles, frags, xp, damage, wins, survive,shots, hit
        FROM ships
        WHERE account_id = ?
        AND date = ?
        """
        try:
            cursor = await db.execute(sql_cmd, (account_id, date_cmp))
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


async def remove():
    ddl = str(datetime.date.today() - datetime.timedelta(days=30))
    async with aiosqlite.connect('src/wows_data/user_recent_data.db') as db:
        await db.execute("""DELETE FROM ships where date < '{}'""".format(ddl))
        await db.commit()


async def table_check() -> None:
    drop_users = """
    DROP TABLE IF EXISTS users;
    """
    pr_on = """
    PRAGMA foreign_keys = ON;
    """
    init_users = """
    CREATE TABLE users(
        account_id INT NOT NULL,
        server INT NOT NULL,
        nickName TEXT NOT NULL,
        clan_tag TEXT,
        PRIMARY KEY (account_id)
    );
    """
    drop_ships = """
    DROP TABLE IF EXISTS ships;
    """
    init_ships = """
    CREATE TABLE ships(
        account_id INT NOT NULL,
        ship_id INT NOT NULL,
        date DATE NOT NULL,
        battles INT NOT NULL,
        wins INT NOT NULL,
        shots INT NOT NULL,
        hit INT NOT NULL,
        damage INT NOT NULL,
        frags INT NOT NULL,
        survive INT NOT NULL,
        xp INT NOT NULL,
        PRIMARY KEY (account_id, ship_id, date),
        FOREIGN KEY (account_id) REFERENCES users(account_id) ON DELETE CASCADE
    );
    """
    async with aiosqlite.connect('src/wows_data/user_recent_data.db') as db:
        cur = await db.execute("SELECT name _id FROM sqlite_master WHERE type ='table'")
        tables = await cur.fetchall()
        await db.execute(pr_on)
        if ("users",) not in tables:
            await db.execute(drop_users)
            await db.execute(init_users)
        if ("ships",) not in tables:
            await db.execute(drop_ships)
            await db.execute(init_ships)
    return


async def update():
    await table_check()
    await update_user_detail()
    await remove()
    task = [
        asyncio.create_task(update_user_past_data()),
        asyncio.create_task(update_ship_data()),
    ]
    await asyncio.gather(*task)
    await update_res()
    return


async def read_ship_dic():
    async with aiofiles.open('src/wows_data/wows_ship_list.json', 'r') as f:
        js = await f.read()
        json_dic = json.loads(js)
        data_name = {}
        for ship_id, ship in json_dic.items():
            data_name[ship['name']] = ship_id
        return data_name


async def remove_user(sender_id: int, user_remove: str):
    user_dic = await read_user_data()
    if len(user_dic[str(sender_id)]) == 1:
        user_dic.pop(str(sender_id))
    else:
        accounts = user_dic[str(sender_id)]
        new_accounts = []
        for account in accounts:
            if account["account_id"] == user_remove:
                pass
            else:
                new_accounts.append(account)
        user_dic[str(sender_id)] = new_accounts
    async with aiofiles.open('src/wows_data/user_data.json', mode='w') as f:
        await f.write(json.dumps(user_dic, ensure_ascii=False, indent=4))
    cnt = 0
    for user in user_dic.values():
        for account in user:
            if account["account_id"] == user_remove:
                cnt = 1
                break
        if cnt == 1:
            break
    if cnt == 0:
        async with aiosqlite.connect('src/wows_data/user_recent_data.db') as db:
            pr_on = """
            PRAGMA foreign_keys = ON;
            """
            sql_cmd = """DELETE FROM users WHERE account_id == ?"""
            await db.execute(pr_on)
            await db.execute(sql_cmd, (int(user_remove),))
            await db.commit()
    return


async def update_res():
    REs = []
    tasks = []
    async with aiofiles.open('src/wows_data/wows_ship_list.json', 'r') as f:
        js = await f.read()
        ships = json.loads(js)
    for ship_id, ship in ships.items():
        if ship['RE']:
            REs.append(ship_id)
    users = await read_user_data()
    async with aiosqlite.connect('src/wows_data/user_recent_data.db') as db:
        for qid, accounts in users.items():
            for account in accounts:
                account_id = account['account_id']
                server = account['server']
                tasks.append(asyncio.create_task(update_account_re(account_id, REs, server, db)))
        await asyncio.gather(*tasks)
        await db.commit()


async def update_account_re(account_id: str, REs: list, server: int, db):
    match server:
        case 0:
            s = 'asia'
        case 1:
            s = 'ru'
        case 2:
            s = 'eu'
        case 3:
            s = 'com'
    today = str(datetime.date.today())
    for ship_id in REs:
        API = 'https://vortex.worldofwarships.{}/api/accounts/{}/ships/{}/pvp/'.format(s, account_id, ship_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(API) as resp:
                if 200 == resp.status:
                    data = await resp.json()
                    if data['status'] == 'ok':
                        if data['data'][str(account_id)]['statistics'] != {} and data['data'][str(account_id)]['statistics'][str(ship_id)]['pvp'] != {}:
                            try:
                                print('RE ship {} ,user {}'.format(ship_id, account_id))
                                ship = data['data'][str(account_id)]['statistics'][str(ship_id)]['pvp']
                                battles = ship['battles_count']
                                frags = ship['frags']
                                XP = ship['exp']
                                damage = ship['damage_dealt']
                                wins = ship['wins']
                                survived = ship['survived']
                                shots = ship['shots_by_main']
                                hits = ship['hits_by_main']
                                sql_cmd = """INSERT INTO ships (account_id, ship_id, date, battles, wins, shots, hit, 
                                damage, frags, survive, xp) VALUES (?,?,?,?,?,?,?,?,?,?,?)
                                ON CONFLICT (account_id, ship_id, date) DO
                                UPDATE SET account_id=excluded.account_id,
                                ship_id=excluded.ship_id,
                                date=excluded.date,
                                battles=excluded.battles,
                                wins=excluded.wins,
                                shots=excluded.shots,
                                hit=excluded.hit
                                ; """
                                await db.execute(sql_cmd, (
                                    account_id, ship_id, today, battles, wins, shots, hits, damage, frags, survived,
                                    XP))
                            except Exception as e:
                                print(e)
                                print(account_id, ship_id)
                                print(data['data'][str(account_id)]['statistics'][str(ship_id)]['pvp'])
                        else:
                            print('No ship')
                    else:
                        print(data)
                else:
                    print(resp.status)
