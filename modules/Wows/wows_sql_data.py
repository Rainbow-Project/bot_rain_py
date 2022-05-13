import json
import requests
import sqlite3


api_user = 'https://api.worldofwarships.SERVER/wows/ships/stats/?application_id=fc6d975614f91c3d2c87557577f4c60a' \
      '&account_id=WOWS_USER_ID '


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


def get_user_data_wg_api(user_wows_id: str, user_server: str):
    dataini = requests.get(api_user.replace('SERVER',user_server).replace('WOWS_USER_ID',user_wows_id))
    data = dataini.json()
    return data


def update():
    con = sqlite3.connect('src/wows_data/user_recent_data.db')
    c = con.cursor()
    dic = read_dic()
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


def read_sql_data(user_wows_id:str):
    con = sqlite3.connect("user_recent_data.db")
    c = con.cursor()
    dic = {}
    cursor = c.execute("SELECT ship_id, battles, damage_dealt, wins, frags  from '%s'" % user_wows_id)
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
    return dic
