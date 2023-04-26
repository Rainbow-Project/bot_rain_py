import math

class Ship:
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

    pr = None

    display_battles = None
    display_winrate = None
    display_damage = None
    display_xp = None
    display_kd = None
    display_accu_rate = None

    def __init__(self, ship_dict: dict, ship_list:dict, expected_data) -> None:
        # 原始数据
        self.org_json = ship_dict
        # 基本数据
        self.ship_id = ship_dict['ship_id']
        self.ship_name = ship_list[self.ship_id]['name']
        # 非战斗数据
        self.last_battle_time = ship_dict['last_battle_time']
        self.distance = ship_dict['battles']
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
        self.max_frags = pvp['max_frags']
        self.max_planes_killed = pvp['max_planes_killed']
        self.max_total_agro = pvp['max_total_agro']
        self.max_xp = pvp['max_xp']
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

class User:
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
    def __init__(self, user: dict, ships: dict, server: int, clan_id, clan_tag) -> None:
        self.org_json = user
        
        self.clan_id = clan_id
        self.clan_tag = clan_tag

        self.account_id = user['account_id']
        self.nick_name = user['nickname']
        self.server = server

        # 非战斗数据
        self.last_battle_time = user['last_battle_time']  # 上次战斗
        self.leveling_tier = user['leveling_tier']  # 等级
        self.created_at = user['created_at']  # 账号创建时间
        self.hidden_profile = user['hidden_profile']  # 隐藏战绩
        self.logout_at = user['logout_at']  # 上次退出游戏
        self.distance = user['distance']  # 航行长度

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
        self.max_frags = pvp['max_frags']
        self.max_planes_killed = pvp['max_planes_killed']
        self.max_total_agro = pvp['max_total_agro']
        self.max_xp = pvp['max_xp']

        # 船表
        self.ship_list = []  # 玩家船只列表
        for ship in ships:
            self.ship_list.append(Ship(ship))

        # PR
        self.pr = Pr()  # pr 数值
        self.pr.init_pr_user(self.ship_list)

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

        for ship in ships:
            total_pr += ship.pr.pr_number

        self.pr_number = total_pr / len(ships)

        self.color_init()

    def init_pr_ship(self, ship: Ship, expected_data: dict) -> None:
        ship_id = ship.ship_id

        battles = ship.battles

        exp_damage = expected_data['data'][ship_id]['average_damage_dealt']
        exp_frags = expected_data['data'][ship_id]['average_frags']
        exp_winrate = expected_data['data'][ship_id]['win_rate']

        damage = ship.damage_dealt / ship.battles
        frags = ship.frags / ship.battles
        winrate = ship.wins / ship.battles

        r_dmg = damage / exp_damage
        r_frags = frags / exp_frags
        r_winrate = winrate / exp_winrate


        w1 = 1/1+math.e^(-0.7 * (battles - 3))
        w2 = 1/1+math.e^(-20 * (winrate - 0.50))

        w_wins = (1000 * w1) - ((1000 * w1 * 0.4) * w2)
        w_dmg = (1000 * (1 - w1)) + ((1000 * w1 * 0.4) * w2)
        w_frags = 150

        # n_dmg = max(0, (r_dmg - 0.4) / (1 - 0.4))
        # n_frags = max(0, (r_frags - 0.1) / (1 - 0.1))
        # n_wins = max(0, (r_winrate - 0.7) / (1 - 0.7))

        self.pr_number = round((w_dmg * r_dmg) + (w_frags * r_frags) + (w_wins * r_winrate))

        self.color_init()

    def color_init(self) -> None:
        if self.pr_number <= 750:
            self.pr_color = (255, 0, 0)
            self.color_background = (255, 166, 166)
            self.color_text = (255, 255, 255)
            self.pr_text = '还需努力'
        elif self.pr_number <= 1100:
            self.pr_color = (255, 140, 0)
            self.color_background = (255, 189, 179)
            self.color_text = (0, 0, 0)
            self.pr_text = '低于平均'
        elif self.pr_number <= 1350:
            self.pr_color = (255, 165, 0)
            self.color_background = (255, 196, 175)
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
        
    