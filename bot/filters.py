from aiogram.types import Message, CallbackQuery
from aiogram.filters import BaseFilter
from bot_instans import bot_storage_key, dp
from aiogram.fsm.context import FSMContext
from postgres_functions import return_last


class USER_BAZA_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery, state:FSMContext):
        # print(f'\n\nUSER_BAZA_FILTE worsk, cb data = {cb.data}\n')
        bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
        # print('bot_dict = ', bot_dict)
        if not bot_dict:
            return False
        us_mahnung_baza = bot_dict[str(cb.from_user.id)]['reg']  # Получаю базу регулярных напоминаний юзера
        uniq_baza = bot_dict[str(cb.from_user.id)]['uniq']
        last = await return_last(cb.from_user.id) # '' or '1'
        # print('uniq_baza = ', uniq_baza)
        # print('last = ', last)
        if str(cb.data) in us_mahnung_baza and last=='1':  # Смена этого индикатора снова на возможна только в классическом колбэк хэндлере
            # print('RETURN TRUE\n')
            return True
        if str(cb.data) in uniq_baza and last=='1':
            # print('RETURN TRUE\n')
            return True
        # print('RETURN FALSE')
        return False

class USER_BAZA_TWO_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery):
        # print(f'\n\nTWO_FILTE worsk, cb data = {cb.data}\n\n')
        if not cb.data.isdigit():
            return False
        last = await return_last(cb.from_user.id)
        # print('us_mahnung_baza = ', us_mahnung_baza)
        # print('last = ', last)
        if not last and str(cb.data):
            # print('TWO RETURN TRUE\n')
            return True
        # print('TWO RETURN FALSE')
        return False


class IS_ADMIN(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id == 6685637602:
            return True
        return False








