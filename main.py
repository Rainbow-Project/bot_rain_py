import pkgutil
from PIL import Image as IMG
from PIL import ImageFont
from graia.ariadne.app import Ariadne
from graia.saya import Saya
import cv2 as cv
import numpy as np
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.scheduler import GraiaScheduler
from graia.scheduler.saya import GraiaSchedulerBehaviour

app = Ariadne(
    connection=config(
        1829414471,  # 你的机器人的 qq 号
        "HELLO",  # 填入你的 mirai-api-http 配置中的 verifyKey
        # 以下两行（不含注释）里的 host 参数的地址
        # 是你的 mirai-api-http 地址中的地址与端口
        # 他们默认为 "http://localhost:8080"
        # 如果你 mirai-api-http 的地址与端口也是 localhost:8080
        # 就可以删掉这两行，否则需要修改为 mirai-api-http 的地址与端口
        HttpClientConfig(host="http://localhost:9333"),
        WebsocketClientConfig(host="http://localhost:9333"),
    ),
)
img_avg = IMG.open('wows_pic/wows_id_avg.jpg')
img_below_avg = IMG.open('wows_pic/wows_id_below_avg.jpg')
img_god = IMG.open('wows_pic/wows_id_god.jpg')
img_good = IMG.open('wows_pic/wows_id_good.jpg')
img_work_hard = IMG.open('wows_pic/wows_id_need_work_hard.jpg')
img_unknown = IMG.open('wows_pic/wows_id_unknown.jpg')
img_very_good = IMG.open('wows_pic/wows_id_very_good.jpg')
img_dalao = IMG.open('wows_pic/wows_id_dalao.jpg')


img_avg_cv = cv.imread('wows_pic/wows_id_avg.jpg')
img_below_avg_cv = cv.imread('wows_pic/wows_id_below_avg.jpg')
img_god_cv = cv.imread('wows_pic/wows_id_god.jpg')
img_good_cv = cv.imread('wows_pic/wows_id_good.jpg')
img_work_hard_cv = cv.imread('wows_pic/wows_id_need_work_hard.jpg')
img_unknown_cv = cv.imread('wows_pic/wows_id_unknown.jpg')
img_very_good_cv = cv.imread('wows_pic/wows_id_very_good.jpg')
img_dalao_cv = cv.imread('wows_pic/wows_id_dalao.jpg')

wows_pic = {
    'draw_avg': [img_avg, img_avg_cv],
    'draw_below_avg': [img_below_avg, img_below_avg_cv],
    'draw_god': [img_god, img_god_cv],
    'draw_good': [img_good, img_good_cv],
    'draw_work_hard': [img_work_hard, img_work_hard_cv],
    'draw_unknown': [img_unknown, img_unknown_cv],
    'draw_very_good': [img_very_good, img_very_good_cv],
    'draw_dalao': [img_dalao, img_dalao_cv]
}
setFont = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 50)
setFont_big = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 70)
Font = {
    'setFont': setFont,
    'setFont_big': setFont_big,
}
app.create(GraiaScheduler)
saya = app.create(Saya)
saya.install_behaviours(
    app.create(BroadcastBehaviour),
    app.create(GraiaSchedulerBehaviour),
)

with saya.module_context():
    saya.mount('wows_pic', wows_pic)
    saya.mount('Font', Font)
    saya.mount('CoolDown', [])
    for module_info in pkgutil.iter_modules(["modules"]):
        saya.require("modules." + module_info.name)
app.launch_blocking()
