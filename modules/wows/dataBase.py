# -*- coding: UTF-8 -*-
"""
@Project ：Bot_rain
@File    ：dataBase.py
@Author  ：INTMAX
@Date    ：2022-06-03 7:50 p.m. 
"""
import json
import sqlite3
import requests

import ApiKeys
from modules.wows import APIs


def updata_ship_data():
    api = 'https://api.wows-numbers.com/personal/rating/expected/json/'

    dataini = requests.get(api)
    data = dataini.json()
    with open("src/wows_data/wows_exp.json", 'w') as f:
        f.write(json.dumps(data))


def read_user_data():
    file = open('src/wows_data/user_data.data', 'r')
    js = file.read()
    try:
        dic = json.loads(js)
    except Exception:
        dic = {}
    print(dic)
    file.close()
    return dic


def get_user_data_wg_api(user_wows_id: str, user_server: str):
    api_user = 'https://api.worldofwarships.SERVER/wows/ships/stats/?application_id=1145141919810' \
               '&account_id=WOWS_USER_ID '
    dataini = requests.get(
        api_user.replace('SERVER', user_server).replace('WOWS_USER_ID', user_wows_id).replace('1145141919810',
                                                                                              ApiKeys.wowsApikey))
    data = dataini.json()
    return data


def update():
    updata_ship_data()
    con = sqlite3.connect('src/wows_data/user_recent_data.db')
    c = con.cursor()
    dic = read_user_data()
    for i in dic.values():
        user_wows_id = i[0]
        user_server = i[1]
        c = con.cursor()
        try:
            c.execute("DROP TABLE '%s'" % user_wows_id)
        except:
            None

        c.execute('''CREATE TABLE '%s'
               (ship_id INT NOT NULL,
               battles INT NOT NULL,
               damage_dealt INT NOT NULL,
               wins  INT NOT NULL,
               frags INT NOT NULL);''' % user_wows_id)
        data_ini = get_user_data_wg_api(user_wows_id, user_server)
        if data_ini['status'] == 'ok':
            data = data_ini['data'][user_wows_id]
            for i in data:
                dic_tmp = {}
                ship_id = i['ship_id']
                i = i['pvp']
                battles = i['battles']
                damage_dealt = i['damage_dealt']
                wins = i['wins']
                frags = i['frags']
                sql_cmd = '''INSERT INTO '%s' (ship_id,battles,damage_dealt,wins,frags) VALUES (%d,%d,%d,%d,%d)''' % (
                    user_wows_id, ship_id, battles, damage_dealt, wins, frags)
                c.execute(sql_cmd)
    con.commit()
    con.close()
    return


def read_sql_data(account_id: str):
    con = sqlite3.connect('src/wows_data/user_recent_data.db')
    c = con.cursor()
    dic = {}
    try:
        cursor = c.execute("SELECT ship_id, battles, damage_dealt, wins, frags  from '%s'" % account_id)
        for row in cursor:
            dic_tmp = {}
            ship_id = row[0]
            battles = row[1]
            damage_dealt = row[2]
            wins = row[3]
            frags = row[4]
            dic_tmp['battles'] = battles
            dic_tmp['damage_dealt'] = damage_dealt
            dic_tmp['wins'] = wins
            dic_tmp['frags'] = frags
            dic[str(ship_id)] = dic_tmp
    except Exception:
        return {}
    return dic


def wows_get_numbers_api():
    data: json
    with open("src/wows_data/wows_exp.json", "r") as f:
        return json.load(f)


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


def get_ship_id_fuzzy(ship_name: str):
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


def get_ship_name(ship_id: str):
    dict_temp = {}
    with open("src/wows_data/wows_ship_official_name.txt", 'r') as f:
        for line in f.readlines():
            line = line.strip()
            k = line.split(' ')[0]
            v = line.split(' ')[1]
            dict_temp[k] = v
    if ship_id in dict_temp.keys():
        return dict_temp[ship_id]
    else:
        return ''


def add_user(QQ_ID: int, account_id: str, server: str):
    dic = read_user_data()
    lis = []
    lis += [str(account_id)]
    lis += [server]
    dic[QQ_ID] = lis
    json_str = json.dumps(dic)
    file = open('src/wows_data/user_data.data', 'w')
    file.write(json_str)
    file.close()


def get_dev():
    with open('src/wows_data/DEV.DEV', 'r') as f:
        line = f.readline()
        if line == '1':
            return True
        else:
            return False


def set_dev(mode):
    with open('src/wows_data/DEV.DEV', 'w') as f:
        f.write(mode)
