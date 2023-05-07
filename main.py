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
from ApiKeys import bot_qq, host, key

app = Ariadne(
    connection=config(
        bot_qq,  # 你的机器人的 qq 号
        key,  # 填入你的 mirai-api-http 配置中的 verifyKey
        # 以下两行（不含注释）里的 host 参数的地址
        # 是你的 mirai-api-http 地址中的地址与端口
        # 他们默认为 "http://localhost:8080"
        # 如果你 mirai-api-http 的地址与端口也是 localhost:8080
        # 就可以删掉这两行，否则需要修改为 mirai-api-http 的地址与端口
        HttpClientConfig(host=host),
        WebsocketClientConfig(host=host),
    ),
)
main_data_img = cv.imread('components/recent.png')
pr_bar_img = cv.imread('components/pr_bar.png')
max_data_img = cv.imread('components/max_main.png')
recent_data_img = cv.imread('components/recent.png')
images = [main_data_img, pr_bar_img, max_data_img, recent_data_img]
font_medium = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 40)
font_heavy = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 48)
font_medium_32 = ImageFont.truetype("src/font/SourceHanSans-Heavy.otf", 32)
fonts = [font_medium, font_heavy, font_medium_32]
app.create(GraiaScheduler)
saya = app.create(Saya)
saya.install_behaviours(
    app.create(BroadcastBehaviour),
    app.create(GraiaSchedulerBehaviour),
)

with saya.module_context():
    saya.mount('wows_images', images)
    saya.mount('Font', fonts)
    saya.mount('CoolDown', [])
    saya.require("wows")
    for module_info in pkgutil.iter_modules(["modules"]):
        saya.require("modules." + module_info.name)
app.launch_blocking()
