import json
import requests
import sqlite3


def updata_ship_data():
    api = 'https://api.wows-numbers.com/personal/rating/expected/json/'

    dataini = requests.get(api)
    data = dataini.json()
    data
    data
    with open("src/wows_data/wows_exp.json", 'w') as f:
        f.write(json.dumps(data))


api_user = 'https://api.worldofwarships.SERVER/wows/ships/stats/?application_id=1145141919810' \
           '&account_id=WOWS_USER_ID '
wows_API_ID = "1145141919810"

def read_dic():
    with open('src/wows_data/user_data.data', 'r') as file:
        js = file.read()
        try:
            dic = json.loads(js)
        except:
            dic = {}
        print(dic)
    return dic


def get_user_data_wg_api(user_wows_id: str, user_server: str):
    dataini = requests.get(api_user.replace('SERVER', user_server).replace('WOWS_USER_ID', user_wows_id).replace('1145141919810',wows_API_ID))
    return dataini.json()


def update():
    updata_ship_data()
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
            dic_tmp = {}
            for i in data:
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


def read_sql_data(user_wows_id: str):
    con = sqlite3.connect('src/wows_data/user_recent_data.db')
    c = con.cursor()
    dic = {}
    try:
        cursor = c.execute("SELECT ship_id, battles, damage_dealt, wins, frags  from '%s'" % user_wows_id)
        for row in cursor:
            ship_id = row[0]
            battles = row[1]
            damage_dealt = row[2]
            wins = row[3]
            frags = row[4]
            dic_tmp = {
                'battles': battles,
                'damage_dealt': damage_dealt,
                'wins': wins,
                'frags': frags,
            }

            dic[str(ship_id)] = dic_tmp
    except:
        return {}
    return dic
