from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import StorageKey, MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, Redis, StorageKey
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import settings
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.middleware import FSMContextMiddleware

key_builder = DefaultKeyBuilder(with_destiny=True)

using_redis = Redis(host=settings.REDIS_HOST)

redis_storage = RedisStorage(redis=using_redis, key_builder=key_builder)

job_stores = {
    'default': RedisJobStore(
        host=settings.REDIS_HOST,  # Укажите IP адрес Redis контейнера  REDIS_HOST
        db=0,              # Номер базы данных Redis
        password=None      # Пароль, если требуется
    )
}

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')#, jobstores=job_stores)
# scheduler = AsyncIOScheduler()

aio_storage = MemoryStorage()

# BOT_TOKEN = '6471784185:AAEWakBbPrU-bKGGanxahUq__ZbyZ1s8dBI'

# bot = Bot(token=BOT_TOKEN,
#               default=DefaultBotProperties(parse_mode=ParseMode.HTML))

bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

bot_storage_key = StorageKey(bot_id=bot.id, user_id=bot.id, chat_id=bot.id)

dp = Dispatcher(storage=redis_storage)

class ZAPUSK(StatesGroup):
    set_lan = State()
    spam = State()
    set_timezone = State()
    add_show = State()

class WORK_WITH_SCHED(StatesGroup):
    choose_regular_or_unique = State()
    calendar = State()
    uhr = State()
    minuten = State()
    titel = State()
    vor_mahnung = State()
    nach_mahnung_accepting = State()

# temp_baza = [] # Сюда записываю юзеров стартанувших бота, а при рестарте база обнуляется


