import json
import random

import aiofiles
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, MatchResult, WildcardMatch
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import Waiter, InterruptControl
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from modules.wows import APIs
from modules.wows import dataBase

channel = Channel.current()
saya = Saya.current()
interrupt = InterruptControl(saya.broadcast)


async def fun_get_me(sender_id: int):
    """
    找找 me 是谁
    :param sender_id: 发送者的 QQ 号
    :return:
    """
    dic_users = await dataBase.read_user_data()
    if str(sender_id) in dic_users.keys():
        return dic_users[str(sender_id)]
    else:
        return None


async def fun_wait_me(app: Ariadne, group: Group, member: Member):
    @Waiter.create_using_function([GroupMessage])
    async def InterruptWaiter(g: Group, m: Member, msg: MessageChain):
        if group.id == g.id and member.id == m.id:
            return msg

    sender_data = await fun_get_me(member.id)
    if sender_data is None:
        await app.send_group_message(group, MessageChain('找不到绑定数据'))
        return -1, "", "", ""
    else:
        if len(sender_data) == 1:
            account_id = sender_data[0]['account_id']
            server = sender_data[0]['server']
            clan_tag = sender_data[0]['clan_tag']
            return 1, account_id, server, clan_tag, sender_data[0]['nickName']
        elif len(sender_data) > 1:
            ask_message = '请选择你想查询的账号：'
            servers = ['亚服', '毛服', '欧服', '美服']
            num = 0
            for account in sender_data:
                nickName = account['nickName']
                server_code = account['server']
                server = servers[server_code]
                ask_message += '\n{}: {} {}'.format(num, nickName, server)
                num += 1
            await app.send_group_message(group, MessageChain(ask_message))
            try:
                res_msg = await interrupt.wait(InterruptWaiter, timeout=30)
                res = int(res_msg.display)
                if 0 <= res < len(sender_data):
                    account = sender_data[res]
                    account_id = account['account_id']
                    server = account['server']
                    clan_tag = account['clan_tag']
                    return 1, account_id, server, clan_tag, account['nickName']
                else:
                    await app.send_group_message(group, MessageChain('推荐好好说话'))
                    return 0, "", "", ""
            except Exception:
                await app.send_group_message(group, MessageChain('不说就算了/说了不对的'))
                return 0, "", "", ""
    return


async def read_ship_json():
    async with aiofiles.open('src/wows_data/wows_ship_list.json', 'r') as f:
        js = await f.read()
        json_dic = json.loads(js)
        return json_dic


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("随机开啥船"),
         WildcardMatch(optional=True) @ "para"]
    )]
))
async def wows(app: Ariadne, group: Group, para: MatchResult, member: Member):
    _cmd = (para.result.display.strip() if para.matched else '').split()
    _len = len(_cmd)
    session = Ariadne.service.client_session
    _shipList = await read_ship_json()
    match _len:
        case 0:
            stat_code, account_id, server, clan_tag, nickName = await fun_wait_me(app, group, member)
            match stat_code:
                case -1:
                    ship_id = random.sample(_shipList.keys(), 1)[0]
                    ship_name = _shipList[str(ship_id)]['name']
                    await app.send_group_message(group, MessageChain('你可以尝试一下{}'.format(ship_name)))
                case 0:
                    pass
                case 1:
                    res = await APIs.api_get_player_ship_data(session, account_id, server)
                    ships = res[account_id]
                    ship = random.choice(ships)
                    ship_id = ship['ship_id']
                    ship_name = _shipList[str(ship_id)]['name']
                    await app.send_group_message(group, MessageChain('你可以尝试一下{}'.format(ship_name)))
        case 1:
            try:
                ship_tier = int(_cmd[0])
                stat_code, account_id, server, clan_tag, nickName = await fun_wait_me(app, group, member)
                match stat_code:
                    case -1:
                        ship_within_tier = {}
                        for ship_id_tmp, ship_tmp in _shipList.items():
                            if ship_tmp['tier'] == ship_tier:
                                ship_within_tier[ship_id_tmp] = ship_tmp
                        ship_id = random.sample(ship_within_tier.keys(), 1)[0]
                        ship_name = _shipList[str(ship_id)]['name']
                        await app.send_group_message(group, MessageChain('你可以尝试一下{}'.format(ship_name)))
                    case 0:
                        pass
                    case 1:
                        res = await APIs.api_get_player_ship_data(session, account_id, server)
                        ships = res[account_id]
                        ship_within_tier = {}
                        for ship_tmp in ships:
                            try:
                                ship_id_tmp = ship_tmp['ship_id']
                                if _shipList[str(ship_id_tmp)]['tier'] == ship_tier:
                                    ship_within_tier[str(ship_id_tmp)] = _shipList[str(ship_id_tmp)]
                            except Exception:
                                pass
                        ship_id = random.sample(ship_within_tier.keys(), 1)[0]
                        ship_name = _shipList[str(ship_id)]['name']
                        await app.send_group_message(group, MessageChain('你可以尝试一下{}'.format(ship_name)))
            except Exception as e:
                raise e
                await app.send_group_message(group, MessageChain('转换异常,参数可能不是数字?'))
        case _:
            await app.send_group_message(group, MessageChain('参数太多了'))
