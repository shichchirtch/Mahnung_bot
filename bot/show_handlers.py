from aiogram.types import User, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Row, Group
from aiogram_dialog.widgets.kbd import Button, Cancel
from lexicon import *
from aiogram_dialog.api.entities.modes import ShowMode
from aiogram_dialog.widgets.input import  TextInput
from aiogram.fsm.state import State, StatesGroup
from dialog_functions import id_check
from dialog_functions import return_right_row
from bot_instans import bot, bot_storage_key, dp
import datetime
import asyncio
from input_handlers import correct_id_handler, error_id_handler
from postgres_functions import return_tz, return_lan

class SHOW_MAHNUNG(StatesGroup):
    show_mahnung_start = State()
    show_mahnung_end = State()
    delete_mahn = State()
    weiter_edit = State()

tz_dict = {'Europe/Berlin':3600, 'Europe/Kiev':7200, 'Europe/Moscow':10800, 'Europe/Samara':14400, 'Asia/Yekaterinburg':18000, 'Asia/Novosibirsk':21600, 'Europe/London':0}

async def get_users_mahnungen(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'welche': neu_or_alt[lan], 'past': alt[lan], 'zukunft':neu[lan]}
    return getter_data

async def schow_last_mahnung(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    print('schow_last_mahnung works')
    user_id = callback.from_user.id
    lan = await return_lan(user_id)
    us_tz  = await return_tz(user_id)
    dialog_manager.dialog_data['lan'] = lan
    in_stamp_dt_obj = datetime.datetime.now().replace(second=0, microsecond=0)  # Прибавить ТаймЗону
    in_stamp_s_uchetom_tz = int(in_stamp_dt_obj.timestamp()) + tz_dict[us_tz]  # Подставлены параметры таймзоны юзера
    # print('41 in_stamp = ', in_stamp)
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    us_mahnung_baza = bot_dict[str(callback.from_user.id)] # Получаю базу напоминаний юзера  {'1732806300': {}}
    # print('us_mahnung_baza = ', us_mahnung_baza)
    caunter = 0
    # vsego_ivent = len(us_mahnung_baza)
    if us_mahnung_baza:
        for za_chas_key,  mahnung in sorted(us_mahnung_baza.items()):
            mahn_data = mahnung["real_time"]   # Время на которое юзер устновил событие  #  28.11.2024  16:20
            if mahnung['selector'] == 'U':  # Только для уникальных напоминаний
                dt_object = datetime.datetime.strptime(mahn_data, "%d.%m.%Y %H:%M") # Переводим строку в ЭК datetime
                int_mahn_data = int(dt_object.timestamp())
                if int_mahn_data < in_stamp_s_uchetom_tz:  # Если событие уже в прошлом
                    if not mahnung['foto_id']:  # Для текстовых напоминаний
                        formed_text = f'🔕 <b>{mahn_data}</b>\n\n{mahnung["titel"]}\n\n<i>ID Mahnung  {za_chas_key}</i>'
                        await bot.send_message(chat_id=user_id, text=formed_text)
                        await asyncio.sleep(0.25)
                    else:
                        await bot.send_photo(chat_id=user_id, photo=mahnung['foto_id'], caption=f'🔕 {mahn_data}\n\n<i>ID Mahnung  {za_chas_key}</i>')
                    caunter+=1

        await bot.send_message(chat_id=user_id,
                                       text=f'{event_in_future[lan]} <b>{len(us_mahnung_baza) - caunter}</b>')

    else:
        await bot.send_message(chat_id=user_id, text=net_napominaniy[lan])
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await asyncio.sleep(0.3)
    await dialog_manager.next()


async def schow_zukunft_mahnung(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    print('schow_zukunft_mahnung works')
    user_id = callback.from_user.id
    lan = await return_lan(user_id)
    us_tz = await return_tz(user_id)
    in_stamp_dt_obj = datetime.datetime.now().replace(second=0, microsecond=0)  # Прибавить ТаймЗону
    in_stamp = int(in_stamp_dt_obj.timestamp()) + tz_dict[us_tz] # Здесь  параметры таймзоны
    # print('80 in_stamp = ', in_stamp)
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота

    us_mahnung_baza = bot_dict[str(callback.from_user.id)]  # Получаю базу напоминаний юзера
    # print('us_mahnung_baza = ', us_mahnung_baza)
    caunter = 0
    if us_mahnung_baza:
        for user_mahnung_key,  mahnung in sorted(us_mahnung_baza.items()):  # user_mahnung_key = '1732806300'
            mahn_data = mahnung['real_time']   # Время на которое юзер устновил событие # 28.11.2024  17:05 or Thu San
            if mahnung['selector'] == 'U':
                dt_object = datetime.datetime.strptime(mahn_data, "%d.%m.%Y %H:%M") # Переводим строку в ЭК datetime
                int_mahn_data = int(dt_object.timestamp())
                if int_mahn_data > in_stamp:  # 20.12.24 > 18.12.20 - нужно заменить на инты
                    # print('za_chas_key = ', type(user_mahnung_key))  # 1732806300
                    if not mahnung['foto_id']:
                        formed_text = f'🔺 <b>{mahn_data}</b>\n\n{mahnung["titel"]}\n\n<i>id Mahnung</i>  {user_mahnung_key}'
                        await bot.send_message(chat_id=user_id, text=formed_text)
                        await asyncio.sleep(0.25)
                    else:
                        caption = f'🔺 <b>{mahn_data}</b>\n\n<i>id Mahnung</i>  {user_mahnung_key}'
                        await bot.send_photo(chat_id=user_id, photo=mahnung["foto_id"], caption=caption)
                else:
                    caunter+=1
                    # print('caunter = ', caunter)
            elif mahnung['selector'] == 'M':
                repres = return_right_row(mahn_data)  #  121450
                if not mahnung['foto_id']:
                    # print('We are at 108 cb_dialogs')
                    formed_text = f'🔺 <b>{repres}</b>\n\n{mahnung["titel"]}\n\n<i>id Mahnung</i>  {user_mahnung_key}'
                    await bot.send_message(chat_id=user_id, text=formed_text)
                    await asyncio.sleep(0.25)
                else:
                    caption = f'🔺 <b>{repres}</b>\n\n<i>id Mahnung</i>  {user_mahnung_key}'
                    await bot.send_photo(chat_id=user_id, photo=mahnung["foto_id"], caption=caption)
            elif mahnung['selector'] == 'W':
                # repres = return_right_row(mahn_data)  #  121450
                if not mahnung['foto_id']:
                    # print('We are at 152 cb_dialogs')
                    formed_text = f'🔺 <b>{mahn_data}</b>\n\n{mahnung["titel"]}\n\n<i>id Mahnung</i>  {user_mahnung_key}'
                    await bot.send_message(chat_id=user_id, text=formed_text)
                    await asyncio.sleep(0.25)
                else:
                    caption = f'🔺 <b>{mahn_data}</b>\n\n<i>id Mahnung</i>  {user_mahnung_key}'
                    await bot.send_photo(chat_id=user_id, photo=mahnung["foto_id"], caption=caption)
            else:
                if not mahnung["foto_id"]:
                    # print('We are at 160 cb_dialogs')
                    formed_text = f'🔺 <b>{mahn_data}</b>\n\n{mahnung["titel"]}\n\n<i>id Mahnung</i>  {user_mahnung_key}'
                    await bot.send_message(chat_id=user_id, text=formed_text)
                    await asyncio.sleep(0.25)
                else:
                    caption = f'🔺 <b>{mahn_data}</b>\n\n<i>id Mahnung</i>  {user_mahnung_key}'
                    await bot.send_photo(chat_id=user_id, photo=mahnung['foto_id'], caption=caption)

        if caunter:
            await bot.send_message(chat_id=user_id, text=f'{event_in_past[lan]} <b>{caunter}</b>')
    else:
        await bot.send_message(chat_id=user_id, text=net_napominaniy[lan])
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await asyncio.sleep(0.3)
    await dialog_manager.next()


async def go_to_input_mahnung_id_for_show(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next()


async def return_funk_to_basic(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND

async def get_edit_window(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    user_id = event_from_user.id
    lan = await return_lan(user_id)
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    us_bot_dict = bot_dict[str(user_id)]
    if us_bot_dict:
        gibt_es_mahnung = True
    else:
        gibt_es_mahnung = False
    getter_data = {'wahl': edit_or_back[lan], 'edit': edit[lan], 'return_to_basic': '⬅️', 'gibt_es_mahnung': gibt_es_mahnung}
    return getter_data


async def go_to_3_window(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    await dialog_manager.switch_to(state=SHOW_MAHNUNG.show_mahnung_end,  show_mode=ShowMode.SEND)

async def get_data_for_3_window_in_SHOW_MAHNUNG(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'id_deleted_mahn': give_me_id_mahnung[lan]}
    return getter_data

async def get_weiter_edit(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    user_id = event_from_user.id
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    us_bot_dict = bot_dict[str(user_id)]
    if us_bot_dict:
        gibt_es_mahnung = True
    else:
        gibt_es_mahnung = False

    getter_data = {'weiter_edit': weiter_edit[lan], 'gibt_es_mahnung': gibt_es_mahnung, 'return_to_basic': '⬅️', 'edit':edit[lan]}
    return getter_data


show_mahnung_dialog = Dialog(
    Window(  # Окно отправляющее запланированные ивенты
        Format('{welche}'),
        Button(text=Format('{past}'),
              id='past_button',
              on_click=schow_last_mahnung),
        Button(text=Format('{zukunft}'),
              id='zukunft_button',
              on_click=schow_zukunft_mahnung),

        state=SHOW_MAHNUNG.show_mahnung_start,
        getter=get_users_mahnungen
    ),

    Window( # В окне происходит выбор, удалять ивенты или вернуться к басик окну
        Format('{wahl}'),
        Group(
            Row(
                Button(text=Format('{edit}', when='gibt_es_mahnung'),
                      id='edit_button',
                      on_click=go_to_input_mahnung_id_for_show),
                Cancel(
                      Format(text='{return_to_basic}'),
                      id='return_button',
                      on_click=return_funk_to_basic),
            ),
        ),
        state=SHOW_MAHNUNG.show_mahnung_end,
        getter=get_edit_window),

    Window( # В окне происходит удаление напоминания
        Format('{id_deleted_mahn}'),
        TextInput(
            id='id_input',
            type_factory=id_check,
            on_success=correct_id_handler,
            on_error=error_id_handler,
        ),
        state=SHOW_MAHNUNG.delete_mahn,
        getter=get_data_for_3_window_in_SHOW_MAHNUNG
    ),

Window( # В окне происходит выбор удалить ещё одно сообщение или вернуться назад
        Format('{weiter_edit}'),
        Group(
                Cancel(text=Format(text='{return_to_basic}'),
                      id='return_button',
                      on_click=return_funk_to_basic),
                Button(text=Format('{edit}', when='gibt_es_mahnung'),
                      id='edit_button',
                      on_click=go_to_3_window)
        ),
        state=SHOW_MAHNUNG.weiter_edit,
        getter=get_weiter_edit),
)