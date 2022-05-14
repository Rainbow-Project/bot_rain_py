from graia.ariadne import Ariadne
from graia.saya import Saya, Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from modules.Wows.wows_sql_data import update

saya = Saya.current()
channel = Channel.current()


@channel.use(SchedulerSchema(timers.crontabify("30 2 * * * 30")))
async def wows_auto_update(app: Ariadne):
    update()