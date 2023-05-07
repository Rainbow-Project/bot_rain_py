# -*- coding: UTF-8 -*-
"""
@Project ：Bot_rain
@File    ：iwarship.py
@Author  ：INTMAX
@Date    ：2022-06-23 8:47 a.m.
"""
import asyncio
import copy
import os
from datetime import time

import requests
from bs4 import BeautifulSoup
from graia.ariadne import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Saya, Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from html2image import Html2Image
from graia.ariadne.message.element import *
import time as tm
from PIL import Image as IMG
import datetime

saya = Saya.current()
channel = Channel.current()
groups = {
    124500140,
    429463785,
    755167601,
}


def pic_pre_process(path: str):
    im = IMG.open(path)
    x, y = im.size
    im.convert("RGB")
    p = IMG.new("RGB", im.size, (255, 255, 255))
    p.paste(im, (0, 0, x, y), im)
    p.save(out := BytesIO(), format="JPEG")
    return out


@channel.use(SchedulerSchema(timers.crontabify("30 09 * * * 00")))
async def iWarShipUpdate(app: Ariadne):
    print("START_IARSHIP_CHECK")
    hti = Html2Image()
    hti.output_path = "/home/BOT/bot_ker/bot_rain_py/"
    headers = {}
    response = requests.get("https://iwarship.net/sitemap.xml", headers=headers)

    data = response.text
    soup = BeautifulSoup(data, "xml")
    urlTags = soup.find_all("url")
    yesterday = datetime.date.today() + datetime.timedelta(-1)
    d1 = yesterday.strftime("%Y-%m-%d")
    for sitemap in urlTags:
        loc = sitemap.findNext("loc").text
        lastmod = sitemap.findNext("lastmod").text
        if "devblog" in loc and d1 in lastmod:
            await asyncio.sleep(15)
            response_lp = requests.get(loc, headers=headers)
            data_lp = response_lp.text
            soup_lp = BeautifulSoup(data_lp, "lxml")
            soup_new = BeautifulSoup("")
            all_hr = soup_lp.select("hr")
            cont = 0
            for hr in all_hr[:-1]:
                print(f"{hr!r}")
                for sibling in hr.next_siblings:
                    sibling_copy = copy.copy(sibling)
                    if sibling in all_hr:
                        break
                    cont += 1
                    soup_new.append(sibling_copy)

            uuid = hash(tm.time())
            paths = hti.screenshot(
                html_str=soup_new.prettify(),
                save_as=str(uuid) + ".png",
                size=(1920, 40 * cont),
            )
            print(paths)
            out = pic_pre_process(str(uuid) + ".png")
            os.remove(str(uuid) + ".png")
            for group in groups:
                await app.send_group_message(
                    group, MessageChain(Image(data_bytes=out.getvalue()))
                )
