from aiogram_dialog import Dialog, Window
from getters import (get_languages, get_spam, choosing_data_getter,
                     form_mahnung_getter, mahnung_accepted,
                     choosing_minut_getter, get_type, select_data,
                     get_titel, get_timezone_info)
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import (Button, Row,
                                        Radio, Start, Calendar, Cancel)
from aiogram_dialog.widgets.input import MessageInput
from aiogram.types import ContentType
from callback_dialogs import radio_spam_button_clicked, set_lan, go_to_unique, reset_funk
import operator
from bot_instans import ZAPUSK, WORK_WITH_SCHED
from input_handlers import message_text_handler, on_photo_sent, message_not_foto_handler
from calendar_functions import (on_date_selected, button_uhr_clicked,
                                button_min_clicked, button_zapusk_clicked, pre_scheduler, set_user_tz)
from monat_handlers import MONAT_MAHNUNG
from show_handlers import SHOW_MAHNUNG


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
        Button(text=Format('{minus_3}'),id='tz_minus_3', on_click=set_user_tz),
        Button(text=Format('{minus_2}'), id='tz_minus_2', on_click=set_user_tz),
        Button(text=Format('{minus_1}'), id='tz_minus_1', on_click=set_user_tz),
        Button(text=Format('{gleich}'), id='tz_gleich', on_click=set_user_tz),
        Button(text=Format('{plus_1}'), id='tz_plus_1', on_click=set_user_tz),
        Button(text=Format('{plus_2}'), id='tz_plus_2', on_click=set_user_tz),
        Button(text=Format('{plus_3}'), id='tz_plus_3', on_click=set_user_tz),
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
        getter=get_languages
    ),)

####################################################################################
uniqe_dialog = Dialog(
    Window(
        Format('{type}'),
        Button(text=Format('{uniq}'),
               id='unique_mahnung',
               on_click=go_to_unique),
        Start(text=Format('{reg}'),
               id='regular_mahnung',
               state=MONAT_MAHNUNG.general),
    state=WORK_WITH_SCHED.choose_regular_or_unique,
    getter=get_type),

    Window(
        Format('{select_data}'),
        Calendar(id='calendar',
                 on_click=on_date_selected,
                 ),
        state=WORK_WITH_SCHED.calendar,
        getter=select_data
    ),

    Window(
        Format('{text_for_2_wind}', when='choosing_data'),
        Row(
            Button(text=Const('00'), id='button_00', on_click=button_uhr_clicked),
            Button(text=Const('01'), id='button_1', on_click=button_uhr_clicked),
            Button(text=Const('02'), id='button_2', on_click=button_uhr_clicked),
            Button(text=Const('03'), id='button_3', on_click=button_uhr_clicked),
            Button(text=Const('04'), id='button_4', on_click=button_uhr_clicked),
            Button(text=Const('05'), id='button_5', on_click=button_uhr_clicked), ),
        Row(
            Button(text=Const('06'), id='button_6', on_click=button_uhr_clicked),
            Button(text=Const('07'), id='button_7', on_click=button_uhr_clicked),
            Button(text=Const('08'), id='button_8', on_click=button_uhr_clicked),
            Button(text=Const('09'), id='button_9', on_click=button_uhr_clicked),
            Button(text=Const('10'), id='button_10', on_click=button_uhr_clicked),
            Button(text=Const('11'), id='button_11', on_click=button_uhr_clicked), ),
        Row(
            Button(text=Const('12'), id='button_12', on_click=button_uhr_clicked),
            Button(text=Const('13'), id='button_13', on_click=button_uhr_clicked),
            Button(text=Const('14'), id='button_14', on_click=button_uhr_clicked),
            Button(text=Const('15'), id='button_15', on_click=button_uhr_clicked),
            Button(text=Const('16'), id='button_16', on_click=button_uhr_clicked),
            Button(text=Const('17'), id='button_17', on_click=button_uhr_clicked), ),
        Row(
            Button(text=Const('18'), id='button_18', on_click=button_uhr_clicked),
            Button(text=Const('19'), id='button_19', on_click=button_uhr_clicked),
            Button(text=Const('20'), id='button_20', on_click=button_uhr_clicked),
            Button(text=Const('21'), id='button_21', on_click=button_uhr_clicked),
            Button(text=Const('22'), id='button_22', on_click=button_uhr_clicked),
            Button(text=Const('23'), id='button_23', on_click=button_uhr_clicked)
        ),
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
            Button(text=Format('{form_grafik_mahnungen}'), id='zapusk', on_click=button_zapusk_clicked),
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
            func=on_photo_sent,
            content_types=ContentType.PHOTO,
        ),
        MessageInput(
            func=message_not_foto_handler,
            content_types=ContentType.ANY,
        ),
        state=WORK_WITH_SCHED.titel,
        getter=get_titel
    ),

    Window(  #  Окно запускающее шедулер
        Format('{text_for_4_wind}', when='choosing_data'),  # Запускаем Планировщик
        Button(text=Format('{remind_me}'),  # Напомнить мне
              id='see_stelle_button',
              on_click=pre_scheduler),
        state=WORK_WITH_SCHED.vor_mahnung,
        getter=choosing_minut_getter
    ),
    Window(  # окно возвращаюшее в начало диалога
        Format(text='{accepted}'),  #  Напоминание принято
        Cancel(text=Format(text='{return_to_basic}'),  #
              id='see_stelle_button',
              on_click=reset_funk),
        state=WORK_WITH_SCHED.nach_mahnung_accepting,
        getter=mahnung_accepted),)


