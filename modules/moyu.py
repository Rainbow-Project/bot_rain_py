import asyncio

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import *
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.scheduler import timers
from graia.scheduler.saya.schema import SchedulerSchema

from typing import Optional
from datetime import date, timedelta
from itertools import takewhile, dropwhile

saya = Saya.current()
channel = Channel.current()

groups = (964132418, 429463785, 696443646, 565540208)

# 来自《国务院办公厅关于2023年部分节假日安排的通知》
holiday = {
    "元旦": [date(2022, 12, 31), date(2023, 1, 2)],
    "春节": [date(2023, 1, 21), date(2023, 1, 27)],
    "清明节": [date(2023, 4, 5), date(2023, 4, 5)],
    "劳动节": [date(2023, 4, 29), date(2023, 5, 3)],
    "端午节": [date(2023, 6, 22), date(2023, 6, 24)],
    "中秋节、国庆节": [date(2023, 9, 29), date(2023, 10, 6)],
}

# 周末上班
weekend_but_work = {
    # 春节
    date(2023, 1, 28),
    date(2023, 1, 29),
    # 劳动节
    date(2023, 4, 23),
    date(2023, 5, 6),
    # 端午
    date(2023, 6, 25),
    # 中秋节、国庆节
    date(2023, 10, 7),
    date(2023, 10, 8),
}


def next_weekend() -> Optional[date]:
    now = date.today()

    # 现在就是周末
    if now.isoweekday() in [6, 7]:
        return

    weekend = now + timedelta(days=6 - now.isoweekday())

    while True:
        # 是调休，不能算是周末
        if weekend in weekend_but_work:
            w = weekend.isoweekday()
            weekend += timedelta(days=1 if w == 6 else 6)
            continue

        for _, [f, t] in holiday.items():
            # 这是假期，超越了周末
            if f <= weekend <= t:
                if t.isoweekday() in [6, 7]:
                    t = t + timedelta(days=1)
                weekend = t + timedelta(days=6 - t.isoweekday())
                continue
        break

    return weekend


def in_holiday() -> bool:
    now = date.today()
    for _, [f, t] in holiday.items():
        if f <= now <= t:
            return True
    return False


@channel.use(SchedulerSchema(timers.crontabify("0 8 * * * 0")))
async def moyu(app: Ariadne):
    today = date.today()
    msg = MessageChain(f"早上好，摸鱼人！今天是{today.strftime('%Y年%m月%d日')}\n")

    # 看看今天是不是周末
    if today.isoweekday() in [6, 7]:
        msg += "\n今天是周末，"
        if today in weekend_but_work:
            msg += "但很可惜，是要上班desu"
        elif in_holiday():
            msg += "而且还是放假期间哦"
        else:
            msg += "好好休息一下吧"
    else:
        if in_holiday():
            msg += "现在是假期哦~"

    end_holiday = list(dropwhile(lambda x: x[1][1] < today, holiday.items()))
    if weekend := next_weekend():
        i = len(list(takewhile(lambda x: x[1][1] < today, end_holiday)))
        end_holiday.insert(i, ("周末", [weekend]))

    msg += "\n\n"

    for n, (day, f) in enumerate(end_holiday, 1):
        if n > 3:
            break

        f = f[0]
        msg += f"距离{day}还有{(f - today).days}天\n"
    for i in groups:
        await app.send_group_message(i, msg)
        await asyncio.sleep(2)
