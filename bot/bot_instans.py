from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
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
scheduler = AsyncIOScheduler(timezone='Europe/Moscow', jobstores=job_stores)

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
    ask_capture = State()
    enter_capture = State()
    vor_mahnung = State()
    nach_mahnung_accepting = State()

class MONAT_MAHNUNG(StatesGroup):
    general = State()
    taily = State()
    napominalka_start = State()
    nach_napom = State()
    hour = State()
    minuten = State()
    get_content = State()
    ask_capture = State()
    accept_capture = State()
    choose_type = State()

otvet_chas_dict = {'button_00': '00', 'button_1': '01', 'button_2': '02', 'button_3': '03',
                'button_4': '04', 'button_5': '05', 'button_6': '06', 'button_7': '07',
                'button_8': '08', 'button_9': '09', 'button_10': '10', 'button_11': '11',
                'button_12': '12', 'button_13': '13', 'button_14': '14', 'button_15': '15',
                'button_16': '16', 'button_17': '17', 'button_18': '18', 'button_19': '19',
                'button_20': '20', 'button_21': '21', 'button_22': '22', 'button_23': '23'}

real_min_dict = {'button_00': '00', 'button_05': '05', 'button_10': '10', 'button_15': '15',
                'button_20': '20', 'button_25': '25', 'button_30': '30', 'button_35': '35',
                'button_40': '40', 'button_45': '45', 'button_50': '50', 'button_55': '55',
                }


# Очередь для сообщений
message_queue = asyncio.Queue()
# Фоновый воркер для обработки сообщений
async def background_worker():
    while True:
        message = await message_queue.get()
        chat_id = message["chat_id"]
        content_type = message["content_type"]
        content = message["content"]
        caption = message.get("caption")  # Подпись для фото
        try:
            if content_type == "text":
                await bot.send_message(chat_id=chat_id, text=content)
            elif content_type == "photo":
                await bot.send_photo(chat_id=chat_id, photo=content, caption=caption)
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            await asyncio.sleep(1)  # Повторная попытка через 1 секунду
        finally:
            await asyncio.sleep(0.05)  # Соблюдаем лимит Telegram API

# Функция для добавления сообщений в очередь
# Добавляем сообщение в очередь (для текстовых и фото сообщений)
async def queue_sender_message(chat_id: int, content: str, content_type: str = "text", caption: str = None):
    """
    Добавляет сообщение в очередь на отправку.
    :param chat_id: ID чата
    :param content: Текст сообщения или путь/ссылка на фото
    :param content_type: Тип содержимого ('text' или 'photo')
    :param caption: Подпись для фото (только для content_type='photo')
    """
    await message_queue.put({
        "chat_id": chat_id,
        "content_type": content_type,
        "content": content,
        "caption": caption
    })


class LAST_MAHNUNG(StatesGroup):
    indefinite = State()
    single = State()


tz_dict = {'Europe/Berlin':3600, 'Europe/Kiev':7200, 'Europe/Moscow':10800, 'Europe/Samara':14400,
           'Asia/Yekaterinburg':18000, 'Asia/Omsk':21600, 'Europe/London':0,
            'Asia/Novosibirsk':25200,  # +7
             'Asia/Krasnoyarsk':28800,  # +8
            'Asia/Irkutsk':32400,   # +9
            'Asia/Chita':36000,   # +10
            'Asia/Vladivostok': 39600,  # +11
             'Asia/Magadan' : 43200    # +12
           }



