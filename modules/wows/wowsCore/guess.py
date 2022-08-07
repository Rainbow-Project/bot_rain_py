import asyncio
import json
import random

import aiofiles
import aiohttp
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, At, Plain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch
from graia.ariadne.model import Group, Member
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.interrupt import Waiter
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema

from modules.wows.wowsCore.wows import interrupt

channel = Channel.current()
saya = Saya.current()
CD = saya.access('CoolDown')


def check_cool_down():
    async def check_group_cool_down(app: Ariadne, group: Group):
        if group.id in CD:
            await app.send_group_message(group, MessageChain('功能正在重新装填'))
            raise ExecutionStop
        else:
            CD.append(group.id)
            saya.mount('CoolDown', CD)

    return Depend(check_group_cool_down)


async def remove_cool_down(group: Group, saya_get: Saya):
    if group.id in CD:
        CD.remove(group.id)
        saya_get.mount('CoolDown', CD)


async def read_ship_json():
    async with aiofiles.open('src/wows_data/wows_ship_list.json', 'r') as f:
        js = await f.read()
        json_dic = json.loads(js)
        return json_dic


async def read_ship_img(session: aiohttp.ClientSession, img_url: str):
    async with session.get(img_url) as res:
        img = await res.read()
        return img


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("猜个船")]
    )],
    decorators=[check_cool_down()]
))
async def guess_ship(app: Ariadne, group: Group):
    session = Ariadne.service.client_session
    try:
        ship_json = await read_ship_json()
        random_ship_id = random.sample(ship_json.keys(), 1)[0]
        ship_random = ship_json[random_ship_id]
        ship_img = await read_ship_img(session, ship_random['images']['large'])
        ship_name = ship_random['name']
        ship_tier = ship_random['tier']
        match ship_random['nation']:
            case 'japan':
                ship_nation = '日本'
            case 'usa':
                ship_nation = '美国'
            case 'pan_asia':
                ship_nation = '泛亚'
            case 'ussr':
                ship_nation = '苏联'
            case 'europe':
                ship_nation = '欧洲'
            case 'uk':
                ship_nation = '英国'
            case 'germany':
                ship_nation = '德国'
            case 'italy':
                ship_nation = '意大利'
            case 'netherlands':
                ship_nation = '荷兰'
            case 'france':
                ship_nation = '法国'
            case 'commonwealth':
                ship_nation = 'commonwealth：联邦'
            case 'pan_america':
                ship_nation = '泛美'
            case _:
                ship_nation = ship_random['nation']
        match ship_random['type']:
            case 'Cruiser':
                ship_type = '巡洋舰'
            case 'Destroyer':
                ship_type = '驱逐舰'
            case 'Battleship':
                ship_type = '战列舰'
            case 'AirCarrier':
                ship_type = '航空母舰'
            case _:
                ship_type = ship_random['type']

        @Waiter.create_using_function([GroupMessage])
        async def InterruptWaiter(g: Group, msg: MessageChain, member: Member):
            if group.id == g.id and msg.display.upper() == ship_name.upper():
                return member

        await app.send_group_message(group, MessageChain(Image(data_bytes=ship_img)))
        try:
            member_winner = await interrupt.wait(InterruptWaiter, timeout=120)
            await app.send_group_message(group, MessageChain([Plain('恭喜'), At(member_winner.id), Plain('成功的找出了这条船')]))
        except asyncio.TimeoutError:
            await app.send_group_message(group, MessageChain('已经两分钟了(120s)'))
            await app.send_group_message(group, MessageChain('小提示: \n这艘战舰所属的国家为：{}'.format(ship_nation)))
            try:
                member_winner = await interrupt.wait(InterruptWaiter, timeout=120)
                await app.send_group_message(group,
                                             MessageChain([Plain('恭喜'), At(member_winner.id), Plain('成功的找出了这条船')]))
            except asyncio.TimeoutError:
                await app.send_group_message(group, MessageChain('已经四分钟了(120s x 2)'))
                await app.send_group_message(group, MessageChain('小提示: \n这艘战舰是{}级{}'.format(ship_tier, ship_type)))
                try:
                    member_winner = await interrupt.wait(InterruptWaiter, timeout=60)
                    await app.send_group_message(group,
                                                 MessageChain([Plain('恭喜'), At(member_winner.id), Plain('成功的找出了这条船')]))
                except asyncio.TimeoutError:
                    await app.send_group_message(group, MessageChain('时间到，没有猜出结果'))
                    await app.send_group_message(group, MessageChain('这艘战舰的名字是{}'.format(ship_name)))
        await remove_cool_down(group, saya)
    except Exception as e:
        await app.send_group_message(group, MessageChain('出现异常' + str(e.args)))
        await remove_cool_down(group, saya)
