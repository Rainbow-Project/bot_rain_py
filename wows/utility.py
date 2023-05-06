import math
import aiofiles
import json
import datetime
import cv2 as cv
import freetype as ft
import numpy as np


class Ship:
    """
    这是一个对 船只抽象的类

    Returns:
        Ship: 一个船只对象
    """
    org_json = None

    ship_id = None
    ship_name = None
    last_battle_time = None
    distance = None

    battles = None
    wins = None
    damage_dealt = None
    xp = None
    frags = None
    survived_battles = None
    shots = None
    hits = None

    max_damage_dealt = None
    max_damage_scouting = None
    max_frags = None
    max_planes_killed = None
    max_total_agro = None
    max_xp = None
    max_ships_spotted = None

    pr = None

    display_battles = None
    display_winrate = None
    display_damage = None
    display_xp = None
    display_kd = None
    display_accu_rate = None

    def __init__(self) -> None:
        pass

    def init_ship(self, ship_dict: dict, ship_list:dict, expected_data) -> None:
        # 原始数据
        self.org_json = ship_dict
        # 基本数据
        self.ship_id = ship_dict['ship_id']
        self.ship_name = ship_list[str(self.ship_id)]['name']
        # 非战斗数据
        date = datetime.datetime.fromtimestamp(ship_dict['last_battle_time'])
        self.last_battle_time = date.strftime("%Y-%m-%d %H:%M:%S")
        self.distance = None
        # pvp 数据
        pvp = ship_dict['pvp']
        # 战斗数据
        self.battles = pvp['battles']
        self.damage_dealt = pvp['damage_dealt']
        self.wins = pvp['wins']
        self.xp = pvp['xp']
        self.frags = pvp['frags']
        self.survived_battles = pvp['survived_battles']
        self.shots = pvp['main_battery']['shots']
        self.hits = pvp['main_battery']['hits']
        # 最佳数据
        self.max_damage_dealt = pvp['max_damage_dealt']
        self.max_damage_scouting = pvp['max_damage_scouting']
        self.max_frags = pvp['max_frags_battle']
        self.max_planes_killed = pvp['max_planes_killed']
        self.max_total_agro = pvp['max_total_agro']
        self.max_xp = pvp['max_xp']
        self.max_ships_spotted = pvp['max_ships_spotted']
        # 显示数据
        self.display_battles = f'{self.battles}'
        self.display_damage = f'{round(self.damage_dealt / self.battles)}'
        if self.survived_battles == self.battles:
            self.display_kd = 'N/A'
        else:
            self.display_kd = f'{round(self.frags / (self.battles - self.survived_battles), 2)}'
        if self.shots == 0:
            self.display_accu_rate = 'N/A'
        else:
            self.display_accu_rate = format(self.hits / self.shots, '.2%')
        self.display_winrate = format(self.wins / self.battles, '.2%')
        self.display_xp = f'{round(self.xp / self.battles)}'
        # PR 数据
        self.pr = Pr()
        self.pr.init_pr_ship(self, expected_data)
    
    def __sub__(self, other):
            new_ship = Ship()
            new_ship.battles = self.battles - other.battles
            new_ship.wins = self.wins - other.wins
            new_ship.damage_dealt = self.damage_dealt - other.damage_dealt
            new_ship.xp = self.xp - other.xp
            new_ship.frags = self.frags - other.frags
            new_ship.ship_name = self.ship_name
            new_ship.last_battle_time = self.last_battle_time
            new_ship.ship_id = self.ship_id
            new_ship.pr = Pr()
            new_ship.pr.init_pr_ship(new_ship)
            return new_ship
    
    def __it__(self, other):
        return self.last_battle_time < other.last_battle_time
    
    def __eq__(self, other):
        return self.last_battle_time == other.last_battle_time
        

class User:
    """
    这是一个对 用户抽象的类

    Returns:
        User: 一个用户对象
    """
    account_id = None
    nick_name = None
    server = None

    org_json = None

    # 非战斗数据
    last_battle_time = None  # 上次战斗
    leveling_tier = None  # 等级
    created_at = None  # 账号创建时间
    hidden_profile = None  # 隐藏战绩
    logout_at = None  # 上次退出游戏
    distance = None  # 航行长度

    # 战斗数据
    # 基本战斗数据
    battles = None  # 战斗场数
    wins = None  # 胜场
    losses = None  # 败场
    damage_dealt = None  # 总伤害
    xp = None  # 总经验
    frags = None  # 总k头
    survived_battles = None
    # 主炮参数
    frags_battery = None  # 主炮k头
    hits = None  # 主炮命中
    shots = None  # 发射
    # 详细数据
    draws = None  # 平局
    ships_spotted = None  # 点亮数

    # 最佳数据
    max_damage_dealt = None  # 最大伤害
    max_frags = None  # 最大k头
    max_planes_killed = None
    max_xp = None  # 最高xp
    max_ships_spotted = None  # 最佳点亮
    max_damage_scouting = None  # 最大点亮伤害
    max_total_agro = None  # 最大潜在

    # 船表
    ship_list = None  # 玩家船只列表
    ship_dic = None

    # PR
    pr = None  # pr 数值

    # 显示数据
    display_battles = None
    display_winrate = None
    display_damage = None
    display_xp = None
    display_kd = None
    display_accu_rate = None

    clan_id = None
    clan_tag = None

    def __init__(self) -> None:
        pass

    def init_user(self, user: dict, ships: dict, server: int, clan_id, clan_tag) -> None:
        self.org_json = user
        
        self.clan_id = clan_id
        self.clan_tag = clan_tag

        self.account_id = user['account_id']
        self.nick_name = user['nickname']
        self.server = server

        # 非战斗数据
        date = datetime.datetime.fromtimestamp(user['last_battle_time'])
        self.last_battle_time = date.strftime("%Y-%m-%d %H:%M:%S")  # 上次战斗
        self.leveling_tier = user['leveling_tier']  # 等级
        date = datetime.datetime.fromtimestamp(user['created_at'])
        self.created_at = date.strftime("%Y-%m-%d %H:%M:%S")
        self.hidden_profile = user['hidden_profile']  # 隐藏战绩
        self.logout_at = user['logout_at']  # 上次退出游戏

        pvp = user['statistics']['pvp']

        # 战斗数据
        # 基本战斗数据
        self.battles = pvp['battles']
        self.damage_dealt = pvp['damage_dealt']
        self.wins = pvp['wins']
        self.xp = pvp['xp']
        self.frags = pvp['frags']
        self.survived_battles = pvp['survived_battles']
        self.shots = pvp['main_battery']['shots']
        self.hits = pvp['main_battery']['hits']

        # 最佳数据
        self.max_damage_dealt = pvp['max_damage_dealt']
        self.max_damage_scouting = pvp['max_damage_scouting']
        self.max_frags = pvp['max_frags_battle']
        self.max_planes_killed = pvp['max_planes_killed']
        self.max_total_agro = pvp['max_total_agro']
        self.max_xp = pvp['max_xp']
        self.max_ships_spotted = pvp['max_ships_spotted']

        # 显示数据
        self.display_battles = f'{self.battles}'
        self.display_damage = f'{round(self.damage_dealt / self.battles)}'
        if self.survived_battles == self.battles:
            self.display_kd = 'N/A'
        else:
            self.display_kd = f'{round(self.frags / (self.battles - self.survived_battles), 2)}'
        if self.shots == 0:
            self.display_accu_rate = 'N/A'
        else:
            self.display_accu_rate = format(self.hits / self.shots, '.2%')
        self.display_winrate = format(self.wins / self.battles, '.2%')
        self.display_xp = f'{round(self.xp / self.battles)}'

    async def async_init(self, ships) -> None:
        ship_ls = await read_ship_dic()
        exps = await wows_get_numbers_api()
        # 船表
        self.ship_list = []  # 玩家船只列表
        self.ship_dic = {}
        for ship in ships:
            if ship['pvp']['battles'] != 0 and str(ship['ship_id']) in ship_ls.keys():
                ship_add = Ship()
                ship_add.init_ship(ship, ship_ls, exps)
                # self.ship_list.append(ship_add)
                self.ship_dic[str(ship['ship_id'])] = ship_add
        self.ship_list = list(self.ship_dic.values())

        # PR
        self.pr = Pr()  # pr 数值
        self.pr.init_pr_user(self.ship_list)
    def __sub__(self, other):
        other = self
        if self.battles == other.battles:
            raise Exception('场次未发生变化')
        else:
            new_user = User()
            new_user.battles = self.battles - other.battles
            new_user.wins = self.wins - other.wins
            new_user.damage_dealt = self.damage_dealt - other.damage_dealt
            new_user.xp = self.xp - other.xp
            new_user.frags = self.frags - other.frags
            new_user.nick_name = self.nick_name
            new_user.clan_tag = self.clan_tag
            new_user.ship_list = []
            old_ship_map = other.ship_dic
            for ship_now in self.ship_list:
                ship_past = old_ship_map.get(str(ship_now.ship_id), None)
                if ship_past == None:
                    continue
                else:
                    if ship_now.battles == ship_past.battles:
                        continue
                    else:
                        new_user.ship_list.append(ship_now - ship_past)
            new_user.ship_list = sorted(new_user.ship_list)
            new_user.pr = Pr()
            new_user.pr.init_pr_user(new_user)
            return new_user


class Pr:
    
    pr_text = None
    pr_number = None
    pr_color = None
    color_background = None
    color_text = None
 

    def __init__(self) -> None:
        pass

    def init_pr_user(self, ships:list[Ship]) -> None:
        total_pr = 0
        total_battles = 0

        for ship in ships:
            total_pr += (ship.pr.pr_number * ship.battles)
            total_battles += ship.battles

        self.pr_number = round(total_pr / total_battles)

        self.color_init()

    def init_pr_ship(self, ship: Ship, expected_data: dict) -> None:
        ship_id = ship.ship_id

        battles = ship.battles

        exp_damage = expected_data['data'][str(ship_id)]['average_damage_dealt']
        exp_frags = expected_data['data'][str(ship_id)]['average_frags']
        exp_winrate = expected_data['data'][str(ship_id)]['win_rate']

        damage = ship.damage_dealt / ship.battles
        frags = ship.frags / ship.battles
        winrate = (ship.wins / ship.battles) * 100

        r_dmg = damage / exp_damage
        r_frags = frags / exp_frags
        r_winrate = winrate / exp_winrate


        w1 = 1 / (1 + math.exp(-0.7 * (battles - 3)))
        w2 = 1 / (1 + math.exp(-20 * (winrate - 0.50)))

        w_wins = (1000 * w1) - ((1000 * w1 * 0.35) * w2)
        w_dmg = (1000 * (1 - w1)) + ((1000 * w1 * 0.35) * w2)
        w_frags = 150

        n_dmg = max(0, (r_dmg - 0.4) / (1 - 0.4))
        n_frags = max(0, (r_frags - 0.1) / (1 - 0.1))
        n_wins = max(0, (r_winrate - 0.7) / (1 - 0.7))

        self.pr_number = round((w_dmg * n_dmg) + (w_frags * n_frags) + (w_wins * n_wins))

        self.color_init()

    def color_init(self) -> None:
        if self.pr_number <= 750:
            self.pr_color = (255, 0, 0)
            self.color_background = (255, 226, 230)
            self.color_text = (255, 255, 255)
            self.pr_text = '还需努力'
        elif self.pr_number <= 1100:
            self.pr_color = (255, 140, 0)
            self.color_background = (255, 140, 0)
            self.color_text = (0, 0, 0)
            self.pr_text = '低于平均'
        elif self.pr_number <= 1350:
            self.pr_color = (255, 255, 102)
            self.color_background = (255, 219, 153)
            self.color_text = (0, 0, 0)
            self.pr_text = '平均水平'
        elif self.pr_number <= 1550:
            self.pr_color = (0, 205, 0)
            self.color_background = (166, 255, 144)
            self.color_text = (0, 0, 0)
            self.pr_text = '好'
        elif self.pr_number <= 1750:
            self.pr_color = (0, 139, 0)
            self.color_background = (118, 255, 64)
            self.color_text = (0, 0, 0)
            self.pr_color = '很好'
        elif self.pr_number <= 2100:
            self.pr_color = (0, 255, 255)
            self.color_background = (203, 255, 247)
            self.color_text = (0, 0, 0)
            self.pr_text = '非常好'
        elif self.pr_number <= 2450:
            self.pr_color = (255, 52, 179)
            self.color_background = (255, 173, 223)
            self.color_text = (0, 0, 0)
            self.pr_text = '大佬平均'
        else:
            self.pr_color = (139, 0, 139)
            self.color_background = (207, 85, 255)
            self.color_text = (255, 255, 255)
            self.pr_text = '神佬平均'
        
async def read_ship_dic():
    async with aiofiles.open('src/wows_data/wows_ship_list.json', 'r') as f:
        js = await f.read()
        json_dic = json.loads(js)
        return json_dic
    
async def wows_get_numbers_api():
    async with aiofiles.open('src/wows_data/wows_exp.json', mode='r') as f:
        js = await f.read()
        try:
            dic = json.loads(js)
        except Exception:
            dic = {}
        return dic
    
def render_text(image, text, center_position, font, font_size, color):
    face = font
    face.set_char_size(font_size * 64)

    slot = face.glyph

    # 计算文本宽度
    text_width = 0
    for c in text:
        face.load_char(c, ft.FT_LOAD_RENDER | ft.FT_LOAD_FORCE_AUTOHINT)
        text_width += slot.advance.x >> 6

    # 计算起始 x 位置以使文本居中
    x_position = center_position[0] - (text_width // 2)

    for i, c in enumerate(text):
        face.load_char(c, ft.FT_LOAD_RENDER | ft.FT_LOAD_FORCE_AUTOHINT)
        bitmap = slot.bitmap

        x_pos = x_position + slot.bitmap_left
        y_pos = center_position[1] - slot.bitmap_top

        img_height, img_width = image.shape[:2]
        glyph_height, glyph_width = bitmap.rows, bitmap.width

        for y in range(glyph_height):
            for x in range(glyph_width):
                if y + y_pos < img_height and x + x_pos < img_width:
                    pixel = image[y + y_pos, x + x_pos]
                    glyph_pixel = bitmap.buffer[y * bitmap.pitch + x]

                    blended_pixel = ((1 - (glyph_pixel / 255.0)) * pixel + (glyph_pixel / 255.0) * np.array(color)).astype(np.uint8)
                    image[y + y_pos, x + x_pos] = blended_pixel

        x_position += slot.advance.x >> 6


async def wows_user(user: User):
    main_data_img = cv.imread('components/main_data.png')
    max_data_img = cv.imread('components/max_main.png')
    pr_bar_img = cv.imread('components/pr_bar.png') 
    color_bg = user.pr.color_background[::-1]
    color_pr = user.pr.pr_color[::-1]
    pr_bar_img[:,:,0][pr_bar_img[:,:,0] == 222] = color_pr[0]
    pr_bar_img[:,:,1][pr_bar_img[:,:,1] == 222] = color_pr[1]
    pr_bar_img[:,:,2][pr_bar_img[:,:,2] == 222] = color_pr[2]

    main_data_img[:,:,0][main_data_img[:,:,0] == 222] = color_bg[0]
    main_data_img[:,:,1][main_data_img[:,:,1] == 222] = color_bg[1]
    main_data_img[:,:,2][main_data_img[:,:,2] == 222] = color_bg[2]

    max_data_img[:,:,0][max_data_img[:,:,0] == 222] = color_bg[0]
    max_data_img[:,:,1][max_data_img[:,:,1] == 222] = color_bg[1]
    max_data_img[:,:,2][max_data_img[:,:,2] == 222] = color_bg[2]

    font_medium = 'src/font/SourceHanSans-Medium.otf'
    font_heavy = 'src/font/SourceHanSans-Heavy.otf'
    font_medium = ft.Face(font_medium)
    font_heavy = ft.Face(font_heavy)

    img = np.full((1900, 1242, 3), 255, dtype=np.uint8)
    img[336:336 + 120, :] = pr_bar_img
    img[483:483 + 650, :] = main_data_img
    img[1160:1160 + 650, :] = max_data_img

    render_text(img, user.clan_tag, (621, 66), font_heavy, 48, user.pr.color_text)
    render_text(img, user.nick_name, (621, 152), font_medium, 48, user.pr.color_text)
    render_text(img, '账号创建时间', (310, 245), font_medium, 32, user.pr.color_text)
    render_text(img, '最后战斗时间', (931, 245), font_medium, 32, user.pr.color_text)
    render_text(img, user.created_at, (310, 284), font_medium, 32, user.pr.color_text)
    render_text(img, user.last_battle_time, (931, 284), font_medium, 32, user.pr.color_text)

    render_text(img, f'{user.pr.pr_text} {user.pr.pr_number}', (621, 410), font_medium, 32, user.pr.color_text)

    render_text(img, user.display_battles, (270, 776), font_medium, 32, user.pr.color_text)
    render_text(img, user.display_xp, (270, 1026), font_medium, 32, user.pr.color_text)

    render_text(img, user.display_winrate, (621, 776), font_medium, 32, user.pr.color_text)
    render_text(img, user.display_kd, (621, 1026), font_medium, 32, user.pr.color_text)

    render_text(img, f'{user.display_damage}', (970, 776), font_medium, 32, user.pr.color_text)
    render_text(img, f'{user.display_accu_rate}', (970, 1026), font_medium, 32, user.pr.color_text)

    render_text(img, f'{user.max_damage_dealt}', (215, 1443), font_medium, 32, user.pr.color_text)
    render_text(img, f'{user.max_planes_killed}', (215, 1666), font_medium, 32, user.pr.color_text)

    render_text(img, f'{user.max_xp}', (621, 1443), font_medium, 32, user.pr.color_text)
    render_text(img, f'{user.max_total_agro}', (621, 1666), font_medium, 32, user.pr.color_text)

    render_text(img, f'{user.max_frags}', (1025, 1443), font_medium, 32, user.pr.color_text)
    render_text(img, f'{user.max_ships_spotted}', (1025, 1666), font_medium, 32, user.pr.color_text)

    # render_text(img, f'{user.max_ships_spotted}', (1025, 1810), font_medium, 32, user.pr.color_text)
    _, buffer = cv.imencode('.jpeg', img)
    bytes_io = buffer.tobytes()
    return bytes_io


async def wows_ship(user: User, ship_id: str):
    main_data_img = cv.imread('components/main_data.png')
    max_data_img = cv.imread('components/max_main.png')
    pr_bar_img = cv.imread('components/pr_bar.png') 
    ship = user.ship_dic.get(ship_id, None)
    if ship is None:
        raise('没有该船只')
    color_bg = ship.pr.color_background[::-1]
    color_pr = ship.pr.pr_color[::-1]
    pr_bar_img[:,:,0][pr_bar_img[:,:,0] == 222] = color_pr[0]
    pr_bar_img[:,:,1][pr_bar_img[:,:,1] == 222] = color_pr[1]
    pr_bar_img[:,:,2][pr_bar_img[:,:,2] == 222] = color_pr[2]

    main_data_img[:,:,0][main_data_img[:,:,0] == 222] = color_bg[0]
    main_data_img[:,:,1][main_data_img[:,:,1] == 222] = color_bg[1]
    main_data_img[:,:,2][main_data_img[:,:,2] == 222] = color_bg[2]

    max_data_img[:,:,0][max_data_img[:,:,0] == 222] = color_bg[0]
    max_data_img[:,:,1][max_data_img[:,:,1] == 222] = color_bg[1]
    max_data_img[:,:,2][max_data_img[:,:,2] == 222] = color_bg[2]

    font_medium = 'src/font/SourceHanSans-Medium.otf'
    font_heavy = 'src/font/SourceHanSans-Heavy.otf'
    font_medium = ft.Face(font_medium)
    font_heavy = ft.Face(font_heavy)

    img = np.full((1900, 1242, 3), 255, dtype=np.uint8)
    img[336:336 + 120, :] = pr_bar_img
    img[483:483 + 650, :] = main_data_img
    img[1160:1160 + 650, :] = max_data_img
    render_text(img, user.clan_tag, (621, 66), font_heavy, 48, user.pr.color_text)
    render_text(img, user.nick_name, (621, 152), font_medium, 48, user.pr.color_text)


    render_text(img, ship.ship_name, (621, 265), font_medium, 48, ship.pr.color_text)

    render_text(img, f'{ship.pr.pr_text} {ship.pr.pr_number}', (621, 410), font_medium, 32, ship.pr.color_text)

    render_text(img, ship.display_battles, (270, 776), font_medium, 32, ship.pr.color_text)
    render_text(img, ship.display_xp, (270, 1026), font_medium, 32, ship.pr.color_text)

    render_text(img, ship.display_winrate, (621, 776), font_medium, 32, ship.pr.color_text)
    render_text(img, ship.display_kd, (621, 1026), font_medium, 32, ship.pr.color_text)

    render_text(img, f'{ship.display_damage}', (970, 776), font_medium, 32, ship.pr.color_text)
    render_text(img, f'{ship.display_accu_rate}', (970, 1026), font_medium, 32, ship.pr.color_text)

    render_text(img, f'{ship.max_damage_dealt}', (215, 1443), font_medium, 32, ship.pr.color_text)
    render_text(img, f'{ship.max_planes_killed}', (215, 1666), font_medium, 32, ship.pr.color_text)

    render_text(img, f'{ship.max_xp}', (621, 1443), font_medium, 32, ship.pr.color_text)
    render_text(img, f'{ship.max_total_agro}', (621, 1666), font_medium, 32, ship.pr.color_text)

    render_text(img, f'{ship.max_frags}', (1025, 1443), font_medium, 32, ship.pr.color_text)
    render_text(img, f'{ship.max_ships_spotted}', (1025, 1666), font_medium, 32, user.pr.color_text)
    
    _, buffer = cv.imencode('.jpeg', img)
    bytes_io = buffer.tobytes()
    return bytes_io