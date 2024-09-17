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
import asyncpg

import ApiKeys

from wows.utility import User, Ship

application_id = ApiKeys.wowsApikey
pgsql_connect_url = ApiKeys.data_base


async def get_user_data(account_id: str, server: int):
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
    async with aiohttp.ClientSession() as session:
        async with session.get(API, params=params) as resp:
            if 200 == resp.status:
                data = await resp.json()
                if data["status"] == "ok":
                    return data["data"]
                else:
                    print(data)
                    return {}
            else:
                print(resp.status)
                return {}


async def update_ship_data():
    api = "https://api.wows-numbers.com/personal/rating/expected/json/"
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as resp:
            if 200 == resp.status:
                data = await resp.json()
                async with aiofiles.open("src/wows_data/wows_exp.json", mode="w") as f:
                    await f.write(json.dumps(data, ensure_ascii=False, indent=4))


async def read_user_data():
    async with aiofiles.open("src/wows_data/user_data.json", mode="r") as f:
        js = await f.read()
        try:
            dic = json.loads(js)
        except Exception:
            dic = {}
        return dic


async def update_user_ship_list(account_id: str, server: int):
    wows_warship_stat_ru = "https://api.worldofwarships.ru/wows/ships/stats/"
    wows_warship_stat_eu = "https://api.worldofwarships.eu/wows/ships/stats/"
    wows_warship_stat_na = "https://api.worldofwarships.com/wows/ships/stats/"
    wows_warship_stat_asia = "https://api.worldofwarships.asia/wows/ships/stats/"
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

    async with aiohttp.ClientSession() as session:
        async with session.get(API, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data["status"] == "ok":
                    shipList = data["data"][account_id]
                    today = datetime.date.today()
                    conn = await asyncpg.connect(pgsql_connect_url)
                    try:
                        for ship in shipList:
                            ship_id = ship["ship_id"]
                            battles = ship["pvp"]["battles"]
                            frags = ship["pvp"]["frags"]
                            XP = ship["pvp"]["xp"]
                            damage = ship["pvp"]["damage_dealt"]
                            wins = ship["pvp"]["wins"]
                            survived = ship["pvp"]["survived_battles"]
                            shots = ship["pvp"]["main_battery"]["shots"]
                            hits = ship["pvp"]["main_battery"]["hits"]
                            sql_cmd = """
                            INSERT INTO ships (account_id, ship_id, date, battles, wins, shots, hit, 
                            damage, frags, survive, xp) 
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                            ON CONFLICT (account_id, ship_id, date) DO
                            UPDATE SET battles = excluded.battles,
                                       wins = excluded.wins,
                                       shots = excluded.shots,
                                       hit = excluded.hit,
                                       damage = excluded.damage,
                                       frags = excluded.frags,
                                       survive = excluded.survive,
                                       xp = excluded.xp;
                            """
                            await conn.execute(
                                sql_cmd,
                                int(account_id),
                                int(ship_id),
                                today,
                                battles,
                                wins,
                                shots,
                                hits,
                                damage,
                                frags,
                                survived,
                                XP,
                            )
                    finally:
                        await conn.close()
                else:
                    print(data)
            else:
                print(resp.status)



async def wows_get_numbers_api():
    async with aiofiles.open("src/wows_data/wows_exp.json", mode="r") as f:
        js = await f.read()
        try:
            dic = json.loads(js)
        except Exception:
            dic = {}
        return dic


async def update_user_past_data():
    users = await read_user_data()
    async with asyncio.TaskGroup() as tg:
        for user in users.values():
            for accounts in user:
                account_id = accounts["account_id"]
                server = accounts["server"]
                tg.create_task(update_user_ship_list(account_id, server))
                await asyncio.sleep(random.randrange(10, 20) / 100)
    return


async def get_clan_data(account_id: str, server: int):
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
    async with aiohttp.ClientSession() as session:
        async with session.get(API, params=params) as resp:
            if 200 == resp.status:
                data = await resp.json()
                if data["status"] == "ok":
                    return data["data"]
                else:
                    print(data)
                    return {}
            else:
                print(resp.status)
                return {}


async def get_clan_tag(clan_id: str, server: int):
    wows_clans_clan_details_ru = "https://api.worldofwarships.ru/wows/clans/info/"
    wows_clans_clan_details_eu = "https://api.worldofwarships.eu/wows/clans/info/"
    wows_clans_clan_details_na = "https://api.worldofwarships.com/wows/clans/info/"
    wows_clans_clan_details_asia = "https://api.worldofwarships.asia/wows/clans/info/"
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
    async with aiohttp.ClientSession() as session:
        async with session.get(API, params=params) as resp:
            if 200 == resp.status:
                data = await resp.json()
                if data["status"] == "ok":
                    return data["data"]
                else:
                    print(data)
                    return {}
            else:
                print(resp.status)
                return {}


async def update_task(accounts: list, sender_id: int):
    tmp_list = []
    for account in accounts:
        account_id = account["account_id"]
        server = account["server"]
        item = await get_clan_data(account_id, server)
        if item != {}:
            if str(account_id) in item.keys() and item[str(account_id)] is not None:
                nickName = item[str(account_id)]["account_name"]
                if account_id not in item.keys():
                    clan_tag = "NO CLAN DATA"
                else:
                    clan_id = str(item[account_id]["clan_id"])
                    clan_details = await get_clan_tag(clan_id, server)
                    if clan_details != {}:
                        clan_tag = clan_details[clan_id]["tag"]
                    else:
                        clan_tag = "NO CLAN DATA"
                tmp_list.append(
                    {
                        "account_id": account_id,
                        "server": server,
                        "clan_tag": clan_tag,
                        "nickName": nickName,
                    }
                )
            else:
                account["clan_tag"] = "NO CLAN DATA"
                item = await get_user_data(account_id, server)
                if item == {}:
                    pass
                else:
                    account["nickName"] = item[account_id]["nickname"]
                tmp_list.append(account)
        else:
            tmp_list.append(account)
    print("json" + str(sender_id))
    return [sender_id, tmp_list]


async def add_user(sender_id: int, user_add: dict):
    sender_id = str(sender_id)
    old_data = await read_user_data()
    if sender_id in old_data.keys():
        tmp_list = old_data[sender_id]
        if len(tmp_list) < 6:
            add_stat = True
            for account in tmp_list:
                if account["account_id"] == user_add["account_id"]:
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
    async with aiofiles.open("src/wows_data/user_data.json", mode="w") as f:
        await f.write(json.dumps(old_data, ensure_ascii=False, indent=4))
    return 0


async def update_user_detail():
    user_detail = {}
    old_data = await read_user_data()
    tasks = []

    # Gather user details with update_task
    async with asyncio.TaskGroup() as tg:
        for sender_id, accounts in old_data.items():
            tasks.append(tg.create_task(update_task(accounts, sender_id)))
            await asyncio.sleep(random.randrange(50, 100) / 100)

    # Collect results from tasks
    results = [task.result() for task in tasks]
    for item in results:
        sender_id = item[0]
        user_detail[sender_id] = item[1]

    # Write user details to JSON file
    async with aiofiles.open("src/wows_data/user_data.json", mode="w") as f:
        await f.write(json.dumps(user_detail, ensure_ascii=False, indent=4))

    # Insert or update user details in PostgreSQL
    async with asyncpg.create_pool(pgsql_connect_url) as pool:
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for qid, accounts in user_detail.items():
                for account in accounts:
                    account_id = account["account_id"]
                    server = account["server"]
                    clan_tag = account["clan_tag"]
                    nickName = account["nickName"]
                    if clan_tag == "NO CLAN DATA":
                        clan_tag = None
                    sql_cmd = """
                    INSERT INTO users (account_id, server, nickName, clan_tag)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (account_id) DO
                    UPDATE SET server = excluded.server,
                               nickName = excluded.nickName,
                               clan_tag = excluded.clan_tag;
                    """
                    # Create a task and acquire a new connection for each task
                    tasks.append(tg.create_task(insert_user(pool, sql_cmd, account_id, server, nickName, clan_tag)))

        # Wait for all tasks to finish
        for task in tasks:
            await task

    return

# Helper function to execute the SQL command using a separate connection
async def insert_user(pool, sql_cmd, account_id, server, nickName, clan_tag):
    async with pool.acquire() as conn:
        await conn.execute(sql_cmd, int(account_id), server, nickName, clan_tag)


async def read_recent_data(account_id: str, days: int):
    date_cmp = datetime.date.today() - datetime.timedelta(days=days)
    sql_cmd = """
    SELECT ship_id, battles, frags, xp, damage, wins, survive, shots, hit
    FROM ships
    WHERE account_id = $1
    AND date = $2
    """
    
    conn = None
    try:
        conn = await asyncpg.connect(pgsql_connect_url)
        rows = await conn.fetch(sql_cmd, int(account_id), date_cmp)
        
        user = User()
        user.date = date_cmp
        ship_list = []

        user.battles = 0
        user.xp = 0
        user.wins = 0
        user.frags = 0
        user.shots = 0
        user.damage_dealt = 0
        user.hits = 0
        user.survived_battles = 0
        
        for row in rows:
            ship_id = row['ship_id']
            battles = row['battles']
            frags = row['frags']
            xp = row['xp']
            damage = row['damage']
            wins = row['wins']
            survived = row['survive']
            shots = row['shots']
            hits = row['hit']
            
            user.battles += battles
            user.xp += xp
            user.wins += wins
            user.frags += frags
            user.shots += shots
            user.hits += hits
            user.damage_dealt += damage
            user.survived_battles += survived

            ship_list.append(
                {
                    "pvp": {
                        "battles": battles,
                        "frags": frags,
                        "damage_dealt": damage,
                        "wins": wins,
                        "xp": xp,
                        "survived_battles": survived,
                        "main_battery": {"shots": shots, "hits": hits},
                    },
                    "ship_id": ship_id,
                    "last_battle_time": 0,
                }
            )
        
        user.update_displays()
        await user.async_init(ship_list)
        return user
    except Exception as e:
        print(e)
        return None
    finally:
        if conn is not None:
            await conn.close()



async def read_recent_data_auto(account_id: str, battles: int):
    sql_cmd_max_date = """
    SELECT MAX(date)
    FROM (
        SELECT date
        FROM ships
        WHERE account_id = $1
        GROUP BY date
        HAVING SUM(battles) <> $2
    ) subquery;
    """

    sql_cmd_select = """
    SELECT ship_id, battles, frags, xp, damage, wins, survive, shots, hit
    FROM ships
    WHERE account_id = $1
    AND date = $2
    """

    conn = None
    try:
        conn = await asyncpg.connect(pgsql_connect_url)
        date_result = await conn.fetchval(sql_cmd_max_date, int(account_id), int(battles))
        
        if not date_result:
            print("No data found.")
            return {}

        date = date_result
        print(date)

        user = User()
        user.battles = 0
        user.xp = 0
        user.wins = 0
        user.frags = 0
        user.shots = 0
        user.damage_dealt = 0
        user.hits = 0
        user.survived_battles = 0
        user.date = date

        ship_list = []

        rows = await conn.fetch(sql_cmd_select, int(account_id), date)
        for row in rows:
            ship_id = row['ship_id']
            battles = row['battles']
            frags = row['frags']
            xp = row['xp']
            damage = row['damage']
            wins = row['wins']
            survived = row['survive']
            shots = row['shots']
            hits = row['hit']

            user.battles += battles
            user.xp += xp
            user.wins += wins
            user.frags += frags
            user.shots += shots
            user.hits += hits
            user.damage_dealt += damage
            user.survived_battles += survived

            ship_list.append(
                {
                    "pvp": {
                        "battles": battles,
                        "frags": frags,
                        "damage_dealt": damage,
                        "wins": wins,
                        "xp": xp,
                        "survived_battles": survived,
                        "main_battery": {"shots": shots, "hits": hits},
                    },
                    "ship_id": ship_id,
                    "last_battle_time": 0,
                }
            )

        user.update_displays()
        await user.async_init(ship_list)
        return user
    except Exception as e:
        print(e)
        return None
    finally:
        if conn is not None:
            await conn.close()


async def remove():
    ddl = datetime.date.today() - datetime.timedelta(days=30)

    conn = None
    try:
        conn = await asyncpg.connect(pgsql_connect_url)
        await conn.execute("""
            DELETE FROM ships
            WHERE date < $1
        """, ddl)
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            await conn.close()



async def table_check() -> None:
    drop_users = """
    DROP TABLE IF EXISTS users;
    """
    init_users = """
    CREATE TABLE users(
        account_id BIGINT NOT NULL,
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
        account_id BIGINT NOT NULL,
        ship_id BIGINT NOT NULL,
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
    
    conn = None
    try:
        conn = await asyncpg.connect(pgsql_connect_url)
        tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        table_names = {table['table_name'] for table in tables}
        
        if 'users' not in table_names:
            await conn.execute(drop_users)
            await conn.execute(init_users)
        
        if 'ships' not in table_names:
            await conn.execute(drop_ships)
            await conn.execute(init_ships)
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            await conn.close()


async def update():
    await table_check()
    await update_user_detail()
    await remove()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(update_user_past_data())
        tg.create_task(update_ship_data())

    return


async def read_ship_dic():
    async with aiofiles.open("src/wows_data/wows_ship_list.json", "r") as f:
        js = await f.read()
        json_dic = json.loads(js)
        data_name = {}
        for ship_id, ship in json_dic.items():
            data_name[ship["name"]] = ship_id
        return data_name


async def remove_user(sender_id: int, user_remove: str):
    # Read existing user data
    user_dic = await read_user_data()
    
    # Check if sender_id exists in the user dictionary
    if str(sender_id) in user_dic:
        if len(user_dic[str(sender_id)]) == 1:
            # Remove the sender_id entry if only one account is left
            user_dic.pop(str(sender_id))
        else:
            # Remove the specific account if multiple accounts exist
            accounts = user_dic[str(sender_id)]
            new_accounts = [account for account in accounts if account["account_id"] != user_remove]
            user_dic[str(sender_id)] = new_accounts

        # Update the user data JSON file
        async with aiofiles.open("src/wows_data/user_data.json", mode="w") as f:
            await f.write(json.dumps(user_dic, ensure_ascii=False, indent=4))

    # Check if the user_remove account_id still exists in the updated dictionary
    user_exists = any(account["account_id"] == user_remove for user_list in user_dic.values() for account in user_list)

    if not user_exists:
        # Remove the user from the PostgreSQL database if no longer present in the dictionary
        conn = await asyncpg.connect(pgsql_connect_url)
        try:
            sql_cmd = "DELETE FROM users WHERE account_id = $1"
            await conn.execute(sql_cmd, int(user_remove))
        except Exception as e:
            print(e)
        finally:
            await conn.close()

async def get_user_battles_since(account_id: int, server: int, start_time: datetime, ship_ids: list[int]):
    query = """
    SELECT account_id, ship_id, last_battle_time, battles, damage_dealt, wins, xp, frags, survived_battles, shots, hits
    FROM recents
    WHERE account_id = $1 AND server = $2 AND last_battle_time >= $3 AND ship_id = ANY($4)
    """
    start_time = datetime.datetime.combine(start_time, datetime.time(2, 32, 0))
    conn = await asyncpg.connect(pgsql_connect_url)
    try:
        results = await conn.fetch(query, int(account_id), server, start_time, ship_ids)
    finally:
        await conn.close()
    return results