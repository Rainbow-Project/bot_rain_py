# -*- coding: UTF-8 -*-
"""
@Project ：Bot_rain
@File    ：wows.py
@Author  ：INTMAX
@Date    ：2022-06-03 7:48 p.m.
@Refactor1At ：2022-07-17 2:46 p.m
"""
import asyncio

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import *
from graia.ariadne.message.parser.twilight import (
    FullMatch,
    MatchResult,
    Twilight,
    WildcardMatch,
)
from graia.ariadne.model import Group
from graia.broadcast.interrupt import Waiter, InterruptControl
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
import difflib
from wows import dataBase
from wows import APIs

saya = Saya.current()
channel = Channel.current()
interrupt = InterruptControl(saya.broadcast)
wows_images = saya.access("wows_images")
Fonts = saya.access("Font")


async def fun_get_me(sender_id: int) -> Any | None:
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
        await app.send_group_message(group, MessageChain("找不到绑定数据"))
        return 0, "", "", ""
    else:
        if len(sender_data) == 1:
            account_id = sender_data[0]["account_id"]
            server = sender_data[0]["server"]
            clan_tag = sender_data[0]["clan_tag"]
            return 1, account_id, server, clan_tag, sender_data[0]["nickName"]
        elif len(sender_data) > 1:
            ask_message = "请选择你想查询的账号："
            servers = ["亚服", "毛服", "欧服", "美服"]
            num = 0
            for account in sender_data:
                nickName = account["nickName"]
                server_code = account["server"]
                server = servers[server_code]
                ask_message += "\n{}: {} {}".format(num, nickName, server)
                num += 1
            await app.send_group_message(group, MessageChain(ask_message))
            try:
                res_msg = await interrupt.wait(InterruptWaiter, timeout=30)
                res = int(res_msg.display)
                if 0 <= res < len(sender_data):
                    account = sender_data[res]
                    account_id = account["account_id"]
                    server = account["server"]
                    clan_tag = account["clan_tag"]
                    return 1, account_id, server, clan_tag, account["nickName"]
                else:
                    await app.send_group_message(group, MessageChain("推荐好好说话"))
                    return 0, "", "", ""
            except Exception:
                await app.send_group_message(group, MessageChain("不说就算了/说了不对的"))
                return 0, "", "", ""
    return


async def fun_wait_target(app: Ariadne, group: Group, member: Member, target: int):
    @Waiter.create_using_function([GroupMessage])
    async def InterruptWaiter(g: Group, m: Member, msg: MessageChain):
        if group.id == g.id and member.id == m.id:
            return msg

    sender_data = await fun_get_me(target)
    if sender_data is None:
        await app.send_group_message(group, MessageChain("找不到绑定数据"))
        return 0, "", "", ""
    else:
        if len(sender_data) == 1:
            account_id = sender_data[0]["account_id"]
            server = sender_data[0]["server"]
            clan_tag = sender_data[0]["clan_tag"]
            return 1, account_id, server, clan_tag, sender_data[0]["nickName"]
        elif len(sender_data) > 1:
            ask_message = "请选择你想查询的账号："
            servers = ["亚服", "毛服", "欧服", "美服"]
            num = 0
            for account in sender_data:
                nickName = account["nickName"]
                server_code = account["server"]
                server = servers[server_code]
                ask_message += "\n{}: {} {}".format(num, nickName, server)
                num += 1
            await app.send_group_message(group, MessageChain(ask_message))
            try:
                res_msg = await interrupt.wait(InterruptWaiter, timeout=30)
                res = int(res_msg.display)
                if 0 <= res < len(sender_data):
                    account = sender_data[res]
                    account_id = account["account_id"]
                    server = account["server"]
                    clan_tag = account["clan_tag"]
                    return 1, account_id, server, clan_tag, account["nickName"]
                else:
                    await app.send_group_message(group, MessageChain("无法解析语句"))
                    return 0, "", "", ""
            except Exception:
                await app.send_group_message(group, MessageChain("不说就算了/说了不对的"))
                return 0, "", "", ""
    return


async def wait_ship_id(app: Ariadne, group: Group, member: Member, shipName: str):
    @Waiter.create_using_function([GroupMessage])
    async def InterruptWaiter(g: Group, m: Member, msg: MessageChain):
        if group.id == g.id and member.id == m.id:
            return msg

    data_name = await dataBase.read_ship_dic()
    if shipName in data_name.keys():
        return 0, data_name[shipName], shipName
    else:
        fuzzy_list = difflib.get_close_matches(
            shipName, data_name.keys(), 5, cutoff=0.2
        )
        if len(fuzzy_list) == 0:
            await app.send_group_message(group, MessageChain("模糊查询也找不到"))
            return 1, "-1", "-1"
        else:
            ask_msg = "猜你想找:"
            count = 1
            for fuzzy in fuzzy_list:
                ask_msg += "\n" + str(count) + ": " + fuzzy
                count += 1
            await app.send_group_message(group, MessageChain(ask_msg))
            try:
                res_msg = await interrupt.wait(InterruptWaiter, timeout=30)
                res = int(res_msg.display)
                return 0, data_name[fuzzy_list[res - 1]], fuzzy_list[res - 1]
            except Exception:
                await app.send_group_message(group, MessageChain("不说就算了/说了不对的"))
                return 1, "-1", "-1"


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([FullMatch("wows"), WildcardMatch(optional=True) @ "para"])
        ],
    )
)
async def wows(app: Ariadne, group: Group, para: MatchResult, member: Member):
    try:
        _cmd = (para.result.display.strip() if para.matched else "").split()
        _len = len(_cmd)
        serverList = ["asia", "na", "ru", "eu"]
        session = Ariadne.service.client_session
        match _len:
            case 1:
                """当指令长度为1时只有wows me 和 wows exboom wows help 3种情况"""
                match _cmd[0]:
                    case "me":
                        """
                        wows me
                        直接去找me 并且判断是否含有服务器和UID信息
                        """
                        (
                            stat_code,
                            account_id,
                            server,
                            clan_tag,
                            nickName,
                        ) = await fun_wait_me(app, group, member)
                        if stat_code == 1:
                            try:
                                img = await APIs.fun_wows_me(
                                    session,
                                    account_id,
                                    server,
                                    clan_tag,
                                    wows_images,
                                    Fonts,
                                )
                                await app.send_group_message(
                                    group, MessageChain(Image(data_bytes=img))
                                )
                            except (APIs.APIError, APIs.NetError, APIs.Notfound) as e:
                                await app.send_group_message(
                                    group, MessageChain(e.args)
                                )
                    case "help":
                        """
                        看看帮助
                        """
                        try:
                            await app.send_group_message(
                                group,
                                MessageChain(
                                    "发太长了会封控,看看链接吧\n"
                                    + "https://rainbow-project.github.io/pages/3c92d6/"
                                ),
                            )
                        except Exception as e:
                            await app.send_group_message(group, MessageChain(e.args))
                    case _:
                        """
                        其他的情况就是 wows nickName 了
                        """
                        try:
                            img = await APIs.fun_wows_nickName(
                                session, _cmd[0], 0, wows_images, Fonts
                            )
                            await app.send_group_message(
                                group, MessageChain(Image(data_bytes=img))
                            )
                        except (APIs.APIError, APIs.NetError, APIs.Notfound) as e:
                            await app.send_group_message(group, MessageChain(e.args))
            case 2:
                """
                当指令长度为2时
                会出现wows me/@ recent 和 wows asia exboom 和新的 wows me/@ recents 
                wows me rank
                wows exboom rank
                """
                match _cmd[1]:
                    case "recent":
                        if _cmd[0] == "me":
                            (
                                stat_code,
                                account_id,
                                server,
                                clan_tag,
                                nickName,
                            ) = await fun_wait_me(app, group, member)
                            if stat_code == 1:
                                try:
                                    img = await APIs.wows_get_recent(
                                        session,
                                        account_id,
                                        server,
                                        clan_tag,
                                        None,
                                        wows_images,
                                        Fonts,
                                    )
                                    await app.send_group_message(
                                        group, MessageChain(Image(data_bytes=img))
                                    )
                                except (
                                    APIs.APIError,
                                    APIs.NetError,
                                    APIs.Notfound,
                                ) as e:
                                    await app.send_group_message(
                                        group, MessageChain(e.args)
                                    )
                        else:
                            target = _cmd[0][1:]
                            (
                                stat_code,
                                account_id,
                                server,
                                clan_tag,
                                nickName,
                            ) = await fun_wait_target(app, group, member, int(target))
                            if stat_code == 1:
                                try:
                                    img = await APIs.wows_get_recent(
                                        session,
                                        account_id,
                                        server,
                                        clan_tag,
                                        None,
                                        wows_images,
                                        Fonts,
                                    )
                                    await app.send_group_message(
                                        group, MessageChain(Image(data_bytes=img))
                                    )
                                except (
                                    APIs.APIError,
                                    APIs.NetError,
                                    APIs.Notfound,
                                    Exception,
                                ) as e:
                                    await app.send_group_message(
                                        group, MessageChain(e.args)
                                    )
                    case "rank":
                        # await app.send_group_message(
                        #     group, MessageChain("该功能暂时无法使用， 等待修复")
                        # )
                        if _cmd[0] == 'me':
                            stat_code, account_id, server, clan_tag, nickName = await fun_wait_me(app, group, member)
                            if stat_code == 1:
                                try:
                                    img = await APIs.wows_rank_me(session, nickName, account_id, server, clan_tag, wows_images, Fonts)
                                    await app.send_group_message(group, MessageChain(Image(data_bytes=img)))
                                except (APIs.APIError, APIs.NetError, APIs.Notfound) as e:
                                    await app.send_group_message(group, MessageChain(e.args))
                        else:
                            try:
                                img = await APIs.wows_rank_account_id(session, _cmd[0], 0, wows_images, Fonts)
                                await app.send_group_message(group, MessageChain(Image(data_bytes=img)))
                            except (APIs.APIError, APIs.NetError, APIs.Notfound) as e:
                                await app.send_group_message(group, MessageChain(e.args))
                    case "remove":
                        if _cmd[0] == "me":

                            @Waiter.create_using_function([GroupMessage])
                            async def InterruptWaiter(
                                g: Group, m: Member, msg: MessageChain
                            ):
                                if group.id == g.id and member.id == m.id:
                                    return msg

                            msg = """
    警告：本操作不可撤销，过去服务器保存的数据可能会丢失
    账号过去的战绩信息将在没有人绑定该账号时删除
    回复删除来确认
                            """
                            (
                                stat_code,
                                account_id,
                                server,
                                clan_tag,
                                nickName,
                            ) = await fun_wait_me(app, group, member)
                            if stat_code == 1:
                                await app.send_group_message(group, MessageChain(msg))
                                try:
                                    res_msg = await interrupt.wait(
                                        InterruptWaiter, timeout=15
                                    )
                                    if str(res_msg) == "删除":
                                        try:
                                            await app.send_group_message(
                                                group, MessageChain("正在尝试解析依赖")
                                            )
                                            await dataBase.remove_user(
                                                member.id, account_id
                                            )
                                            await app.send_group_message(
                                                group, MessageChain("移除完成")
                                            )
                                        except Exception as e:
                                            await app.send_group_message(
                                                group, MessageChain("由于错误无法移除数据")
                                            )
                                            raise e
                                    else:
                                        await app.send_group_message(
                                            group, MessageChain("放弃移除数据")
                                        )
                                except Exception as e:
                                    await app.send_group_message(
                                        group, MessageChain("由于超时放弃移除数据")
                                    )
                                    raise e
                    case 'recents':
                        if _cmd[0] == "me":
                            (
                                stat_code,
                                account_id,
                                server,
                                clan_tag,
                                nickName,
                            ) = await fun_wait_me(app, group, member)
                            if stat_code == 1:
                                try:
                                    img = await APIs.wows_get_recents(
                                        session,
                                        account_id,
                                        server,
                                        clan_tag,
                                        None,
                                        wows_images,
                                        Fonts,
                                    )
                                    await app.send_group_message(
                                        group, MessageChain(Image(data_bytes=img))
                                    )
                                except (
                                    APIs.APIError,
                                    APIs.NetError,
                                    APIs.Notfound,
                                ) as e:
                                    await app.send_group_message(
                                        group, MessageChain(e.args)
                                    )
                        else:
                            target = _cmd[0][1:]
                            (
                                stat_code,
                                account_id,
                                server,
                                clan_tag,
                                nickName,
                            ) = await fun_wait_target(app, group, member, int(target))
                            if stat_code == 1:
                                try:
                                    img = await APIs.wows_get_recents(
                                        session,
                                        account_id,
                                        server,
                                        clan_tag,
                                        None,
                                        wows_images,
                                        Fonts,
                                    )
                                    await app.send_group_message(
                                        group, MessageChain(Image(data_bytes=img))
                                    )
                                except (
                                    APIs.APIError,
                                    APIs.NetError,
                                    APIs.Notfound,
                                ) as e:
                                    await app.send_group_message(
                                        group, MessageChain(e.args)
                                    )
                    case _:
                        if _cmd[0].lower() in serverList:
                            match _cmd[0].lower():
                                case "asia":
                                    server = 0
                                case "ru":
                                    server = 1
                                case "eu":
                                    server = 2
                                case "na":
                                    server = 3
                                case _:
                                    server = 0
                            try:
                                img = await APIs.fun_wows_nickName(
                                    session, _cmd[1], server, wows_images, Fonts
                                )
                                await app.send_group_message(
                                    group, MessageChain(Image(data_bytes=img))
                                )
                            except (APIs.APIError, APIs.NetError, APIs.Notfound) as e:
                                await app.send_group_message(
                                    group, MessageChain(e.args)
                                )
                        else:
                            await app.send_group_message(
                                group, MessageChain("错误: 意料外的指令")
                            )
            case 3:
                """
                当指令为3时可能出现
                wows me ship 大胆
                wows exboom ship 大胆
                wows set asia exboom
                wows asia exboom rank
                wows me recent n
                wows target recent n
                """
                if _cmd[0].lower() == "set":
                    """
                    wows set server nickName
                    """
                    if _cmd[1].lower() in serverList:
                        match _cmd[1].lower():
                            case "asia":
                                server = 0
                            case "ru":
                                server = 1
                            case "eu":
                                server = 2
                            case "na":
                                server = 3
                            case _:
                                server = 0
                        try:
                            api_res = await APIs.api_get_account_id(
                                session, _cmd[2], server
                            )
                            account_id = str(api_res[0]["account_id"])
                            try:
                                clan_res = await APIs.api_get_clan_id(
                                    session, account_id, server
                                )
                                clan_id = str(clan_res[account_id]["clan_id"])
                                clan_details = await APIs.api_get_clan_details(
                                    session, clan_id, server
                                )
                                clan_tag = clan_details[clan_id]["tag"]
                                nickName = clan_res[str(account_id)]["account_name"]
                            except Exception:
                                clan_tag = "NO_CLAN"
                                nickName = "Waiting_Refactor"
                            user_add = {
                                "account_id": account_id,
                                "server": server,
                                "clan_tag": clan_tag,
                                "nickName": nickName,
                            }
                            stat_add = await dataBase.add_user(member.id, user_add)
                            match stat_add:
                                case 0:
                                    await app.send_group_message(
                                        group,
                                        MessageChain(
                                            "已将 {} 与QQ号 {} 绑定".format(
                                                nickName, member.id
                                            )
                                        ),
                                    )
                                case 1:
                                    await app.send_group_message(
                                        group, MessageChain("已达最大绑定数量，不过依然可以联系管理者手动加入")
                                    )
                                case 2:
                                    await app.send_group_message(
                                        group, MessageChain("似乎已经添加过了")
                                    )
                        except (APIs.APIError, APIs.NetError, APIs.Notfound) as e:
                            await app.send_group_message(group, MessageChain(e.args))
                elif _cmd[2].lower() == "rank":
                    """
                    wows server nickName rank
                    """
                    match _cmd[0].lower():
                        case 'asia':
                            server = 0
                        case 'ru':
                            server = 1
                        case 'eu':
                            server = 2
                        case 'na':
                            server = 3
                        case _:
                            server = 0
                    nickName = _cmd[1]
                    try:
                        img = await APIs.wows_rank_account_id(session, nickName, server, wows_images, Fonts)
                        await app.send_group_message(group, MessageChain(Image(data_bytes=img)))
                    except (APIs.APIError, APIs.NetError, APIs.Notfound) as e:
                        await app.send_group_message(group, MessageChain(e.args))
                    # await app.send_group_message(group, MessageChain("该功能暂时停用"))
                elif _cmd[1].lower() == "ship":
                    """
                    wows nickName ship shipName
                    wows me ship shipName
                    """
                    match _cmd[0].lower():
                        case "me":
                            (
                                stat_code,
                                account_id,
                                server,
                                clan_tag,
                                nickName,
                            ) = await fun_wait_me(app, group, member)
                            if stat_code == 1:
                                stat_code_ship, ship_id, shipName = await wait_ship_id(
                                    app, group, member, _cmd[-1]
                                )
                                if stat_code_ship == 0:
                                    try:
                                        img = await APIs.wows_get_ship_img_me(
                                            session,
                                            account_id,
                                            server,
                                            ship_id,
                                            shipName,
                                            nickName,
                                            clan_tag,
                                            wows_images,
                                            Fonts,
                                        )
                                        await app.send_group_message(
                                            group, MessageChain(Image(data_bytes=img))
                                        )
                                    except (
                                        APIs.APIError,
                                        APIs.NetError,
                                        APIs.Notfound,
                                    ) as e:
                                        await app.send_group_message(
                                            group, MessageChain(e.args)
                                        )
                        case _:
                            stat_code_ship, ship_id, shipName = await wait_ship_id(
                                app, group, member, _cmd[-1]
                            )
                            if stat_code_ship == 0:
                                try:
                                    img = await APIs.wows_get_ship_nickName(
                                        session,
                                        _cmd[0],
                                        0,
                                        ship_id,
                                        shipName,
                                        wows_images,
                                        Fonts,
                                    )
                                    await app.send_group_message(
                                        group, MessageChain(Image(data_bytes=img))
                                    )
                                except (
                                    APIs.APIError,
                                    APIs.NetError,
                                    APIs.Notfound,
                                ) as e:
                                    await app.send_group_message(
                                        group, MessageChain(e.args)
                                    )
                elif _cmd[1].lower() == "recent":
                    """
                    wows me recent n
                    wows target recent n
                    """
                    if _cmd[0].lower() == "me":
                        try:
                            days = int(_cmd[2])
                            if days > 30:
                                raise Exception(">30")
                        except Exception as e:
                            await app.send_group_message(
                                group, MessageChain("天数在转换时出现错误，它可能不是一个数字,或者它大于30")
                            )
                            raise e
                        (
                            stat_code,
                            account_id,
                            server,
                            clan_tag,
                            nickName,
                        ) = await fun_wait_me(app, group, member)
                        if stat_code == 1:
                            try:
                                img = await APIs.wows_get_recent(
                                    session,
                                    account_id,
                                    server,
                                    clan_tag,
                                    days,
                                    wows_images,
                                    Fonts,
                                )
                                await app.send_group_message(
                                    group, MessageChain(Image(data_bytes=img))
                                )
                            except (APIs.APIError, APIs.NetError, APIs.Notfound) as e:
                                await app.send_group_message(
                                    group, MessageChain(e.args)
                                )
                    else:
                        target = _cmd[0][1:]
                        try:
                            days = int(_cmd[2])
                            if days > 30:
                                raise Exception(">30")
                        except Exception as e:
                            await app.send_group_message(
                                group, MessageChain("天数在转换时出现错误，它可能不是一个数字,或者它大于30")
                            )
                            raise e
                        (
                            stat_code,
                            account_id,
                            server,
                            clan_tag,
                            nickName,
                        ) = await fun_wait_target(app, group, member, int(target))
                        if stat_code == 1:
                            try:
                                img = await APIs.wows_get_recent(
                                    session,
                                    account_id,
                                    server,
                                    clan_tag,
                                    days,
                                    wows_images,
                                    Fonts,
                                )
                                await app.send_group_message(
                                    group, MessageChain(Image(data_bytes=img))
                                )
                            except (APIs.APIError, APIs.NetError, APIs.Notfound) as e:
                                await app.send_group_message(
                                    group, MessageChain(e.args)
                                )
            case 4:
                """
                当指令为4时可能出现
                wows asia exboom ship 大胆
                """
                match _cmd[0].lower():
                    case "asia":
                        server = 0
                    case "ru":
                        server = 1
                    case "eu":
                        server = 2
                    case "na":
                        server = 3
                    case _:
                        server = 0
                if _cmd[0] in serverList:
                    stat_code_ship, ship_id, shipName = await wait_ship_id(
                        app, group, member, _cmd[-1]
                    )
                    if stat_code_ship == 0:
                        try:
                            img = await APIs.wows_get_ship_nickName(
                                session,
                                _cmd[1],
                                server,
                                ship_id,
                                shipName,
                                wows_images,
                                Fonts,
                            )
                            await app.send_group_message(
                                group, MessageChain(Image(data_bytes=img))
                            )
                        except (APIs.APIError, APIs.NetError, APIs.Notfound) as e:
                            await app.send_group_message(group, MessageChain(e.args))
    except Exception as e:
        await app.send_group_message(group, MessageChain(f'出现错误:{e}'))
        print(e.with_traceback())
        raise(e)
    finally:
        pass
