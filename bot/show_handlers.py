from aiogram.types import User, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Row
from aiogram_dialog.widgets.kbd import Button, Cancel
from lexicon import *
from aiogram_dialog.api.entities.modes import ShowMode
from aiogram_dialog.widgets.input import  TextInput
from aiogram.fsm.state import State, StatesGroup
from dialog_functions import id_check
from dialog_functions import return_right_row
from bot_instans import bot, bot_storage_key, dp
import asyncio
from input_handlers import correct_id_handler, error_id_handler
from postgres_functions import return_lan
from show_uniq_events import SHOW_UNIQ_EVENTS


class SHOW_MAHNUNG(StatesGroup):
    show_mahnung_start = State()
    show_mahnung_end = State()
    delete_mahn = State()
    weiter_edit = State()


async def get_users_mahnungen(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    us_bot_dict = bot_dict[str(event_from_user.id)]
    if us_bot_dict['uniq']:
        est_uniq = True
    else:
        est_uniq = False

    if us_bot_dict['reg']:
        est_reg = True
    else:
        est_reg = False

    if not us_bot_dict['uniq'] and not us_bot_dict['reg']:
        net_sobytiy = True
        est_sibitiya = False
    else:
        net_sobytiy = False
        est_sibitiya = True

    getter_data = {'welche':  regular_or_uniq[lan], 'uniq': alt[lan], 'regular':neu[lan],
                   'est_uniq':est_uniq, 'est_reg':est_reg, 'net_sobytiy':net_sobytiy,
                   'no_one':no_events[lan], 'gibt_es_events':est_sibitiya
                   }
    return getter_data

async def go_to_show_uniq(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    await dialog_manager.start(state=SHOW_UNIQ_EVENTS.pre_cal)

async def schow_zukunft_mahnung(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    # print('schow_zukunft_mahnung works')
    user_id = callback.from_user.id
    lan = await return_lan(user_id)
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    us_mahnung_baza = bot_dict[str(callback.from_user.id)]['reg']  # Получаю базу напоминаний юзера
    # print('us_mahnung_baza = ', us_mahnung_baza)
    if us_mahnung_baza:
        i = ''
        m = ''
        w = ''
        d = ''
        interval_msg = f'🌍  <b>{interval_list[lan]}</b>\n\n'
        monat_text = f'🔆  <b>{monat_list[lan]}</b>\n\n'
        week_text = f'⭐️  <b>{week_list[lan]}</b>\n\n'
        day_text = f'🔔  <b>{day_list[lan]}</b>\n\n'
        for user_mahnung_key,  mahnung in sorted(us_mahnung_baza.items()):  # user_mahnung_key = '1732806300'
            mahn_data = mahnung['real_time']   # Время на которое юзер устновил событие # 28.11.2024  17:05 or Thu San
            capture = mahnung['capture']
            await asyncio.sleep(0.2)
            if mahnung['selector'] == 'I':
                imnterval = mahnung['my_interval']

                if not mahnung['foto_id']:
                    interval_msg += f'🔺 <b>{mahn_data}</b>\n<b>Interval days: {imnterval}</b>\n\n{mahnung["titel"]}\n\n<i>id Mahnung</i>  {user_mahnung_key}\n\n'
                    i = 1
                    await asyncio.sleep(0.25)
                else:
                    caption = f'🔺 <b>{mahn_data}</b>\n<b>Interval days: {imnterval}</b>\n\n<i>id Mahnung</i>  {user_mahnung_key}'
                    await bot.send_photo(chat_id=user_id, photo=mahnung["foto_id"], caption=caption)

            elif mahnung['selector'] == 'M':
                repres = return_right_row(mahn_data)  #  121450
                if not mahnung['foto_id']:
                    # print('We are at 108 cb_dialogs')
                    monat_text += f'🔺 <b>{repres}</b>\n\n{mahnung["titel"]}\n\n<i>id Mahnung</i>  {user_mahnung_key}\n\n'
                    m = 1
                else:
                    caption = f'🔺 <b>{repres}</b>\n\n{capture}\n\n<i>id Mahnung</i>  {user_mahnung_key}'
                    await bot.send_photo(chat_id=user_id, photo=mahnung["foto_id"], caption=caption)
            elif mahnung['selector'] == 'W':
                # repres = return_right_row(mahn_data)  #  121450
                if not mahnung['foto_id']:
                    # print('We are at 152 cb_dialogs')
                    week_text += f'🔺 <b>{mahn_data}</b>\n\n{mahnung["titel"]}\n\n<i>id Mahnung</i>  {user_mahnung_key}\n\n'
                    w = 1
                else:
                    caption = f'🔺 <b>{mahn_data}</b>\n\n{capture}\n\n<i>id Mahnung</i>  {user_mahnung_key}'
                    await bot.send_photo(chat_id=user_id, photo=mahnung["foto_id"], caption=caption)
            else:
                if not mahnung["foto_id"]:
                    day_text += f'🔺 <b>{mahn_data}</b>\n\n{mahnung["titel"]}\n\n<i>id Mahnung</i>  {user_mahnung_key}\n\n'
                    d = 1
                else:
                    caption = f'🔺 <b>{mahn_data}</b>\n\n{capture}\n\n<i>id Mahnung</i>  {user_mahnung_key}'
                    await bot.send_photo(chat_id=user_id, photo=mahnung['foto_id'], caption=caption)

        if i:
            await bot.send_message(chat_id=user_id, text=interval_msg)
            await asyncio.sleep(0.2)
        if m:
            await bot.send_message(chat_id=user_id, text=monat_text)
            await asyncio.sleep(0.2)
        if w:
            await bot.send_message(chat_id=user_id, text=week_text)
            await asyncio.sleep(0.2)
        if d:
            await bot.send_message(chat_id=user_id, text=day_text)
            await asyncio.sleep(0.2)
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await asyncio.sleep(0.3)
        await dialog_manager.next()
    else:
        await bot.send_message(chat_id=user_id, text=net_napominaniy[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await asyncio.sleep(0.3)
        await dialog_manager.done()


async def go_to_basic_func(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    await dialog_manager.done()

async def go_to_basic_func_for_last_dialog(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    await dialog_manager.done()

async def go_to_input_mahnung_id_for_show(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next() #  switch_to(state=SHOW_MAHNUNG.weiter_edit)


async def return_funk_to_basic(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):

    await dialog_manager.back()# start(state=ZAPUSK.add_show, show_mode=ShowMode.SEND)

async def return_funk_to_basic_2(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):

    await dialog_manager.done() #start(state=ZAPUSK.add_show, show_mode=ShowMode.DELETE_AND_SEND)

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
    print('\n\ngo_to_3_window works = ')
    await dialog_manager.switch_to(state=SHOW_MAHNUNG.show_mahnung_start,  show_mode=ShowMode.DELETE_AND_SEND)

async def get_data_for_3_window_in_SHOW_MAHNUNG(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'id_deleted_mahn': give_me_id_mahnung[lan]}
    return getter_data

async def get_weiter_edit(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    user_id = event_from_user.id
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    us_bot_dict = bot_dict[str(user_id)]['reg']  # Получаю только регулярные события
    if us_bot_dict:
        gibt_es_mahnung = True
        net_drugix = False
    else:
        gibt_es_mahnung = False
        net_drugix = True

    getter_data = {'weiter_edit': weiter_edit[lan], 'gibt_es_mahnung': gibt_es_mahnung,
                   'return_to_basic': '⬅️', 'edit':edit[lan], 'net_drugix':net_drugix,
                   'pusto': net_regular_mahnung[lan]}
    return getter_data


async def get_len_user_mahn_list(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    user_id = event_from_user.id
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    us_bot_dict = bot_dict[str(user_id)]
    if us_bot_dict:
        gibt_es_mahnung = False
    else:
        gibt_es_mahnung = True

    getter_data = {'not_mahnung': gibt_es_mahnung, 'last_dialog_text':last_dialog_text[lan]}
    return getter_data

#########################################################################################################

show_mahnung_dialog = Dialog(
    Window(  # Окно отправляющее запланированные ивенты
        Format('{welche}', when='gibt_es_events'), #  Выберите уникальные или регулярные напоминания вы хотети посмотреть
        Format('{no_one}', when='net_sobytiy'),
        Row(Button(Const('◀️'),
              id='zuruck_button',
               on_click=go_to_basic_func),
            Button(text=Format('{uniq}', when='est_uniq'),  # Уникальные события
              id='uniq_button',
              on_click=go_to_show_uniq)
            ),
            Button(text=Format('{regular}', when='est_reg'),
              id='reg_button',
              on_click=schow_zukunft_mahnung),
        state=SHOW_MAHNUNG.show_mahnung_start,
        getter=get_users_mahnungen
    ),
#############################################################################################
    Window( # В окне происходит выбор, удалять ивенты или вернуться к басик окну
        Format('{wahl}'), # Хотите удалить напоминание ?
        Row(Button(text=Format('{edit}', when='gibt_es_mahnung'),
                      id='edit_button',
                      on_click=go_to_input_mahnung_id_for_show),
                Button(
                      Format(text='{return_to_basic}'),
                      id='return_button_1',
                      on_click=return_funk_to_basic)
        ),
        state=SHOW_MAHNUNG.show_mahnung_end,
        getter=get_edit_window),

    Window( # В окне происходит удаление напоминания
        Format('{id_deleted_mahn}'),
        TextInput(
            id='id_input',
            type_factory=id_check,
            on_success=correct_id_handler,
            on_error=error_id_handler
        ),
        Cancel(Const('◀️'),
               id='cancel_att'),
        state=SHOW_MAHNUNG.delete_mahn,
        getter=get_data_for_3_window_in_SHOW_MAHNUNG
    ),

Window( # В окне происходит выбор удалить ещё одно сообщение или вернуться назад
        Format('{weiter_edit}', when='gibt_es_mahnung'),  # Удалить другие напоминания ?
        Format('{pusto}', when='net_drugix'),
        Row(
            Button(text=Format('{edit}', when='gibt_es_mahnung'),  # Удалить напоминания
                  id='edit_button',
                  on_click=go_to_3_window),
            Cancel(text=Format(text='{return_to_basic}'),
                  id='return_button_2',  #  Вернусь в коренвое окно
                  ),
        ),
        state=SHOW_MAHNUNG.weiter_edit,
        getter=get_weiter_edit),
)

