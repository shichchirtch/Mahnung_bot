from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from getters import (get_set_or_show, get_spam, choosing_data_getter,
                     form_mahnung_getter, mahnung_accepted, get_type, select_data,
                     get_titel, get_timezone_info)
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Row, Group, Radio, Start, Calendar, Cancel, Back, Next
from aiogram_dialog.widgets.input import MessageInput
from aiogram.types import ContentType, Message, CallbackQuery, User
from callback_dialogs import radio_spam_button_clicked, set_lan, go_to_unique, reset_funk
import operator
from bot_instans import ZAPUSK, WORK_WITH_SCHED, dp, bot_storage_key
from input_handlers import message_text_handler, message_not_foto_handler
from calendar_functions import (on_date_selected, button_uhr_clicked,
                                button_min_clicked, button_zapusk_clicked, pre_scheduler, set_user_tz)
from monat_handlers import MONAT_MAHNUNG
from show_handlers import SHOW_MAHNUNG
from postgres_functions import return_lan, return_spisok_uniq_events, insert_uniq_events
from lexicon import *

async def getter_for_capture(dialog_manager: DialogManager, event_from_user: User,**kwargs):
    lan = await return_lan(event_from_user.id)
    return {'enter_capture':enter_capture[lan]}

async def get_enter_capture(dialog_manager: DialogManager, event_from_user: User,**kwargs):
    lan = await return_lan(event_from_user.id)
    return {'data_capture':not_text_capture_send[lan]}

async def get_pre_sheduler_window(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    if dialog_manager.dialog_data['choosing_data']:
        getter_data = {'text_for_4_wind': zapuskaem_scheduler[lan], 'choosing_data':True, 'remind_me':remind_me[lan] }
    else:
        getter_data = {'text_for_4_wind': car_time[lan], 'choosing_data':False}
    return getter_data


async def accepting_foto(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    print('accepting_foto works')
    foto_id = message.photo[-1].file_id
    dialog_manager.dialog_data['foto_id'] = foto_id
    dialog_manager.dialog_data['capture'] = ''
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next()

async def set_foto_mahnung_ohne_capture(cb: CallbackQuery, widget: Button, dialog_manager: DialogManager) -> None:
    """Хэндлер формирует словарь с фото без подписи"""
    user_id = str(cb.from_user.id)
    lan = await return_lan(cb.from_user.id)
    za_chas = dialog_manager.dialog_data['za_chas']
    dialog_manager.dialog_data['capture'] = ''
    spisok_uniq_za_chas = await return_spisok_uniq_events(cb.from_user.id)
    if str(za_chas) not in spisok_uniq_za_chas:
        str_za_chas = str(za_chas)
        za_sutki = dialog_manager.dialog_data['za_sutki']
        str_za_sutki = str(za_sutki)
        real_time = dialog_manager.dialog_data['real_time']  #  29.12.2024  13:15
        dialog_manager.dialog_data['titel'] = ''
        foto_id = dialog_manager.dialog_data['foto_id']
        job_id = str_za_chas

        pseudo_class = {'titel': '', 'foto_id': foto_id, 'za_chas': str_za_chas, 'za_sutki': str_za_sutki,
                        'selector': 'U', 'real_time': real_time, 'capture':'', 'job_id': job_id}
        # print('pseudo_class = ', pseudo_class)
        bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
        # b_u_dict = bot_dict[user_id]  # получаю словарь юзера
        time_code = str(dialog_manager.dialog_data['day'])
        bot_dict[user_id]['uniq'].setdefault(time_code, []).append(pseudo_class)
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await cb.message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await dialog_manager.switch_to(WORK_WITH_SCHED.vor_mahnung)
    else:
        await cb.message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await dialog_manager.done()

async def message_not_text_handler_in_capture(message: Message, widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    lan = await return_lan(message.from_user.id)
    await message.answer(not_text_capture_send[lan])


async def message_capture_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    """Хэндлер устанавливает capture"""
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    capture = message.text
    dialog_manager.dialog_data['titel'] = ''
    za_chas = dialog_manager.dialog_data['za_chas']
    foto_id = dialog_manager.dialog_data['foto_id']
    dialog_manager.dialog_data['capture'] = message.text
    spisok_uniq_za_chas = await return_spisok_uniq_events(message.from_user.id)
    if za_chas not in spisok_uniq_za_chas:
        str_za_chas = str(za_chas)
        za_sutki = dialog_manager.dialog_data['za_sutki']
        str_za_sutki = str(za_sutki)
        real_time = dialog_manager.dialog_data['real_time'] # type srt 2024-11-21 15:55:00
        job_id = str(za_chas)
        dialog_manager.dialog_data['job_id']=job_id
        pseudo_class = {'titel': '', 'foto_id': foto_id, 'za_chas': str_za_chas, 'za_sutki': str_za_sutki,
                        'selector': 'U', 'real_time': real_time, 'capture':capture,'job_id': job_id}
        time_code = str(dialog_manager.dialog_data['day'])
        bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
        # b_u_dict = bot_dict[user_id]  # получаю словарь юзера
        # b_u_dict_uniq = b_u_dict['uniq']  # Получаю словарь для уникальных событий
        bot_dict[user_id]['uniq'].setdefault(time_code, []).append(pseudo_class)  # Записываю туда вот такую струкутру '173000000':[]
        # print('36 bot_dict',bot_dict)  # 36 bot_dict
        # {'6685637602': {'uniq': {'1734912000': # День в 00:00 value = [], ключа за час - нет
        # [{'titel': 'test', 'foto_id': '', 'za_chas': '1734875400', #  За час и job_id - совпадают
        # 'za_sutki': '', 'selector': 'U', 'real_time': '22.12.2024  14:50',
        # 'job_id': '1734875400'}]},
        # 'reg': {} # Регулярных событий ещё нет
        #   }
        # }  - Не удалять комменатрий !


        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота

        await insert_uniq_events(message.from_user.id, str_za_chas)  # записываю уникальное событие в списоск

        await message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await message.delete()
        await dialog_manager.next()
    else:
        await message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await dialog_manager.done()

async def return_to_calender(cb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
     dialog_manager.dialog_data['day'] = ''
     dialog_manager.dialog_data['choosing_data']=False
     dialog_manager.show_mode = ShowMode.EDIT
     await dialog_manager.back()


async def return_to_hours(cb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['hours'] = ''
    dialog_manager.show_mode = ShowMode.EDIT
    await dialog_manager.back()




zapusk_dialog = Dialog(
    Window(
        Const('Choose Language'),
        Button(text=Const('🇩🇪'),
               id='de',
               on_click=set_lan),
        Button(text=Const('🇬🇧'),
               id='en',
               on_click=set_lan),
        Button(text=Const('🇺🇦'),
               id='uk',
               on_click=set_lan),
        Button(text=Const('🇹🇷'),
               id='tr',
               on_click=set_lan),
        Button(text=Const('🇮🇷'),
               id='fa',
               on_click=set_lan),
        Button(text=Const('🇸🇦'),
               id='ar',
               on_click=set_lan),
        Button(text=Const('🇷🇺'),
               id='ru',
               on_click=set_lan),
    state=ZAPUSK.set_lan),

    Window(  # SPAM
        Format('{lan}'),
        Row(
            Radio(
                checked_text=Format('🔘 {item[0]}'),
                unchecked_text=Format('⚪️ {item[0]}'),
                id='spam_window',
                item_id_getter=operator.itemgetter(1),
                items="spam_data",
                on_state_changed=radio_spam_button_clicked,
            ),
        ),
        state=ZAPUSK.spam,
        getter=get_spam),
    Window(
        Format('{bot_time}'),
        Button(text=Format('{gleich}'), id='tz_gleich', on_click=set_user_tz),
        Button(text=Format('{plus_1}'), id='tz_plus_1', on_click=set_user_tz),
        Button(text=Format('{plus_2}'), id='tz_plus_2', on_click=set_user_tz),
        Button(text=Format('{plus_3}'), id='tz_plus_3', on_click=set_user_tz),
        Button(text=Format('{plus_4}'), id='tz_plus_4', on_click=set_user_tz),
        Button(text=Format('{plus_5}'), id='tz_plus_5', on_click=set_user_tz),
        Button(text=Format('{plus_6}'), id='tz_plus_6', on_click=set_user_tz),
            state=ZAPUSK.set_timezone,
            getter=get_timezone_info),

    Window( # Это корневое окно других диалогов
        Format('{knopka}'), # Создать напоминание или посмотреть мои напоминания
        Start(text=Format('{set_r}'),
               id='set_mahnung',
               state=WORK_WITH_SCHED.choose_regular_or_unique),

        Start(text=Format('{see_r}'),
              id='list_mahnung',
              state=SHOW_MAHNUNG.show_mahnung_start),

        state=ZAPUSK.add_show,
        getter=get_set_or_show
    ))

####################################################################################
uniqe_dialog = Dialog(
    Window(
        Format('{type}'),   #  Выберите тип напоминания
        Button(text=Format('{uniq}'),
               id='unique_mahnung',
               on_click=go_to_unique),
        Group(Row(Cancel(Const('◀️'),
                         id='zuruck'),

        Start(text=Format('{reg}'),  # Начало диалога с ежемесячными напоминаниями
               id='regular_mahnung',
               state=MONAT_MAHNUNG.general))),
    state=WORK_WITH_SCHED.choose_regular_or_unique,
    getter=get_type),

    Window(
        Format('{select_data}'),
        Calendar(id='calendar',
                 on_click=on_date_selected),
        Back(Const('◀️'),
            id='prev_win'),
        state=WORK_WITH_SCHED.calendar,
        getter=select_data
    ),

    Window(
        Format('{text_for_2_wind}', when='choosing_data'),
        Row(
            Button(text=Const('00'), id='ubutton_00', on_click=button_uhr_clicked),
            Button(text=Const('01'), id='ubutton_1', on_click=button_uhr_clicked),
            Button(text=Const('02'), id='ubutton_2', on_click=button_uhr_clicked),
            Button(text=Const('03'), id='ubutton_3', on_click=button_uhr_clicked),
            Button(text=Const('04'), id='ubutton_4', on_click=button_uhr_clicked),
            Button(text=Const('05'), id='ubutton_5', on_click=button_uhr_clicked)),
        Row(
            Button(text=Const('06'), id='ubutton_6', on_click=button_uhr_clicked),
            Button(text=Const('07'), id='ubutton_7', on_click=button_uhr_clicked),
            Button(text=Const('08'), id='ubutton_8', on_click=button_uhr_clicked),
            Button(text=Const('09'), id='ubutton_9', on_click=button_uhr_clicked),
            Button(text=Const('10'), id='ubutton_10', on_click=button_uhr_clicked),
            Button(text=Const('11'), id='ubutton_11', on_click=button_uhr_clicked)),
        Row(
            Button(text=Const('12'), id='ubutton_12', on_click=button_uhr_clicked),
            Button(text=Const('13'), id='ubutton_13', on_click=button_uhr_clicked),
            Button(text=Const('14'), id='ubutton_14', on_click=button_uhr_clicked),
            Button(text=Const('15'), id='ubutton_15', on_click=button_uhr_clicked),
            Button(text=Const('16'), id='ubutton_16', on_click=button_uhr_clicked),
            Button(text=Const('17'), id='ubutton_17', on_click=button_uhr_clicked)),
        Row(
            Button(text=Const('18'), id='ubutton_18', on_click=button_uhr_clicked),
            Button(text=Const('19'), id='ubutton_19', on_click=button_uhr_clicked),
            Button(text=Const('20'), id='ubutton_20', on_click=button_uhr_clicked),
            Button(text=Const('21'), id='ubutton_21', on_click=button_uhr_clicked),
            Button(text=Const('22'), id='ubutton_22', on_click=button_uhr_clicked),
            Button(text=Const('23'), id='ubutton_23', on_click=button_uhr_clicked)
        ),
        Button(Const('◀️'),
            id='back_to_calender',
            on_click=return_to_calender),
        state=WORK_WITH_SCHED.uhr,
        getter=choosing_data_getter
    ),

    Window(  # Окно формирует одно или два задания для планировщика, или пишет - об ошибке, если дата из прошлого
        Format('{text_for_3_wind}', when='choosing_data'),
        Row(
            Button(text=Const('00'), id='button_00', on_click=button_min_clicked),
            Button(text=Const('05'), id='button_05', on_click=button_min_clicked),
            Button(text=Const('10'), id='button_10', on_click=button_min_clicked),),
        Row(
            Button(text=Const('15'), id='button_15', on_click=button_min_clicked),
            Button(text=Const('20'), id='button_20', on_click=button_min_clicked),
            Button(text=Const('25'), id='button_25', on_click=button_min_clicked), ),
        Row(
            Button(text=Const('30'), id='button_30', on_click=button_min_clicked),
            Button(text=Const('35'), id='button_35', on_click=button_min_clicked),
            Button(text=Const('40'), id='button_40', on_click=button_min_clicked), ),
        Row(
            Button(text=Const('45'), id='button_45', on_click=button_min_clicked),
            Button(text=Const('50'), id='button_50', on_click=button_min_clicked),
            Button(text=Const('55'), id='button_55', on_click=button_min_clicked), ),
        Row(
            Button(Const('◀️'),
            id='back_to_hours',
            on_click=return_to_hours),
            Button(text=Const('▶️'), id='zapusk', on_click=button_zapusk_clicked),
        ),
        state=WORK_WITH_SCHED.minuten,
        getter=form_mahnung_getter
    ),

    Window(  # Окно принимающее содержание напоминания и форммирующее ЭК Mahnung
        Format(text='{data_mahnung}'),  # Отправьте мне название напоминания
        MessageInput(
            func=message_text_handler,
            content_types=ContentType.TEXT,
        ),
        MessageInput(
            func=accepting_foto,
            content_types=ContentType.PHOTO,
        ),
        MessageInput(
            func=message_not_foto_handler,
            content_types=ContentType.ANY,
        ),
        Cancel(Const('◀️'),
               id='Cancel_for_uniq_day'),
        state=WORK_WITH_SCHED.titel,
        getter=get_titel
    ),

    Window( # Окно предлагающее ввести capture
        Format('{enter_capture}'),  # Хотите сделать подпись по фотографией ?
        Cancel(Const('◀️'),
             id='return_to_basic'),
        Row(Next(Const('😃'),
            id='yes_capture'),
            Button(Const('❌'),
                     id='no_capture',
                     on_click=set_foto_mahnung_ohne_capture)),

        state=WORK_WITH_SCHED.ask_capture,
        getter=getter_for_capture
    ),

    Window(  # Окно принимающее capture
        Format(text='{data_capture}'),  # Отправьте capture
        MessageInput(
            func=message_capture_handler,
            content_types=ContentType.TEXT,
        ),
        MessageInput(
            func=message_not_text_handler_in_capture,
            content_types=ContentType.ANY,
        ),
        Cancel(Const('◀️'),
               id='Cancel_for_uniq_day'),
        state=WORK_WITH_SCHED.enter_capture,
        getter=get_enter_capture
    ),

    Window(  #  Окно запускающее шедулер
        Format('{text_for_4_wind}', when='choosing_data'),  # Запускаем Планировщик
        Button(text=Format('{remind_me}'),  # Напомнить мне
              id='see_stelle_button',
              on_click=pre_scheduler),
        state=WORK_WITH_SCHED.vor_mahnung,
        getter=get_pre_sheduler_window
    ),
    Window(  # окно возвращаюшее в начало диалога
        Format(text='{accepted}'),  #  Напоминание принято
        Cancel(text=Format(text='{return_to_basic}'),  #
              id='see_stelle_button',
              on_click=reset_funk),
        state=WORK_WITH_SCHED.nach_mahnung_accepting,
        getter=mahnung_accepted))


