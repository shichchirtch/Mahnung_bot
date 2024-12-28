from bot_instans import scheduler
import time
from datetime import datetime
from bot_instans import queue_sender_message
from random import randint

async def mahnung_gearbeitet(user_id, mahnung_data, time_stamp, capture):
    print('WE are into mahnung gearbeitet function')
    formatted_date = f'‼️ <b>MAHNUNG   {time_stamp}</b>'
    if mahnung_data.startswith('🔶'):
        titel = formatted_date +'\n\n' + mahnung_data
        try:  # Страхуюсь на случай блокировки бота
            await queue_sender_message(chat_id=user_id, content=titel, content_type="text")
        except Exception as e:
            print(f'За час yникальное событие исключение {e}')
            pass
    else:
        # Это фото с подписью
        if capture:  # Если юзер добавил подпись к фото
            combo_capture = f'{capture}\n\n{formatted_date}'
        else:
            combo_capture = formatted_date
        try:
            await queue_sender_message(chat_id=user_id, content=mahnung_data, content_type="photo", caption=combo_capture)
        except Exception as e:
            print(f'За час yникальное событие исключение foto {e}')
            pass

def scheduler_job(user_id, dialog_dict, tz:str):
    int_za_chas = int(dialog_dict['za_chas'])
    # print('int_za_chas = ', int_za_chas)
    smesenie = randint(1, 9)
    new_future = int_za_chas + smesenie
    # print('new_future = ', new_future)
    future = datetime.fromtimestamp(new_future)  # Время когда действие должно быть закончено
    # print('future = ', future, type(future))
    id = str(user_id) + str(dialog_dict['za_chas'])
    # print('tz = ', tz)

    if dialog_dict['titel']:
        mahnung_data ='🔶  ' + dialog_dict['titel']
        capture = ''
    else:
        mahnung_data = dialog_dict['foto_id']
        capture = dialog_dict['capture']
    time_stamp = dialog_dict['real_time']  # 28.11.2024  13:50 <class 'str'>
    # print('37 time stamp = ', time_stamp, type(time_stamp))
    scheduler.add_job(mahnung_gearbeitet, "date", run_date=future, timezone=tz, args=(user_id, mahnung_data, time_stamp, capture), id=id)
    time.sleep(0.2)

#################################################################################

async def mahnung_za_sutki_gearbeitet(user_id, mahnung_data, time_stamp, capture):
    # print('WE are into mahnung gearbeitet za sutki function')
    formatted_date = f'‼️ <b>MAHNUNG   {time_stamp}</b>'
    if mahnung_data.startswith('🔶'):
        titel = formatted_date + '\n\n' + mahnung_data
        try:
            await queue_sender_message(chat_id=user_id, content=titel, content_type="text")
        except Exception as e:
            print(f'Sutki scheduler Exeption {e}')
    else:
        try:
            new_capture = f'{formatted_date}\n\n{capture}'
            await queue_sender_message(chat_id=user_id, content=mahnung_data, content_type="photo", caption=new_capture)
        except Exception as e:
            print(f'Sutki scheduler Exeption {e}')

def scheduler_za_sutki_job(user_id:int, dialog_dict, tz:str):
    native_za_sutki_flat_time = dialog_dict['za_sutki']
    smesenie = randint(1, 9)
    new_future_za_sutki = native_za_sutki_flat_time + smesenie
    future_za_sutki = datetime.fromtimestamp(new_future_za_sutki)  # Время когда действие должно быть закончено datetime Obj

    id = str(user_id)+str(dialog_dict['za_sutki'])
    if dialog_dict['titel']:
        mahnung_data ='🔶  ' + dialog_dict['titel']
    else:
        mahnung_data = dialog_dict['foto_id']
    time_stamp = dialog_dict['real_time']
    capture = dialog_dict['capture']
    scheduler.add_job(mahnung_za_sutki_gearbeitet, "date", run_date=future_za_sutki, timezone=tz,
                      args=(user_id, mahnung_data, time_stamp, capture), id=id)
    time.sleep(0.2)

#######################################################################################################

async  def napominalka_async_for_month(user_id, mahnung_data, time_data, capture):
    formatted_date = f'🔆 <b>MAHNUNG   {time_data}</b>'
    if mahnung_data.startswith('🔶'):
        titel = formatted_date + '\n\n' + mahnung_data
        try:
            await queue_sender_message(chat_id=user_id, content=titel, content_type="text")
        except Exception as e:
            print(f'Monat napominalka Exeption {e}')
            pass
    else:
        # Это фото с подписью
        try:
            mit_podis = f'{formatted_date}\n\n{capture}'
            await queue_sender_message(chat_id=user_id, content=mahnung_data, content_type="photo", caption=mit_podis)
        except Exception as e:
            print(f'Monat napominalka Exeption {e}')
            pass

def napominalka_sync_for_month(user_id, dialog_dict:dict):
    print('napominalka_sync works')
    print('days = ', dialog_dict['day'])

    temp_days = set(dialog_dict['day'].split(','))
    t = ''
    for x in temp_days:
        t+=x+','
    day_of_month = t[:-1]
    # print('day_of month = ', day_of_month)
    chas = int(dialog_dict['hours'])  # интую
    minutusy = int(dialog_dict['minuts'])
    if dialog_dict['titel']:
        mahnung_data ='🔶  ' + dialog_dict['titel']
    else:
        mahnung_data = dialog_dict['foto_id']
    data_s_tochkami = dialog_dict['real_time']
    tz = dialog_dict['tz']
    job_id =dialog_dict['job_id']
    capture = dialog_dict['capture']
    sec = randint(1,9)
    id = str(user_id) + job_id  # 6685637602301550
    scheduler.add_job(napominalka_async_for_month, "cron", day=day_of_month, hour = chas,
                      minute = minutusy, second=sec, end_date='2037-05-30',  timezone=tz,
                      args=(user_id, mahnung_data, data_s_tochkami, capture), id=id)
#####################################################################################

async  def async_week_sched(user_id, mahnung_data, time_data, capture):
    formatted_date = f'⭐️ <b>MAHNUNG   {time_data}</b>'
    if mahnung_data.startswith('🔹'):
        titel = formatted_date + '\n\n' + mahnung_data
        try:
            await queue_sender_message(chat_id=user_id, content=titel, content_type="text")
        except Exception as e:
            print(f'Week sched exception {e}')
            pass
    else:
        new_capture = f'{formatted_date}\n\n{capture}'
        try:
            await queue_sender_message(chat_id=user_id, content=mahnung_data, content_type="photo",
                                   caption=new_capture)
        except Exception as e:
            print(f'Week sched exception {e}')
            pass


def week_sched(user_id, dialog_dict:dict):
    # print('week_sched_sync works')
    week_days = dialog_dict['week_days']
    chas = int(dialog_dict['hours'])  # интую
    minutusy = int(dialog_dict['minuts'])
    if dialog_dict['titel']:
        mahnung_data ='🔹  ' + dialog_dict['titel']
    else:
        mahnung_data = dialog_dict['foto_id']
    week_key = dialog_dict['key']
    # print('week_key = ', week_key)
    r_t = dialog_dict['real_time']
    # print('r_t= ', r_t)
    id = str(user_id) + week_key  # 6685637602301550
    # print('week = ', dialog_dict)
    sec = randint(1, 9)
    tz = dialog_dict['tz']
    capture = dialog_dict['capture']
    scheduler.add_job(async_week_sched, "cron", day_of_week=week_days, hour = chas,
                      minute = minutusy, second=sec, end_date='2037-05-30',  timezone=tz,
                      args=(user_id, mahnung_data, r_t, capture), id=id)

########################################################################################

async  def async_day_sched(user_id, mahnung_data, time_data, capture):
    formatted_date = f'🔔 <b>MAHNUNG   {time_data}</b>'
    if mahnung_data.startswith('♦️'):
        titel = formatted_date + '\n\n' + mahnung_data
        try:
            await queue_sender_message(chat_id=user_id, content=titel, content_type="text")
        except Exception as e:
            print(f'DAY sched exception {e}')
            pass

    else:
        try:
            new_capture = f'{formatted_date}\n\n{capture}'
            await queue_sender_message(chat_id=user_id, content=mahnung_data, content_type="photo",
                                       caption=new_capture)
        except Exception as e:
            print(f'DAY sched exception {e}')
            pass


def day_sched(user_id, dialog_dict:dict):
    # print('day_sched_sync works')
    chas = dialog_dict['hours']
    # print('chas in shed = ', chas)
    minutusy = dialog_dict['minuts']
    if dialog_dict['titel']:
        mahnung_data ='♦️  ' + dialog_dict['titel']
    else:
        mahnung_data = dialog_dict['foto_id']
    day_key = dialog_dict['key']
    # print('day_key = ', day_key)
    r_t = dialog_dict['real_time']
    # print('r_t= ', r_t)
    id = str(user_id) + day_key  # 6685637602011550
    # print('day_dict = ' , dialog_dict)
    tz = dialog_dict['tz']
    capture = dialog_dict['capture']
    sec = randint(1, 9)
    scheduler.add_job(async_day_sched, "cron", hour = chas,
                      minute = minutusy, second=sec, end_date='2037-05-30',  timezone=tz,
                      args=(user_id, mahnung_data, r_t, capture), id=id)

######################################################################################################


async def interval_gearbeitet(user_id, mahnung_data, time_stamp, capture):
    # print('WE are into mahnung gearbeitet function')
    formatted_date = f'🌍 <b>MAHNUNG   {time_stamp}</b>'
    if mahnung_data.startswith('⚡️'):
        titel = formatted_date +'\n\n' + mahnung_data
        try:  # Страхуюсь на случай блокировки бота
            await queue_sender_message(chat_id=user_id, content=titel, content_type="text")
        except Exception as e:
            print(f'За час yникальное событие исключение {e}')
            pass
    else:
        # Это фото с подписью
        if capture:  # Если юзер добавил подпись к фото
            combo_capture = f'{capture}\n\n{formatted_date}'
        else:
            combo_capture = formatted_date
        try:
            await queue_sender_message(chat_id=user_id, content=mahnung_data, content_type="photo", caption=combo_capture)
        except Exception as e:
            print(f'За час yникальное событие исключение foto {e}')
            pass

def interval_sched(user_id, dialog_dict, tz):
    id = str(user_id) + str(dialog_dict['job_id'])
    if dialog_dict['titel']:
        mahnung_data ='⚡️  ' + dialog_dict['titel']
        capture = ''
    else:
        mahnung_data = dialog_dict['foto_id']
        capture = dialog_dict['capture']
    time_stamp = dialog_dict['zagolovok']  # 28.11.2024  13:50 <class 'str'>
    start_date = dialog_dict['start_time']
    days = int(dialog_dict['interval']) #timedelta(days=int(dialog_dict['interval']))
    scheduler.add_job(interval_gearbeitet, "interval", days=days, start_date=start_date, timezone=tz, args=(user_id, mahnung_data, time_stamp, capture), id=id)
    time.sleep(0.2)











