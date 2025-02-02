from lexicon import *
from aiogram.fsm.state import State, StatesGroup
from dialog_functions import seconds_to_date_string
import datetime
from postgres_functions import return_tz, return_lan, insert_last_1
import asyncio
from aiogram_dialog import Dialog, Window, ChatEvent, DialogManager
from aiogram_dialog.widgets.text import Const, Format, Text
from aiogram_dialog.widgets.kbd import (Button, Row, Calendar, Cancel, Back,
                                        CalendarScope, ManagedCalendar, SwitchTo)
from datetime import date, datetime
from aiogram_dialog.widgets.kbd.calendar_kbd import (DATE_TEXT, TODAY_TEXT, CalendarMonthView, CalendarScopeView,
                                                     CalendarYearsView)
from bot_instans import bot, LAST_MAHNUNG, bot_storage_key, dp, tz_dict, scheduler, ZAPUSK, store_past_event
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, User, Message
from aiogram_dialog.widgets.kbd.calendar_kbd import CalendarDaysView, CalendarConfig
from aiogram_dialog.api.entities.modes import ShowMode, StartMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from babel.dates import get_day_names, get_month_names
from dialog_functions import create_past_mahnung_keyboard, format_time_ago


class SHOW_UNIQ_EVENTS(StatesGroup):
    pre_cal = State()
    cal = State()
    accept_uniq_id = State()
    post_cal = State()


calendar_config = CalendarConfig()

SELECTED_DAYS_KEY = "selected_dates"

class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_day_names(
            width="short", context="stand-alone", locale=locale,
        )[selected_date.weekday()].title()


class MarkedDay(Text):
    def __init__(self, mark: str, other: Text):
        super().__init__()
        self.mark = mark
        self.other = other

    async def _render_text(self, data, manager: DialogManager) -> str:
        emo_dict = {'01': '1️⃣', '02': '2️⃣', '03': '3️⃣', '04': '4️⃣', '05': '5️⃣', '06': '6️⃣',
                    '07': '7️⃣', '08': '8️⃣', '09': '9️⃣', '10': '🔟', '11': '1️⃣1️⃣', '12': '1️⃣2️⃣',
                    '13': '1️⃣3️⃣', '14': '1️⃣4️⃣', '15': '1️⃣5️⃣', '16': '1️⃣6️⃣', '17': '1️⃣7️⃣', '18': '1️⃣8️⃣',
                    '19': '1️⃣9️⃣', '20': '2️⃣0️⃣', '21': '2️⃣1️⃣', '22': '2️⃣2️⃣', '23': '2️⃣3️⃣', '24': '2️⃣4️⃣',
                    '25': '2️⃣5️⃣', '26': '2️⃣6️⃣', '27': '2️⃣7️⃣', '28': '2️⃣8️⃣', '29': '2️⃣9️⃣', '30': '3️⃣0️⃣',
                    '31': '3️⃣1️⃣'}
        current_date: date = data["date"]  # 2024-12-26
        serial_date = current_date.isoformat()
        selected = manager.dialog_data.get(SELECTED_DAYS_KEY, [])
        if serial_date in selected:
            my_day = serial_date.split('-')[-1]
            return f'{emo_dict[my_day]}'
        return await self.other.render_text(data, manager)


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_month_names(
            "wide", context="stand-alone", locale=locale,
        )[selected_date.month].title()


class CustomCalendar(Calendar):
    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                config=calendar_config,
                date_text=MarkedDay("🔴", DATE_TEXT),
                today_text=MarkedDay("⭕", TODAY_TEXT),
                header_text="~~~~~ " + Month() + " ~~~~~",
                weekday_text=WeekDay(),
                next_month_text=Month() + " >>",
                prev_month_text="<< " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                config=calendar_config,
                month_text=Month(),
                header_text="~~~~~ " + Format("{date:%Y}") + " ~~~~~",
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
                config=calendar_config,
            ),
        }


def uniq_id_check(id_mahnung: str) -> str:
    if id_mahnung.isdigit() and len(id_mahnung) == 10 and id_mahnung.startswith('17'):
        return id_mahnung
    raise ValueError


async def getter_zaglushka(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    us_event_dict = bot_dict[str(event_from_user.id)]['uniq']  # получаю словарь юзера с уникальными событиями

    if us_event_dict:
        gibt_es_mahnung = True
        kein_events = False
    else:
        gibt_es_mahnung = False
        kein_events = True

    return {'First_Windows': zaglushka[lan], 'gibt_es_uniq_mahnung':gibt_es_mahnung, 'kein_events':kein_events,
            'no_treffen':no_uniq_events[lan]}


async def on_date_clicked(callback: ChatEvent, widget: ManagedCalendar, manager: DialogManager,
                          selected_date: date, /, ):
    await callback.message.answer(str(selected_date)) # Что это ?


async def first_cal(callback: CallbackQuery, widget: Button, manager: DialogManager, /, ):
    manager.dialog_data.get(SELECTED_DAYS_KEY, [])
    # us_dict = users_db[callback.from_user.id]['events']  # us_dict  =  {'1734649200': [{'titel': 'test', 'time_code': '1734649200', 'selector': 'U', 'real_time': '19.12.2024  15:50'}]}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    us_mahnung_baza = bot_dict[str(callback.from_user.id)]['uniq']  # Получаю базу напоминаний юзера
    # print('us_mahnung_baza  = ', us_mahnung_baza)
    keys = sorted(us_mahnung_baza.keys())
    # print('keys = ', keys)
    required_list = seconds_to_date_string(keys)  # required_list =  ['2024-12-19', '2024-12-28']
    manager.dialog_data[SELECTED_DAYS_KEY] = required_list  # Добавляю список в диалог_дата
    await manager.next()


async def on_date_selected(callback: ChatEvent, widget: ManagedCalendar,
                           manager: DialogManager, clicked_date: date, /, ):
    """"Функция срабатывает при нажатии на эмоджи - цифры и отправляет фото или текстовое напоминание"""
    lan = await return_lan(callback.from_user.id)
    int_key = int(callback.data.split(':')[1])  # - 86400  # callback.data =  RgQAj9calendar:1734735600
    # print('int_key = ', int_key, type(int_key))  # 1734735600 <class 'str'>
    str_key = str(int_key)  # = 1735430400  а в uniq 1735344000
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    user_uniq_dict = bot_dict[str(callback.from_user.id)]['uniq']  # получаю словарь юзера
    # print('user_uniq_dict = ',user_uniq_dict)  # {'1735344000': [{'titel': 'test', 'foto_id': '', 'za_chas': '1735311000', 'za_sutki': '1735228200', 'selector': 'U', 'real_time': '27.12.2024  15:50', 'job_id': '1735311000'}]}
    if str_key not in user_uniq_dict:
        await callback.message.answer(pusto_cal[lan])  # Для того, чтобы установить заметку на этот день - перейдите в режим добаления уникальных заметок
        manager.show_mode = ShowMode.SEND
        await manager.switch_to(SHOW_UNIQ_EVENTS.pre_cal)
    else:
        msg_list = user_uniq_dict[str_key]  # {1734994800: [{'titel': '1 test', 'selector': 'U'}, {'titel': '2 test', 'selector': 'P'}]}
        counter = 0
        us_tz = await return_tz(callback.from_user.id)
        for mahnung in msg_list:
            # ant_text = mahnung['titel']
            jetzt = datetime.now().replace(second=0, microsecond=0)
            # print('jetzt = ', jetzt)
            now = int(jetzt.timestamp()) + tz_dict[us_tz]  # Добавитть Тайм зону !
            # print('\nnow = ', now)
            mahn_data = mahnung["real_time"]
            user_mahnung_key = mahnung['job_id']
            capture = mahnung['capture']
            if (int_key + 86400) >= now:  # События в Будущем. События в день события считаются будущими событиями.
                # print('????????????????????????????????')
                if not mahnung['foto_id']:  # Для текстовых напоминаний
                    formed_text = f'🔺 <b>{mahn_data}</b>\n\n{mahnung["titel"]}\n\n<i>id Mahnung</i>  {user_mahnung_key}'  # \n\n<i>ID Mahnung  {za_chas_key}</i>'
                    await bot.send_message(chat_id=callback.from_user.id, text=formed_text)
                else:
                    if capture:
                        caption = f'🔺 <b>{mahn_data}</b>\n\n{capture}\n\n<i>id Mahnung</i> {user_mahnung_key}'
                    else:
                        caption = f'🔺 <b>{mahn_data}</b>\n\n<i>id Mahnung</i>{user_mahnung_key}'

                    await bot.send_photo(chat_id=callback.from_user.id, photo=mahnung['foto_id'], caption=caption)

                await asyncio.sleep(0.8)
                manager.show_mode = ShowMode.DELETE_AND_SEND
            else:  # События в Прошлом. События в день события считаются будущими событиями.
                if len(msg_list) == 1:
                    # print('*******************************')
                    mahn_button = InlineKeyboardButton(text='delete', callback_data=str_key)
                    delet_kb = InlineKeyboardMarkup(inline_keyboard=[[mahn_button]])
                    if not mahnung['foto_id']:  # Для текстовых напоминаний
                        formed_text = f'🔕 <b>{mahn_data}</b>\n\n{mahnung["titel"]}'  # \n\n<i>ID Mahnung  {za_chas_key}</i>'

                        await bot.send_message(chat_id=callback.from_user.id, text=formed_text, reply_markup=delet_kb)
                        await asyncio.sleep(0.25)
                    else:

                        await bot.send_photo(chat_id=callback.from_user.id, photo=mahnung['foto_id'],
                                             caption=f'🔕 {mahn_data}\n\n{capture}',
                                             reply_markup=delet_kb)
                        await asyncio.sleep(0.25)
                    await insert_last_1(callback.from_user.id)  #  Переводит значение last в  True
                    manager.show_mode = ShowMode.DELETE_AND_SEND
                    await manager.start(state=LAST_MAHNUNG.single)
                else:
                    counter += 1
                    if counter < len(msg_list): # Кнопка DELETE не подставляется, а дописывается текст большого сообщения
                        if not mahnung['foto_id']:  # Для текстовых напоминаний
                            formed_text = f'🔕 <b>{mahn_data}</b>\n\n{mahnung["titel"]}'  # \n\n<i>ID Mahnung  {za_chas_key}</i>'
                            await bot.send_message(chat_id=callback.from_user.id, text=formed_text)
                            await asyncio.sleep(0.1)
                        else:
                            await bot.send_photo(chat_id=callback.from_user.id, photo=mahnung['foto_id'],
                                             caption=f'🔕 {mahn_data}\n\n{capture}')
                            await asyncio.sleep(0.1)
                    else:  # Для последнего сообщения в списке дня подставляется кнопка DELETE
                        mahn_button = InlineKeyboardButton(text='delete', callback_data=str_key)
                        delet_kb = InlineKeyboardMarkup(inline_keyboard=[[mahn_button]])
                        if not mahnung['foto_id']:  # Для текстовых напоминаний
                            formed_text = f'🔕 <b>{mahn_data}</b>\n\n{mahnung["titel"]}'  # \n\n<i>ID Mahnung  {za_chas_key}</i>'
                            await bot.send_message(chat_id=callback.from_user.id, text=formed_text,
                                               reply_markup=delet_kb)
                            await asyncio.sleep(0.1)
                        else:
                            await bot.send_photo(chat_id=callback.from_user.id, photo=mahnung['foto_id'],
                                                     caption=f'🔕 {mahn_data}\n\n{capture}',
                                                     reply_markup=delet_kb)
                        await insert_last_1(callback.from_user.id)  # Переводит last  в True
                        manager.show_mode = ShowMode.SEND
                        await manager.start(state=LAST_MAHNUNG.single)
            await asyncio.sleep(0.1)


async def selection_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    selected = dialog_manager.dialog_data[SELECTED_DAYS_KEY]
    lan = await return_lan(event_from_user.id)
    # print('selected_days = ', selected)
    user_id = event_from_user.id
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    us_bot_dict = bot_dict[str(user_id)]['uniq']  # Получаею только уникальные события
    if us_bot_dict:
        gibt_es_mahnung = True
        no_one = False
    else:
        gibt_es_mahnung = False
        no_one = True
    return {'selected': ", ".join(sorted(selected)),
            'Custom_Calender': cal_events[lan],
            'gibt_es_uniq_mahnung': gibt_es_mahnung,
            'edit': edit[lan],
            'no_treffen':no_uniq_events[lan],
            'no_one':no_one}


async def go_to_basic_func_for_last_dialog(callback: CallbackQuery, widget: Button,
                                           dialog_manager: DialogManager, *args, **kwargs):
    await dialog_manager.done()


async def get_len_user_mahn_list(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    us_event_dict = bot_dict[str(event_from_user.id)]['uniq']  # получаю словарь юзера с уникальными событиями
    if us_event_dict:
        gibt_es_mahnung = False
    else:
        gibt_es_mahnung = True

    getter_data = {'not_mahnung': gibt_es_mahnung,
                   'last_dialog_text': last_dialog_text[lan],  # 'Если не хотите удалять сообщения - воспользуйтесь основным меню'
                   'no_mahnung': gibt_es_mahnung,
                   'no_future_events': no_future_uniq_events[lan],
                   }
    return getter_data


async def get_data_for_uniq(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'id_deleted_mahn': give_me_id_mahnung[lan]}
    return getter_data


async def error_uniq_id_handler(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: ValueError):
    lan = await return_lan(message.from_user.id)
    await message.answer(text=incorrect_id[lan])  # Вы введи неверный id попробуйте ещё раз
    await asyncio.sleep(1)


async def go_to_input_uniq_mahnung_id_for_show(callback: CallbackQuery, widget: Button,
                                               dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next()


async def correct_uniq_id_handler(message: Message, widget: ManagedTextInput,
                                  dialog_manager: DialogManager, *args, **kwargs) -> None:
    """Хэндлер удаляет уникальное напоминание в будущем по введённому id"""
    lan = await return_lan(message.from_user.id)
    user_id = str(message.from_user.id)
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    uniq_dict = bot_dict[user_id]['uniq']  # {'1735344000': [{'titel': 'test', 'foto_id': '', 'za_chas': '1735347600',
    # 'za_sutki': '1735264800', 'real_time': '28.12.2024  02:00', 'job_id': '1735347600'}]}
    # print('uniq_dict = ', uniq_dict)
    mahn_id = message.text
    marker = 0
    deleted_arr_element = ''
    if uniq_dict:
        for k, v in uniq_dict.items():
            # print( 'v = ', v) # Это список словарей [1735286100 <- за час :{pseudo_class}, 1735286400:{pseudoclass}]
            if not marker:
                for pseudo_class in v:
                    if pseudo_class['job_id'] == mahn_id:
                        # print('\n\nHERE\n\n')
                        marker = k
                        if pseudo_class['za_sutki']:
                            # print(" key_job_id['za_'] = ", pseudo_class)
                            try:
                                scheduler_za_sutki_id = str(user_id) + str(pseudo_class['za_sutki'])
                                scheduler.remove_job(scheduler_za_sutki_id)

                            except Exception as ex:  # JobLookupError:
                                pass

                        try:
                            # print('\n\n284 here\n\n')
                            scheduler_id = user_id + mahn_id
                            marker = k
                            deleted_arr_element = pseudo_class
                            stroka = f'{deleted[lan]}\n\nid = {message.text}'
                            scheduler.remove_job(scheduler_id)
                            await message.answer(text=stroka)
                        except Exception as ex:  # JobLookupError:
                            await message.answer(f'{deleted_past[lan]}\n\nid = {message.text}')
                    else:
                        pass
        if marker:
            # print('\n\nif marker', uniq_dict[marker])
            if len(uniq_dict[marker]) == 1:
                del uniq_dict[marker]
            else:
                # print('uniq_dict for del', uniq_dict)
                uniq_dict[marker].remove(deleted_arr_element)
            # print('307 uniq dict = ', uniq_dict)
            await dp.storage.update_data(key=bot_storage_key, data=bot_dict)
    else:
        await message.answer(text=f'UNIQ {no_id[lan]}')  # у вас нет напоминания с таким номером
    await asyncio.sleep(1)
    dialog_manager.show_mode = ShowMode.SEND
    await message.delete()
    await dialog_manager.next()


async def get_weiter_uniq_edit(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    user_id = event_from_user.id
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    us_bot_dict = bot_dict[str(user_id)]['uniq']  # Получаею только уникальные события
    if us_bot_dict:
        gibt_es_mahnung = True
        show_delete = False
    else:
        gibt_es_mahnung = False
        show_delete = True

    getter_data = {'weiter_edit': weiter_edit[lan],
                   'gibt_es_mahnung': gibt_es_mahnung,
                   'return_to_basic': '⬅️', 'edit': edit[lan],
                   'vernutsya_nazad': no_future_uniq_events_else[lan],
                   'show_delete': show_delete}
    return getter_data


async def go_to_core(callback: CallbackQuery, widget: Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.start(ZAPUSK.add_show, mode=StartMode.RESET_STACK)

async def public_future_list(callback: CallbackQuery, widget: Button, manager: DialogManager,  *args, **kwargs ):
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    user_uniq_dict = bot_dict[str(callback.from_user.id)]['uniq']  # {'1735344000': [{'titel': 'test', 'foto_id': '', 'za_chas': '1735347600',
    # 'za_sutki': '1735264800', 'real_time': '28.12.2024  02:00', 'job_id': '1735347600'}]}
    keys = sorted(user_uniq_dict.keys())
    required_list = seconds_to_date_string(keys)  # required_list =  ['2024-12-19', '2024-12-28']
    manager.dialog_data[SELECTED_DAYS_KEY] = required_list  # Добавляю список в диалог_дата
    user_tz = await return_tz(callback.from_user.id)
    NOW = int(datetime.now().timestamp()) + tz_dict[user_tz]
    lan = await return_lan(callback.from_user.id)
    big_msg = f'‼️ {uniq_future_event[lan]}\n\n'
    counter = 0
    second_counter = 0
    for day, spispk in user_uniq_dict.items():
        if (int(day) + 86400) > NOW:  #  Прибавляю сутки времени для чтоы сегодняшние события считались будущими
            second_counter += 1
            for element in spispk:
                if not element['foto_id']:
                    big_msg+=f'<b>{element["real_time"]}</b>\n{element["titel"]}\n<i>id  {element["job_id"]}</i>\n\n'
                    counter = 1
                else:
                    capture_mit_id = f"<b>{element['real_time']}</b>\n{element['capture']}\n<i>id  {element['job_id']}</i>"
                    await bot.send_photo(chat_id=callback.from_user.id, photo=element["foto_id"], caption=capture_mit_id)
                    await asyncio.sleep(0.2)
    if counter:
        await bot.send_message(chat_id=callback.from_user.id, text=big_msg)
        await asyncio.sleep(0.2)
    if not second_counter :
        await bot.send_message(chat_id=callback.from_user.id, text=alles_in_past[lan])
        await asyncio.sleep(0.2)
    manager.show_mode = ShowMode.DELETE_AND_SEND
    await manager.next()

async def public_past_list(callback: CallbackQuery, widget: Button, manager: DialogManager,  *args, **kwargs ):
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    user_uniq_dict = bot_dict[str(callback.from_user.id)]['uniq']  # получаю словарь юзера
    keys = sorted(user_uniq_dict.keys())
    required_list = seconds_to_date_string(keys)  # required_list =  ['2024-12-19', '2024-12-28']
    manager.dialog_data[SELECTED_DAYS_KEY] = required_list  # Добавляю список в диалог_дата
    user_tz = await return_tz(callback.from_user.id)
    NOW = int(datetime.now().timestamp()) + tz_dict[user_tz]
    lan = await return_lan(callback.from_user.id)
    big_msg = f'‼️ {uniq_past_event[lan]}\n\n'
    counter = 0
    second_counter = 0
    past_picture_events_list = []
    in_stamp = datetime.now().replace(second=0, microsecond=0)  # 2024-12-05 19:56:00
    current_seconds = int(in_stamp.timestamp())  # 1732800900
    int_key_list =  sorted(map(int, user_uniq_dict))  # Создаю список интовых ключей. Не помню зачем я сделал ключи строками ?
    for day in int_key_list: #user_uniq_dict.items():
        if (day + 86400) < NOW:
            second_counter += 1
            for element in user_uniq_dict[str(day)]:  # day - это отсортированные ключи в событиях юзера
                proshlo_secund = current_seconds - int(element["job_id"])  # Вычисляю секунды с прошедшего события до сейчас
                eto_bylo = format_time_ago(proshlo_secund)  # Получаю строку 6 years 2 months 20 days ago
                if not element['foto_id']:
                    big_msg += f'<b>{element["real_time"]}</b>\n{element["titel"]}\n<i>Event was {eto_bylo}</i>\n\n'
                    counter = 1
                else:
                    capture_mit_id = f"<b>{element['real_time']}</b>\n{element['capture']}\n<i>Event was {eto_bylo}</i>"
                    # await bot.send_photo(chat_id=callback.from_user.id, photo=element["foto_id"],
                    #                      caption=capture_mit_id)
                    past_picture_events_list.append((element["foto_id"], capture_mit_id,))  # Добавляю картеж во временный список
                    await asyncio.sleep(0.2)
    if counter:
        await bot.send_message(chat_id=callback.from_user.id, text=big_msg)
        await asyncio.sleep(0.2)
    if not second_counter:
        await bot.send_message(chat_id=callback.from_user.id, text=alles_in_future[lan])
        await asyncio.sleep(0.2)
    if len(past_picture_events_list)>1:  # Если есть прошлые события с фото, хотя бы 2 - записиываю список в глобальный словарь
        store_past_event[callback.from_user.id] = {'events':past_picture_events_list, 'index':0}
        first_foto_id = past_picture_events_list[0][0]
        first_capture = past_picture_events_list[0][1]
        len_evens_in_past = len(past_picture_events_list)
        await callback.message.answer_photo(
            photo=first_foto_id,
            caption=first_capture,
            reply_markup=create_past_mahnung_keyboard(len_evens_in_past, page=0)
        )
        manager.show_mode = ShowMode.NO_UPDATE
        await manager.done()
    else:
        manager.show_mode = ShowMode.DELETE_AND_SEND
        await manager.next()



####################################################################################

custom_dialog = Dialog(
    Window(
        Format('{First_Windows}', when='gibt_es_uniq_mahnung'),  # Посмотреть календарь уникальных событий
        Format('{no_treffen}', when='kein_events'),  # У вас нет уникальных событий
        Row(
            Cancel(Const('◀️'),
                   id='first_cancel'),
            Button(Const('📉', when='gibt_es_uniq_mahnung'),
                   id='public_future_list',
                   on_click=public_future_list)),
        Row(
            Button(Const('📈', when='gibt_es_uniq_mahnung'),
                   id='public_past_list',
                   on_click=public_past_list),

            Button(Const('▶️', when='gibt_es_uniq_mahnung'),
                   id='first_calendar',
                   on_click=first_cal)
        ),
        state=SHOW_UNIQ_EVENTS.pre_cal,
        getter=getter_zaglushka
    ),

    Window(
        Format('{Custom_Calender}'),  # Календарь событий
        Format('{no_treffen}', when='no_one'),  # У вас нет уникальных событий
        CustomCalendar(id='calendar',
                       on_click=on_date_selected,  #
                       when='gibt_es_uniq_mahnung'),
        Row(Button(text=Format('{edit}', when='gibt_es_uniq_mahnung'),  # Удалить напоминание
                   id='edit_button',
                   on_click=go_to_input_uniq_mahnung_id_for_show),
            SwitchTo(
                text=Const("◀️"),
                id="back",
                state=SHOW_UNIQ_EVENTS.pre_cal)
            ),
        getter=selection_getter,
        state=SHOW_UNIQ_EVENTS.cal,
    ),

    Window(  # В окне происходит удаление напоминания
        Format('{id_deleted_mahn}'),  # Отправьте мне id номер напоминания
        TextInput(
            id='id_input',
            type_factory=uniq_id_check,
            on_success=correct_uniq_id_handler,  # Удаляет напоминания
            on_error=error_uniq_id_handler
        ),
        Back(Const('◀️'),
             id='ne_znau_nomer'
             ),
        state=SHOW_UNIQ_EVENTS.accept_uniq_id,
        getter=get_data_for_uniq
    ),

    Window(  # В окне происходит выбор удалить ещё одно сообщение или вернуться назад
        Format('{weiter_edit}', when='gibt_es_mahnung'),  # Удалить другие напоминания ?
        Format('{vernutsya_nazad}', when='show_delete'),  # У Вас больше нет событий в будущем
        Row(
            Back(text=Format('{edit}', when='gibt_es_mahnung'),  # Удалить напоминания
                 id='edit_button'),
            Button(text=Format(text='{return_to_basic}'),
                   id='return_button_2',
                   on_click=go_to_core  # Вернусь в коренвое окно
                   ),
        ),
        state=SHOW_UNIQ_EVENTS.post_cal,
        getter=get_weiter_uniq_edit),
)

show_last_dialog = Dialog(
    Window(  # Окно отправляющее прошедщие уникальные ивенты
        Format('{last_dialog_text}'),  # Если не хотите удалять сообщения - воспользутесь основным меню
        Format('{no_future_events}', when='no_mahnung'),
        Button(text=Const('◀️'),  # DELETE Удалить напоминания
               id='sl_button',
               on_click=go_to_basic_func_for_last_dialog,
               when='not_mahnung'),
        state=LAST_MAHNUNG.single,
        getter=get_len_user_mahn_list
    )
)
