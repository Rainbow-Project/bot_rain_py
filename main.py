import pkgutil

from graia.ariadne.app import Ariadne
from graia.saya import Saya
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
        HttpClientConfig(host="http://127.0.1:1575"),
        WebsocketClientConfig(host="http://127.0.1:1575"),
    ),
)
app.create(GraiaScheduler)
saya = app.create(Saya)
saya.install_behaviours(
    app.create(BroadcastBehaviour),
    app.create(GraiaSchedulerBehaviour),
)

with saya.module_context():
    for module_info in pkgutil.iter_modules(["modules"]):
        saya.require("modules." + module_info.name)

app.launch_blocking()
