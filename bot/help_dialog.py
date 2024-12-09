from aiogram_dialog import Dialog, Window
from aiogram.types import CallbackQuery, User, Message, ContentType
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.api.entities.modes import ShowMode
from lexicon import *
from aiogram.fsm.state import State, StatesGroup
import asyncio
import datetime
from postgres_functions import get_user_count, return_lan, insert_timezone, insert_lan
from aiogram_dialog.widgets.input import MessageInput
from bot_instans import ZAPUSK
from aiogram_dialog.api.entities.modes import StartMode


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
    getter_data = {'help_text': help_text[lan],
                   'back': '⏪',
                   're_set_lan': '🇩🇪 🇬🇧 🇺🇦 🇹🇷 🇮🇷 🇸🇦 🇷🇺',
                   'show_presentation': show_presentation[lan],
                   'reset_tz':'⏱️      🔁     ⏰',
                   'rew_1':send_review[lan],
                   'skolko_format':'👥'
                   }
    return getter_data


async def go_to_previous(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    await dialog_manager.start(ZAPUSK.add_show, mode=StartMode.RESET_STACK)


async def go_to_reset_lan(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    print('go to reset lan works')
    await dialog_manager.next()


async def provide_presentation(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    lan = await return_lan(callback.from_user.id)
    chosing_presentation = get_lynk[lan]
    await callback.message.answer(text=chosing_presentation)
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await asyncio.sleep(3)
    await dialog_manager.done()


async def button_skolko(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    print('\n\nbutton_skolko works\n\n')
    lan = await return_lan(callback.from_user.id)
    skolko = skolko_us[lan]
    print('skolk0 = ', skolko)
    taily_users = await get_user_count()
    print('taily_ussers = ', taily_users)
    await callback.message.answer(f'{skolko} {taily_users} 🔥')
    await dialog_manager.done()  # выход из режима админа


async def reset_lan(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    print('reset lan works')
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
    # print('89 lan = ', lan)
    current_time = datetime.datetime.now()
    bot_time = current_time.strftime("%H:%M")
    getter_data = {'bot_time_reset':f'<b>{bot_time_now[lan]} {bot_time}</b>',
                   'gleich':us_tz_gleich[lan], 'plus_1':us_tz_plus_1[lan], 'plus_2':us_tz_plus_2[lan], 'plus_3':us_tz_plus_3[lan],
                   'plus_4': us_tz_plus_4[lan], 'plus_5': us_tz_plus_5[lan], 'plus_6': us_tz_plus_6[lan]}
    return getter_data

async def reset_user_tz(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    print('reset_user_tz works')
    user_id = callback.from_user.id
    tz_dict = {'tz_gleich': 'Europe/London',
               'tz_plus_1': 'Europe/Berlin',
               'tz_plus_2': "Europe/Kiev",
               'tz_plus_3': 'Europe/Moscow',
               'tz_plus_4': 'Europe/Samara',
               'tz_plus_5': "Asia/Yekaterinburg",
               'tz_plus_6': 'Asia/Novosibirsk'}
    tz = tz_dict[callback.data]
    dialog_manager.dialog_data['tz']=tz
    await insert_timezone(user_id, tz)
    att = await callback.message.answer(text=f'Now your TimeZone is {tz}')
    await dialog_manager.done()
    dialog_manager.show_mode = ShowMode.SEND
    await asyncio.sleep(3)
    await att.delete()
#############################################################################################

async def get_review_enter(dialog_manager: DialogManager, event_from_user: User, *args, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'write_review': write_review[lan]}
    return getter_data


async def message_text_handler_for_review(message: Message, widget: MessageInput,
                                        dialog_manager: DialogManager, *args, **kwargs) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    lan = await return_lan(message.from_user.id)
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    join_text = f'User_id {user_id}, user_name  {user_name} send MESSAGE {message.text}'
    await message.bot.send_message(chat_id=-1002226816025, text=join_text)
    await message.answer(danke[lan])
    await dialog_manager.done()
    dialog_manager.show_mode = ShowMode.NO_UPDATE

async def message_not_text_handler(message: Message, widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    print('message_not_text_handler works ')
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    lan = await return_lan(message.from_user.id)
    await message.answer(data_mahnung_nur_text[lan])


dialog_help = Dialog(
    Window(
        Format('{help_text}'),
        Button(text=Format('{back}'),
               id='go_to_previous_window',
               on_click=go_to_previous),
        Button(text=Format('{re_set_lan}'),
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
        Button(text=Format('{skolko_format}'),
               id='skolko_id',
               on_click=reset_user_tz),
        state=HELP_DIAL.erst,
        getter=get_help_1),

    Window(
        Const('Choose Language'),
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
        Button(text=Format('{gleich}'), id='tz_gleich', on_click=reset_user_tz),
        Button(text=Format('{plus_1}'), id='tz_plus_1', on_click=reset_user_tz),
        Button(text=Format('{plus_2}'), id='tz_plus_2', on_click=reset_user_tz),
        Button(text=Format('{plus_3}'), id='tz_plus_3', on_click=reset_user_tz),
        Button(text=Format('{plus_4}'), id='tz_plus_4', on_click=reset_user_tz),
        Button(text=Format('{plus_5}'), id='tz_plus_5', on_click=reset_user_tz),
        Button(text=Format('{plus_6}'), id='tz_plus_6', on_click=reset_user_tz),
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