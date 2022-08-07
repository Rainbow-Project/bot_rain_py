import asyncio
from io import BytesIO
import time
from modules.wows import APIs as API
import aiohttp
import line_profiler
from PIL import Image as IMG
from PIL import ImageFont
import cv2 as cv
import modules.wows.dataBase as dataBase


async def main():
    img_avg = IMG.open('wows_pic/wows_id_avg.jpg')
    img_below_avg = IMG.open('wows_pic/wows_id_below_avg.jpg')
    img_god = IMG.open('wows_pic/wows_id_god.jpg')
    img_good = IMG.open('wows_pic/wows_id_good.jpg')
    img_work_hard = IMG.open('wows_pic/wows_id_need_work_hard.jpg')
    img_unknown = IMG.open('wows_pic/wows_id_unknown.jpg')
    img_very_good = IMG.open('wows_pic/wows_id_very_good.jpg')
    img_avg_cv = cv.imread('wows_pic/wows_id_avg.jpg')
    img_below_avg_cv = cv.imread('wows_pic/wows_id_below_avg.jpg')
    img_god_cv = cv.imread('wows_pic/wows_id_god.jpg')
    img_good_cv = cv.imread('wows_pic/wows_id_good.jpg')
    img_work_hard_cv = cv.imread('wows_pic/wows_id_need_work_hard.jpg')
    img_unknown_cv = cv.imread('wows_pic/wows_id_unknown.jpg')
    img_very_good_cv = cv.imread('wows_pic/wows_id_very_good.jpg')
    wows_pic = {
        'draw_avg': [img_avg, img_avg_cv],
        'draw_below_avg': [img_below_avg, img_below_avg_cv],
        'draw_god': [img_god, img_god_cv],
        'draw_good': [img_good, img_good_cv],
        'draw_work_hard': [img_work_hard, img_work_hard_cv],
        'draw_unknown': [img_unknown, img_unknown_cv],
        'draw_very_good': [img_very_good, img_very_good_cv],
    }
    setFont = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 50)
    setFont_big = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 70)
    Font = {
        'setFont': setFont,
        'setFont_big': setFont_big,
    }
    async with aiohttp.ClientSession() as session:
        dic = await dataBase.read_recent_data('2022397176', 0)
        dic
        dic
    return


async def data():
    await dataBase.update_user_past_data()


if __name__ == '__main__':
    """profile = line_profiler.LineProfiler(main)
    profile.enable()"""
    asyncio.run(data())
    """profile.disable()
    profile.print_stats()"""
