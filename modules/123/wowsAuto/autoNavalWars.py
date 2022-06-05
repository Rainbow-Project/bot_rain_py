# -*- coding: UTF-8 -*-
"""
@Project ：Bot_rain
@File    ：autoNavalWars.py
@Author  ：INTMAX
@Date    ：2022-06-04 1:48 a.m. 
"""
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import *
from graia.saya import Saya, Channel
from graia.scheduler import timers
from graia.scheduler.saya.schema import SchedulerSchema
from datetime import date

saya = Saya.current()
channel = Channel.current()


@channel.use(SchedulerSchema(timers.crontabify("0 14 * * * 0")))
async def NavalWars(app: Ariadne):
    today = date.today()
    msg = MessageChain.create(
        f"自动提醒：请记得打开海军大战")
    if today.isoweekday() in [5, 6, 7]:
        await app.sendGroupMessage(429463785,msg)
