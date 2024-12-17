from aiogram.types import Message, CallbackQuery
from aiogram.filters import BaseFilter
from bot_instans import bot_storage_key, dp
from aiogram.fsm.context import FSMContext
from postgres_functions import return_last


class USER_BAZA_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery, state:FSMContext):
        print(f'\n\nUSER_BAZA_FILTE worsk, cb data = {cb.data}\n\n')
        bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
        us_mahnung_baza = bot_dict[str(cb.from_user.id)]  # Получаю базу напоминаний юзера
        last = await return_last(cb.from_user.id)
        print('us_mahnung_baza = ', us_mahnung_baza)
        print('last = ', last)
        if str(cb.data) in us_mahnung_baza and last=='1':
            print('RETURN TRUE\n')
            return True
        print('RETURN FALSE')
        return False

class USER_BAZA_TWO_FILTER(BaseFilter):
    async def __call__(self, cb: CallbackQuery, state:FSMContext):
        print(f'\n\nTWO_FILTE worsk, cb data = {cb.data}\n\n')
        if not cb.data.isdigit():
            return False
        us_dict = await state.get_data()
        last = await return_last(cb.from_user.id)
        # print('us_mahnung_baza = ', us_mahnung_baza)
        print('last = ', last)
        if not last and str(cb.data) not in us_dict['del_msg']:
            print('TWO RETURN TRUE\n')
            return True
        print('TWO RETURN FALSE')
        return False


class IS_ADMIN(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id == 6685637602:
            return True
        return False








