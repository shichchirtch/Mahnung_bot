from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# from aiogram.fsm.storage.memory import StorageKey, MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, Redis, StorageKey
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import settings
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import DefaultKeyBuilder

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

otvet_chas_dict = {'button_00': '00', 'button_1': '01', 'button_2': '02', 'button_3': '03',
                'button_4': '04', 'button_5': '05', 'button_6': '06', 'button_7': '07',
                'button_8': '08', 'button_9': '09', 'button_10': '10', 'button_11': '11',
                'button_12': '12', 'button_13': '13', 'button_14': '14', 'button_15': '15',
                'button_16': '16', 'button_17': '17', 'button_18': '18', 'button_19': '19',
                'button_20': '20', 'button_21': '21', 'button_22': '22', 'button_23': '23'}

min_dict = {'button_00': '00', 'button_05': '05', 'button_10': '10', 'button_15': '15',
                'button_20': '20', 'button_25': '25', 'button_30': '30', 'button_35': '35',
                'button_40': '40', 'button_45': '45', 'button_50': '50', 'button_55': '55',
                }


