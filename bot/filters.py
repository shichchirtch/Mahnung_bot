from aiogram.types import Message
from aiogram.filters import BaseFilter
from bot_instans import temp_baza
from aiogram.fsm.context import FSMContext




# class PRE_START(BaseFilter):
#     async def __call__(self, message: Message):
#         if message.from_user.id not in temp_baza:
#             return True
#         return False

# class USER_DICT_FILTER(BaseFilter):
#     async def __call__(self, message: Message, state:FSMContext):
#         us_dict = await state.get_data()
#         print('us_dict = ', us_dict)
#         shalter = us_dict.get('shalter', False)
#         print('shalter = ' , shalter)
#         if not us_dict :
#             return True
#         if shalter==False:
#             return True
#         print('return false')
#         return False


class IS_ADMIN(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id == 6685637602:
            return True
        return False








