from aiogram_dialog import Dialog, Window
from aiogram.types import CallbackQuery, User, Message, ContentType
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Start, Row
from aiogram_dialog.api.entities.modes import ShowMode
from lexicon import *
from aiogram.fsm.state import State, StatesGroup
import asyncio
import datetime
from postgres_functions import get_user_count, return_lan, insert_timezone, insert_lan
from aiogram_dialog.widgets.input import MessageInput
from bot_instans import tz_dict_letter


class HELP_DIAL(StatesGroup):
    erst = State()
    reset_lan = State()
    show_presentation = State()

class RESET_TZ(StatesGroup):
    one = State()

class REVIEW(StatesGroup):
    enter = State()
    post_input = State()


async def get_help_1(dialog_manager: DialogManager, event_from_user: User, *args, **kwargs):
    lan = await return_lan(event_from_user.id)
    if not lan:
        lan = 'ru'
        await insert_lan(event_from_user.id, 'ru')
        await insert_timezone(event_from_user.id, 'Europe/Moscow')
    taily_users = await get_user_count()
    # print('taily_users = ', taily_users)
    getter_data = {'help_text': f'<b>{help_text[lan]}</b>',
                   'back': f'⏪  👮🏼‍♂️🧑🏼‍🚒👩🏻👨🏼‍🦱👩🏽‍🦱   {taily_users}',
                   're_set_lan': '🇩🇪 🇬🇧 🇺🇦 🇹🇷 🇮🇷 🇸🇦 🇷🇺',
                   'show_presentation': show_presentation[lan],
                   'reset_tz':'⏱️      🔁     ⏰',
                   'rew_1':send_review[lan]}
    return getter_data

async def go_to_previous(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.done()


async def go_to_reset_lan(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await dialog_manager.next()


async def provide_presentation(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    lan = await return_lan(callback.from_user.id)
    if not lan:
        lan = 'ru'
        await insert_lan(callback.from_user.id, 'ru')
    video_dict = {
        'ru': 'BAACAgIAAxkBAAINBWdv5xZKBAjtV3p-ThlpdMpMxxsIAAJXXQACyNSAS8TQD540NahaNgQ',
        'de': 'BAACAgIAAxkBAAINB2dv51Z2PSjMkJJ7iDekP1ILLfe-AAJgXQACyNSAS0cioGi1tLHANgQ',
        'en': 'BAACAgIAAxkBAAINCWdv55OChWWsivD2Mh24Xu-tmdT1AAJmXQACyNSAS4acmJy9HHuWNgQ',
        'uk': 'BAACAgIAAxkBAAINC2dv58vjGzSfUhgDFrFU0KKi_eDEAAJoXQACyNSAS1saFWdD3RVMNgQ',
        'tr': 'BAACAgIAAxkBAAINDWdv5_pUe5r4RWpF3gbR4tewdbHRAAJrXQACyNSAS4FWc2TO_UqqNgQ',
        'ar': 'BAACAgIAAxkBAAIND2dv6CtbhHF9JkjgUHkLuoygaS4jAAJyXQACyNSAS_u0bAKvuUczNgQ',
        'fa': 'BAACAgIAAxkBAAINEWdv6FQeAAENqqFOe2SDyq6wWWOp5AACeV0AAsjUgEu5SVCREBByGjYE'}

    await callback.message.answer_video(video=video_dict[lan], caption=opisanie_rolika[lan])
    # await callback.message.answer(text=chosing_presentation)
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await asyncio.sleep(2)
    await dialog_manager.done()


async def reset_lan(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    # print('reset lan works')
    old_lan = await return_lan(callback.from_user.id)
    new_lan = callback.data
    if old_lan != new_lan:
        await insert_lan(callback.from_user.id, new_lan)
        await callback.message.answer(lan_reset[callback.data])
    else:
        await callback.message.answer(lan_same[callback.data])
    dialog_manager.show_mode = ShowMode.SEND

    await dialog_manager.done()

async def get_timezone_info_reset(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    if not lan:
        lan = 'ru'
        await insert_lan(event_from_user.id, 'ru')

    current_time = datetime.datetime.now()
    bot_time = current_time.strftime("%H:%M")
    getter_data = {'bot_time_reset':f'<b>{bot_time_now[lan]} {bot_time}</b>',
                   'gleich':us_tz_gleich[lan], 'plus_1':'+ 1️⃣', 'plus_2':'+ 2️⃣', 'plus_3':'+ 3️⃣',
                   'plus_4': '+ 4️⃣', 'plus_5': '+ 5️⃣', 'plus_6': '+ 6️⃣',
                   'plus_7': '+ 7️⃣',
                   'plus_8': '+ 8️⃣',
                   'plus_9': '+ 9️⃣',
                   'plus_10': '+ 🔟',
                   'plus_11': '+ 1️⃣1️⃣',
                   'plus_12': '+ 1️⃣2️⃣',
                   }
    return getter_data

async def reset_user_tz(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    user_id = callback.from_user.id
    tz = tz_dict_letter[callback.data] # from bot_instans
    print(f'user {user_id} {callback.from_user.first_name} REset tz {tz} \n\n')
    dialog_manager.dialog_data['tz']=tz
    await insert_timezone(user_id, tz)
    lan = await return_lan(callback.from_user.id)
    att = await callback.message.answer(text=f'{reset_tz[lan]} <b>{tz}</b>')
    await dialog_manager.done()
    dialog_manager.show_mode = ShowMode.SEND
    await asyncio.sleep(3)
    await att.delete()
#############################################################################################

async def get_review_enter(dialog_manager: DialogManager, event_from_user: User, *args, **kwargs):
    lan = await return_lan(event_from_user.id)
    if not lan:
        lan = 'ru'
        await insert_lan(event_from_user.id, 'ru')
    getter_data = {'write_review': write_review[lan]}
    return getter_data


async def message_text_handler_for_review(message: Message, widget: MessageInput,
                                        dialog_manager: DialogManager, *args, **kwargs) -> None:

    lan = await return_lan(message.from_user.id)
    if not lan:
        lan = 'ru'
        await insert_lan(message.from_user.id, 'ru')
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    join_text = f'User_id {user_id}, user_name  {user_name} send MESSAGE {message.text}'
    await message.bot.send_message(chat_id=-1002226816025, text=join_text)
    await message.answer(danke[lan])
    await dialog_manager.done()
    dialog_manager.show_mode = ShowMode.NO_UPDATE

async def message_not_text_handler(message: Message, widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    # print('message_not_text_handler works ')
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    lan = await return_lan(message.from_user.id)
    if not lan:
        lan = 'ru'
        await insert_lan(message.from_user.id, 'ru')
    await message.answer(data_mahnung_nur_text[lan])


dialog_help = Dialog(
    Window(
        Format('{help_text}'),
        Button(text=Format('{back}'),
               id='go_to_previous_window',
               on_click=go_to_previous),
        Button(text=Format('{re_set_lan}'),  #  Кнопка продолжает этот же диалог
               id='lan_reset',
               on_click=go_to_reset_lan),
        Button(text=Format('{show_presentation}'),
               id='presentation',
               on_click=provide_presentation),
        Start(text=Format('{reset_tz}'),
               id='reset_timezone',
               state=RESET_TZ.one),
        Start(text=Format('{rew_1}'),
               id='rew_1_button',
               state=REVIEW.enter),

        state=HELP_DIAL.erst,
        getter=get_help_1),

    Window(
        Const('<b>Choose Language</b>'),
        Button(text=Const('🇩🇪'),
               id='de',
               on_click=reset_lan),
        Button(text=Const('🇬🇧'),
               id='en',
               on_click=reset_lan),
        Button(text=Const('🇺🇦'),
               id='uk',
               on_click=reset_lan),
        Button(text=Const('🇹🇷'),
               id='tr',
               on_click=reset_lan),
        Button(text=Const('🇮🇷'),
               id='fa',
               on_click=reset_lan),
        Button(text=Const('🇸🇦'),
               id='ar',
               on_click=reset_lan),
        Button(text=Const('🇷🇺'),
               id='ru',
               on_click=reset_lan),
        state=HELP_DIAL.reset_lan)
)


reset_tz_dialog = Dialog(
    Window(
        Format('{bot_time_reset}'),
        Row(
        Button(text=Format('{gleich}'), id='tz_gleich', on_click=reset_user_tz),
        Button(text=Format('{plus_1}'), id='tz_plus_1', on_click=reset_user_tz)),
        Row(
        Button(text=Format('{plus_2}'), id='tz_plus_2', on_click=reset_user_tz),
        Button(text=Format('{plus_3}'), id='tz_plus_3', on_click=reset_user_tz)),
        Row(
        Button(text=Format('{plus_4}'), id='tz_plus_4', on_click=reset_user_tz),
        Button(text=Format('{plus_5}'), id='tz_plus_5', on_click=reset_user_tz)),
        Row(
        Button(text=Format('{plus_6}'), id='tz_plus_6', on_click=reset_user_tz),
        Button(text=Format('{plus_7}'), id='tz_plus_7', on_click=reset_user_tz)),
        Row(
        Button(text=Format('{plus_8}'), id='tz_plus_8', on_click=reset_user_tz),
        Button(text=Format('{plus_9}'), id='tz_plus_9', on_click=reset_user_tz)),
        Row(
        Button(text=Format('{plus_10}'), id='tz_plus_10', on_click=reset_user_tz),
        Button(text=Format('{plus_11}'), id='tz_plus_11', on_click=reset_user_tz),
        Button(text=Format('{plus_12}'), id='tz_plus_12', on_click=reset_user_tz)),
        state=RESET_TZ.one,
        getter=get_timezone_info_reset))

################################################################################################


review_dialog = Dialog(
    Window(
        Format('{write_review}'),
        MessageInput(
            func=message_text_handler_for_review,
            content_types=ContentType.TEXT,
        ),
        MessageInput(
            func=message_not_text_handler,
            content_types=ContentType.ANY,
        ),
        state=REVIEW.enter,
        getter=get_review_enter
    ))
