# -*- coding: UTF-8 -*-
"""
@Project ：Bot_rain
@File    ：autoUpdate.py
@Author  ：INTMAX
@Date    ：2022-06-03 7:47 p.m.
"""
from graia.ariadne import Ariadne
from graia.saya import Saya, Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from modules.wows.dataBase import update

saya = Saya.current()
channel = Channel.current()


@channel.use(SchedulerSchema(timers.crontabify("30 2 * * * 30")))
async def wows_auto_update(app: Ariadne):
    update()
